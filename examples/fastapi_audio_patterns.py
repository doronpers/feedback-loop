"""
FastAPI Audio Processing Patterns - Best Practices for Large File Handling

This module demonstrates production-ready patterns for handling massive audio files
(up to 800MB) in FastAPI backends, addressing common pitfalls that AI often creates.

Key Constraints Addressed:
- Memory: Prevent OOM errors by streaming files instead of loading into memory
- Network: Handle nginx client_max_body_size and timeout configurations
- Cleanup: Ensure ephemeral storage is properly managed in Docker containers
- Security: Validate file types, sizes, and handle path traversal attacks
"""

import logging
import os
import tempfile
from typing import Any, Dict, Optional, Tuple
import numpy as np
from fastapi import UploadFile, HTTPException
from pathlib import Path

logger = logging.getLogger(__name__)


async def stream_upload_to_disk(
    file: UploadFile,
    max_size_bytes: int = 800 * 1024 * 1024,  # 800MB default
    chunk_size: int = 1024 * 1024,  # 1MB chunks
    allowed_extensions: Optional[Tuple[str, ...]] = None
) -> Tuple[str, bool]:
    """
    Stream large file uploads directly to disk without loading into memory.
    
    This is the CRITICAL pattern AI often gets wrong by using file.read()
    which crashes on 800MB payloads. This uses manual chunking with async reads.
    
    Args:
        file: FastAPI UploadFile object
        max_size_bytes: Maximum allowed file size (default 800MB)
        chunk_size: Size of chunks for streaming (default 1MB)
        allowed_extensions: Tuple of allowed file extensions (e.g., ('.wav', '.mp3'))
        
    Returns:
        Tuple of (temp_file_path, success)
        
    Raises:
        HTTPException: For validation failures (size, type, etc.)
    """
    # GOOD: Validate file extension before processing
    if allowed_extensions:
        file_ext = Path(file.filename).suffix.lower() if file.filename else ""
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {allowed_extensions}"
            )
    
    fd = None
    path = None
    bytes_written = 0
    
    try:
        # GOOD: Use mkstemp for secure temp file creation
        fd, path = tempfile.mkstemp(suffix=".tmp")
        
        # GOOD: Stream file in chunks using manual async reads
        # This prevents loading entire 800MB file into memory
        with os.fdopen(fd, 'wb') as tmp_file:
            fd = None  # fd now managed by file object
            
            # Stream file contents chunk by chunk
            while True:
                chunk = await file.read(chunk_size)
                if not chunk:
                    break
                
                bytes_written += len(chunk)
                
                # GOOD: Check size limit during streaming
                if bytes_written > max_size_bytes:
                    raise HTTPException(
                        status_code=413,
                        detail=f"File too large. Max size: {max_size_bytes} bytes"
                    )
                
                tmp_file.write(chunk)
        
        logger.debug(f"Successfully streamed {bytes_written} bytes to {path}")
        return path, True
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except (IOError, OSError) as e:
        logger.debug(f"Failed to stream file: {e}")
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")
    finally:
        # GOOD: Cleanup on error
        if fd is not None:
            try:
                os.close(fd)
            except OSError:
                pass


