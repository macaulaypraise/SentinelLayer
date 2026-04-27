from fastapi import APIRouter

from app.api.v1.endpoints import postmortem, sentinel, stream, webhooks

api_router = APIRouter()
api_router.include_router(sentinel.router)
api_router.include_router(stream.router)
api_router.include_router(postmortem.router)
api_router.include_router(webhooks.router)
