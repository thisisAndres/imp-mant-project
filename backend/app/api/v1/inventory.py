from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, require_role
from app.db.session import get_db
from app.models.user import User
from app.repositories import inventory_repo
from app.schemas.inventory import InventoryUpdate, InventoryResponse
from app.services import inventory_service

router = APIRouter()

admin_manager = require_role("admin", "manager")


@router.get("/", response_model=list[InventoryResponse])
async def list_inventory(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    items = await inventory_service.get_all_with_status(db, skip, limit)
    results = []
    for item in items:
        inv = item["inventory"]
        results.append(InventoryResponse(
            id=inv.id,
            product_id=inv.product_id,
            quantity=inv.quantity,
            min_stock=inv.min_stock,
            max_stock=inv.max_stock,
            last_updated_at=inv.last_updated_at,
            stock_status=item["stock_status"],
        ))
    return results


@router.get("/{product_id}", response_model=InventoryResponse)
async def get_inventory(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    item = await inventory_service.get_by_product_with_status(db, product_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory not found")
    inv = item["inventory"]
    return InventoryResponse(
        id=inv.id,
        product_id=inv.product_id,
        quantity=inv.quantity,
        min_stock=inv.min_stock,
        max_stock=inv.max_stock,
        last_updated_at=inv.last_updated_at,
        stock_status=item["stock_status"],
    )


@router.put("/{product_id}", response_model=InventoryResponse)
async def update_inventory(
    product_id: int,
    body: InventoryUpdate,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(admin_manager),
):
    inv = await inventory_repo.set_inventory(
        db, product_id, body.quantity, body.min_stock, body.max_stock
    )
    if not inv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory not found")
    item = await inventory_service.get_by_product_with_status(db, product_id)
    return InventoryResponse(
        id=inv.id,
        product_id=inv.product_id,
        quantity=inv.quantity,
        min_stock=inv.min_stock,
        max_stock=inv.max_stock,
        last_updated_at=inv.last_updated_at,
        stock_status=item["stock_status"] if item else "normal",
    )
