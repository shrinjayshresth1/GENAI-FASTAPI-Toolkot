"""Rate limiting implementation using slowapi."""

import time
from collections import defaultdict
from typing import Dict, Optional

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.requests import Request

from app.config import Settings, get_settings
from app.core.exceptions import RateLimitError


class RateLimiter:
    """Rate limiter for API requests."""

    def __init__(self, settings: Optional[Settings] = None):
        """
        Initialize rate limiter.

        Args:
            settings: Application settings (optional)

        Example:
            ```python
            settings = get_settings()
            limiter = RateLimiter(settings)
            ```
        """
        self.settings = settings or get_settings()
        self.limiter = Limiter(
            key_func=self._get_identifier,
            default_limits=[f"{self.settings.RATE_LIMIT_PER_HOUR}/hour"],
        )
        self._request_counts: Dict[str, Dict[float, int]] = defaultdict(
            lambda: defaultdict(int)
        )

    def _get_identifier(self, request: Request) -> str:
        """
        Get identifier for rate limiting (IP address or API key).

        Args:
            request: FastAPI request object

        Returns:
            str: Identifier string
        """
        # Check for API key in headers
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"api_key:{api_key}"

        # Fall back to IP address
        return get_remote_address(request)

    async def check_rate_limit(
        self, request: Request, per_minute: Optional[int] = None
    ) -> None:
        """
        Check if request is within rate limits.

        Args:
            request: FastAPI request object
            per_minute: Optional custom per-minute limit

        Raises:
            RateLimitError: If rate limit is exceeded

        Example:
            ```python
            await limiter.check_rate_limit(request)
            ```
        """
        if not self.settings.RATE_LIMIT_ENABLED:
            return

        identifier = self._get_identifier(request)
        current_time = time.time()

        # Check per-minute limit
        minute_limit = per_minute or self.settings.RATE_LIMIT_PER_MINUTE
        minute_window = int(current_time / 60)

        if identifier not in self._request_counts:
            self._request_counts[identifier] = {}

        counts = self._request_counts[identifier]

        # Clean old entries (older than 1 hour)
        counts = {
            k: v
            for k, v in counts.items()
            if (current_time / 60) - k < 60
        }
        self._request_counts[identifier] = counts

        # Count requests in current minute
        minute_count = counts.get(minute_window, 0)

        if minute_count >= minute_limit:
            retry_after = 60 - (current_time % 60)
            raise RateLimitError(
                f"Rate limit exceeded: {minute_limit} requests per minute",
                retry_after=int(retry_after),
            )

        # Increment counter
        counts[minute_window] = minute_count + 1
        self._request_counts[identifier] = counts

    def get_limiter(self) -> Limiter:
        """
        Get slowapi limiter instance.

        Returns:
            Limiter: slowapi limiter instance

        Example:
            ```python
            limiter = rate_limiter.get_limiter()
            ```
        """
        return self.limiter


# Global rate limiter instance
_rate_limiter: Optional[RateLimiter] = None


def get_rate_limiter(settings: Optional[Settings] = None) -> RateLimiter:
    """
    Get global rate limiter instance.

    Args:
        settings: Application settings (optional)

    Returns:
        RateLimiter: Rate limiter instance

    Example:
        ```python
        limiter = get_rate_limiter()
        ```
    """
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter(settings)
    return _rate_limiter

