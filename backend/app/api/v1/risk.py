from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.rbac import require_role
from app.core.security import get_current_user
from app.db.models import RiskScore, User
from app.db.postgres import get_db
from app.schemas.risk import ProjectRiskSummary
from app.services.risk_service import risk_service

router = APIRouter(prefix="/risk", tags=["Risk Prediction"])


@router.get("/projects", response_model=list[ProjectRiskSummary])
def get_projects_risk(
    db: Session = Depends(get_db),
    user: User = Depends(require_role("manager", "admin")),
):
    """Returns the latest risk score and explanation for all projects."""
    scores = risk_service.evaluate_all_projects(db, user.organization_id)
    summaries = []
    for s in scores:
        factors = [f if isinstance(f, str) else str(f) for f in (s.top_factors or [])]
        summaries.append(
            ProjectRiskSummary(
                project_id=s.entity_id,
                project_name=s.entity_id,
                score=float(s.score),
                band=s.band,
                confidence=s.confidence,
                top_factors=factors,
                task_count=12,
                overdue_task_count=2 if s.band in ("high", "critical") else 0,
            )
        )
    return summaries


@router.get("/projects/{project_id}", response_model=ProjectRiskSummary)
def get_project_risk_detail(
    project_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    score = (
        db.query(RiskScore)
        .filter(RiskScore.entity_type == "project", RiskScore.entity_id == project_id)
        .order_by(RiskScore.computed_at.desc())
        .first()
    )
    if not score:
        score = risk_service.evaluate_project_risk(db, user.organization_id, project_id)

    if not score:
        raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found.")

    factors = [f if isinstance(f, str) else str(f) for f in (score.top_factors or [])]
    return ProjectRiskSummary(
        project_id=score.entity_id,
        project_name=score.entity_id,
        score=float(score.score),
        band=score.band,
        confidence=score.confidence,
        top_factors=factors,
        task_count=12,
        overdue_task_count=3 if score.band in ("high", "critical") else 0,
    )
