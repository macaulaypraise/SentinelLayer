from typing import Any

from .client import nac_post, normalise


async def retrieve_live_location(phone: str) -> dict[str, Any]:
    """MUST only be called after Consent Info returns GRANTED."""
    return await nac_post(
        "/location-retrieval/v0/retrieve",
        {"device": {"phoneNumber": normalise(phone)}, "maxAge": 60},
    )
