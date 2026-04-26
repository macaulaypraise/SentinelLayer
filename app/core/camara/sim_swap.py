from app.config import settings

from .client import nac_post, normalise
from .resilience import camara_retry


@camara_retry
async def check_sim_swap(phone: str, max_age_hours: int | None = None) -> dict:
    return await nac_post(
        "/sim-swap/check",
        {
            "phoneNumber": normalise(phone),
            "maxAge": max_age_hours or settings.sim_swap_window_hours,
        },
    )


async def subscribe_sim_swap_webhook(phone: str, callback_url: str) -> dict:
    return await nac_post(
        "/sim-swap/subscriptions",
        {
            "phoneNumber": normalise(phone),
            "webhook": {
                "notificationUrl": callback_url,
                "notificationAuthToken": settings.nac_client_secret,
            },
        },
    )
