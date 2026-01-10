#!/usr/bin/env python3
"""
Demo for FastAPI Audio Processing Patterns

Demonstrates the complete workflow for handling 800MB audio files safely.
Shows all patterns from the problem statement implemented.
"""

import asyncio
import io
import logging
import os
import tempfile

import numpy as np
from fastapi import UploadFile

from examples.fastapi_audio_patterns import (convert_numpy_audio_result,
                                             process_audio_file_chunked,
                                             safe_audio_upload_workflow,
                                             stream_upload_to_disk,
                                             validate_audio_file_header)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG, format="%(levelname)s - %(name)s - %(message)s"
)


async def demo_streaming_upload():
    """Demo 1: Streaming file upload (prevents OOM on 800MB files)."""
    print("\n" + "=" * 70)
    print("Demo 1: Streaming File Upload (Memory-Safe for 800MB files)")
    print("=" * 70)

    # Simulate a 5MB upload
    content = b"audio data content " * (5 * 1024 * 1024 // 20)
    file = UploadFile(filename="test_audio.wav", file=io.BytesIO(content))

    print(f"Uploading file: {file.filename}")
    print(f"File size: {len(content) / (1024*1024):.2f} MB")

    temp_path, success = await stream_upload_to_disk(file)

    try:
        print(f"Upload success: {success}")
        print(f"Temp file path: {temp_path}")
        print(f"File exists: {os.path.exists(temp_path)}")
        print("✅ File streamed to disk without loading into memory!")

        # Verify
        actual_size = os.path.getsize(temp_path)
        print(f"Verified file size on disk: {actual_size / (1024*1024):.2f} MB")
    finally:
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)


async def demo_chunked_processing():
    """Demo 2: Chunked file processing (memory-safe)."""
    print("\n" + "=" * 70)
    print("Demo 2: Chunked Audio Processing")
    print("=" * 70)

    # Create a test file
    fd, test_path = tempfile.mkstemp(suffix=".wav")
    try:
        # Write 10MB test file
        test_data = b"x" * (10 * 1024 * 1024)
        with os.fdopen(fd, "wb") as f:
            f.write(test_data)

        print(f"Processing file: {test_path}")
        print(f"File size: {len(test_data) / (1024*1024):.2f} MB")

        result = await process_audio_file_chunked(test_path, chunk_size=1024 * 1024)

        print(f"\nProcessing results:")
        print(f"  - Chunks processed: {result['chunks_processed']}")
        print(f"  - Total bytes: {result['total_bytes_processed']}")
        print(f"  - Size (MB): {result['file_size_mb']:.2f}")
        print("✅ File processed in chunks without memory exhaustion!")

    finally:
        if os.path.exists(test_path):
            os.unlink(test_path)


async def demo_complete_workflow():
    """Demo 3: Complete upload + process + cleanup workflow."""
    print("\n" + "=" * 70)
    print("Demo 3: Complete Safe Audio Upload Workflow")
    print("=" * 70)

    # Simulate audio file upload
    content = b"audio content " * 1000
    file = UploadFile(filename="recording.wav", file=io.BytesIO(content))

    print(f"Starting workflow for: {file.filename}")

    result = await safe_audio_upload_workflow(file)

    print(f"\nWorkflow completed successfully!")
    print(f"  - File size: {result['file_size_mb']:.2f} MB")
    print(f"  - Chunks processed: {result['chunks_processed']}")
    print("✅ Complete workflow: upload → process → cleanup!")


def demo_numpy_nan_inf_handling():
    """Demo 4: Handling NaN and Inf values in audio processing."""
    print("\n" + "=" * 70)
    print("Demo 4: NumPy NaN/Inf Handling (Critical for Audio)")
    print("=" * 70)

    # Simulate audio processing results with edge cases
    audio_result = {
        "sample_rate": np.int64(44100),
        "duration": np.float64(5.5),
        "peak_amplitude": np.float64(np.nan),  # Could happen with silent audio
        "rms": np.float64(0.125),
        "clipping_count": np.int64(0),
        "overflow_metric": np.float64(np.inf),  # Could happen with bad computation
    }

    print("Raw audio processing result (with NumPy types):")
    for key, value in audio_result.items():
        print(f"  {key}: {value} (type: {type(value).__name__})")

    # Convert for JSON safety
    safe_result = convert_numpy_audio_result(audio_result)

    print("\nSafe result (JSON-serializable, NaN/Inf handled):")
    for key, value in safe_result.items():
        print(f"  {key}: {value} (type: {type(value).__name__})")

    print("✅ NaN and Inf values handled safely for JSON APIs!")


async def demo_file_validation():
    """Demo 5: File type validation with magic bytes."""
    print("\n" + "=" * 70)
    print("Demo 5: Audio File Validation (Security)")
    print("=" * 70)

    # Create test files
    fd1, wav_path = tempfile.mkstemp(suffix=".wav")
    fd2, fake_path = tempfile.mkstemp(suffix=".wav")

    try:
        # Valid WAV file (starts with RIFF)
        with os.fdopen(fd1, "wb") as f:
            f.write(b"RIFF" + b"\x00" * 100)

        # Invalid file pretending to be WAV
        with os.fdopen(fd2, "wb") as f:
            f.write(b"FAKE" + b"\x00" * 100)

        print("Validating files:")

        is_valid_wav = await validate_audio_file_header(wav_path, b"RIFF")
        print(f"  Real WAV file: {'✓ Valid' if is_valid_wav else '✗ Invalid'}")

        is_valid_fake = await validate_audio_file_header(fake_path, b"RIFF")
        print(f"  Fake WAV file: {'✓ Valid' if is_valid_fake else '✗ Invalid'}")

        print("✅ File type validation prevents malicious uploads!")

    finally:
        for path in [wav_path, fake_path]:
            if os.path.exists(path):
                os.unlink(path)


async def main():
    """Run all demonstrations."""
    print("\n" + "=" * 70)
    print("FastAPI Audio Processing Patterns - Live Demo")
    print("Handling 800MB Files Safely")
    print("=" * 70)

    await demo_streaming_upload()
    await demo_chunked_processing()
    await demo_complete_workflow()
    demo_numpy_nan_inf_handling()
    await demo_file_validation()

    print("\n" + "=" * 70)
    print("All Demos Complete!")
    print("=" * 70)
    print("\n✅ All patterns demonstrated successfully!")
    print("\nKey Takeaways:")
    print("1. Stream files to disk (never use file.read() for large files)")
    print("2. Process in chunks (1MB chunks for 800MB files)")
    print("3. Always cleanup temp files (use try/finally)")
    print("4. Handle NaN/Inf in audio processing results")
    print("5. Validate file types before processing")
    print("\nConfiguration Required:")
    print("- nginx: client_max_body_size 800M")
    print("- Docker: RUN apk add --no-cache ca-certificates")
    print("\nSee examples/ for complete FastAPI application.")


if __name__ == "__main__":
    asyncio.run(main())
