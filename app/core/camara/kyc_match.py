from datetime import date

from .client import nac_post, normalise
from .resilience import camara_retry


@camara_retry
async def check_kyc(phone: str, name: str, dob: date, address: str) -> dict:
    """Returns {match: bool, matchScore: int 0-100}. Text match vs MNO NIN records."""
    return await nac_post(
        "/kyc-match",
        {
            "phoneNumber": normalise(phone),
            "name": name,
            "dateOfBirth": dob.isoformat(),
            "address": address,
        },
    )
