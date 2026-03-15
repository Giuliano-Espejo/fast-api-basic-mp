from __future__ import annotations

from pydantic import BaseModel
from typing import Optional


class PaymentResponse(BaseModel):
    order_id: int
    preference_id: str
    payment_url: str
    sandbox_payment_url: Optional[str] = None