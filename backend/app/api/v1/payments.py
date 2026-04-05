from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_role
from app.db.session import get_db
from app.models.user import User
from app.repositories import payment_repo
from app.schemas.payment import PaymentCreate, PaymentResponse

router = APIRouter()

admin_manager = require_role("admin", "manager")


@router.get("/", response_model=list[PaymentResponse])
async def list_payments(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    sales_order_id: int | None = None,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(admin_manager),
):
    return await payment_repo.get_all(db, skip=skip, limit=limit, sales_order_id=sales_order_id)


@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(
    body: PaymentCreate,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(admin_manager),
):
    return await payment_repo.create(
        db, sales_order_id=body.sales_order_id, amount=body.amount, method=body.method
    )
