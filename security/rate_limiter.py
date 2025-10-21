"""
Rate Limiting Middleware
Implements rate limiting to protect against abuse
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Optional, Tuple
from pathlib import Path
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import hashlib


class RateLimitExceeded(HTTPException):
    """Exception raised when rate limit is exceeded"""

    def __init__(self, retry_after: int):
        super().__init__(
            status_code=429,
            detail=f"Rate limit exceeded. Try again in {retry_after} seconds.",
            headers={"Retry-After": str(retry_after)}
        )


class RateLimiter:
    """
    Token bucket rate limiter using SQLite for persistence
    """

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize rate limiter

        Args:
            db_path: Path to SQLite database
        """
        if db_path is None:
            db_path = Path(__file__).parent.parent / "milton_publicist.db"

        self.db_path = Path(db_path)

    def _get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _cleanup_old_entries(self, conn: sqlite3.Connection):
        """Remove expired rate limit entries"""
        conn.execute("""
            DELETE FROM rate_limits
            WHERE window_end < datetime('now', '-1 hour')
        """)
        conn.commit()

    def check_rate_limit(
        self,
        key: str,
        limit_type: str,
        max_requests: int,
        window_seconds: int
    ) -> Tuple[bool, Optional[int]]:
        """
        Check if request is within rate limit

        Args:
            key: Identifier for rate limiting (IP, user ID, API key, etc.)
            limit_type: Type of limit (api, content_generation, publishing, etc.)
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds

        Returns:
            Tuple of (is_allowed, retry_after_seconds)
        """
        with self._get_connection() as conn:
            # Cleanup old entries periodically
            self._cleanup_old_entries(conn)

            now = datetime.now()
            window_start = now - timedelta(seconds=window_seconds)

            # Get current count in window
            cursor = conn.execute("""
                SELECT
                    id,
                    request_count,
                    window_start,
                    window_end
                FROM rate_limits
                WHERE key = ?
                  AND limit_type = ?
                  AND window_end > ?
                ORDER BY window_end DESC
                LIMIT 1
            """, (key, limit_type, now))

            row = cursor.fetchone()

            if row:
                # Existing window found
                if row["request_count"] >= max_requests:
                    # Limit exceeded
                    retry_after = int((datetime.fromisoformat(row["window_end"]) - now).total_seconds())
                    return False, max(1, retry_after)

                # Increment count
                conn.execute("""
                    UPDATE rate_limits
                    SET request_count = request_count + 1
                    WHERE id = ?
                """, (row["id"],))

            else:
                # Create new window
                window_end = now + timedelta(seconds=window_seconds)

                conn.execute("""
                    INSERT INTO rate_limits (key, limit_type, request_count, window_start, window_end)
                    VALUES (?, ?, 1, ?, ?)
                """, (key, limit_type, now, window_end))

            conn.commit()
            return True, None

    def get_rate_limit_status(self, key: str, limit_type: str) -> dict:
        """
        Get current rate limit status

        Args:
            key: Rate limit key
            limit_type: Type of limit

        Returns:
            Dictionary with status information
        """
        with self._get_connection() as conn:
            now = datetime.now()

            cursor = conn.execute("""
                SELECT
                    request_count,
                    window_start,
                    window_end
                FROM rate_limits
                WHERE key = ?
                  AND limit_type = ?
                  AND window_end > ?
                ORDER BY window_end DESC
                LIMIT 1
            """, (key, limit_type, now))

            row = cursor.fetchone()

            if row:
                window_end = datetime.fromisoformat(row["window_end"])
                remaining_seconds = int((window_end - now).total_seconds())

                return {
                    "current_count": row["request_count"],
                    "window_start": row["window_start"],
                    "window_end": row["window_end"],
                    "resets_in": max(0, remaining_seconds)
                }

            return {
                "current_count": 0,
                "window_start": None,
                "window_end": None,
                "resets_in": 0
            }

    def reset_rate_limit(self, key: str, limit_type: Optional[str] = None):
        """
        Reset rate limit for a key

        Args:
            key: Rate limit key
            limit_type: Optional limit type (resets all if None)
        """
        with self._get_connection() as conn:
            if limit_type:
                conn.execute("""
                    DELETE FROM rate_limits
                    WHERE key = ? AND limit_type = ?
                """, (key, limit_type))
            else:
                conn.execute("""
                    DELETE FROM rate_limits
                    WHERE key = ?
                """, (key,))

            conn.commit()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for rate limiting
    """

    # Rate limit configurations
    LIMITS = {
        "global": {"max_requests": 1000, "window_seconds": 3600},  # 1000 req/hour
        "api": {"max_requests": 100, "window_seconds": 60},  # 100 req/minute
        "content_generation": {"max_requests": 50, "window_seconds": 3600},  # 50/hour
        "publishing": {"max_requests": 20, "window_seconds": 86400},  # 20/day
    }

    def __init__(self, app, db_path: Optional[str] = None):
        """
        Initialize middleware

        Args:
            app: FastAPI application
            db_path: Path to database
        """
        super().__init__(app)
        self.limiter = RateLimiter(db_path)

    def _get_client_key(self, request: Request) -> str:
        """
        Get unique key for client (IP address or authenticated user)

        Args:
            request: FastAPI request

        Returns:
            Client key for rate limiting
        """
        # Try to get user ID from JWT token
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            # Hash token to create consistent key
            return hashlib.sha256(token.encode()).hexdigest()[:16]

        # Fall back to IP address
        client_ip = request.client.host if request.client else "unknown"
        return f"ip_{client_ip}"

    def _get_limit_type(self, request: Request) -> str:
        """
        Determine limit type based on request path

        Args:
            request: FastAPI request

        Returns:
            Limit type
        """
        path = request.url.path

        if "/api/generate" in path or "/api/content" in path:
            return "content_generation"
        elif "/api/publish" in path:
            return "publishing"
        elif "/api/" in path:
            return "api"
        else:
            return "global"

    async def dispatch(self, request: Request, call_next):
        """
        Process request with rate limiting

        Args:
            request: FastAPI request
            call_next: Next middleware/route handler

        Returns:
            Response
        """
        # Skip rate limiting for certain paths
        exempt_paths = ["/", "/health", "/docs", "/openapi.json"]
        if request.url.path in exempt_paths:
            return await call_next(request)

        # Get client key and limit type
        client_key = self._get_client_key(request)
        limit_type = self._get_limit_type(request)

        # Get limit configuration
        limit_config = self.LIMITS.get(limit_type, self.LIMITS["global"])

        # Check rate limit
        is_allowed, retry_after = self.limiter.check_rate_limit(
            key=client_key,
            limit_type=limit_type,
            max_requests=limit_config["max_requests"],
            window_seconds=limit_config["window_seconds"]
        )

        if not is_allowed:
            raise RateLimitExceeded(retry_after=retry_after)

        # Get current status for response headers
        status = self.limiter.get_rate_limit_status(client_key, limit_type)

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(limit_config["max_requests"])
        response.headers["X-RateLimit-Remaining"] = str(
            max(0, limit_config["max_requests"] - status["current_count"])
        )
        response.headers["X-RateLimit-Reset"] = str(status["resets_in"])

        return response


# Decorator for route-specific rate limiting
def rate_limit(max_requests: int, window_seconds: int, limit_type: str = "custom"):
    """
    Decorator for applying rate limits to specific routes

    Args:
        max_requests: Maximum requests allowed
        window_seconds: Time window in seconds
        limit_type: Type of limit

    Example:
        @app.post("/api/expensive-operation")
        @rate_limit(max_requests=5, window_seconds=3600)
        async def expensive_operation():
            pass
    """
    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            limiter = RateLimiter()

            # Get client key
            client_ip = request.client.host if request.client else "unknown"
            client_key = f"ip_{client_ip}"

            # Check rate limit
            is_allowed, retry_after = limiter.check_rate_limit(
                key=client_key,
                limit_type=limit_type,
                max_requests=max_requests,
                window_seconds=window_seconds
            )

            if not is_allowed:
                raise RateLimitExceeded(retry_after=retry_after)

            return await func(request, *args, **kwargs)

        return wrapper
    return decorator


if __name__ == "__main__":
    # Test rate limiter
    limiter = RateLimiter()

    print("=" * 60)
    print("RATE LIMITER TEST")
    print("=" * 60)
    print()

    # Test basic rate limiting
    test_key = "test_user"
    test_limit_type = "test"
    max_requests = 5
    window_seconds = 60

    print(f"Testing: {max_requests} requests per {window_seconds} seconds")
    print()

    for i in range(7):
        is_allowed, retry_after = limiter.check_rate_limit(
            key=test_key,
            limit_type=test_limit_type,
            max_requests=max_requests,
            window_seconds=window_seconds
        )

        if is_allowed:
            print(f"Request {i+1}: [OK] Allowed")
        else:
            print(f"Request {i+1}: [BLOCKED] Rate limit exceeded. Retry in {retry_after}s")

    # Show current status
    print()
    status = limiter.get_rate_limit_status(test_key, test_limit_type)
    print(f"Current count: {status['current_count']}")
    print(f"Resets in: {status['resets_in']} seconds")

    print()
    print("=" * 60)
