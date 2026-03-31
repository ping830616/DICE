#!/usr/bin/env python3
"""Crash-aware early-warning analysis for DICE results."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    balanced_accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


CONFIG_LABELS = {
    "tier0": "Tier-0",
    "tier0_tier1": "Tier-0/1",
    "tier0_tier1_tier2": "Tier-0/1/2",
}

PROFILE_LABELS = {
    "mixed": "Mixed",
    "full": "Full",
}

WORKLOAD_ORDER = ["BROWSER", "VIDEO_SW", "PY_AI", "PY_STATS"]
STRESSOR_ORDER = ["ATOMIC", "BRANCH", "CACHE", "MEMBW", "TLB", "NOMINAL"]
LEAD_TIME_THRESHOLDS_S = [30, 60, 120, 300]


def safe_div(num: float, den: float) -> float:
    den = float(den)
    if not np.isfinite(den) or abs(den) <= 1e-12:
        return float("nan")
    return float(num) / den


def finite_median(values: Iterable[float]) -> float:
    arr = np.asarray(list(values), dtype=float)
    arr = arr[np.isfinite(arr)]
    if arr.size == 0:
        return float("nan")
    return float(np.median(arr))


def finite_percentile(values: Iterable[float], q: float) -> float:
    arr = np.asarray(list(values), dtype=float)
    arr = arr[np.isfinite(arr)]
    if arr.size == 0:
        return float("nan")
    return float(np.percentile(arr, q))


def safe_auc(y_true: pd.Series, y_score: pd.Series) -> float:
    y = np.asarray(y_true, dtype=int)
    s = np.asarray(y_score, dtype=float)
    keep = np.isfinite(s)
    y = y[keep]
    s = s[keep]
    if len(np.unique(y)) < 2:
        return float("nan")
    return float(roc_auc_score(y, s))


def safe_ap(y_true: pd.Series, y_score: pd.Series) -> float:
    y = np.asarray(y_true, dtype=int)
    s = np.asarray(y_score, dtype=float)
    keep = np.isfinite(s)
    y = y[keep]
    s = s[keep]
    if len(np.unique(y)) < 2:
        return float("nan")
    return float(average_precision_score(y, s))


def infer_profile_label(feature_profile: str) -> str:
    return PROFILE_LABELS.get(str(feature_profile), str(feature_profile).title())


def ordered_categories(values: Iterable[object], preferred: list[str]) -> list[str]:
    observed = [str(value) for value in values if pd.notna(value)]
    extras = sorted({value for value in observed if value not in preferred})
    present_preferred = [value for value in preferred if value in observed]
    return [*present_preferred, *extras]


def ordered_stressor_categories(values: Iterable[object]) -> list[str]:
    observed = [str(value) for value in values if pd.notna(value)]
    base_order = {name: idx for idx, name in enumerate(STRESSOR_ORDER)}

    def key(name: str) -> tuple[int, int, str]:
        for variant_rank, suffix in enumerate(["", "_CONTROL", "_ABORT"]):
            if suffix and name.endswith(suffix):
                base = name[: -len(suffix)]
                return (base_order.get(base, len(base_order)), variant_rank, name)
        return (base_order.get(name, len(base_order)), 0, name)

    return sorted(set(observed), key=key)


def markdown_table(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    header = "| " + " | ".join(cols) + " |"
    rule = "| " + " | ".join(["---"] * len(cols)) + " |"
    rows = []
    for record in df.to_dict(orient="records"):
        vals = ["" if pd.isna(record.get(col)) else str(record.get(col)) for col in cols]
        rows.append("| " + " | ".join(vals) + " |")
    return "\n".join([header, rule, *rows])


def first_warning_block(blocks: pd.DataFrame) -> tuple[pd.Series | None, str]:
    ordered = blocks.sort_values(["block_idx", "score"], ascending=[True, False]).copy()
    candidates = [
        ("first_persistent_alert", ordered[ordered.get("persist_alert", 0) == 1]),
        ("first_block_alert", ordered[ordered.get("block_alert", 0) == 1]),
        ("diagnosis_selected_fallback", ordered[ordered.get("is_selected_for_diagnosis", 0) == 1]),
    ]
    for source, frame in candidates:
        if not frame.empty:
            return frame.iloc[0], source
    if ordered.empty:
        return None, "missing_blocks"
    return ordered.sort_values(["score", "block_idx"], ascending=[False, True]).iloc[0], "peak_score_fallback"


def build_warning_summary(
    case_pred: pd.DataFrame,
    block_df: pd.DataFrame,
    config: str,
    feature_profile: str | None = None,
) -> pd.DataFrame:
    pred = case_pred.copy()
    blocks = block_df.copy()

    if feature_profile and "feature_profile" in pred.columns:
        pred = pred[pred["feature_profile"].astype(str) == str(feature_profile)].copy()
    if feature_profile and "feature_profile" in blocks.columns:
        blocks = blocks[blocks["feature_profile"].astype(str) == str(feature_profile)].copy()

    pred = pred[pred["config"].astype(str) == str(config)].copy()
    blocks = blocks[blocks["config"].astype(str) == str(config)].copy()

    rows: list[dict[str, object]] = []
    for pred_row in pred.itertuples(index=False):
        case_blocks = blocks[blocks["case_id"] == pred_row.case_id].copy()
        warn_block, warn_source = first_warning_block(case_blocks)
        feature_profile_value = (
            getattr(pred_row, "feature_profile")
            if hasattr(pred_row, "feature_profile")
            else (feature_profile if feature_profile else "")
        )

        row = {
            "feature_profile": str(feature_profile_value),
            "profile_label": infer_profile_label(str(feature_profile_value)),
            "config": str(pred_row.config),
            "config_label": CONFIG_LABELS.get(str(pred_row.config), str(pred_row.config)),
            "case_id": str(pred_row.case_id),
            "workload": str(pred_row.workload),
            "stressor": str(pred_row.stressor),
            "label": int(pred_row.label),
            "run_score": float(getattr(pred_row, "run_score", np.nan)),
            "run_score_wc": float(getattr(pred_row, "run_score_wc", np.nan)),
            "run_alert": int(getattr(pred_row, "run_alert", 0)),
            "first_block_alert_s": float(getattr(pred_row, "first_block_alert_s", np.nan)),
            "time_to_detect_s": float(getattr(pred_row, "time_to_detect_s", np.nan)),
            "n_blocks": int(getattr(pred_row, "n_blocks", 0)),
            "warning_source": warn_source,
            "first_warning_s": float(getattr(pred_row, "time_to_detect_s", np.nan)),
            "first_warning_window_start_s": float("nan"),
            "first_warning_window_end_s": float("nan"),
            "first_warning_block_idx": float("nan"),
            "warning_dominant_tier": "",
            "warning_dominant_mechanism": "",
            "warning_top_feature_1": "",
            "warning_top_feature_score_1": float("nan"),
            "warning_top_feature_2": "",
            "warning_top_feature_score_2": float("nan"),
            "warning_threshold": float("nan"),
            "run_duration_s": float(case_blocks["block_end_s"].max()) if not case_blocks.empty else float("nan"),
        }

        if np.isfinite(row["first_block_alert_s"]) and not np.isfinite(row["first_warning_s"]):
            row["first_warning_s"] = row["first_block_alert_s"]

        alert_based_warning = warn_source in {"first_persistent_alert", "first_block_alert"} and np.isfinite(row["first_warning_s"])
        if warn_block is not None and alert_based_warning:
            row["first_warning_window_start_s"] = float(warn_block.get("block_start_s", np.nan))
            row["first_warning_window_end_s"] = float(warn_block.get("block_end_s", np.nan))
            row["first_warning_block_idx"] = float(warn_block.get("block_idx", np.nan))
            row["warning_dominant_tier"] = str(warn_block.get("dominant_tier", ""))
            row["warning_dominant_mechanism"] = str(warn_block.get("dominant_mechanism", ""))
            row["warning_top_feature_1"] = str(warn_block.get("top_feature_1", ""))
            row["warning_top_feature_score_1"] = float(warn_block.get("top_feature_score_1", np.nan))
            row["warning_top_feature_2"] = str(warn_block.get("top_feature_2", ""))
            row["warning_top_feature_score_2"] = float(warn_block.get("top_feature_score_2", np.nan))
            row["warning_threshold"] = float(warn_block.get("threshold", np.nan))
            if not np.isfinite(row["first_warning_s"]) and np.isfinite(row["first_warning_window_end_s"]):
                row["first_warning_s"] = row["first_warning_window_end_s"]
        else:
            row["warning_source"] = "no_detected_warning"
            row["first_warning_s"] = float("nan")

        row["warning_available"] = int(np.isfinite(row["first_warning_s"]))
        rows.append(row)

    out = pd.DataFrame(rows)
    if out.empty:
        return out
    workload_order = ordered_categories(out["workload"], WORKLOAD_ORDER)
    stressor_order = ordered_stressor_categories(out["stressor"])
    out["workload"] = pd.Categorical(out["workload"], workload_order, ordered=True)
    out["stressor"] = pd.Categorical(out["stressor"], stressor_order, ordered=True)
    return out.sort_values(["workload", "stressor", "case_id"]).reset_index(drop=True)


def normalize_crash_manifest(path: Path | None) -> pd.DataFrame:
    if path is None or not Path(path).exists():
        return pd.DataFrame(
            columns=[
                "case_id",
                "workload",
                "stressor",
                "crash_outcome_observed",
                "crash_detected",
                "crash_time_s",
                "run_start_utc",
                "run_end_utc",
                "monitor_duration_s",
                "crash_source",
                "crash_kind",
                "diagnostic_report_path",
                "system_log_path",
                "screenshot_path",
                "evidence_note",
            ]
        )

    manifest = pd.read_csv(path).copy()
    renamed = {col.lower(): col for col in manifest.columns}

    def resolve(*candidates: str, default: object = np.nan) -> pd.Series:
        for candidate in candidates:
            if candidate in manifest.columns:
                return manifest[candidate]
            lowered = candidate.lower()
            if lowered in renamed:
                return manifest[renamed[lowered]]
        return pd.Series([default] * len(manifest))

    out = pd.DataFrame()
    out["case_id"] = resolve("case_id", default="")
    out["workload"] = resolve("workload", default="")
    out["stressor"] = resolve("stressor", default="")
    out["run_start_utc"] = pd.to_datetime(resolve("run_start_utc", "run_start_time_utc"), utc=True, errors="coerce")
    out["run_end_utc"] = pd.to_datetime(resolve("run_end_utc", "run_end_time_utc"), utc=True, errors="coerce")
    out["crash_time_utc"] = pd.to_datetime(resolve("crash_time_utc", "first_crash_time_utc"), utc=True, errors="coerce")
    out["crash_time_s"] = pd.to_numeric(
        resolve("crash_time_s", "relative_crash_time_s", "first_crash_time_s"),
        errors="coerce",
    )
    out["monitor_duration_s"] = pd.to_numeric(
        resolve("monitor_duration_s", "run_duration_s"),
        errors="coerce",
    )
    out["crash_outcome_observed"] = pd.to_numeric(
        resolve("crash_outcome_observed", "outcome_observed", default=1),
        errors="coerce",
    ).fillna(1).astype(int)
    crash_detected = pd.to_numeric(
        resolve("crash_detected", "crash_found"),
        errors="coerce",
    )
    out["crash_detected"] = crash_detected
    out["crash_source"] = resolve("crash_source", default="")
    out["crash_kind"] = resolve("crash_kind", "event_kind", default="")
    out["diagnostic_report_path"] = resolve("diagnostic_report_path", default="")
    out["system_log_path"] = resolve("system_log_path", "log_show_path", default="")
    out["screenshot_path"] = resolve("screenshot_path", default="")
    out["evidence_note"] = resolve("evidence_note", "notes", default="")

    inferred_crash = (
        out["crash_time_s"].notna()
        | out["crash_time_utc"].notna()
        | out["diagnostic_report_path"].astype(str).str.len().gt(0)
        | out["crash_kind"].astype(str).str.len().gt(0)
    )
    out["crash_detected"] = out["crash_detected"].fillna(inferred_crash.astype(int)).astype(int)

    need_relative = out["crash_time_s"].isna() & out["crash_time_utc"].notna() & out["run_start_utc"].notna()
    out.loc[need_relative, "crash_time_s"] = (
        out.loc[need_relative, "crash_time_utc"] - out.loc[need_relative, "run_start_utc"]
    ).dt.total_seconds()

    need_duration = out["monitor_duration_s"].isna() & out["run_start_utc"].notna() & out["run_end_utc"].notna()
    out.loc[need_duration, "monitor_duration_s"] = (
        out.loc[need_duration, "run_end_utc"] - out.loc[need_duration, "run_start_utc"]
    ).dt.total_seconds()

    if out.empty:
        return out

    def pick_case_row(part: pd.DataFrame) -> pd.Series:
        crash_rows = part[part["crash_detected"] == 1].copy()
        if not crash_rows.empty:
            crash_rows = crash_rows.sort_values(["crash_time_s", "crash_time_utc"], na_position="last")
            return crash_rows.iloc[0]
        return part.iloc[0]

    grouped = [pick_case_row(part) for _, part in out.groupby("case_id", sort=False)]
    norm = pd.DataFrame(grouped).reset_index(drop=True)
    return norm.sort_values("case_id").reset_index(drop=True)


def merge_warning_and_crash(warning_df: pd.DataFrame, crash_df: pd.DataFrame) -> pd.DataFrame:
    if warning_df.empty:
        return warning_df.copy()

    if crash_df.empty:
        merged = warning_df.copy()
        merged["crash_outcome_observed"] = 0
        merged["crash_detected"] = 0
        merged["crash_time_s"] = np.nan
        merged["monitor_duration_s"] = merged["run_duration_s"]
        merged["crash_source"] = ""
        merged["crash_kind"] = ""
        merged["diagnostic_report_path"] = ""
        merged["system_log_path"] = ""
        merged["screenshot_path"] = ""
        merged["evidence_note"] = "No crash manifest was supplied for this run."
    else:
        merged = warning_df.merge(crash_df, on=["case_id"], how="left", suffixes=("", "_crash"))
        merged["workload"] = merged["workload"].fillna(merged.get("workload_crash"))
        merged["stressor"] = merged["stressor"].fillna(merged.get("stressor_crash"))
        merged["crash_outcome_observed"] = pd.to_numeric(merged["crash_outcome_observed"], errors="coerce").fillna(0).astype(int)
        merged["crash_detected"] = pd.to_numeric(merged["crash_detected"], errors="coerce").fillna(0).astype(int)
        merged["monitor_duration_s"] = pd.to_numeric(merged["monitor_duration_s"], errors="coerce")

    merged["lead_time_s"] = merged["crash_time_s"] - merged["first_warning_s"]
    merged["warning_before_crash"] = (
        merged["warning_available"].astype(bool)
        & merged["crash_detected"].astype(bool)
        & np.isfinite(merged["lead_time_s"])
        & (merged["lead_time_s"] >= 0.0)
    ).astype(int)
    merged["late_warning_after_crash"] = (
        merged["warning_available"].astype(bool)
        & merged["crash_detected"].astype(bool)
        & np.isfinite(merged["lead_time_s"])
        & (merged["lead_time_s"] < 0.0)
    ).astype(int)
    merged["warning_without_observed_crash"] = (
        merged["warning_available"].astype(bool)
        & merged["crash_outcome_observed"].astype(bool)
        & ~merged["crash_detected"].astype(bool)
    ).astype(int)
    merged["missing_warning_before_crash"] = (
        merged["crash_detected"].astype(bool) & ~merged["warning_before_crash"].astype(bool)
    ).astype(int)
    return merged


def compute_detection_metrics(case_pred: pd.DataFrame, config: str, feature_profile: str | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    pred = case_pred.copy()
    if feature_profile and "feature_profile" in pred.columns:
        pred = pred[pred["feature_profile"].astype(str) == str(feature_profile)].copy()
    pred = pred[pred["config"].astype(str) == str(config)].copy()
    if pred.empty:
        return pd.DataFrame(), pd.DataFrame()

    def summarize(part: pd.DataFrame, scope: str, value: str) -> dict[str, object]:
        y_true = part["label"].astype(int)
        y_score = part["run_score"].astype(float)
        y_pred = part["run_alert"].astype(int)
        tn = int(((y_true == 0) & (y_pred == 0)).sum())
        fp = int(((y_true == 0) & (y_pred == 1)).sum())
        fn = int(((y_true == 1) & (y_pred == 0)).sum())
        tp = int(((y_true == 1) & (y_pred == 1)).sum())
        return {
            "feature_profile": str(part["feature_profile"].iloc[0]) if "feature_profile" in part.columns else (feature_profile or ""),
            "profile_label": infer_profile_label(str(part["feature_profile"].iloc[0])) if "feature_profile" in part.columns else infer_profile_label(feature_profile or ""),
            "config": config,
            "config_label": CONFIG_LABELS.get(config, config),
            "scope": scope,
            "scope_value": value,
            "n_cases": int(len(part)),
            "n_positive": int((y_true == 1).sum()),
            "n_negative": int((y_true == 0).sum()),
            "roc_auc": safe_auc(y_true, y_score),
            "pr_auc": safe_ap(y_true, y_score),
            "precision": float(precision_score(y_true, y_pred, zero_division=0)),
            "recall": float(recall_score(y_true, y_pred, zero_division=0)),
            "f1_score": float(f1_score(y_true, y_pred, zero_division=0)),
            "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
            "specificity": safe_div(tn, tn + fp),
            "false_alarm_rate": safe_div(fp, tn + fp),
            "true_positive_rate": safe_div(tp, tp + fn),
            "benign_alert_rate": safe_div(fp, tn + fp),
            "anomaly_detect_rate": safe_div(tp, tp + fn),
            "median_time_to_detect_s": finite_median(part.loc[(part["label"] == 1) & (part["run_alert"] == 1), "time_to_detect_s"]),
        }

    overall_rows = [summarize(pred, "overall", "ALL")]
    workload_rows = [summarize(part, "workload", workload) for workload, part in pred.groupby("workload", sort=False, observed=False)]
    return pd.DataFrame(overall_rows), pd.DataFrame(workload_rows)


def compute_early_warning_metrics(merged: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    if merged.empty:
        return pd.DataFrame(), pd.DataFrame()

    def summarize(part: pd.DataFrame, scope: str, value: str) -> dict[str, object]:
        observed = part[part["crash_outcome_observed"] == 1].copy()
        crash = observed[observed["crash_detected"] == 1].copy()
        noncrash = observed[observed["crash_detected"] == 0].copy()
        tp = int(crash["warning_before_crash"].sum())
        fn = int(len(crash) - tp)
        fp = int(noncrash["warning_available"].sum())
        tn = int(len(noncrash) - fp)
        hit_rows = crash[crash["warning_before_crash"] == 1].copy()
        monitored_hours = pd.to_numeric(noncrash["monitor_duration_s"], errors="coerce").fillna(0.0).sum() / 3600.0
        row = {
            "feature_profile": str(part["feature_profile"].iloc[0]) if "feature_profile" in part.columns else "",
            "profile_label": infer_profile_label(str(part["feature_profile"].iloc[0])) if "feature_profile" in part.columns else "",
            "config": str(part["config"].iloc[0]),
            "config_label": CONFIG_LABELS.get(str(part["config"].iloc[0]), str(part["config"].iloc[0])),
            "scope": scope,
            "scope_value": value,
            "n_cases": int(len(part)),
            "observed_outcomes": int(len(observed)),
            "observed_crashes": int(len(crash)),
            "observed_noncrashes": int(len(noncrash)),
            "warning_precision": safe_div(tp, tp + fp),
            "warning_recall_before_crash": safe_div(tp, tp + fn),
            "warning_f1": safe_div(2.0 * tp, (2.0 * tp) + fp + fn),
            "warning_balanced_accuracy": safe_div(
                safe_div(tp, tp + fn) + safe_div(tn, tn + fp),
                2.0,
            ),
            "late_warning_rate": safe_div(int(crash["late_warning_after_crash"].sum()), len(crash)),
            "false_alarm_rate_runs": safe_div(fp, fp + tn),
            "false_alarm_rate_per_monitored_hour": safe_div(fp, monitored_hours),
            "median_lead_time_s": finite_median(hit_rows["lead_time_s"]),
            "mean_lead_time_s": float(hit_rows["lead_time_s"].mean()) if not hit_rows.empty else float("nan"),
            "p10_lead_time_s": finite_percentile(hit_rows["lead_time_s"], 10),
            "p90_lead_time_s": finite_percentile(hit_rows["lead_time_s"], 90),
        }
        for threshold in LEAD_TIME_THRESHOLDS_S:
            row[f"lead_time_ge_{threshold}s_rate"] = safe_div(
                int((hit_rows["lead_time_s"] >= float(threshold)).sum()),
                len(crash),
            )
        return row

    overall = pd.DataFrame([summarize(merged, "overall", "ALL")])
    by_workload = pd.DataFrame(
        [summarize(part, "workload", workload) for workload, part in merged.groupby("workload", sort=False, observed=False)]
    )
    return overall, by_workload


def plot_warning_timeline(merged: pd.DataFrame, out_png: Path) -> None:
    if merged.empty:
        return

    plot_df = merged.copy()
    plot_df["sort_lead"] = plot_df["lead_time_s"].where(plot_df["warning_before_crash"] == 1, np.nan)
    plot_df = plot_df.sort_values(
        ["warning_before_crash", "sort_lead", "workload", "stressor"],
        ascending=[False, False, True, True],
        na_position="last",
    ).reset_index(drop=True)
    labels = [f"{row.workload} / {row.stressor}" for row in plot_df.itertuples(index=False)]
    ypos = np.arange(len(plot_df))

    fig_height = max(4.5, 0.35 * len(plot_df) + 1.2)
    fig, ax = plt.subplots(figsize=(11.5, fig_height))
    run_end = pd.to_numeric(plot_df["monitor_duration_s"], errors="coerce").fillna(plot_df["run_duration_s"])
    for idx, row in enumerate(plot_df.itertuples(index=False)):
        if np.isfinite(run_end.iloc[idx]):
            ax.hlines(idx, 0.0, float(run_end.iloc[idx]), color="#E2E8F0", linewidth=2.0, zorder=1)

    warning_mask = np.isfinite(plot_df["first_warning_s"])
    crash_mask = np.isfinite(plot_df["crash_time_s"])
    ax.scatter(plot_df.loc[warning_mask, "first_warning_s"], ypos[warning_mask], s=55, color="#2563EB", label="First warning", zorder=3)
    ax.scatter(plot_df.loc[crash_mask, "crash_time_s"], ypos[crash_mask], s=75, marker="X", color="#DC2626", label="Crash", zorder=4)

    if crash_mask.any():
        for idx, row in enumerate(plot_df.itertuples(index=False)):
            if np.isfinite(row.first_warning_s) and np.isfinite(row.crash_time_s):
                color = "#16A34A" if row.warning_before_crash else "#F59E0B"
                ax.hlines(idx, float(row.first_warning_s), float(row.crash_time_s), color=color, linewidth=2.4, alpha=0.9, zorder=2)

    ax.set_yticks(ypos, labels)
    ax.set_xlabel("Time from run start (s)")
    ax.set_title("First anomaly warning versus first crash event")
    ax.grid(axis="x", color="#CBD5E1", alpha=0.35)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.invert_yaxis()
    ax.legend(loc="lower right")
    fig.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=220, bbox_inches="tight")
    plt.close(fig)


def plot_lead_time_distribution(merged: pd.DataFrame, out_png: Path) -> None:
    hit_rows = merged[(merged["warning_before_crash"] == 1) & np.isfinite(merged["lead_time_s"])].copy()
    fig, ax = plt.subplots(figsize=(8.4, 4.8))
    if hit_rows.empty:
        ax.text(0.5, 0.5, "No crash-alignment rows with a valid lead time are available yet.", ha="center", va="center", fontsize=12)
        ax.set_axis_off()
    else:
        lead = hit_rows["lead_time_s"].to_numpy(dtype=float)
        bins = min(8, max(4, int(np.sqrt(len(lead))) + 1))
        ax.hist(lead, bins=bins, color="#2563EB", edgecolor="white", alpha=0.9)
        ax.axvline(np.median(lead), color="#DC2626", linestyle="--", linewidth=2.0, label=f"Median = {np.median(lead):.1f}s")
        ax.set_xlabel("Lead time from first warning to crash (s)")
        ax.set_ylabel("Cases")
        ax.set_title("Crash lead-time distribution")
        ax.grid(axis="y", color="#CBD5E1", alpha=0.35)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.legend(loc="upper right")
    fig.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=220, bbox_inches="tight")
    plt.close(fig)


def plot_lead_time_by_workload(by_workload: pd.DataFrame, out_png: Path) -> None:
    fig, ax = plt.subplots(figsize=(8.8, 4.8))
    if by_workload.empty or by_workload["observed_crashes"].fillna(0).sum() == 0:
        ax.text(0.5, 0.5, "No crash manifest with workload-level outcomes is available yet.", ha="center", va="center", fontsize=12)
        ax.set_axis_off()
    else:
        view = by_workload.copy()
        view["workload"] = view["scope_value"]
        view = view[view["scope"] == "workload"].copy()
        workload_order = ordered_categories(view["workload"], WORKLOAD_ORDER)
        view["workload"] = pd.Categorical(view["workload"], workload_order, ordered=True)
        view = view.sort_values("workload")
        xpos = np.arange(len(view))
        ax.bar(xpos, view["warning_recall_before_crash"], color="#2563EB", width=0.48, label="Warning recall")
        ax.plot(xpos, view["lead_time_ge_60s_rate"], color="#DC2626", marker="o", linewidth=2.0, label="Lead time >= 60s")
        ax.set_xticks(xpos, list(view["workload"]))
        ax.set_ylim(0.0, 1.05)
        ax.set_ylabel("Rate")
        ax.set_title("Crash-warning coverage by workload")
        ax.grid(axis="y", color="#CBD5E1", alpha=0.35)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.legend(loc="upper right")
    fig.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=220, bbox_inches="tight")
    plt.close(fig)


def write_markdown_report(
    out_path: Path,
    detection_overall: pd.DataFrame,
    warning_overall: pd.DataFrame,
    warning_cases: pd.DataFrame,
    crash_manifest_path: Path | None,
) -> None:
    lines = [
        "# DICE Early-Warning Analysis",
        "",
        "## What This Export Contains",
        "",
        "- `anomaly_detection_metrics.csv`: run-level ROC-AUC, PR-AUC, precision, recall, F1-score, and balanced accuracy for the selected DICE operating point.",
        "- `early_warning_case_summary.csv`: first warning time for each case, derived from the first persistent abnormal window when available.",
        "- `early_warning_crash_alignment.csv`: merged case-level warning and crash evidence table.",
        "- `early_warning_metrics.csv`: early-warning precision, recall-before-crash, lead-time statistics, and false-alarm measures.",
        "- `fig_early_warning_timeline.png`: warning and crash timing for each case.",
        "- `fig_early_warning_lead_time_distribution.png`: lead-time distribution for cases where a warning preceded a crash.",
        "",
        "## Metric Interpretation",
        "",
        "- `ROC-AUC` and `PR-AUC` measure ranking quality before an alert threshold is fixed. Higher values mean the digital twin separates benign and anomalous runs more cleanly.",
        "- `Precision`, `Recall`, and `F1-score` describe the chosen alert operating point. In a deployed system, high precision limits alarm fatigue, while high recall limits missed anomalies.",
        "- `Warning recall before crash` measures how often the first anomaly arrives before the first observed crash. This is the core early-warning metric for predictive maintenance.",
        "- `Median lead time` and `lead_time_ge_*` rates measure how much operator response time DICE provides after the first warning. Larger values are better.",
        "- `False alarm rate per monitored hour` measures how often DICE would trigger on runs with an observed non-crash outcome. Lower values are better for long-lived monitoring deployments.",
        "",
    ]

    if crash_manifest_path is None or not crash_manifest_path.exists():
        lines.extend(
            [
                "## Crash-Evidence Status",
                "",
                "No crash manifest was supplied for this export, so crash-specific precision, recall, and lead-time claims remain unavailable.",
                "The warning-time tables and plots are still useful because they define the anomaly timestamps that will be paired with crash evidence in future collections.",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "## Crash-Evidence Status",
                "",
                f"Crash manifest used: `{crash_manifest_path}`",
                "",
            ]
        )

    if not detection_overall.empty:
        d = detection_overall.iloc[0]
        lines.extend(
            [
                "## Headline Monitoring Result",
                "",
                (
                    f"The selected {d['profile_label']} {d['config_label']} operating point achieves "
                    f"ROC-AUC {d['roc_auc']:.4f}, PR-AUC {d['pr_auc']:.4f}, precision {d['precision']:.4f}, "
                    f"recall {d['recall']:.4f}, and F1-score {d['f1_score']:.4f}."
                ),
                "",
            ]
        )

    if not warning_overall.empty:
        w = warning_overall.iloc[0]
        observed_crashes = int(w.get("observed_crashes", 0))
        if observed_crashes > 0:
            lines.extend(
                [
                    "## Headline Early-Warning Result",
                    "",
                    (
                        f"Across {observed_crashes} observed crashes, DICE warns before the crash in "
                        f"{100.0 * float(w['warning_recall_before_crash']):.1f}% of cases, with a median lead time "
                        f"of {float(w['median_lead_time_s']):.1f}s."
                    ),
                    "",
                ]
            )

    if not warning_cases.empty:
        preview = warning_cases[
            [
                "case_id",
                "workload",
                "stressor",
                "first_warning_s",
                "crash_time_s",
                "lead_time_s",
                "warning_source",
            ]
        ].head(8)
        lines.extend(["## Case Preview", "", markdown_table(preview), ""])

    out_path.write_text("\n".join(lines).rstrip() + "\n")


def run_analysis(
    result_dir: Path,
    out_dir: Path,
    crash_manifest: Path | None = None,
    config: str = "tier0_tier1_tier2",
    feature_profile: str | None = None,
) -> dict[str, object]:
    result_dir = Path(result_dir)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    pred_path = result_dir / "case_predictions.csv"
    trace_path = result_dir / "case_block_traces.csv"
    if not pred_path.exists():
        raise FileNotFoundError(f"Missing predictions file: {pred_path}")
    if not trace_path.exists():
        raise FileNotFoundError(f"Missing block trace file: {trace_path}")

    case_pred = pd.read_csv(pred_path)
    block_df = pd.read_csv(trace_path)

    inferred_profile = feature_profile
    if inferred_profile is None and "feature_profile" in case_pred.columns:
        values = [v for v in case_pred["feature_profile"].dropna().astype(str).unique() if v]
        if len(values) == 1:
            inferred_profile = values[0]

    detection_overall, detection_by_workload = compute_detection_metrics(case_pred, config=config, feature_profile=inferred_profile)
    warning_summary = build_warning_summary(case_pred, block_df, config=config, feature_profile=inferred_profile)
    crash_df = normalize_crash_manifest(crash_manifest)
    merged = merge_warning_and_crash(warning_summary, crash_df)
    warning_overall, warning_by_workload = compute_early_warning_metrics(merged)

    detection_overall.to_csv(out_dir / "anomaly_detection_metrics.csv", index=False)
    detection_by_workload.to_csv(out_dir / "anomaly_detection_by_workload.csv", index=False)
    warning_summary.to_csv(out_dir / "early_warning_case_summary.csv", index=False)
    merged.to_csv(out_dir / "early_warning_crash_alignment.csv", index=False)
    warning_overall.to_csv(out_dir / "early_warning_metrics.csv", index=False)
    warning_by_workload.to_csv(out_dir / "early_warning_by_workload.csv", index=False)

    plot_warning_timeline(merged, out_dir / "fig_early_warning_timeline.png")
    plot_lead_time_distribution(merged, out_dir / "fig_early_warning_lead_time_distribution.png")
    plot_lead_time_by_workload(warning_by_workload, out_dir / "fig_early_warning_by_workload.png")

    write_markdown_report(
        out_dir / "EARLY_WARNING_REPORT.md",
        detection_overall,
        warning_overall,
        merged,
        crash_manifest,
    )

    status = {
        "result_dir": str(result_dir),
        "out_dir": str(out_dir),
        "config": config,
        "feature_profile": inferred_profile or "",
        "crash_manifest": str(crash_manifest) if crash_manifest else "",
        "crash_manifest_exists": bool(crash_manifest and crash_manifest.exists()),
        "n_cases": int(len(warning_summary)),
        "n_observed_crashes": int(warning_overall["observed_crashes"].iloc[0]) if not warning_overall.empty else 0,
    }
    (out_dir / "early_warning_status.json").write_text(json.dumps(status, indent=2) + "\n")
    return status


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate crash-aware early-warning analysis from saved DICE results.")
    ap.add_argument("--result_dir", "--result-dir", dest="result_dir", type=Path, required=True)
    ap.add_argument("--out_dir", "--out-dir", dest="out_dir", type=Path, required=True)
    ap.add_argument("--crash_manifest", "--crash-manifest", dest="crash_manifest", type=Path, default=None)
    ap.add_argument("--config", default="tier0_tier1_tier2")
    ap.add_argument("--feature_profile", "--feature-profile", dest="feature_profile", default=None)
    args = ap.parse_args()
    run_analysis(
        result_dir=args.result_dir,
        out_dir=args.out_dir,
        crash_manifest=args.crash_manifest,
        config=args.config,
        feature_profile=args.feature_profile,
    )


if __name__ == "__main__":
    main()
