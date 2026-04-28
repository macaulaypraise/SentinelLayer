from datetime import UTC

import structlog
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.camara.consent_info import get_consent_status
from app.core.security.api_key import get_current_tenant
from app.db.models import Account, APIKey
from app.dependencies import get_db, get_redis

router = APIRouter(prefix="/v1/sentinel", tags=["consent"])
log = structlog.get_logger()


# ── Schemas ────────────────────────────────────────────────────────────────


class ConsentCheckRequest(BaseModel):
    phone_number: str


class ConsentCheckResponse(BaseModel):
    phone_number: str
    consent_status: str  # GRANTED | DENIED | PENDING | UNKNOWN
    source: str  # cache | api
    account_flagged: bool


class ConsentGrantRequest(BaseModel):
    phone_number: str
    authorised_by: str  # ACCOUNT_HOLDER | INSTITUTION | TELECOM


class ConsentGrantResponse(BaseModel):
    phone_number: str
    consent_status: str
    account_updated: bool


# ── Endpoints ──────────────────────────────────────────────────────────────


@router.post("/consent/check", response_model=ConsentCheckResponse)
async def check_consent(
    body: ConsentCheckRequest,
    tenant: APIKey = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> ConsentCheckResponse:
    """
    Query consent status for a phone number via Nokia NaC Consent Info API.
    Checks Redis cache first (300s TTL), then live API.

    Used by institutions before triggering Mode 2 live enforcement —
    confirms the legal gate is satisfied before precise location is requested.
    """
    consent = await get_consent_status(body.phone_number, redis)

    # Check if account is flagged (pre-emptive SIM swap flag)
    result = await db.execute(
        select(Account).where(
            Account.phone_number == body.phone_number,
            Account.tenant_id == tenant.tenant_id,
        )
    )
    account = result.scalar_one_or_none()
    is_flagged = account.is_flagged if account else False

    log.info(
        "consent_checked",
        phone=body.phone_number,
        status=consent["status"],
        source=consent["source"],
        tenant_id=str(tenant.tenant_id),
    )

    return ConsentCheckResponse(
        phone_number=body.phone_number,
        consent_status=consent["status"],
        source=consent["source"],
        account_flagged=is_flagged,
    )


@router.post("/consent/grant", response_model=ConsentGrantResponse)
async def record_consent_grant(
    body: ConsentGrantRequest,
    tenant: APIKey = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> ConsentGrantResponse:
    """
    Records that consent has been granted for a phone number.
    Updates the account record and warms the Redis consent cache.

    Called when:
    1. The account holder verbally confirms to their institution.
    2. The institution's fraud desk confirms independently.
    3. The telecom provider confirms via their security channel.

    This creates the auditable record that protects both the institution
    and the telecom entity from legal repercussion.
    """
    from app.config import settings
    from app.core.camara.client import normalise

    e164 = normalise(body.phone_number)

    # Warm the consent cache immediately
    cache_key = f"consent:{e164}"
    await redis.setex(cache_key, settings.consent_cache_ttl_seconds, "GRANTED")

    # Update account consent record in DB
    result = await db.execute(
        select(Account).where(
            Account.phone_number == e164,
            Account.tenant_id == tenant.tenant_id,
        )
    )
    account = result.scalar_one_or_none()
    account_updated = False

    if account:
        from datetime import datetime

        account.consent_granted = True
        account.consent_updated = datetime.now(UTC)
        await db.commit()
        account_updated = True

    log.info(
        "consent_granted",
        phone=e164,
        authorised_by=body.authorised_by,
        account_updated=account_updated,
        tenant_id=str(tenant.tenant_id),
    )

    return ConsentGrantResponse(
        phone_number=e164,
        consent_status="GRANTED",
        account_updated=account_updated,
    )


@router.delete("/consent/revoke", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_consent(
    body: ConsentCheckRequest,
    tenant: APIKey = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> None:
    """
    Revokes consent for a phone number.
    Clears Redis cache and updates account record.
    Mode 2 cannot retrieve location after this until consent is re-granted.
    """
    from app.core.camara.client import normalise

    e164 = normalise(body.phone_number)
    cache_key = f"consent:{e164}"
    await redis.delete(cache_key)

    result = await db.execute(
        select(Account).where(
            Account.phone_number == e164,
            Account.tenant_id == tenant.tenant_id,
        )
    )
    account = result.scalar_one_or_none()
    if account:
        account.consent_granted = False
        await db.commit()

    log.info("consent_revoked", phone=e164, tenant_id=str(tenant.tenant_id))
