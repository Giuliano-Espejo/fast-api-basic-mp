from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional


class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float = Field(gt=0)
    stock: int = Field(ge=0, default=0)
    image_url: Optional[str] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(default=None, gt=0)
    stock: Optional[int] = Field(default=None, ge=0)
    image_url: Optional[str] = None