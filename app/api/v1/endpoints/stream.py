import asyncio
import hashlib
import json
from collections.abc import AsyncGenerator

import structlog
from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select

from app.core.notifications.sse import event_broadcaster
from app.db.models import APIKey
from app.db.session import AsyncSessionLocal

router = APIRouter(prefix="/v1/sentinel", tags=["stream"])
log = structlog.get_logger()


async def _resolve_tenant(api_key: str) -> APIKey:
    """
    Validate API key passed as query param.
    Browsers cannot send custom headers on EventSource — query param is
    the standard SSE authentication pattern.
    """
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    async with AsyncSessionLocal() as db:
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


@router.get("/stream")
async def fraud_stream(
    api_key: str = Query(..., description="Tenant API key (query param — SSE standard)"),
) -> StreamingResponse:
    tenant = await _resolve_tenant(api_key)
    tenant_id = str(tenant.tenant_id)

    async def generator() -> AsyncGenerator[str, None]:
        queue = await event_broadcaster.subscribe(tenant_id)
        log.info("sse_client_connected", tenant_id=tenant_id)
        try:
            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield f"data: {json.dumps(event)}\n\n"
                except TimeoutError:
                    # Heartbeat keeps the connection alive through proxies
                    yield 'data: {"type":"heartbeat"}\n\n'
        finally:
            await event_broadcaster.unsubscribe(tenant_id, queue)
            log.info("sse_client_disconnected", tenant_id=tenant_id)

    return StreamingResponse(
        generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # disables Nginx buffering
            "Connection": "keep-alive",
        },
    )
