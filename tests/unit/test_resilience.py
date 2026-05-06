from unittest.mock import patch

import httpx
import pytest

from app.core.camara.call_forwarding import check_call_forwarding


@pytest.mark.asyncio
async def test_camara_circuit_breaker_timeout() -> None:
    """
    Validates that Tenacity catches network timeouts, retries,
    and eventually raises the exception.
    """
    # Fix: Mock .post instead of .get
    with patch("httpx.AsyncClient.post", side_effect=httpx.TimeoutException("Nokia API Down")):
        with pytest.raises(httpx.TimeoutException):
            await check_call_forwarding("+2348011111111")
