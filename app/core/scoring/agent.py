import json
from typing import Any, cast

import httpx
import structlog

from app.config import settings

from .rules import fast_score
from .weights import SIGNAL_WEIGHTS, THRESHOLD_HOLD, THRESHOLD_MODE2

log = structlog.get_logger()

# 1. SAFE IMPORT & TOOL DEFINITION
try:
    from google import genai
    from google.genai import types

    HAS_GENAI = True

    # Define tools ONLY if imports succeed to avoid NameError
    check_device_roaming_func = types.FunctionDeclaration(
        name="check_device_roaming",
        description="Query live roaming status from Nokia NaC to verify location truth.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "phone_number": types.Schema(
                    type=types.Type.STRING, description="Phone number in E.164 format"
                )
            },
            required=["phone_number"],
        ),
    )
    nokia_mcp_tools = types.Tool(function_declarations=[check_device_roaming_func])

except ImportError:
    HAS_GENAI = False
    nokia_mcp_tools = None  # type: ignore[assignment]
    log.error("gemini_sdk_missing_ai_disabled")

# 2. SYSTEM PROMPT
SYSTEM_PROMPT = """... (keep your existing prompt) ..."""


# 3. HELPER FUNCTIONS
async def execute_roaming_check(phone_number: str) -> dict[str, Any]:
    """Live retrieval via Nokia RapidAPI."""
    payload = {"device": {"phoneNumber": phone_number}}
    try:
        async with httpx.AsyncClient(timeout=8.0) as c:
            r = await c.post(
                f"{settings.nac_base_url}/device-status/device-roaming-status/v1/retrieve",
                headers={
                    "X-RapidAPI-Key": settings.nac_rapidapi_key,
                    "X-RapidAPI-Host": settings.nac_rapidapi_host,
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            r.raise_for_status()
            return cast(dict[str, Any], r.json())
    except Exception as e:
        log.error("mcp_tool_execution_failed", error=str(e))
        return {"error": "Nokia API unreachable", "details": str(e)}


def _weighted_score(signals: dict[str, bool]) -> dict[str, Any]:
    """Deterministic fallback using SIGNAL_WEIGHTS[cite: 4]."""
    raw = sum(SIGNAL_WEIGHTS.get(k, 0) for k, v in signals.items() if v)
    max_possible = sum(SIGNAL_WEIGHTS.values())
    score = min(100, int((raw / max_possible) * 100)) if max_possible else 0

    action = (
        "HOLD" if score >= THRESHOLD_HOLD else ("STEP-UP" if score >= THRESHOLD_MODE2 else "ALLOW")
    )
    drivers = sorted(
        [k for k, v in signals.items() if v], key=lambda k: SIGNAL_WEIGHTS.get(k, 0), reverse=True
    )[:3]

    return {
        "risk_score": score,
        "recommended_action": action,
        "signal_drivers": drivers,
        "reasoning": "Weighted signal scoring (Fail-safe Fallback).",
        "fast_path": False,
    }


# 4. MAIN SCORING LOGIC
async def score_signals(
    signals: dict[str, Any], phone_number: str = "+2348011111111"
) -> dict[str, Any]:
    fast = fast_score(signals)
    if fast:
        return fast

    if not HAS_GENAI or not getattr(settings, "gemini_api_key", None):
        return _weighted_score(signals)

    try:
        client = genai.Client(api_key=settings.gemini_api_key)
        chat = client.aio.chats.create(
            model="gemini-2.5-pro",
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                tools=[nokia_mcp_tools],
                temperature=0.1,
                response_mime_type="application/json",
            ),
        )

        user_msg = f"Score signals for {phone_number}: {json.dumps(signals)}"
        response = await chat.send_message(user_msg)

        if response.function_calls:
            for tool_call in response.function_calls:
                if tool_call.name == "check_device_roaming":
                    args = tool_call.args or {}
                    roam_phone = str(args.get("phone_number", phone_number))
                    tool_result = await execute_roaming_check(roam_phone)
                    response = await chat.send_message(
                        types.Part.from_function_response(
                            name=tool_call.name, response={"result": tool_result}
                        )
                    )

        text_content = response.text or "{}"
        try:
            result = cast(dict[str, Any], json.loads(text_content.strip()))
            return result
        except json.JSONDecodeError:
            return _weighted_score(signals)

    except Exception as exc:
        log.warning("ai_agent_failed_falling_back", error=str(exc))
        return _weighted_score(signals)
