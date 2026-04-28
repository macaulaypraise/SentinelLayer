from datetime import datetime
from typing import Any

from .client import nac_post, normalise


async def get_visit_locations(phone: str, start: datetime, end: datetime) -> dict[str, Any]:
    """Historical location trail for incident window. Mode 3 only."""
    return await nac_post(
        "/device-visit-location",
        {
            "device": {"phoneNumber": normalise(phone)},
            "startTime": start.isoformat(),
            "endTime": end.isoformat(),
        },
    )
