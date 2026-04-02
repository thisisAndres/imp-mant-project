import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class SalesOrderDetailCreate(BaseModel):
    product_id: int
    quantity: int
    unit_price: Decimal


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
    notes: str | None = None
    details: list[SalesOrderDetailCreate]


class SalesOrderStatusUpdate(BaseModel):
    status: str


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
