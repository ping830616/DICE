#!/usr/bin/env python3
"""Generate paper-ready crash evidence cards for DICE."""

from __future__ import annotations

import argparse
import json
import os
import sys
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.early_warning_analysis import merge_warning_and_crash, normalize_crash_manifest


CARD_WIDTH_IN = 13.8
CARD_HEIGHT_IN = 8.1
STATUS_COLOR = {
    "warning_before_crash": "#166534",
    "late_warning_after_crash": "#B45309",
    "missed_crash": "#B91C1C",
    "warning_without_observed_crash": "#1D4ED8",
    "observed_noncrash": "#475569",
    "warning_only_template": "#7C3AED",
    "monitoring_only": "#64748B",
}


def safe_float(value: object) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return float("nan")
    return out if np.isfinite(out) else float("nan")


def fmt_seconds(value: object) -> str:
    val = safe_float(value)
    if not np.isfinite(val):
        return "n/a"
    return f"{val:.1f} s"


def fmt_flag(value: object) -> str:
    if pd.isna(value):
        return "n/a"
    return "yes" if int(bool(value)) else "no"


def display_text(value: object, default: str = "n/a") -> str:
    if value is None or pd.isna(value):
        return default
    text = str(value).strip()
    return text if text else default


def wrap_block(text: str, width: int = 100, max_lines: int = 12) -> str:
    if not text.strip():
        return "No excerpt available."
    lines: list[str] = []
    for raw in text.splitlines():
        raw = raw.rstrip()
        if not raw:
            if lines and lines[-1] != "":
                lines.append("")
            continue
        wrapped = textwrap.wrap(raw, width=width, break_long_words=False, break_on_hyphens=False)
        lines.extend(wrapped or [""])
        if len(lines) >= max_lines:
            break
    if len(lines) > max_lines:
        lines = lines[:max_lines]
    if lines and len(text.splitlines()) > max_lines:
        lines[-1] = lines[-1][: max(0, width - 3)] + "..."
    return "\n".join(lines) if lines else "No excerpt available."


def first_existing_path(value: object) -> Path | None:
    if value is None or pd.isna(value):
        return None
    for token in str(value).split(";"):
        token = token.strip()
        if not token:
            continue
        path = Path(token)
        if path.exists():
            return path
    return None


def short_path(path: Path | None) -> str:
    if path is None:
        return "n/a"
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def relative_path(from_dir: Path, to_path: Path) -> Path:
    return Path(os.path.relpath(to_path, start=from_dir))


