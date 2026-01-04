"""
Example FastAPI Application - Audio Processing API

Demonstrates production-ready patterns for handling large audio file uploads
with proper memory management, error handling, and cleanup.

nginx Configuration Required:
    server {
        client_max_body_size 800M;
        client_body_timeout 300s;
        proxy_read_timeout 300s;
    }

Docker Configuration Required:
    FROM python:3.11-alpine
    RUN apk add --no-cache ca-certificates  # Critical for SSL/HTTPS
    ...
"""

import logging
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from examples.fastapi_audio_patterns import (
    safe_audio_upload_workflow,
    convert_numpy_audio_result
)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Audio Processing API",
    description="Production-ready API for processing large audio files (up to 800MB)",
    version="1.0.0"
)


@app.post("/api/v1/audio/upload")
async def upload_audio_file(
    file: UploadFile = File(..., description="Audio file to process (WAV, MP3, FLAC, OGG)")
):
    """
    Upload and process audio file with streaming to prevent OOM errors.
    
    This endpoint demonstrates the complete pattern:
    1. Stream file to disk (no memory loading)
    2. Process in chunks (memory-safe)
    3. Auto-cleanup temp files
    4. JSON-safe responses (NumPy types converted)
    
    Maximum file size: 800MB
    Supported formats: .wav, .mp3, .flac, .ogg
    
    Returns:
        Processing results including file size, chunks processed, etc.
        
    Raises:
        HTTPException: For validation errors, size limits, or processing failures
    """
    try:
        logger.info(f"Receiving audio upload: {file.filename}")
        
        # Use the safe workflow pattern
        result = await safe_audio_upload_workflow(
            file,
            max_size_bytes=800 * 1024 * 1024  # 800MB
        )
        
        # GOOD: Ensure NumPy types are converted for JSON response
        safe_result = convert_numpy_audio_result(result)
        
        logger.info(f"Successfully processed {file.filename}: {safe_result['file_size_mb']:.2f} MB")
        return JSONResponse(content=safe_result, status_code=200)
        
    except HTTPException:
        # Re-raise HTTP exceptions with their original status codes
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing {file.filename}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/api/v1/health")
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    
    Returns:
        Status message
    """
    return {"status": "healthy", "service": "audio-processing-api"}


@app.get("/api/v1/config")
async def get_configuration():
    """
    Get API configuration limits.
    
    Returns:
        Configuration including max file size, supported formats, etc.
    """
    return {
        "max_file_size_mb": 800,
        "max_file_size_bytes": 800 * 1024 * 1024,
        "supported_formats": [".wav", ".mp3", ".flac", ".ogg"],
        "chunk_size_mb": 1,
        "processing_mode": "streaming"
    }


# Error handlers for common issues
@app.exception_handler(413)
async def request_entity_too_large_handler(request, exc):
    """Handle file too large errors."""
    return JSONResponse(
        status_code=413,
        content={
            "error": "File too large",
            "detail": "Maximum file size is 800MB",
            "max_size_bytes": 800 * 1024 * 1024
        }
    )


@app.exception_handler(400)
async def bad_request_handler(request, exc):
    """Handle bad request errors."""
    return JSONResponse(
        status_code=400,
        content={
            "error": "Bad request",
            "detail": str(exc.detail) if hasattr(exc, 'detail') else "Invalid request"
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    # Run with: python examples/fastapi_audio_example.py
    # Or: uvicorn examples.fastapi_audio_example:app --reload
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="debug"
    )
