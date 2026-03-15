from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from ..models.order import OrderStatus


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int


class OrderCreate(BaseModel):
    user_email: str
    items: List[OrderItemCreate]


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    quantity: int
    unit_price: float
    subtotal: float


class OrderResponse(BaseModel):
    id: int
    user_email: str
    status: OrderStatus
    total_amount: float
    preference_id: Optional[str]
    payment_id: Optional[str]
    created_at: datetime
    paid_at: Optional[datetime]
    items: List[OrderItemResponse]