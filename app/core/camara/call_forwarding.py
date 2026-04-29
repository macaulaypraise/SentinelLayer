from typing import Any

from .client import nac_post, normalise
from .resilience import camara_retry


@camara_retry
async def check_call_forwarding(phone: str) -> dict[str, Any]:
    """Checks unconditional call forwarding — the step-zero fraud signal."""
    try:
        result = await nac_post(
            "/passthrough/camara/v1/call-forwarding-signal/"
            "call-forwarding-signal/v0.3/unconditional-call-forwardings",
            {"phoneNumber": normalise(phone)},
        )
        # Response contains list — active if any entry exists
        return {"active": bool(result)}
    except Exception:
        return {"active": False}
