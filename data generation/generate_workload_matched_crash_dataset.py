#!/usr/bin/env python3
"""Collect a workload-matched crash dataset across the original ITC workloads."""

import argparse
import csv
import importlib.util
import json
import os
import sys
from contextlib import contextmanager
from pathlib import Path
from time import perf_counter

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT / "src"))

WRAPPER_COMPLETION_GRACE_S = 5
SCHEDULE_ENV_KEYS = [
    "DICE_MATCHED_WORKLOAD_CRASH_WARMUP_S",
    "DICE_MATCHED_WORKLOAD_CRASH_RAMP_S",
    "DICE_MATCHED_WORKLOAD_CRASH_HOLD_S",
]
STAGGERED_WORKLOAD_SCHEDULES = {
    "BROWSER": {"warmup_s": 25.0, "ramp_s": 105.0, "hold_s": 30.0},
    "VIDEO_SW": {"warmup_s": 50.0, "ramp_s": 95.0, "hold_s": 25.0},
    "PY_AI": {"warmup_s": 65.0, "ramp_s": 115.0, "hold_s": 30.0},
    "PY_STATS": {"warmup_s": 35.0, "ramp_s": 130.0, "hold_s": 25.0},
}

from dice.cfg import (
    ANOMALOUS_STRESSORS,
    WORKLOADS,
    case_id,
    parse_workload_crash_stressor,
    workload_matched_crash_cases,
)
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


def parse_csv_list(raw: str | None, default: list[str]) -> list[str]:
    if raw is None or not str(raw).strip():
        return list(default)
    values = [item.strip().upper() for item in str(raw).split(",") if item.strip()]
    return values if values else list(default)


def validate_workload_dependencies(workloads: list[str]) -> None:
    missing: list[str] = []
    if "PY_AI" in workloads and importlib.util.find_spec("torch") is None:
        missing.append("torch (required for PY_AI)")
    if missing:
        joined = ", ".join(missing)
        raise RuntimeError(
            "Missing workload dependency: "
            f"{joined}. Install it in the active environment before collecting this dataset."
        )


def print_tier_timing_note(phase: str, duration_s: int, n_cases: int) -> None:
    expected = duration_s * n_cases
    note = f"[DICE workload-crash] {phase}: nominal collection window is about {format_seconds(expected)} for {n_cases} cases"
    if phase == "tier0":
        note += " (+ about 10s once for the Tier-0 schema probe if the schema does not already exist)"
    elif phase == "tier1_alt":
        note += " (+ parsing overhead; fallback to powermetrics can make a failed case take roughly twice as long)"
    elif phase == "tier1":
        note += " (+ parsing overhead and any sudo/powermetrics startup time)"
    elif phase == "tier2":
        note += " (+ trace export overhead after each capture)"
    print(note)


def workload_schedule_for_case(workload: str, args: argparse.Namespace) -> dict[str, float]:
    if args.schedule_profile == "staggered":
        if workload not in STAGGERED_WORKLOAD_SCHEDULES:
            raise ValueError(f"No staggered schedule is defined for workload: {workload}")
        return dict(STAGGERED_WORKLOAD_SCHEDULES[workload])
    return {
        "warmup_s": float(args.warmup_s),
        "ramp_s": float(args.ramp_s),
        "hold_s": float(args.hold_s),
    }


def build_workload_schedule_map(workloads: list[str], args: argparse.Namespace) -> dict[str, dict[str, float]]:
    return {workload: workload_schedule_for_case(workload, args) for workload in workloads}


def schedule_summary(schedule: dict[str, float]) -> str:
    return (
        f"warmup={schedule['warmup_s']:.0f}s "
        f"ramp={schedule['ramp_s']:.0f}s "
        f"hold={schedule['hold_s']:.0f}s "
        f"crash≈{schedule['warmup_s'] + schedule['ramp_s'] + schedule['hold_s']:.0f}s"
    )


