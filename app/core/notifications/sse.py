import asyncio
from collections import defaultdict


class EventBroadcaster:
    def __init__(self) -> None:
        self._queues: dict[str, list[asyncio.Queue]] = defaultdict(list)

    async def subscribe(self, tenant_id: str) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue(maxsize=100)
        self._queues[tenant_id].append(q)
        return q

    async def unsubscribe(self, tenant_id: str, q: asyncio.Queue) -> None:
        try:
            self._queues[tenant_id].remove(q)
        except ValueError:
            pass

    async def broadcast(self, tenant_id: str, event: dict) -> None:
        for q in list(self._queues.get(tenant_id, [])):
            if not q.full():
                await q.put(event)


event_broadcaster = EventBroadcaster()
