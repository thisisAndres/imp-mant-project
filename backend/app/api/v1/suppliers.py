from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_role
from app.db.session import get_db
from app.models.user import User
from app.repositories import supplier_repo
from app.schemas.supplier import SupplierCreate, SupplierUpdate, SupplierResponse

router = APIRouter()

admin_manager = require_role("admin", "manager")


@router.get("/", response_model=list[SupplierResponse])
async def list_suppliers(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(admin_manager),
):
    return await supplier_repo.get_all(db, skip, limit)


@router.get("/{supplier_id}", response_model=SupplierResponse)
async def get_supplier(
    supplier_id: int,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(admin_manager),
):
    supplier = await supplier_repo.get_by_id(db, supplier_id)
    if not supplier:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found")
    return supplier


@router.post("/", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
async def create_supplier(
    body: SupplierCreate,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(admin_manager),
):
    return await supplier_repo.create(
        db, company_name=body.company_name, contact_name=body.contact_name,
        email=body.email, phone=body.phone, address=body.address,
    )


@router.put("/{supplier_id}", response_model=SupplierResponse)
async def update_supplier(
    supplier_id: int,
    body: SupplierUpdate,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(admin_manager),
):
    supplier = await supplier_repo.update_supplier(
        db, supplier_id, body.model_dump(exclude_unset=True)
    )
    if not supplier:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found")
    return supplier


@router.delete("/{supplier_id}", response_model=SupplierResponse)
async def deactivate_supplier(
    supplier_id: int,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(admin_manager),
):
    supplier = await supplier_repo.deactivate(db, supplier_id)
    if not supplier:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found")
    return supplier
