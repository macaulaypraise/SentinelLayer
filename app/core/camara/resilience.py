# app/core/camara/resilience.py
import logging

import httpx
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

log = logging.getLogger(__name__)

camara_retry = retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=0.2, max=2.0),
    retry=retry_if_exception_type(
        (httpx.TimeoutException, httpx.ConnectError, httpx.HTTPStatusError)
    ),
    before_sleep=before_sleep_log(log, logging.WARNING),  # type: ignore[arg-type]
    reraise=True,
)
