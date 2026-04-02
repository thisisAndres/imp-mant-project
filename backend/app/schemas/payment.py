from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class PaymentCreate(BaseModel):
    sales_order_id: int
    amount: Decimal
    method: str


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sales_order_id: int | None = None
    amount: Decimal
    method: str
    status: str
    paid_at: datetime
