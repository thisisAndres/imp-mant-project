import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


_VALID_SALES_STATUSES = {"pending", "completed", "cancelled"}


class SalesOrderDetailCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)
    unit_price: Decimal = Field(ge=0)


class SalesOrderDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sales_order_id: int
    product_id: int | None = None
    quantity: int
    unit_price: Decimal
    subtotal: Decimal


class SalesOrderCreate(BaseModel):
    customer_id: int | None = None
    notes: str | None = Field(default=None, max_length=500)
    details: list[SalesOrderDetailCreate] = Field(min_length=1)


class SalesOrderStatusUpdate(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def status_allowlist(cls, v: str) -> str:
        if v not in _VALID_SALES_STATUSES:
            raise ValueError(f"status must be one of {_VALID_SALES_STATUSES}")
        return v


class SalesOrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_number: str
    customer_id: int | None = None
    user_id: uuid.UUID | None = None
    status: str
    total_amount: Decimal
    notes: str | None = None
    created_at: datetime


class SalesOrderDetailResponse2(BaseModel):
    """Extended response including nested details."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_number: str
    customer_id: int | None = None
    user_id: uuid.UUID | None = None
    status: str
    total_amount: Decimal
    notes: str | None = None
    created_at: datetime
    details: list[SalesOrderDetailResponse] = []
