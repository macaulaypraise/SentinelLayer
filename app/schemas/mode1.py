# app/schemas/mode1.py
from datetime import date

from pydantic import BaseModel


class Mode1Request(BaseModel):
    phone_number: str
    account_registered_at: date
    name: str
    dob: date
    address: str
    expected_region: str
