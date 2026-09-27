---
name: trace2fix
description: Investigate production incidents using independent log, code, documentation/configuration, and test analysis, then perform evidence-backed remediation after explicit human approval. Use when the user provides an incident ID such as INC-001 and asks to investigate, debug, or trace a production failure.
---

# Trace2Fix — Production Incident Investigation and Remediation

This skill guides a parent agent through structured incident investigation, evidence synthesis,
human-gated approval, and minimal safe remediation. It must **not** use prior knowledge of any
seeded defect — all conclusions must come from repository evidence.

---

## PHASE 0 — Orientation

1. Read `AGENTS.md` in the project root for project-specific constraints.
2. Identify the incident ID from the user's request (e.g. `INC-001`).
3. Read `incidents/<INCIDENT-ID>.md` to understand the reported symptoms, timeline, and affected
   endpoint. Extract the representative request ID if present.
4. Identify the log file referenced in the incident file.
5. Do **not** read application source, tests, or configuration yet.
6. Do **not** modify any files during investigation.

---

## PHASE 1 — Parallel Investigation

Spawn exactly **four independent investigation subagents** in parallel.
Investigators must not share conclusions with each other before returning.
Each returns a concise structured report only.

---

### Investigator A — Log Investigator

**Goal:** Characterize the runtime failure from log evidence alone.

**Instructions:**
1. Read the incident log file identified in Phase 0.
2. Filter entries by the representative request ID from the incident file.
3. Reconstruct the event sequence for that request: start → intermediate steps → failure.
4. Identify: error type, error message, component names, stack trace snippets if present.
5. Note other request IDs that show the same failure pattern (if any).
6. Do **not** read source code, tests, or configuration files.

**Return this exact structure:**

```
AGENT: Log Investigator

OBSERVATIONS
- <what the logs directly show>

EVIDENCE
- <file: line/entry reference>

HYPOTHESES
- <what the log evidence suggests — clearly marked as hypothesis>

UNKNOWNS
- <what the logs cannot answer>
```

---

### Investigator B — Code Investigator

**Goal:** Trace the observed failure through source code.

**Instructions:**
1. Identify the affected endpoint from the incident file.
2. Read `app/main.py` to find the route handler.
3. Follow the execution path from the handler through all called functions.
4. Read each function in the call chain.
5. Identify: unsafe assumptions, missing guards, places where a bad value could propagate.
6. Do **not** read logs, tests, or configuration files (read config *loading* code only if
   needed to understand how values reach the code).

**Return this exact structure:**

```
AGENT: Code Investigator

EXECUTION PATH
- <ordered list of function calls from entry point to failure site>

OBSERVATIONS
- <what the code directly shows>

EVIDENCE
- <file:line references>

HYPOTHESES
- <what the code suggests — clearly marked as hypothesis>

UNKNOWNS
- <what code inspection cannot answer>
```

---

### Investigator C — Documentation + Configuration Investigator

**Goal:** Determine what behavior was intended and whether configuration matches it.

**Instructions:**
1. Read all files under `docs/`.
2. Read `config/prod.yaml` and `config/dev.yaml`.
3. Note what each configuration key is documented to do.
4. Compare documented requirements against what is present in production configuration.
5. Note any mismatches between documented expectations and actual configuration values.
6. Do **not** read source code or logs.

**Return this exact structure:**

```
AGENT: Documentation + Configuration Investigator

EXPECTED BEHAVIOR
- <what docs say should happen>

OBSERVATIONS
- <what the config files actually contain>

EVIDENCE
- <file references>

MISMATCHES
- <documented requirement vs actual config — only state facts, not conclusions>

HYPOTHESES
- <what mismatches suggest — clearly marked as hypothesis>

UNKNOWNS
- <what docs/config cannot answer>
```

---

### Investigator D — Test Investigator

**Goal:** Assess existing test coverage and identify gaps.

**Instructions:**
1. Read all test files under `tests/`.
2. Read `tests/conftest.py` to understand fixture setup.
3. Identify: which scenarios are covered, which configurations are tested.
4. Identify: scenarios that are *not* covered, particularly edge cases related to the
   incident symptoms.
5. Recommend a regression test scenario (do **not** create the test yet).
6. Do **not** read logs, source code beyond tests, or documentation.

**Return this exact structure:**

