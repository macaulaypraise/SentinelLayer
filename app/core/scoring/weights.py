SIGNAL_WEIGHTS: dict[str, int] = {
    "call_forwarding_active": 35,
    "sim_swapped_recent": 30,
    "device_swapped": 25,
    "number_recycled": 25,
    "number_verification_failed": 20,
    "kyc_match_score_low": 18,
    "kyc_tenure_short": 15,
    "location_outside_region": 15,
    "device_unreachable": 15,
    "customer_insight_spike": 10,
    "population_density_anomaly": 8,
    "region_device_sparse": 7,
    "location_no_baseline": 5,
    "device_identifier_new": 5,
}
THRESHOLD_MODE2 = 45
THRESHOLD_HOLD = 70
