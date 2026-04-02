import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class PurchaseOrderDetailCreate(BaseModel):
    product_id: int
    quantity: int
    unit_cost: Decimal


class PurchaseOrderDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    purchase_order_id: int
    product_id: int | None = None
    quantity: int
    unit_cost: Decimal
    subtotal: Decimal


class PurchaseOrderCreate(BaseModel):
    supplier_id: int | None = None
    notes: str | None = None
    details: list[PurchaseOrderDetailCreate]


class PurchaseOrderStatusUpdate(BaseModel):
    status: str


class PurchaseOrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_number: str
    supplier_id: int | None = None
    user_id: uuid.UUID | None = None
    status: str
    total_amount: Decimal
    notes: str | None = None
    ordered_at: datetime
    received_at: datetime | None = None


class PurchaseOrderDetailResponse2(BaseModel):
    """Extended response including nested details."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_number: str
    supplier_id: int | None = None
    user_id: uuid.UUID | None = None
    status: str
    total_amount: Decimal
    notes: str | None = None
    ordered_at: datetime
    received_at: datetime | None = None
    details: list[PurchaseOrderDetailResponse] = []
