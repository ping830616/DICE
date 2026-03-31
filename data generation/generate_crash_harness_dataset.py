#!/usr/bin/env python3
"""Collect a small crash-harness dataset with the normal DICE tier collectors."""

import argparse
import csv
import json
import os
import sys
from pathlib import Path
from time import perf_counter

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from dice.cfg import crash_harness_cases, case_id
from dice.run_itc_two_phase import (
    can_run_tier1,
    can_run_tier1_alt,
    can_run_tier2,
    ensure_xctrace_ready,
    run_case_tier0,
    run_case_tier1,
    run_case_tier1_alt,
    run_case_tier2,
)


def mkdirp(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def format_seconds(seconds: float) -> str:
    total = int(round(max(seconds, 0.0)))
    hours, rem = divmod(total, 3600)
    minutes, secs = divmod(rem, 60)
    if hours:
        return f"{hours:d}h {minutes:02d}m {secs:02d}s"
    if minutes:
        return f"{minutes:d}m {secs:02d}s"
    return f"{secs:d}s"


def print_tier_timing_note(phase: str, duration_s: int, n_cases: int) -> None:
    expected = duration_s * n_cases
    note = f"[DICE crash-harness] {phase}: nominal collection window is about {format_seconds(expected)} for {n_cases} cases"
    if phase == "tier0":
        note += " (+ about 10s once for the Tier-0 schema probe if the schema does not already exist)"
    elif phase == "tier1_alt":
        note += " (+ parsing overhead; fallback to powermetrics can make a failed case take roughly twice as long)"
    elif phase == "tier1":
        note += " (+ parsing overhead and any sudo/powermetrics startup time)"
    elif phase == "tier2":
        note += " (+ trace export overhead after each capture)"
    print(note)


def write_case_inventory(out_root: Path, cases, args: argparse.Namespace) -> None:
    rows = []
    for case in cases:
        rows.append(
            {
                "case_id": case_id(case.workload, case.stressor),
                "workload": case.workload,
                "stressor": case.stressor,
                "label_name": case.label,
                "label": 0 if str(case.label).upper() == "NOMINAL" else 1,
            }
        )

    inventory_path = out_root / "case_inventory.csv"
    with inventory_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    collection_config = {
        "phase": args.phase,
        "duration_s": int(args.duration_s),
        "warmup_s": float(args.warmup_s),
        "ramp_s": float(args.ramp_s),
        "hold_s": float(args.hold_s),
        "memory_step_mb": int(args.memory_step_mb),
        "max_memory_mb": int(args.max_memory_mb),
        "cpu_threads": int(args.cpu_threads),
        "cpu_duty_min": float(args.cpu_duty_min),
        "cpu_duty_max": float(args.cpu_duty_max),
        "harness_gui": bool(args.harness_gui),
        "capture_crash_evidence": bool(args.capture_crash_evidence),
        "capture_crash_screenshot": bool(args.capture_crash_screenshot),
        "tier1_alt_bin": str(args.tier1_alt_bin),
        "tier2_template": str(args.tier2_template),
        "cases": rows,
    }
    (out_root / "crash_harness_collection_config.json").write_text(json.dumps(collection_config, indent=2) + "\n")


def run_phase(phase: str, cases, runner, duration_s: int) -> None:
    tier_start = perf_counter()
    total = len(cases)
    print(f"[DICE crash-harness] Generating {phase} for {total} cases...")
    print_tier_timing_note(phase, duration_s, total)

    for idx, case in enumerate(cases, start=1):
        cid = case_id(case.workload, case.stressor)
        case_start = perf_counter()
        print(f"[DICE crash-harness] [{phase}] {idx}/{total} starting {cid}")
        try:
            runner(case)
        except Exception:
            case_elapsed = perf_counter() - case_start
            tier_elapsed = perf_counter() - tier_start
            print(
                f"[DICE crash-harness] [{phase}] {idx}/{total} failed {cid} after {format_seconds(case_elapsed)} "
                f"(tier elapsed {format_seconds(tier_elapsed)})"
            )
            raise

        case_elapsed = perf_counter() - case_start
        tier_elapsed = perf_counter() - tier_start
        avg_case = tier_elapsed / idx
        remaining = avg_case * (total - idx)
        print(
            f"[DICE crash-harness] [{phase}] {idx}/{total} finished {cid} in {format_seconds(case_elapsed)} | "
            f"tier elapsed {format_seconds(tier_elapsed)} | est. remaining {format_seconds(remaining)}"
        )

    print(f"[DICE crash-harness] {phase} complete in {format_seconds(perf_counter() - tier_start)}")


def apply_harness_env(args: argparse.Namespace) -> None:
    env_updates = {
        "DICE_CRASH_WARMUP_S": str(float(args.warmup_s)),
        "DICE_CRASH_RAMP_S": str(float(args.ramp_s)),
        "DICE_CRASH_HOLD_S": str(float(args.hold_s)),
        "DICE_CRASH_MEMORY_STEP_MB": str(int(args.memory_step_mb)),
        "DICE_CRASH_MAX_MEMORY_MB": str(int(args.max_memory_mb)),
        "DICE_CRASH_CPU_THREADS": str(int(args.cpu_threads)),
        "DICE_CRASH_CPU_DUTY_MIN": str(float(args.cpu_duty_min)),
        "DICE_CRASH_CPU_DUTY_MAX": str(float(args.cpu_duty_max)),
    }
    for key, value in env_updates.items():
        os.environ[key] = value
    if args.harness_gui:
        os.environ["DICE_CRASH_HARNESS_GUI"] = "1"
    else:
        os.environ.pop("DICE_CRASH_HARNESS_GUI", None)


def main() -> None:
    ap = argparse.ArgumentParser(
        description=(
            "Collect a small, controlled user-space crash-harness dataset with the standard DICE tier collectors. "
            "Collection happens in the terminal; the notebook is used later for analysis."
        )
    )
    ap.add_argument("--phase", choices=["tier0", "tier1", "tier1_alt", "tier2", "recommended", "portable"], default="recommended")
    ap.add_argument("--duration_s", "--duration-s", dest="duration_s", type=int, default=300)
    ap.add_argument("--out_dir", "--out-dir", dest="out_dir", type=Path, default=REPO_ROOT / "data_crash_harness")
    ap.add_argument("--scripts_dir", "--scripts-dir", dest="scripts_dir", type=Path, default=REPO_ROOT / "scripts")
    ap.add_argument("--tier2_template", "--tier2-template", dest="tier2_template", default="Time Profiler")
    ap.add_argument("--tier1_alt_bin", "--tier1-alt-bin", dest="tier1_alt_bin", default="macmon")
    ap.add_argument("--capture_crash_evidence", "--capture-crash-evidence", dest="capture_crash_evidence", action="store_true")
    ap.add_argument("--capture_crash_screenshot", "--capture-crash-screenshot", dest="capture_crash_screenshot", action="store_true")
    ap.add_argument("--crash_log_grace_s", "--crash-log-grace-s", dest="crash_log_grace_s", type=int, default=60)
    ap.add_argument("--warmup_s", "--warmup-s", dest="warmup_s", type=float, default=45.0)
    ap.add_argument("--ramp_s", "--ramp-s", dest="ramp_s", type=float, default=120.0)
    ap.add_argument("--hold_s", "--hold-s", dest="hold_s", type=float, default=45.0)
    ap.add_argument("--memory_step_mb", "--memory-step-mb", dest="memory_step_mb", type=int, default=32)
    ap.add_argument("--max_memory_mb", "--max-memory-mb", dest="max_memory_mb", type=int, default=768)
    ap.add_argument("--cpu_threads", "--cpu-threads", dest="cpu_threads", type=int, default=2)
    ap.add_argument("--cpu_duty_min", "--cpu-duty-min", dest="cpu_duty_min", type=float, default=0.20)
    ap.add_argument("--cpu_duty_max", "--cpu-duty-max", dest="cpu_duty_max", type=float, default=0.92)
    ap.add_argument("--harness_gui", "--harness-gui", dest="harness_gui", action="store_true")
    args = ap.parse_args()

    if args.duration_s < int(round(args.warmup_s + args.ramp_s + args.hold_s)):
        raise ValueError(
            "duration_s is too short for the requested crash-harness schedule. "
            "Set duration_s to at least warmup_s + ramp_s + hold_s."
        )

    apply_harness_env(args)

    out_root = Path(args.out_dir)
    scripts_dir = Path(args.scripts_dir)
    for subdir in ["tier0", "tier1", "tier1_alt", "tier2", "meta", "logs"]:
        mkdirp(out_root / subdir)

    cases = crash_harness_cases()
    write_case_inventory(out_root, cases, args)
    print("[DICE crash-harness] Cases:")
    for case in cases:
        print(f"  - {case_id(case.workload, case.stressor)} ({case.label})")

    if args.phase in ("tier0", "recommended", "portable"):
        run_phase(
            "tier0",
            cases,
            lambda case: run_case_tier0(
                case.workload,
                case.stressor,
                case.label,
                args.duration_s,
                out_root=out_root,
                capture_crash_evidence=args.capture_crash_evidence,
                crash_log_grace_s=args.crash_log_grace_s,
                capture_crash_screenshot=args.capture_crash_screenshot,
            ),
            args.duration_s,
        )

    if args.phase in ("tier1",):
        run_phase(
            "tier1",
            cases,
            lambda case: run_case_tier1(
                case.workload,
                case.stressor,
                case.label,
                args.duration_s,
                out_root=out_root,
                scripts_dir=scripts_dir,
                capture_crash_evidence=args.capture_crash_evidence,
                crash_log_grace_s=args.crash_log_grace_s,
                capture_crash_screenshot=args.capture_crash_screenshot,
            ),
            args.duration_s,
        )

    if args.phase in ("tier1_alt", "recommended"):
        run_phase(
            "tier1_alt",
            cases,
            lambda case: run_case_tier1_alt(
                case.workload,
                case.stressor,
                case.label,
                args.duration_s,
                out_root=out_root,
                scripts_dir=scripts_dir,
                macmon_bin=args.tier1_alt_bin,
                capture_crash_evidence=args.capture_crash_evidence,
                crash_log_grace_s=args.crash_log_grace_s,
                capture_crash_screenshot=args.capture_crash_screenshot,
            ),
            args.duration_s,
        )
    elif args.phase == "portable":
        if can_run_tier1_alt(args.tier1_alt_bin):
            run_phase(
                "tier1_alt",
                cases,
                lambda case: run_case_tier1_alt(
                    case.workload,
                    case.stressor,
                    case.label,
                    args.duration_s,
                    out_root=out_root,
                    scripts_dir=scripts_dir,
                    macmon_bin=args.tier1_alt_bin,
                    capture_crash_evidence=args.capture_crash_evidence,
                    crash_log_grace_s=args.crash_log_grace_s,
                    capture_crash_screenshot=args.capture_crash_screenshot,
                ),
                args.duration_s,
            )
        elif can_run_tier1():
            print("[DICE crash-harness] portable mode: macmon is unavailable; falling back to legacy Tier-1 powermetrics collection.")
            run_phase(
                "tier1",
                cases,
                lambda case: run_case_tier1(
                    case.workload,
                    case.stressor,
                    case.label,
                    args.duration_s,
                    out_root=out_root,
                    scripts_dir=scripts_dir,
                    capture_crash_evidence=args.capture_crash_evidence,
                    crash_log_grace_s=args.crash_log_grace_s,
                    capture_crash_screenshot=args.capture_crash_screenshot,
                ),
                args.duration_s,
            )
        else:
            print("[DICE crash-harness] portable mode: skipping Tier-1 because neither macmon nor powermetrics is available on this machine.")

    if args.phase in ("tier2", "recommended"):
        ensure_xctrace_ready()
        run_phase(
            "tier2",
            cases,
            lambda case: run_case_tier2(
                case.workload,
                case.stressor,
                case.label,
                args.duration_s,
                out_root=out_root,
                scripts_dir=scripts_dir,
                template=args.tier2_template,
                capture_crash_evidence=args.capture_crash_evidence,
                crash_log_grace_s=args.crash_log_grace_s,
                capture_crash_screenshot=args.capture_crash_screenshot,
            ),
            args.duration_s,
        )
    elif args.phase == "portable":
        if can_run_tier2():
            ensure_xctrace_ready()
            run_phase(
                "tier2",
                cases,
                lambda case: run_case_tier2(
                    case.workload,
                    case.stressor,
                    case.label,
                    args.duration_s,
                    out_root=out_root,
                    scripts_dir=scripts_dir,
                    template=args.tier2_template,
                    capture_crash_evidence=args.capture_crash_evidence,
                    crash_log_grace_s=args.crash_log_grace_s,
                    capture_crash_screenshot=args.capture_crash_screenshot,
                ),
                args.duration_s,
            )
        else:
            print("[DICE crash-harness] portable mode: skipping Tier-2 because xctrace is unavailable on this machine.")


if __name__ == "__main__":
    main()
