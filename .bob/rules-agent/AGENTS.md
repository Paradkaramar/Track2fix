# AGENTS.md — Agent (Coding) Mode

Do not repair seeded incidents unless explicitly requested during remediation.

## Non-Obvious Coding Rules

### Config injection pattern
`app/main.py` uses a private `_cfg()` helper that calls `get_config()` on each request.
When writing new routes or tests, follow this pattern — do **not** call `get_config()` at
module level or store it in a module-level variable (that would permanently capture `APP_ENV`
at import time and break env-switching).

### TestClient env switching
Always set `os.environ["APP_ENV"]` **before** the `from app.main import app` import line.
Module-level FastAPI app object is created at import; env must already be correct.
See `scripts/reproduce_incident.py` for the canonical pattern.

### Exception handling
`app/main.py` has a global `@app.exception_handler(Exception)` that catches all unhandled
exceptions and returns `{"detail": "Internal Server Error"}` with HTTP 500 — without
re-raising. When using `TestClient(raise_server_exceptions=False)`, 500s are returned
as normal responses. When using `raise_server_exceptions=True`, the underlying exception
propagates to the test (useful for asserting exception type).

### IDs
Order IDs: `ORD-{uuid4().hex[:6].upper()}` — 6 hex chars, uppercase.
Payment IDs: `PAY-{uuid4().hex[:6].upper()}` — same pattern.
Request IDs: read from `X-Request-ID` header; auto-generated as `req-{uuid4().hex[:8]}` if absent.

### No persistence
There is no database. Orders are not stored. The `POST /orders` route returns a generated
`order_id` but nothing is persisted. Payment routes do not validate that an order exists.
