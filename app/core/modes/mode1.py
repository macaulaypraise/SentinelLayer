import asyncio
import time
from typing import Any, cast

import structlog
from redis.asyncio import Redis

from app.core.camara import (
    call_forwarding,
    customer_insights,
    device_identifier,
    device_reachability,
    device_swap,
    kyc_match,
    kyc_tenure,
    location_verify,
    most_freq_location,
    number_recycling,
    number_verify,
    population_density,
    region_device_count,
    sim_swap,
)
from app.core.scoring.agent import score_signals
from app.observability.metrics import fraud_checks_total, risk_score_histogram
from app.schemas.mode1 import Mode1Request
from kafka.producer import publish_fraud_signal

log = structlog.get_logger()


async def run_mode1(
    req: Mode1Request,
    redis_client: Redis,
    tenant_id: str,
) -> dict[str, Any]:
    start = time.perf_counter()
    phone = req.phone_number

    # 14 CAMARA calls in parallel — wall time = slowest single call
    results = await asyncio.gather(
        sim_swap.check_sim_swap(phone),
        call_forwarding.check_call_forwarding(phone),
        device_swap.check_device_swap(phone),
        number_verify.verify_number(phone),
        number_recycling.check_recycling(phone, req.account_registered_at),
        kyc_match.check_kyc(phone, req.name, req.dob, req.address),
        kyc_tenure.check_tenure(phone),
        customer_insights.get_insights(phone),
        location_verify.verify_location(phone, req.expected_region),
        most_freq_location.get_frequent_location(phone),
        population_density.get_density(phone),
        region_device_count.get_count(phone),
        device_identifier.get_identifier(phone),
        device_reachability.check_reachability(phone),
        return_exceptions=True,  # fail open — CAMARA error != transaction blocked
    )

    def _safe(r: object) -> dict[str, Any]:
        """Return result as dict, or empty dict if the CAMARA call failed."""
        return cast(dict[str, Any], r) if isinstance(r, dict) else {}

    # Safely unpack results
    sim = _safe(results[0])
    fwd = _safe(results[1])
    dsw = _safe(results[2])
    nv = _safe(results[3])
    rec = _safe(results[4])
    km = _safe(results[5])
    kt = _safe(results[6])
    ins = _safe(results[7])
    lv = _safe(results[8])
    fl = _safe(results[9])
    pd = _safe(results[10])
    rc = _safe(results[11])
    di = _safe(results[12])
    dr = _safe(results[13])

    # Signals dictionary
    signals = {
        "call_forwarding_active": fwd.get("active", False),
        "sim_swapped_recent": sim.get("swapped", False),
        "device_swapped": dsw.get("swapped", False),
        "number_verification_failed": not nv.get("verified", True),
        "number_recycled": rec.get("recycled", False),
        "kyc_match_score_low": km.get("matchScore", 100) < 60,
        "kyc_tenure_short": kt.get("tenureDays", 999) < 90,
        "customer_insight_spike": ins.get("anomaly", False),
        "location_outside_region": not lv.get("inRegion", True),
        "location_no_baseline": fl.get("baseline") is None,
        "population_density_anomaly": pd.get("anomalous", False),
        "region_device_sparse": rc.get("sparse", False),
        "device_identifier_new": di.get("newDevice", False),
        "device_unreachable": not dr.get("reachable", True),
    }

    # Scoring
    scored = await score_signals(signals)
    duration = time.perf_counter() - start

    # Increment metrics
    fraud_checks_total.labels(
        tenant_id=tenant_id,
        recommended_action=scored["recommended_action"],
        fast_path=str(scored.get("fast_path", False)),
    ).inc()
    risk_score_histogram.labels(tenant_id=tenant_id).observe(scored["risk_score"])

    # Log the result
    log.info(
        "mode1_complete",
        phone=phone,
        score=scored["risk_score"],
        action=scored["recommended_action"],
        duration_ms=round(duration * 1000, 1),
    )

    # Publish fraud signal
    await publish_fraud_signal(
        {"tenant_id": tenant_id, "phone": phone, "signals": signals, "score": scored}
    )

    return {
        **scored,
        "mode_triggered": 1,
        "signals": signals,
        "duration_ms": round(duration * 1000, 1),
    }
