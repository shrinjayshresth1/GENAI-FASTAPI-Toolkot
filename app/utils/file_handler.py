"""File handling utilities for uploads and processing."""

import base64
import logging
import os
import tempfile
from io import BytesIO
from pathlib import Path
from typing import List, Optional

from fastapi import UploadFile
from PIL import Image as PILImage

from app.config import Settings, get_settings
from app.core.exceptions import FileProcessingError

logger = logging.getLogger(__name__)


async def validate_file(
    file: UploadFile,
    max_size_mb: int,
    allowed_types: List[str],
    settings: Optional[Settings] = None,
) -> None:
    """
    Validate uploaded file.

    Args:
        file: FastAPI UploadFile
        max_size_mb: Maximum file size in MB
        allowed_types: List of allowed MIME types
        settings: Application settings (optional)

    Raises:
        FileProcessingError: If file is invalid

    Example:
        ```python
        await validate_file(
            file,
            max_size_mb=10,
            allowed_types=["image/jpeg", "image/png"]
        )
        ```
    """
    settings = settings or get_settings()

    # Check file size
    file.seek(0, 2)  # Seek to end
    file_size = file.tell()
    file.seek(0)  # Reset to start

    max_size_bytes = max_size_mb * 1024 * 1024
    if file_size > max_size_bytes:
        raise FileProcessingError(
            f"File size {file_size / (1024*1024):.2f}MB exceeds maximum of {max_size_mb}MB",
            file_type=file.content_type,
        )

    # Check MIME type
    if file.content_type not in allowed_types:
        raise FileProcessingError(
            f"File type '{file.content_type}' not allowed. Allowed types: {', '.join(allowed_types)}",
            file_type=file.content_type,
        )

    logger.info(f"File validated: {file.filename}, size: {file_size} bytes, type: {file.content_type}")


async def process_image(contents: bytes) -> PILImage.Image:
    """
    Process image bytes into PIL Image.

    Args:
        contents: Image bytes

    Returns:
        PILImage.Image: PIL Image object

    Raises:
        FileProcessingError: If image processing fails

    Example:
        ```python
        with open("image.jpg", "rb") as f:
            image_bytes = f.read()
        image = await process_image(image_bytes)
        ```
    """
    try:
        image = PILImage.open(BytesIO(contents))
        # Convert to RGB if necessary
        if image.mode not in ("RGB", "RGBA"):
            image = image.convert("RGB")
        return image
    except Exception as e:
        logger.error(f"Image processing failed: {e}", exc_info=True)
        raise FileProcessingError(f"Failed to process image: {str(e)}", file_type="image") from e


async def encode_image_base64(image: PILImage.Image) -> str:
    """
    Encode PIL Image to base64 string.

    Args:
        image: PIL Image object

    Returns:
        str: Base64 encoded image string

    Example:
        ```python
        base64_str = await encode_image_base64(image)
        ```
    """
    try:
        buffer = BytesIO()
        image.save(buffer, format="JPEG")
        image_bytes = buffer.getvalue()
        return base64.b64encode(image_bytes).decode("utf-8")
    except Exception as e:
        logger.error(f"Base64 encoding failed: {e}", exc_info=True)
        raise FileProcessingError(f"Failed to encode image: {str(e)}", file_type="image") from e


async def save_temp_file(file: UploadFile, suffix: Optional[str] = None) -> str:
    """
    Save uploaded file temporarily and return path.

    Args:
        file: FastAPI UploadFile
        suffix: Optional file suffix (e.g., '.jpg')

    Returns:
        str: Path to temporary file

    Example:
        ```python
        temp_path = await save_temp_file(file, suffix=".mp4")
        try:
            # Process file
        finally:
            await cleanup_temp_file(temp_path)
        ```
    """
    try:
        contents = await file.read()
        file_extension = suffix or Path(file.filename or "temp").suffix

        # Create temporary file
        temp_fd, temp_path = tempfile.mkstemp(suffix=file_extension)
        with os.fdopen(temp_fd, "wb") as temp_file:
            temp_file.write(contents)

        logger.info(f"Saved temporary file: {temp_path}")
        return temp_path
    except Exception as e:
        logger.error(f"Failed to save temporary file: {e}", exc_info=True)
        raise FileProcessingError(f"Failed to save file: {str(e)}", file_type=file.content_type) from e


async def cleanup_temp_file(path: str) -> None:
    """
    Clean up temporary file.

    Args:
        path: Path to temporary file

    Example:
        ```python
        await cleanup_temp_file("/tmp/file123.mp4")
        ```
    """
    try:
        if os.path.exists(path):
            os.remove(path)
            logger.info(f"Cleaned up temporary file: {path}")
    except Exception as e:
        logger.warning(f"Failed to cleanup temporary file {path}: {e}")


async def read_file_bytes(file_path: str) -> bytes:
    """
    Read file as bytes.

    Args:
        file_path: Path to file

    Returns:
        bytes: File contents

    Raises:
        FileProcessingError: If file reading fails

    Example:
        ```python
        contents = await read_file_bytes("video.mp4")
        ```
    """
    try:
        with open(file_path, "rb") as f:
            return f.read()
    except Exception as e:
        logger.error(f"Failed to read file {file_path}: {e}", exc_info=True)
        raise FileProcessingError(f"Failed to read file: {str(e)}") from e


def get_file_extension(filename: str) -> str:
    """
    Get file extension from filename.

    Args:
        filename: Filename

    Returns:
        str: File extension (including dot)

    Example:
        ```python
        ext = get_file_extension("image.jpg")  # Returns ".jpg"
        ```
    """
    return Path(filename).suffix.lower()


def is_image_file(filename: str) -> bool:
    """
    Check if file is an image based on extension.

    Args:
        filename: Filename

    Returns:
        bool: True if image file

    Example:
        ```python
        if is_image_file("photo.jpg"):
            # Process as image
        ```
    """
    image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}
    return get_file_extension(filename) in image_extensions


def is_video_file(filename: str) -> bool:
    """
    Check if file is a video based on extension.

    Args:
        filename: Filename

    Returns:
        bool: True if video file

    Example:
        ```python
        if is_video_file("clip.mp4"):
            # Process as video
        ```
    """
    video_extensions = {".mp4", ".avi", ".mov", ".mkv", ".webm", ".flv"}
    return get_file_extension(filename) in video_extensions


def is_audio_file(filename: str) -> bool:
    """
    Check if file is audio based on extension.

    Args:
        filename: Filename

    Returns:
        bool: True if audio file

    Example:
        ```python
        if is_audio_file("song.mp3"):
            # Process as audio
        ```
    """
    audio_extensions = {".mp3", ".wav", ".ogg", ".flac", ".aac", ".m4a"}
    return get_file_extension(filename) in audio_extensions

