from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password


async def seed_initial_data(db: AsyncSession) -> None:
    """Seed roles and default admin user."""
    pass
