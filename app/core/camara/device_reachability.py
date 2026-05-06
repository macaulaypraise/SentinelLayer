from typing import Any

from .client import nac_post, normalise
from .resilience import camara_retry


@camara_retry
async def check_reachability(phone: str) -> dict[str, Any]:
    try:
        result = await nac_post(
            "/device-status/device-reachability-status/v1/retrieve",
            {"device": {"phoneNumber": normalise(phone)}},
        )
        # Response: {"connectivityStatus": "CONNECTED_DATA"|"CONNECTED_SMS"|"NOT_CONNECTED"}
        status = result.get("connectivityStatus", "CONNECTED_DATA")
        return {"reachable": status != "NOT_CONNECTED", "status": status}
    except Exception:
        return {"reachable": True, "status": "UNKNOWN"}
