import argparse
import json
import platform
import subprocess
import threading
from pathlib import Path
from typing import Optional

from .cfg import all_cases, case_id, HZ, SEED, TIER2_DEFAULT_TEMPLATE
from .workloads import run_workload, run_stressor
from .tier0_collect_schema import build_and_save_global_schema, load_schema, collect_with_schema
from .powermetrics_parse_full import build_global_schema as build_tier1_global_schema, parse_with_schema as parse_tier1_with_schema
from .tier2_xctrace_parse import build_global_schema as build_tier2_global_schema, parse_with_schema as parse_tier2_with_schema

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT = REPO_ROOT / "data"
DEFAULT_SCRIPTS = REPO_ROOT / "scripts"


def mkdirp(p: Path):
    p.mkdir(parents=True, exist_ok=True)

def append_manifest(manifest_path: Path, row: dict):
    import csv
    exists = manifest_path.exists()
    with manifest_path.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(row.keys()))
        if not exists: w.writeheader()
        w.writerow(row)


def ensure_xctrace_ready():
    p = subprocess.run(
        ["xcrun", "xctrace", "version"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if p.returncode == 0:
        return

    msg = (p.stderr or p.stdout or "").strip()
    if not msg:
        msg = "xctrace invocation failed."
    raise RuntimeError(
        "Tier-2 requires xctrace to be available and licensed. "
        f"Current error: {msg}"
    )


def run_case_tier0(
    w: str,
    s: str,
    label: str,
    duration_s: int,
    out_root: Path = DEFAULT_OUT,
    tier0_schema_path: Optional[Path] = None,
):
    out_root = Path(out_root)
    tier0_schema = Path(tier0_schema_path) if tier0_schema_path else out_root / "tier0_schema_global.json"
    cid = case_id(w, s)
    out_dir = out_root / "tier0" / cid
    meta_dir = out_root / "meta" / cid
    logs = out_root / "logs" / cid
    for d in [out_dir, meta_dir, logs]: mkdirp(d)

    # ensure tier0 schema exists
    if not tier0_schema.exists():
        schema = build_and_save_global_schema(str(tier0_schema), hz=HZ, probe_s=10)
    else:
        schema = load_schema(str(tier0_schema))

    meta = {
        "case_id": cid, "workload": w, "stressor": s, "label": label,
        "duration_s": duration_s, "hz": HZ, "seed": SEED,
        "platform": platform.platform(), "phase": "tier0",
        "tier0_schema": str(tier0_schema),
    }

    stop_evt = threading.Event()
    th_w = threading.Thread(target=run_workload, args=(w, stop_evt), daemon=True)
    th_s = threading.Thread(target=run_stressor, args=(s, stop_evt), daemon=True)
    th_w.start(); th_s.start()

    out_csv = out_dir / "tier0_full_5hz.csv"
    collect_with_schema(str(out_csv), hz=HZ, duration_s=duration_s, schema=schema)

    stop_evt.set()
    th_w.join(timeout=3); th_s.join(timeout=3)

    meta_path = meta_dir / "meta_tier0.json"
    meta_path.write_text(json.dumps(meta, indent=2))
    append_manifest(out_root / "manifest_tier0.csv", {
        "case_id": cid, "workload": w, "stressor": s, "label": label,
        "duration_s": duration_s, "tier0_csv": str(out_csv),
        "tier0_schema": str(tier0_schema), "meta_json": str(meta_path),
    })


def run_case_tier1(
    w: str,
    s: str,
    label: str,
    duration_s: int,
    out_root: Path = DEFAULT_OUT,
    scripts_dir: Path = DEFAULT_SCRIPTS,
    tier1_schema_path: Optional[Path] = None,
):
    out_root = Path(out_root)
    scripts_dir = Path(scripts_dir)
    tier1_schema = Path(tier1_schema_path) if tier1_schema_path else out_root / "tier1_schema_global.json"
    powermetrics_script = scripts_dir / "03_powermetrics_collect_5hz.sh"
    if not powermetrics_script.exists():
        raise FileNotFoundError(f"Missing powermetrics script: {powermetrics_script}")

    cid = case_id(w, s)
    out_dir = out_root / "tier1" / cid
    meta_dir = out_root / "meta" / cid
    logs = out_root / "logs" / cid
    for d in [out_dir, meta_dir, logs]: mkdirp(d)

    samples_target = HZ * duration_s
    raw_txt = out_dir / "powermetrics_raw.txt"

    meta = {
        "case_id": cid, "workload": w, "stressor": s, "label": label,
        "duration_s": duration_s, "hz": HZ, "seed": SEED,
        "platform": platform.platform(), "phase": "tier1",
        "tier1_schema": str(tier1_schema),
    }

    stop_evt = threading.Event()
    th_w = threading.Thread(target=run_workload, args=(w, stop_evt), daemon=True)
    th_s = threading.Thread(target=run_stressor, args=(s, stop_evt), daemon=True)
    th_w.start(); th_s.start()

    cmd = ["bash", str(powermetrics_script), str(raw_txt), str(samples_target), "200"]
    with (logs / "tier1_collect.log").open("w") as lf:
        p = subprocess.Popen(cmd, stdout=lf, stderr=subprocess.STDOUT)

    try:
        p.wait(timeout=duration_s + 240)
    except subprocess.TimeoutExpired:
        try:
            p.terminate(); p.wait(timeout=10)
        except Exception:
            try: p.kill()
            except Exception: pass

    stop_evt.set()
    th_w.join(timeout=3); th_s.join(timeout=3)

    # build tier1 schema once
    if not tier1_schema.exists():
        build_tier1_global_schema(str(raw_txt), str(tier1_schema), max_keys=250)

    out_core = out_dir / "tier1_core_5hz.csv"
    out_full = out_dir / "tier1_full_5hz.csv"
    parse_tier1_with_schema(str(raw_txt), str(out_core), str(out_full), str(tier1_schema), samples_target=samples_target)

    meta_path = meta_dir / "meta_tier1.json"
    meta_path.write_text(json.dumps(meta, indent=2))
    append_manifest(out_root / "manifest_tier1.csv", {
        "case_id": cid, "workload": w, "stressor": s, "label": label,
        "duration_s": duration_s,
        "tier1_core_csv": str(out_core), "tier1_full_csv": str(out_full),
        "tier1_raw_txt": str(raw_txt),
        "tier1_schema": str(tier1_schema),
        "meta_json": str(meta_path),
    })


def run_case_tier2(
    w: str,
    s: str,
    label: str,
    duration_s: int,
    out_root: Path = DEFAULT_OUT,
    scripts_dir: Path = DEFAULT_SCRIPTS,
    tier2_schema_path: Optional[Path] = None,
    template: str = TIER2_DEFAULT_TEMPLATE,
):
    out_root = Path(out_root)
    scripts_dir = Path(scripts_dir)
    tier2_schema = Path(tier2_schema_path) if tier2_schema_path else out_root / "tier2_schema_global.json"
    xctrace_script = scripts_dir / "05_xctrace_record_export.sh"
    if not xctrace_script.exists():
        raise FileNotFoundError(f"Missing xctrace script: {xctrace_script}")

    cid = case_id(w, s)
    out_dir = out_root / "tier2" / cid
    meta_dir = out_root / "meta" / cid
    logs = out_root / "logs" / cid
    for d in [out_dir, meta_dir, logs]:
        mkdirp(d)

    samples_target = HZ * duration_s
    trace_out = out_dir / "xctrace.trace"
    raw_export = out_dir / "xctrace_export.xml"

    meta = {
        "case_id": cid,
        "workload": w,
        "stressor": s,
        "label": label,
        "duration_s": duration_s,
        "hz": HZ,
        "seed": SEED,
        "platform": platform.platform(),
        "phase": "tier2",
        "tier2_schema": str(tier2_schema),
        "xctrace_template": template,
    }

    stop_evt = threading.Event()
    th_w = threading.Thread(target=run_workload, args=(w, stop_evt), daemon=True)
    th_s = threading.Thread(target=run_stressor, args=(s, stop_evt), daemon=True)
    th_w.start()
    th_s.start()

    cmd = ["bash", str(xctrace_script), str(duration_s), str(trace_out), str(raw_export), str(template)]
    with (logs / "tier2_collect.log").open("w") as lf:
        p = subprocess.Popen(cmd, stdout=lf, stderr=subprocess.STDOUT)

    try:
        p.wait(timeout=duration_s + 300)
    except subprocess.TimeoutExpired:
        try:
            p.terminate()
            p.wait(timeout=10)
        except Exception:
            try:
                p.kill()
            except Exception:
                pass

    stop_evt.set()
    th_w.join(timeout=3)
    th_s.join(timeout=3)

    if p.returncode not in (0, None):
        raise RuntimeError(
            f"Tier-2 collection failed for {cid}. "
            f"See log: {logs / 'tier2_collect.log'}"
        )

    if not tier2_schema.exists():
        build_tier2_global_schema(str(raw_export), str(tier2_schema), max_keys=300)

    out_core = out_dir / "tier2_core_5hz.csv"
    out_full = out_dir / "tier2_full_5hz.csv"
    parse_tier2_with_schema(
        str(raw_export),
        str(out_core),
        str(out_full),
        str(tier2_schema),
        samples_target=samples_target,
    )

    meta_path = meta_dir / "meta_tier2.json"
    meta_path.write_text(json.dumps(meta, indent=2))
    append_manifest(out_root / "manifest_tier2.csv", {
        "case_id": cid,
        "workload": w,
        "stressor": s,
        "label": label,
        "duration_s": duration_s,
        "tier2_core_csv": str(out_core),
        "tier2_full_csv": str(out_full),
        "tier2_trace": str(trace_out),
        "tier2_raw_export": str(raw_export),
        "tier2_schema": str(tier2_schema),
        "meta_json": str(meta_path),
    })


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=["tier0", "tier1", "tier2"], required=True)
    ap.add_argument("--duration_s", "--duration-s", dest="duration_s", type=int, default=1000)
    ap.add_argument("--out_dir", "--out-dir", dest="out_dir", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--scripts_dir", "--scripts-dir", dest="scripts_dir", type=Path, default=DEFAULT_SCRIPTS)
    ap.add_argument("--tier2_template", "--tier2-template", dest="tier2_template", default=TIER2_DEFAULT_TEMPLATE)
    args = ap.parse_args()

    out_root = Path(args.out_dir)
    scripts_dir = Path(args.scripts_dir)
    tier0_schema = out_root / "tier0_schema_global.json"
    tier1_schema = out_root / "tier1_schema_global.json"
    tier2_schema = out_root / "tier2_schema_global.json"

    mkdirp(out_root)
    mkdirp(out_root / "tier0")
    mkdirp(out_root / "tier1")
    mkdirp(out_root / "tier2")
    mkdirp(out_root / "meta")
    mkdirp(out_root / "logs")

    if args.phase == "tier2":
        ensure_xctrace_ready()

    for c in all_cases():
        if args.phase == "tier0":
            run_case_tier0(
                c.workload,
                c.stressor,
                c.label,
                args.duration_s,
                out_root=out_root,
                tier0_schema_path=tier0_schema,
            )
            continue
        if args.phase == "tier1":
            run_case_tier1(
                c.workload,
                c.stressor,
                c.label,
                args.duration_s,
                out_root=out_root,
                scripts_dir=scripts_dir,
                tier1_schema_path=tier1_schema,
            )
            continue
        run_case_tier2(
            c.workload,
            c.stressor,
            c.label,
            args.duration_s,
            out_root=out_root,
            scripts_dir=scripts_dir,
            tier2_schema_path=tier2_schema,
            template=args.tier2_template,
        )


if __name__ == "__main__":  # pragma: no cover
    main()
