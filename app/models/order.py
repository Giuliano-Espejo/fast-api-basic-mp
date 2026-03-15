from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from enum import Enum

if TYPE_CHECKING:
    from .product import Product


class OrderStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    user_email: str = Field(index=True)
    status: OrderStatus = Field(default=OrderStatus.PENDING)
    total_amount: float = Field(gt=0)

    # Mercado Pago
    preference_id: Optional[str] = None
    payment_id: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.now)
    paid_at: Optional[datetime] = None

    # relación
    items: List["OrderItem"] = Relationship(back_populates="order")


class OrderItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    order_id: int = Field(foreign_key="order.id")
    product_id: int = Field(foreign_key="product.id")

    quantity: int = Field(gt=0)
    unit_price: float = Field(gt=0)

    # relaciones
    order: "Order" = Relationship(back_populates="items")
    product: "Product" = Relationship(back_populates="order_items")