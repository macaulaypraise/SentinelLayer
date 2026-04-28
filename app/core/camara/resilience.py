import logging
from typing import Any, Protocol, cast

import httpx
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)


class _LoggerProtocol(Protocol):
    def log(self, level: int, msg: str, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401
        ...


log = logging.getLogger(__name__)

camara_retry = retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=0.2, max=2.0),
    retry=retry_if_exception_type(
        (httpx.TimeoutException, httpx.ConnectError, httpx.HTTPStatusError)
    ),
    before_sleep=before_sleep_log(cast(_LoggerProtocol, log), logging.WARNING),
    reraise=True,
)
