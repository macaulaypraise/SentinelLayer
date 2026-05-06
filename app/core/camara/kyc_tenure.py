from datetime import date, timedelta
from typing import Any

from .client import nac_post, normalise
from .resilience import camara_retry


@camara_retry
async def check_tenure(phone: str) -> dict[str, Any]:
    # Check if subscriber has been with operator for at least 90 days
    tenure_threshold = (date.today() - timedelta(days=90)).isoformat()
    return await nac_post(
        "/passthrough/camara/v1/kyc-tenure/kyc-tenure/v0.1/check-tenure",
        {"phoneNumber": normalise(phone), "tenureDate": tenure_threshold},
    )
