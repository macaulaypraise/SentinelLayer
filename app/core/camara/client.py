import time
from typing import Any

import httpx
import phonenumbers
import structlog

from app.config import settings
from app.observability.metrics import camara_api_errors, camara_api_latency

log = structlog.get_logger()
_token_cache: dict[str, Any] = {}


def normalise(phone: str, region: str = "NG") -> str:
    """Parse any format and return E.164. Handles NG, KE, GH, ZA."""
    parsed = phonenumbers.parse(phone, region)
    if not phonenumbers.is_valid_number(parsed):
        raise ValueError(f"Invalid phone number: {phone}")
    return str(phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164))


async def get_access_token() -> str:
    """OAuth2 client credentials. Cached until 60s before expiry."""
    now = time.time()
    if _token_cache.get("expires_at", 0) - now > 60:
        return str(_token_cache["access_token"])
    async with httpx.AsyncClient(timeout=10.0) as c:
        r = await c.post(
            settings.nac_token_url,
            data={
                "grant_type": "client_credentials",
                "client_id": settings.nac_client_id,
                "client_secret": settings.nac_client_secret,
                "scope": "openid",
            },
        )
        r.raise_for_status()
        d = r.json()
    _token_cache.update(
        {"access_token": d["access_token"], "expires_at": now + d.get("expires_in", 3600)}
    )
    log.info("nac_token_refreshed")
    return str(_token_cache["access_token"])


async def nac_get(endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    api_name = endpoint.lstrip("/").split("/")[0]
    token = await get_access_token()
    with camara_api_latency.labels(api_name=api_name).time():
        try:
            async with httpx.AsyncClient(timeout=10.0) as c:
                r = await c.get(
                    f"{settings.nac_base_url}{endpoint}",
                    headers={"Authorization": f"Bearer {token}"},
                    params=params or {},
                )
                r.raise_for_status()
                return dict(r.json())
        except Exception as e:
            camara_api_errors.labels(api_name=api_name, error_type=type(e).__name__).inc()
            raise


async def nac_post(endpoint: str, body: dict[str, Any]) -> dict[str, Any]:
    api_name = endpoint.lstrip("/").split("/")[0]
    token = await get_access_token()
    with camara_api_latency.labels(api_name=api_name).time():
        try:
            async with httpx.AsyncClient(timeout=10.0) as c:
                r = await c.post(
                    f"{settings.nac_base_url}{endpoint}",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json",
                    },
                    json=body,
                )
                r.raise_for_status()
                return dict(r.json())
        except Exception as e:
            camara_api_errors.labels(api_name=api_name, error_type=type(e).__name__).inc()
            raise
