"""
cloud_logging_service.py — Structured Cloud Logging Integration

Provides a unified logging interface that uses Google Cloud Logging in
production environments and falls back to Python's standard logging
module for local development.
"""

import logging
import os
from typing import Optional


# ---------------------------------------------------------------------------
# Module-level logger cache
# ---------------------------------------------------------------------------

_logger_instance: Optional[logging.Logger] = None


def get_logger(name: str = "election-assistant") -> logging.Logger:
    """Get a configured logger instance.

    In production (when ``ENABLE_CLOUD_LOGGING`` is set to ``true``),
    returns a logger backed by Google Cloud Logging with structured
    JSON output. In local development, returns a standard Python logger
    with formatted console output.

    Args:
        name: The logger name. Defaults to ``"election-assistant"``.

    Returns:
        A configured ``logging.Logger`` instance ready for use.

    Examples:
        >>> logger = get_logger()
        >>> logger.info("User generated roadmap", extra={"state": "Delhi"})
    """
    global _logger_instance

    if _logger_instance is not None:
        return _logger_instance

    enable_cloud: str = os.getenv("ENABLE_CLOUD_LOGGING", "false").lower()

    if enable_cloud == "true":
        _logger_instance = _setup_cloud_logger(name)
    else:
        _logger_instance = _setup_local_logger(name)

    return _logger_instance


def _setup_cloud_logger(name: str) -> logging.Logger:
    """Configure Google Cloud Logging for production.

    Attaches the Cloud Logging handler to the Python logging module,
    enabling structured JSON logs that appear in Cloud Logging console.

    Args:
        name: The logger name for Cloud Logging.

    Returns:
        A ``logging.Logger`` with Cloud Logging handler attached.
    """
    try:
        import google.cloud.logging as cloud_logging

        client: cloud_logging.Client = cloud_logging.Client()
        client.setup_logging()

        logger: logging.Logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)

        logger.info(
            "Cloud Logging initialized successfully.",
            extra={"service": "election-assistant", "environment": "production"},
        )
        return logger

    except ImportError:
        # Fallback if google-cloud-logging not installed
        logger = _setup_local_logger(name)
        logger.warning(
            "google-cloud-logging not installed. Using local logger. "
            "Install with: pip install google-cloud-logging"
        )
        return logger

    except Exception as exc:
        # Fallback on any Cloud Logging initialization error
        logger = _setup_local_logger(name)
        logger.warning(
            "Cloud Logging initialization failed: %s. Using local logger.", str(exc)
        )
        return logger


def _setup_local_logger(name: str) -> logging.Logger:
    """Configure a local console logger for development.

    Creates a logger with a formatted console handler showing timestamps,
    log levels, and messages in a human-readable format.

    Args:
        name: The logger name.

    Returns:
        A ``logging.Logger`` with console handler attached.
    """
    logger: logging.Logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Avoid duplicate handlers on re-initialization
    if not logger.handlers:
        handler: logging.StreamHandler = logging.StreamHandler()
        handler.setLevel(logging.INFO)

        formatter: logging.Formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def log_user_action(action: str, details: Optional[dict] = None) -> None:
    """Log a user interaction event with structured metadata.

    Convenience function for logging user actions like page visits,
    form submissions, and button clicks.

    Args:
        action: A short description of the user action (e.g., "roadmap_generated").
        details: Optional dict of additional metadata to log.

    Examples:
        >>> log_user_action("vote_cast", {"party": "Party A", "page": "ballot"})
    """
    logger: logging.Logger = get_logger()
    log_data: dict = {"action": action}
    if details:
        log_data.update(details)
    logger.info("User action: %s", action, extra=log_data)


def log_error(error_type: str, message: str, details: Optional[dict] = None) -> None:
    """Log an error event with structured metadata.

    Convenience function for logging errors and failures with
    contextual information for debugging.

    Args:
        error_type: Category of the error (e.g., "validation_error", "api_timeout").
        message: Human-readable error description.
        details: Optional dict of additional debugging metadata.

    Examples:
        >>> log_error("api_timeout", "Maps API timed out after 10s", {"zip": "110001"})
    """
    logger: logging.Logger = get_logger()
    log_data: dict = {"error_type": error_type}
    if details:
        log_data.update(details)
    logger.error("Error [%s]: %s", error_type, message, extra=log_data)


def log_warning(warning_type: str, message: str) -> None:
    """Log a warning event.

    Used for non-critical issues like API key fallbacks or degraded
    functionality.

    Args:
        warning_type: Category of the warning (e.g., "api_fallback").
        message: Human-readable warning description.

    Examples:
        >>> log_warning("api_fallback", "Maps API key not set, using OpenStreetMap.")
    """
    logger: logging.Logger = get_logger()
    logger.warning("Warning [%s]: %s", warning_type, message)
