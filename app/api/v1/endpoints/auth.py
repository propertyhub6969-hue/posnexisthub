from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.api.deps import get_current_user
from app.models.tenant import Tenant
from app.models.user import User, UserRole
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserResponse

router = APIRouter()


def _token_for(user: User) -> str:
    return create_access_token({"sub": str(user.id), "tenant_id": str(user.tenant_id)})


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    exists = (await db.execute(select(User).where(User.email == payload.email))).scalar_one_or_none()
    if exists:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Email sudah terdaftar")
    tenant = Tenant(name=payload.outlet_name)
    db.add(tenant)
    await db.flush()
    user = User(
        tenant_id=tenant.id, email=payload.email, full_name=payload.full_name,
        hashed_password=get_password_hash(payload.password), role=UserRole.OWNER, is_active=True,
    )
    db.add(user)
    await db.flush()
    return TokenResponse(access_token=_token_for(user))


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = (await db.execute(select(User).where(User.email == payload.email))).scalar_one_or_none()
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Email atau password salah")
    if not user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Akun nonaktif")
    return TokenResponse(access_token=_token_for(user))


@router.get("/me", response_model=UserResponse)
async def me(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    tenant = (await db.execute(select(Tenant).where(Tenant.id == user.tenant_id))).scalar_one_or_none()
    resp = UserResponse.model_validate(user)
    resp.outlet_name = tenant.name if tenant else None
    return resp
