from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import hash_password
from app.models.role import Role
from app.models.user import User

ROLES = [
    {"name": "admin", "description": "Full access to all features"},
    {"name": "manager", "description": "Access to reports; no user management"},
    {"name": "employee", "description": "Read-only inventory; create sales orders"},
]

ADMIN_FULL_NAME = "System Administrator"


async def seed_initial_data(db: AsyncSession) -> None:
    """Seed roles and default admin user on first run.

    The admin account credentials are read exclusively from environment variables
    ADMIN_EMAIL and ADMIN_PASSWORD.  If either variable is absent the seed step
    is skipped to prevent accidentally creating an account with a known password.
    """
    # --- Roles ---
    for role_data in ROLES:
        result = await db.execute(select(Role).where(Role.name == role_data["name"]))
        if result.scalar_one_or_none() is None:
            db.add(Role(**role_data))

    await db.flush()  # make roles available for the FK below

    # --- Admin user ---
    admin_email = settings.ADMIN_EMAIL
    admin_password = settings.ADMIN_PASSWORD

    if not admin_email or not admin_password:
        # No credentials supplied — skip creating the bootstrap admin account.
        # Set ADMIN_EMAIL and ADMIN_PASSWORD in the environment on first deploy.
        await db.commit()
        return

    if len(admin_password) < 12:
        raise ValueError(
            "ADMIN_PASSWORD must be at least 12 characters. "
            "Set a strong password in the environment before deploying."
        )

    result = await db.execute(select(User).where(User.email == admin_email))
    if result.scalar_one_or_none() is None:
        admin_role = (
            await db.execute(select(Role).where(Role.name == "admin"))
        ).scalar_one()
        db.add(
            User(
                email=admin_email,
                password_hash=hash_password(admin_password),
                full_name=ADMIN_FULL_NAME,
                role_id=admin_role.id,
            )
        )

    await db.commit()
