from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ProductCreate(BaseModel):
    sku: str
    name: str
    description: str | None = None
    unit_price: Decimal
    cost_price: Decimal
    category_id: int | None = None
    supplier_id: int | None = None
    unit: str = "unit"


class ProductUpdate(BaseModel):
    sku: str | None = None
    name: str | None = None
    description: str | None = None
    unit_price: Decimal | None = None
    cost_price: Decimal | None = None
    category_id: int | None = None
    supplier_id: int | None = None
    unit: str | None = None
    is_active: bool | None = None


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sku: str
    name: str
    description: str | None = None
    unit_price: Decimal
    cost_price: Decimal
    category_id: int | None = None
    supplier_id: int | None = None
    unit: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
