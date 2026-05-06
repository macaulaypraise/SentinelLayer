from typing import Any

from .client import nac_post, normalise
from .resilience import camara_retry


@camara_retry
async def verify_number(phone: str) -> dict[str, Any]:
    try:
        result = await nac_post(
            "/passthrough/camara/v1/number-verification/number-verification/v0/verify",
            {"phoneNumber": normalise(phone)},
        )
        # Response: {"devicePhoneNumberVerified": true/false}
        verified = result.get("devicePhoneNumberVerified", True)
        return {"verified": verified}
    except Exception:
        return {"verified": True}  # fail open
