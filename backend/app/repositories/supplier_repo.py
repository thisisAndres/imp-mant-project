from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.supplier import Supplier


async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Supplier]:
    result = await db.execute(select(Supplier).offset(skip).limit(limit))
    return list(result.scalars().all())


async def get_by_id(db: AsyncSession, supplier_id: int) -> Supplier | None:
    result = await db.execute(select(Supplier).where(Supplier.id == supplier_id))
    return result.scalar_one_or_none()


async def create(db: AsyncSession, *, company_name: str, contact_name: str | None = None,
                 email: str | None = None, phone: str | None = None,
                 address: str | None = None) -> Supplier:
    supplier = Supplier(
        company_name=company_name, contact_name=contact_name,
        email=email, phone=phone, address=address,
    )
    db.add(supplier)
    await db.commit()
    await db.refresh(supplier)
    return supplier


async def update_supplier(db: AsyncSession, supplier_id: int, data: dict) -> Supplier | None:
    supplier = await get_by_id(db, supplier_id)
    if not supplier:
        return None
    for key, value in data.items():
        if value is not None:
            setattr(supplier, key, value)
    await db.commit()
    await db.refresh(supplier)
    return supplier


async def deactivate(db: AsyncSession, supplier_id: int) -> Supplier | None:
    supplier = await get_by_id(db, supplier_id)
    if not supplier:
        return None
    supplier.is_active = False
    await db.commit()
    await db.refresh(supplier)
    return supplier
