from typing import Any

from pydantic import BaseModel


class Mode2Result(BaseModel):
    mode_triggered: int
    outcome: str
    location: dict | None = None
    consent_record_id: str | None = None
    alerted_parties: list[str] = []
    consent_status: str | None = None
    location_retrieved: bool = False


class SentinelCheckResponse(BaseModel):
    session_id: str
    risk_score: int
    recommended_action: str
    mode_triggered: int
    signals: dict[str, Any]
    signal_drivers: list[str] = []
    fast_path: bool = False
    duration_ms: float | None = None
    mode2: Mode2Result | None = None


class PostmortemResponse(BaseModel):
    mode_triggered: int
    maps_evidence_url: str
    locations_visited: int
    home_zone: dict | None = None
    incident_id: str
