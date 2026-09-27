# Benchmark Results

Structured results are persisted to `benchmark/results.csv` by the CLI.
This file contains usage guidance and a summary template.

## Quick Reference

```bash
# Start investigation timer
python benchmark/benchmark.py start --workflow manual --incident INC-001 --phase investigation

# Stop investigation timer
python benchmark/benchmark.py stop  --workflow manual --incident INC-001 --phase investigation

# Record final metrics (timing auto-read from stopped timers if not overridden)
python benchmark/benchmark.py record \
  --workflow manual \
  --incident INC-001 \
  --manual-steps 15 \
  --root-cause-correct yes \
  --fix-attempts 2 \
  --regression-test-created yes \
  --verification-completed 8 \
  --verification-total 10

# List all recorded results
python benchmark/benchmark.py list

# Compare manual vs trace2fix for an incident
python benchmark/benchmark.py compare --incident INC-001
```

## Metrics Recorded

| Field | Description |
|-------|-------------|
| `incident_id` | Incident identifier |
| `workflow` | `manual` or `trace2fix` |
| `investigation_time_seconds` | Time from start to root-cause identification |
| `resolution_time_seconds` | Time from approval to verified fix |
| `total_time_seconds` | Sum of above |
| `manual_steps` | Distinct manual actions taken |
| `root_cause_correct` | `yes` / `no` |
| `fix_attempts` | Number of fix iterations before passing tests |
| `regression_test_created` | `yes` / `no` |
| `verification_completed` | Checks that passed (out of 10) |
| `verification_total` | Applicable checks (≤ 10) |
| `verification_percentage` | `completed / total × 100` |

## Notes

Populate rows after each investigation run. Results are appended to `results.csv`;
multiple runs for the same incident/workflow are all preserved.
