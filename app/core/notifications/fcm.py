import asyncio
from typing import Any

import firebase_admin
import structlog
from firebase_admin import App, credentials, messaging

from app.config import settings

log = structlog.get_logger()

# Initialise Firebase Admin SDK once at import time
_firebase_app = None


def _get_firebase_app() -> App:
    global _firebase_app
    if _firebase_app is None:
        cred = credentials.Certificate(settings.firebase_service_account_path)
        _firebase_app = firebase_admin.initialize_app(cred)
    return _firebase_app


def _send_fcm_sync(token: str, title: str, body: str, data: dict[str, Any]) -> None:
    """Synchronous FCM V1 send via firebase-admin SDK."""
    _get_firebase_app()
    message = messaging.Message(
        notification=messaging.Notification(title=title, body=body),
        data={k: str(v) for k, v in data.items()},  # data values must be strings
        token=token,
    )
    response = messaging.send(message)
    log.info("fcm_sent", response=response, token=token[:10])


async def _send_fcm(token: str, title: str, body: str, data: dict[str, Any]) -> None:
    """Async wrapper — runs sync SDK call in thread pool."""
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _send_fcm_sync, token, title, body, data)


async def send_mode2_alert(payload: dict[str, Any]) -> None:
    """Three-way simultaneous push — all parties notified at the same moment."""
    msg = f"LIVE FRAUD ALERT | {payload['phone']} | Trigger: {payload['trigger']}"
    await asyncio.gather(
        _send_fcm(settings.fraud_desk_fcm_token, "SentinelLayer: Live Fraud Alert", msg, payload),
        _send_fcm(settings.telecom_team_fcm_token, "SentinelLayer: Live Fraud Alert", msg, payload),
        return_exceptions=True,
    )


async def send_preemptive_alert(payload: dict[str, Any]) -> None:
    """Fires when SIM Swap webhook received — before any fraud attempt."""
    msg = f"SIM SWAP DETECTED | {payload['phone']} | {payload.get('swap_time', '')}"
    await _send_fcm(settings.fraud_desk_fcm_token, "SentinelLayer: SIM Swap Alert", msg, payload)
