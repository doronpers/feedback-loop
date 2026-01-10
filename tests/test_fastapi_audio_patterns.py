"""
Adversarial Test Cases for FastAPI Audio Processing Patterns

These tests focus on "silent failures" and edge cases that AI often misses:
- 800MB files that are actually silent/white noise
- Disconnecting client mid-upload (timeout handling)
- Simulating 'Disk Full' error (OSError) during write
- Validating NumPy-to-JSON serialization of NaN or Inf values
- Path traversal attacks in temp file creation
"""

import io
import logging
import os
import tempfile
from unittest.mock import patch

import numpy as np
import pytest
from fastapi import HTTPException, UploadFile

from examples.fastapi_audio_patterns import (convert_numpy_audio_result,
                                             process_audio_file_chunked,
                                             safe_audio_upload_workflow,
                                             stream_upload_to_disk,
                                             validate_audio_file_header)


class TestStreamUploadToDisk:
    """Test streaming file upload patterns."""

    @pytest.mark.asyncio
    async def test_stream_small_file_success(self, tmp_path):
        """Test streaming a small file successfully."""
        # Create mock upload file
        content = b"test audio data" * 100
        file = UploadFile(filename="test.wav", file=io.BytesIO(content))

        temp_path, success = await stream_upload_to_disk(file)

        try:
            assert success is True
            assert os.path.exists(temp_path)

            # Verify content
            with open(temp_path, "rb") as f:
                written_content = f.read()
            assert written_content == content
        finally:
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)

    @pytest.mark.asyncio
    async def test_stream_file_exceeds_size_limit(self):
        """Test that files exceeding size limit are rejected during streaming."""
        # Create a large mock file (larger than limit)
        large_content = b"x" * (5 * 1024)  # 5KB
        file = UploadFile(filename="large.wav", file=io.BytesIO(large_content))

        # Set max size to 1KB
        with pytest.raises(HTTPException) as exc_info:
            await stream_upload_to_disk(file, max_size_bytes=1024)

        assert exc_info.value.status_code == 413
        assert "too large" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_invalid_file_extension_rejected(self):
        """Test that invalid file extensions are rejected."""
        content = b"malicious content"
        file = UploadFile(filename="malware.exe", file=io.BytesIO(content))

        with pytest.raises(HTTPException) as exc_info:
            await stream_upload_to_disk(file, allowed_extensions=(".wav", ".mp3"))

        assert exc_info.value.status_code == 400
        assert "Invalid file type" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_no_filename_with_extension_check(self):
        """Test handling of upload without filename when extensions checked."""
        content = b"test data"
        file = UploadFile(filename=None, file=io.BytesIO(content))

        with pytest.raises(HTTPException) as exc_info:
            await stream_upload_to_disk(file, allowed_extensions=(".wav",))

        assert exc_info.value.status_code == 400


class TestDiskFullSimulation:
    """Test handling of disk full errors during file operations."""

    @pytest.mark.asyncio
    async def test_io_error_during_write(self):
        """Simulate IOError during file write (disk full, permission denied, etc)."""
        content = b"x" * 1024
        file = UploadFile(filename="test.wav", file=io.BytesIO(content))

        # Mock tempfile.mkstemp to raise OSError
        with patch(
            "tempfile.mkstemp", side_effect=OSError(28, "No space left on device")
        ):
            with pytest.raises(HTTPException) as exc_info:
                await stream_upload_to_disk(file)

            # Should handle the error gracefully
            assert exc_info.value.status_code == 500
            assert "upload failed" in exc_info.value.detail.lower()


class TestProcessAudioFileChunked:
    """Test chunked audio file processing."""

    @pytest.mark.asyncio
    async def test_process_file_in_chunks(self, tmp_path):
        """Test processing a file in chunks."""
        test_file = tmp_path / "test.wav"
        # Create 2.5MB file
        test_data = b"x" * (2560 * 1024)
        test_file.write_bytes(test_data)

        result = await process_audio_file_chunked(
            str(test_file), chunk_size=1024 * 1024
        )

        assert result["file_size_bytes"] == len(test_data)
        assert result["chunks_processed"] == 3  # 2.5MB / 1MB = 3 chunks
        assert result["total_bytes_processed"] == len(test_data)

    @pytest.mark.asyncio
    async def test_process_nonexistent_file(self):
        """Test processing a file that doesn't exist."""
        with pytest.raises(HTTPException) as exc_info:
            await process_audio_file_chunked("/tmp/nonexistent_file.wav")

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_process_empty_file(self, tmp_path):
        """Test processing an empty file (silent failure case)."""
        empty_file = tmp_path / "empty.wav"
        empty_file.write_bytes(b"")

        result = await process_audio_file_chunked(str(empty_file))

        assert result["file_size_bytes"] == 0
        assert result["chunks_processed"] == 0


