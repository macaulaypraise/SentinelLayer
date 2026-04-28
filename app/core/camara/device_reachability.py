from typing import Any

from .client import nac_get, normalise
from .resilience import camara_retry


@camara_retry
async def check_reachability(phone: str) -> dict[str, Any]:
    """Returns {reachable: bool}. Unreachable device transacting = anomaly."""
    return await nac_get("/device-reachability-status", {"phoneNumber": normalise(phone)})
