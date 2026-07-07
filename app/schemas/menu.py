import uuid
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field


# ── Category ──
class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    sort_order: int = 0


class CategoryResponse(BaseModel):
    id: uuid.UUID
    name: str
    sort_order: int

    class Config:
        from_attributes = True


# ── Menu Item ──
class MenuItemCreate(BaseModel):
    category_id: Optional[uuid.UUID] = None
    name: str = Field(..., min_length=1, max_length=150)
    price: Decimal = Field(0, ge=0)
    is_available: bool = True


class MenuItemUpdate(BaseModel):
    category_id: Optional[uuid.UUID] = None
    name: Optional[str] = Field(None, min_length=1, max_length=150)
    price: Optional[Decimal] = Field(None, ge=0)
    is_available: Optional[bool] = None


class MenuItemResponse(BaseModel):
    id: uuid.UUID
    category_id: Optional[uuid.UUID] = None
    category_name: Optional[str] = None
    name: str
    price: Decimal
    is_available: bool

    class Config:
        from_attributes = True
