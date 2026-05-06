from datetime import date
from typing import Any

from .client import nac_post, normalise
from .resilience import camara_retry


@camara_retry
async def check_recycling(phone: str, registered_at: date) -> dict[str, Any]:
    return await nac_post(
        "/passthrough/camara/v1/number-recycling/number-recycling/v0.2/check",
        {"phoneNumber": normalise(phone), "specifiedDate": registered_at.isoformat()},
    )
