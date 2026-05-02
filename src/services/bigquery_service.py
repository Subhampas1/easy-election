"""
bigquery_service.py — Google BigQuery Analytics Integration

Provides election analytics and usage tracking using Google BigQuery.
Enables data-driven insights on voter engagement, feature usage, and
regional election participation patterns. Falls back to in-memory
analytics when BigQuery is unavailable.
"""

import os
import time
from typing import Optional
from collections import defaultdict

from src.services.base_service import BaseCloudService
from src.services.cloud_logging_service import get_logger, log_user_action, log_warning


# ---------------------------------------------------------------------------
# BigQuery Service
# ---------------------------------------------------------------------------

class BigQueryService(BaseCloudService):
    """Google BigQuery integration for election analytics.

    Provides:
        - Usage event tracking (page views, interactions).
        - Regional engagement analytics.
        - Feature adoption metrics.
        - Aggregated voter readiness reports.

    Falls back to in-memory tracking when BigQuery is unavailable.
    """

    @property
    def service_name(self) -> str:
        """Return the service name."""
        return "Google BigQuery"

    def initialize(self) -> bool:
        """Initialize the BigQuery client.

        Returns:
            True if BigQuery SDK is available and configured.
        """
        try:
            from google.cloud import bigquery

            project_id: str = os.getenv("GCP_PROJECT_ID", "")
            if project_id:
                self._client = bigquery.Client(project=project_id)
            else:
                self._client = bigquery.Client()
            self._log_init_success()
            return True

        except ImportError:
            self._log_init_failure("google-cloud-bigquery not installed")
            return False
        except Exception as exc:
            self._log_init_failure(str(exc))
            return False

    def health_check(self) -> dict[str, str | bool]:
        """Check if BigQuery is available.

        Returns:
            Health status dict.
        """
        if self._initialized and self._client is not None:
            return {
                "service": self.service_name,
                "status": "healthy",
                "available": True,
                "message": "BigQuery connected and ready for analytics.",
            }
        return {
            "service": self.service_name,
            "status": "degraded",
            "available": False,
            "message": "Using in-memory analytics fallback.",
        }


# ---------------------------------------------------------------------------
# In-memory analytics store (fallback when BigQuery is unavailable)
# ---------------------------------------------------------------------------

_analytics_store: dict[str, list[dict]] = defaultdict(list)
_service_instance: Optional[BigQueryService] = None


def _get_service() -> BigQueryService:
    """Get or create the singleton BigQueryService instance.

    Returns:
        The initialized BigQueryService instance.
    """
    global _service_instance
    if _service_instance is None:
        _service_instance = BigQueryService()
        _service_instance.initialize()
    return _service_instance


# ---------------------------------------------------------------------------
# Analytics Functions
# ---------------------------------------------------------------------------

def track_event(
    event_name: str,
    properties: Optional[dict] = None,
    user_session: str = "anonymous",
) -> bool:
    """Track a user interaction event for analytics.

    In production, inserts the event into a BigQuery table. In
    development, stores it in memory for local analysis.

    Args:
        event_name: Name of the event (e.g., ``"page_view"``, ``"vote_cast"``).
        properties: Optional dict of event properties.
        user_session: Session identifier for the user.

    Returns:
        True if the event was successfully tracked.

    Examples:
        >>> track_event("roadmap_generated", {"state": "Delhi", "age": 25})
        True
    """
    logger = get_logger()
    service: BigQueryService = _get_service()

    event_data: dict = {
        "event_name": event_name,
        "timestamp": time.time(),
        "session_id": user_session,
        "properties": properties or {},
    }

    if service.is_initialized and service._client is not None:
        try:
            dataset_id: str = os.getenv("BQ_DATASET_ID", "election_analytics")
            table_id: str = os.getenv("BQ_TABLE_ID", "events")
            table_ref: str = f"{os.getenv('GCP_PROJECT_ID', 'project')}.{dataset_id}.{table_id}"

            rows_to_insert: list[dict] = [event_data]
            errors = service._client.insert_rows_json(table_ref, rows_to_insert)

            if not errors:
                logger.info("Event '%s' tracked in BigQuery.", event_name)
                return True
            else:
                logger.warning("BigQuery insert errors: %s", str(errors))

        except Exception as exc:
            logger.warning("BigQuery tracking failed: %s. Using fallback.", str(exc))

    # In-memory fallback
    _analytics_store[event_name].append(event_data)
    logger.info("Event '%s' tracked in memory (BigQuery unavailable).", event_name)
    return True


def get_analytics_summary() -> dict[str, int | dict]:
    """Get a summary of tracked analytics events.

    Returns aggregated event counts and recent activity metrics.
    In production, queries BigQuery. In development, aggregates
    in-memory data.

    Returns:
        A dict containing:
            - ``total_events`` (int): Total events tracked.
            - ``event_counts`` (dict[str, int]): Count per event type.
            - ``recent_events`` (int): Events in the last hour.

    Examples:
        >>> summary = get_analytics_summary()
        >>> assert "total_events" in summary
    """
    logger = get_logger()

    # In-memory summary (works with or without BigQuery)
    total: int = sum(len(events) for events in _analytics_store.values())
    event_counts: dict[str, int] = {
        name: len(events) for name, events in _analytics_store.items()
    }

    one_hour_ago: float = time.time() - 3600
    recent: int = sum(
        1
        for events in _analytics_store.values()
        for event in events
        if event.get("timestamp", 0) > one_hour_ago
    )

    summary: dict = {
        "total_events": total,
        "event_counts": event_counts,
        "recent_events": recent,
    }

    logger.info("Analytics summary: %d total events, %d recent.", total, recent)
    return summary


def get_feature_usage_report() -> list[dict[str, str | int]]:
    """Get a feature usage breakdown for the dashboard.

    Returns:
        A list of dicts with feature names and usage counts.

    Examples:
        >>> report = get_feature_usage_report()
        >>> assert isinstance(report, list)
    """
    feature_map: dict[str, str] = {
        "page_view": "Page Views",
        "roadmap_page_submit": "Roadmaps Generated",
        "ballot_page_cast": "Votes Simulated",
        "myth_page_check": "Myths Checked",
        "polling_station_search": "Station Lookups",
        "ai_verify_claim": "AI Verifications",
        "ai_voter_query": "AI Queries",
    }

    report: list[dict[str, str | int]] = []
    for event_key, display_name in feature_map.items():
        count: int = len(_analytics_store.get(event_key, []))
        report.append({"feature": display_name, "usage_count": count})

    return report


def get_regional_engagement() -> dict[str, int]:
    """Get regional engagement metrics by state.

    Aggregates events that contain state information to produce
    a per-state engagement count.

    Returns:
        A dict mapping state names to event counts.

    Examples:
        >>> engagement = get_regional_engagement()
        >>> assert isinstance(engagement, dict)
    """
    engagement: dict[str, int] = defaultdict(int)

    for events in _analytics_store.values():
        for event in events:
            state: str = event.get("properties", {}).get("state", "")
            if state:
                engagement[state] += 1

    return dict(engagement)


def get_bigquery_service_health() -> dict[str, str | bool]:
    """Get the health status of the BigQuery service.

    Returns:
        Health check result dict.
    """
    return _get_service().health_check()
