from typing import Any

from .client import nac_get, normalise
from .resilience import camara_retry


@camara_retry
async def get_density(phone: str) -> dict[str, Any]:
    """Returns {anomalous: bool} — device in near-zero-population zone."""
    return await nac_get("/population-density", {"phoneNumber": normalise(phone)})
