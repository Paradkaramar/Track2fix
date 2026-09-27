---
name: trace2fix
description: Investigate production incidents using independent log, code, documentation/configuration, and test analysis, then perform evidence-backed remediation after explicit human approval. Use when the user types /trace2fix or provides an incident ID such as INC-001 and asks to investigate, debug, or trace a production failure.
---

# Trace2Fix — Universal Multi-Agent Incident Investigation & Remediation

This skill guides an AI assistant through structured incident investigation, evidence synthesis,
human-gated approval, and minimal safe remediation. It must **not** use prior knowledge of any
seeded defect — all conclusions must come from repository evidence.

---

## Quick Invocation

```text
/trace2fix INC-001
```
or
```text
Investigate INC-001
```

---

## PHASE 0 — Orientation & Scoping

1. Read `AGENTS.md` in the project root for project-specific constraints and invariants.
2. Identify the incident ID from the user's request (e.g. `INC-001`).
3. Read `incidents/<INCIDENT-ID>.md` to understand the reported symptoms, timeline, and affected endpoint. Extract the representative request ID if present (e.g. `req-1842`).
4. Identify the log file referenced in the incident file (e.g. `incidents/INC-001-logs.json`).
5. **Strict Constraint:** Do **not** read application source, tests, or configuration yet.
6. **Strict Constraint:** Do **not** modify any files during investigation.

---

## PHASE 1 — Parallel Epistemic Investigation

Spawn or execute four strictly isolated investigation roles. Each investigator must analyze **only** their designated domain without cross-domain pollution.

---

### Role A — Log Forensic Investigator

**Domain:** Runtime telemetry only (`incidents/<INCIDENT-ID>-logs.json`).
**Prohibited:** Application code, test files, configuration files, documentation.

**Instructions:**
1. Filter log entries by the representative request ID from the incident file (e.g. `req-1842`).
2. Reconstruct the chronological event sequence: start → intermediate steps → failure.
3. Identify: error type, error message, component names, stack trace snippets if present.
4. Note other request IDs that exhibit the identical failure pattern.

**Output Format:**
```text
AGENT: Log Investigator
OBSERVATIONS: <what the logs directly show>
EVIDENCE: <file:line/entry reference>
HYPOTHESES: <what the log evidence suggests — clearly marked as hypothesis>
UNKNOWNS: <what the logs cannot answer>
```

---

### Role B — Source Code Investigator

**Domain:** Application implementation only (`app/`).
**Prohibited:** Runtime log files, test suites, YAML configuration files.

**Instructions:**
1. Identify the affected endpoint from the incident file.
2. Read `app/main.py` to inspect the route handler.
3. Follow the execution path from the handler through all called functions (e.g. `app/payment.py`).
4. Read each function in the call chain.
5. Identify: unsafe assumptions, missing type guards, places where a `None` or unvalidated value could propagate.

**Output Format:**
```text
AGENT: Code Investigator
EXECUTION PATH: <ordered list of function calls from entry point to failure site>
OBSERVATIONS: <what the code directly shows>
EVIDENCE: <file:line references>
HYPOTHESES: <what the code suggests — clearly marked as hypothesis>
UNKNOWNS: <what code inspection cannot answer>
```

---

### Role C — Documentation & Configuration Investigator

**Domain:** Specifications & Configuration profiles only (`docs/`, `config/`).
**Prohibited:** Application source code, runtime log JSON files.

**Instructions:**
1. Read all files under `docs/` (e.g. `docs/configuration.md`, `docs/api.md`, `docs/payment-flow.md`).
2. Read `config/prod.yaml` and `config/dev.yaml`.
3. Note what each configuration key is documented to require.
4. Compare documented requirements against what is present in production configuration.
5. Flag any mismatches between documented expectations and actual configuration values.

**Output Format:**
```text
AGENT: Documentation + Configuration Investigator
EXPECTED BEHAVIOR: <what docs say should happen>
OBSERVATIONS: <what the config files actually contain>
EVIDENCE: <file references>
MISMATCHES: <documented requirement vs actual config — facts only>
HYPOTHESES: <what mismatches suggest — clearly marked as hypothesis>
UNKNOWNS: <what docs/config cannot answer>
```

---

### Role D — Test Coverage Investigator

**Domain:** Test suite & harness only (`tests/`).
**Prohibited:** Runtime logs, application source code beyond tests, documentation.

