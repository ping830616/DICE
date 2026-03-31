import argparse
import contextlib
import json
import platform
import shutil
import subprocess
import threading
from pathlib import Path
from typing import Optional

from .cfg import all_cases, case_id, HZ, SEED, TIER2_DEFAULT_TEMPLATE
from .workloads import run_workload, run_stressor
from .tier0_collect_schema import build_and_save_global_schema, load_schema, collect_with_schema
from .powermetrics_parse_full import build_global_schema as build_tier1_global_schema, parse_with_schema as parse_tier1_with_schema
from .tier1_alt_macmon import (
    build_global_schema as build_tier1_alt_global_schema,
    collect_samples_to_jsonl as collect_tier1_alt_samples,
    convert_powermetrics_raw_to_jsonl as convert_tier1_alt_from_powermetrics,
    parse_with_schema as parse_tier1_alt_with_schema,
)
from .tier2_xctrace_parse import build_global_schema as build_tier2_global_schema, parse_with_schema as parse_tier2_with_schema
from .macos_collectors import (
    collect_powermetrics_text,
    export_xctrace_time_profile,
    record_xctrace_time_profile,
)
from .crash_evidence import begin_case_capture, finalize_case_capture

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


def command_available(name: str) -> bool:
    return shutil.which(name) is not None


def ensure_powermetrics_ready() -> None:
    if platform.system() != "Darwin":
        raise RuntimeError("Tier-1 powermetrics collection is only supported on macOS.")
    if not command_available("powermetrics"):
        raise RuntimeError(
            "Tier-1 collection requires the 'powermetrics' command to be available on this machine."
        )


def can_run_tier1() -> bool:
    return platform.system() == "Darwin" and command_available("powermetrics")


def can_run_tier1_alt(macmon_bin: str = "macmon") -> bool:
    return platform.system() == "Darwin" and command_available(macmon_bin)


def can_run_tier2() -> bool:
    if platform.system() != "Darwin":
        return False
    try:
        ensure_xctrace_ready()
    except Exception:
        return False
    return True


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