```
AGENT: Test Investigator

EXISTING COVERAGE
- <list of tested scenarios>

MISSING COVERAGE
- <list of untested scenarios relevant to the incident>

EVIDENCE
- <file references>

RECOMMENDED REGRESSION TEST
- <describe the test scenario: inputs, expected behavior, expected failure mode>

UNKNOWNS
- <what test inspection cannot answer>
```

---

## PHASE 2 — Evidence Synthesis

After all four investigators return, the **parent agent** must:

1. Tabulate all directly observed facts vs hypotheses across all four reports.
2. Identify where two or more investigators independently point to the same component or
   mechanism — this raises confidence.
3. Identify any conflicts between investigators and note them explicitly.
4. Do **not** treat a single investigator's hypothesis as confirmed fact.
5. A root cause claim is only HIGH confidence when:
   - At least two evidence domains (logs, code, config/docs, tests) independently support it.
   - No investigator evidence contradicts it.

---

## PHASE 3 — Root Cause Report

Output the following report (do **not** edit any files yet):

```
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

OBSERVED FACTS  (directly evidenced — not hypothesis)
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

CONFIDENCE  : HIGH / MEDIUM / LOW
REASON      : <why this confidence level>

REMAINING UNKNOWNS
  - <anything unresolved>
══════════════════════════════════════════════════════════
```

---

## PHASE 4 — Human Approval Gate

After printing the Root Cause Report, output **exactly**:

```
══════════════════════════════════════════════════════════
STATUS: AWAITING REMEDIATION APPROVAL

The root cause analysis above is complete.
No files have been modified.

To proceed with remediation, reply with:
  "Root cause approved. Proceed with remediation."

To cancel, reply with anything else or close the session.
══════════════════════════════════════════════════════════
```

**STOP. Do not proceed until the developer sends explicit approval.**

---

## PHASE 5 — Remediation (only after explicit approval)

### Step 5.1 — Regression Test

1. Create the smallest test that reproduces the confirmed defect.
2. Place it in `tests/` following existing test file conventions.
3. Run the new test **before** changing application code:
   ```
   python -m pytest tests/<new_test_file>.py -v
   ```
4. Record and display the result — it should **fail** at this point.
5. If it unexpectedly passes, re-examine the root cause before continuing.

### Step 5.2 — Minimal Fix

Apply the smallest change that addresses the confirmed root cause:
- Fix only what the evidence identified.
- Do not refactor unrelated code.
- Do not change configuration unless the approved remediation explicitly requires it.
- Do not change documentation unless the fix changes or clarifies documented behavior.

### Step 5.3 — Verification

Run in this order:
1. `python -m pytest tests/<regression_test>.py -v`
2. `python -m pytest tests/ -v`
3. Review the diff of all changed files.

Check each item:

| # | Check | Result |
|---|-------|--------|
| 1 | Root cause supported by evidence | |
| 2 | Defect reproduced by regression test | |
| 3 | Regression test created | |
| 4 | Regression test passes after fix | |
| 5 | Relevant subsystem tests pass | |
| 6 | Full test suite passes | |
| 7 | Documentation impact checked | |
| 8 | Configuration impact checked | |
| 9 | Changed files reviewed | |
| 10 | No unrelated modifications | |

Calculate: `verification_percentage = completed_checks / applicable_checks × 100`

Do not mark VERIFIED unless all applicable checks pass.

### Step 5.4 — Documentation Impact

- Read `docs/configuration.md` and any other potentially affected doc files.
- Determine: does the fix change or clarify any documented behavior?
- If **yes**: update the relevant documentation section minimally.
- If **no**: make no documentation changes.
- Record the decision either way.

---

## PHASE 6 — Final Incident Report

Create `reports/` directory if it does not exist.

Write `reports/<INCIDENT-ID>.md` with these sections:

```markdown
# Trace2Fix Incident Report

## Incident
## Observed Symptoms
## Investigation Summary
## Root Cause
## Supporting Evidence
## Affected Components
## Regression Test
## Before-Fix Test Result
## Remediation
## Files Changed
## Targeted Test Results
## Full Test Suite Result
## Documentation Impact
## Configuration Impact
## Verification Checklist
## Verification Completeness
## Remaining Risks
```

---

## Constraints

- Never read `PROTOTYPE_PLAN.md` as incident evidence.
- Never embed known answers or hard-coded root causes.
- Never skip the human approval gate.
- Never modify incident files (`incidents/`), application code, config, or tests during
  investigation (Phase 0–3).
- Prefer exactly four investigation subagents. Do not spawn extras unless a narrowly scoped
  supporting lookup is genuinely required.
