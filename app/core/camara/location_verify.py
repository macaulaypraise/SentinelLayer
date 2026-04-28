from typing import Any

from .client import nac_post, normalise
from .resilience import camara_retry


@camara_retry
async def verify_location(phone: str, expected_region: str) -> dict[str, Any]:
    """Boolean only — is device in expected zone? No coordinates exposed."""
    return await nac_post(
        "/location-verification/verify",
        {"device": {"phoneNumber": normalise(phone)}, "area": {"region": expected_region}},
    )
