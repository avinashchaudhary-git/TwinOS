from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.db.models import User
from app.schemas.user import SessionUser

router = APIRouter(tags=["Auth"])


@router.post("/auth/session", response_model=SessionUser)
def get_session(current_user: User = Depends(get_current_user)):
    return SessionUser(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        role=current_user.role,
        organization_id=current_user.organization_id,
    )
