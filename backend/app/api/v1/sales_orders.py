from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, require_role
from app.db.session import get_db
from app.models.user import User
from app.repositories import sales_order_repo
from app.schemas.sales_order import (
    SalesOrderCreate,
    SalesOrderStatusUpdate,
    SalesOrderResponse,
    SalesOrderDetailResponse2,
)
from app.services import sales_order_service

router = APIRouter()

admin_manager = require_role("admin", "manager")

_VALID_STATUSES = {"pending", "completed", "cancelled"}


@router.get("/", response_model=list[SalesOrderResponse])
async def list_sales_orders(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    status_filter: str | None = None,
    customer_id: int | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    if status_filter is not None and status_filter not in _VALID_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"status_filter must be one of {_VALID_STATUSES}",
        )
    return await sales_order_repo.get_all(
        db, skip=skip, limit=limit, status=status_filter,
        customer_id=customer_id, start_date=start_date, end_date=end_date,
    )


@router.get("/{order_id}", response_model=SalesOrderDetailResponse2)
async def get_sales_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    order = await sales_order_repo.get_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sales order not found")
    return order


@router.post("/", response_model=SalesOrderDetailResponse2, status_code=status.HTTP_201_CREATED)
async def create_sales_order(
    body: SalesOrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    details = [d.model_dump() for d in body.details]
    order = await sales_order_service.create_order(
        db, customer_id=body.customer_id, user_id=current_user.id,
        notes=body.notes, details=details,
    )
    return order


@router.put("/{order_id}/status", response_model=SalesOrderDetailResponse2)
async def update_sales_order_status(
    order_id: int,
    body: SalesOrderStatusUpdate,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(admin_manager),
):
    return await sales_order_service.update_status(db, order_id, body.status)


@router.delete("/{order_id}", response_model=SalesOrderDetailResponse2)
async def cancel_sales_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(admin_manager),
):
    return await sales_order_service.cancel_order(db, order_id)
