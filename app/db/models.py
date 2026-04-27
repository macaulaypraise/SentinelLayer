import uuid
from datetime import UTC, datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


def now_utc() -> datetime:
    return datetime.now(UTC)


class Tenant(Base):
    __tablename__ = "tenants"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    tier: Mapped[str] = mapped_column(String(20), nullable=False, default="DEVELOPER")
    country: Mapped[str] = mapped_column(String(10), nullable=False, default="NG")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)


class APIKey(Base):
    __tablename__ = "api_keys"
    __table_args__ = (Index("idx_api_keys_hash", "key_hash", postgresql_where="is_active = TRUE"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"))
    key_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    key_prefix: Mapped[str] = mapped_column(String(12), nullable=False)
    label: Mapped[str | None] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class Account(Base):
    __tablename__ = "accounts"
    __table_args__ = (
        UniqueConstraint("tenant_id", "account_id"),
        UniqueConstraint("tenant_id", "phone_number"),
        Index("idx_accounts_phone", "tenant_id", "phone_number"),
    )
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"))
    account_id: Mapped[str] = mapped_column(String(128), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    registered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    baseline_region: Mapped[str | None] = mapped_column(String(100))
    consent_granted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    consent_updated: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    is_flagged: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    flag_reason: Mapped[str | None] = mapped_column(Text)


class Session(Base):
    __tablename__ = "sessions"
    __table_args__ = (
        CheckConstraint("risk_score BETWEEN 0 AND 100"),
        CheckConstraint("recommended_action IN ('ALLOW','STEP-UP','HOLD')"),
        CheckConstraint("mode_triggered IN (1,2,3)"),
        Index("idx_sessions_tenant_created", "tenant_id", "created_at"),
        Index("idx_sessions_phone", "tenant_id", "phone_number"),
    )
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"))
    account_id: Mapped[str | None] = mapped_column(String(128))
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    transaction_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
    risk_score: Mapped[int] = mapped_column(Integer, nullable=False)
    recommended_action: Mapped[str] = mapped_column(String(10), nullable=False)
    mode_triggered: Mapped[int] = mapped_column(Integer, nullable=False)
    signals: Mapped[dict] = mapped_column(JSONB, nullable=False)
    signal_drivers: Mapped[dict | None] = mapped_column(JSONB)
    fast_path: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    resolution: Mapped[str | None] = mapped_column(String(20))


class ConsentRecord(Base):
    __tablename__ = "consent_records"
    __table_args__ = (
        Index("idx_consent_tenant", "tenant_id"),
        Index("idx_consent_session", "session_id"),
    )
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"))
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sessions.id"))
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    consent_status: Mapped[str] = mapped_column(String(20), nullable=False)
    authorised_by: Mapped[str] = mapped_column(String(50), nullable=False)
    authorised_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    location_retrieved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    raw_consent_response: Mapped[dict | None] = mapped_column(JSONB)


class Incident(Base):
    __tablename__ = "incidents"
    __table_args__ = (Index("idx_incidents_tenant", "tenant_id"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"))
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sessions.id"))
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    incident_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    incident_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    visit_locations: Mapped[dict | None] = mapped_column(JSONB)
    home_zone: Mapped[dict | None] = mapped_column(JSONB)
    maps_url: Mapped[str | None] = mapped_column(Text)
    evidence_notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class RecommendedAction(str, Enum):
    ALLOW = "ALLOW"
    STEP_UP = "STEP-UP"
    HOLD = "HOLD"


class ConsentStatus(str, Enum):
    GRANTED = "GRANTED"
    DENIED = "DENIED"
    PENDING = "PENDING"