def load_alignment_table(
    alignment_csv: Path | None,
    crash_manifest: Path | None,
    warning_csv: Path | None,
) -> pd.DataFrame:
    if alignment_csv is not None and alignment_csv.exists():
        df = pd.read_csv(alignment_csv).copy()
    else:
        crash_df = normalize_crash_manifest(crash_manifest)
        if warning_csv is not None and warning_csv.exists():
            warning_df = pd.read_csv(warning_csv).copy()
            df = merge_warning_and_crash(warning_df, crash_df)
        elif not crash_df.empty:
            df = crash_df.copy()
        else:
            raise FileNotFoundError(
                "Provide an existing --alignment_csv, or provide --crash_manifest with optional --warning_csv."
            )

    defaults: dict[str, object] = {
        "case_id": "",
        "workload": "",
        "stressor": "",
        "warning_available": 0,
        "first_warning_s": np.nan,
        "warning_source": "",
        "warning_before_crash": 0,
        "late_warning_after_crash": 0,
        "warning_without_observed_crash": 0,
        "crash_outcome_observed": 0,
        "crash_detected": 0,
        "crash_time_s": np.nan,
        "monitor_duration_s": np.nan,
        "run_duration_s": np.nan,
        "lead_time_s": np.nan,
        "crash_source": "",
        "crash_kind": "",
        "diagnostic_report_path": "",
        "system_log_path": "",
        "screenshot_path": "",
        "evidence_note": "",
        "config_label": "",
        "profile_label": "",
        "warning_dominant_tier": "",
        "warning_dominant_mechanism": "",
        "warning_top_feature_1": "",
        "warning_top_feature_score_1": np.nan,
        "warning_top_feature_2": "",
        "warning_top_feature_score_2": np.nan,
    }
    for col, value in defaults.items():
        if col not in df.columns:
            df[col] = value

    if "lead_time_s" not in df.columns or df["lead_time_s"].isna().all():
        df["lead_time_s"] = pd.to_numeric(df["crash_time_s"], errors="coerce") - pd.to_numeric(
            df["first_warning_s"], errors="coerce"
        )

    numeric_cols = [
        "warning_available",
        "warning_before_crash",
        "late_warning_after_crash",
        "warning_without_observed_crash",
        "crash_outcome_observed",
        "crash_detected",
        "first_warning_s",
        "crash_time_s",
        "monitor_duration_s",
        "run_duration_s",
        "lead_time_s",
        "warning_top_feature_score_1",
        "warning_top_feature_score_2",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df.copy()


def classify_case(row: pd.Series) -> tuple[str, str]:
    warning_before = int(bool(row.get("warning_before_crash", 0)))
    late_warning = int(bool(row.get("late_warning_after_crash", 0)))
    warning_available = int(bool(row.get("warning_available", 0)))
    observed = int(bool(row.get("crash_outcome_observed", 0)))
    crash_detected = int(bool(row.get("crash_detected", 0)))

    if crash_detected and warning_before:
        return "warning_before_crash", "Warning before crash"
    if crash_detected and late_warning:
        return "late_warning_after_crash", "Late warning after crash"
    if crash_detected and not warning_available:
        return "missed_crash", "Crash observed, no early warning"
    if observed and not crash_detected and warning_available:
        return "warning_without_observed_crash", "Warning without observed crash"
    if observed and not crash_detected:
        return "observed_noncrash", "Observed non-crash run"
    if warning_available:
        return "warning_only_template", "Warning-only template"
    return "monitoring_only", "Monitoring-only template"


def sort_cases(df: pd.DataFrame) -> pd.DataFrame:
    view = df.copy()
    status_rank = {
        "warning_before_crash": 0,
        "late_warning_after_crash": 1,
        "missed_crash": 2,
        "warning_without_observed_crash": 3,
        "observed_noncrash": 4,
        "warning_only_template": 5,
        "monitoring_only": 6,
    }
    view["status_rank"] = view["card_status_key"].map(status_rank).fillna(99)
    view["lead_sort"] = pd.to_numeric(view["lead_time_s"], errors="coerce").fillna(-1e9)
    view["crash_sort"] = pd.to_numeric(view["crash_time_s"], errors="coerce").fillna(-1e9)
    return view.sort_values(
        ["status_rank", "lead_sort", "crash_sort", "workload", "stressor", "case_id"],
        ascending=[True, False, False, True, True, True],
        na_position="last",
    ).reset_index(drop=True)


def parse_diagnostic_report_excerpt(path: Path | None, max_lines: int = 10) -> str:
    if path is None or not path.exists():
        return "No diagnostic report was captured for this case."

    preferred_prefixes = [
        "Process:",
        "Path:",
        "Identifier:",
        "Version:",
        "Code Type:",
        "Parent Process:",
        "Date/Time:",
        "OS Version:",
        "Exception Type:",
        "Exception Codes:",
        "Termination Reason:",
        "Triggered by Thread:",
    ]
    lines = [line.rstrip() for line in path.read_text(errors="ignore").splitlines()]
    selected: list[str] = []
    for prefix in preferred_prefixes:
        for line in lines:
            if line.startswith(prefix):
                selected.append(line)
                break
        if len(selected) >= max_lines:
            break
    if not selected:
        selected = [line for line in lines if line.strip()][:max_lines]
    return wrap_block("\n".join(selected), width=82, max_lines=max_lines)


def parse_system_log_excerpt(path: Path | None, max_lines: int = 8) -> str:
    if path is None or not path.exists():
        return "No filtered crash-window system log was captured for this case."

    lines: list[str] = []
    for raw in path.read_text(errors="ignore").splitlines():
        raw = raw.strip()
        if not raw:
            continue
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            lines.append(raw)
            if len(lines) >= max_lines:
                break
            continue
        timestamp = payload.get("timestamp") or payload.get("time") or payload.get("date") or "unknown-time"
        process = payload.get("process") or payload.get("sender") or payload.get("subsystem") or "unknown-process"
        message = str(payload.get("eventMessage") or payload.get("message") or "").strip()
        if message:
            message = textwrap.shorten(message, width=120, placeholder="...")
        else:
            message = "No eventMessage payload."
        lines.append(f"{timestamp} | {process} | {message}")
        if len(lines) >= max_lines:
            break
    return wrap_block("\n".join(lines), width=96, max_lines=max_lines)


def timeline_summary(row: pd.Series) -> str:
    if int(bool(row.get("crash_detected", 0))) and int(bool(row.get("warning_before_crash", 0))):
        return (
            f"DICE first warned at {fmt_seconds(row.get('first_warning_s'))}; "
            f"the first crash artifact appeared at {fmt_seconds(row.get('crash_time_s'))}; "
            f"lead time = {fmt_seconds(row.get('lead_time_s'))}."
        )
    if int(bool(row.get("crash_detected", 0))) and int(bool(row.get("late_warning_after_crash", 0))):
        return (
            f"A warning was recorded at {fmt_seconds(row.get('first_warning_s'))}, but the first crash artifact "
            f"arrived earlier at {fmt_seconds(row.get('crash_time_s'))}."
        )
    if int(bool(row.get("crash_detected", 0))) and not int(bool(row.get("warning_available", 0))):
        return f"No warning was recorded before the crash artifact at {fmt_seconds(row.get('crash_time_s'))}."
    if int(bool(row.get("warning_available", 0))):
        return (
            f"A first warning is available at {fmt_seconds(row.get('first_warning_s'))}, but this card is still a "
            "template because no observed crash artifact has been linked yet."
        )
    return "No warning or crash artifact is linked yet for this case."


def build_card_markdown(row: pd.Series, fig_rel: Path, screenshot_rel: Path | None, report_excerpt: str, log_excerpt: str) -> str:
    report_path = first_existing_path(row.get("diagnostic_report_path"))
    log_path = first_existing_path(row.get("system_log_path"))
    screenshot_path = first_existing_path(row.get("screenshot_path"))

    lines = [
        f"# Crash Evidence Card: {row.get('case_id', 'unknown_case')}",
        "",
        f"![Crash evidence card]({fig_rel.as_posix()})",
        "",
        "## Summary",
        "",
        f"- Status: {row.get('card_status_label', 'n/a')}",
        f"- Workload: {row.get('workload', 'n/a')}",
        f"- Stressor: {row.get('stressor', 'n/a')}",
        f"- Warning time: {fmt_seconds(row.get('first_warning_s'))}",
        f"- Crash time: {fmt_seconds(row.get('crash_time_s'))}",
        f"- Lead time: {fmt_seconds(row.get('lead_time_s'))}",
        f"- Warning source: {display_text(row.get('warning_source'))}",
        f"- Crash source: {display_text(row.get('crash_source'))}",
        "",
        "## Evidence Files",
        "",
        f"- Diagnostic report: `{short_path(report_path)}`",
        f"- System log: `{short_path(log_path)}`",
        f"- Screenshot: `{short_path(screenshot_path)}`",
    ]
    if screenshot_rel is not None:
        lines.extend(["", f"![Screenshot artifact]({screenshot_rel.as_posix()})"])
    lines.extend(
        [
            "",
            "## Diagnostic Report Excerpt",
            "",
            "```text",
            report_excerpt,
            "```",
            "",
            "## System Log Excerpt",
            "",
            "```text",
            log_excerpt,
            "```",
        ]
    )
    note = str(row.get("evidence_note", "") or "").strip()
    if note:
        lines.extend(["", "## Notes", "", note])
    return "\n".join(lines).rstrip() + "\n"


def render_text_panel(ax, title: str, body: str, fontsize: float = 10.2, monospace: bool = False) -> None:
    ax.set_axis_off()
    ax.text(
        0.0,
        1.0,
        title,
        fontsize=12.5,
        fontweight="bold",
        color="#0F172A",
        va="top",
        ha="left",
        transform=ax.transAxes,
    )
    ax.text(
        0.0,
        0.92,
        body,
        fontsize=fontsize,
        color="#1E293B",
        va="top",
        ha="left",
        linespacing=1.35,
        family="DejaVu Sans Mono" if monospace else "DejaVu Sans",
        transform=ax.transAxes,
    )


def render_timeline(ax, row: pd.Series) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", left=False, labelleft=False)
    ax.grid(axis="x", color="#CBD5E1", alpha=0.35)
    ax.set_facecolor("#F8FAFC")

    end_candidates = [
        safe_float(row.get("monitor_duration_s")),
        safe_float(row.get("run_duration_s")),
        safe_float(row.get("first_warning_s")),
        safe_float(row.get("crash_time_s")),
    ]
    finite = [value for value in end_candidates if np.isfinite(value)]
    timeline_end = max(finite) if finite else 1.0
    timeline_end = max(timeline_end, 1.0)
    ax.hlines(0.0, 0.0, timeline_end, color="#CBD5E1", linewidth=10.0, zorder=1)

    warning_time = safe_float(row.get("first_warning_s"))
    crash_time = safe_float(row.get("crash_time_s"))
    if np.isfinite(warning_time):
        ax.scatter([warning_time], [0.0], s=110, color="#2563EB", zorder=3, label="First warning")
        ax.text(warning_time, 0.18, f"warning\n{warning_time:.1f}s", ha="center", va="bottom", fontsize=9.5, color="#1D4ED8")
    if np.isfinite(crash_time):
        ax.scatter([crash_time], [0.0], s=140, marker="X", color="#DC2626", zorder=4, label="Crash artifact")
        ax.text(crash_time, -0.22, f"crash\n{crash_time:.1f}s", ha="center", va="top", fontsize=9.5, color="#991B1B")
    if np.isfinite(warning_time) and np.isfinite(crash_time):
        line_color = "#16A34A" if int(bool(row.get("warning_before_crash", 0))) else "#F59E0B"
        ax.hlines(0.0, min(warning_time, crash_time), max(warning_time, crash_time), color=line_color, linewidth=4.0, zorder=2)

    ax.set_xlim(-0.02 * timeline_end, 1.02 * timeline_end)
    ax.set_ylim(-0.5, 0.5)
    ax.set_xlabel("Time from run start (s)")
    ax.set_title("Warning-to-crash timeline", fontsize=12.5, fontweight="bold", color="#0F172A")


def render_screenshot_panel(ax, screenshot_path: Path | None, status_label: str) -> None:
    ax.set_axis_off()
    ax.text(
        0.0,
        1.0,
        "Screenshot or visual artifact",
        fontsize=12.5,
        fontweight="bold",
        color="#0F172A",
        va="top",
        ha="left",
        transform=ax.transAxes,
    )
    if screenshot_path is not None and screenshot_path.exists():
        try:
            image = plt.imread(str(screenshot_path))
            ax.imshow(image)
            ax.set_aspect("auto")
            ax.text(
                0.0,
                -0.08,
                short_path(screenshot_path),
                fontsize=9.0,
                color="#475569",
                va="top",
                ha="left",
                transform=ax.transAxes,
            )
            return
        except Exception:
            pass
    ax.add_patch(
        Rectangle((0.02, 0.12), 0.96, 0.72, facecolor="#E2E8F0", edgecolor="#CBD5E1", linewidth=1.5, transform=ax.transAxes)
    )
    ax.text(
        0.5,
        0.50,
        "No screenshot was captured.\nUse the diagnostic report and system log\nas the primary crash evidence.",
        fontsize=11.0,
        color="#334155",
        ha="center",
        va="center",
        transform=ax.transAxes,
    )
    ax.text(
        0.5,
        0.18,
        f"Card status: {status_label}",
        fontsize=10.0,
        color="#475569",
        ha="center",
        va="center",
        transform=ax.transAxes,
    )


def render_card_png(row: pd.Series, out_png: Path, title: str) -> None:
    report_path = first_existing_path(row.get("diagnostic_report_path"))
    log_path = first_existing_path(row.get("system_log_path"))
    screenshot_path = first_existing_path(row.get("screenshot_path"))
    report_excerpt = parse_diagnostic_report_excerpt(report_path)
    log_excerpt = parse_system_log_excerpt(log_path)

    fig = plt.figure(figsize=(CARD_WIDTH_IN, CARD_HEIGHT_IN), facecolor="white")
    gs = fig.add_gridspec(2, 2, width_ratios=[1.16, 0.84], height_ratios=[0.56, 0.44], hspace=0.20, wspace=0.12)
    ax_summary = fig.add_subplot(gs[0, 0])
    ax_shot = fig.add_subplot(gs[0, 1])
    ax_timeline = fig.add_subplot(gs[1, 0])
    ax_evidence = fig.add_subplot(gs[1, 1])

    fig.text(0.03, 0.965, title, fontsize=16.5, fontweight="bold", color="#0F172A", ha="left", va="top")
    fig.text(
        0.03,
        0.927,
        f"{row.get('case_id', 'unknown_case')} | {row.get('workload', 'n/a')} / {row.get('stressor', 'n/a')}",
        fontsize=11.5,
        color="#334155",
        ha="left",
        va="top",
    )

    badge_color = STATUS_COLOR.get(str(row.get("card_status_key", "")), "#475569")
    fig.text(
        0.965,
        0.955,
        str(row.get("card_status_label", "n/a")),
        fontsize=11.5,
        color="white",
        ha="right",
        va="top",
        bbox=dict(boxstyle="round,pad=0.35", facecolor=badge_color, edgecolor=badge_color),
    )

    summary_lines = [
        f"Profile: {row.get('profile_label', '') or 'n/a'}",
        f"Config: {row.get('config_label', '') or 'n/a'}",
        f"Warning available: {fmt_flag(row.get('warning_available'))}",
        f"Warning time: {fmt_seconds(row.get('first_warning_s'))}",
        f"Crash observed: {fmt_flag(row.get('crash_detected'))}",
        f"Crash time: {fmt_seconds(row.get('crash_time_s'))}",
        f"Lead time: {fmt_seconds(row.get('lead_time_s'))}",
        f"Warning source: {display_text(row.get('warning_source'))}",
        f"Crash source: {display_text(row.get('crash_source'))}",
    ]
    warning_tier = str(row.get("warning_dominant_tier", "") or "").strip()
    warning_mech = str(row.get("warning_dominant_mechanism", "") or "").strip()
    if warning_tier:
        summary_lines.append(f"Warning tier: {warning_tier}")
    if warning_mech:
        summary_lines.append(f"Warning mechanism: {warning_mech}")

    feature_bits = []
    feature_1 = str(row.get("warning_top_feature_1", "") or "").strip()
    feature_2 = str(row.get("warning_top_feature_2", "") or "").strip()
    if feature_1:
        score_1 = safe_float(row.get("warning_top_feature_score_1"))
        feature_bits.append(f"{feature_1} ({score_1:.3f})" if np.isfinite(score_1) else feature_1)
    if feature_2:
        score_2 = safe_float(row.get("warning_top_feature_score_2"))
        feature_bits.append(f"{feature_2} ({score_2:.3f})" if np.isfinite(score_2) else feature_2)
    if feature_bits:
        summary_lines.append("Top warning features: " + ", ".join(feature_bits))
    summary_lines.extend(["", timeline_summary(row)])
    note = str(row.get("evidence_note", "") or "").strip()
    if note:
        summary_lines.extend(["", "Evidence note: " + note])
    render_text_panel(ax_summary, "Case summary", "\n".join(summary_lines), fontsize=10.5, monospace=False)

    render_screenshot_panel(ax_shot, screenshot_path, str(row.get("card_status_label", "n/a")))
    render_timeline(ax_timeline, row)

    evidence_lines = [
        "Diagnostic report",
        report_excerpt,
        "",
        "System log",
        log_excerpt,
        "",
        f"Diagnostic report path: {short_path(report_path)}",
        f"System log path: {short_path(log_path)}",
        f"Screenshot path: {short_path(screenshot_path)}",
    ]
    render_text_panel(ax_evidence, "Crash artifacts", "\n".join(evidence_lines), fontsize=9.0, monospace=True)

    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def markdown_table(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    header = "| " + " | ".join(cols) + " |"
    rule = "| " + " | ".join(["---"] * len(cols)) + " |"
    rows = []
    for record in df.to_dict(orient="records"):
        vals = ["" if pd.isna(record.get(col)) else str(record.get(col)) for col in cols]
        rows.append("| " + " | ".join(vals) + " |")
    return "\n".join([header, rule, *rows])


def write_gallery_markdown(out_path: Path, cards: pd.DataFrame, title: str) -> None:
    lines = [
        f"# {title}",
        "",
        "This gallery summarizes the joined DICE warning-to-crash evidence available for each selected case.",
        "",
        "## Card Index",
        "",
    ]
    preview = cards[
        [
            "case_id",
            "card_status_label",
            "first_warning_s",
            "crash_time_s",
            "lead_time_s",
            "crash_source",
        ]
    ].copy()
    preview["first_warning_s"] = preview["first_warning_s"].map(fmt_seconds)
    preview["crash_time_s"] = preview["crash_time_s"].map(fmt_seconds)
    preview["lead_time_s"] = preview["lead_time_s"].map(fmt_seconds)
    lines.extend([markdown_table(preview), ""])
    for row in cards.itertuples(index=False):
        fig_rel = Path("figures") / f"{row.case_id}.png"
        md_rel = Path("cards") / f"{row.case_id}.md"
        lines.extend(
            [
                f"## {row.case_id}",
                "",
                f"- Status: {row.card_status_label}",
                f"- Markdown card: `{md_rel.as_posix()}`",
                "",
                f"![{row.case_id}]({fig_rel.as_posix()})",
                "",
            ]
        )
    out_path.write_text("\n".join(lines).rstrip() + "\n")


def prepare_cards(df: pd.DataFrame, include_noncrash: bool, max_cards: int | None) -> pd.DataFrame:
    cards = df.copy()
    cards[["card_status_key", "card_status_label"]] = cards.apply(
        lambda row: pd.Series(classify_case(row)),
        axis=1,
    )
    if not include_noncrash:
        cards = cards[
            cards["card_status_key"].isin(
                [
                    "warning_before_crash",
                    "late_warning_after_crash",
                    "missed_crash",
                    "warning_only_template",
                ]
            )
        ].copy()
    cards = sort_cases(cards)
    if max_cards is not None and max_cards > 0:
        cards = cards.head(int(max_cards)).copy()
    return cards.reset_index(drop=True)


def run(
    out_dir: Path,
    alignment_csv: Path | None = None,
    crash_manifest: Path | None = None,
    warning_csv: Path | None = None,
    title: str = "DICE Crash Evidence Gallery",
    include_noncrash: bool = False,
    max_cards: int = 12,
) -> dict[str, object]:
    out_dir = Path(out_dir)
    figs_dir = out_dir / "figures"
    cards_dir = out_dir / "cards"
    out_dir.mkdir(parents=True, exist_ok=True)
    figs_dir.mkdir(parents=True, exist_ok=True)
    cards_dir.mkdir(parents=True, exist_ok=True)

    merged = load_alignment_table(alignment_csv, crash_manifest, warning_csv)
    cards = prepare_cards(merged, include_noncrash=include_noncrash, max_cards=max_cards)
    if cards.empty:
        raise RuntimeError("No cases matched the card-selection filters.")

    summary_rows: list[dict[str, object]] = []
    for row in cards.itertuples(index=False):
        row_series = pd.Series(row._asdict())
        fig_path = figs_dir / f"{row.case_id}.png"
        md_path = cards_dir / f"{row.case_id}.md"
        render_card_png(row_series, fig_path, title=title)

        report_excerpt = parse_diagnostic_report_excerpt(first_existing_path(row_series.get("diagnostic_report_path")))
        log_excerpt = parse_system_log_excerpt(first_existing_path(row_series.get("system_log_path")))
        screenshot_path = first_existing_path(row_series.get("screenshot_path"))
        screenshot_rel = None
        if screenshot_path is not None:
            screenshot_rel = relative_path(md_path.parent, screenshot_path)
        fig_rel = relative_path(md_path.parent, fig_path)
        md_path.write_text(build_card_markdown(row_series, fig_rel, screenshot_rel, report_excerpt, log_excerpt))

        summary_rows.append(
            {
                "case_id": row.case_id,
                "workload": row.workload,
                "stressor": row.stressor,
                "card_status": row.card_status_label,
                "first_warning_s": safe_float(row.first_warning_s),
                "crash_time_s": safe_float(row.crash_time_s),
                "lead_time_s": safe_float(row.lead_time_s),
                "warning_source": row.warning_source,
                "crash_source": row.crash_source,
                "figure_path": str(fig_path),
                "markdown_path": str(md_path),
            }
        )

    summary_df = pd.DataFrame(summary_rows)
    summary_df.to_csv(out_dir / "crash_evidence_cards.csv", index=False)
    write_gallery_markdown(out_dir / "CRASH_EVIDENCE_GALLERY.md", cards, title=title)

    status = {
        "out_dir": str(out_dir),
        "alignment_csv": str(alignment_csv) if alignment_csv else "",
        "warning_csv": str(warning_csv) if warning_csv else "",
        "crash_manifest": str(crash_manifest) if crash_manifest else "",
        "n_cards": int(len(cards)),
        "include_noncrash": bool(include_noncrash),
        "max_cards": int(max_cards),
    }
    (out_dir / "crash_evidence_cards_status.json").write_text(json.dumps(status, indent=2) + "\n")
    return status


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate paper-ready crash evidence cards from DICE warning/crash artifacts.")
    ap.add_argument("--out_dir", "--out-dir", dest="out_dir", type=Path, required=True)
    ap.add_argument("--alignment_csv", "--alignment-csv", dest="alignment_csv", type=Path, default=None)
    ap.add_argument("--warning_csv", "--warning-csv", dest="warning_csv", type=Path, default=None)
    ap.add_argument("--crash_manifest", "--crash-manifest", dest="crash_manifest", type=Path, default=None)
    ap.add_argument("--title", default="DICE Crash Evidence Gallery")
    ap.add_argument("--include_noncrash", "--include-noncrash", dest="include_noncrash", action="store_true")
    ap.add_argument("--max_cards", "--max-cards", dest="max_cards", type=int, default=12)
    args = ap.parse_args()
    run(
        out_dir=args.out_dir,
        alignment_csv=args.alignment_csv,
        crash_manifest=args.crash_manifest,
        warning_csv=args.warning_csv,
        title=args.title,
        include_noncrash=args.include_noncrash,
        max_cards=args.max_cards,
    )


if __name__ == "__main__":
    main()
