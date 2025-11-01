"""Health check and system information endpoints."""

import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.config import Settings, get_settings
from app.core.gemini_client import GeminiClient
from app.dependencies import get_gemini_client

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str


class TokenCountRequest(BaseModel):
    """Request for token counting."""

    text: str


class TokenCountResponse(BaseModel):
    """Token count response."""

    token_count: int
    text_length: int
    model: str


@router.get("/health", response_model=HealthResponse)
async def health_check(settings: Settings = Depends(get_settings)) -> HealthResponse:
    """
    Basic health check endpoint.

    Returns:
        HealthResponse: Health status

    Example:
        ```bash
        curl http://localhost:8000/health
        ```
    """
    return HealthResponse(
        status="healthy",
        version=settings.API_VERSION,
    )


@router.get("/health/ready", response_model=HealthResponse)
async def readiness_check(
    client: GeminiClient = Depends(get_gemini_client),
) -> HealthResponse:
    """
    Readiness probe - checks if service can handle requests.

    Returns:
        HealthResponse: Readiness status

    Raises:
        HTTPException: If service is not ready

    Example:
        ```bash
        curl http://localhost:8000/health/ready
        ```
    """
    try:
        # Test API connection
        await client.count_tokens("test")
        return HealthResponse(status="ready", version="1.0.0")
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service not ready",
        )


@router.get("/health/live", response_model=HealthResponse)
async def liveness_check() -> HealthResponse:
    """
    Liveness probe - checks if service is alive.

    Returns:
        HealthResponse: Liveness status

    Example:
        ```bash
        curl http://localhost:8000/health/live
        ```
    """
    return HealthResponse(status="alive", version="1.0.0")


@router.get("/models")
async def list_models(settings: Settings = Depends(get_settings)) -> Dict[str, str]:
    """
    List available models.

    Returns:
        Dict[str, str]: Available models

    Example:
        ```bash
        curl http://localhost:8000/models
        ```
    """
    return {
        "text": settings.GEMINI_MODEL_TEXT,
        "vision": settings.GEMINI_MODEL_VISION,
        "audio": settings.GEMINI_MODEL_AUDIO,
    }


@router.post("/tokens/count", response_model=TokenCountResponse)
async def count_tokens(
    request: TokenCountRequest,
    client: GeminiClient = Depends(get_gemini_client),
) -> TokenCountResponse:
    """
    Count tokens in text.

    Args:
        request: Token count request
        client: Gemini client

    Returns:
        TokenCountResponse: Token count result

    Example:
        ```python
        response = requests.post(
            "http://localhost:8000/tokens/count",
            json={"text": "Hello world"}
        )
        ```
    """
    try:
        token_count = await client.count_tokens(request.text)
        return TokenCountResponse(
            token_count=token_count,
            text_length=len(request.text),
            model=client.settings.GEMINI_MODEL_TEXT,
        )
    except Exception as e:
        logger.error(f"Token counting failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token counting failed: {str(e)}",
        )


@router.get("/usage")
async def get_usage_stats() -> Dict[str, Any]:
    """
    Get usage statistics.

    Returns:
        Dict[str, any]: Usage statistics

    Example:
        ```bash
        curl http://localhost:8000/usage
        ```
    """
    # Placeholder - would track actual usage
    return {
        "total_requests": 0,
        "total_tokens": 0,
        "requests_per_minute": 0,
    }

