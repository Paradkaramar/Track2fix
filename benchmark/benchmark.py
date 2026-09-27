"""
Trace2Fix Benchmark CLI

Supports start/stop timing for investigation and resolution phases,
recording final metrics, and optional comparison of manual vs trace2fix.

Usage:
    python benchmark/benchmark.py start  --workflow manual --incident INC-001 --phase investigation
    python benchmark/benchmark.py stop   --workflow manual --incident INC-001 --phase investigation
    python benchmark/benchmark.py record --workflow manual --incident INC-001 \\
        --manual-steps 15 --root-cause-correct yes --fix-attempts 2 \\
        --regression-test-created yes --verification-completed 8 --verification-total 10
    python benchmark/benchmark.py compare --incident INC-001
    python benchmark/benchmark.py list
"""
import argparse
import csv
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

BENCH_DIR = Path(__file__).parent
STATE_FILE = BENCH_DIR / ".benchmark_state.json"
RESULTS_CSV = BENCH_DIR / "results.csv"

CSV_FIELDS = [
    "incident_id",
    "workflow",
    "recorded_at",
    "investigation_time_seconds",
    "resolution_time_seconds",
    "total_time_seconds",
    "manual_steps",
    "root_cause_correct",
    "fix_attempts",
    "regression_test_created",
    "verification_completed",
    "verification_total",
    "verification_percentage",
]


# ── State helpers ─────────────────────────────────────────────────────────────

def _load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}


def _save_state(state: dict):
    STATE_FILE.write_text(json.dumps(state, indent=2))


def _timer_key(workflow: str, incident: str, phase: str) -> str:
    return f"{workflow}:{incident}:{phase}"


# ── CSV helpers ───────────────────────────────────────────────────────────────

def _ensure_csv():
    if not RESULTS_CSV.exists():
        with open(RESULTS_CSV, "w", newline="") as f:
            csv.DictWriter(f, fieldnames=CSV_FIELDS).writeheader()


def _read_csv() -> list[dict]:
    if not RESULTS_CSV.exists():
        return []
    with open(RESULTS_CSV, newline="") as f:
        return list(csv.DictReader(f))


