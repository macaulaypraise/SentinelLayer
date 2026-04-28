import asyncio
from collections import defaultdict
from typing import Any


class EventBroadcaster:
    def __init__(self) -> None:
        self._queues: dict[str, list[asyncio.Queue[dict[str, Any]]]] = defaultdict(list)

    async def subscribe(self, tenant_id: str) -> asyncio.Queue[dict[str, Any]]:
        q: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=100)
        self._queues[tenant_id].append(q)
        return q

    async def unsubscribe(self, tenant_id: str, q: asyncio.Queue[dict[str, Any]]) -> None:
        try:
            self._queues[tenant_id].remove(q)
        except ValueError:
            pass

    async def broadcast(self, tenant_id: str, event: dict[str, Any]) -> None:
        for q in list(self._queues.get(tenant_id, [])):
            if not q.full():
                await q.put(event)


event_broadcaster = EventBroadcaster()
