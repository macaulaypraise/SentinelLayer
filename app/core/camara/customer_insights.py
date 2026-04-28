from typing import Any

from .client import nac_get, normalise
from .resilience import camara_retry


@camara_retry
async def get_insights(phone: str) -> dict[str, Any]:
    """Aggregated MNO subscriber behaviour. Returns {anomaly: bool}."""
    return await nac_get("/customer-insights", {"phoneNumber": normalise(phone)})
