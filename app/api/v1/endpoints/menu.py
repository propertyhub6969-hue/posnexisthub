import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_context, AuthContext, require_owner
from app.models.menu import Category, MenuItem
from app.schemas.menu import (
    CategoryCreate, CategoryResponse, MenuItemCreate, MenuItemUpdate, MenuItemResponse,
)

router = APIRouter()
CNOTDEL = Category.is_deleted == False   # noqa: E712
MNOTDEL = MenuItem.is_deleted == False   # noqa: E712


# ── Categories ──
@router.get("/categories", response_model=list[CategoryResponse])
async def list_categories(ctx: AuthContext = Depends(get_current_context), db: AsyncSession = Depends(get_db)):
    r = await db.execute(
        select(Category).where(Category.tenant_id == ctx.tenant_id, CNOTDEL)
        .order_by(Category.sort_order, Category.name)
    )
    return r.scalars().all()


@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(payload: CategoryCreate, _=Depends(require_owner), ctx: AuthContext = Depends(get_current_context), db: AsyncSession = Depends(get_db)):
    c = Category(tenant_id=ctx.tenant_id, **payload.model_dump())
    db.add(c); await db.flush(); await db.refresh(c)
    return c


@router.delete("/categories/{cid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(cid: uuid.UUID, _=Depends(require_owner), ctx: AuthContext = Depends(get_current_context), db: AsyncSession = Depends(get_db)):
    c = (await db.execute(select(Category).where(Category.id == cid, Category.tenant_id == ctx.tenant_id, CNOTDEL))).scalar_one_or_none()
    if c is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Kategori tidak ditemukan")
    c.is_deleted = True; c.deleted_at = datetime.utcnow()


# ── Menu items ──
async def _to_item_resp(db, ctx, items):
    cats = {c.id: c.name for c in (await db.execute(select(Category).where(Category.tenant_id == ctx.tenant_id))).scalars().all()}
    out = []
    for it in items:
        r = MenuItemResponse.model_validate(it)
        r.category_name = cats.get(it.category_id)
        out.append(r)
    return out


@router.get("/items", response_model=list[MenuItemResponse])
async def list_items(ctx: AuthContext = Depends(get_current_context), db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(MenuItem).where(MenuItem.tenant_id == ctx.tenant_id, MNOTDEL).order_by(MenuItem.name))
    return await _to_item_resp(db, ctx, r.scalars().all())


@router.post("/items", response_model=MenuItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(payload: MenuItemCreate, _=Depends(require_owner), ctx: AuthContext = Depends(get_current_context), db: AsyncSession = Depends(get_db)):
    m = MenuItem(tenant_id=ctx.tenant_id, **payload.model_dump())
    db.add(m); await db.flush(); await db.refresh(m)
    return (await _to_item_resp(db, ctx, [m]))[0]


@router.patch("/items/{mid}", response_model=MenuItemResponse)
async def update_item(mid: uuid.UUID, payload: MenuItemUpdate, _=Depends(require_owner), ctx: AuthContext = Depends(get_current_context), db: AsyncSession = Depends(get_db)):
    m = (await db.execute(select(MenuItem).where(MenuItem.id == mid, MenuItem.tenant_id == ctx.tenant_id, MNOTDEL))).scalar_one_or_none()
    if m is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Menu tidak ditemukan")
    for f, v in payload.model_dump(exclude_unset=True).items():
        setattr(m, f, v)
    await db.flush(); await db.refresh(m)
    return (await _to_item_resp(db, ctx, [m]))[0]


@router.delete("/items/{mid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(mid: uuid.UUID, _=Depends(require_owner), ctx: AuthContext = Depends(get_current_context), db: AsyncSession = Depends(get_db)):
    m = (await db.execute(select(MenuItem).where(MenuItem.id == mid, MenuItem.tenant_id == ctx.tenant_id, MNOTDEL))).scalar_one_or_none()
    if m is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Menu tidak ditemukan")
    m.is_deleted = True; m.deleted_at = datetime.utcnow()
