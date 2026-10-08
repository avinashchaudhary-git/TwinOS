from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.rbac import require_role
from app.db.models import User
from app.db.postgres import get_db
from app.schemas.dashboard import DashboardSummaryResponse
from app.services.dashboard_service import dashboard_service

router = APIRouter(prefix="/dashboard", tags=["Executive Dashboard"])


@router.get("/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(
    refresh: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("manager", "admin")),
):
    """Aggregates executive KPIs, risk distributions, workload heatmap, and sync status (cached 30s)."""
    return dashboard_service.get_summary(
        db=db, org_id=current_user.organization_id, force_refresh=refresh
    )
