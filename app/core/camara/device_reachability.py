from typing import Any

from .client import nac_post, normalise
from .resilience import camara_retry


@camara_retry
async def check_reachability(phone: str) -> dict[str, Any]:
    """Returns {reachable: bool}. Unreachable device transacting = anomaly."""
    return await nac_post(
        "/device-status/device-reachability-status/v1/retrieve",
        {"device": {"phoneNumber": normalise(phone)}},
    )
