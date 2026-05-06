from datetime import datetime
from typing import Any
from urllib.parse import quote


async def build_evidence_map(
    visit_locations: dict[str, Any],
    home_zone: dict[str, Any],
    incident_start: datetime,
    incident_end: datetime,
) -> str:
    """
    Builds an interactive Google Maps Directions URL.
    - NO API KEY REQUIRED.
    - NO BILLING REQUIRED.
    - Preserves the fraudster path and home baseline.
    """
    locations = visit_locations.get("locations", []) if visit_locations else []

    if not locations:
        return ""

    # Filter and validate coordinate points
    path_points = []
    for loc in locations:
        if isinstance(loc, dict):
            lat, lng = loc.get("latitude"), loc.get("longitude")
            if lat and lng:
                path_points.append(f"{lat},{lng}")

    if not path_points:
        return ""

    # Determine the "Home" baseline if it exists
    home_lat = home_zone.get("latitude") if isinstance(home_zone, dict) else None
    home_lng = home_zone.get("longitude") if isinstance(home_zone, dict) else None

    # Scenario A: Multiple locations (Build a full interactive trail)
    if len(path_points) > 1:
        # Start at the victim's home (if known) or the first fraud point
        origin = f"{home_lat},{home_lng}" if (home_lat and home_lng) else path_points[0]
        # End at the most recent fraudster location
        destination = path_points[-1]
        # Use intermediate points as waypoints
        waypoints = "|".join(path_points[1:-1]) if len(path_points) > 2 else ""

        url = (
            f"https://www.google.com/maps/dir/?api=1"
            f"&origin={quote(origin)}"
            f"&destination={quote(destination)}"
        )
        if waypoints:
            url += f"&waypoints={quote(waypoints)}"

        url += "&travelmode=driving"
        return url

    # Scenario B: Single location (Simple marker)
    else:
        lat_lng = path_points[0]
        return f"https://www.google.com/maps/search/?api=1&query={quote(lat_lng)}"
