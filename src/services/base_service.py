"""
base_service.py — Abstract Base Class for Google Cloud Services

Defines a common interface for all Google Cloud service integrations.
Ensures consistent initialization, health checking, and fallback
patterns across Cloud Logging, Storage, Maps, Vertex AI, and BigQuery.
"""

import abc
import logging
from typing import Optional


class BaseCloudService(abc.ABC):
    """Abstract base class for all Google Cloud service integrations.

    Enforces a consistent contract for initialization, health checks,
    and graceful degradation across all service adapters.

    Subclasses must implement:
        - ``initialize()`` — set up the service client.
        - ``health_check()`` — verify the service is reachable.
        - ``service_name`` (property) — return the human-readable name.
    """

    def __init__(self) -> None:
        """Initialize the base service with default state."""
        self._initialized: bool = False
        self._client: Optional[object] = None
        self._logger: logging.Logger = logging.getLogger(self.__class__.__name__)

    @property
    @abc.abstractmethod
    def service_name(self) -> str:
        """Return the human-readable name of this service.

        Returns:
            A string identifying the Google Cloud service.
        """
        ...

    @abc.abstractmethod
    def initialize(self) -> bool:
        """Initialize the service client and dependencies.

        Returns:
            True if initialization was successful, False otherwise.
        """
        ...

    @abc.abstractmethod
    def health_check(self) -> dict[str, str | bool]:
        """Perform a health check on the service.

        Returns:
            A dict with keys:
                - ``service`` (str): The service name.
                - ``status`` (str): ``'healthy'`` or ``'degraded'``.
                - ``available`` (bool): Whether the service is available.
                - ``message`` (str): Additional details.
        """
        ...

    @property
    def is_initialized(self) -> bool:
        """Whether this service has been successfully initialized."""
        return self._initialized

    def _log_init_success(self) -> None:
        """Log successful service initialization."""
        self._logger.info(
            "%s initialized successfully.", self.service_name
        )
        self._initialized = True

    def _log_init_failure(self, reason: str) -> None:
        """Log failed service initialization with reason.

        Args:
            reason: Human-readable description of the failure.
        """
        self._logger.warning(
            "%s initialization failed: %s. Using fallback.",
            self.service_name,
            reason,
        )
        self._initialized = False
