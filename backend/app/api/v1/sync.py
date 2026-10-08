from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.rbac import require_role
from app.db.models import PlatformConnection, SyncRun, User
from app.db.postgres import get_db
from app.schemas.integration import SyncRunRead
from app.services.audit_service import audit_service
from app.services.ingestion_service import ingestion_service
from app.services.risk_service import risk_service
from app.services.sync_service import sync_service

router = APIRouter(prefix="/sync", tags=["Sync"])


@router.post("/run")
def trigger_sync(
    use_mock: bool = True,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("manager", "admin")),
):
    """Triggers end-to-end sync across platforms, ingests to graph/vector, and updates risk models."""
    # Ensure platform connections exist for org
    existing_conns = (
        db.query(PlatformConnection)
        .filter(PlatformConnection.organization_id == user.organization_id)
        .all()
    )
    if not existing_conns:
        # Seed default mock connections for demo
        for plat in ("github", "trello", "gmail", "gcalendar"):
            conn = PlatformConnection(
                user_id=user.id,
                organization_id=user.organization_id,
                platform=plat,
                status="connected",
            )
            db.add(conn)
        db.commit()

    # Step 1: Run connectors and stage records
    staged = sync_service.run_all_syncs(db, org_id=user.organization_id, use_mock=use_mock)

    # Step 2: Ingest staging records into Knowledge Graph & Chroma
    ingested = ingestion_service.ingest_pending_records(db)

    # Step 3: Recompute risk scores and check alerts
    scores = risk_service.evaluate_all_projects(db, org_id=user.organization_id)

    audit_service.log_action(
        db=db,
        actor_id=user.id,
        action="manual_sync_triggered",
        target_entity="sync_pipeline",
        target_id=user.organization_id,
        metadata={"staged": staged, "ingested": ingested, "projects_scored": len(scores)},
    )

    return {
        "status": "success",
        "records_staged": staged,
        "records_ingested": ingested,
        "projects_evaluated": len(scores),
        "message": f"Sync pipeline completed: {staged} staged, {ingested} ingested, {len(scores)} projects scored.",
    }


@router.get("/runs", response_model=list[SyncRunRead])
def list_sync_runs(
    db: Session = Depends(get_db),
    user: User = Depends(require_role("manager", "admin")),
):
    runs = db.query(SyncRun).order_by(SyncRun.started_at.desc()).limit(20).all()
    return runs