def _append_csv(row: dict):
    _ensure_csv()
    with open(RESULTS_CSV, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writerow(row)


def _get_elapsed(state: dict, workflow: str, incident: str, phase: str) -> float | None:
    key = _timer_key(workflow, incident, phase)
    if key in state:
        return time.time() - state[key]["start"]
    return None


# ── Commands ──────────────────────────────────────────────────────────────────

def cmd_start(args):
    state = _load_state()
    key = _timer_key(args.workflow, args.incident, args.phase)
    if key in state:
        print(f"Timer already running: {key}. Stop it first.")
        sys.exit(1)
    state[key] = {
        "start": time.time(),
        "workflow": args.workflow,
        "incident": args.incident,
        "phase": args.phase,
    }
    _save_state(state)
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
    print(f"[{ts}] Timer started  workflow={args.workflow}  incident={args.incident}  phase={args.phase}")


def cmd_stop(args):
    state = _load_state()
    key = _timer_key(args.workflow, args.incident, args.phase)
    if key not in state:
        print(f"No timer running for: {key}. Run 'start' first.")
        sys.exit(1)
    entry = state.pop(key)
    elapsed = time.time() - entry["start"]
    _save_state(state)
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
    print(f"[{ts}] Timer stopped  workflow={args.workflow}  incident={args.incident}  phase={args.phase}")
    print(f"      Elapsed: {elapsed:.1f}s  ({elapsed / 60:.1f} min)")
    # Persist phase time to a scratch area so 'record' can pick it up
    scratch_key = f"elapsed:{args.workflow}:{args.incident}:{args.phase}"
    state2 = _load_state()
    state2[scratch_key] = round(elapsed, 1)
    _save_state(state2)
    return elapsed


def cmd_record(args):
    state = _load_state()

    def _elapsed_from_state(phase: str) -> float:
        key = f"elapsed:{args.workflow}:{args.incident}:{phase}"
        return float(state.get(key, 0))

    inv_time = args.investigation_time if args.investigation_time is not None else _elapsed_from_state("investigation")
    res_time = args.resolution_time if args.resolution_time is not None else _elapsed_from_state("resolution")
    total = round(inv_time + res_time, 1)

    completed = args.verification_completed
    total_v = args.verification_total
    pct = round(completed / total_v * 100, 1) if total_v > 0 else 0.0

    row = {
        "incident_id": args.incident,
        "workflow": args.workflow,
        "recorded_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "investigation_time_seconds": inv_time,
        "resolution_time_seconds": res_time,
        "total_time_seconds": total,
        "manual_steps": args.manual_steps,
        "root_cause_correct": args.root_cause_correct,
        "fix_attempts": args.fix_attempts,
        "regression_test_created": args.regression_test_created,
        "verification_completed": completed,
        "verification_total": total_v,
        "verification_percentage": pct,
    }

    _append_csv(row)
    print(f"Recorded: {args.workflow} / {args.incident}")
    print(f"  investigation_time : {inv_time}s")
    print(f"  resolution_time    : {res_time}s")
    print(f"  total_time         : {total}s")
    print(f"  verification       : {completed}/{total_v} ({pct}%)")
    print(f"  root_cause_correct : {args.root_cause_correct}")
    print(f"  fix_attempts       : {args.fix_attempts}")
    print(f"  regression_test    : {args.regression_test_created}")
    print(f"  >> written to {RESULTS_CSV}")


def cmd_compare(args):
    rows = _read_csv()
    incident_rows = [r for r in rows if r["incident_id"] == args.incident]
    by_workflow: dict[str, dict] = {}
    for r in incident_rows:
        by_workflow[r["workflow"]] = r

    if len(by_workflow) < 2:
        present = list(by_workflow.keys()) or ["(none)"]
        print(f"Not enough data to compare for {args.incident}. Found: {present}")
        sys.exit(0)

    manual = by_workflow.get("manual")
    t2f = by_workflow.get("trace2fix")
    if not manual or not t2f:
        print(f"Need both 'manual' and 'trace2fix' rows. Found: {list(by_workflow.keys())}")
        sys.exit(0)

    def _f(v):
        try:
            return float(v)
        except (TypeError, ValueError):
            return None

    def _diff(a, b, label, unit="s", lower_better=True):
        fa, fb = _f(a), _f(b)
        if fa is None or fb is None:
            print(f"  {label:<35} manual={a}  trace2fix={b}")
            return
        diff = fb - fa
        direction = "faster" if diff < 0 else "slower"
        if not lower_better:
            direction = "better" if diff > 0 else "worse"
        print(f"  {label:<35} manual={fa}{unit}  trace2fix={fb}{unit}  d={diff:+.1f}{unit} ({direction})")

    print(f"\n{'-'*60}")
    print(f"Comparison: {args.incident}")
    print(f"{'-'*60}")
    _diff(manual["investigation_time_seconds"], t2f["investigation_time_seconds"], "Investigation time")
    _diff(manual["resolution_time_seconds"],    t2f["resolution_time_seconds"],    "Resolution time")
    _diff(manual["total_time_seconds"],          t2f["total_time_seconds"],          "Total time")
    _diff(manual["manual_steps"],                t2f["manual_steps"],                "Manual steps", unit="")
    _diff(manual["fix_attempts"],                t2f["fix_attempts"],                "Fix attempts", unit="")
    _diff(manual["verification_percentage"],     t2f["verification_percentage"],     "Verification completeness", unit="%", lower_better=False)
    print(f"  {'Root cause correct':<35} manual={manual['root_cause_correct']}  trace2fix={t2f['root_cause_correct']}")
    print(f"  {'Regression test created':<35} manual={manual['regression_test_created']}  trace2fix={t2f['regression_test_created']}")
    print(f"{'-'*60}\n")


def cmd_list(_args):
    rows = _read_csv()
    if not rows:
        print("No results recorded yet.")
        return
    print(f"\n{'-'*90}")
    print(f"{'incident':<12} {'workflow':<12} {'inv(s)':<8} {'res(s)':<8} {'total(s)':<10} {'rc?':<6} {'verify%':<10} recorded_at")
    print(f"{'-'*90}")
    for r in rows:
        print(f"{r['incident_id']:<12} {r['workflow']:<12} {r['investigation_time_seconds']:<8} "
              f"{r['resolution_time_seconds']:<8} {r['total_time_seconds']:<10} "
              f"{r['root_cause_correct']:<6} {r['verification_percentage']:<10} {r['recorded_at']}")
    print(f"{'-'*90}\n")


# ── CLI definition ────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Trace2Fix benchmark CLI — time investigations and record metrics.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # start
    p_start = sub.add_parser("start", help="Start a phase timer")
    p_start.add_argument("--workflow", required=True, choices=["manual", "trace2fix"])
    p_start.add_argument("--incident", required=True)
    p_start.add_argument("--phase", required=True, choices=["investigation", "resolution"])

    # stop
    p_stop = sub.add_parser("stop", help="Stop a phase timer and save elapsed time")
    p_stop.add_argument("--workflow", required=True, choices=["manual", "trace2fix"])
    p_stop.add_argument("--incident", required=True)
    p_stop.add_argument("--phase", required=True, choices=["investigation", "resolution"])

    # record
    p_rec = sub.add_parser("record", help="Record final benchmark metrics to results.csv")
    p_rec.add_argument("--workflow", required=True, choices=["manual", "trace2fix"])
    p_rec.add_argument("--incident", required=True)
    p_rec.add_argument("--investigation-time", type=float, default=None,
                       help="Override investigation seconds (uses stopped timer if omitted)")
    p_rec.add_argument("--resolution-time", type=float, default=None,
                       help="Override resolution seconds (uses stopped timer if omitted)")
    p_rec.add_argument("--manual-steps", type=int, default=0)
    p_rec.add_argument("--root-cause-correct", default="unknown")
    p_rec.add_argument("--fix-attempts", type=int, default=0)
    p_rec.add_argument("--regression-test-created", default="no")
    p_rec.add_argument("--verification-completed", type=int, default=0)
    p_rec.add_argument("--verification-total", type=int, default=10)

    # compare
    p_cmp = sub.add_parser("compare", help="Compare manual vs trace2fix for an incident")
    p_cmp.add_argument("--incident", required=True)

    # list
    sub.add_parser("list", help="List all recorded results")

    args = parser.parse_args()
    {
        "start": cmd_start,
        "stop": cmd_stop,
        "record": cmd_record,
        "compare": cmd_compare,
        "list": cmd_list,
    }[args.command](args)


if __name__ == "__main__":
    main()
