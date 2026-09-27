# AGENTS.md — Ask Mode

Do not describe the root cause of INC-001 unless explicitly working on remediation.

## Non-Obvious Documentation Context

- `PROTOTYPE_PLAN.md` contains implementation knowledge about the seeded incident. It is
  the only file where the root cause is described explicitly — it exists for construction
  purposes, not for agent investigation use.
- `docs/configuration.md` is the canonical reference for what configuration keys are
  required. It documents expected behavior, not the current production state.
- `incidents/INC-001.md` deliberately omits the root cause — this is intentional, not
  an oversight. Do not add diagnostic information to it.
- `incidents/INC-001-logs.json` contains synthetic but realistic log entries. The
  relevant error entries are not the first entries — agents must filter by `request_id`.
- The `benchmark/results.md` template is for recording human-vs-Trace2Fix timing and
  verification completeness. It is intentionally blank until investigations run.
