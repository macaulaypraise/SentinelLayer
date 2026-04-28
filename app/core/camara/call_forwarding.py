from typing import Any

from .client import nac_get, normalise
from .resilience import camara_retry


@camara_retry
async def check_call_forwarding(phone: str) -> dict[str, Any]:
    """Returns {active: bool, type: str|None}. Active = step-zero fraud."""
    return await nac_get("/call-forwarding-signal", {"phoneNumber": normalise(phone)})
