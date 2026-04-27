from fastapi import APIRouter, Request

from app.workers.sim_swap_listener import handle_sim_swap_webhook

router = APIRouter(prefix="/v1/webhooks", tags=["webhooks"])


@router.post("/sim-swap")
async def sim_swap_webhook(request: Request) -> dict:
    payload = await request.json()
    handle_sim_swap_webhook.delay(payload)  # offload to Celery immediately
    return {"status": "received"}  # 200 back to Nokia NaC without delay
