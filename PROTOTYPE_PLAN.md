# Trace2Fix Prototype Plan

## Overview

Minimal Python FastAPI application simulating a payment/order service.
One deterministic seeded bug (missing `EXCHANGE_RATE` in production config) causes
a `TypeError` during currency conversion, returning HTTP 500. The root cause is only
recoverable by correlating evidence across logs, source code, configuration/docs, and
tests. Bob 2.0's Trace2Fix skill investigates INC-001, synthesizes evidence, receives
human approval, then repairs and verifies.

---

## Repository Structure

```
trace2fix/
├── app/
│   __init__.py
│   main.py              # FastAPI app, routes: POST /orders, POST /payments
│   config.py            # Loads YAML config; get(key) returns None if key absent
│   payment.py           # Currency conversion — reads rate from config, assumes non-None
│   models.py            # Pydantic request/response models
├── config/
│   dev.yaml             # Full config including EXCHANGE_RATE
│   prod.yaml            # BUG: EXCHANGE_RATE intentionally omitted
├── tests/
│   conftest.py          # Pytest fixtures; loads dev config by default
│   test_orders.py       # Happy-path order tests (pass)
│   test_payments.py     # Happy-path payment tests using dev config (pass)
├── incidents/
│   INC-001.md           # Incident: timeline, impact, symptoms only — no root cause
│   INC-001-logs.json    # Noisy structured logs; TypeError buried in noise, no cause named
├── docs/
│   architecture.md      # Component overview, request flow
│   payment-flow.md      # Payment processing steps, currency conversion logic
│   api.md               # Endpoint contracts, request/response shapes
│   configuration.md     # Config keys, required vs optional, env overrides
├── scripts/
│   reproduce_incident.py  # Deterministic INC-001 reproducer via FastAPI TestClient
├── benchmark/
│   benchmark.py         # CLI tool: record start/stop timestamps, compute duration
│   results.md           # Template for recording manual vs Trace2Fix results
├── requirements.txt
├── PROTOTYPE_PLAN.md
└── README.md
```

---

## Implementation Order

1. **`requirements.txt`** — fastapi, uvicorn, pyyaml, pydantic, pytest, httpx
2. **`config/dev.yaml` and `config/prod.yaml`** — insert the bug in prod
3. **`app/config.py`** — load YAML by env var `APP_ENV` (default `dev`); `get(key)` returns
   `None` for absent keys; config object is instantiated per-request or injected so tests
   and scripts can override `APP_ENV` without hitting Python module-caching issues
4. **`app/models.py`** — `OrderRequest`, `PaymentRequest`, response models
5. **`app/payment.py`** — `convert_currency(amount, currency)` reads `EXCHANGE_RATE` via
   `config.get()`; assumes value is a valid float; no None-guard → `TypeError` when `None`
6. **`app/main.py`** — FastAPI app; `POST /orders`, `POST /payments`
7. **`tests/`** — fixtures load dev config; write happy-path tests (all must pass)
8. **`incidents/INC-001.md`** and **`incidents/INC-001-logs.json`**
9. **`docs/`** — four lightweight markdown docs
10. **`scripts/reproduce_incident.py`** — sets `APP_ENV=prod`, uses FastAPI `TestClient`,
    issues the failing payment request, prints HTTP status; must not reveal root cause
11. **`benchmark/benchmark.py`** and **`benchmark/results.md`**
12. **`README.md`** — setup, test, dev-server commands; how to run reproducer;
    states a seeded production incident exists; must not reveal root cause

---

## Primary Incident Behavior

| Attribute | Detail |
|-----------|--------|
| Bug area | Interaction between production config and payment/currency-conversion logic |
| Trigger | `POST /payments` with `currency != "USD"` while `APP_ENV=prod` |
| Production condition | `EXCHANGE_RATE` absent from `config/prod.yaml`; `config.get()` returns `None` |
| Runtime symptom | Currency calculation receives `None` rate → `TypeError` (unsupported operand for `float * NoneType`) |
| External symptom | HTTP 500 `Internal Server Error` |
| Log evidence | Payment request failed; currency-conversion stage involved; `TypeError`; request ID and call sequence — no root cause named |
| Code evidence | `payment.py` reads rate from config and assumes non-None; no validation present |
| Config/docs evidence | `prod.yaml` lacks the required key; `docs/configuration.md` documents `EXCHANGE_RATE` as required |
| Test evidence | Dev-config payment scenarios covered; missing-config scenario not covered |
| Incident file | `incidents/INC-001.md` |
| Log file | `incidents/INC-001-logs.json` — ≥ 40 lines; `TypeError` present but not the first entry |

