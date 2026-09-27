# Architecture

## Overview

`payment-service` is a single-process Python FastAPI application that handles order
creation and payment processing. It has no external database or message queue.

## Components

```
┌─────────────────────────────────────────────────────┐
│                   payment-service                   │
│                                                     │
│  app/main.py       FastAPI application, routes      │
│  app/config.py     YAML configuration loader        │
│  app/payment.py    Currency conversion logic        │
│  app/models.py     Pydantic request/response types  │
│                                                     │
│  config/dev.yaml   Development environment config   │
│  config/prod.yaml  Production environment config    │
└─────────────────────────────────────────────────────┘
```

## Request Flow

```
Client
  │
  ▼
POST /payments (app/main.py)
  │  reads APP_ENV → loads config YAML (app/config.py)
  │
  ▼
convert_currency(amount, currency, config)  (app/payment.py)
  │  reads EXCHANGE_RATE from config
  │
  ▼
PaymentResponse → HTTP 200
```

## Environment Selection

The application selects its configuration file using the `APP_ENV` environment variable.
Accepted values: `dev`, `prod`. Default: `dev`.

Configuration is loaded on each request via `get_config()` — it is not cached at
module import time.
