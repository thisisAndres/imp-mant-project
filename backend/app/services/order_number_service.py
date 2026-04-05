from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import purchase_order_repo, sales_order_repo


async def generate_order_number(db: AsyncSession, prefix: str) -> str:
    """Generate next order number like SO-2026-0001 or PO-2026-0001."""
    year = datetime.utcnow().year
    year_prefix = f"{prefix}-{year}-"

    if prefix == "PO":
        max_num = await purchase_order_repo.get_max_order_number(db, year_prefix)
    else:
        max_num = await sales_order_repo.get_max_order_number(db, year_prefix)

    if max_num:
        # Extract the sequential part and increment
        seq = int(max_num.split("-")[-1]) + 1
    else:
        seq = 1

    return f"{year_prefix}{seq:04d}"
