from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.modes.mode3 import run_mode3
from app.core.security.api_key import get_current_tenant
from app.db.models import APIKey
from app.dependencies import get_db
from app.schemas.request import PostmortemRequest
from app.schemas.response import PostmortemResponse

router = APIRouter(prefix="/v1/sentinel", tags=["postmortem"])


@router.post("/postmortem", response_model=PostmortemResponse)
async def postmortem(
    req: PostmortemRequest,
    tenant: APIKey = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
) -> PostmortemResponse:
    start = datetime.fromisoformat(req.incident_start).replace(tzinfo=UTC)
    end = datetime.fromisoformat(req.incident_end).replace(tzinfo=UTC)
    result = await run_mode3(
        req.session_id, req.phone_number, start, end, db, str(tenant.tenant_id)
    )
    return PostmortemResponse(**result)
