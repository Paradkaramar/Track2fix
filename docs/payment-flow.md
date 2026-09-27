# Payment Flow

## Overview

Payments are processed via `POST /payments`. The core step for non-USD transactions
is currency conversion, which converts the submitted amount to USD before confirming
the payment.

## Steps

### 1. Request received

`app/main.py` receives a `PaymentRequest` containing:

- `order_id` — reference to the associated order
- `amount` — payment amount in the submitted currency
- `currency` — ISO 4217 currency code (e.g. `USD`, `EUR`)

### 2. Configuration loaded

`get_config()` is called to load the active environment's YAML configuration.
The configuration supplies runtime parameters including the exchange rate.

### 3. Currency conversion

`app/payment.py → convert_currency(amount, currency, config)`

- If `currency == "USD"`: amount is returned unchanged.
- Otherwise: the configured `EXCHANGE_RATE` is retrieved and applied:

  ```
  amount_usd = float(amount) * EXCHANGE_RATE
  ```

### 4. Response

A `PaymentResponse` is returned with:

- `payment_id` — generated identifier
- `order_id` — echoed from request
- `amount_usd` — converted amount
- `status` — `"success"`

## Currency Conversion Dependency

Currency conversion for non-USD payments requires `EXCHANGE_RATE` to be present and
numeric in the active configuration. This value must be set correctly for the service
to process cross-currency payments.