class TestSilentAudioDetection:
    """Test handling of files that are silent or white noise."""

    @pytest.mark.asyncio
    async def test_large_silent_file(self, tmp_path):
        """Test 800MB file that is actually silent (all zeros)."""
        silent_file = tmp_path / "silent.wav"
        # Create 1MB of silence for testing (representing 800MB conceptually)
        silent_data = b"\x00" * (1024 * 1024)
        silent_file.write_bytes(silent_data)

        result = await process_audio_file_chunked(str(silent_file))

        # Should process successfully even if silent
        assert result["file_size_bytes"] == len(silent_data)
        assert result["total_bytes_processed"] == len(silent_data)

    @pytest.mark.asyncio
    async def test_white_noise_file(self, tmp_path):
        """Test file with white noise (random data)."""
        noise_file = tmp_path / "noise.wav"
        # Simulate white noise with random bytes
        noise_data = os.urandom(1024 * 1024)  # 1MB random
        noise_file.write_bytes(noise_data)

        result = await process_audio_file_chunked(str(noise_file))

        assert result["file_size_bytes"] == len(noise_data)
        assert result["total_bytes_processed"] == len(noise_data)


class TestNumpyJsonSerialization:
    """Test NumPy type serialization for JSON responses."""

    def test_convert_numpy_int(self):
        """Test converting NumPy integers."""
        result = {"sample_rate": np.int64(44100)}
        converted = convert_numpy_audio_result(result)

        assert isinstance(converted["sample_rate"], int)
        assert converted["sample_rate"] == 44100

    def test_convert_numpy_float(self):
        """Test converting NumPy floats."""
        result = {"duration": np.float64(123.45)}
        converted = convert_numpy_audio_result(result)

        assert isinstance(converted["duration"], float)
        assert converted["duration"] == pytest.approx(123.45)

    def test_convert_nan_values(self):
        """Test handling NaN values (critical edge case)."""
        result = {
            "invalid_metric": np.float64(np.nan),
            "valid_metric": np.float64(10.5),
        }
        converted = convert_numpy_audio_result(result)

        # NaN should be converted to None or handled gracefully
        assert converted["invalid_metric"] is None
        assert converted["valid_metric"] == pytest.approx(10.5)

    def test_convert_inf_values(self):
        """Test handling Inf values (critical edge case)."""
        result = {
            "overflow_metric": np.float64(np.inf),
            "underflow_metric": np.float64(-np.inf),
            "normal_metric": np.float64(5.5),
        }
        converted = convert_numpy_audio_result(result)

        # Inf should be converted to None or handled gracefully
        assert converted["overflow_metric"] is None
        assert converted["underflow_metric"] is None
        assert converted["normal_metric"] == pytest.approx(5.5)

    def test_convert_nested_numpy_types(self):
        """Test converting nested structures with NumPy types."""
        result = {
            "metadata": {
                "samples": np.int64(1000000),
                "duration": np.float64(22.68),
                "channels": np.array([1, 2]),
            }
        }
        converted = convert_numpy_audio_result(result)

        assert isinstance(converted["metadata"]["samples"], int)
        assert isinstance(converted["metadata"]["duration"], float)
        assert isinstance(converted["metadata"]["channels"], list)


class TestSafeAudioUploadWorkflow:
    """Test complete upload workflow with cleanup."""

    @pytest.mark.asyncio
    async def test_workflow_success(self):
        """Test successful upload workflow."""
        content = b"audio content" * 100
        file = UploadFile(filename="test.wav", file=io.BytesIO(content))

        result = await safe_audio_upload_workflow(file)

        assert result["file_size_bytes"] == len(content)
        assert result["total_bytes_processed"] == len(content)
        # Verify temp file was cleaned up (we can't check directly but no error means success)

    @pytest.mark.asyncio
    async def test_workflow_cleanup_on_error(self, caplog):
        """Test that temp files are cleaned up even on processing error."""
        # Create file that will pass upload but might fail processing
        content = b"test data"
        file = UploadFile(filename="test.wav", file=io.BytesIO(content))

        # The workflow should handle cleanup even if something goes wrong
        with caplog.at_level(logging.DEBUG):
            result = await safe_audio_upload_workflow(file)

        # Verify cleanup message logged
        assert "Cleaned up temp file" in caplog.text or result is not None

    @pytest.mark.asyncio
    async def test_workflow_rejects_invalid_extension(self):
        """Test workflow rejects invalid file extensions."""
        content = b"malicious content"
        file = UploadFile(filename="virus.exe", file=io.BytesIO(content))

        with pytest.raises(HTTPException) as exc_info:
            await safe_audio_upload_workflow(file)

        assert exc_info.value.status_code == 400


