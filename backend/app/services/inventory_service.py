from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import inventory_repo


def compute_stock_status(quantity: int, min_stock: int) -> str:
    if quantity <= 0:
        return "critical"
    if quantity <= min_stock:
        return "low"
    return "normal"


async def get_all_with_status(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[dict]:
    inventories = await inventory_repo.get_all(db, skip, limit)
    results = []
    for inv in inventories:
        results.append({
            "inventory": inv,
            "stock_status": compute_stock_status(inv.quantity, inv.min_stock),
        })
    return results


async def get_by_product_with_status(db: AsyncSession, product_id: int) -> dict | None:
    inv = await inventory_repo.get_by_product(db, product_id)
    if not inv:
        return None
    return {
        "inventory": inv,
        "stock_status": compute_stock_status(inv.quantity, inv.min_stock),
    }
