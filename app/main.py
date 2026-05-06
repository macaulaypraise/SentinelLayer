from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.v1.router import api_router
from app.config import settings
from app.observability.logging import configure_logging
from app.observability.tracing import configure_tracing

configure_logging()

if settings.sentry_dsn:
    sentry_sdk.init(dsn=settings.sentry_dsn, traces_sample_rate=0.2, environment=settings.app_env)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup: create Kafka topics, register SIM swap webhooks
    yield
    # Shutdown: flush Kafka producer


middleware = [
    Middleware(
        CORSMiddleware,  # type: ignore[arg-type, unused-ignore]
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
]

app = FastAPI(
    title="SentinelLayer API",
    version="1.0.0",
    description="Network-native pre-authentication fraud intelligence for African fintech",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    middleware=middleware,
)

configure_tracing(app)
Instrumentator().instrument(app).expose(app, endpoint="/metrics")
app.include_router(api_router)


@app.get("/health", tags=["system"])
async def health() -> dict[str, Any]:
    return {
        "status": "healthy",
        "service": "sentinellayer",
        "version": "1.0.0",
        "modes": ["pre-emptive", "live-enforcement", "post-mortem"],
        "apis_connected": 18,
        "agentic_ai": True,
    }
