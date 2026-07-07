import uuid
from pydantic import BaseModel, EmailStr, Field
from app.models.user import UserRole


class RegisterRequest(BaseModel):
    """Daftar outlet baru + akun owner."""
    outlet_name: str = Field(..., min_length=2, max_length=200)
    full_name: str = Field(..., min_length=2, max_length=200)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    email: str
    full_name: str
    role: UserRole
    outlet_name: str | None = None

    class Config:
        from_attributes = True
