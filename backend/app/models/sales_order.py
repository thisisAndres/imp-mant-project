import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Computed, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base


class SalesOrder(Base):
    __tablename__ = "sales_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    customer_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("customers.id"), nullable=True
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    status: Mapped[str] = mapped_column(String(30), server_default="pending")
    total_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), server_default="0")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    customer: Mapped["Customer"] = relationship(back_populates="sales_orders")  # noqa: F821
    user: Mapped["User"] = relationship(back_populates="sales_orders")  # noqa: F821
    details: Mapped[list["SalesOrderDetail"]] = relationship(
        back_populates="sales_order", cascade="all, delete-orphan"
    )
    payments: Mapped[list["Payment"]] = relationship(back_populates="sales_order")  # noqa: F821


class SalesOrderDetail(Base):
    __tablename__ = "sales_order_details"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sales_order_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("sales_orders.id", ondelete="CASCADE"),
        nullable=False,
    )
    product_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("products.id"), nullable=True
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        Computed("quantity * unit_price", persisted=True),
    )

    sales_order: Mapped["SalesOrder"] = relationship(back_populates="details")
    product: Mapped["Product"] = relationship(back_populates="sales_order_details")  # noqa: F821
