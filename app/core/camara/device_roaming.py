from typing import Any

from .client import nac_post, normalise
from .resilience import camara_retry


@camara_retry
async def check_roaming(phone: str) -> dict[str, Any]:
    """Roaming device making domestic transaction = anomaly signal."""
    try:
        result = await nac_post(
            "/device-status/device-roaming-status/v1/retrieve",
            {"device": {"phoneNumber": normalise(phone)}},
        )
        return {"roaming": result.get("roaming", False), "country_code": result.get("countryCode")}
    except Exception:
        return {"roaming": False, "country_code": None}
