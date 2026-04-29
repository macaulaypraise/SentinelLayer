from typing import Any

from .client import nac_post, normalise
from .resilience import camara_retry


@camara_retry
async def check_device_swap(phone: str) -> dict[str, Any]:
    """IMSI-IMEI mismatch. Returns {swapped: bool, swappedAt: str|None}."""
    return await nac_post(
        "/passthrough/camara/v1/device-swap/device-swap/v1/check",
        {"phoneNumber": normalise(phone), "maxAge": 120},
    )
