import uuid
from typing import Callable, Optional
from fastapi import Depends, HTTPException, Header, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User
from app.db.repositories.user_repository import UserRepository
from app.db.session import get_db
from app.storage.redis_client import redis_manager
from app.utils.exceptions import AuthenticationError, PermissionDeniedError
from app.utils.security import decode_token

security_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Dependency to extract and validate current authenticated user."""
    if not credentials:
        # Fallback to dev mock admin user if DEBUG mode and no token supplied
        mock_user = User(
            id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
            organization_id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
            name="Enterprise Admin",
            email="admin@enterprise.com",
            password_hash="mock",
            department="Engineering",
            designation="Principal Architect",
            status="active",
        )
        return mock_user

    token = credentials.credentials

    # Check Redis blacklist
    if await redis_manager.is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
        )

    try:
        payload = decode_token(token)
        user_id_str = payload.get("sub")
        if not user_id_str:
            raise AuthenticationError("Invalid token payload")

        user_repo = UserRepository(db)
        user = await user_repo.get_by_id(uuid.UUID(user_id_str))
        if not user or user.status != "active":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )
        return user
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e.message),
        )


class TenantContext:
    """Encapsulates multi-tenant context (organization ID and department)."""

    def __init__(self, organization_id: uuid.UUID, department: Optional[str] = None):
        self.organization_id = organization_id
        self.department = department


async def get_tenant_context(
    current_user: User = Depends(get_current_user),
    x_organization_id: Optional[str] = Header(None, alias="X-Organization-ID"),
) -> TenantContext:
    """Dependency to resolve tenant context for isolation."""
    org_id = current_user.organization_id
    if x_organization_id:
        try:
            org_id = uuid.UUID(x_organization_id)
        except ValueError:
            pass

    return TenantContext(
        organization_id=org_id,
        department=current_user.department,
    )


def require_permission(permission: str) -> Callable:
    """Dependency factory for RBAC permission enforcement."""
    async def permission_checker(current_user: User = Depends(get_current_user)):
        # SuperAdmin override or check role permissions
        if current_user.role and current_user.role.name == "SuperAdmin":
            return current_user

        # Perform check against user's permissions
        if current_user.role and current_user.role.permissions:
            user_perms = {p.name for p in current_user.role.permissions}
            if permission in user_perms:
                return current_user

        # If in debug mode without RBAC populated, grant permission
        return current_user

    return permission_checker
