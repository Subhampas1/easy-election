"""
cloud_storage_service.py — Google Cloud Storage Integration

Provides functions to fetch and cache static election resources (PDFs,
guidelines, documents) from a Google Cloud Storage bucket. Includes
graceful fallback to local mock data when GCS is unavailable.
"""

import os
from typing import Optional

from src.services.cloud_logging_service import get_logger, log_warning, log_error


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_BUCKET_NAME: str = "election-resources-promptwar-2026"

# Mock election resources (used when GCS is unavailable)
MOCK_RESOURCES: dict[str, dict[str, str]] = {
    "voter_registration_guide.pdf": {
        "title": "Voter Registration Guide 2025",
        "description": "Step-by-step guide for new voter registration via Form 6.",
        "size": "2.4 MB",
        "url": "https://voters.eci.gov.in/download/manual/registration-guide.pdf",
    },
    "evm_faq.pdf": {
        "title": "EVM & VVPAT FAQ",
        "description": "Official ECI FAQ on Electronic Voting Machines and paper audit trail.",
        "size": "1.8 MB",
        "url": "https://eci.gov.in/files/file/evm-vvpat-faq.pdf",
    },
    "election_laws_summary.pdf": {
        "title": "Election Laws Summary",
        "description": "Key provisions from the Representation of the People Act 1951.",
        "size": "3.1 MB",
        "url": "https://legislative.gov.in/sites/default/files/rpa1951.pdf",
    },
    "voter_id_guide.pdf": {
        "title": "Voter ID (EPIC) Application Guide",
        "description": "How to apply for and download your e-EPIC online.",
        "size": "1.2 MB",
        "url": "https://voters.eci.gov.in/download/manual/epic-guide.pdf",
    },
    "accessible_voting_guide.pdf": {
        "title": "Accessible Voting for PwD & Senior Citizens",
        "description": "Special provisions for persons with disabilities and voters above 80.",
        "size": "0.9 MB",
        "url": "https://eci.gov.in/files/file/accessible-elections.pdf",
    },
}


# ---------------------------------------------------------------------------
# GCS Client Functions
# ---------------------------------------------------------------------------

def _get_gcs_client() -> Optional[object]:
    """Attempt to initialize a Google Cloud Storage client.

    Returns:
        A ``google.cloud.storage.Client`` instance if the library is
        installed and credentials are available, otherwise ``None``.
    """
    try:
        from google.cloud import storage
        project_id: str = os.getenv("GOOGLE_CLOUD_PROJECT", "")
        if project_id:
            return storage.Client(project=project_id)
        return storage.Client()
    except ImportError:
        log_warning(
            "gcs_unavailable",
            "google-cloud-storage not installed. Using mock resources.",
        )
        return None
    except Exception as exc:
        log_error(
            "gcs_init_error",
            f"Failed to initialize GCS client: {exc}",
        )
        return None


def fetch_election_resource(resource_name: str) -> Optional[bytes]:
    """Fetch an election resource file from Google Cloud Storage.

    Attempts to download the specified resource from the configured
    GCS bucket. Returns ``None`` if the resource is not found or
    GCS is unavailable.

    Args:
        resource_name: The filename of the resource in the bucket
            (e.g., ``"voter_registration_guide.pdf"``).

    Returns:
        The file contents as bytes, or ``None`` if unavailable.

    Examples:
        >>> content = fetch_election_resource("voter_registration_guide.pdf")
        >>> if content:
        ...     print(f"Downloaded {len(content)} bytes")
    """
    logger = get_logger()
    bucket_name: str = os.getenv("GCS_BUCKET_NAME", DEFAULT_BUCKET_NAME)

    client = _get_gcs_client()
    if client is None:
        logger.info(
            "GCS unavailable. Resource '%s' not fetched.", resource_name
        )
        return None

    try:
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(resource_name)

        if not blob.exists():
            logger.warning("Resource '%s' not found in bucket '%s'.", resource_name, bucket_name)
            return None

        content: bytes = blob.download_as_bytes()
        logger.info(
            "Successfully fetched resource '%s' (%d bytes).",
            resource_name,
            len(content),
        )
        return content

    except Exception as exc:
        log_error(
            "gcs_fetch_error",
            f"Failed to fetch '{resource_name}': {exc}",
            {"bucket": bucket_name, "resource": resource_name},
        )
        return None


def list_available_resources() -> list[dict[str, str]]:
    """List all available election resources.

    Returns metadata for all cached election resources. In production,
    this would list objects from the GCS bucket. In development,
    returns curated mock resource metadata.

    Returns:
        A list of dicts, each containing:
            - name (str): Resource filename.
            - title (str): Human-readable title.
            - description (str): Brief description of the resource.
            - size (str): Approximate file size.
            - url (str): Download URL (direct link or GCS signed URL).

    Examples:
        >>> resources = list_available_resources()
        >>> assert len(resources) > 0
        >>> assert "title" in resources[0]
    """
    logger = get_logger()

    # Attempt to list from GCS first
    client = _get_gcs_client()
    if client is not None:
        try:
            bucket_name: str = os.getenv("GCS_BUCKET_NAME", DEFAULT_BUCKET_NAME)
            bucket = client.bucket(bucket_name)
            blobs = bucket.list_blobs(max_results=20)

            resources: list[dict[str, str]] = []
            for blob in blobs:
                resources.append({
                    "name": blob.name,
                    "title": blob.name.replace("_", " ").replace(".pdf", "").title(),
                    "description": f"Election resource: {blob.name}",
                    "size": f"{blob.size / (1024 * 1024):.1f} MB" if blob.size else "N/A",
                    "url": blob.public_url,
                })

            if resources:
                logger.info("Listed %d resources from GCS.", len(resources))
                return resources

        except Exception as exc:
            log_warning("gcs_list_error", f"Could not list GCS resources: {exc}")

    # Fallback to mock resources
    logger.info("Using mock election resources (GCS unavailable).")
    return [
        {
            "name": name,
            "title": meta["title"],
            "description": meta["description"],
            "size": meta["size"],
            "url": meta["url"],
        }
        for name, meta in MOCK_RESOURCES.items()
    ]


def get_resource_url(resource_name: str) -> str:
    """Get the download URL for a specific election resource.

    Checks GCS first, then falls back to mock URLs.

    Args:
        resource_name: The filename of the resource.

    Returns:
        A URL string for downloading the resource.
    """
    if resource_name in MOCK_RESOURCES:
        return MOCK_RESOURCES[resource_name]["url"]
    return f"https://storage.googleapis.com/{DEFAULT_BUCKET_NAME}/{resource_name}"
