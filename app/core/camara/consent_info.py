from redis.asyncio import Redis

from app.config import settings

from .client import nac_post, normalise

# Nokia NaC simulator numbers that should always return GRANTED consent.
# The real Nokia consent API returns UNKNOWN for these numbers because
# they are test identifiers with no real subscriber records.
_SIMULATOR_NUMBERS = {"+99999991000", "+99999991001", "+99999991002", "+99999991003"}


async def get_consent_status(phone: str, redis_client: Redis) -> dict[str, str]:
    e164 = normalise(phone)

    # ── Simulator override ──────────────────────────────────────────────────
    # Grant consent immediately for Nokia simulator numbers so Mode 2
    # can proceed to Location Retrieval during the demo.
    if e164 in _SIMULATOR_NUMBERS:
        return {"status": "GRANTED", "source": "simulator_override"}

    # ── Cache check ─────────────────────────────────────────────────────────
    cached = await redis_client.get(f"consent:{e164}")
    if cached:
        return {"status": cached.decode(), "source": "cache"}

    # ── Live Nokia NaC Consent Info API ─────────────────────────────────────
    try:
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
    except Exception:
        status = "UNKNOWN"

    # Cache GRANTED status to avoid repeated API calls within the TTL window
    if status == "GRANTED":
        await redis_client.setex(f"consent:{e164}", settings.consent_cache_ttl_seconds, status)

    return {"status": status, "source": "api"}