### What remains intentionally broken before Trace2Fix investigates

- `config/prod.yaml` does **not** contain `EXCHANGE_RATE`
- `app/payment.py` has no None-guard on the rate value
- No regression test exists for the missing-rate scenario
- `INC-001.md` and logs do not name `EXCHANGE_RATE` or missing configuration as the cause
- `README.md` acknowledges a seeded incident but does not describe it

---

## Configuration

```yaml
# dev.yaml (complete)
SERVICE_NAME: payment-service
BASE_CURRENCY: USD
EXCHANGE_RATE: 1.08          # EUR/USD rate used for conversion
PAYMENT_TIMEOUT_SEC: 5

# prod.yaml (intentionally missing EXCHANGE_RATE — this is the seeded bug)
SERVICE_NAME: payment-service
BASE_CURRENCY: USD
PAYMENT_TIMEOUT_SEC: 5
```

### Configuration loading note

`config.py` must not bind `APP_ENV` permanently at module-import time. Load the YAML
file lazily or pass the environment as a parameter so that `reproduce_incident.py` and
test fixtures can reliably switch between `dev` and `prod` without Python module-caching
problems. Keep this simple — a plain function or a lightweight class instantiated on
first use per call-site is sufficient.

---

## Run Commands

```bash
# Install
pip install -r requirements.txt

# Run dev server
APP_ENV=dev uvicorn app.main:app --reload

# Run prod server (exposes the bug)
APP_ENV=prod uvicorn app.main:app --reload

# Manually trigger INC-001 (optional — use reproducer script instead)
curl -X POST http://localhost:8000/payments \
  -H "Content-Type: application/json" \
  -d '{"order_id":"ORD-001","amount":100,"currency":"EUR"}'
# → HTTP 500

# Deterministic incident reproduction (no manual server required)
python scripts/reproduce_incident.py
# → prints request payload and HTTP 500 response

# Run tests (all must pass — dev config by default)
pytest

# Benchmark CLI
python benchmark/benchmark.py start --investigator manual --incident INC-001
python benchmark/benchmark.py stop  --investigator manual --incident INC-001
```

---

## Acceptance Criteria

- [ ] `pytest` (default, dev config) passes all tests with zero failures
- [ ] `APP_ENV=dev` currency payment request → HTTP 200
- [ ] `python scripts/reproduce_incident.py` deterministically → HTTP 500
- [ ] Runtime failure is a `TypeError` (not `KeyError: EXCHANGE_RATE`)
- [ ] `INC-001.md` contains realistic timeline, impact, and symptoms only — does not name `EXCHANGE_RATE`, missing config, or any root-cause hypothesis
- [ ] `INC-001-logs.json` contains ≥ 40 lines; `TypeError` traceback present but not the first entry; root cause not named
- [ ] `README.md` does not reveal the root cause of INC-001
- [ ] `docs/configuration.md` documents `EXCHANGE_RATE` as a required key
- [ ] All four doc files reference real symbols/config keys from the codebase
- [ ] Each of the four evidence domains (logs, code, config/docs, tests) contributes distinct evidence without alone revealing the complete root cause
- [ ] `scripts/reproduce_incident.py` exists and prints HTTP status without revealing root cause
- [ ] Benchmark tool records start/stop and computes elapsed seconds to stdout
- [ ] No database, no Docker, no frontend, no extra services

---

## What Trace2Fix Will Do (Post-Plan, Not Implemented Here)

The `trace2fix` Bob skill (Phase 2) will:

1. Run four parallel investigation sub-agents (logs / source / docs+config / tests)
2. Parent agent synthesizes evidence → STOP for human approval
3. On approval: write regression test → confirm it fails → apply minimal fix →
   run targeted tests → run full suite
4. Inspect documentation impact; update `docs/configuration.md` **only if** the fix
   changes or clarifies documented behavior; record `Documentation impact: update required /
   no update required` with a short reason in the final report
5. Generate incident report

The prototype must be in the "broken" state described above when Trace2Fix is invoked.
