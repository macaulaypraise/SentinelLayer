import json
import uuid
from datetime import UTC, datetime

from confluent_kafka import Producer

from app.config import settings

_producer: Producer | None = None


def _get_producer() -> Producer:
    global _producer
    if _producer is None:
        conf: dict = {"bootstrap.servers": settings.kafka_bootstrap_servers}
        if settings.kafka_sasl_username:
            conf.update(
                {
                    "sasl.mechanism": "PLAIN",
                    "security.protocol": "SASL_SSL",
                    "sasl.username": settings.kafka_sasl_username,
                    "sasl.password": settings.kafka_sasl_password,
                }
            )
        _producer = Producer(conf)
    return _producer


async def publish_fraud_signal(data: dict) -> None:
    event = {
        "event_id": str(uuid.uuid4()),
        "event_type": "FRAUD_SIGNAL",
        "timestamp": datetime.now(UTC).isoformat(),
        "payload": data,
    }
    p = _get_producer()
    p.produce(
        settings.kafka_fraud_signals_topic,
        key=data.get("account_id", "unknown").encode(),
        value=json.dumps(event).encode(),
    )
    p.poll(0)
