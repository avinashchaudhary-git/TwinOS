import uuid
from datetime import UTC, datetime

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.db.postgres import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(UTC)


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    platform_connections = relationship("PlatformConnection", back_populates="organization")


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(Text, nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    role = Column(
        String(20),
        CheckConstraint("role IN ('manager', 'employee', 'admin')", name="check_user_role"),
        nullable=False,
        default="employee",
    )
    firebase_uid = Column(String(255), unique=True, nullable=True, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    organization = relationship("Organization", back_populates="users")
    aliases = relationship("EmployeeAlias", back_populates="user", cascade="all, delete-orphan")
    connections = relationship(
        "PlatformConnection", back_populates="user", cascade="all, delete-orphan"
    )
    alerts = relationship("Alert", back_populates="recipient", cascade="all, delete-orphan")


class EmployeeAlias(Base):
    __tablename__ = "employee_aliases"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    platform = Column(String(50), nullable=False)
    external_id = Column(String(255), nullable=False)

    user = relationship("User", back_populates="aliases")

    __table_args__ = (UniqueConstraint("platform", "external_id", name="uq_platform_external_id"),)


class PlatformConnection(Base):
    __tablename__ = "platform_connections"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    organization_id = Column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    platform = Column(
        String(50),
        CheckConstraint(
            "platform IN ('github', 'trello', 'gmail', 'gcalendar')", name="check_platform_name"
        ),
        nullable=False,
    )
    oauth_token_ref = Column(Text, nullable=True)  # Fernet encrypted ciphertext
    scopes = Column(JSON, nullable=True, default=list)  # list of scope strings
    status = Column(String(50), default="connected")
    last_synced_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="connections")
    organization = relationship("Organization", back_populates="platform_connections")
    sync_runs = relationship("SyncRun", back_populates="connection", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("user_id", "platform", name="uq_user_platform"),)


class SyncRun(Base):
    __tablename__ = "sync_runs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    connection_id = Column(
        String(36), ForeignKey("platform_connections.id", ondelete="CASCADE"), nullable=False
    )
    started_at = Column(DateTime(timezone=True), default=utc_now)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(50), default="running")  # running, success, failed, rate_limited
    records_pulled = Column(Integer, default=0)
    error = Column(Text, nullable=True)

    connection = relationship("PlatformConnection", back_populates="sync_runs")


class StagingRecord(Base):
    __tablename__ = "staging_records"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), nullable=False, index=True)
    platform = Column(String(50), nullable=False)
    entity_type = Column(String(50), nullable=False)
    external_id = Column(String(255), nullable=False)
    payload = Column(JSON, nullable=False)
    content_hash = Column(String(64), nullable=False)
    status = Column(
        String(20),
        CheckConstraint("status IN ('pending', 'ingested', 'failed')", name="check_staging_status"),
        default="pending",
    )
    created_at = Column(DateTime(timezone=True), default=utc_now)

    __table_args__ = (
        UniqueConstraint(
            "platform", "entity_type", "external_id", "content_hash", name="uq_staging_record"
        ),
        Index("idx_staging_status", "status"),
    )


class RiskScore(Base):
    __tablename__ = "risk_scores"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), nullable=False, index=True)
    entity_type = Column(
        String(20),
        CheckConstraint("entity_type IN ('project', 'task')", name="check_risk_entity_type"),
        nullable=False,
    )
    entity_id = Column(String(255), nullable=False, index=True)
    score = Column(Numeric(4, 3), nullable=False)
    band = Column(
        String(20),
        CheckConstraint("band IN ('low', 'medium', 'high', 'critical')", name="check_risk_band"),
        nullable=False,
    )
    confidence = Column(
        String(20),
        CheckConstraint("confidence IN ('normal', 'low')", name="check_risk_confidence"),
        default="normal",
    )
    top_factors = Column(JSON, nullable=True)  # list of top factor explanations
    model_version = Column(String(50), default="1.0.0")
    computed_at = Column(DateTime(timezone=True), default=utc_now)

    __table_args__ = (Index("idx_risk_entity_time", "entity_type", "entity_id", "computed_at"),)


class RiskConfig(Base):
    __tablename__ = "risk_config"

    organization_id = Column(String(36), primary_key=True)
    medium_threshold = Column(Numeric(4, 3), default=0.35)
    high_threshold = Column(Numeric(4, 3), default=0.60)
    critical_threshold = Column(Numeric(4, 3), default=0.80)
    min_history_days = Column(Integer, default=14)
    sync_interval_minutes = Column(Integer, default=15)
    updated_by = Column(String(36), nullable=True)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), nullable=False, index=True)
    recipient_user_id = Column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String(255), nullable=False)
    from_band = Column(String(20), nullable=True)
    to_band = Column(String(20), nullable=False)
    message = Column(Text, nullable=False)
    recommendation = Column(Text, nullable=True)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    recipient = relationship("User", back_populates="alerts")


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    actor_id = Column(String(36), nullable=True, index=True)
    action = Column(String(100), nullable=False)
    target_entity = Column(String(100), nullable=True)
    target_id = Column(String(255), nullable=True)
    metadata_json = Column("metadata", JSON, nullable=True)
    timestamp = Column(DateTime(timezone=True), default=utc_now)
