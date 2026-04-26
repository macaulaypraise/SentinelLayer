from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False
    )

    # Nokia NaC
    nac_client_id: str = ""
    nac_client_secret: str = ""
    nac_base_url: str = ""
    nac_token_url: str = ""
    nac_maas_endpoint: str = ""
    nac_maas_api_key: str = ""
    nac_request_url: str = ""
    nac_app_name: str = ""

    # Database
    database_url: str = "postgresql+asyncpg://sentinel:dev@localhost:5432/sentinellayer"

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # Kafka
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_sasl_username: str = ""
    kafka_sasl_password: str = ""
    kafka_fraud_signals_topic: str = "sentinel.fraud.signals"
    kafka_mode2_topic: str = "sentinel.mode2.triggers"

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
