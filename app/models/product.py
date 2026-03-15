from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

from .order import OrderItem


class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    name: str = Field(index=True)
    description: Optional[str] = None
    price: float = Field(gt=0)
    stock: int = Field(ge=0, default=0)
    image_url: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.now)

    order_items: List[OrderItem] = Relationship(back_populates="product")