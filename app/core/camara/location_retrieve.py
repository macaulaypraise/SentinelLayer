from .client import nac_post, normalise


async def retrieve_live_location(phone: str) -> dict:
    """Precise MNO cell-tower coordinates. ONLY call after GRANTED consent."""
    return await nac_post(
        "/location-retrieval", {"device": {"phoneNumber": normalise(phone)}, "maxAge": 60}
    )
