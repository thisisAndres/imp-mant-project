from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


_VALID_PAYMENT_METHODS = {"cash", "card", "transfer"}


class PaymentCreate(BaseModel):
    sales_order_id: int
    amount: Decimal = Field(gt=0)
    method: str

    @field_validator("method")
    @classmethod
    def method_allowlist(cls, v: str) -> str:
        if v not in _VALID_PAYMENT_METHODS:
            raise ValueError(f"method must be one of {_VALID_PAYMENT_METHODS}")
        return v


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sales_order_id: int | None = None
    amount: Decimal
    method: str
    status: str
    paid_at: datetime
