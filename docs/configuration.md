# Configuration Reference

Configuration is loaded from `config/<APP_ENV>.yaml` where `APP_ENV` defaults to `dev`.

## Environment Selection

Set the `APP_ENV` environment variable before starting the service:

```bash
APP_ENV=dev   uvicorn app.main:app   # development
APP_ENV=prod  uvicorn app.main:app   # production
```

## Configuration Keys

| Key | Type | Required | Description |
|-----|------|----------|-------------|
| `SERVICE_NAME` | string | yes | Name reported in logs |
| `BASE_CURRENCY` | string | yes | Base currency for payments (expected: `USD`) |
| `EXCHANGE_RATE` | float | yes | Multiplier applied to convert non-base-currency amounts to USD |
| `PAYMENT_TIMEOUT_SEC` | integer | yes | Maximum seconds allowed for a payment operation |
| `LOG_LEVEL` | string | no | Logging verbosity. Default: `INFO` |

## Notes

- `EXCHANGE_RATE` is required whenever the service processes payments in a currency
  other than `BASE_CURRENCY`. It must be a positive float.
- Missing or `null` values for required keys will cause runtime failures when the
  affected code path is exercised.
- Configuration files are plain YAML. There is no schema enforcement at startup.

## Example: dev.yaml

```yaml
SERVICE_NAME: payment-service
BASE_CURRENCY: USD
EXCHANGE_RATE: 1.08
PAYMENT_TIMEOUT_SEC: 5
LOG_LEVEL: INFO
```
