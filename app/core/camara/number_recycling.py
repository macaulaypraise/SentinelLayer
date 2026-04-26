from datetime import date

from .client import nac_get, normalise
from .resilience import camara_retry


@camara_retry
async def check_recycling(phone: str, registered_at: date) -> dict:
    """Binary: was this number reassigned since registered_at?"""
    return await nac_get(
        "/number-recycling/check",
        {"phoneNumber": normalise(phone), "sinceDate": registered_at.isoformat()},
    )
