from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.purchase_order import PurchaseOrder, PurchaseOrderDetail


async def get_all(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    status: str | None = None,
    supplier_id: int | None = None,
) -> list[PurchaseOrder]:
    stmt = select(PurchaseOrder)
    if status:
        stmt = stmt.where(PurchaseOrder.status == status)
    if supplier_id is not None:
        stmt = stmt.where(PurchaseOrder.supplier_id == supplier_id)
    stmt = stmt.order_by(PurchaseOrder.ordered_at.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_by_id(db: AsyncSession, order_id: int) -> PurchaseOrder | None:
    result = await db.execute(
        select(PurchaseOrder)
        .options(selectinload(PurchaseOrder.details))
        .where(PurchaseOrder.id == order_id)
    )
    return result.scalar_one_or_none()


async def get_max_order_number(db: AsyncSession, prefix: str) -> str | None:
    result = await db.execute(
        select(func.max(PurchaseOrder.order_number))
        .where(PurchaseOrder.order_number.like(f"{prefix}%"))
    )
    return result.scalar_one_or_none()


async def create(db: AsyncSession, order: PurchaseOrder, details: list[dict]) -> PurchaseOrder:
    db.add(order)
    await db.flush()
    total = 0
    for d in details:
        detail = PurchaseOrderDetail(
            purchase_order_id=order.id,
            product_id=d["product_id"],
            quantity=d["quantity"],
            unit_cost=d["unit_cost"],
        )
        db.add(detail)
        total += d["quantity"] * d["unit_cost"]
    order.total_amount = total
    await db.commit()
    await db.refresh(order, attribute_names=["details"])
    return order


async def update_status(db: AsyncSession, order_id: int, status: str,
                        received_at=None) -> PurchaseOrder | None:
    order = await get_by_id(db, order_id)
    if not order:
        return None
    order.status = status
    if received_at:
        order.received_at = received_at
    await db.commit()
    await db.refresh(order, attribute_names=["details"])
    return order
