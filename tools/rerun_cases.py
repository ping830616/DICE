import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from dice.run_itc_two_phase import run_case_tier0, run_case_tier1, run_case_tier2, ensure_xctrace_ready

def parse_case_id(cid: str):
    if "__" not in cid:
        raise ValueError(f"Bad case_id: {cid}")
    w, s = cid.split("__", 1)
    label = "NOMINAL" if s == "NOMINAL" else "ANOMALY"
    return w, s, label

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=["tier0", "tier1", "tier2"], required=True)
    ap.add_argument("--duration_s", "--duration-s", dest="duration_s", type=int, default=1000)
    ap.add_argument("--out_dir", "--out-dir", dest="out_dir", type=Path, default=REPO_ROOT / "data")
    ap.add_argument("--scripts_dir", "--scripts-dir", dest="scripts_dir", type=Path, default=REPO_ROOT / "scripts")
    ap.add_argument("--tier2_template", "--tier2-template", dest="tier2_template", default="Time Profiler")
    ap.add_argument("--cases", nargs="+", required=True, help="Case IDs like BROWSER__NOMINAL")
    args = ap.parse_args()

    if args.phase == "tier2":
        ensure_xctrace_ready()

    for cid in args.cases:
        w,s,label = parse_case_id(cid)
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
