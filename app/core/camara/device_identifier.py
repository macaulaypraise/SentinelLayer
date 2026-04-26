from .client import nac_get, normalise
from .resilience import camara_retry


@camara_retry
async def get_identifier(phone: str) -> dict:
    """Hardware-level device ID without exposing raw IMEI. Returns {newDevice: bool}."""
    return await nac_get("/device-identifier", {"phoneNumber": normalise(phone)})
