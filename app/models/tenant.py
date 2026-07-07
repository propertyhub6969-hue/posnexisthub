from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel, SoftDeleteMixin


class Tenant(BaseModel, SoftDeleteMixin):
    """Satu outlet/merchant F&B."""
    __tablename__ = "tenants"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    address: Mapped[str] = mapped_column(String(300), nullable=True)
    phone: Mapped[str] = mapped_column(String(30), nullable=True)

    def __repr__(self) -> str:
        return f"<Tenant {self.name}>"
