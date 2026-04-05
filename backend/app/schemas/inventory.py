from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class InventoryUpdate(BaseModel):
    quantity: int = Field(ge=0)
    min_stock: int | None = Field(default=None, ge=0)
    max_stock: int | None = Field(default=None, ge=0)


class InventoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    quantity: int
    min_stock: int
    max_stock: int
    last_updated_at: datetime
    stock_status: str | None = None
