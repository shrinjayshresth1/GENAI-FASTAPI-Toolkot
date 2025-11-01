"""Application configuration using Pydantic Settings."""

import logging
from functools import lru_cache
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Google Gemini API Configuration
    GOOGLE_API_KEY: str = Field(..., description="Google Gemini API key")
    GEMINI_MODEL_TEXT: str = Field(
        "gemini-2.0-flash-exp", description="Default text model"
    )
    GEMINI_MODEL_VISION: str = Field(
        "gemini-2.0-flash-exp", description="Default vision model"
    )
    GEMINI_MODEL_AUDIO: str = Field(
        "gemini-2.0-flash-exp", description="Default audio model"
    )

    # Server Configuration
    HOST: str = Field("0.0.0.0", description="Server host")
    PORT: int = Field(8000, gt=0, le=65535, description="Server port")
    DEBUG: bool = Field(False, description="Debug mode")
    WORKERS: int = Field(4, gt=0, le=32, description="Number of worker processes")
    RELOAD: bool = Field(False, description="Auto-reload on code changes")

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(60, gt=0, description="Requests per minute")
    RATE_LIMIT_PER_HOUR: int = Field(1000, gt=0, description="Requests per hour")
    RATE_LIMIT_ENABLED: bool = Field(True, description="Enable rate limiting")

    # File Upload Configuration
    MAX_FILE_SIZE_MB: int = Field(10, gt=0, le=100, description="Maximum file size in MB")
    ALLOWED_IMAGE_TYPES: List[str] = Field(
        default=["image/jpeg", "image/png", "image/gif", "image/webp"],
        description="Allowed image MIME types",
    )
    ALLOWED_AUDIO_TYPES: List[str] = Field(
        default=["audio/wav", "audio/mpeg", "audio/mp3"],
        description="Allowed audio MIME types",
    )
    ALLOWED_VIDEO_TYPES: List[str] = Field(
        default=["video/mp4", "video/webm", "video/quicktime"],
        description="Allowed video MIME types",
    )

    # Caching Configuration
    ENABLE_CACHE: bool = Field(True, description="Enable caching")
    REDIS_URL: Optional[str] = Field(
        None, description="Redis connection URL (optional)"
    )
    CACHE_TTL_SECONDS: int = Field(3600, gt=0, description="Cache TTL in seconds")
    CACHE_MAX_SIZE: int = Field(1000, gt=0, description="Maximum cache entries")

    # CORS Configuration
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173", "*"],
        description="Allowed CORS origins",
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(True, description="Allow CORS credentials")
    CORS_ALLOW_METHODS: List[str] = Field(
        default=["*"], description="Allowed HTTP methods"
    )
    CORS_ALLOW_HEADERS: List[str] = Field(
        default=["*"], description="Allowed HTTP headers"
    )

    # Logging Configuration
    LOG_LEVEL: str = Field("INFO", description="Logging level")
    LOG_FORMAT: str = Field("json", description="Log format: json or text")

    # API Configuration
    API_V1_PREFIX: str = Field("/api/v1", description="API version prefix")
    API_TITLE: str = Field(
        "Gemini FastAPI Toolkit", description="API documentation title"
    )
    API_VERSION: str = Field("1.0.0", description="API version")
    API_DESCRIPTION: str = Field(
        "Production-ready FastAPI toolkit for Google Gemini API integration with multimodal support",
        description="API description",
    )

    @property
    def max_file_size_bytes(self) -> int:
        """Convert MB to bytes."""
        return self.MAX_FILE_SIZE_MB * 1024 * 1024

    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list."""
        if "*" in self.CORS_ORIGINS:
            return ["*"]
        return self.CORS_ORIGINS


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Returns:
        Settings: Application settings singleton

    Example:
        ```python
        settings = get_settings()
        api_key = settings.GOOGLE_API_KEY
        ```
    """
    return Settings()


def setup_logging(settings: Settings) -> None:
    """
    Configure application logging.

    Args:
        settings: Application settings

    Example:
        ```python
        settings = get_settings()
        setup_logging(settings)
        logger.info("Application started")
        ```
    """
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    log_format = (
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        if settings.LOG_FORMAT == "text"
        else "%(message)s"
    )

    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[logging.StreamHandler()],
    )

    if settings.LOG_FORMAT == "json":
        # Configure JSON formatter if needed
        import json
        import sys

        class JSONFormatter(logging.Formatter):
            def format(self, record: logging.LogRecord) -> str:
                log_data = {
                    "timestamp": self.formatTime(record, self.datefmt),
                    "level": record.levelname,
                    "logger": record.name,
                    "message": record.getMessage(),
                }
                if record.exc_info:
                    log_data["exception"] = self.formatException(record.exc_info)
                return json.dumps(log_data)

        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        logging.root.handlers = [handler]

