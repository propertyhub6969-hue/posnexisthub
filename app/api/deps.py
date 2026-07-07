import uuid
from dataclasses import dataclass
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User, UserRole

security = HTTPBearer()


@dataclass
class AuthContext:
    user_id: uuid.UUID
    tenant_id: uuid.UUID


async def get_current_context(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> AuthContext:
    exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_token(credentials.credentials)
    if payload is None or payload.get("type") != "access":
        raise exc
    user_id = payload.get("sub")
    tenant_id = payload.get("tenant_id")
    if user_id is None or tenant_id is None:
        raise exc
    try:
        return AuthContext(user_id=uuid.UUID(user_id), tenant_id=uuid.UUID(tenant_id))
    except (ValueError, TypeError):
        raise exc


async def get_current_user(
    ctx: AuthContext = Depends(get_current_context),
    db: AsyncSession = Depends(get_db),
) -> User:
    user = (await db.execute(select(User).where(User.id == ctx.user_id))).scalar_one_or_none()
    if user is None or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="User tidak aktif")
    return user


def require_owner(user: User = Depends(get_current_user)) -> User:
    if user.role != UserRole.OWNER:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Hanya owner yang boleh")
    return user
