# Trace2Fix Demo

A minimal FastAPI payment/order service used to demonstrate the Trace2Fix agentic
debugging workflow powered by IBM Bob 2.0.

The repository contains a seeded production incident (INC-001) for use with the
Trace2Fix investigation skill. Do not repair INC-001 manually — it is intentional
and required for the demonstration.

---

## Setup

```bash
pip install -r requirements.txt
```

---

## Running Tests

```bash
pytest
```

All tests use development configuration and should pass.

---

## Development Server

```bash
APP_ENV=dev uvicorn app.main:app --reload
```

---

## Production Server

```bash
APP_ENV=prod uvicorn app.main:app --reload
```

---

## Reproducing INC-001

Run the reproduction script (no server required):

```bash
python scripts/reproduce_incident.py
```

The script uses production configuration and will print the HTTP response status.

Alternatively, with a running production server:

```bash
curl -X POST http://localhost:8000/payments \
  -H "Content-Type: application/json" \
  -H "X-Request-ID: req-1842" \
  -d '{"order_id":"ORD-INC001","amount":250,"currency":"EUR"}'
```

---

## Trace2Fix Skill

The `trace2fix` Bob skill automates incident investigation and remediation.

**Flow:**
1. **Investigation** — four independent agents analyze logs, code, docs/config, and tests in parallel.
2. **Synthesis** — the parent agent correlates evidence and produces a root-cause report.
3. **Approval gate** — the skill stops and waits for explicit human confirmation before changing anything.
4. **Remediation** — regression test → minimal fix → full test suite → documentation impact check → incident report.

**Invoke the skill:**

In Bob, start a new task and say:

```
Investigate INC-001
```

or

```
/trace2fix INC-001
```

**Benchmark the investigation:**

```bash
# Start timer
python benchmark/benchmark.py start --workflow trace2fix --incident INC-001 --phase investigation.

# (run the skill)

# Stop timer after root-cause report
python benchmark/benchmark.py stop --workflow trace2fix --incident INC-001 --phase investigation

# Start resolution timer after approval
python benchmark/benchmark.py start --workflow trace2fix --incident INC-001 --phase resolution

# (approve and complete remediation)

# Stop and record final metrics
python benchmark/benchmark.py stop --workflow trace2fix --incident INC-001 --phase resolution
python benchmark/benchmark.py record \
  --workflow trace2fix --incident INC-001 \
  --root-cause-correct yes --fix-attempts 1 \
  --regression-test-created yes \
  --verification-completed 10 --verification-total 10

# Compare against a manual run
python benchmark/benchmark.py compare --incident INC-001
```

Incident reports are written to `reports/<INCIDENT-ID>.md` after remediation.

---

## Project Structure

```
app/            Application source (FastAPI, config, payment logic, models)
config/         Environment configuration files
tests/          Pytest test suite
incidents/      Incident reports and logs
docs/           Architecture, API, payment flow, and configuration docs
scripts/        Utility scripts including the INC-001 reproducer
benchmark/      Investigation timing CLI and results.csv
reports/        Trace2Fix incident reports (generated after remediation)
.bob/skills/    Bob skills including trace2fix
```
