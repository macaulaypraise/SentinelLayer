from datetime import date

from pydantic import BaseModel, Field


class SentinelCheckRequest(BaseModel):
    phone_number: str = Field(..., description="E.164 format e.g. +2348012345678")
    account_id: str = Field(..., description="Fintech internal account ID")
    transaction_amount: float | None = Field(None, ge=0)
    expected_region: str = Field(..., description="Subscriber expected region e.g. Lagos")
    name: str = Field(..., description="Full name as registered with fintech")
    dob: date = Field(..., description="Date of birth")
    address: str = Field(..., description="Registered address first line")
    account_registered_at: date = Field(..., description="Date account was registered")


class PostmortemRequest(BaseModel):
    session_id: str
    phone_number: str
    incident_start: str = Field(..., description="ISO 8601 datetime")
    incident_end: str = Field(..., description="ISO 8601 datetime")
