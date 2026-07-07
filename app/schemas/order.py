import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field
from app.models.order import OrderType, OrderStatus, PaymentMethod


class OrderItemIn(BaseModel):
    menu_item_id: Optional[uuid.UUID] = None
    name: str = Field(..., min_length=1, max_length=150)
    price: Decimal = Field(0, ge=0)
    quantity: Decimal = Field(1, gt=0)
    note: Optional[str] = Field(None, max_length=200)


class OrderCreate(BaseModel):
    order_type: OrderType = OrderType.DINE_IN
    table_no: Optional[str] = Field(None, max_length=20)
    payment_method: PaymentMethod = PaymentMethod.CASH
    paid_amount: Decimal = Field(0, ge=0)
    notes: Optional[str] = None
    items: List[OrderItemIn] = Field(..., min_length=1)


class OrderItemResponse(BaseModel):
    id: uuid.UUID
    menu_item_id: Optional[uuid.UUID] = None
    name: str
    price: Decimal
    quantity: Decimal
    line_total: Decimal
    note: Optional[str] = None

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: uuid.UUID
    order_number: Optional[str] = None
    order_type: OrderType
    table_no: Optional[str] = None
    status: OrderStatus
    subtotal: Decimal
    total: Decimal
    payment_method: Optional[PaymentMethod] = None
    paid_amount: Decimal
    change_amount: Decimal
    cashier_id: Optional[uuid.UUID] = None
    cashier_name: Optional[str] = None
    notes: Optional[str] = None
    items: List[OrderItemResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True
