import uuid
from sqlalchemy import String, ForeignKey, Numeric, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel, SoftDeleteMixin


class Category(BaseModel, SoftDeleteMixin):
    """Kategori menu (mis. Makanan, Minuman, Kopi)."""
    __tablename__ = "categories"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    def __repr__(self) -> str:
        return f"<Category {self.name}>"


class MenuItem(BaseModel, SoftDeleteMixin):
    """Item menu yang dijual."""
    __tablename__ = "menu_items"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<MenuItem {self.name} {self.price}>"