async def process_audio_file_chunked(
    file_path: str,
    chunk_size: int = 1024 * 1024  # 1MB chunks
) -> Dict[str, Any]:
    """
    Process audio file in chunks to avoid memory exhaustion.
    
    This demonstrates chunked reading for actual audio processing
    (not just metadata extraction). Prevents 800MB files from crashing servers.
    
    Args:
        file_path: Path to the audio file
        chunk_size: Size of chunks for reading (default 1MB)
        
    Returns:
        Dictionary with processing results
    """
    try:
        file_size = os.path.getsize(file_path)
        chunks_processed = 0
        total_bytes = 0
        
        # GOOD: Read and process file in chunks
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                
                # Process chunk (example: just count bytes)
                # In production: decode audio, apply DSP, etc.
                total_bytes += len(chunk)
                chunks_processed += 1
        
        # GOOD: Return JSON-safe native Python types (not NumPy)
        return {
            "file_path": file_path,
            "file_size_bytes": int(file_size),
            "file_size_mb": float(file_size / (1024 * 1024)),
            "chunks_processed": int(chunks_processed),
            "total_bytes_processed": int(total_bytes)
        }
        
    except FileNotFoundError:
        logger.debug(f"File not found: {file_path}")
        raise HTTPException(status_code=404, detail="File not found")
    except (IOError, OSError) as e:
        logger.debug(f"Error processing file: {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


async def safe_audio_upload_workflow(
    file: UploadFile,
    max_size_bytes: int = 800 * 1024 * 1024
) -> Dict[str, Any]:
    """
    Complete workflow for safe audio file upload and processing.
    
    Demonstrates the full pattern:
    1. Stream upload to disk (prevents OOM)
    2. Process in chunks (memory-safe)
    3. Cleanup temp files (prevents disk leaks)
    
    This is the pattern to use in production FastAPI endpoints.
    
    Args:
        file: FastAPI UploadFile object
        max_size_bytes: Maximum allowed file size
        
    Returns:
        Dictionary with processing results
    """
    temp_path = None
    
    try:
        # Step 1: Stream upload to disk
        temp_path, success = await stream_upload_to_disk(
            file,
            max_size_bytes=max_size_bytes,
            allowed_extensions=('.wav', '.mp3', '.flac', '.ogg')
        )
        
        if not success or not temp_path:
            raise HTTPException(status_code=500, detail="Upload failed")
        
        # Step 2: Process file in chunks
        result = await process_audio_file_chunked(temp_path)
        
        return result
        
    finally:
        # Step 3: CRITICAL - Always cleanup temp files
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
                logger.debug(f"Cleaned up temp file: {temp_path}")
            except OSError as e:
                logger.debug(f"Failed to cleanup temp file {temp_path}: {e}")


def convert_numpy_audio_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert audio processing results containing NumPy types to JSON-safe types.
    
    AI often returns NumPy types from audio processing (sample rates, durations, etc.)
    which cause JSON serialization errors. This ensures everything is JSON-safe.
    
    Args:
        result: Dictionary potentially containing NumPy types
        
    Returns:
        Dictionary with all NumPy types converted to native Python types
    """
    def convert_value(val: Any) -> Any:
        """Recursively convert NumPy types to Python native types."""
        if isinstance(val, np.integer):
            return int(val)
        elif isinstance(val, np.floating):
            # GOOD: Handle NaN and Inf values
            if np.isnan(val):
                return None  # or "NaN" depending on API contract
            elif np.isinf(val):
                return None  # or "Infinity" depending on API contract
            return float(val)
        elif isinstance(val, np.ndarray):
            return val.tolist()
        elif isinstance(val, dict):
            return {k: convert_value(v) for k, v in val.items()}
        elif isinstance(val, list):
            return [convert_value(item) for item in val]
        return val
    
    return convert_value(result)


async def validate_audio_file_header(
    file_path: str,
    expected_magic_bytes: Optional[bytes] = None
) -> bool:
    """
    Validate audio file by checking magic bytes without loading entire file.
    
    Security pattern: Prevent attacks where non-audio files are uploaded
    with audio extensions. Only reads first few bytes.
    
    Args:
        file_path: Path to the file to validate
        expected_magic_bytes: Expected magic bytes for file type (e.g., b'RIFF' for WAV)
        
    Returns:
        True if valid, False otherwise
    """
    try:
        # GOOD: Only read first bytes for validation
        with open(file_path, 'rb') as f:
            header = f.read(12)  # Read enough for most audio formats
        
        if expected_magic_bytes and not header.startswith(expected_magic_bytes):
            logger.debug(f"Invalid magic bytes in {file_path}")
            return False
        
        return True
        
    except (IOError, OSError) as e:
        logger.debug(f"Error validating file header: {e}")
        return False


# Example Pydantic models for FastAPI endpoints
from typing import Optional as OptionalType


class AudioUploadResponse:
    """Response model for audio upload endpoint."""
    
    def __init__(
        self,
        file_size_bytes: int,
        file_size_mb: float,
        chunks_processed: int,
        total_bytes_processed: int,
        file_path: OptionalType[str] = None
    ):
        self.file_size_bytes = file_size_bytes
        self.file_size_mb = file_size_mb
        self.chunks_processed = chunks_processed
        self.total_bytes_processed = total_bytes_processed
        self.file_path = file_path


class AudioProcessingError:
    """Error response model for audio processing failures."""
    
    def __init__(self, error: str, detail: str):
        self.error = error
        self.detail = detail
