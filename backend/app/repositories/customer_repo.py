from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customer import Customer


async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Customer]:
    result = await db.execute(select(Customer).offset(skip).limit(limit))
    return list(result.scalars().all())


async def get_by_id(db: AsyncSession, customer_id: int) -> Customer | None:
    result = await db.execute(select(Customer).where(Customer.id == customer_id))
    return result.scalar_one_or_none()


async def create(db: AsyncSession, *, full_name: str, email: str | None = None,
                 phone: str | None = None, address: str | None = None,
                 id_number: str | None = None) -> Customer:
    customer = Customer(
        full_name=full_name, email=email, phone=phone,
        address=address, id_number=id_number,
    )
    db.add(customer)
    await db.commit()
    await db.refresh(customer)
    return customer


async def update_customer(db: AsyncSession, customer_id: int, data: dict) -> Customer | None:
    customer = await get_by_id(db, customer_id)
    if not customer:
        return None
    for key, value in data.items():
        if value is not None:
            setattr(customer, key, value)
    await db.commit()
    await db.refresh(customer)
    return customer


async def deactivate(db: AsyncSession, customer_id: int) -> Customer | None:
    customer = await get_by_id(db, customer_id)
    if not customer:
        return None
    customer.is_active = False
    await db.commit()
    await db.refresh(customer)
    return customer
