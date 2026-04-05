from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payment import Payment


async def get_all(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    sales_order_id: int | None = None,
) -> list[Payment]:
    stmt = select(Payment)
    if sales_order_id is not None:
        stmt = stmt.where(Payment.sales_order_id == sales_order_id)
    stmt = stmt.order_by(Payment.paid_at.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def create(db: AsyncSession, *, sales_order_id: int, amount, method: str) -> Payment:
    payment = Payment(sales_order_id=sales_order_id, amount=amount, method=method)
    db.add(payment)
    await db.commit()
    await db.refresh(payment)
    return payment