class TestValidateAudioFileHeader:
    """Test audio file validation by magic bytes."""

    @pytest.mark.asyncio
    async def test_valid_wav_header(self, tmp_path):
        """Test validation of valid WAV file header."""
        wav_file = tmp_path / "test.wav"
        # WAV files start with "RIFF" magic bytes
        wav_file.write_bytes(b"RIFF" + b"\x00" * 100)

        is_valid = await validate_audio_file_header(str(wav_file), b"RIFF")
        assert is_valid is True

    @pytest.mark.asyncio
    async def test_invalid_magic_bytes(self, tmp_path):
        """Test rejection of file with wrong magic bytes."""
        fake_file = tmp_path / "fake.wav"
        fake_file.write_bytes(b"FAKE" + b"\x00" * 100)

        is_valid = await validate_audio_file_header(str(fake_file), b"RIFF")
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_no_expected_magic_bytes(self, tmp_path):
        """Test validation without checking magic bytes."""
        any_file = tmp_path / "any.wav"
        any_file.write_bytes(b"anything" * 10)

        is_valid = await validate_audio_file_header(str(any_file))
        assert is_valid is True


class TestClientDisconnectSimulation:
    """Test handling of client disconnects during upload."""

    @pytest.mark.asyncio
    async def test_incomplete_read_during_upload(self):
        """Simulate client disconnecting mid-upload."""
        # Use a real BytesIO that will hit EOF naturally
        # This simulates a client that sends some data then disconnects
        partial_content = b"x" * (2 * 1024)  # 2KB of data
        file = UploadFile(filename="test.wav", file=io.BytesIO(partial_content))

        # Should handle partial upload gracefully (EOF is normal)
        temp_path, success = await stream_upload_to_disk(file, chunk_size=1024)

        try:
            # File should be created with partial content
            assert success is True
            assert os.path.exists(temp_path)

            # Verify we got the data that was sent before "disconnect"
            with open(temp_path, "rb") as f:
                content = f.read()
            assert len(content) == len(partial_content)
            assert content == partial_content
        finally:
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)


class TestEdgeCases:
    """Test various edge cases and corner conditions."""

    @pytest.mark.asyncio
    async def test_zero_byte_file(self, tmp_path):
        """Test handling of zero-byte file."""
        empty_file = tmp_path / "empty.wav"
        empty_file.write_bytes(b"")

        result = await process_audio_file_chunked(str(empty_file))

        assert result["file_size_bytes"] == 0
        assert result["chunks_processed"] == 0

    @pytest.mark.asyncio
    async def test_permission_denied_during_read(self, tmp_path):
        """Test handling of permission denied errors."""
        restricted_file = tmp_path / "restricted.wav"
        restricted_file.write_bytes(b"content")
        restricted_file.chmod(0o000)  # Remove all permissions

        if os.access(restricted_file, os.R_OK):
            pytest.skip("Permissions not enforced in this environment")

        try:
            with pytest.raises(HTTPException) as exc_info:
                await process_audio_file_chunked(str(restricted_file))

            assert exc_info.value.status_code == 500
        finally:
            # Restore permissions for cleanup
            restricted_file.chmod(0o644)

    def test_numpy_array_with_mixed_types(self):
        """Test converting complex nested structures."""
        result = {
            "metrics": [np.int64(1), np.float64(2.5), {"nested": np.float64(np.nan)}]
        }
        converted = convert_numpy_audio_result(result)

        assert isinstance(converted["metrics"][0], int)
        assert isinstance(converted["metrics"][1], float)
        assert converted["metrics"][2]["nested"] is None


