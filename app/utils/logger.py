"""Logging configuration and utilities."""

import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict, Optional

from app.config import Settings, get_settings


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON.

        Args:
            record: Log record

        Returns:
            str: JSON formatted log string
        """
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id

        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id

        # Add all custom fields
        for key, value in record.__dict__.items():
            if key not in [
                "name",
                "msg",
                "args",
                "created",
                "filename",
                "funcName",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "message",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "thread",
                "threadName",
                "exc_info",
                "exc_text",
            ]:
                log_data[key] = value

        return json.dumps(log_data)


def setup_logging(settings: Optional[Settings] = None) -> None:
    """
    Configure application logging.

    Args:
        settings: Application settings (optional)

    Example:
        ```python
        setup_logging()
        logger.info("Application started")
        ```
    """
    settings = settings or get_settings()
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    # Remove existing handlers
    root_logger = logging.getLogger()
    root_logger.handlers = []

    # Create handler
    handler = logging.StreamHandler(sys.stdout)

    # Set formatter based on format setting
    if settings.LOG_FORMAT == "json":
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level)

    # Configure third-party loggers
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """
    Get logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        logging.Logger: Logger instance

    Example:
        ```python
        logger = get_logger(__name__)
        logger.info("Message")
        ```
    """
    return logging.getLogger(name)


def log_request(
    logger: logging.Logger,
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
    request_id: Optional[str] = None,
) -> None:
    """
    Log HTTP request.

    Args:
        logger: Logger instance
        method: HTTP method
        path: Request path
        status_code: Response status code
        duration_ms: Request duration in milliseconds
        request_id: Optional request ID

    Example:
        ```python
        log_request(logger, "POST", "/api/v1/text/generate", 200, 123.45, "req_123")
        ```
    """
    extra = {
        "method": method,
        "path": path,
        "status_code": status_code,
        "duration_ms": duration_ms,
    }
    if request_id:
        extra["request_id"] = request_id

    logger.info(f"{method} {path} - {status_code} - {duration_ms:.2f}ms", extra=extra)


def log_error(
    logger: logging.Logger,
    error: Exception,
    context: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None,
) -> None:
    """
    Log error with context.

    Args:
        logger: Logger instance
        error: Exception to log
        context: Optional context dictionary
        request_id: Optional request ID

    Example:
        ```python
        log_error(logger, ValueError("Invalid input"), {"field": "prompt"}, "req_123")
        ```
    """
    extra = {"error_type": type(error).__name__, "error_message": str(error)}
    if context:
        extra.update(context)
    if request_id:
        extra["request_id"] = request_id

    logger.error(f"Error: {error}", exc_info=True, extra=extra)

