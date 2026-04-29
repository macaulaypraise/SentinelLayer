from typing import Any

import httpx
import phonenumbers

from app.config import settings
from app.observability.metrics import camara_api_errors, camara_api_latency


def normalise(phone: str, region: str = "NG") -> str:
    """Parse any format and return E.164."""
    parsed = phonenumbers.parse(phone, region)
    if not phonenumbers.is_valid_number(parsed):
        raise ValueError(f"Invalid phone number: {phone}")
    return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)


def _headers() -> dict[str, str]:
    """RapidAPI auth — two headers, no OAuth2, no token exchange."""
    return {
        "x-rapidapi-key": settings.nac_rapidapi_key,
        "x-rapidapi-host": settings.nac_rapidapi_host,
        "Content-Type": "application/json",
    }


async def nac_get(
    endpoint: str,
    params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    api_name = endpoint.lstrip("/").split("/")[0]
    with camara_api_latency.labels(api_name=api_name).time():
        try:
            async with httpx.AsyncClient(timeout=10.0) as c:
                r = await c.get(
                    f"{settings.nac_base_url}{endpoint}",
                    headers=_headers(),
                    params=params or {},
                )
                r.raise_for_status()
                return dict(r.json())
        except Exception as e:
            camara_api_errors.labels(api_name=api_name, error_type=type(e).__name__).inc()
            raise


async def nac_post(
    endpoint: str,
    body: dict[str, Any],
) -> dict[str, Any]:
    api_name = endpoint.lstrip("/").split("/")[0]
    with camara_api_latency.labels(api_name=api_name).time():
        try:
            async with httpx.AsyncClient(timeout=10.0) as c:
                r = await c.post(
                    f"{settings.nac_base_url}{endpoint}",
                    headers=_headers(),
                    json=body,
                )
                r.raise_for_status()
                return dict(r.json())
        except Exception as e:
            camara_api_errors.labels(api_name=api_name, error_type=type(e).__name__).inc()
            raise
