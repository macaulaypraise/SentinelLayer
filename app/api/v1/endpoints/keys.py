import hashlib
import secrets
import uuid

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security.api_key import get_current_tenant
from app.db.models import APIKey
from app.dependencies import get_db

router = APIRouter(prefix="/v1/keys", tags=["api-keys"])
log = structlog.get_logger()


# ── Schemas ────────────────────────────────────────────────────────────────


class APIKeyCreateRequest(BaseModel):
    label: str | None = None


class APIKeyResponse(BaseModel):
    id: str
    key_prefix: str
    label: str | None
    is_active: bool
    created_at: str
    # raw_key only returned on creation — never stored, never shown again
    raw_key: str | None = None


class APIKeyListResponse(BaseModel):
    keys: list[APIKeyResponse]


# ── Helpers ────────────────────────────────────────────────────────────────


def _generate_key() -> tuple[str, str, str]:
    """
    Returns (raw_key, key_hash, key_prefix).
    raw_key   — shown to user ONCE at creation time, never stored.
    key_hash  — SHA-256 stored in DB, used for lookup.
    key_prefix — first 12 chars shown in listings for identification.
    """
    raw = f"sl_live_{secrets.token_urlsafe(32)}"
    key_hash = hashlib.sha256(raw.encode()).hexdigest()
    prefix = raw[:12]
    return raw, key_hash, prefix


# ── Endpoints ──────────────────────────────────────────────────────────────


@router.post(
    "/",
    response_model=APIKeyResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_api_key(
    body: APIKeyCreateRequest,
    tenant: APIKey = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
) -> APIKeyResponse:
    """
    Create a new API key for the calling tenant.
    The raw key is returned ONCE — store it immediately.
    It cannot be retrieved again.
    """
    raw_key, key_hash, key_prefix = _generate_key()

    new_key = APIKey(
        tenant_id=tenant.tenant_id,
        key_hash=key_hash,
        key_prefix=key_prefix,
        label=body.label,
        is_active=True,
    )
    db.add(new_key)
    await db.commit()
    await db.refresh(new_key)

    log.info(
        "api_key_created",
        tenant_id=str(tenant.tenant_id),
        key_prefix=key_prefix,
        label=body.label,
    )

    return APIKeyResponse(
        id=str(new_key.id),
        key_prefix=new_key.key_prefix,
        label=new_key.label,
        is_active=new_key.is_active,
        created_at=new_key.created_at.isoformat(),
        raw_key=raw_key,  # only time this is ever returned
    )


@router.get("/", response_model=APIKeyListResponse)
async def list_api_keys(
    tenant: APIKey = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
) -> APIKeyListResponse:
    """List all active API keys for the calling tenant (no raw keys shown)."""
    result = await db.execute(
        select(APIKey).where(
            APIKey.tenant_id == tenant.tenant_id,
            APIKey.is_active.is_(True),
        )
    )
    keys = result.scalars().all()

    return APIKeyListResponse(
        keys=[
            APIKeyResponse(
                id=str(k.id),
                key_prefix=k.key_prefix,
                label=k.label,
                is_active=k.is_active,
                created_at=k.created_at.isoformat(),
            )
            for k in keys
        ]
    )


@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_api_key(
    key_id: str,
    tenant: APIKey = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Revoke an API key. Sets is_active=False — does not delete.
    Audit trail is preserved in the DB.
    """
    result = await db.execute(
        select(APIKey).where(
            APIKey.id == uuid.UUID(key_id),
            APIKey.tenant_id == tenant.tenant_id,  # tenant scope enforced
        )
    )
    key = result.scalar_one_or_none()

    if not key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found or does not belong to this tenant.",
        )

    key.is_active = False
    await db.commit()

    log.info(
        "api_key_revoked",
        key_id=key_id,
        tenant_id=str(tenant.tenant_id),
    )
