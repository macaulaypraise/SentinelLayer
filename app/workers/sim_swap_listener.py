import structlog
from celery import Task

from app.config import settings
from app.workers.celery_app import celery_app

log = structlog.get_logger()


@celery_app.task(bind=True, max_retries=3, default_retry_delay=5)
def handle_sim_swap_webhook(self: Task, payload: dict) -> None:
    """Fires when Nokia NaC SIM Swap subscription push arrives."""
    try:
        from sqlalchemy import create_engine, select
        from sqlalchemy.orm import Session as SyncSession

        from app.db.models import Account

        sync_url = settings.database_url.replace("+asyncpg", "")
        engine = create_engine(sync_url, pool_pre_ping=True)

        phone = payload.get("phoneNumber", "")
        swap_time = payload.get("swapTimestamp", "")

        with SyncSession(engine) as db:
            account = db.execute(
                select(Account).where(Account.phone_number == phone)
            ).scalar_one_or_none()
            if account:
                account.is_flagged = True
                account.flag_reason = f"SIM swapped at {swap_time}"
                db.commit()
                log.info("account_pre_flagged", phone=phone, swap_time=swap_time)

        import asyncio

        from kafka.producer import publish_fraud_signal

        asyncio.run(
            publish_fraud_signal(
                {"type": "WEBHOOK_SIM_SWAP", "phone": phone, "swap_time": swap_time}
            )
        )
    except Exception as exc:
        raise self.retry(exc=exc) from exc
