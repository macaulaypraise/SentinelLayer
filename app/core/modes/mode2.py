from datetime import UTC, datetime
from typing import Any
from typing import cast as type_cast

import structlog
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.camara.consent_info import get_consent_status
from app.core.camara.location_retrieve import retrieve_live_location  # Mode 2 ONLY
from app.core.notifications.fcm import send_mode2_alert
from app.db.models import ConsentRecord
from app.observability.metrics import mode2_active, mode2_triggers_total

log = structlog.get_logger()


async def run_mode2(
    session_id: str,
    phone: str,
    trigger_reason: str,
    redis_client: Redis,
    db: AsyncSession,
    tenant_id: str,
) -> dict[str, Any]:
    mode2_triggers_total.labels(tenant_id=tenant_id, trigger_reason=trigger_reason).inc()
    mode2_active.inc()
    try:
        # ── Step A: Consent gate — must return GRANTED before any coordinates ──
        consent = await get_consent_status(phone, redis_client)
        record = ConsentRecord(
            session_id=session_id,
            phone_number=phone,
            tenant_id=tenant_id,
            consent_status=consent["status"],
            authorised_by=trigger_reason,
            authorised_at=datetime.now(UTC),
        )
        db.add(record)
        await db.commit()

        if consent["status"] != "GRANTED":
            log.warning("mode2_no_consent", phone=phone, status=consent["status"])
            return {
                "mode_triggered": 2,
                "outcome": "FROZEN_NO_LOCATION",
                "reason": "Consent not granted — account frozen pending verification.",
                "consent_status": consent["status"],
                "location_retrieved": False,
            }

        # ── Step B: Retrieve precise MNO coordinates ──
        location: dict[str, Any] = await retrieve_live_location(phone)
        record.location_retrieved = True
        raw = consent.get("raw")
        record.raw_consent_response = type_cast(
            dict[str, Any] | None, raw if isinstance(raw, dict) else None
        )
        await db.commit()

        # ── Step C: Three-way simultaneous notification ──
        # All parties alerted at the same moment — no inter-party delay
        payload = {
            "session_id": session_id,
            "phone": phone,
            "location": location,
            "trigger": trigger_reason,
            "consent_trail": str(record.id),
            "timestamp": datetime.now(UTC).isoformat(),
        }
        await send_mode2_alert(payload)

        log.info("mode2_alert_sent", phone=phone, trigger=trigger_reason)
        return {
            "mode_triggered": 2,
            "outcome": "LOCATION_RETRIEVED",
            "location": location,
            "consent_record_id": str(record.id),
            "alerted_parties": ["fraud_desk", "telecom_security", "enforcement"],
        }
    finally:
        mode2_active.dec()
