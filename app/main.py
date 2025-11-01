"""Main FastAPI application."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import Settings, get_settings, setup_logging
from app.core.exceptions import (
    AuthenticationError,
    FileProcessingError,
    GeminiAPIError,
    InvalidInputError,
    ModelNotFoundError,
    RateLimitError,
)
from app.middleware import (
    ErrorTrackingMiddleware,
    LoggingMiddleware,
    RequestIDMiddleware,
)
from app.routers import (
    audio,
    health,
    image,
    multimodal,
    streaming,
    text,
    video,
)
from app.utils.formatters import format_error_response

# Setup logging
settings = get_settings()
setup_logging(settings)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Gemini FastAPI Toolkit")
    logger.info(f"API Version: {settings.API_VERSION}")
    logger.info(f"Models - Text: {settings.GEMINI_MODEL_TEXT}, Vision: {settings.GEMINI_MODEL_VISION}")
    yield
    # Shutdown
    logger.info("Shutting down Gemini FastAPI Toolkit")


# Create FastAPI application
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Custom middleware
app.add_middleware(RequestIDMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(ErrorTrackingMiddleware)

# Include routers
app.include_router(health.router)
app.include_router(text.router)
app.include_router(image.router)
app.include_router(audio.router)
app.include_router(video.router)
app.include_router(multimodal.router)
app.include_router(streaming.router)


# Exception handlers
@app.exception_handler(GeminiAPIError)
async def gemini_api_error_handler(request: Request, exc: GeminiAPIError) -> JSONResponse:
    """Handle Gemini API errors."""
    logger.error(f"Gemini API error: {exc.message}", exc_info=True)
    return JSONResponse(
        status_code=exc.status_code,
        content=format_error_response(
            exc.message,
            error_code="GEMINI_API_ERROR",
            details=exc.details,
        ),
    )


@app.exception_handler(RateLimitError)
async def rate_limit_error_handler(request: Request, exc: RateLimitError) -> JSONResponse:
    """Handle rate limit errors."""
    logger.warning(f"Rate limit exceeded: {exc.message}")
    response = JSONResponse(
        status_code=exc.status_code,
        content=format_error_response(
            exc.message,
            error_code="RATE_LIMIT_EXCEEDED",
            details=exc.details,
        ),
    )
    if exc.retry_after:
        response.headers["Retry-After"] = str(exc.retry_after)
    return response


@app.exception_handler(InvalidInputError)
async def invalid_input_error_handler(request: Request, exc: InvalidInputError) -> JSONResponse:
    """Handle invalid input errors."""
    logger.warning(f"Invalid input: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content=format_error_response(
            exc.message,
            error_code="INVALID_INPUT",
            details=exc.details or {"field": exc.field},
        ),
    )


@app.exception_handler(FileProcessingError)
async def file_processing_error_handler(request: Request, exc: FileProcessingError) -> JSONResponse:
    """Handle file processing errors."""
    logger.error(f"File processing error: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content=format_error_response(
            exc.message,
            error_code="FILE_PROCESSING_ERROR",
            details=exc.details or {"file_type": exc.file_type},
        ),
    )


@app.exception_handler(ModelNotFoundError)
async def model_not_found_error_handler(request: Request, exc: ModelNotFoundError) -> JSONResponse:
    """Handle model not found errors."""
    logger.warning(f"Model not found: {exc.model_name}")
    return JSONResponse(
        status_code=exc.status_code,
        content=format_error_response(
            exc.message,
            error_code="MODEL_NOT_FOUND",
            details=exc.details or {"model_name": exc.model_name},
        ),
    )


@app.exception_handler(AuthenticationError)
async def authentication_error_handler(request: Request, exc: AuthenticationError) -> JSONResponse:
    """Handle authentication errors."""
    logger.warning(f"Authentication error: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content=format_error_response(
            exc.message,
            error_code="AUTHENTICATION_ERROR",
            details=exc.details,
        ),
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle validation errors."""
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=format_error_response(
            "Validation error",
            error_code="VALIDATION_ERROR",
            details={"errors": exc.errors()},
        ),
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle HTTP exceptions."""
    logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content=format_error_response(
            str(exc.detail),
            error_code="HTTP_ERROR",
        ),
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle generic exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=format_error_response(
            "Internal server error",
            error_code="INTERNAL_ERROR",
        ),
    )


@app.get("/")
async def root() -> dict:
    """
    Root endpoint.

    Returns:
        dict: API information

    Example:
        ```bash
        curl http://localhost:8000/
        ```
    """
    return {
        "name": settings.API_TITLE,
        "version": settings.API_VERSION,
        "description": settings.API_DESCRIPTION,
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        workers=settings.WORKERS if not settings.RELOAD else 1,
    )

