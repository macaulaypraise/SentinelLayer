from datetime import date
from typing import Any

from .client import nac_post, normalise
from .resilience import camara_retry


@camara_retry
async def check_kyc(phone: str, name: str, dob: date, address: str) -> dict[str, Any]:
    return await nac_post(
        "/passthrough/camara/v1/kyc-match/kyc-match/v0.3/match",
        {
            "phoneNumber": normalise(phone),
            "name": name,
            "birthdate": dob.isoformat(),
            "address": address,
        },
    )
