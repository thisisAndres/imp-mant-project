from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, require_role
from app.db.session import get_db
from app.models.user import User
from app.repositories import product_repo
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse

router = APIRouter()

admin_manager = require_role("admin", "manager")


@router.get("/", response_model=list[ProductResponse])
async def list_products(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    category_id: int | None = None,
    supplier_id: int | None = None,
    is_active: bool | None = None,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    return await product_repo.get_all(
        db, skip=skip, limit=limit,
        category_id=category_id, supplier_id=supplier_id, is_active=is_active,
    )


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    product = await product_repo.get_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    body: ProductCreate,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(admin_manager),
):
    return await product_repo.create(db, **body.model_dump())


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    body: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(admin_manager),
):
    product = await product_repo.update_product(
        db, product_id, body.model_dump(exclude_unset=True)
    )
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


@router.delete("/{product_id}", response_model=ProductResponse)
async def deactivate_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(admin_manager),
):
    product = await product_repo.deactivate(db, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product
