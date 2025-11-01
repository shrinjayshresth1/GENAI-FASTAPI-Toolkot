"""Data formatting utilities."""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional


def format_usage_info(usage: Dict[str, int]) -> Dict[str, Any]:
    """
    Format token usage information.

    Args:
        usage: Usage dictionary with token counts

    Returns:
        Dict[str, Any]: Formatted usage information

    Example:
        ```python
        usage = {"prompt_tokens": 10, "completion_tokens": 20}
        formatted = format_usage_info(usage)
        ```
    """
    return {
        "prompt_tokens": usage.get("prompt_tokens", 0),
        "completion_tokens": usage.get("completion_tokens", 0),
        "total_tokens": usage.get("total_tokens", 0),
    }


def format_timestamp(dt: Optional[datetime] = None) -> str:
    """
    Format datetime as ISO string.

    Args:
        dt: Datetime object (uses UTC now if None)

    Returns:
        str: ISO formatted timestamp

    Example:
        ```python
        timestamp = format_timestamp()  # Returns current UTC time
        ```
    """
    if dt is None:
        dt = datetime.utcnow()
    return dt.isoformat() + "Z"


def format_error_response(
    message: str,
    error_code: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Format error response.

    Args:
        message: Error message
        error_code: Optional error code
        details: Optional error details

    Returns:
        Dict[str, Any]: Formatted error response

    Example:
        ```python
        error = format_error_response(
            "Invalid input",
            error_code="INVALID_INPUT",
            details={"field": "prompt"}
        )
        ```
    """
    response = {
        "detail": message,
        "timestamp": format_timestamp(),
    }
    if error_code:
        response["error_code"] = error_code
    if details:
        response["details"] = details
    return response


def format_stream_chunk(text: str, finish: bool = False) -> str:
    """
    Format text chunk for SSE streaming.

    Args:
        text: Text chunk
        finish: Whether this is the final chunk

    Returns:
        str: Formatted SSE chunk

    Example:
        ```python
        chunk = format_stream_chunk("Hello", finish=False)
        # Returns: "data: {\"text\": \"Hello\", \"finish\": false}\n\n"
        ```
    """
    data = {"text": text, "finish": finish}
    return f"data: {json.dumps(data)}\n\n"


def format_list_response(
    items: List[Any],
    total: Optional[int] = None,
    page: Optional[int] = None,
    page_size: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Format paginated list response.

    Args:
        items: List of items
        total: Total number of items
        page: Current page number
        page_size: Page size

    Returns:
        Dict[str, Any]: Formatted list response

    Example:
        ```python
        response = format_list_response([1, 2, 3], total=100, page=1, page_size=10)
        ```
    """
    response: Dict[str, Any] = {"items": items}
    if total is not None:
        response["total"] = total
    if page is not None:
        response["page"] = page
    if page_size is not None:
        response["page_size"] = page_size
        if total is not None and page is not None:
            response["total_pages"] = (total + page_size - 1) // page_size
    return response


def sanitize_for_logging(data: Any, max_length: int = 1000) -> str:
    """
    Sanitize data for logging (truncate long strings).

    Args:
        data: Data to sanitize
        max_length: Maximum length

    Returns:
        str: Sanitized string

    Example:
        ```python
        sanitized = sanitize_for_logging({"key": "very long string..."}, max_length=50)
        ```
    """
    data_str = json.dumps(data) if not isinstance(data, str) else data
    if len(data_str) > max_length:
        return data_str[:max_length] + "... [truncated]"
    return data_str