**Instructions:**
1. Read all test files under `tests/` (`test_payments.py`, `test_orders.py`).
2. Read `tests/conftest.py` to inspect fixture setup.
3. Identify which scenarios are covered, and which environment configurations are exercised.
4. Identify missing coverage (e.g. tests forced to `APP_ENV=dev` masking production bugs).
5. Recommend a regression test scenario (do **not** create the test yet).

**Output Format:**
```text
AGENT: Test Investigator
EXISTING COVERAGE: <list of tested scenarios>
MISSING COVERAGE: <list of untested scenarios relevant to the incident>
EVIDENCE: <file references>
RECOMMENDED REGRESSION TEST: <describe inputs, expected behavior, expected failure>
UNKNOWNS: <what test inspection cannot answer>
```

---

## PHASE 2 — Multi-Domain Evidence Synthesis

The parent orchestrator collects all four independent reports and executes triangulation:
1. Tabulate directly observed facts vs hypotheses across all four reports.
2. Identify where two or more investigators independently point to the same component or mechanism — this raises confidence.
3. A root cause claim is **HIGH confidence** only when:
   - At least two evidence domains (logs, code, config/docs, tests) independently support it.
   - Zero investigator evidence contradicts it.

---

## PHASE 3 — Root Cause Report

Output the formal structured Root Cause Report:

```text
══════════════════════════════════════════════════════════
TRACE2FIX ROOT CAUSE REPORT
══════════════════════════════════════════════════════════

INCIDENT
  ID       : <incident-id>
  Endpoint : <affected endpoint>
  Symptom  : <external HTTP symptom>

OBSERVED SYMPTOMS
  - <from incident file and logs>

RUNTIME SEQUENCE
  1. <ordered events from log investigator>

RELEVANT EXECUTION PATH
  - <ordered call chain from code investigator>

OBSERVED FACTS (directly evidenced — not hypothesis)
  - <fact 1>  [source: <investigator/file>]
  - <fact 2>  [source: ...]

ROOT CAUSE
  <one concise statement>

SUPPORTING EVIDENCE
  - <file:line or log entry>
  - <cross-referencing second domain>

AFFECTED COMPONENTS
  - <file or component>

MISSING TEST COVERAGE
  - <scenario>

RECOMMENDED REGRESSION TEST
  - <describe inputs, assertion, expected failure>

PROPOSED REMEDIATION
  - <minimal change required>
  - <configuration or code — specify exactly one or both if both are needed>

CONFIDENCE : HIGH / MEDIUM / LOW
REASON     : <why this confidence level>

REMAINING UNKNOWNS
  - <anything unresolved>
══════════════════════════════════════════════════════════
```

---

## PHASE 4 — Mandatory Human Approval Gate

After printing the Root Cause Report, the agent **must** output exactly:

```text
══════════════════════════════════════════════════════════
STATUS: AWAITING REMEDIATION APPROVAL

The root cause analysis above is complete.
No files have been modified.

To proceed with remediation, reply with:
  "Root cause approved. Proceed with remediation."

To cancel, reply with anything else or close the session.
══════════════════════════════════════════════════════════
```

**STOP. Do not proceed until the developer explicitly approves remediation.**

---

## PHASE 5 — Remediation & Verification (After Human Approval)

1. **Step 5.1 (Regression Test):** Create smallest test in `tests/` reproducing the defect.
2. **Step 5.2 (Red Phase):** Run `pytest tests/<new_test>.py -v` and confirm it **fails** (HTTP 500).
3. **Step 5.3 (Minimal Fix):** Apply the smallest surgical remediation to the confirmed file. No refactoring.
4. **Step 5.4 (Green Phase):** Re-run the regression test and confirm it **passes** (HTTP 200).
5. **Step 5.5 (Full Suite):** Run the complete pytest suite (`pytest -v`).
6. **Step 5.6 (Audit Checklist):** Verify all 10 checks:
   - Root cause evidenced
   - Defect reproduced
   - Regression test created
   - Regression test passes post-fix
   - Subsystem tests pass
   - Full test suite passes
   - Documentation impact checked
   - Configuration impact checked
   - Changed files reviewed
   - No unrelated modifications

---

## PHASE 6 — Final Postmortem Publication

Generate the audit report in `reports/<INCIDENT-ID>.md`.
