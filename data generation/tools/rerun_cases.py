import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from dice.run_itc_two_phase import (
    run_case_tier0,
    run_case_tier1,
    run_case_tier1_alt,
    run_case_tier2,
    ensure_xctrace_ready,
)
from dice.cfg import WORKLOADS, STRESSORS


def parse_case_id(cid: str):
    if "__" not in cid:
        raise ValueError(f"Bad case_id: {cid}")
    w, s = cid.split("__", 1)
    if w not in WORKLOADS:
        raise ValueError(
            f"Bad case_id workload '{w}' in '{cid}'. "
            f"Expected one of: {WORKLOADS}"
        )
    if s not in STRESSORS:
        raise ValueError(
            f"Bad case_id stressor '{s}' in '{cid}'. "
            f"Expected one of: {STRESSORS}. "
            "If you passed a variable with many case IDs, do not wrap it in quotes."
        )
    label = "NOMINAL" if s == "NOMINAL" else "ANOMALY"
    return w, s, label


def normalize_case_args(cases_args):
    """
    Accepts:
      --cases A__B C__D
      --cases "A__B C__D"
      --cases A__B,C__D
    and normalizes into ['A__B', 'C__D'].
    """
    out = []
    seen = set()
    for token in cases_args:
        for piece in token.replace(",", " ").split():
            c = piece.strip()
            if not c or c in seen:
                continue
            out.append(c)
            seen.add(c)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=["tier0", "tier1", "tier1_alt", "tier2"], required=True)
    ap.add_argument("--duration_s", "--duration-s", dest="duration_s", type=int, default=1000)
    ap.add_argument("--out_dir", "--out-dir", dest="out_dir", type=Path, default=REPO_ROOT / "data")
    ap.add_argument("--scripts_dir", "--scripts-dir", dest="scripts_dir", type=Path, default=REPO_ROOT / "scripts")
    ap.add_argument("--tier2_template", "--tier2-template", dest="tier2_template", default="Time Profiler")
    ap.add_argument("--tier1_alt_bin", "--tier1-alt-bin", dest="tier1_alt_bin", default="macmon")
    ap.add_argument("--cases", nargs="+", required=True, help="Case IDs like BROWSER__NOMINAL")
    args = ap.parse_args()

    cases = normalize_case_args(args.cases)
    if not cases:
        raise SystemExit("No valid case IDs provided to --cases.")

    if args.phase == "tier2":
        ensure_xctrace_ready()

    for cid in cases:
        w, s, label = parse_case_id(cid)
        if args.phase == "tier0":
            run_case_tier0(w, s, label, args.duration_s, out_root=args.out_dir)
        elif args.phase == "tier1":
            run_case_tier1(
                w,
                s,
                label,
                args.duration_s,
                out_root=args.out_dir,
                scripts_dir=args.scripts_dir,
            )
        elif args.phase == "tier1_alt":
            run_case_tier1_alt(
                w,
                s,
                label,
                args.duration_s,
                out_root=args.out_dir,
                scripts_dir=args.scripts_dir,
                macmon_bin=args.tier1_alt_bin,
            )
        else:
            run_case_tier2(
                w,
                s,
                label,
                args.duration_s,
                out_root=args.out_dir,
                scripts_dir=args.scripts_dir,
                template=args.tier2_template,
            )


if __name__ == "__main__":
    main()
