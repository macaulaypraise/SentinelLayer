# ── Stage 1: Builder ──────────────────────────────────────────
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0 \
    UV_HTTP_TIMEOUT=120

WORKDIR /app

# Deps layer — cached until uv.lock changes
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

COPY app/ ./app/
COPY kafka/ ./kafka/
COPY app/db/migrations/ ./app/db/migrations/
COPY alembic.ini pyproject.toml uv.lock README.md ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable


# ── Stage 2: Runtime ──────────────────────────────────────────
FROM python:3.12-slim-bookworm AS runtime

RUN groupadd --gid 1001 sentinel && \
    useradd --uid 1001 --gid sentinel --create-home sentinel

RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \
    libpq5 curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/app /app/app
COPY --from=builder /app/kafka /app/kafka
COPY --from=builder /app/app/db/migrations /app/app/db/migrations
COPY --from=builder /app/alembic.ini /app/alembic.ini

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

USER sentinel

CMD ["sh", "-c", "alembic upgrade head && gunicorn app.main:app \
    -w 2 -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:$PORT --timeout 60 --graceful-timeout 30"]
