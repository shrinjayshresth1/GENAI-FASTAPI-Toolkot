"""Input validation utilities."""

import re
from typing import Any, List, Optional

from app.core.exceptions import InvalidInputError


def validate_prompt(prompt: str, max_length: int = 10000, min_length: int = 1) -> str:
    """
    Validate prompt string.

    Args:
        prompt: Input prompt to validate
        max_length: Maximum allowed length
        min_length: Minimum required length

    Returns:
        str: Validated prompt

    Raises:
        InvalidInputError: If prompt is invalid

    Example:
        ```python
        validated = validate_prompt("Hello world", max_length=100)
        ```
    """
    if not isinstance(prompt, str):
        raise InvalidInputError("Prompt must be a string", field="prompt")

    prompt = prompt.strip()

    if len(prompt) < min_length:
        raise InvalidInputError(
            f"Prompt must be at least {min_length} characters", field="prompt"
        )

    if len(prompt) > max_length:
        raise InvalidInputError(
            f"Prompt exceeds maximum length of {max_length} characters", field="prompt"
        )

    return prompt


def validate_temperature(temperature: float, min_val: float = 0.0, max_val: float = 2.0) -> float:
    """
    Validate temperature parameter.

    Args:
        temperature: Temperature value to validate
        min_val: Minimum allowed value
        max_val: Maximum allowed value

    Returns:
        float: Validated temperature

    Raises:
        InvalidInputError: If temperature is invalid

    Example:
        ```python
        validated = validate_temperature(0.7)
        ```
    """
    if not isinstance(temperature, (int, float)):
        raise InvalidInputError("Temperature must be a number", field="temperature")

    if temperature < min_val or temperature > max_val:
        raise InvalidInputError(
            f"Temperature must be between {min_val} and {max_val}",
            field="temperature",
        )

    return float(temperature)


def validate_max_tokens(max_tokens: Optional[int], max_allowed: int = 8192) -> Optional[int]:
    """
    Validate max_tokens parameter.

    Args:
        max_tokens: Max tokens value to validate
        max_allowed: Maximum allowed value

    Returns:
        Optional[int]: Validated max_tokens or None

    Raises:
        InvalidInputError: If max_tokens is invalid

    Example:
        ```python
        validated = validate_max_tokens(1024)
        ```
    """
    if max_tokens is None:
        return None

    if not isinstance(max_tokens, int):
        raise InvalidInputError("max_tokens must be an integer", field="max_tokens")

    if max_tokens <= 0:
        raise InvalidInputError(
            "max_tokens must be greater than 0", field="max_tokens"
        )

    if max_tokens > max_allowed:
        raise InvalidInputError(
            f"max_tokens exceeds maximum allowed value of {max_allowed}",
            field="max_tokens",
        )

    return max_tokens


def validate_file_type(
    mime_type: str, allowed_types: List[str]
) -> None:
    """
    Validate file MIME type.

    Args:
        mime_type: MIME type to validate
        allowed_types: List of allowed MIME types

    Raises:
        InvalidInputError: If file type is not allowed

    Example:
        ```python
        validate_file_type("image/jpeg", ["image/jpeg", "image/png"])
        ```
    """
    if mime_type not in allowed_types:
        raise InvalidInputError(
            f"File type '{mime_type}' not allowed. Allowed types: {', '.join(allowed_types)}",
            field="file_type",
        )


def validate_file_size(
    size_bytes: int, max_size_bytes: int
) -> None:
    """
    Validate file size.

    Args:
        size_bytes: File size in bytes
        max_size_bytes: Maximum allowed size in bytes

    Raises:
        InvalidInputError: If file size exceeds limit

    Example:
        ```python
        validate_file_size(1024 * 1024, 10 * 1024 * 1024)  # 1MB, max 10MB
        ```
    """
    if size_bytes > max_size_bytes:
        max_mb = max_size_bytes / (1024 * 1024)
        raise InvalidInputError(
            f"File size exceeds maximum allowed size of {max_mb:.1f}MB",
            field="file_size",
        )


def validate_role(role: str) -> str:
    """
    Validate chat message role.

    Args:
        role: Role to validate (user, assistant, system)

    Returns:
        str: Validated role

    Raises:
        InvalidInputError: If role is invalid

    Example:
        ```python
        validated = validate_role("user")
        ```
    """
    valid_roles = ["user", "assistant", "system"]
    if role not in valid_roles:
        raise InvalidInputError(
            f"Role must be one of: {', '.join(valid_roles)}", field="role"
        )
    return role


def validate_url(url: str) -> str:
    """
    Validate URL format.

    Args:
        url: URL string to validate

    Returns:
        str: Validated URL

    Raises:
        InvalidInputError: If URL is invalid

    Example:
        ```python
        validated = validate_url("https://example.com/image.jpg")
        ```
    """
    url_pattern = re.compile(
        r"^https?://"  # http:// or https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain...
        r"localhost|"  # localhost...
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
        r"(?::\d+)?"  # optional port
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )

    if not url_pattern.match(url):
        raise InvalidInputError("Invalid URL format", field="url")

    return url


def validate_language_code(language: Optional[str]) -> Optional[str]:
    """
    Validate language code (ISO 639-1).

    Args:
        language: Language code to validate or "auto"

    Returns:
        Optional[str]: Validated language code

    Raises:
        InvalidInputError: If language code is invalid

    Example:
        ```python
        validated = validate_language_code("en")
        ```
    """
    if language is None or language == "auto":
        return language

    if not isinstance(language, str) or len(language) != 2:
        raise InvalidInputError(
            "Language code must be a 2-character ISO 639-1 code or 'auto'",
            field="language",
        )

    return language.lower()

