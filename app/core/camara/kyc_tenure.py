from datetime import date
from typing import Any

from .client import nac_post, normalise
from .resilience import camara_retry


@camara_retry
async def check_tenure(phone: str) -> dict[str, Any]:
    """Returns {tenureDays: int}. Short tenure on large transaction = high risk."""
    return await nac_post(
        "/passthrough/camara/v1/kyc-tenure/kyc-tenure/v0.1/check-tenure",
        {"phoneNumber": normalise(phone), "tenureDate": date.today().isoformat()},
    )
