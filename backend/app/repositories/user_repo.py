import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.core.security import hash_password


async def get_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(
        select(User).options(selectinload(User.role)).where(User.email == email)
    )
    return result.scalar_one_or_none()


async def get_by_id(db: AsyncSession, user_id: uuid.UUID) -> User | None:
    result = await db.execute(
        select(User).options(selectinload(User.role)).where(User.id == user_id)
    )
    return result.scalar_one_or_none()


async def list_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[User]:
    result = await db.execute(
        select(User).options(selectinload(User.role)).offset(skip).limit(limit)
    )
    return list(result.scalars().all())


async def create(db: AsyncSession, *, email: str, password: str, full_name: str, role_id: int | None = None) -> User:
    user = User(
        email=email,
        password_hash=hash_password(password),
        full_name=full_name,
        role_id=role_id,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user, attribute_names=["role"])
    return user


async def update_user(db: AsyncSession, user_id: uuid.UUID, data: dict) -> User | None:
    user = await get_by_id(db, user_id)
    if not user:
        return None
    for key, value in data.items():
        if value is not None:
            setattr(user, key, value)
    await db.commit()
    return await get_by_id(db, user_id)


async def deactivate(db: AsyncSession, user_id: uuid.UUID) -> User | None:
    user = await get_by_id(db, user_id)
    if not user:
        return None
    user.is_active = False
    await db.commit()
    await db.refresh(user)
    return user
