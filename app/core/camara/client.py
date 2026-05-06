from typing import Any

import httpx
import phonenumbers

from app.config import settings
from app.observability.metrics import camara_api_errors, camara_api_latency

# Initialize a global client for connection pooling and keep-alive
http_client = httpx.AsyncClient(
    timeout=4.0, limits=httpx.Limits(max_keepalive_connections=100, max_connections=200)
)


def normalise(phone: str, region: str = "NG") -> str:
    # 1. Bypass validation for Nokia sandbox numbers
    if phone.startswith("+999"):
        return phone

    # 2. Proceed with standard validation for real numbers
    parsed = phonenumbers.parse(phone, region)
    if not phonenumbers.is_valid_number(parsed):
        raise ValueError(f"Invalid phone number: {phone}")
    return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)


def _headers() -> dict[str, str]:
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
            # Use the global client instead of opening a new socket
            r = await http_client.get(
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
            # Use the global client here as well
            r = await http_client.post(
                f"{settings.nac_base_url}{endpoint}",
                headers=_headers(),
                json=body,
            )
            r.raise_for_status()
            return dict(r.json())
        except Exception as e:
            camara_api_errors.labels(api_name=api_name, error_type=type(e).__name__).inc()
            raise
