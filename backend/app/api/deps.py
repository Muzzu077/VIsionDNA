"""
Common FastAPI dependencies.
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user, require_role
from app.db.database import get_db as _get_db
from app.models.models import User


async def get_db() -> AsyncSession:  # type: ignore[misc]
    """Yield an async database session (re-export for convenience)."""
    async for session in _get_db():
        yield session


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Return the current user only if active."""
    return current_user


require_admin = require_role("ADMIN")
require_operator = require_role("ADMIN", "OPERATOR")
require_viewer = require_role("ADMIN", "OPERATOR", "VIEWER")
