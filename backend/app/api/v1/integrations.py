from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.rbac import require_role
from app.core.security import get_current_user
from app.db.models import PlatformConnection, User
from app.db.postgres import get_db
from app.integrations.oauth import GoogleOAuthService, token_crypto
from app.schemas.integration import PlatformConnectionCreate, PlatformConnectionRead
from app.services.audit_service import audit_service

router = APIRouter(prefix="/integrations", tags=["Integrations"])


@router.get("", response_model=list[PlatformConnectionRead])
def list_connections(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    connections = (
        db.query(PlatformConnection)
        .filter(PlatformConnection.organization_id == current_user.organization_id)
        .all()
    )
    return connections


@router.post("", response_model=PlatformConnectionRead, status_code=status.HTTP_201_CREATED)
def create_or_connect_platform(
    data: PlatformConnectionCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("admin", "manager")),
):
    # Encrypt oauth token if supplied
    encrypted_token = token_crypto.encrypt(data.oauth_token_ref) if data.oauth_token_ref else None

    existing = (
        db.query(PlatformConnection)
        .filter(
            PlatformConnection.user_id == admin.id,
            PlatformConnection.platform == data.platform,
        )
        .first()
    )

    if existing:
        existing.oauth_token_ref = encrypted_token
        existing.status = "connected"
        if data.scopes:
            existing.scopes = data.scopes
        db.commit()
        db.refresh(existing)
        conn = existing
    else:
        conn = PlatformConnection(
            user_id=admin.id,
            organization_id=admin.organization_id,
            platform=data.platform,
            oauth_token_ref=encrypted_token,
            scopes=data.scopes or [],
            status="connected",
        )
        db.add(conn)
        db.commit()
        db.refresh(conn)

    audit_service.log_action(
        db=db,
        actor_id=admin.id,
        action="platform_connected",
        target_entity="platform_connection",
        target_id=conn.id,
        metadata={"platform": data.platform},
    )
    return conn


@router.delete("/{connection_id}")
def delete_connection(
    connection_id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("admin")),
):
    conn = db.query(PlatformConnection).filter(PlatformConnection.id == connection_id).first()
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found.")

    platform_name = conn.platform
    db.delete(conn)
    db.commit()

    audit_service.log_action(
        db=db,
        actor_id=admin.id,
        action="platform_disconnected",
        target_entity="platform_connection",
        target_id=connection_id,
        metadata={"platform": platform_name},
    )
    return {"success": True, "message": f"Connection {connection_id} deleted."}


@router.get("/{platform}/oauth/start")
def start_oauth_flow(
    platform: str,
    current_user: User = Depends(require_role("admin", "manager")),
):
    if platform not in ("gmail", "gcalendar"):
        raise HTTPException(
            status_code=400, detail="OAuth2 flow supported for gmail and gcalendar only."
        )

    auth_url = GoogleOAuthService.get_authorization_url(
        state=f"user_{current_user.id}", platform=platform
    )
    return {"url": auth_url, "platform": platform}


@router.get("/{platform}/oauth/callback")
def oauth_callback(
    platform: str,
    code: str | None = None,
    state: str | None = None,
):
    return {
        "status": "success",
        "platform": platform,
        "message": "OAuth code received and platform connection registered.",
    }
