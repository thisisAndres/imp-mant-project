from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.sales_order import SalesOrder, SalesOrderDetail


async def get_all(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    status: str | None = None,
    customer_id: int | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> list[SalesOrder]:
    stmt = select(SalesOrder)
    if status:
        stmt = stmt.where(SalesOrder.status == status)
    if customer_id is not None:
        stmt = stmt.where(SalesOrder.customer_id == customer_id)
    if start_date:
        stmt = stmt.where(SalesOrder.created_at >= start_date)
    if end_date:
        stmt = stmt.where(SalesOrder.created_at <= end_date)
    stmt = stmt.order_by(SalesOrder.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_by_id(db: AsyncSession, order_id: int) -> SalesOrder | None:
    result = await db.execute(
        select(SalesOrder)
        .options(selectinload(SalesOrder.details))
        .where(SalesOrder.id == order_id)
    )
    return result.scalar_one_or_none()


async def get_max_order_number(db: AsyncSession, prefix: str) -> str | None:
    result = await db.execute(
        select(func.max(SalesOrder.order_number))
        .where(SalesOrder.order_number.like(f"{prefix}%"))
    )
    return result.scalar_one_or_none()


async def create(db: AsyncSession, order: SalesOrder, details: list[dict]) -> SalesOrder:
    db.add(order)
    await db.flush()
    total = 0
    for d in details:
        detail = SalesOrderDetail(
            sales_order_id=order.id,
            product_id=d["product_id"],
            quantity=d["quantity"],
            unit_price=d["unit_price"],
        )
        db.add(detail)
        total += d["quantity"] * d["unit_price"]
    order.total_amount = total
    await db.commit()
    await db.refresh(order, attribute_names=["details"])
    return order


async def update_status(db: AsyncSession, order_id: int, status: str) -> SalesOrder | None:
    order = await get_by_id(db, order_id)
    if not order:
        return None
    order.status = status
    await db.commit()
    await db.refresh(order, attribute_names=["details"])
    return order
