# GitHub Copilot Instructions for Trace2Fix

When prompted with `/trace2fix` or asked to investigate an incident (such as `INC-001`):

1. **Protocol:** Strictly adhere to `AGENTS.md` and `.bob/skills/trace2fix/SKILL.md`.
2. **Investigation Phase:** Do not make any edits or modify code/configuration.
3. **Four Evidence Domains:**
   - Log Telemetry: `incidents/`
   - Code Call Paths: `app/`
   - Specifications & Config: `docs/`, `config/`
   - Test Gaps: `tests/`
4. **Approval Gate:** Output the formal root-cause synthesis report and halt execution. Require explicit user approval before generating any fixes or tests.
5. **Remediation Phase:** Apply Test-Driven Development (regression test -> confirmation of failure -> minimal fix -> test passage -> 10-point checklist).
