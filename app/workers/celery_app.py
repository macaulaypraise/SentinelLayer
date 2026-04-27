from celery import Celery

from app.config import settings

celery_app = Celery(
    "sentinellayer",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.workers.sim_swap_listener"],
)
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)
