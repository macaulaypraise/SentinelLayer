from typing import Any

from .client import nac_post, normalise
from .resilience import camara_retry


@camara_retry
async def verify_number(phone: str) -> dict[str, Any]:
    """Silent auth. v2.0 works over WiFi via OS-level TS.43 entitlement."""
    return await nac_post("/number-verification/verify", {"phoneNumber": normalise(phone)})
