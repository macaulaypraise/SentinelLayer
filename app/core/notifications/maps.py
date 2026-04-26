from datetime import datetime

from app.config import settings


async def build_evidence_map(
    visit_locations: dict, home_zone: dict, incident_start: datetime, incident_end: datetime
) -> str:
    """Builds a Google Maps Static URL: red trail = fraudster path, green = victim home."""
    base = "https://maps.googleapis.com/maps/api/staticmap"
    params = [f"key={settings.google_maps_api_key}", "size=800x600", "maptype=roadmap"]

    # Handle visit locations
    locations = visit_locations.get("locations", [])
    if not locations:
        return ""  # Return an empty string if no locations exist

    # Add markers for each location
    for i, loc in enumerate(locations):
        lat, lng = loc.get("latitude"), loc.get("longitude")
        if lat and lng:  # Ensure latitude and longitude are available
            params.append(f"markers=color:red|label:{i + 1}|{lat},{lng}")

    # Add home zone marker if available
    if home_zone.get("latitude") and home_zone.get("longitude"):
        params.append(
            f"markers=color:green|label:H|{home_zone['latitude']},{home_zone['longitude']}"
        )

    # Add path if there are multiple locations
    if len(locations) > 1:
        path = "|".join(f"{loc['latitude']},{loc['longitude']}" for loc in locations)
        params.append(f"path=color:0xff0000ff|weight:3|{path}")

    # Return the final URL
    return f"{base}?" + "&".join(params)
