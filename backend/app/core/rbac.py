from collections.abc import Callable

from fastapi import Depends, HTTPException, status

from app.core.security import get_current_user
from app.db.models import User
from app.schemas.common import RoleEnum


def require_role(*allowed_roles: str) -> Callable[[User], User]:
    """Dependency that enforces role-based access control.
    Returns 403 Forbidden if current user role is not in allowed_roles.
    """

    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        user_role = current_user.role
        # Check direct match or enum values
        allowed_set = {r.value if isinstance(r, RoleEnum) else str(r) for r in allowed_roles}
        if user_role not in allowed_set:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden: role '{user_role}' lacks required permissions ({', '.join(allowed_set)}).",
            )
        return current_user

    return role_checker
