from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.role import Role
from app.models.user import User

ROLES = [
    {"name": "admin", "description": "Full access to all features"},
    {"name": "manager", "description": "Access to reports; no user management"},
    {"name": "employee", "description": "Read-only inventory; create sales orders"},
]

ADMIN_EMAIL = "admin@sgiv.local"
ADMIN_PASSWORD = "Admin1234!"
ADMIN_FULL_NAME = "System Administrator"


async def seed_initial_data(db: AsyncSession) -> None:
    """Seed roles and default admin user on first run."""
    # --- Roles ---
    for role_data in ROLES:
        result = await db.execute(select(Role).where(Role.name == role_data["name"]))
        if result.scalar_one_or_none() is None:
            db.add(Role(**role_data))

    await db.flush()  # make roles available for the FK below

    # --- Admin user ---
    result = await db.execute(select(User).where(User.email == ADMIN_EMAIL))
    if result.scalar_one_or_none() is None:
        admin_role = (
            await db.execute(select(Role).where(Role.name == "admin"))
        ).scalar_one()
        db.add(
            User(
                email=ADMIN_EMAIL,
                password_hash=hash_password(ADMIN_PASSWORD),
                full_name=ADMIN_FULL_NAME,
                role_id=admin_role.id,
            )
        )

    await db.commit()
