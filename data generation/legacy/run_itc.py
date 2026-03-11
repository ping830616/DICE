import argparse, json, time, threading, subprocess, platform
from pathlib import Path

from cfg import WORKLOADS, STRESSORS, HZ, SEED
from workloads import run_workload, run_stressor
from tier0_collect import collect_tier0_5hz
from powermetrics_parse import parse_powermetrics_to_csv

OUT = Path("/Users/hsiaopingni/ITC_2026_M2Pro_DATA")
CODE = Path("/Users/hsiaopingni/ITC_2026_M2Pro_CODE")

def mkdirp(p: Path): 
    p.mkdir(parents=True, exist_ok=True)

def make_run_id(workload: str, stressor: str) -> str:
    return f"{time.strftime('%Y%m%d_%H%M%S')}__{workload}__{stressor}"

def append_manifest(row: dict):
    import csv
    mf = OUT / "manifest.csv"
    exists = mf.exists()
    with mf.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(row.keys()))
        if not exists:
            w.writeheader()
        w.writerow(row)

def run_one(workload: str, stressor: str, duration_s: int):
    label = "NOMINAL" if stressor == "NOMINAL" else "ANOMALY"
    rid = make_run_id(workload, stressor)

    t0 = OUT / "tier0" / rid
    t1 = OUT / "tier1" / rid
    meta_dir = OUT / "meta" / rid
    logs = OUT / "logs" / rid
    for d in [t0, t1, meta_dir, logs]:
        mkdirp(d)

    meta = {
        "run_id": rid,
        "workload": workload,
        "stressor": stressor,
        "label": label,
        "duration_s": duration_s,
        "hz": HZ,
        "seed": SEED,
        "platform": platform.platform(),
        "ai_mode": "numpy+torch(mps if available)",
        "video_mode": "software pipeline (no external files)",
    }

    # Workload + stressor threads
    stop_evt = threading.Event()
    th_w = threading.Thread(target=run_workload, args=(workload, stop_evt), daemon=True)
    th_s = threading.Thread(target=run_stressor, args=(stressor, stop_evt), daemon=True)
    th_w.start()
    th_s.start()

    # Tier-1 powermetrics capture (exact N samples)
    samples_target = HZ * duration_s
    raw_plistnul = t1 / "powermetrics_raw.plistnul"
    cmd_t1 = ["bash", str(CODE / "03_powermetrics_collect_5hz.sh"), str(raw_plistnul), str(samples_target), "200"]
    with (logs / "tier1_collect.log").open("w") as lf:
        p1 = subprocess.Popen(cmd_t1, stdout=lf, stderr=subprocess.STDOUT)

    # Tier-0 capture
    tier0_csv = t0 / "tier0_5hz.csv"
    collect_tier0_5hz(str(tier0_csv), hz=HZ, duration_s=duration_s)

    # Stop workload/stressor
    stop_evt.set()
    th_w.join(timeout=3)
    th_s.join(timeout=3)

    # Wait powermetrics
    p1.wait(timeout=600)

    # Parse Tier-1 into exact row count
    tier1_csv = t1 / "tier1_5hz.csv"
    parse_powermetrics_to_csv(str(raw_plistnul), str(tier1_csv), samples_target=samples_target)

    (meta_dir / "meta.json").write_text(json.dumps(meta, indent=2))

    append_manifest({
        "run_id": rid,
        "workload": workload,
        "stressor": stressor,
        "label": label,
        "duration_s": duration_s,
        "tier0_csv": str(tier0_csv),
        "tier1_csv": str(tier1_csv),
        "tier1_raw": str(raw_plistnul),
        "meta_json": str(meta_dir / "meta.json"),
    })

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["single", "all"], default="all")
    ap.add_argument("--workload", choices=WORKLOADS, default="PY_AI")
    ap.add_argument("--stressor", choices=STRESSORS, default="NOMINAL")
    ap.add_argument("--duration_s", type=int, default=20)
    args = ap.parse_args()

    mkdirp(OUT / "tier0")
    mkdirp(OUT / "tier1")
    mkdirp(OUT / "meta")
    mkdirp(OUT / "logs")

    if args.mode == "single":
        run_one(args.workload, args.stressor, args.duration_s)
    else:
        for w in WORKLOADS:
            for s in STRESSORS:
                run_one(w, s, args.duration_s)

if __name__ == "__main__":
    main()