@contextlib.contextmanager
def sudo_keepalive(required: bool):
    """
    Keep sudo timestamp fresh during long-running collection jobs.
    """
    if not required:
        yield
        return

    try:
        check = subprocess.run(
            ["sudo", "-n", "-v"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            text=True,
        )
    except (FileNotFoundError, PermissionError) as e:
        raise RuntimeError(
            "Unable to execute sudo for powermetrics collection. "
            f"Error: {e}"
        ) from e
    if check.returncode != 0:
        try:
            prompt = subprocess.run(["sudo", "-v"], text=True)
        except (FileNotFoundError, PermissionError) as e:
            raise RuntimeError(
                "Unable to execute sudo for powermetrics collection. "
                f"Error: {e}"
            ) from e
        if prompt.returncode != 0:
            raise RuntimeError(
                "sudo authentication failed. Please run 'sudo -v' in this terminal "
                "and enter your password, then rerun the command."
            )

    stop_evt = threading.Event()

    def _refresh():
        while not stop_evt.wait(60):
            subprocess.run(
                ["sudo", "-n", "-v"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                text=True,
            )

    th = threading.Thread(target=_refresh, daemon=True)
    th.start()
    try:
        yield
    finally:
        stop_evt.set()
        th.join(timeout=2)


def run_case_tier0(
    w: str,
    s: str,
    label: str,
    duration_s: int,
    out_root: Path = DEFAULT_OUT,
    tier0_schema_path: Optional[Path] = None,
    capture_crash_evidence: bool = False,
    crash_log_grace_s: int = 60,
    capture_crash_screenshot: bool = False,
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

    crash_ctx = (
        begin_case_capture(
            case_id=cid,
            workload=w,
            stressor=s,
            label=label,
            phase="tier0",
            out_root=out_root,
            capture_screenshot_flag=capture_crash_screenshot,
            log_grace_s=crash_log_grace_s,
        )
        if capture_crash_evidence
        else None
    )
    case_success = False
    crash_note = ""
    try:
        stop_evt = threading.Event()
        th_w = threading.Thread(target=run_workload, args=(w, stop_evt), daemon=True)
        th_s = threading.Thread(target=run_stressor, args=(s, stop_evt), daemon=True)
        th_w.start(); th_s.start()

        out_csv = out_dir / "tier0_full_5hz.csv"
        try:
            collect_with_schema(str(out_csv), hz=HZ, duration_s=duration_s, schema=schema)
        finally:
            stop_evt.set()
            th_w.join(timeout=3); th_s.join(timeout=3)

        meta_path = meta_dir / "meta_tier0.json"
        meta_path.write_text(json.dumps(meta, indent=2))
        append_manifest(out_root / "manifest_tier0.csv", {
            "case_id": cid, "workload": w, "stressor": s, "label": label,
            "duration_s": duration_s, "tier0_csv": str(out_csv),
            "tier0_schema": str(tier0_schema), "meta_json": str(meta_path),
        })
        case_success = True
    except Exception as exc:
        crash_note = f"Tier-0 case failed: {exc}"
        raise
    finally:
        if crash_ctx is not None:
            finalize_case_capture(crash_ctx, success=case_success, extra_note=crash_note)


def run_case_tier1(
    w: str,
    s: str,
    label: str,
    duration_s: int,
    out_root: Path = DEFAULT_OUT,
    scripts_dir: Path = DEFAULT_SCRIPTS,
    tier1_schema_path: Optional[Path] = None,
    capture_crash_evidence: bool = False,
    crash_log_grace_s: int = 60,
    capture_crash_screenshot: bool = False,
):
    out_root = Path(out_root)
    tier1_schema = Path(tier1_schema_path) if tier1_schema_path else out_root / "tier1_schema_global.json"
    ensure_powermetrics_ready()

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

    crash_ctx = (
        begin_case_capture(
            case_id=cid,
            workload=w,
            stressor=s,
            label=label,
            phase="tier1",
            out_root=out_root,
            capture_screenshot_flag=capture_crash_screenshot,
            log_grace_s=crash_log_grace_s,
        )
        if capture_crash_evidence
        else None
    )
    case_success = False
    crash_note = ""
    try:
        stop_evt = threading.Event()
        th_w = threading.Thread(target=run_workload, args=(w, stop_evt), daemon=True)
        th_s = threading.Thread(target=run_stressor, args=(s, stop_evt), daemon=True)
        th_w.start(); th_s.start()

        try:
            with sudo_keepalive(required=True):
                result = collect_powermetrics_text(
                    raw_txt,
                    samples_target=samples_target,
                    sample_rate_ms=200,
                    log_path=logs / "tier1_collect.log",
                )
        finally:
            stop_evt.set()
            th_w.join(timeout=3); th_s.join(timeout=3)

        if result.returncode != 0:
            raw_err = Path(f"{raw_txt}.stderr.log")
            raise RuntimeError(
                f"Tier-1 collection failed for {cid}. "
                f"See logs: {logs / 'tier1_collect.log'}"
                + (f" and {raw_err}" if raw_err.exists() else "")
            )

        if (not raw_txt.exists()) or raw_txt.stat().st_size < 5000:
            raw_err = Path(f"{raw_txt}.stderr.log")
            raise RuntimeError(
                f"Tier-1 raw capture is missing/too small for {cid}. "
                f"raw={raw_txt} size={raw_txt.stat().st_size if raw_txt.exists() else 0} bytes. "
                f"See logs: {logs / 'tier1_collect.log'}"
                + (f" and {raw_err}" if raw_err.exists() else "")
            )

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
        case_success = True
    except Exception as exc:
        crash_note = f"Tier-1 case failed: {exc}"
        raise
    finally:
        if crash_ctx is not None:
            finalize_case_capture(crash_ctx, success=case_success, extra_note=crash_note)


def run_case_tier1_alt(
    w: str,
    s: str,
    label: str,
    duration_s: int,
    out_root: Path = DEFAULT_OUT,
    scripts_dir: Path = DEFAULT_SCRIPTS,
    tier1_alt_schema_path: Optional[Path] = None,
    macmon_bin: str = "macmon",
    capture_crash_evidence: bool = False,
    crash_log_grace_s: int = 60,
    capture_crash_screenshot: bool = False,
):
    out_root = Path(out_root)
    tier1_alt_schema = (
        Path(tier1_alt_schema_path)
        if tier1_alt_schema_path
        else out_root / "tier1_alt_schema_global.json"
    )
    ensure_powermetrics_ready()

    cid = case_id(w, s)
    out_dir = out_root / "tier1_alt" / cid
    meta_dir = out_root / "meta" / cid
    logs = out_root / "logs" / cid
    for d in [out_dir, meta_dir, logs]:
        mkdirp(d)

    samples_target = HZ * duration_s
    raw_jsonl = out_dir / "macmon_raw.jsonl"

    meta = {
        "case_id": cid,
        "workload": w,
        "stressor": s,
        "label": label,
        "duration_s": duration_s,
        "hz": HZ,
        "seed": SEED,
        "platform": platform.platform(),
        "phase": "tier1_alt",
        "tier1_alt_schema": str(tier1_alt_schema),
        "tier1_alt_collector": "macmon",
        "macmon_bin": macmon_bin,
    }

    crash_ctx = (
        begin_case_capture(
            case_id=cid,
            workload=w,
            stressor=s,
            label=label,
            phase="tier1_alt",
            out_root=out_root,
            capture_screenshot_flag=capture_crash_screenshot,
            log_grace_s=crash_log_grace_s,
        )
        if capture_crash_evidence
        else None
    )
    case_success = False
    crash_note = ""
    try:
        stop_evt = threading.Event()
        th_w = threading.Thread(target=run_workload, args=(w, stop_evt), daemon=True)
        th_s = threading.Thread(target=run_stressor, args=(s, stop_evt), daemon=True)
        th_w.start()
        th_s.start()

        collect_err = None
        try:
            collect_tier1_alt_samples(
                str(raw_jsonl),
                hz=HZ,
                duration_s=duration_s,
                macmon_bin=macmon_bin,
            )
        except Exception as e:
            collect_err = e
        finally:
            stop_evt.set()
            th_w.join(timeout=3)
            th_s.join(timeout=3)

        if collect_err is not None:
            fallback_raw_txt = out_dir / "powermetrics_fallback_raw.txt"
            stop_evt_fb = threading.Event()
            th_w_fb = threading.Thread(target=run_workload, args=(w, stop_evt_fb), daemon=True)
            th_s_fb = threading.Thread(target=run_stressor, args=(s, stop_evt_fb), daemon=True)
            th_w_fb.start()
            th_s_fb.start()

            try:
                with sudo_keepalive(required=True):
                    result = collect_powermetrics_text(
                        fallback_raw_txt,
                        samples_target=samples_target,
                        sample_rate_ms=200,
                        log_path=logs / "tier1_alt_collect_fallback.log",
                    )
            finally:
                stop_evt_fb.set()
                th_w_fb.join(timeout=3)
                th_s_fb.join(timeout=3)

            if result.returncode != 0:
                fallback_err = Path(f"{fallback_raw_txt}.stderr.log")
                raise RuntimeError(
                    f"Tier-1-alt collection failed for {cid}. "
                    f"macmon error: {collect_err}. "
                    f"Fallback powermetrics also failed. "
                    f"See logs: {logs / 'tier1_alt_collect_fallback.log'}"
                    + (f" and {fallback_err}" if fallback_err.exists() else "")
                )

            if (not fallback_raw_txt.exists()) or fallback_raw_txt.stat().st_size < 5000:
                raise RuntimeError(
                    f"Tier-1-alt collection failed for {cid}. "
                    f"macmon error: {collect_err}. "
                    f"Fallback powermetrics raw capture is missing/too small: {fallback_raw_txt}"
                )

            convert_tier1_alt_from_powermetrics(
                raw_txt=str(fallback_raw_txt),
                out_jsonl=str(raw_jsonl),
                hz=HZ,
                duration_s=duration_s,
            )
            meta["tier1_alt_collector"] = "powermetrics_fallback"
            meta["tier1_alt_fallback_reason"] = str(collect_err)
            meta["tier1_alt_fallback_raw_txt"] = str(fallback_raw_txt)

        if (not raw_jsonl.exists()) or raw_jsonl.stat().st_size < 1000:
            raise RuntimeError(
                f"Tier-1-alt raw capture is missing/too small for {cid}. "
                f"raw={raw_jsonl} size={raw_jsonl.stat().st_size if raw_jsonl.exists() else 0} bytes."
            )

        if not tier1_alt_schema.exists():
            build_tier1_alt_global_schema(str(raw_jsonl), str(tier1_alt_schema), max_keys=300)

        out_core = out_dir / "tier1_alt_core_5hz.csv"
        out_full = out_dir / "tier1_alt_full_5hz.csv"
        parse_tier1_alt_with_schema(
            str(raw_jsonl),
            str(out_core),
            str(out_full),
            str(tier1_alt_schema),
            samples_target=samples_target,
        )

        meta_path = meta_dir / "meta_tier1_alt.json"
        meta_path.write_text(json.dumps(meta, indent=2))
        append_manifest(out_root / "manifest_tier1_alt.csv", {
            "case_id": cid,
            "workload": w,
            "stressor": s,
            "label": label,
            "duration_s": duration_s,
            "tier1_alt_core_csv": str(out_core),
            "tier1_alt_full_csv": str(out_full),
            "tier1_alt_raw_jsonl": str(raw_jsonl),
            "tier1_alt_schema": str(tier1_alt_schema),
            "meta_json": str(meta_path),
        })
        case_success = True
    except Exception as exc:
        crash_note = f"Tier-1-alt case failed: {exc}"
        raise
    finally:
        if crash_ctx is not None:
            finalize_case_capture(crash_ctx, success=case_success, extra_note=crash_note)


def run_case_tier2(
    w: str,
    s: str,
    label: str,
    duration_s: int,
    out_root: Path = DEFAULT_OUT,
    scripts_dir: Path = DEFAULT_SCRIPTS,
    tier2_schema_path: Optional[Path] = None,
    template: str = TIER2_DEFAULT_TEMPLATE,
    capture_crash_evidence: bool = False,
    crash_log_grace_s: int = 60,
    capture_crash_screenshot: bool = False,
):
    out_root = Path(out_root)
    tier2_schema = Path(tier2_schema_path) if tier2_schema_path else out_root / "tier2_schema_global.json"

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

    crash_ctx = (
        begin_case_capture(
            case_id=cid,
            workload=w,
            stressor=s,
            label=label,
            phase="tier2",
            out_root=out_root,
            capture_screenshot_flag=capture_crash_screenshot,
            log_grace_s=crash_log_grace_s,
        )
        if capture_crash_evidence
        else None
    )
    case_success = False
    crash_note = ""
    try:
        stop_evt = threading.Event()
        th_w = threading.Thread(target=run_workload, args=(w, stop_evt), daemon=True)
        th_s = threading.Thread(target=run_stressor, args=(s, stop_evt), daemon=True)
        th_w.start()
        th_s.start()

        try:
            record_result = record_xctrace_time_profile(
                trace_out=trace_out,
                duration_s=duration_s,
                template=template,
                log_path=logs / "tier2_collect.log",
            )
            if record_result.returncode != 0:
                raise RuntimeError(
                    f"Tier-2 collection failed for {cid}. "
                    f"See log: {logs / 'tier2_collect.log'}"
                )
            export_xctrace_time_profile(
                trace_out=trace_out,
                raw_export=raw_export,
                log_path=logs / "tier2_collect.log",
            )
        finally:
            stop_evt.set()
            th_w.join(timeout=3)
            th_s.join(timeout=3)

        if not raw_export.exists():
            raise RuntimeError(
                f"Tier-2 collection failed for {cid}. "
                f"Missing export: {raw_export}"
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
        case_success = True
    except Exception as exc:
        crash_note = f"Tier-2 case failed: {exc}"
        raise
    finally:
        if crash_ctx is not None:
            finalize_case_capture(crash_ctx, success=case_success, extra_note=crash_note)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=["tier0", "tier1", "tier1_alt", "tier2"], required=True)
    ap.add_argument("--duration_s", "--duration-s", dest="duration_s", type=int, default=1000)
    ap.add_argument("--out_dir", "--out-dir", dest="out_dir", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--scripts_dir", "--scripts-dir", dest="scripts_dir", type=Path, default=DEFAULT_SCRIPTS)
    ap.add_argument("--tier2_template", "--tier2-template", dest="tier2_template", default=TIER2_DEFAULT_TEMPLATE)
    ap.add_argument("--tier1_alt_bin", "--tier1-alt-bin", dest="tier1_alt_bin", default="macmon")
    ap.add_argument("--capture_crash_evidence", "--capture-crash-evidence", dest="capture_crash_evidence", action="store_true")
    ap.add_argument("--capture_crash_screenshot", "--capture-crash-screenshot", dest="capture_crash_screenshot", action="store_true")
    ap.add_argument("--crash_log_grace_s", "--crash-log-grace-s", dest="crash_log_grace_s", type=int, default=60)
    args = ap.parse_args()

    out_root = Path(args.out_dir)
    scripts_dir = Path(args.scripts_dir)
    tier0_schema = out_root / "tier0_schema_global.json"
    tier1_schema = out_root / "tier1_schema_global.json"
    tier1_alt_schema = out_root / "tier1_alt_schema_global.json"
    tier2_schema = out_root / "tier2_schema_global.json"

    mkdirp(out_root)
    mkdirp(out_root / "tier0")
    mkdirp(out_root / "tier1")
    mkdirp(out_root / "tier1_alt")
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
                capture_crash_evidence=args.capture_crash_evidence,
                crash_log_grace_s=args.crash_log_grace_s,
                capture_crash_screenshot=args.capture_crash_screenshot,
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
                capture_crash_evidence=args.capture_crash_evidence,
                crash_log_grace_s=args.crash_log_grace_s,
                capture_crash_screenshot=args.capture_crash_screenshot,
            )
            continue
        if args.phase == "tier1_alt":
            run_case_tier1_alt(
                c.workload,
                c.stressor,
                c.label,
                args.duration_s,
                out_root=out_root,
                scripts_dir=scripts_dir,
                tier1_alt_schema_path=tier1_alt_schema,
                macmon_bin=args.tier1_alt_bin,
                capture_crash_evidence=args.capture_crash_evidence,
                crash_log_grace_s=args.crash_log_grace_s,
                capture_crash_screenshot=args.capture_crash_screenshot,
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
            capture_crash_evidence=args.capture_crash_evidence,
            crash_log_grace_s=args.crash_log_grace_s,
            capture_crash_screenshot=args.capture_crash_screenshot,
        )


if __name__ == "__main__":  # pragma: no cover
    main()
