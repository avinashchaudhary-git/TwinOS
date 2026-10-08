from datetime import datetime
from typing import Any

from app.schemas.common import BaseSchema
from app.schemas.risk import ProjectRiskSummary


class RiskBandCounts(BaseSchema):
    low: int = 0
    medium: int = 0
    high: int = 0
    critical: int = 0


class WorkloadEmployee(BaseSchema):
    employee_id: str
    name: str
    email: str
    active_tasks: int
    overdue_tasks: int
    completed_tasks: int
    workload_score: float  # 0.0 to 1.0


class OverdueTaskItem(BaseSchema):
    id: str
    title: str
    project_id: str
    project_name: str
    assignee_name: str
    due_date: str | None = None
    days_overdue: int


class SyncHealthStatus(BaseSchema):
    platform: str
    status: str
    last_synced_at: datetime | None = None
    records_synced: int = 0


class DashboardSummaryResponse(BaseSchema):
    total_projects: int
    total_employees: int
    total_tasks: int
    risk_distribution: RiskBandCounts
    top_at_risk_projects: list[ProjectRiskSummary]
    overdue_tasks: list[OverdueTaskItem]
    workload_heatmap: list[WorkloadEmployee]
    recent_alerts: list[dict[str, Any]]
    sync_health: list[SyncHealthStatus]
