import asyncio
import json
from collections.abc import AsyncGenerator

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.core.notifications.sse import event_broadcaster
from app.core.security.api_key import get_current_tenant
from app.db.models import APIKey

router = APIRouter(prefix="/v1/sentinel", tags=["stream"])


@router.get("/stream")
async def fraud_stream(
    tenant: APIKey = Depends(get_current_tenant),
) -> StreamingResponse:
    async def generator() -> AsyncGenerator[str, None]:
        queue = await event_broadcaster.subscribe(str(tenant.tenant_id))
        try:
            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield f"data: {json.dumps(event)}\n\n"
                except TimeoutError:
                    yield 'data: {"type":"heartbeat"}\n\n'
        finally:
            await event_broadcaster.unsubscribe(str(tenant.tenant_id), queue)

    return StreamingResponse(
        generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
