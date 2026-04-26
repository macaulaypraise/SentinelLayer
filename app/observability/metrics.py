from prometheus_client import Counter, Gauge, Histogram

fraud_checks_total = Counter(
    "sentinel_fraud_checks_total",
    "Total fraud risk checks processed",
    ["tenant_id", "recommended_action", "fast_path"],
)
risk_score_histogram = Histogram(
    "sentinel_risk_score",
    "Distribution of risk scores",
    ["tenant_id"],
    buckets=[10, 20, 30, 44, 45, 60, 70, 85, 100],
)
mode2_triggers_total = Counter(
    "sentinel_mode2_triggers_total",
    "Mode 2 live enforcement triggers",
    ["tenant_id", "trigger_reason"],
)
camara_api_latency = Histogram(
    "sentinel_camara_api_duration_seconds",
    "CAMARA API call latency by API name",
    ["api_name"],
    buckets=[0.05, 0.1, 0.2, 0.3, 0.5, 1.0, 2.0, 5.0],
)
camara_api_errors = Counter(
    "sentinel_camara_api_errors_total", "CAMARA API call failures", ["api_name", "error_type"]
)
mode2_active = Gauge("sentinel_mode2_active_total", "Live Mode 2 enforcement sessions active")
