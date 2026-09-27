# API Reference

## Base URL

`http://localhost:8000`

---

## GET /health

Health check endpoint.

**Response**

```json
{"status": "ok"}
```

HTTP 200.

---

## POST /orders

Create a new order.

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `customer_id` | string | yes | Customer identifier |
| `amount` | float | yes | Order amount |
| `currency` | string | no | ISO 4217 currency code. Default: `USD` |
| `description` | string | no | Optional order description |

**Response (200)**

```json
{
  "order_id": "ORD-A1B2C3",
  "customer_id": "cust-001",
  "amount": 100.0,
  "currency": "USD",
  "status": "pending"
}
```

---

## POST /payments

Process a payment for an existing order.

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `order_id` | string | yes | Order to pay |
| `amount` | float | yes | Payment amount |
| `currency` | string | no | ISO 4217 currency code. Default: `USD` |

**Request header (optional)**

| Header | Description |
|--------|-------------|
| `X-Request-ID` | Caller-supplied request identifier used in logs |

**Response (200)**

```json
{
  "payment_id": "PAY-D4E5F6",
  "order_id": "ORD-A1B2C3",
  "amount_usd": 108.0,
  "status": "success"
}
```

**Error responses**

| HTTP Status | Meaning |
|-------------|---------|
| 422 | Validation error — malformed request body |
| 500 | Internal server error — see application logs |
