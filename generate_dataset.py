#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from dice.cfg import all_cases
from dice.run_itc_two_phase import run_case_tier0, run_case_tier1, run_case_tier2, ensure_xctrace_ready


def mkdirp(p: Path):
    p.mkdir(parents=True, exist_ok=True)


def main():
    ap = argparse.ArgumentParser(description="Generate ITC dataset across Tier-0/Tier-1/Tier-2 phases.")
    ap.add_argument("--phase", choices=["tier0", "tier1", "tier2", "both", "all"], default="both")
    ap.add_argument("--duration_s", "--duration-s", dest="duration_s", type=int, default=1000)
    ap.add_argument("--out_dir", "--out-dir", dest="out_dir", type=Path, default=REPO_ROOT / "data")
    ap.add_argument("--scripts_dir", "--scripts-dir", dest="scripts_dir", type=Path, default=REPO_ROOT / "scripts")
    ap.add_argument("--tier2_template", "--tier2-template", dest="tier2_template", default="Time Profiler")
    args = ap.parse_args()

    out_root = Path(args.out_dir)
    scripts_dir = Path(args.scripts_dir)
    mkdirp(out_root / "tier0")
    mkdirp(out_root / "tier1")
    mkdirp(out_root / "tier2")
    mkdirp(out_root / "meta")
    mkdirp(out_root / "logs")

    cases = all_cases()

    if args.phase in ("tier0", "both", "all"):
        print(f"[DICE] Generating Tier-0 for {len(cases)} cases...")
        for c in cases:
            run_case_tier0(
                c.workload,
                c.stressor,
                c.label,
                args.duration_s,
                out_root=out_root,
            )

    if args.phase in ("tier1", "both", "all"):
        print(f"[DICE] Generating Tier-1 for {len(cases)} cases...")
        for c in cases:
            run_case_tier1(
                c.workload,
                c.stressor,
                c.label,
                args.duration_s,
                out_root=out_root,
                scripts_dir=scripts_dir,
            )

    if args.phase in ("tier2", "all"):
        ensure_xctrace_ready()
        print(f"[DICE] Generating Tier-2 for {len(cases)} cases...")
        for c in cases:
            run_case_tier2(
                c.workload,
                c.stressor,
                c.label,
                args.duration_s,
                out_root=out_root,
                scripts_dir=scripts_dir,
                template=args.tier2_template,
            )

    print(f"[DICE] Done. Output root: {out_root}")


if __name__ == "__main__":
    main()
