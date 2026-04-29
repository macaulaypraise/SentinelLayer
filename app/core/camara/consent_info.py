from typing import Any

from redis.asyncio import Redis

from app.config import settings

from .client import nac_post, normalise

CONSENT_PREFIX = "consent:"


async def get_consent_status(phone: str, redis_client: Redis) -> dict[str, Any]:
    """Check consent from cache first, then Nokia NaC API."""
    e164 = normalise(phone)
    cached = await redis_client.get(f"consent:{e164}")
    if cached:
        return {"status": cached.decode(), "source": "cache"}
    result = await nac_post(
        "/passthrough/camara/v1/consent-info/consent-info/v0.1/retrieve",
        {
            "phoneNumber": e164,
            "scopes": ["location-verification:verify"],
            "purpose": "dpv:FraudPreventionAndDetection",
            "requestCaptureUrl": False,
        },
    )
    status = result.get("consentStatus", "UNKNOWN")
    if status == "GRANTED":
        await redis_client.setex(f"consent:{e164}", settings.consent_cache_ttl_seconds, status)
    return {"status": status, "source": "api", "raw": result}
