import uuid

import structlog
from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.modes.mode1 import run_mode1
from app.core.modes.mode2 import run_mode2
from app.core.notifications.sse import event_broadcaster
from app.core.security.api_key import get_current_tenant
from app.db.models import APIKey
from app.db.models import Session as DBSession
from app.dependencies import get_db, get_redis
from app.schemas.mode1 import Mode1Request
from app.schemas.request import SentinelCheckRequest
from app.schemas.response import Mode2Result, SentinelCheckResponse

router = APIRouter(prefix="/v1/sentinel", tags=["sentinel"])
log = structlog.get_logger()


@router.post("/check", response_model=SentinelCheckResponse)
async def sentinel_check(
    req: SentinelCheckRequest,  # external contract stays
    tenant: APIKey = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> SentinelCheckResponse:
    session_id = str(uuid.uuid4())
    tenant_id = str(tenant.tenant_id)

    # ── Convert external request to internal Mode 1 contract ──
    mode1_req = Mode1Request(
        phone_number=req.phone_number,
        account_registered_at=req.account_registered_at,
        name=req.name,
        dob=req.dob,
        address=req.address,
        expected_region=req.expected_region,
    )

    mode1_result = await run_mode1(mode1_req, session_id, redis, db, tenant_id)

    session = DBSession(
        id=uuid.UUID(session_id),
        tenant_id=tenant.tenant_id,
        account_id=req.account_id,
        phone_number=req.phone_number,
        transaction_amount=req.transaction_amount,
        risk_score=mode1_result["risk_score"],
        recommended_action=mode1_result["recommended_action"],
        mode_triggered=1,
        signals=mode1_result["signals"],
        signal_drivers=mode1_result.get("signal_drivers"),
        fast_path=mode1_result.get("fast_path", False),
    )
    db.add(session)
    await db.commit()

    if mode1_result["risk_score"] >= settings.risk_threshold_mode2:
        await event_broadcaster.broadcast(
            tenant_id,
            {
                "type": "RISK_FLAG",
                "session_id": session_id,
                "score": mode1_result["risk_score"],
                "action": mode1_result["recommended_action"],
                "drivers": mode1_result.get("signal_drivers", []),
            },
        )
        mode2_result = await run_mode2(
            session_id, req.phone_number, "MODE1_THRESHOLD", redis, db, tenant_id
        )
        return SentinelCheckResponse(
            session_id=session_id, **mode1_result, mode2=Mode2Result(**mode2_result)
        )
    return SentinelCheckResponse(session_id=session_id, **mode1_result)
