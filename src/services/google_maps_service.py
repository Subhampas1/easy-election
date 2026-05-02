"""
google_maps_service.py — Google Maps API Integration

Provides polling station lookup and static map generation using the
Google Maps Static API. Includes graceful fallback to OpenStreetMap
when API credentials are unavailable.
"""

import os
import urllib.parse
from typing import Optional

from src.services.cloud_logging_service import get_logger, log_warning


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_LOCATION: str = "India Gate, New Delhi"
DEFAULT_ZOOM: int = 15
DEFAULT_MAP_SIZE: str = "600x300"

# Sample polling station data (mock for demonstration)
MOCK_POLLING_STATIONS: list[dict[str, str | float]] = [
    {
        "name": "Government Boys Sr. Sec. School",
        "address": "Rajpath Area, New Delhi - 110001",
        "lat": 28.6129,
        "lng": 77.2295,
        "distance": "0.8 km",
    },
    {
        "name": "Community Hall, Connaught Place",
        "address": "Block A, Connaught Place, New Delhi - 110001",
        "lat": 28.6315,
        "lng": 77.2167,
        "distance": "1.2 km",
    },
    {
        "name": "Municipal Corporation Primary School",
        "address": "Lodhi Road, New Delhi - 110003",
        "lat": 28.5918,
        "lng": 77.2273,
        "distance": "2.5 km",
    },
]


# ---------------------------------------------------------------------------
# Maps API Functions
# ---------------------------------------------------------------------------

def get_polling_station_map_url(
    location: str = DEFAULT_LOCATION,
    zoom: int = DEFAULT_ZOOM,
    size: str = DEFAULT_MAP_SIZE,
) -> str:
    """Generate a Google Maps Static API URL for polling station visualization.

    Uses the ``GOOGLE_MAPS_API_KEY`` from environment variables. Falls back
    to an OpenStreetMap embed URL if the key is not configured.

    Args:
        location: Address or landmark for the map center.
        zoom: Map zoom level (1–20).
        size: Image dimensions as ``'WIDTHxHEIGHT'``.

    Returns:
        URL string for the static map image or OpenStreetMap embed.

    Examples:
        >>> url = get_polling_station_map_url("Connaught Place, Delhi")
        >>> assert "maps.googleapis.com" in url or "openstreetmap" in url
    """
    logger = get_logger()
    api_key: str = os.getenv("GOOGLE_MAPS_API_KEY", "")
    encoded_location: str = urllib.parse.quote(location)

    if api_key:
        logger.info(
            "Generating Maps URL with API key for location: %s", location
        )
        return (
            f"https://maps.googleapis.com/maps/api/staticmap"
            f"?center={encoded_location}"
            f"&zoom={zoom}"
            f"&size={size}"
            f"&markers=color:red%7C{encoded_location}"
            f"&key={api_key}"
        )

    # Fallback: OpenStreetMap embed (no API key needed)
    log_warning(
        "api_fallback",
        "GOOGLE_MAPS_API_KEY not set. Using OpenStreetMap fallback.",
    )
    return (
        f"https://www.openstreetmap.org/export/embed.html"
        f"?bbox=77.1,28.5,77.3,28.7"
        f"&layer=mapnik"
        f"&marker=28.6139,77.2090"
    )


def get_static_map_url(lat: float, lng: float, zoom: int = 15) -> str:
    """Generate a static map URL for specific coordinates.

    Args:
        lat: Latitude of the location.
        lng: Longitude of the location.
        zoom: Map zoom level (1–20). Defaults to 15.

    Returns:
        URL string for the static map image centered on the coordinates.
    """
    api_key: str = os.getenv("GOOGLE_MAPS_API_KEY", "")

    if api_key:
        return (
            f"https://maps.googleapis.com/maps/api/staticmap"
            f"?center={lat},{lng}"
            f"&zoom={zoom}"
            f"&size={DEFAULT_MAP_SIZE}"
            f"&markers=color:red%7C{lat},{lng}"
            f"&key={api_key}"
        )

    return (
        f"https://www.openstreetmap.org/export/embed.html"
        f"?bbox={lng - 0.01},{lat - 0.01},{lng + 0.01},{lat + 0.01}"
        f"&layer=mapnik"
        f"&marker={lat},{lng}"
    )


def find_polling_stations(zip_code: str) -> list[dict[str, str | float]]:
    """Find nearest polling stations based on a ZIP/PIN code.

    In production with a valid API key, this would query the Google
    Places API. Currently returns curated mock data for demonstration
    and testing purposes.

    Args:
        zip_code: An Indian 6-digit PIN code.

    Returns:
        A list of dicts, each containing:
            - name (str): Polling station name.
            - address (str): Full address.
            - lat (float): Latitude.
            - lng (float): Longitude.
            - distance (str): Approximate distance from the PIN code center.

    Examples:
        >>> stations = find_polling_stations("110001")
        >>> assert len(stations) > 0
        >>> assert "name" in stations[0]
    """
    logger = get_logger()
    logger.info("Looking up polling stations for PIN: %s", zip_code)

    # In a real implementation, this would call Google Places API:
    # url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    # params = {"location": f"{lat},{lng}", "radius": 2000,
    #           "keyword": "polling station", "key": api_key}
    # For now, return curated mock data
    return MOCK_POLLING_STATIONS.copy()


def get_map_fallback_message() -> str:
    """Return a user-friendly message when Maps API key is not configured.

    Returns:
        Informational string about the map placeholder, or empty string
        if the API key is available.
    """
    api_key: str = os.getenv("GOOGLE_MAPS_API_KEY", "")
    if api_key:
        return ""
    return (
        "Showing a demo map of New Delhi. To see your actual nearest polling "
        "station, configure your `GOOGLE_MAPS_API_KEY` in the `.env` file."
    )
