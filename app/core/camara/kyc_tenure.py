from .client import nac_get, normalise
from .resilience import camara_retry


@camara_retry
async def check_tenure(phone: str) -> dict:
    """Returns {tenureDays: int}. Short tenure on large transaction = high risk."""
    return await nac_get("/kyc-tenure", {"phoneNumber": normalise(phone)})
