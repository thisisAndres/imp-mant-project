import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.purchase_order import PurchaseOrder
from app.repositories import purchase_order_repo, inventory_repo
from app.services.order_number_service import generate_order_number


async def create_order(
    db: AsyncSession,
    supplier_id: int | None,
    user_id: uuid.UUID,
    notes: str | None,
    details: list[dict],
) -> PurchaseOrder:
    order_number = await generate_order_number(db, "PO")
    order = PurchaseOrder(
        order_number=order_number,
        supplier_id=supplier_id,
        user_id=user_id,
        notes=notes,
    )
    return await purchase_order_repo.create(db, order, details)


async def update_status(db: AsyncSession, order_id: int, new_status: str) -> PurchaseOrder:
    order = await purchase_order_repo.get_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Purchase order not found")

    valid_transitions = {
        "pending": ["received", "cancelled"],
        "received": [],
        "cancelled": [],
    }
    if new_status not in valid_transitions.get(order.status, []):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot transition from '{order.status}' to '{new_status}'",
        )

    received_at = None
    if new_status == "received":
        received_at = datetime.now(timezone.utc).replace(tzinfo=None)
        # Increment inventory for each detail line
        for detail in order.details:
            await inventory_repo.update_quantity(db, detail.product_id, detail.quantity)

    return await purchase_order_repo.update_status(db, order_id, new_status, received_at)


async def cancel_order(db: AsyncSession, order_id: int) -> PurchaseOrder:
    order = await purchase_order_repo.get_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Purchase order not found")
    if order.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending orders can be cancelled",
        )
    return await purchase_order_repo.update_status(db, order_id, "cancelled")
