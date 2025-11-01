"""Custom exceptions for Gemini FastAPI Toolkit."""

from typing import Any, Dict, Optional


class GeminiAPIError(Exception):
    """Base exception for all Gemini API errors."""

    def __init__(
        self,
        message: str,
        status_code: int = 503,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize Gemini API error.

        Args:
            message: Error message
            status_code: HTTP status code
            details: Additional error details

        Example:
            ```python
            raise GeminiAPIError("API request failed", status_code=503)
            ```
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class RateLimitError(GeminiAPIError):
    """Exception raised when rate limit is exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize rate limit error.

        Args:
            message: Error message
            retry_after: Seconds to wait before retrying
            details: Additional error details

        Example:
            ```python
            raise RateLimitError(retry_after=60)
            ```
        """
        super().__init__(message, status_code=429, details=details)
        self.retry_after = retry_after


class InvalidInputError(GeminiAPIError):
    """Exception raised for invalid input validation errors."""

    def __init__(
        self,
        message: str = "Invalid input provided",
        field: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize invalid input error.

        Args:
            message: Error message
            field: Field name that caused the error
            details: Additional error details

        Example:
            ```python
            raise InvalidInputError("Prompt too long", field="prompt")
            ```
        """
        super().__init__(message, status_code=400, details=details)
        self.field = field


class FileProcessingError(GeminiAPIError):
    """Exception raised during file processing operations."""

    def __init__(
        self,
        message: str = "File processing failed",
        file_type: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize file processing error.

        Args:
            message: Error message
            file_type: Type of file that caused the error
            details: Additional error details

        Example:
            ```python
            raise FileProcessingError("Invalid file format", file_type="image")
            ```
        """
        super().__init__(message, status_code=400, details=details)
        self.file_type = file_type


class ModelNotFoundError(GeminiAPIError):
    """Exception raised when a model is not found."""

    def __init__(
        self,
        message: str = "Model not found",
        model_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize model not found error.

        Args:
            message: Error message
            model_name: Name of the model that wasn't found
            details: Additional error details

        Example:
            ```python
            raise ModelNotFoundError(model_name="gemini-invalid")
            ```
        """
        super().__init__(message, status_code=404, details=details)
        self.model_name = model_name


class AuthenticationError(GeminiAPIError):
    """Exception raised for authentication failures."""

    def __init__(
        self,
        message: str = "Authentication failed",
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize authentication error.

        Args:
            message: Error message
            details: Additional error details

        Example:
            ```python
            raise AuthenticationError("Invalid API key")
            ```
        """
        super().__init__(message, status_code=401, details=details)