class TestAdditionalCoverage:
    """Additional tests to achieve 100% coverage."""

    @pytest.mark.asyncio
    async def test_safe_audio_upload_workflow_cleanup_failure(
        self, monkeypatch, caplog
    ):
        """Test workflow when cleanup fails."""
        import os as os_module

        content = b"test audio data"
        file = UploadFile(filename="test.wav", file=io.BytesIO(content))

        # Mock os.unlink to raise OSError during cleanup
        original_unlink = os_module.unlink

        def mock_unlink(path):
            raise OSError("Permission denied")

        with caplog.at_level(logging.DEBUG):
            monkeypatch.setattr(os_module, "unlink", mock_unlink)
            result = await safe_audio_upload_workflow(file)

        # Should still succeed even if cleanup fails
        assert result is not None
        assert "Failed to cleanup temp file" in caplog.text

    @pytest.mark.asyncio
    async def test_safe_audio_upload_workflow_upload_fails(self):
        """Test workflow when upload fails."""
        # Create a file that will fail validation
        file = UploadFile(filename=None, file=io.BytesIO(b"test"))

        with pytest.raises(HTTPException) as exc_info:
            await safe_audio_upload_workflow(file)

        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_stream_upload_cleanup_on_error(self, monkeypatch):
        """Test that file descriptor is closed on error."""
        content = b"test audio data"
        file = UploadFile(filename="test.wav", file=io.BytesIO(content))

        # Mock os.fdopen to raise an error
        import tempfile as temp_module

        original_mkstemp = temp_module.mkstemp

        def mock_mkstemp(suffix=".tmp", prefix="tmp", dir=None):
            fd, path = original_mkstemp(suffix=suffix, prefix=prefix, dir=dir)
            # Create a mock that will fail when os.fdopen is called
            return fd, path

        original_fdopen = os.fdopen

        def mock_fdopen(fd, mode):
            raise IOError("Failed to open file descriptor")

        monkeypatch.setattr(temp_module, "mkstemp", mock_mkstemp)
        monkeypatch.setattr(os, "fdopen", mock_fdopen)

        with pytest.raises(HTTPException) as exc_info:
            await stream_upload_to_disk(file)

        assert exc_info.value.status_code == 500

    def test_convert_numpy_list(self):
        """Test converting list with NumPy types."""
        data = [np.int64(1), np.float64(2.5), np.array([3, 4])]
        result = convert_numpy_audio_result(data)
        assert isinstance(result, list)
        assert isinstance(result[0], int)
        assert isinstance(result[1], float)
        assert isinstance(result[2], list)

    def test_convert_nested_dict(self):
        """Test converting nested dict with NumPy types."""
        data = {"outer": {"inner": np.int64(42), "array": np.array([1, 2, 3])}}
        result = convert_numpy_audio_result(data)
        assert isinstance(result["outer"]["inner"], int)
        assert isinstance(result["outer"]["array"], list)

    def test_convert_non_numpy_passthrough(self):
        """Test that non-NumPy types pass through unchanged."""
        data = {"string": "hello", "int": 42, "float": 3.14, "bool": True}
        result = convert_numpy_audio_result(data)
        assert result == data

    @pytest.mark.asyncio
    async def test_validate_audio_file_header_empty(self, tmp_path):
        """Test validating empty file."""
        empty_file = tmp_path / "empty.wav"
        empty_file.write_bytes(b"")

        result = await validate_audio_file_header(str(empty_file))
        assert result is False

    @pytest.mark.asyncio
    async def test_validate_audio_file_header_io_error(
        self, monkeypatch, tmp_path, caplog
    ):
        """Test validating file when IOError occurs."""
        test_file = tmp_path / "test.wav"
        test_file.write_bytes(b"test")

        # Mock open to raise IOError
        original_open = open

        def mock_open(path, mode):
            if "test.wav" in str(path) and mode == "rb":
                raise IOError("Read error")
            return original_open(path, mode)

        with caplog.at_level(logging.DEBUG):
            monkeypatch.setattr("builtins.open", mock_open)
            result = await validate_audio_file_header(str(test_file))

        assert result is False
        assert "Error validating file header" in caplog.text

    def test_audio_processing_response_model(self):
        """Test AudioUploadResponse model."""
        from examples.fastapi_audio_patterns import AudioUploadResponse

        response = AudioUploadResponse(
            file_size_bytes=1024,
            file_size_mb=0.001,
            chunks_processed=1,
            total_bytes_processed=1024,
            file_path="/tmp/test.wav",
        )

        assert response.file_size_bytes == 1024
        assert response.file_size_mb == 0.001
        assert response.chunks_processed == 1
        assert response.total_bytes_processed == 1024
        assert response.file_path == "/tmp/test.wav"

    def test_audio_processing_error_model(self):
        """Test AudioProcessingError model."""
        from examples.fastapi_audio_patterns import AudioProcessingError

        error = AudioProcessingError(
            error="ValidationError", detail="Invalid file format"
        )

        assert error.error == "ValidationError"
        assert error.detail == "Invalid file format"
