from .client import nac_post, normalise
from .resilience import camara_retry


@camara_retry
async def check_device_swap(phone: str) -> dict:
    """IMSI-IMEI mismatch. Returns {swapped: bool, swappedAt: str|None}."""
    return await nac_post("/device-swap/check", {"phoneNumber": normalise(phone)})
