import hashlib
from typing import Annotated

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import APIKey
from app.dependencies import get_db

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)


async def get_current_tenant(
    db: Annotated[AsyncSession, Depends(get_db)],
    api_key: str = Security(api_key_header),
) -> APIKey:
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    result = await db.execute(
        select(APIKey).where(
            APIKey.key_hash == key_hash,
            APIKey.is_active.is_(True),
        )
    )
    tenant = result.scalar_one_or_none()

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or revoked API key",
        )

    return tenant
