import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


_VALID_PURCHASE_STATUSES = {"pending", "received", "cancelled"}


class PurchaseOrderDetailCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)
    unit_cost: Decimal = Field(ge=0)


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
    notes: str | None = Field(default=None, max_length=500)
    details: list[PurchaseOrderDetailCreate] = Field(min_length=1)


class PurchaseOrderStatusUpdate(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def status_allowlist(cls, v: str) -> str:
        if v not in _VALID_PURCHASE_STATUSES:
            raise ValueError(f"status must be one of {_VALID_PURCHASE_STATUSES}")
        return v


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
