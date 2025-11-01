"""Dependency injection functions."""

from fastapi import Depends, Header, Request
from typing import Optional

from app.config import Settings, get_settings
from app.core.gemini_client import GeminiClient
from app.core.rate_limiter import RateLimiter, get_rate_limiter
from app.services.cache_service import CacheService, get_cache_service
from app.services.text_service import TextService
from app.services.image_service import ImageService
from app.services.audio_service import AudioService
from app.services.video_service import VideoService


# Global client instance
_gemini_client: Optional[GeminiClient] = None


async def get_gemini_client(
    settings: Settings = Depends(get_settings),
) -> GeminiClient:
    """
    Get Gemini client instance.

    Args:
        settings: Application settings

    Returns:
        GeminiClient: Gemini client instance

    Example:
        ```python
        client = await get_gemini_client()
        ```
    """
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = GeminiClient(
            api_key=settings.GOOGLE_API_KEY,
            settings=settings,
        )
    return _gemini_client


def get_text_service(
    client: GeminiClient = Depends(get_gemini_client),
    cache: CacheService = Depends(get_cache_service),
) -> TextService:
    """
    Get text service instance.

    Args:
        client: Gemini client
        cache: Cache service

    Returns:
        TextService: Text service instance
    """
    return TextService(client=client, cache=cache)


def get_image_service(
    client: GeminiClient = Depends(get_gemini_client),
) -> ImageService:
    """
    Get image service instance.

    Args:
        client: Gemini client

    Returns:
        ImageService: Image service instance
    """
    return ImageService(client=client)


def get_audio_service(
    client: GeminiClient = Depends(get_gemini_client),
) -> AudioService:
    """
    Get audio service instance.

    Args:
        client: Gemini client

    Returns:
        AudioService: Audio service instance
    """
    return AudioService(client=client)


def get_video_service(
    client: GeminiClient = Depends(get_gemini_client),
) -> VideoService:
    """
    Get video service instance.

    Args:
        client: Gemini client

    Returns:
        VideoService: Video service instance
    """
    return VideoService(client=client)


def get_cache_service_dep() -> CacheService:
    """
    Get cache service dependency.

    Returns:
        CacheService: Cache service instance
    """
    return get_cache_service()


async def verify_api_key(
    api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> Optional[str]:
    """
    Optional API key verification (for future use).

    Args:
        api_key: API key from header

    Returns:
        Optional[str]: API key if provided

    Example:
        ```python
        api_key = await verify_api_key()
        ```
    """
    # Placeholder for API key verification
    return api_key

