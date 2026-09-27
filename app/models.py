from pydantic import BaseModel
from typing import Optional


class OrderRequest(BaseModel):
    customer_id: str
    amount: float
    currency: str = "USD"
    description: Optional[str] = None


class OrderResponse(BaseModel):
    order_id: str
    customer_id: str
    amount: float
    currency: str
    status: str


class PaymentRequest(BaseModel):
    order_id: str
    amount: float
    currency: str = "USD"


class PaymentResponse(BaseModel):
    payment_id: str
    order_id: str
    amount_usd: float
    status: str
