from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


_VALID_UNITS = {"unit", "kg", "lt"}


class ProductCreate(BaseModel):
    sku: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    unit_price: Decimal = Field(ge=0)
    cost_price: Decimal = Field(ge=0)
    category_id: int | None = None
    supplier_id: int | None = None
    unit: str = Field(default="unit", max_length=30)

    @field_validator("unit")
    @classmethod
    def unit_allowlist(cls, v: str) -> str:
        if v not in _VALID_UNITS:
            raise ValueError(f"unit must be one of {_VALID_UNITS}")
        return v


class ProductUpdate(BaseModel):
    sku: str | None = Field(default=None, min_length=1, max_length=50)
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    unit_price: Decimal | None = Field(default=None, ge=0)
    cost_price: Decimal | None = Field(default=None, ge=0)
    category_id: int | None = None
    supplier_id: int | None = None
    unit: str | None = Field(default=None, max_length=30)
    is_active: bool | None = None

    @field_validator("unit")
    @classmethod
    def unit_allowlist(cls, v: str | None) -> str | None:
        if v is not None and v not in _VALID_UNITS:
            raise ValueError(f"unit must be one of {_VALID_UNITS}")
        return v


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
