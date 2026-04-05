import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sales_order import SalesOrder
from app.repositories import sales_order_repo, inventory_repo
from app.services.order_number_service import generate_order_number


async def create_order(
    db: AsyncSession,
    customer_id: int | None,
    user_id: uuid.UUID,
    notes: str | None,
    details: list[dict],
) -> SalesOrder:
    order_number = await generate_order_number(db, "SO")
    order = SalesOrder(
        order_number=order_number,
        customer_id=customer_id,
        user_id=user_id,
        notes=notes,
    )
    return await sales_order_repo.create(db, order, details)


async def update_status(db: AsyncSession, order_id: int, new_status: str) -> SalesOrder:
    order = await sales_order_repo.get_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sales order not found")

    valid_transitions = {
        "pending": ["completed", "cancelled"],
        "completed": [],
        "cancelled": [],
    }
    if new_status not in valid_transitions.get(order.status, []):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot transition from '{order.status}' to '{new_status}'",
        )

    if new_status == "completed":
        # Check stock availability before decrementing
        for detail in order.details:
            inv = await inventory_repo.get_by_product(db, detail.product_id)
            if not inv or inv.quantity < detail.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Insufficient stock for one or more items in this order",
                )
        # Decrement inventory
        for detail in order.details:
            await inventory_repo.update_quantity(db, detail.product_id, -detail.quantity)

    return await sales_order_repo.update_status(db, order_id, new_status)


async def cancel_order(db: AsyncSession, order_id: int) -> SalesOrder:
    order = await sales_order_repo.get_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sales order not found")
    if order.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending orders can be cancelled",
        )
    return await sales_order_repo.update_status(db, order_id, "cancelled")