def write_case_inventory(out_root: Path, cases, args: argparse.Namespace, schedule_map: dict[str, dict[str, float]]) -> None:
    rows = []
    for case in cases:
        parsed = parse_workload_crash_stressor(case.stressor)
        schedule = dict(schedule_map[case.workload])
        if parsed is None:
            base_stressor = case.stressor
            crash_mode = "NONE"
        else:
            base_stressor, crash_mode = parsed
        rows.append(
            {
                "case_id": case_id(case.workload, case.stressor),
                "workload": case.workload,
                "stressor": case.stressor,
                "base_stressor": base_stressor,
                "crash_mode": crash_mode,
                "label_name": case.label,
                "label": 0 if str(case.label).upper() == "NOMINAL" else 1,
                "warmup_s": float(schedule["warmup_s"]),
                "ramp_s": float(schedule["ramp_s"]),
                "hold_s": float(schedule["hold_s"]),
                "anomaly_onset_target_s": float(schedule["warmup_s"]),
                "crash_target_s": float(schedule["warmup_s"] + schedule["ramp_s"] + schedule["hold_s"]),
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
        "workloads": parse_csv_list(args.workloads, WORKLOADS),
        "stressors": parse_csv_list(args.stressors, ANOMALOUS_STRESSORS),
        "include_nominal": bool(args.include_nominal),
        "schedule_profile": str(args.schedule_profile),
        "wrapper_gui": bool(args.wrapper_gui),
        "wrapper_dry_run": bool(args.wrapper_dry_run),
        "capture_crash_evidence": bool(args.capture_crash_evidence),
        "capture_crash_screenshot": bool(args.capture_crash_screenshot),
        "tier1_alt_bin": str(args.tier1_alt_bin),
        "tier2_template": str(args.tier2_template),
        "workload_schedules": schedule_map,
        "cases": rows,
    }
    (out_root / "workload_crash_collection_config.json").write_text(json.dumps(collection_config, indent=2) + "\n")


def apply_wrapper_env(args: argparse.Namespace) -> None:
    for key in SCHEDULE_ENV_KEYS:
        os.environ.pop(key, None)
    if args.schedule_profile == "uniform":
        env_updates = {
            "DICE_MATCHED_WORKLOAD_CRASH_WARMUP_S": str(float(args.warmup_s)),
            "DICE_MATCHED_WORKLOAD_CRASH_RAMP_S": str(float(args.ramp_s)),
            "DICE_MATCHED_WORKLOAD_CRASH_HOLD_S": str(float(args.hold_s)),
        }
        for key, value in env_updates.items():
            os.environ[key] = value
    if args.wrapper_gui:
        os.environ["DICE_MATCHED_WORKLOAD_CRASH_GUI"] = "1"
    else:
        os.environ.pop("DICE_MATCHED_WORKLOAD_CRASH_GUI", None)
    if args.wrapper_dry_run:
        os.environ["DICE_MATCHED_WORKLOAD_CRASH_DRY_RUN"] = "1"
    else:
        os.environ.pop("DICE_MATCHED_WORKLOAD_CRASH_DRY_RUN", None)


@contextmanager
def case_wrapper_env(case, schedule_map: dict[str, dict[str, float]]) -> None:
    parsed = parse_workload_crash_stressor(case.stressor)
    schedule = dict(schedule_map[case.workload])
    updates = {}
    if parsed is not None:
        base_stressor, mode = parsed
        updates = {
            "DICE_MATCHED_WORKLOAD_CRASH_WORKLOAD": str(case.workload),
            "DICE_MATCHED_WORKLOAD_CRASH_STRESSOR": str(base_stressor),
            "DICE_MATCHED_WORKLOAD_CRASH_MODE": str(mode),
            "DICE_MATCHED_WORKLOAD_CRASH_WARMUP_S": str(float(schedule["warmup_s"])),
            "DICE_MATCHED_WORKLOAD_CRASH_RAMP_S": str(float(schedule["ramp_s"])),
            "DICE_MATCHED_WORKLOAD_CRASH_HOLD_S": str(float(schedule["hold_s"])),
        }
    keys = [
        "DICE_MATCHED_WORKLOAD_CRASH_WORKLOAD",
        "DICE_MATCHED_WORKLOAD_CRASH_STRESSOR",
        "DICE_MATCHED_WORKLOAD_CRASH_MODE",
        *SCHEDULE_ENV_KEYS,
    ]
    old_values = {key: os.environ.get(key) for key in keys}
    try:
        for key in keys:
            os.environ.pop(key, None)
        for key, value in updates.items():
            os.environ[key] = value
        yield
    finally:
        for key, value in old_values.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def run_phase(phase: str, cases, runner, duration_s: int, schedule_map: dict[str, dict[str, float]]) -> None:
    tier_start = perf_counter()
    total = len(cases)
    print(f"[DICE workload-crash] Generating {phase} for {total} cases...")
    print_tier_timing_note(phase, duration_s, total)

    for idx, case in enumerate(cases, start=1):
        cid = case_id(case.workload, case.stressor)
        case_start = perf_counter()
        schedule = dict(schedule_map[case.workload])
        print(f"[DICE workload-crash] [{phase}] {idx}/{total} starting {cid} [{schedule_summary(schedule)}]")
        try:
            with case_wrapper_env(case, schedule_map):
                runner(case)
        except Exception:
            case_elapsed = perf_counter() - case_start
            tier_elapsed = perf_counter() - tier_start
            print(
                f"[DICE workload-crash] [{phase}] {idx}/{total} failed {cid} after {format_seconds(case_elapsed)} "
                f"(tier elapsed {format_seconds(tier_elapsed)})"
            )
            raise

        case_elapsed = perf_counter() - case_start
        tier_elapsed = perf_counter() - tier_start
        avg_case = tier_elapsed / idx
        remaining = avg_case * (total - idx)
        print(
            f"[DICE workload-crash] [{phase}] {idx}/{total} finished {cid} in {format_seconds(case_elapsed)} | "
            f"tier elapsed {format_seconds(tier_elapsed)} | est. remaining {format_seconds(remaining)}"
        )

    print(f"[DICE workload-crash] {phase} complete in {format_seconds(perf_counter() - tier_start)}")


def main() -> None:
    ap = argparse.ArgumentParser(
        description=(
            "Collect workload-matched crash cases across the original DICE workloads. "
            "Each anomaly family gets a *_CONTROL and *_ABORT variant, plus optional NOMINAL controls."
        )
    )
    ap.add_argument("--phase", choices=["tier0", "tier1", "tier1_alt", "tier2", "recommended", "portable"], default="recommended")
    ap.add_argument("--duration_s", "--duration-s", dest="duration_s", type=int, default=240)
    ap.add_argument("--out_dir", "--out-dir", dest="out_dir", type=Path, default=REPO_ROOT / "data_workload_crash_matrix")
    ap.add_argument("--scripts_dir", "--scripts-dir", dest="scripts_dir", type=Path, default=REPO_ROOT / "scripts")
    ap.add_argument("--tier2_template", "--tier2-template", dest="tier2_template", default="Time Profiler")
    ap.add_argument("--tier1_alt_bin", "--tier1-alt-bin", dest="tier1_alt_bin", default="macmon")
    ap.add_argument("--capture_crash_evidence", "--capture-crash-evidence", dest="capture_crash_evidence", action="store_true")
    ap.add_argument("--capture_crash_screenshot", "--capture-crash-screenshot", dest="capture_crash_screenshot", action="store_true")
    ap.add_argument("--crash_log_grace_s", "--crash-log-grace-s", dest="crash_log_grace_s", type=int, default=60)
    ap.add_argument("--workloads", default=",".join(WORKLOADS))
    ap.add_argument("--stressors", default=",".join(ANOMALOUS_STRESSORS))
    ap.add_argument("--include_nominal", "--include-nominal", dest="include_nominal", action=argparse.BooleanOptionalAction, default=True)
    ap.add_argument(
        "--schedule_profile",
        "--schedule-profile",
        dest="schedule_profile",
        choices=["uniform", "staggered"],
        default="uniform",
        help=(
            "Wrapper timing profile. 'uniform' uses the global warmup/ramp/hold values for every workload; "
            "'staggered' uses workload-specific schedules so anomaly onset and crash targets differ by workload."
        ),
    )
    ap.add_argument("--warmup_s", "--warmup-s", dest="warmup_s", type=float, default=45.0)
    ap.add_argument("--ramp_s", "--ramp-s", dest="ramp_s", type=float, default=120.0)
    ap.add_argument("--hold_s", "--hold-s", dest="hold_s", type=float, default=45.0)
    ap.add_argument("--wrapper_gui", "--wrapper-gui", dest="wrapper_gui", action="store_true")
    ap.add_argument("--wrapper_dry_run", "--wrapper-dry-run", dest="wrapper_dry_run", action="store_true")
    args = ap.parse_args()

    workloads = parse_csv_list(args.workloads, WORKLOADS)
    stressors = parse_csv_list(args.stressors, ANOMALOUS_STRESSORS)
    invalid_workloads = [item for item in workloads if item not in WORKLOADS]
    invalid_stressors = [item for item in stressors if item not in ANOMALOUS_STRESSORS]
    if invalid_workloads:
        raise ValueError(f"Unknown workloads: {invalid_workloads}")
    if invalid_stressors:
        raise ValueError(f"Unknown stressors: {invalid_stressors}")
    validate_workload_dependencies(workloads)

    schedule_map = build_workload_schedule_map(workloads, args)
    max_schedule_s = max(
        schedule["warmup_s"] + schedule["ramp_s"] + schedule["hold_s"]
        for schedule in schedule_map.values()
    )
    min_duration = int(round(max_schedule_s + WRAPPER_COMPLETION_GRACE_S))
    if args.duration_s < min_duration:
        raise ValueError(
            "duration_s is too short for the requested workload-crash schedule. "
            f"Set duration_s to at least {min_duration}s for the selected workloads and schedule profile."
        )

    apply_wrapper_env(args)

    out_root = Path(args.out_dir)
    scripts_dir = Path(args.scripts_dir)
    for subdir in ["tier0", "tier1", "tier1_alt", "tier2", "meta", "logs"]:
        mkdirp(out_root / subdir)

    cases = workload_matched_crash_cases(workloads=workloads, stressors=stressors, include_nominal=args.include_nominal)
    write_case_inventory(out_root, cases, args, schedule_map)

    print("[DICE workload-crash] Cases:")
    for case in cases:
        print(f"  - {case_id(case.workload, case.stressor)} ({case.label})")
    print(f"[DICE workload-crash] Schedule profile: {args.schedule_profile}")
    for workload in workloads:
        print(f"[DICE workload-crash]   {workload}: {schedule_summary(schedule_map[workload])}")

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
            schedule_map,
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
            schedule_map,
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
            schedule_map,
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
                schedule_map,
            )
        elif can_run_tier1():
            print("[DICE workload-crash] portable mode: macmon is unavailable; falling back to legacy Tier-1 powermetrics collection.")
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
                schedule_map,
            )
        else:
            print("[DICE workload-crash] portable mode: skipping Tier-1 because neither macmon nor powermetrics is available on this machine.")

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
            schedule_map,
        )
    elif args.phase == "portable":
        if can_run_tier2():
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
                schedule_map,
            )
        else:
            print("[DICE workload-crash] portable mode: skipping Tier-2 because xctrace is unavailable on this machine.")

    print(f"[DICE workload-crash] Done. Output root: {out_root}")


if __name__ == "__main__":
    main()
