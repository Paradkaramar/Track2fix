import uuid
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.config import get_config
from app.models import OrderRequest, OrderResponse, PaymentRequest, PaymentResponse
from app.payment import convert_currency


logger = logging.getLogger("payment-service")
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Payment Service")


def _cfg():
    return get_config()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/orders", response_model=OrderResponse)
def create_order(req: OrderRequest):
    order_id = f"ORD-{uuid.uuid4().hex[:6].upper()}"
    logger.info("order.created order_id=%s customer_id=%s amount=%s currency=%s",
                order_id, req.customer_id, req.amount, req.currency)
    return OrderResponse(
        order_id=order_id,
        customer_id=req.customer_id,
        amount=req.amount,
        currency=req.currency,
        status="pending",
    )


@app.post("/payments", response_model=PaymentResponse)
def process_payment(req: PaymentRequest, http_request: Request):
    request_id = http_request.headers.get("X-Request-ID", f"req-{uuid.uuid4().hex[:8]}")
    cfg = _cfg()
    logger.info("payment.started request_id=%s order_id=%s amount=%s currency=%s",
                request_id, req.order_id, req.amount, req.currency)

    try:
        amount_usd = convert_currency(req.amount, req.currency, cfg)
    except ValueError as exc:
        logger.error("payment.config_error request_id=%s error=%s", request_id, str(exc))
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    payment_id = f"PAY-{uuid.uuid4().hex[:6].upper()}"
    logger.info("payment.completed request_id=%s payment_id=%s amount_usd=%s",
                request_id, payment_id, amount_usd)
    return PaymentResponse(
        payment_id=payment_id,
        order_id=req.order_id,
        amount_usd=round(amount_usd, 2),
        status="success",
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    request_id = request.headers.get("X-Request-ID", "unknown")
    logger.error("unhandled_exception request_id=%s error=%s type=%s",
                 request_id, str(exc), type(exc).__name__)
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})
