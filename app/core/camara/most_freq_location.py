from typing import Any


async def get_frequent_location(phone: str) -> dict[str, Any]:
    # Not available on Nokia NaC sandbox — returns safe default
    return {"baseline": "unknown", "latitude": None, "longitude": None}
