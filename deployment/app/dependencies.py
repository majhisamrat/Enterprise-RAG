"""
Application-wide FastAPI Dependency Exports
"""

from app.api.dependencies import (
    TenantContext,
    get_current_user,
    get_tenant_context,
    require_permission,
)
from app.db.session import get_db

__all__ = [
    "get_current_user",
    "get_tenant_context",
    "TenantContext",
    "require_permission",
    "get_db",
]
