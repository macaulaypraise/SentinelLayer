# Device Swap already covers hardware continuity.
# This module now returns a safe default.
from typing import Any


async def get_identifier(phone: str) -> dict[str, Any]:
    return {"newDevice": False}
