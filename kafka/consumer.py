import json
import logging
from collections.abc import Callable

from confluent_kafka import Consumer, KafkaError, KafkaException

from app.config import settings

log = logging.getLogger(__name__)


def _build_consumer_config() -> dict:
    conf: dict = {
        "bootstrap.servers": settings.kafka_bootstrap_servers,
        "group.id": "sentinellayer-fraud-processor",
        "auto.offset.reset": "earliest",
        "enable.auto.commit": False,
    }
    if settings.kafka_sasl_username:
        conf.update(
            {
                "sasl.mechanism": settings.kafka_sasl_mechanism,
                "security.protocol": settings.kafka_security_protocol,
                "sasl.username": settings.kafka_sasl_username,
                "sasl.password": settings.kafka_sasl_password,
            }
        )
    return conf


def consume_fraud_signals(
    handler: Callable[[dict], None],  # callable(event: dict) -> None
    max_messages: int | None = None,
) -> None:
    """
    Blocking consumer loop. Reads from sentinel.fraud.signals topic.
    Calls handler(event) for each message. Commits offset after handler
    succeeds — guarantees at-least-once delivery.

    Usage (in a standalone worker process or thread):
        from kafka.consumer import consume_fraud_signals
        consume_fraud_signals(handler=my_event_handler)
    """
    consumer = Consumer(_build_consumer_config())
    consumer.subscribe([settings.kafka_fraud_signals_topic])
    log.info("kafka_consumer_started", extra={"topic": settings.kafka_fraud_signals_topic})

    consumed = 0
    try:
        while True:
            msg = consumer.poll(timeout=1.0)

            if msg is None:
                continue

            err = msg.error()
            if err is not None:
                if err.code() == KafkaError._PARTITION_EOF:
                    # End of partition — not an error, just no new messages
                    continue
                raise KafkaException(err)

            value = msg.value()
            if value is None:
                log.warning("kafka_message_with_no_value", extra={"offset": msg.offset()})
                continue

            try:
                event: dict = json.loads(value.decode("utf-8"))
                handler(event)
                consumer.commit(message=msg)  # commit only after success
                # except Exception as exc:
                #     log.error("handler_failed", extra={"error": str(exc), "offset": msg.offset()})
                consumed += 1
                log.info(
                    "fraud_signal_consumed",
                    extra={
                        "event_id": event.get("event_id"),
                        "event_type": event.get("event_type"),
                        "offset": msg.offset(),
                    },
                )
            except Exception as exc:
                # Log and continue — do NOT commit so message is replayed
                log.error(
                    "fraud_signal_handler_failed", extra={"error": str(exc), "offset": msg.offset()}
                )

            if max_messages and consumed >= max_messages:
                break

    finally:
        consumer.close()
        log.info("kafka_consumer_closed")


def consume_mode2_triggers(handler: Callable[[dict], None]) -> None:
    """
    Separate consumer for Mode 2 trigger events.
    Runs in its own consumer group so Mode 1 and Mode 2
    events are processed independently without blocking each other.
    """
    conf = _build_consumer_config()
    conf["group.id"] = "sentinellayer-mode2-processor"

    consumer = Consumer(conf)
    consumer.subscribe([settings.kafka_mode2_topic])
    log.info("mode2_consumer_started", extra={"topic": settings.kafka_mode2_topic})

    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue

            err = msg.error()
            if err is not None:
                if err.code() == KafkaError._PARTITION_EOF:
                    continue
                raise KafkaException(err)

            value = msg.value()
            if value is None:
                log.warning("kafka_message_with_no_value")
                continue

            try:
                event: dict = json.loads(value.decode("utf-8"))
                handler(event)
                consumer.commit(message=msg)
            except Exception as exc:
                log.error("mode2_trigger_handler_failed", extra={"error": str(exc)})
    finally:
        consumer.close()
