# AGENTS.md

This file provides repository guidance for agents working on the Trace2Fix prototype.

## Seeded Incidents

This repository contains intentionally seeded production incidents used for debugging and remediation exercises.

Do not repair, modify, bypass, or preemptively fix a seeded incident unless remediation has been explicitly approved.

During investigation:

- treat the incident as unknown,
- gather evidence before forming conclusions,
- distinguish observations from hypotheses,
- do not modify application source, tests, documentation, or configuration,
- do not assume that any single artifact contains the complete root cause.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests
python -m pytest

# Run a single payment test
python -m pytest tests/test_payments.py::test_payment_currency_conversion -v

# Reproduce the seeded incident deterministically
python scripts/reproduce_incident.py

# Run development server
APP_ENV=dev uvicorn app.main:app --reload

# Run production-style server
APP_ENV=prod uvicorn app.main:app --reload
```

## Repository Structure

Key project areas:

```text
app/          Application source code
config/       Environment configuration
tests/        Automated tests
incidents/    Incident descriptions and logs
docs/         Architecture, API, payment-flow, and configuration documentation
scripts/      Utility and reproduction scripts
benchmark/    Manual and Trace2Fix benchmark tooling
```

Agents should inspect only the areas relevant to their assigned task.

## Configuration

Application configuration is stored under:

```text
config/
```

The active configuration environment is selected using:

```text
APP_ENV
```

`app/config.py` is responsible for configuration loading.

Configuration must remain dynamically selectable so tests and scripts can operate in different environments without depending on permanently cached module-level state.

Do not change configuration behavior during investigation.

Configuration changes are allowed only after explicit remediation approval and only when supported by the confirmed root cause.

## Testing

The project uses Pytest.

General rules:

- normal test execution uses the development configuration,
- tests should be run from the repository root,
- application HTTP errors may be inspected through FastAPI TestClient behavior,
- existing tests represent pre-incident coverage,
- do not create or modify regression tests during investigation.

During remediation:

1. create the smallest regression test that reproduces the confirmed defect,
2. run it before the fix where practical,
3. confirm the expected failure,
4. apply the approved remediation,
5. rerun the regression test,
6. run relevant subsystem tests,
7. run the full test suite.

## Code Style

Follow the existing project conventions.

- Logger name: `payment-service`
- Log messages use `key=value` pairs.
- Event names use dot notation, for example:
  - `payment.started`
  - `payment.completed`
  - `unhandled_exception`
- Pydantic v2 models are used.
- Keep models thin unless validation is required by an approved change.
- Use Python 3.10+ type-hint syntax such as `str | None`.
- Avoid unnecessary abstractions.
- Avoid unrelated refactoring.
- No persistence layer is used.

## Incident Investigation Rules

When investigating an incident, consider all relevant evidence categories:

- runtime logs,
- application source code,
- configuration,
- project documentation,
- existing tests.

Do not assume in advance which category contains the decisive evidence.

Independent investigators should analyze their assigned evidence separately before findings are combined.

Each investigator should return a concise structured summary containing:

- observations,
- evidence,
- hypotheses,
- unknowns.

Evidence should reference concrete repository files or locations whenever possible.

Do not present hypotheses as confirmed facts.

## Root-Cause Analysis Rules

A root-cause conclusion should be produced only after available evidence has been correlated.

The final investigation summary should distinguish:

### Observed Facts

Directly supported by logs, code, configuration, documentation, or tests.

### Hypotheses

Possible explanations that still require supporting evidence.

### Confirmed Root Cause

A conclusion supported by sufficient evidence across the available repository artifacts.

If evidence conflicts or remains incomplete, report the investigation as inconclusive rather than forcing a conclusion.

## Human Approval Gate

Investigation and remediation are separate phases.

Before explicit developer approval:

- do not modify application source,
- do not modify configuration,
- do not modify documentation,
- do not add tests,
- do not implement a fix.

After investigation, present:

- observed symptoms,
- execution path,
- root-cause conclusion,
- supporting evidence,
- affected components,
- missing test coverage,
- proposed remediation,
- confidence,
- remaining unknowns.

Then stop and wait for explicit remediation approval.

## Remediation Rules

After explicit approval:

- create the smallest regression test that captures the confirmed defect,
- reproduce the failure where practical,
- apply the smallest safe remediation,
- avoid unrelated cleanup or refactoring,
- preserve existing behavior outside the incident scope,
- run targeted tests,
- run the full test suite,
- inspect the final diff,
- check documentation impact,
- check configuration impact.

Documentation should be modified only when the approved remediation changes or clarifies documented behavior.

Configuration should be modified only when supported by the confirmed remediation.

## Verification Rules

Do not mark an incident as resolved unless the required verification steps have actually completed.

Verification should consider:

- root cause supported by evidence,
- defect reproduced,
- regression test created,
- regression test passes after the fix,
- relevant subsystem tests pass,
- full test suite passes,
- documentation impact checked,
- configuration impact checked,
- changed files reviewed,
- no unrelated modifications introduced.

If any required verification step fails, report the remediation as incomplete.

## Trace2Fix Agent Coordination

When the Trace2Fix workflow is invoked, use separate investigation roles for:

1. runtime logs,
2. application source code,
3. documentation and configuration,
4. existing test coverage.

Where supported, independent investigations should run in parallel.

Investigators should not read or depend on another investigator's conclusions before completing their own analysis.

The parent agent is responsible for:

- collecting investigator summaries,
- correlating evidence,
- identifying agreement or conflict,
- producing the final root-cause report,
- stopping at the human approval gate.

## Scope Control

This is a hackathon prototype.

Do not add unnecessary systems or features unless explicitly requested.

Avoid introducing:

- databases,
- Docker,
- frontend applications,
- CI/CD pipelines,
- external observability platforms,
- OpenTelemetry,
- authentication systems,
- new microservices,
- external APIs,
- unrelated dependencies.

Prefer the smallest implementation that satisfies the current task.