import uuid
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from tests.fixtures.camara_responses import (
    CLEAN_DEV_ID,
    CLEAN_DEVICE_SWAP,
    CLEAN_FORWARDING,
    CLEAN_FREQ_LOC,
    CLEAN_INSIGHTS,
    CLEAN_KYC,
    CLEAN_LOC_VERIFY,
    CLEAN_NUM_VERIFY,
    CLEAN_POP_DENSITY,
    CLEAN_REACHABILITY,
    CLEAN_RECYCLING,
    CLEAN_REGION_COUNT,
    CLEAN_SIM_SWAP,
    CLEAN_TENURE,
)

TEST_TENANT_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")

TEST_PAYLOAD = {
    "phone_number": "+2348012345678",
    "account_id": "acc_001",
    "transaction_amount": 45000,
    "expected_region": "Lagos",
    "name": "John Doe",
    "dob": "1990-01-01",
    "address": "12 Victoria Island",
    "account_registered_at": "2023-06-01",
}


class FakeTenant:
    tenant_id: uuid.UUID = TEST_TENANT_ID
    tier: str = "DEVELOPER"


@pytest.mark.asyncio
async def test_health_endpoint() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        r = await c.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_clean_transaction_returns_allow(test_tenant_in_db: uuid.UUID) -> None:
    # test_tenant_in_db fixture ensures the tenant row exists in DB
    from app.core.security.api_key import get_current_tenant

    app.dependency_overrides[get_current_tenant] = lambda: FakeTenant()

    try:
        with (
            patch(
                "app.core.camara.sim_swap.check_sim_swap",
                new=AsyncMock(return_value=CLEAN_SIM_SWAP),
            ),
            patch(
                "app.core.camara.call_forwarding.check_call_forwarding",
                new=AsyncMock(return_value=CLEAN_FORWARDING),
            ),
            patch(
                "app.core.camara.device_swap.check_device_swap",
                new=AsyncMock(return_value=CLEAN_DEVICE_SWAP),
            ),
            patch(
                "app.core.camara.number_verify.verify_number",
                new=AsyncMock(return_value=CLEAN_NUM_VERIFY),
            ),
            patch(
                "app.core.camara.number_recycling.check_recycling",
                new=AsyncMock(return_value=CLEAN_RECYCLING),
            ),
            patch("app.core.camara.kyc_match.check_kyc", new=AsyncMock(return_value=CLEAN_KYC)),
            patch(
                "app.core.camara.kyc_tenure.check_tenure", new=AsyncMock(return_value=CLEAN_TENURE)
            ),
            patch(
                "app.core.camara.customer_insights.get_insights",
                new=AsyncMock(return_value=CLEAN_INSIGHTS),
            ),
            patch(
                "app.core.camara.location_verify.verify_location",
                new=AsyncMock(return_value=CLEAN_LOC_VERIFY),
            ),
            patch(
                "app.core.camara.most_freq_location.get_frequent_location",
                new=AsyncMock(return_value=CLEAN_FREQ_LOC),
            ),
            patch(
                "app.core.camara.population_density.get_density",
                new=AsyncMock(return_value=CLEAN_POP_DENSITY),
            ),
            patch(
                "app.core.camara.region_device_count.get_count",
                new=AsyncMock(return_value=CLEAN_REGION_COUNT),
            ),
            patch(
                "app.core.camara.device_identifier.get_identifier",
                new=AsyncMock(return_value=CLEAN_DEV_ID),
            ),
            patch(
                "app.core.camara.device_reachability.check_reachability",
                new=AsyncMock(return_value=CLEAN_REACHABILITY),
            ),
            patch(
                "app.core.modes.mode1.score_signals",
                new=AsyncMock(
                    return_value={
                        "risk_score": 5,
                        "recommended_action": "ALLOW",
                        "signal_drivers": [],
                    }
                ),
            ),
            patch("app.core.modes.mode1.publish_fraud_signal", new=AsyncMock()),
        ):
            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test",
                headers={"X-API-Key": "test-key"},
            ) as c:
                r = await c.post("/v1/sentinel/check", json=TEST_PAYLOAD)
    finally:
        app.dependency_overrides.clear()

    assert r.status_code == 200
    data = r.json()
    assert data["recommended_action"] in ["ALLOW", "STEP-UP"]
    assert "session_id" in data
    assert "signals" in data
    assert len(data["signals"]) == 14
