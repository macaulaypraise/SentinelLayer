import json
from typing import Any, cast

import httpx
import structlog

from app.config import settings

from .rules import fast_score

log = structlog.get_logger()


SYSTEM_PROMPT = """
You are SentinelLayer's fraud risk scoring agent for African fintech.
You receive telecom network signals for a mobile money transaction.
Rules:
1. Analyse ALL signals together — never in isolation.
2. Output risk_score: integer 0 (clean) to 100 (definite fraud).
3. Output recommended_action: ALLOW (0-44) | STEP-UP (45-69) | HOLD (70-100).
4. Output signal_drivers: top 3 signal keys driving the score.
5. Output reasoning: one sentence explaining the risk pattern.
Respond ONLY in valid JSON. No preamble. No markdown fences.
"""


async def score_signals(signals: dict[str, Any]) -> dict[str, Any]:
    # Layer 1: rule-based fast path (no API call needed — sub-10ms)
    fast = fast_score(signals)
    if fast:
        log.info("fast_path", trigger=fast.get("trigger"), score=fast["risk_score"])
        return fast

    # Layer 2: Nokia Model as a Service with Gemini via MCP
    payload = {
        "model": "sentinel-fraud-v1",
        "systemPrompt": SYSTEM_PROMPT,
        "userMessage": f"Signals: {json.dumps(signals)}",
        "maxTokens": 256,
        "temperature": 0.1,
    }
    async with httpx.AsyncClient(timeout=8.0) as c:
        r = await c.post(
            settings.nac_maas_endpoint,
            headers={"Authorization": f"Bearer {settings.nac_maas_api_key}"},
            json=payload,
        )
        r.raise_for_status()
    result = cast(dict[str, Any], json.loads(r.json()["content"]))
    log.info("ai_scored", score=result.get("risk_score"), action=result.get("recommended_action"))
    return result
