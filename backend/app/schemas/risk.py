from datetime import datetime
from typing import Any

from pydantic import Field

from app.schemas.common import BaseSchema, RiskBandEnum, RiskConfidenceEnum


class RiskScoreRead(BaseSchema):
    id: str
    organization_id: str
    entity_type: str
    entity_id: str
    score: float
    band: RiskBandEnum
    confidence: RiskConfidenceEnum
    top_factors: list[dict[str, Any]] | None = None
    model_version: str
    computed_at: datetime


class ProjectRiskSummary(BaseSchema):
    project_id: str
    project_name: str
    score: float
    band: RiskBandEnum
    confidence: RiskConfidenceEnum
    top_factors: list[str]
    recommendation: str | None = None
    task_count: int = 0
    overdue_task_count: int = 0


class RiskConfigRead(BaseSchema):
    organization_id: str
    medium_threshold: float
    high_threshold: float
    critical_threshold: float
    min_history_days: int
    sync_interval_minutes: int
    updated_at: datetime | None = None


class RiskConfigUpdate(BaseSchema):
    medium_threshold: float | None = Field(None, ge=0.0, le=1.0)
    high_threshold: float | None = Field(None, ge=0.0, le=1.0)
    critical_threshold: float | None = Field(None, ge=0.0, le=1.0)
    min_history_days: int | None = Field(None, ge=1)
    sync_interval_minutes: int | None = Field(None, ge=1)
