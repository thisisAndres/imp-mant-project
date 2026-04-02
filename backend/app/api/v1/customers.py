from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_role
from app.db.session import get_db
from app.models.user import User
from app.repositories import customer_repo
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse

router = APIRouter()

admin_manager = require_role("admin", "manager")


@router.get("/", response_model=list[CustomerResponse])
async def list_customers(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(admin_manager),
):
    return await customer_repo.get_all(db, skip, limit)


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: int,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(admin_manager),
):
    customer = await customer_repo.get_by_id(db, customer_id)
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return customer


@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    body: CustomerCreate,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(admin_manager),
):
    return await customer_repo.create(
        db, full_name=body.full_name, email=body.email,
        phone=body.phone, address=body.address, id_number=body.id_number,
    )


@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: int,
    body: CustomerUpdate,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(admin_manager),
):
    customer = await customer_repo.update_customer(
        db, customer_id, body.model_dump(exclude_unset=True)
    )
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return customer


@router.delete("/{customer_id}", response_model=CustomerResponse)
async def deactivate_customer(
    customer_id: int,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(admin_manager),
):
    customer = await customer_repo.deactivate(db, customer_id)
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return customer
