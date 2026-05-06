from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    # Nokia NaC
    nac_base_url: str = "https://network-as-code.p-eu.rapidapi.com"
    nac_rapidapi_key: str = ""
    nac_rapidapi_host: str = "network-as-code.nokia.rapidapi.com"

    # Database
    database_url: str = "postgresql+asyncpg://sentinel:dev@localhost:5432/sentinellayer"
    test_database_url: str = "postgresql+asyncpg://sentinel:dev@localhost:5432/sentinellayer_test"

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    test_redis_url: str = "redis://localhost:6379/9"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # Kafka
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_sasl_username: str = ""
    kafka_sasl_password: str = ""
    kafka_fraud_signals_topic: str = "sentinel.fraud.signals"
    kafka_mode2_topic: str = "sentinel.mode2.triggers"
    kafka_sasl_mechanism: str = "PLAIN"
    kafka_security_protocol: str = "SASL_SSL"

    # Observability
    otel_exporter_otlp_endpoint: str = "http://localhost:4317"
    otel_service_name: str = "sentinellayer"
    sentry_dsn: str = ""

    # Firebase
    fraud_desk_fcm_token: str = ""
    telecom_team_fcm_token: str = ""
    firebase_service_account_path: str = "./firebase-service-account.json"
    firebase_project_id: str = "sentinellayer"

    # Google Maps
    google_maps_api_key: str = ""
    gemini_api_key: str = ""

    # Application
    risk_threshold_mode2: int = 45
    risk_threshold_hold: int = 70
    sim_swap_window_hours: int = 72
    consent_cache_ttl_seconds: int = 300
    app_env: str = "development"
    port: int = 8000


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
