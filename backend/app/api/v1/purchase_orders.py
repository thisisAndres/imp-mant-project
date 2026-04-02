from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_role
from app.db.session import get_db
from app.models.user import User
from app.repositories import purchase_order_repo
from app.schemas.purchase_order import (
    PurchaseOrderCreate,
    PurchaseOrderStatusUpdate,
    PurchaseOrderResponse,
    PurchaseOrderDetailResponse2,
)
from app.services import purchase_order_service

router = APIRouter()

admin_manager = require_role("admin", "manager")


@router.get("/", response_model=list[PurchaseOrderResponse])
async def list_purchase_orders(
    skip: int = 0,
    limit: int = 100,
    status_filter: str | None = None,
    supplier_id: int | None = None,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(admin_manager),
):
    return await purchase_order_repo.get_all(
        db, skip=skip, limit=limit, status=status_filter, supplier_id=supplier_id
    )


@router.get("/{order_id}", response_model=PurchaseOrderDetailResponse2)
async def get_purchase_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(admin_manager),
):
    order = await purchase_order_repo.get_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Purchase order not found")
    return order


@router.post("/", response_model=PurchaseOrderDetailResponse2, status_code=status.HTTP_201_CREATED)
async def create_purchase_order(
    body: PurchaseOrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_manager),
):
    details = [d.model_dump() for d in body.details]
    order = await purchase_order_service.create_order(
        db, supplier_id=body.supplier_id, user_id=current_user.id,
        notes=body.notes, details=details,
    )
    return order


@router.put("/{order_id}/status", response_model=PurchaseOrderDetailResponse2)
async def update_purchase_order_status(
    order_id: int,
    body: PurchaseOrderStatusUpdate,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(admin_manager),
):
    return await purchase_order_service.update_status(db, order_id, body.status)


@router.delete("/{order_id}", response_model=PurchaseOrderDetailResponse2)
async def cancel_purchase_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(admin_manager),
):
    return await purchase_order_service.cancel_order(db, order_id)
