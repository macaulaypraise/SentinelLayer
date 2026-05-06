from typing import Any

from .client import nac_post, normalise
from .resilience import camara_retry


@camara_retry
async def check_call_forwarding(phone: str) -> dict[str, Any]:
    result = await nac_post(
        "/passthrough/camara/v1/call-forwarding-signal"
        "/call-forwarding-signal/v0.3/unconditional-call-forwardings",
        {"phoneNumber": normalise(phone)},
    )
    # Response is a list of service strings e.g. ["unconditional"] or ["inactive"]
    services = result if isinstance(result, list) else result.get("services", [])
    active = any(s != "inactive" for s in services) if services else False
    return {"active": active}
