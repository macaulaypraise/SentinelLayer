from typing import Any

from .client import nac_get, normalise
from .resilience import camara_retry


@camara_retry
async def get_frequent_location(phone: str) -> dict[str, Any]:
    """Returns {baseline: str|None, latitude: float|None, longitude: float|None}."""
    return await nac_get("/most-frequent-location", {"phoneNumber": normalise(phone)})
