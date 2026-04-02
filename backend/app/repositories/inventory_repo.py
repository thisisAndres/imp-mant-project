from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.inventory import Inventory


async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Inventory]:
    result = await db.execute(
        select(Inventory).options(selectinload(Inventory.product)).offset(skip).limit(limit)
    )
    return list(result.scalars().all())


async def get_by_product(db: AsyncSession, product_id: int) -> Inventory | None:
    result = await db.execute(
        select(Inventory)
        .options(selectinload(Inventory.product))
        .where(Inventory.product_id == product_id)
    )
    return result.scalar_one_or_none()


async def update_quantity(db: AsyncSession, product_id: int, delta: int) -> Inventory | None:
    """Atomically add delta to the inventory quantity for a product."""
    await db.execute(
        update(Inventory)
        .where(Inventory.product_id == product_id)
        .values(
            quantity=Inventory.quantity + delta,
            last_updated_at=datetime.now(timezone.utc),
        )
        .execution_options(synchronize_session=False)
    )
    await db.flush()
    return await get_by_product(db, product_id)


async def set_inventory(
    db: AsyncSession,
    product_id: int,
    quantity: int,
    min_stock: int | None = None,
    max_stock: int | None = None,
) -> Inventory | None:
    inv = await get_by_product(db, product_id)
    if not inv:
        return None
    values: dict = {"quantity": quantity, "last_updated_at": datetime.now(timezone.utc)}
    if min_stock is not None:
        values["min_stock"] = min_stock
    if max_stock is not None:
        values["max_stock"] = max_stock
    await db.execute(
        update(Inventory)
        .where(Inventory.product_id == product_id)
        .values(**values)
        .execution_options(synchronize_session=False)
    )
    await db.commit()
    return await get_by_product(db, product_id)


async def create_inventory(db: AsyncSession, product_id: int, quantity: int = 0,
                           min_stock: int = 5, max_stock: int = 500) -> Inventory:
    inv = Inventory(product_id=product_id, quantity=quantity,
                    min_stock=min_stock, max_stock=max_stock)
    db.add(inv)
    await db.commit()
    await db.refresh(inv)
    return inv
