import uuid
import enum
from sqlalchemy import String, ForeignKey, Numeric, Enum as SAEnum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel, SoftDeleteMixin


class OrderType(str, enum.Enum):
    DINE_IN = "dine_in"
    TAKEAWAY = "takeaway"


class OrderStatus(str, enum.Enum):
    OPEN = "open"       # dibuat, belum dibayar
    PAID = "paid"       # lunas
    VOID = "void"       # dibatalkan


class PaymentMethod(str, enum.Enum):
    CASH = "cash"
    QRIS = "qris"
    TRANSFER = "transfer"


class Order(BaseModel, SoftDeleteMixin):
    """Transaksi penjualan (bill)."""
    __tablename__ = "orders"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    order_number: Mapped[str] = mapped_column(String(30), nullable=True)  # auto ORD-000001
    order_type: Mapped[OrderType] = mapped_column(SAEnum(OrderType), default=OrderType.DINE_IN, nullable=False)
    table_no: Mapped[str] = mapped_column(String(20), nullable=True)
    status: Mapped[OrderStatus] = mapped_column(SAEnum(OrderStatus), default=OrderStatus.OPEN, nullable=False)
    subtotal: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    total: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    payment_method: Mapped[PaymentMethod] = mapped_column(SAEnum(PaymentMethod), nullable=True)
    paid_amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    change_amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    cashier_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    notes: Mapped[str] = mapped_column(Text, nullable=True)

    items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Order {self.order_number} {self.total}>"


class OrderItem(BaseModel):
    """Baris item dalam order (snapshot nama & harga saat transaksi)."""
    __tablename__ = "order_items"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True
    )
    menu_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("menu_items.id", ondelete="SET NULL"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    quantity: Mapped[int] = mapped_column(Numeric(10, 2), nullable=False, default=1)
    line_total: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    note: Mapped[str] = mapped_column(String(200), nullable=True)

    order: Mapped["Order"] = relationship("Order", back_populates="items")

    def __repr__(self) -> str:
        return f"<OrderItem {self.name} x{self.quantity}>"
