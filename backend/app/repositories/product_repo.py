from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product


async def get_all(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    category_id: int | None = None,
    supplier_id: int | None = None,
    is_active: bool | None = None,
) -> list[Product]:
    stmt = select(Product)
    if category_id is not None:
        stmt = stmt.where(Product.category_id == category_id)
    if supplier_id is not None:
        stmt = stmt.where(Product.supplier_id == supplier_id)
    if is_active is not None:
        stmt = stmt.where(Product.is_active == is_active)
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_by_id(db: AsyncSession, product_id: int) -> Product | None:
    result = await db.execute(select(Product).where(Product.id == product_id))
    return result.scalar_one_or_none()


async def create(db: AsyncSession, **kwargs) -> Product:
    product = Product(**kwargs)
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product


async def update_product(db: AsyncSession, product_id: int, data: dict) -> Product | None:
    product = await get_by_id(db, product_id)
    if not product:
        return None
    for key, value in data.items():
        if value is not None:
            setattr(product, key, value)
    await db.commit()
    await db.refresh(product)
    return product


async def deactivate(db: AsyncSession, product_id: int) -> Product | None:
    product = await get_by_id(db, product_id)
    if not product:
        return None
    product.is_active = False
    await db.commit()
    await db.refresh(product)
    return product
