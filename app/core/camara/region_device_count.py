from typing import Any

from .client import nac_get, normalise
from .resilience import camara_retry


@camara_retry
async def get_count(phone: str) -> dict[str, Any]:
    """Returns {sparse: bool} — unusually few devices in originating region."""
    return await nac_get("/region-device-count", {"phoneNumber": normalise(phone)})
