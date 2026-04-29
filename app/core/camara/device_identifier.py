from typing import Any

from .client import nac_post, normalise
from .resilience import camara_retry


@camara_retry
async def get_identifier(phone: str) -> dict[str, Any]:
    """Hardware-level device ID without exposing raw IMEI. Returns {newDevice: bool}."""
    return await nac_post(
        "/device-identifier/v0/retrieve", {"device": {"phoneNumber": normalise(phone)}}
    )
