import asyncio
import time
from typing import Any, cast

import structlog
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.camara import (
    call_forwarding,
    # stubs:
    customer_insights,
    device_identifier,
    device_reachability,
    device_roaming,
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
from app.core.notifications.sse import event_broadcaster
from app.core.scoring.agent import score_signals
from app.core.scoring.rules import fast_score
from app.core.scoring.weights import SIGNAL_WEIGHTS
from app.db.models import Account
from app.observability.metrics import fraud_checks_total, risk_score_histogram
from app.schemas.mode1 import Mode1Request
from kafka.producer import publish_fraud_signal

log = structlog.get_logger()


async def get_account_flag(phone: str, db: AsyncSession) -> dict[str, bool] | None:
    """
    Check if this account was pre-flagged by a SIM swap webhook.
    Returns signal hints if flagged, None otherwise.
    Only used for sub-10ms fast pre-check before Nokia API calls.
    """
    result = await db.execute(
        select(Account).where(
            Account.phone_number == phone,
            Account.is_flagged.is_(True),
        )
    )
    account = result.scalar_one_or_none()
    if account:
        # Webhook sets is_flagged=True when a SIM swap push arrives
        # We treat this as a confirmed sim_swap signal
        return {"sim_swap": True, "call_forwarding": False}
    return None


async def run_mode1(
    req: Mode1Request,
    session_id: str,
    redis_client: Redis,
    db: AsyncSession,
    tenant_id: str,
) -> dict[str, Any]:
    start = time.perf_counter()
    phone = req.phone_number

    # ── FAST PRE-CHECK (sub-10ms, no Nokia API calls) ──────────────────────
    # If the SIM swap webhook already pre-flagged this account,
    # we can short-circuit immediately without waiting for Nokia NaC.
    flagged = await get_account_flag(phone, db)
    if flagged:
        pre_signals = {k: False for k in SIGNAL_WEIGHTS}
        pre_signals["sim_swapped_recent"] = flagged.get("sim_swap", False)
        pre_signals["call_forwarding_active"] = flagged.get("call_forwarding", False)
        fast = fast_score(pre_signals)
        if fast:
            duration = time.perf_counter() - start
            fast_result: dict[str, Any] = {
                **fast,
                "mode_triggered": 1,
                "signals": pre_signals,
                "duration_ms": round(duration * 1000, 1),
                "source": "webhook_preflag",
            }
            # Still publish SSE and metrics for the dashboard
            await event_broadcaster.broadcast(
                tenant_id,
                {
                    "type": "RISK_FLAG",
                    "action": fast["recommended_action"],
                    "session_id": session_id,
                    "score": fast["risk_score"],
                    "phone": phone,
                    "drivers": fast.get("signal_drivers", []),
                    "source": "webhook_preflag",
                },
            )
            fraud_checks_total.labels(
                tenant_id=tenant_id,
                recommended_action=fast["recommended_action"],
                fast_path="True",
            ).inc()
            risk_score_histogram.labels(tenant_id=tenant_id).observe(fast["risk_score"])
            log.info(
                "mode1_preflag_fast_path",
                phone=phone,
                score=fast["risk_score"],
                action=fast["recommended_action"],
                duration_ms=round(duration * 1000, 1),
            )
            return fast_result

    # ── LIVE NOKIA NaC CAMARA CALLS (15 signals, parallel)
    try:
        results = await asyncio.wait_for(
            asyncio.gather(
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
                device_roaming.check_roaming(phone),
                return_exceptions=True,
            ),
            timeout=6.0,  # Max 6 seconds for the entire batch
        )
    except TimeoutError:
        log.warn("nokia_nac_gather_timeout", phone=phone)
        results = [{}] * 15  # Fallback to empty results on timeout

    def _safe(r: object) -> dict[str, Any]:
        """Return result dict, or {} if the CAMARA call raised an exception."""
        return cast(dict[str, Any], r) if isinstance(r, dict) else {}

    sim, fwd, dsw, nv, rec, km, kt, ins, lv, fl, pd, rc, di, dr, rm = [_safe(r) for r in results]

    signals: dict[str, Any] = {
        "call_forwarding_active": fwd.get("active", False),
        "sim_swapped_recent": sim.get("swapped", False),
        "device_swapped": dsw.get("swapped", False),
        "number_verification_failed": not nv.get("verified", True),
        "number_recycled": rec.get("recycled", False),
        "kyc_match_score_low": km.get("name_match", True) is False,
        "kyc_tenure_short": not kt.get("tenure_date_check", True),
        "customer_insight_spike": ins.get("anomaly", False),
        "location_outside_region": lv.get("verificationResult", "TRUE") == "FALSE",
        "location_no_baseline": fl.get("baseline") == "unknown",
        "population_density_anomaly": pd.get("anomalous", False),
        "region_device_sparse": rc.get("sparse", False),
        "device_identifier_new": di.get("newDevice", False),
        "device_unreachable": not dr.get("reachable", True),
        "device_roaming_anomaly": rm.get("roaming", False),
    }

    # ── SCORING ─────────────────────────────────────────────────────────────
    scored = await score_signals(signals)
    duration = time.perf_counter() - start

    # ── SSE BROADCAST ON HOLD OR STEP-UP ────────────────────────────────────
    if scored.get("recommended_action") in ("HOLD", "STEP-UP"):
        await event_broadcaster.broadcast(
            tenant_id,
            {
                "type": "RISK_FLAG",
                "action": scored["recommended_action"],
                "session_id": session_id,
                "score": scored.get("risk_score"),
                "phone": phone,
                "drivers": scored.get("signal_drivers", []),
            },
        )

    # ── METRICS ─────────────────────────────────────────────────────────────
    fraud_checks_total.labels(
        tenant_id=tenant_id,
        recommended_action=scored["recommended_action"],
        fast_path=str(scored.get("fast_path", False)),
    ).inc()
    risk_score_histogram.labels(tenant_id=tenant_id).observe(scored["risk_score"])

    log.info(
        "mode1_complete",
        phone=phone,
        score=scored["risk_score"],
        action=scored["recommended_action"],
        duration_ms=round(duration * 1000, 1),
    )

    await publish_fraud_signal(
        {"tenant_id": tenant_id, "phone": phone, "signals": signals, "score": scored}
    )

    return {
        **scored,
        "mode_triggered": 1,
        "signals": signals,
        "duration_ms": round(duration * 1000, 1),
    }
