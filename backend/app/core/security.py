from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import logger
from app.db.models import User
from app.db.postgres import get_db

bearer_scheme = HTTPBearer(auto_error=False)


def verify_firebase_token(token: str) -> dict | None:
    """Verifies Firebase ID token using firebase-admin SDK if configured."""
    try:
        import firebase_admin
        from firebase_admin import auth

        if not firebase_admin._apps:
            firebase_admin.initialize_app()
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        logger.warning(f"Firebase token verification failed: {e}")
        return None


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Authenticates user via dev bearer token or Firebase ID token."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization credentials were not provided.",
        )

    token = credentials.credentials.strip()

    # Dev mode authentication: "dev:<email>"
    if token.startswith("dev:"):
        if settings.ENV == "production":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Dev authentication token is not permitted in production.",
            )
        email = token.split("dev:", 1)[1].strip().lower()
        user = db.query(User).filter(User.email == email, User.is_active.is_(True)).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Dev user with email '{email}' not found.",
            )
        return user

    # Firebase mode authentication
    if settings.AUTH_MODE == "firebase":
        decoded = verify_firebase_token(token)
        if not decoded:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Firebase ID token."
            )
        firebase_uid = decoded.get("uid")
        email = decoded.get("email", "").lower()
        user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
        if not user and email:
            user = db.query(User).filter(User.email == email).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account does not exist or is inactive.",
            )
        return user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unsupported authentication scheme or invalid token.",
    )
