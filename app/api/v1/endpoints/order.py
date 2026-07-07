import uuid
from datetime import datetime, date, timezone, timedelta
from decimal import Decimal
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_context, AuthContext
from app.models.user import User
from app.models.order import Order, OrderItem, OrderStatus, PaymentMethod
from app.schemas.order import OrderCreate, OrderResponse

router = APIRouter()
ONOTDEL = Order.is_deleted == False  # noqa: E712
WITA = timezone(timedelta(hours=8))  # Asia/Makassar


async def _gen_number(db, tenant_id) -> str:
    n = await db.scalar(select(func.count()).select_from(Order).where(Order.tenant_id == tenant_id))
    return f"ORD-{(n or 0) + 1:06d}"


async def _load(db, tenant_id, oid) -> Order:
    o = (await db.execute(
        select(Order).options(selectinload(Order.items))
        .where(Order.id == oid, Order.tenant_id == tenant_id, ONOTDEL)
    )).scalar_one_or_none()
    if o is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Order tidak ditemukan")
    return o


async def _to_resp(db, tenant_id, orders):
    uids = list({o.cashier_id for o in orders if o.cashier_id})
    names = {}
    if uids:
        rows = (await db.execute(select(User.id, User.full_name).where(User.id.in_(uids)))).all()
        names = {r[0]: r[1] for r in rows}
    out = []
    for o in orders:
        r = OrderResponse.model_validate(o)
        r.cashier_name = names.get(o.cashier_id)
        out.append(r)
    return out


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(payload: OrderCreate, ctx: AuthContext = Depends(get_current_context), db: AsyncSession = Depends(get_db)):
    subtotal = Decimal(0)
    order = Order(
        tenant_id=ctx.tenant_id, order_number=await _gen_number(db, ctx.tenant_id),
        order_type=payload.order_type, table_no=payload.table_no,
        payment_method=payload.payment_method, cashier_id=ctx.user_id, notes=payload.notes,
    )
    for it in payload.items:
        line = Decimal(it.price or 0) * Decimal(it.quantity or 0)
        subtotal += line
        order.items.append(OrderItem(
            tenant_id=ctx.tenant_id, menu_item_id=it.menu_item_id, name=it.name,
            price=it.price or 0, quantity=it.quantity or 0, line_total=line, note=it.note,
        ))
    order.subtotal = subtotal
    order.total = subtotal
    paid = Decimal(payload.paid_amount or 0)
    # tunai: butuh cukup bayar; non-tunai: anggap pas
    if payload.payment_method == PaymentMethod.CASH:
        if paid < subtotal:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Nominal bayar kurang dari total")
        order.paid_amount = paid
        order.change_amount = paid - subtotal
    else:
        order.paid_amount = subtotal
        order.change_amount = Decimal(0)
    order.status = OrderStatus.PAID
    db.add(order); await db.flush()
    o = await _load(db, ctx.tenant_id, order.id)
    return (await _to_resp(db, ctx.tenant_id, [o]))[0]


@router.get("", response_model=list[OrderResponse])
async def list_orders(
    today: bool = Query(False), ctx: AuthContext = Depends(get_current_context), db: AsyncSession = Depends(get_db),
):
    conds = [Order.tenant_id == ctx.tenant_id, ONOTDEL]
    if today:
        start = datetime.now(WITA).replace(hour=0, minute=0, second=0, microsecond=0)
        conds.append(Order.created_at >= start)
    r = await db.execute(
        select(Order).options(selectinload(Order.items)).where(*conds).order_by(Order.created_at.desc())
    )
    return await _to_resp(db, ctx.tenant_id, r.scalars().all())


@router.get("/{oid}", response_model=OrderResponse)
async def get_order(oid: uuid.UUID, ctx: AuthContext = Depends(get_current_context), db: AsyncSession = Depends(get_db)):
    o = await _load(db, ctx.tenant_id, oid)
    return (await _to_resp(db, ctx.tenant_id, [o]))[0]


@router.delete("/{oid}", status_code=status.HTTP_204_NO_CONTENT)
async def void_order(oid: uuid.UUID, ctx: AuthContext = Depends(get_current_context), db: AsyncSession = Depends(get_db)):
    o = await _load(db, ctx.tenant_id, oid)
    o.status = OrderStatus.VOID
    o.is_deleted = True
    o.deleted_at = datetime.utcnow()
