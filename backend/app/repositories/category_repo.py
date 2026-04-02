from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category


async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Category]:
    result = await db.execute(select(Category).offset(skip).limit(limit))
    return list(result.scalars().all())


async def get_by_id(db: AsyncSession, category_id: int) -> Category | None:
    result = await db.execute(select(Category).where(Category.id == category_id))
    return result.scalar_one_or_none()


async def create(db: AsyncSession, *, name: str, description: str | None = None) -> Category:
    category = Category(name=name, description=description)
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


async def update_category(db: AsyncSession, category_id: int, data: dict) -> Category | None:
    category = await get_by_id(db, category_id)
    if not category:
        return None
    for key, value in data.items():
        if value is not None:
            setattr(category, key, value)
    await db.commit()
    await db.refresh(category)
    return category


async def delete(db: AsyncSession, category_id: int) -> bool:
    category = await get_by_id(db, category_id)
    if not category:
        return False
    await db.delete(category)
    await db.commit()
    return True
