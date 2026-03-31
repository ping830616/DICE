from __future__ import annotations

import csv
import json
import platform
import shutil
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional


DEFAULT_LOG_PREDICATE = (
    '(eventMessage CONTAINS[c] "crash" OR '
    'eventMessage CONTAINS[c] "panic" OR '
    'process == "ReportCrash" OR '
    'senderImagePath CONTAINS[c] "ReportCrash")'
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_utc(ts: datetime) -> str:
    return ts.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def mkdirp(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def append_manifest_row(path: Path, row: dict[str, object]) -> None:
    mkdirp(path.parent)
    exists = path.exists()
    with path.open("a", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(row.keys()))
        if not exists:
            writer.writeheader()
        writer.writerow(row)


def diagnostic_report_dirs() -> list[Path]:
    return [
        Path.home() / "Library" / "Logs" / "DiagnosticReports",
        Path("/Library/Logs/DiagnosticReports"),
    ]


def snapshot_diagnostic_reports() -> dict[str, float]:
    snapshot: dict[str, float] = {}
    for base in diagnostic_report_dirs():
        if not base.exists():
            continue
        for path in base.glob("*"):
            if not path.is_file():
                continue
            try:
                snapshot[str(path.resolve())] = float(path.stat().st_mtime)
            except OSError:
                continue
    return snapshot


def parse_report_timestamp(path: Path) -> Optional[datetime]:
    stem = path.stem
    parts = stem.split("_")
    for token in parts[::-1]:
        try:
            return datetime.strptime(token, "%Y-%m-%d-%H%M%S").replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    try:
        return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    except OSError:
        return None


def parse_first_log_timestamp(path: Path) -> Optional[datetime]:
    if not path.exists():
        return None
    with path.open() as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            for key in ("timestamp", "time", "date"):
                value = payload.get(key)
                if not value:
                    continue
                try:
                    return datetime.fromisoformat(str(value).replace("Z", "+00:00")).astimezone(timezone.utc)
                except ValueError:
                    continue
    return None


def copy_new_reports(before: dict[str, float], out_dir: Path) -> list[Path]:
    copied: list[Path] = []
    mkdirp(out_dir)
    for base in diagnostic_report_dirs():
        if not base.exists():
            continue
        for path in base.glob("*"):
            if not path.is_file():
                continue
            try:
                resolved = str(path.resolve())
                mtime = float(path.stat().st_mtime)
            except OSError:
                continue
            old_mtime = before.get(resolved)
            if old_mtime is not None and mtime <= old_mtime:
                continue
            dst = out_dir / path.name
            shutil.copy2(path, dst)
            copied.append(dst)
    return copied


def export_log_window(start_utc: datetime, end_utc: datetime, out_path: Path, predicate: str = DEFAULT_LOG_PREDICATE) -> tuple[bool, str]:
    mkdirp(out_path.parent)
    cmd = [
        "log",
        "show",
        "--style",
        "json",
        "--start",
        iso_utc(start_utc),
        "--end",
        iso_utc(end_utc),
        "--predicate",
        predicate,
    ]
    proc = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    out_path.write_text(proc.stdout or "")
    if proc.returncode != 0:
        return False, (proc.stderr or proc.stdout or "").strip()
    return True, ""


def capture_screenshot(out_path: Path) -> tuple[bool, str]:
    mkdirp(out_path.parent)
    proc = subprocess.run(
        ["screencapture", "-x", str(out_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return False, (proc.stderr or proc.stdout or "").strip()
    return True, ""


@dataclass
class CrashCaptureContext:
    case_id: str
    workload: str
    stressor: str
    label: str
    phase: str
    out_root: str
    run_start_utc: str
    before_reports: dict[str, float]
    capture_screenshot: bool
    log_grace_s: int


def begin_case_capture(
    case_id: str,
    workload: str,
    stressor: str,
    label: str,
    phase: str,
    out_root: Path,
    capture_screenshot_flag: bool = False,
    log_grace_s: int = 60,
) -> CrashCaptureContext:
    supported = platform.system() == "Darwin"
    before = snapshot_diagnostic_reports() if supported else {}
    return CrashCaptureContext(
        case_id=case_id,
        workload=workload,
        stressor=stressor,
        label=label,
        phase=phase,
        out_root=str(Path(out_root)),
        run_start_utc=iso_utc(utc_now()),
        before_reports=before,
        capture_screenshot=capture_screenshot_flag,
        log_grace_s=int(log_grace_s),
    )


def finalize_case_capture(
    ctx: CrashCaptureContext,
    success: bool = True,
    extra_note: str = "",
    predicate: str = DEFAULT_LOG_PREDICATE,
) -> dict[str, object]:
    out_root = Path(ctx.out_root)
    evidence_root = out_root / "crash_evidence"
    case_root = evidence_root / ctx.case_id
    report_dir = case_root / "diagnostic_reports"
    log_dir = case_root / "system_logs"
    screenshot_dir = case_root / "screenshots"
    mkdirp(report_dir)
    mkdirp(log_dir)

    start_dt = datetime.fromisoformat(ctx.run_start_utc.replace("Z", "+00:00")).astimezone(timezone.utc)
    end_dt = utc_now()
    observed = int(platform.system() == "Darwin")
    note_parts = [extra_note.strip()] if extra_note.strip() else []

    copied_reports: list[Path] = []
    crash_sources: list[str] = []
    crash_time_candidates: list[datetime] = []
    log_path = log_dir / "crash_window.jsonl"
    screenshot_path = Path()

    if observed:
        copied_reports = copy_new_reports(ctx.before_reports, report_dir)
        for report in copied_reports:
            report_time = parse_report_timestamp(report)
            if report_time is not None:
                crash_time_candidates.append(report_time)
        if copied_reports:
            crash_sources.append("diagnostic_report")

        log_ok, log_msg = export_log_window(
            start_dt,
            end_dt + timedelta(seconds=max(ctx.log_grace_s, 0)),
            log_path,
            predicate=predicate,
        )
        if log_ok:
            log_time = parse_first_log_timestamp(log_path)
            if log_time is not None:
                crash_time_candidates.append(log_time)
                crash_sources.append("system_log")
        elif log_msg:
            note_parts.append(f"log show failed: {log_msg}")

    if observed and ctx.capture_screenshot and crash_time_candidates:
        screenshot_path = screenshot_dir / "post_run_capture.png"
        shot_ok, shot_msg = capture_screenshot(screenshot_path)
        if shot_ok:
            crash_sources.append("screenshot")
        else:
            note_parts.append(f"screencapture failed: {shot_msg}")

    crash_time = min(crash_time_candidates) if crash_time_candidates else None
    crash_detected = int(crash_time is not None or bool(copied_reports))
    crash_time_s = (
        float((crash_time - start_dt).total_seconds())
        if crash_time is not None
        else float("nan")
    )
    monitor_duration_s = float((end_dt - start_dt).total_seconds())

    row = {
        "case_id": ctx.case_id,
        "workload": ctx.workload,
        "stressor": ctx.stressor,
        "label": ctx.label,
        "phase": ctx.phase,
        "capture_supported": observed,
        "crash_outcome_observed": observed,
        "crash_detected": crash_detected,
        "run_success": int(bool(success)),
        "run_start_utc": iso_utc(start_dt),
        "run_end_utc": iso_utc(end_dt),
        "monitor_duration_s": monitor_duration_s,
        "crash_time_utc": iso_utc(crash_time) if crash_time is not None else "",
        "crash_time_s": crash_time_s,
        "crash_source": ",".join(sorted(set(crash_sources))),
        "crash_kind": "system_or_app_crash" if crash_detected else "",
        "diagnostic_report_path": ";".join(str(path) for path in copied_reports),
        "system_log_path": str(log_path) if log_path.exists() else "",
        "screenshot_path": str(screenshot_path) if screenshot_path.exists() else "",
        "evidence_note": " | ".join(part for part in note_parts if part),
    }

    summary_path = case_root / "crash_capture_summary.json"
    summary_path.write_text(json.dumps({"context": asdict(ctx), "summary": row}, indent=2) + "\n")
    append_manifest_row(evidence_root / "crash_events.csv", row)
    return row
