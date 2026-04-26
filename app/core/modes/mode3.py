import asyncio
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.camara.device_visit import get_visit_locations  # Mode 3 ONLY
from app.core.camara.most_freq_location import get_frequent_location
from app.core.notifications.maps import build_evidence_map
from app.db.models import Incident


async def run_mode3(
    session_id: str,
    phone: str,
    incident_start: datetime,
    incident_end: datetime,
    db: AsyncSession,
    tenant_id: str,
) -> dict[str, Any]:
    visits, home_zone = await asyncio.gather(
        get_visit_locations(phone, incident_start, incident_end), get_frequent_location(phone)
    )
    maps_url = await build_evidence_map(visits, home_zone, incident_start, incident_end)

    incident = Incident(
        session_id=session_id,
        tenant_id=tenant_id,
        phone_number=phone,
        incident_start=incident_start,
        incident_end=incident_end,
        visit_locations=visits,
        home_zone=home_zone,
        maps_url=maps_url,
        created_at=datetime.now(UTC),
    )
    db.add(incident)
    await db.commit()

    return {
        "mode_triggered": 3,
        "maps_evidence_url": maps_url,
        "locations_visited": len(visits.get("locations", [])),
        "home_zone": home_zone,
        "incident_id": str(incident.id),
    }
