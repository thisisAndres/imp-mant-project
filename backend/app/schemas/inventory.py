from datetime import datetime

from pydantic import BaseModel, ConfigDict


class InventoryUpdate(BaseModel):
    quantity: int
    min_stock: int | None = None
    max_stock: int | None = None


class InventoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    quantity: int
    min_stock: int
    max_stock: int
    last_updated_at: datetime
    stock_status: str | None = None
