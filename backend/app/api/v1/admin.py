from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.rbac import require_role
from app.db.models import AuditLog, User
from app.db.postgres import get_db
from app.schemas.risk import RiskConfigRead, RiskConfigUpdate
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.services.audit_service import audit_service
from app.services.risk_service import risk_service

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/users", response_model=list[UserRead])
def list_users(
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("admin")),
):
    users = db.query(User).filter(User.organization_id == admin.organization_id).all()
    return users


@router.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("admin")),
):
    existing = db.query(User).filter(User.email == data.email.lower()).first()
    if existing:
        raise HTTPException(status_code=400, detail="User with this email already exists.")

    new_user = User(
        name=data.name,
        email=data.email.lower(),
        role=data.role,
        organization_id=admin.organization_id,
        firebase_uid=data.firebase_uid,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    audit_service.log_action(
        db=db,
        actor_id=admin.id,
        action="user_created",
        target_entity="user",
        target_id=new_user.id,
        metadata={"email": new_user.email, "role": new_user.role},
    )
    return new_user


@router.patch("/users/{user_id}", response_model=UserRead)
def update_user(
    user_id: str,
    data: UserUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("admin")),
):
    user = (
        db.query(User)
        .filter(User.id == user_id, User.organization_id == admin.organization_id)
        .first()
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    if data.name is not None:
        user.name = data.name
    if data.role is not None:
        user.role = data.role
    if data.is_active is not None:
        user.is_active = data.is_active

    db.commit()
    db.refresh(user)

    audit_service.log_action(
        db=db,
        actor_id=admin.id,
        action="user_updated",
        target_entity="user",
        target_id=user.id,
        metadata={"changes": data.model_dump(exclude_unset=True)},
    )
    return user


@router.get("/risk-config", response_model=RiskConfigRead)
def get_risk_config(
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("admin", "manager")),
):
    config = risk_service.get_or_create_config(db, admin.organization_id)
    return RiskConfigRead(
        organization_id=config.organization_id,
        medium_threshold=float(config.medium_threshold or 0.35),
        high_threshold=float(config.high_threshold or 0.60),
        critical_threshold=float(config.critical_threshold or 0.80),
        min_history_days=int(config.min_history_days or 14),
        sync_interval_minutes=int(config.sync_interval_minutes or 15),
        updated_at=config.updated_at,
    )


@router.put("/risk-config", response_model=RiskConfigRead)
def update_risk_config(
    data: RiskConfigUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("admin")),
):
    config = risk_service.get_or_create_config(db, admin.organization_id)
    if data.medium_threshold is not None:
        config.medium_threshold = data.medium_threshold
    if data.high_threshold is not None:
        config.high_threshold = data.high_threshold
    if data.critical_threshold is not None:
        config.critical_threshold = data.critical_threshold
    if data.min_history_days is not None:
        config.min_history_days = data.min_history_days
    if data.sync_interval_minutes is not None:
        config.sync_interval_minutes = data.sync_interval_minutes

    config.updated_by = admin.id
    db.commit()
    db.refresh(config)

    audit_service.log_action(
        db=db,
        actor_id=admin.id,
        action="risk_config_updated",
        target_entity="risk_config",
        target_id=config.organization_id,
        metadata=data.model_dump(exclude_unset=True),
    )

    return RiskConfigRead(
        organization_id=config.organization_id,
        medium_threshold=float(config.medium_threshold),
        high_threshold=float(config.high_threshold),
        critical_threshold=float(config.critical_threshold),
        min_history_days=int(config.min_history_days),
        sync_interval_minutes=int(config.sync_interval_minutes),
        updated_at=config.updated_at,
    )


@router.get("/audit")
def list_audit_logs(
    limit: int = 50,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("admin")),
):
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit).all()
    return [
        {
            "id": log_entry.id,
            "actor_id": log_entry.actor_id,
            "action": log_entry.action,
            "target_entity": log_entry.target_entity,
            "target_id": log_entry.target_id,
            "metadata": log_entry.metadata_json,
            "timestamp": log_entry.timestamp.isoformat() if log_entry.timestamp else None,
        }
        for log_entry in logs
    ]
