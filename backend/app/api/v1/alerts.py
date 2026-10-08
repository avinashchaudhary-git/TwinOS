from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.models import User
from app.db.postgres import get_db
from app.schemas.alert import AlertActionResponse, AlertRead
from app.services.alert_service import alert_service

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("", response_model=list[AlertRead])
def list_user_alerts(
    unread_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    alerts = alert_service.get_user_alerts(db, current_user.id, unread_only=unread_only)
    return alerts


@router.post("/{alert_id}/read", response_model=AlertActionResponse)
def acknowledge_alert(
    alert_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    success = alert_service.mark_as_read(db, alert_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found.")
    return AlertActionResponse(success=True, message="Alert marked as read.")
