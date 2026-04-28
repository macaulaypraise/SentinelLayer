from typing import Any

from redis.asyncio import Redis

from app.config import settings

from .client import nac_get, normalise

CONSENT_PREFIX = "consent:"


async def get_consent_status(phone: str, redis_client: Redis) -> dict[str, Any]:
    """Check consent from cache first, then Nokia NaC API."""
    e164 = normalise(phone)
    cached = await redis_client.get(f"{CONSENT_PREFIX}{e164}")
    if cached:
        return {"status": cached.decode(), "source": "cache"}
    result = await nac_get("/consent-info", {"phoneNumber": e164})
    status = result.get("consentStatus", "UNKNOWN")
    if status == "GRANTED":
        await redis_client.setex(
            f"{CONSENT_PREFIX}{e164}", settings.consent_cache_ttl_seconds, status
        )
    return {"status": status, "source": "api", "raw": result}
