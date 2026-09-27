# AGENTS.md — Plan Mode

Do not plan repairs to seeded incidents unless explicitly requested during remediation.

## Non-Obvious Architectural Constraints

- **No module-level config binding.** Any plan that reads `APP_ENV` or calls `get_config()`
  at module scope will break env-switching for tests and `reproduce_incident.py`. Config
  must remain lazy (resolved at call time).

- **No persistence.** There is no database and none is planned for this prototype. Orders
  are not stored between requests. Do not plan features that assume order lookup by ID.

- **Single process.** There are no microservices, queues, or background workers. All
  request handling is synchronous within the single FastAPI process.

- **Four-domain evidence isolation.** Changes to the codebase must preserve the property
  that each of the four domains (logs, code, config/docs, tests) contributes distinct
  evidence toward INC-001 without any single domain alone revealing the full root cause.
  Plans that add comments, log lines, or documentation that name the missing config key
  in the context of INC-001 break this property.

- **Trace2Fix remediation sequence** (when explicitly requested):
  1. Write regression test → confirm it fails
  2. Apply minimal fix
  3. Run targeted tests → run full suite
  4. Inspect docs impact; update `docs/configuration.md` **only if** behavior changes
  5. Record `Documentation impact: update required / no update required` in report
