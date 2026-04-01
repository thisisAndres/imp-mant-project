import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Computed, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    supplier_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("suppliers.id"), nullable=True
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    status: Mapped[str] = mapped_column(String(30), server_default="pending")
    total_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), server_default="0")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    ordered_at: Mapped[datetime] = mapped_column(server_default=func.now())
    received_at: Mapped[datetime | None] = mapped_column(nullable=True)

    supplier: Mapped["Supplier"] = relationship(back_populates="purchase_orders")  # noqa: F821
    user: Mapped["User"] = relationship(back_populates="purchase_orders")  # noqa: F821
    details: Mapped[list["PurchaseOrderDetail"]] = relationship(
        back_populates="purchase_order", cascade="all, delete-orphan"
    )


class PurchaseOrderDetail(Base):
    __tablename__ = "purchase_order_details"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    purchase_order_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("purchase_orders.id", ondelete="CASCADE"),
        nullable=False,
    )
    product_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("products.id"), nullable=True
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        Computed("quantity * unit_cost", persisted=True),
    )

    purchase_order: Mapped["PurchaseOrder"] = relationship(back_populates="details")
    product: Mapped["Product"] = relationship(back_populates="purchase_order_details")  # noqa: F821
