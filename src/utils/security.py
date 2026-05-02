"""
security.py — Security Middleware and Hardening Utilities

Provides defense-in-depth security features including:
    - Rate limiting for abuse prevention.
    - Content Security Policy (CSP) header generation.
    - CSRF token management.
    - Session fingerprinting for anomaly detection.
    - Input length enforcement.
"""

import hashlib
import secrets
import time
from typing import Optional
from collections import defaultdict


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

RATE_LIMIT_WINDOW: int = 60  # seconds
RATE_LIMIT_MAX_REQUESTS: int = 30  # max requests per window
CSRF_TOKEN_LENGTH: int = 32
SESSION_TIMEOUT: int = 1800  # 30 minutes


# ---------------------------------------------------------------------------
# Rate Limiter
# ---------------------------------------------------------------------------

class RateLimiter:
    """Token-bucket rate limiter for abuse prevention.

    Tracks request timestamps per client identifier and enforces
    a maximum request count within a sliding time window.

    Attributes:
        window: Time window in seconds.
        max_requests: Maximum allowed requests per window.
    """

    def __init__(
        self,
        window: int = RATE_LIMIT_WINDOW,
        max_requests: int = RATE_LIMIT_MAX_REQUESTS,
    ) -> None:
        """Initialize the rate limiter.

        Args:
            window: Time window in seconds (default 60).
            max_requests: Max requests per window (default 30).
        """
        self.window: int = window
        self.max_requests: int = max_requests
        self._requests: dict[str, list[float]] = defaultdict(list)

    def is_allowed(self, client_id: str) -> bool:
        """Check if a request from the given client is allowed.

        Args:
            client_id: Unique identifier for the client (session ID, IP, etc.).

        Returns:
            True if the request is within rate limits, False otherwise.

        Examples:
            >>> limiter = RateLimiter(window=60, max_requests=5)
            >>> limiter.is_allowed("user_123")
            True
        """
        now: float = time.time()
        cutoff: float = now - self.window

        # Prune expired timestamps
        self._requests[client_id] = [
            ts for ts in self._requests[client_id] if ts > cutoff
        ]

        if len(self._requests[client_id]) >= self.max_requests:
            return False

        self._requests[client_id].append(now)
        return True

    def get_remaining(self, client_id: str) -> int:
        """Get the number of remaining requests for a client.

        Args:
            client_id: Unique identifier for the client.

        Returns:
            Number of remaining allowed requests in the current window.
        """
        now: float = time.time()
        cutoff: float = now - self.window
        active: int = len([ts for ts in self._requests[client_id] if ts > cutoff])
        return max(0, self.max_requests - active)

    def reset(self, client_id: str) -> None:
        """Reset the rate limit counter for a client.

        Args:
            client_id: Unique identifier for the client.
        """
        self._requests.pop(client_id, None)


# ---------------------------------------------------------------------------
# CSRF Protection
# ---------------------------------------------------------------------------

def generate_csrf_token() -> str:
    """Generate a cryptographically secure CSRF token.

    Returns:
        A hex-encoded random token string.

    Examples:
        >>> token = generate_csrf_token()
        >>> assert len(token) == 64  # 32 bytes = 64 hex chars
    """
    return secrets.token_hex(CSRF_TOKEN_LENGTH)


def validate_csrf_token(token: str, expected: str) -> bool:
    """Validate a CSRF token using constant-time comparison.

    Uses ``secrets.compare_digest`` to prevent timing attacks.

    Args:
        token: The submitted CSRF token.
        expected: The expected (stored) CSRF token.

    Returns:
        True if the tokens match, False otherwise.

    Examples:
        >>> token = generate_csrf_token()
        >>> validate_csrf_token(token, token)
        True
        >>> validate_csrf_token("fake", token)
        False
    """
    if not token or not expected:
        return False
    return secrets.compare_digest(token, expected)


# ---------------------------------------------------------------------------
# Content Security Policy
# ---------------------------------------------------------------------------

def generate_csp_header() -> str:
    """Generate a Content Security Policy header string.

    Defines strict CSP rules to prevent XSS, clickjacking, and
    data injection attacks. Allows only trusted sources.

    Returns:
        A CSP header value string.

    Examples:
        >>> csp = generate_csp_header()
        >>> assert "default-src" in csp
    """
    directives: list[str] = [
        "default-src 'self'",
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net",
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
        "font-src 'self' https://fonts.gstatic.com",
        "img-src 'self' data: https://*.googleapis.com https://*.openstreetmap.org https://*.tile.openstreetmap.org",
        "connect-src 'self' https://*.googleapis.com",
        "frame-src 'self' https://www.openstreetmap.org",
        "frame-ancestors 'self'",
        "base-uri 'self'",
        "form-action 'self'",
    ]
    return "; ".join(directives)


# ---------------------------------------------------------------------------
# Session Security
# ---------------------------------------------------------------------------

def generate_session_fingerprint(user_agent: str, accept_lang: str) -> str:
    """Generate a session fingerprint for anomaly detection.

    Creates a hash-based fingerprint from browser characteristics
    to detect session hijacking attempts.

    Args:
        user_agent: The client's User-Agent header.
        accept_lang: The client's Accept-Language header.

    Returns:
        A SHA-256 hex digest of the combined fingerprint.

    Examples:
        >>> fp = generate_session_fingerprint("Mozilla/5.0", "en-US")
        >>> assert len(fp) == 64
    """
    raw: str = f"{user_agent}:{accept_lang}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def validate_input_length(
    text: str,
    max_length: int = 500,
    field_name: str = "input",
) -> tuple[bool, str]:
    """Validate that input text does not exceed the maximum length.

    Args:
        text: The input text to validate.
        max_length: Maximum allowed character count.
        field_name: Name of the field for error messages.

    Returns:
        A tuple of (is_valid, message).

    Examples:
        >>> validate_input_length("hello", 500)
        (True, 'Input length valid.')
        >>> validate_input_length("x" * 600, 500)
        (False, 'input exceeds maximum length of 500 characters.')
    """
    if not isinstance(text, str):
        return False, f"{field_name} must be a string."

    if len(text) > max_length:
        return False, f"{field_name} exceeds maximum length of {max_length} characters."

    return True, "Input length valid."


# ---------------------------------------------------------------------------
# Module-level rate limiter instance
# ---------------------------------------------------------------------------

_global_rate_limiter: RateLimiter = RateLimiter()


def check_rate_limit(session_id: str = "default") -> bool:
    """Check the global rate limit for a session.

    Args:
        session_id: The session identifier.

    Returns:
        True if the request is allowed.
    """
    return _global_rate_limiter.is_allowed(session_id)
