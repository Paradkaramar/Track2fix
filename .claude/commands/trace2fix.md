# Trace2Fix Command (/trace2fix)

Investigate and safely remediate a production incident following the 6-phase Trace2Fix protocol.

## Argument
- `$1`: Incident identifier (e.g. `INC-001`)

## Execution Instructions
1. Review `AGENTS.md` and `incidents/$1.md`.
2. Do not modify files during investigation.
3. Independently inspect:
   - Logs: `incidents/$1-logs.json`
   - Code: `app/main.py`, `app/payment.py`
   - Docs & Config: `docs/configuration.md`, `config/dev.yaml`, `config/prod.yaml`
   - Tests: `tests/conftest.py`, `tests/test_*.py`
4. Print the structured TRACE2FIX ROOT CAUSE REPORT.
5. HALT at the Human Approval Gate:
   ```
   ==================================================
   STATUS: AWAITING REMEDIATION APPROVAL
   To proceed with remediation, reply with:
     "Root cause approved. Proceed with remediation."
   ==================================================
   ```
6. Await explicit approval.
7. Implement TDD remediation (failing regression test -> minimal fix -> full test suite).
8. Verify 10-point checklist and output postmortem to `reports/$1.md`.
