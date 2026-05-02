"""
conftest.py — Shared Test Fixtures for Citizen Election Assistant

Provides reusable fixtures for rate limiters, service instances,
mock data, and common test utilities across all test modules.
"""

import pytest
from unittest.mock import MagicMock, patch
from typing import Generator


# ── Rate Limiter Fixture ─────────────────────────────────────────

@pytest.fixture
def rate_limiter():
    """Create a fresh RateLimiter instance for testing."""
    from src.utils.security import RateLimiter
    return RateLimiter(window=60, max_requests=10)


# ── CSRF Token Fixture ───────────────────────────────────────────

@pytest.fixture
def csrf_token() -> str:
    """Generate a fresh CSRF token for testing."""
    from src.utils.security import generate_csrf_token
    return generate_csrf_token()


# ── Mock Logger Fixture ──────────────────────────────────────────

@pytest.fixture(autouse=True)
def mock_cloud_logging() -> Generator:
    """Auto-mock Cloud Logging to prevent real API calls during tests."""
    with patch("src.services.cloud_logging_service.log_user_action") as mock:
        mock.return_value = None
        yield mock


# ── Election Data Fixtures ───────────────────────────────────────

@pytest.fixture
def sample_states() -> list[str]:
    """Return a subset of Indian states for testing."""
    return ["Delhi", "Maharashtra", "Tamil Nadu", "Karnataka", "Uttar Pradesh"]


@pytest.fixture
def sample_candidates() -> list[str]:
    """Return mock EVM candidates for testing."""
    return [
        "Party A — Candidate Alpha",
        "Party B — Candidate Beta",
        "Party C — Candidate Gamma",
        "Party D — Candidate Delta",
        "NOTA (None Of The Above)",
    ]


@pytest.fixture
def sample_myths() -> list[dict[str, str]]:
    """Return sample myth entries for testing."""
    return [
        {
            "myth": "EVMs can be hacked remotely",
            "verdict": "FALSE",
            "explanation": "EVMs have no network connectivity.",
            "source": "ECI FAQ",
        },
        {
            "myth": "Voting is compulsory in India",
            "verdict": "FALSE",
            "explanation": "Voting is a right, not an obligation.",
            "source": "Constitution of India",
        },
    ]


# ── Accessibility Fixtures ───────────────────────────────────────

@pytest.fixture
def high_contrast_colors() -> dict[str, str]:
    """Return color pairs for contrast testing."""
    return {
        "fg_pass": "#ffffff",
        "bg_pass": "#000000",
        "fg_fail": "#cccccc",
        "bg_fail": "#ffffff",
    }


# ── Performance Fixtures ─────────────────────────────────────────

@pytest.fixture
def lazy_loader():
    """Create a LazyLoader instance for testing."""
    from src.utils.performance import LazyLoader
    return LazyLoader(lambda: {"status": "loaded"})
