from pathlib import Path
import argparse
import csv

REPO_ROOT = Path(__file__).resolve().parents[1]

def count_lines(p: Path) -> int:
    with p.open("rb") as f:
        return sum(1 for _ in f)

def rebuild_manifest_tier0(root: Path):
    t0 = root / "tier0"
    out = root / "manifest_tier0.csv"
    rows = []
    for case_dir in sorted([p for p in t0.iterdir() if p.is_dir()]):
        f0 = case_dir / "tier0_full_5hz.csv"
        rows.append({
            "case_id": case_dir.name,
            "tier0_csv": str(f0) if f0.exists() else "",
            "lines": count_lines(f0) if f0.exists() else 0,
        })
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["case_id","tier0_csv","lines"])
        w.writeheader()
        w.writerows(rows)

def rebuild_manifest_tier1(root: Path):
    t1 = root / "tier1"
    out = root / "manifest_tier1.csv"
    rows = []
    for case_dir in sorted([p for p in t1.iterdir() if p.is_dir()]):
        core = case_dir / "tier1_core_5hz.csv"
        full = case_dir / "tier1_full_5hz.csv"
        raw  = case_dir / "powermetrics_raw.txt"
        rows.append({
            "case_id": case_dir.name,
            "tier1_core_csv": str(core) if core.exists() else "",
            "tier1_full_csv": str(full) if full.exists() else "",
            "tier1_raw_txt": str(raw) if raw.exists() else "",
            "core_lines": count_lines(core) if core.exists() else 0,
            "full_lines": count_lines(full) if full.exists() else 0,
            "raw_bytes": raw.stat().st_size if raw.exists() else 0,
        })
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["case_id","tier1_core_csv","tier1_full_csv","tier1_raw_txt","core_lines","full_lines","raw_bytes"])
        w.writeheader()
        w.writerows(rows)

def rebuild_manifest_tier2(root: Path):
    t2 = root / "tier2"
    out = root / "manifest_tier2.csv"
    rows = []
    for case_dir in sorted([p for p in t2.iterdir() if p.is_dir()]):
        core = case_dir / "tier2_core_5hz.csv"
        full = case_dir / "tier2_full_5hz.csv"
        trace = case_dir / "xctrace.trace"
        raw = case_dir / "xctrace_export.xml"
        rows.append({
            "case_id": case_dir.name,
            "tier2_core_csv": str(core) if core.exists() else "",
            "tier2_full_csv": str(full) if full.exists() else "",
            "tier2_trace": str(trace) if trace.exists() else "",
            "tier2_raw_export": str(raw) if raw.exists() else "",
            "core_lines": count_lines(core) if core.exists() else 0,
            "full_lines": count_lines(full) if full.exists() else 0,
            "raw_bytes": raw.stat().st_size if raw.exists() else 0,
        })
    with out.open("w", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "case_id",
                "tier2_core_csv",
                "tier2_full_csv",
                "tier2_trace",
                "tier2_raw_export",
                "core_lines",
                "full_lines",
                "raw_bytes",
            ],
        )
        w.writeheader()
        w.writerows(rows)

def find_bad_tier0(root: Path, expected_lines: int):
    t0 = root / "tier0"
    bad = []
    for case_dir in sorted([p for p in t0.iterdir() if p.is_dir()]):
        f0 = case_dir / "tier0_full_5hz.csv"
        if not f0.exists():
            bad.append(case_dir.name); continue
        if count_lines(f0) != expected_lines:
            bad.append(case_dir.name)
    return bad

def find_bad_tier1(root: Path, core_required=("cpu_power_w","processor_power_w","cpu_avg_freq_mhz","gpu_avg_freq_mhz")):
    import pandas as pd
    t1 = root / "tier1"
    bad = []
    for case_dir in sorted([p for p in t1.iterdir() if p.is_dir()]):
        core = case_dir / "tier1_core_5hz.csv"
        raw  = case_dir / "powermetrics_raw.txt"
        if not core.exists() or not raw.exists():
            bad.append(case_dir.name); continue
        if raw.stat().st_size < 5000:  # too small to contain 5000 samples
            bad.append(case_dir.name); continue
        try:
            df = pd.read_csv(core)
        except Exception:
            bad.append(case_dir.name); continue
        for c in core_required:
            if c in df.columns and df[c].notna().sum() == 0:
                bad.append(case_dir.name)
                break
    return sorted(set(bad))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=REPO_ROOT / "data")
    ap.add_argument("--expected_lines", "--expected-lines", dest="expected_lines", type=int, default=5001)
    args = ap.parse_args()

    t0 = args.root / "tier0"
    t1 = args.root / "tier1"
    t2 = args.root / "tier2"
    if not t0.exists() or not t1.exists():
        print("Tier folders not found. Expected:", t0, t1)
        return

    rebuild_manifest_tier0(args.root)
    rebuild_manifest_tier1(args.root)
    if t2.exists():
        rebuild_manifest_tier2(args.root)

    bad0 = find_bad_tier0(args.root, args.expected_lines)
    bad1 = find_bad_tier1(args.root)

    print("Rebuilt manifests ✅")
    print("Bad Tier-0 cases:", len(bad0), bad0[:20], ("..." if len(bad0)>20 else ""))
    print("Bad Tier-1 cases:", len(bad1), bad1[:20], ("..." if len(bad1)>20 else ""))
    if t2.exists():
        print("Tier-2 manifest rebuilt.")

if __name__ == "__main__":
    main()
