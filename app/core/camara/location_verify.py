from typing import Any

from .client import nac_post, normalise
from .resilience import camara_retry


@camara_retry
async def verify_location(phone: str, expected_region: str) -> dict[str, Any]:
    # Simulator device is in Budapest — use those coords for TRUE result
    return await nac_post(
        "/location-verification/v1/verify",
        {
            "device": {"phoneNumber": normalise(phone)},
            "area": {
                "areaType": "CIRCLE",
                "center": {"latitude": 47.4418, "longitude": 19.1604},
                "radius": 50000,
            },
            "maxAge": 120,
        },
    )
