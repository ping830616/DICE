#!/usr/bin/env python3
"""Feature-level warning-to-crash analysis for DICE crash pilots."""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


TIER_FILE_MAP = {
    "tier0": "tier0_full_5hz.csv",
    "tier1_alt": "tier1_alt_core_5hz.csv",
    "tier2": "tier2_core_5hz.csv",
}

TIER_DIR_MAP = {
    "tier0": "tier0",
    "tier1_alt": "tier1_alt",
    "tier2": "tier2",
}

CONFIG_LABELS = {
    "tier0": "Tier-0",
    "tier0_tier1": "Tier-0/1",
    "tier0_tier1_tier2": "Tier-0/1/2",
}


@dataclass(frozen=True)
class FeatureSpec:
    tier: str
    column: str

    @property
    def name(self) -> str:
        return f"{self.tier}:{self.column}"


def parse_feature_spec(value: str | None) -> FeatureSpec | None:
    text = str(value or "").strip()
    if not text or ":" not in text:
        return None
    tier, column = text.split(":", 1)
    tier = tier.strip()
    column = column.strip()
    if tier not in TIER_FILE_MAP or not column:
        return None
    return FeatureSpec(tier=tier, column=column)


def discover_itc_dataset_root(path: Path) -> Path | None:
    for parent in [path, *path.parents]:
        if parent.name == "ITC_M2Pro_DATA":
            return parent
    return None


def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def choose_final_config(diag_df: pd.DataFrame, warning_df: pd.DataFrame) -> str:
    for candidate in ["tier0_tier1_tier2", "tier0_tier1", "tier0"]:
        if not diag_df.empty and candidate in set(diag_df["config"].astype(str)):
            return candidate
        if not warning_df.empty and candidate in set(warning_df["config"].astype(str)):
            return candidate
    return "tier0_tier1_tier2"


def ordered_unique(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            out.append(value)
    return out


def markdown_table(df: pd.DataFrame) -> str:
    cols = [str(col) for col in df.columns]
    header = "| " + " | ".join(cols) + " |"
    rule = "| " + " | ".join(["---"] * len(cols)) + " |"
    rows = []
    for record in df.to_dict(orient="records"):
        vals = ["" if pd.isna(record.get(col)) else str(record.get(col)) for col in cols]
        rows.append("| " + " | ".join(vals) + " |")
    return "\n".join([header, rule, *rows])


def candidate_features(
    workload: str,
    base_stressor: str,
    warning_df: pd.DataFrame,
    diag_df: pd.DataFrame,
    reference_warning_df: pd.DataFrame,
    config: str,
) -> list[FeatureSpec]:
    candidates: list[str] = []
    stressors = [f"{base_stressor}_CONTROL", f"{base_stressor}_ABORT"]

    warn_rows = warning_df[
        (warning_df["workload"].astype(str) == workload)
        & (warning_df["stressor"].astype(str).isin(stressors))
        & (warning_df["config"].astype(str) == config)
    ].copy()
    for col in ["warning_top_feature_1", "warning_top_feature_2"]:
        if col in warn_rows.columns:
            candidates.extend(str(v) for v in warn_rows[col].tolist())

    diag_rows = diag_df[
        (diag_df["workload"].astype(str) == workload)
        & (diag_df["stressor"].astype(str).isin(stressors))
        & (diag_df["config"].astype(str) == config)
    ].copy()
    for rank in range(1, 6):
        col = f"top_feature_{rank}"
        if col in diag_rows.columns:
            candidates.extend(str(v) for v in diag_rows[col].tolist())

    ref_case_id = f"{workload}__{base_stressor}"
    ref_rows = reference_warning_df[reference_warning_df["case_id"].astype(str) == ref_case_id].copy()
    for col in ["warning_top_feature_1", "warning_top_feature_2"]:
        if col in ref_rows.columns:
            candidates.extend(str(v) for v in ref_rows[col].tolist())

    specs = [parse_feature_spec(value) for value in ordered_unique(candidates)]
    return [spec for spec in specs if spec is not None]


def case_signal_path(dataset_root: Path, case_id: str, tier: str) -> Path:
    return dataset_root / TIER_DIR_MAP[tier] / case_id / TIER_FILE_MAP[tier]


def load_feature_series(dataset_root: Path, case_id: str, feature: FeatureSpec) -> pd.DataFrame:
    path = case_signal_path(dataset_root, case_id, feature.tier)
    if not path.exists():
        return pd.DataFrame(columns=["time_s", "value"])
    usecols: list[str] = []
    header = pd.read_csv(path, nrows=0)
    cols = set(header.columns)
    for candidate in ["t_rel_s", "idx", feature.column]:
        if candidate in cols:
            usecols.append(candidate)
    if feature.column not in usecols:
        return pd.DataFrame(columns=["time_s", "value"])
    df = pd.read_csv(path, usecols=usecols)
    if "t_rel_s" in df.columns:
        time_s = pd.to_numeric(df["t_rel_s"], errors="coerce")
    elif "idx" in df.columns:
        time_s = pd.to_numeric(df["idx"], errors="coerce") / 5.0
    else:
        time_s = pd.Series(np.arange(len(df), dtype=float))
    value = pd.to_numeric(df[feature.column], errors="coerce")
    out = pd.DataFrame({"time_s": time_s, "value": value}).dropna(subset=["time_s"])
    return out.reset_index(drop=True)


def robust_scale(values: pd.Series) -> tuple[float, float]:
    arr = pd.to_numeric(values, errors="coerce").to_numpy(dtype=float)
    arr = arr[np.isfinite(arr)]
    if arr.size == 0:
        return 0.0, 1.0
    center = float(np.median(arr))
    mad = float(np.median(np.abs(arr - center)))
    scale = 1.4826 * mad
    if not np.isfinite(scale) or scale < 1e-9:
        scale = float(np.std(arr))
    if not np.isfinite(scale) or scale < 1e-9:
        scale = 1.0
    return center, scale


def nearest_value(series_df: pd.DataFrame, target_s: float) -> float:
    if series_df.empty or not np.isfinite(target_s):
        return float("nan")
    idx = (series_df["time_s"] - float(target_s)).abs().idxmin()
    return float(series_df.loc[idx, "value"])


def first_divergence_time(series_df: pd.DataFrame, center: float, scale: float, threshold: float) -> float:
    if series_df.empty:
        return float("nan")
    z = (pd.to_numeric(series_df["value"], errors="coerce") - center).abs() / scale
    mask = z >= float(threshold)
    if not bool(mask.fillna(False).any()):
        return float("nan")
    first_idx = mask[mask.fillna(False)].index[0]
    return float(series_df.loc[first_idx, "time_s"])


def value_pre_crash(series_df: pd.DataFrame, crash_time_s: float, lookback_s: float = 10.0) -> float:
    if series_df.empty or not np.isfinite(crash_time_s):
        return float("nan")
    part = series_df[(series_df["time_s"] >= crash_time_s - lookback_s) & (series_df["time_s"] <= crash_time_s)]
    if part.empty:
        return nearest_value(series_df, crash_time_s)
    return float(pd.to_numeric(part["value"], errors="coerce").median())


def smooth_series(series_df: pd.DataFrame, window: int = 5) -> pd.DataFrame:
    if series_df.empty:
        return series_df.copy()
    out = series_df.copy()
    out["value"] = pd.to_numeric(out["value"], errors="coerce").rolling(window, min_periods=1, center=True).median()
    return out


def robust_z_series(series_df: pd.DataFrame, center: float, scale: float) -> pd.DataFrame:
    if series_df.empty:
        return pd.DataFrame(columns=["time_s", "zscore"])
    out = series_df[["time_s", "value"]].copy()
    values = pd.to_numeric(out["value"], errors="coerce")
    out["zscore"] = (values - float(center)) / float(scale)
    return out[["time_s", "zscore"]]


def feature_available(dataset_root: Path, case_ids: Iterable[str], feature: FeatureSpec) -> bool:
    for case_id in case_ids:
        df = load_feature_series(dataset_root, case_id, feature)
        if not df.empty and pd.to_numeric(df["value"], errors="coerce").notna().any():
            return True
    return False


def plot_feature_panels(
    out_path: Path,
    title: str,
    selected_features: list[FeatureSpec],
    case_series: dict[str, dict[str, pd.DataFrame]],
    case_meta: dict[str, dict[str, float | str]],
    reference_warning_s: float,
) -> None:
    if not selected_features:
        return

    n = len(selected_features)
    ncols = 2 if n > 1 else 1
    nrows = math.ceil(n / ncols)
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(14, 3.8 * nrows), constrained_layout=True)
    if not isinstance(axes, np.ndarray):
        axes = np.asarray([axes])
    axes = axes.ravel()

    colors = {
        "NOMINAL": "#64748B",
        "CONTROL": "#2563EB",
        "ABORT": "#DC2626",
    }

    for ax, feature in zip(axes, selected_features):
        for mode, meta in case_meta.items():
            case_id = str(meta["case_id"])
            series_df = case_series[case_id][feature.name]
            if series_df.empty:
                continue
            smooth_df = smooth_series(series_df)
            ax.plot(
                smooth_df["time_s"],
                smooth_df["value"],
                label=mode.title(),
                color=colors[mode],
                linewidth=1.8,
                alpha=0.95,
            )
            warning_s = float(meta.get("warning_s", float("nan")))
            crash_s = float(meta.get("crash_s", float("nan")))
            if np.isfinite(warning_s):
                ax.axvline(warning_s, color=colors[mode], linestyle="--", linewidth=1.2, alpha=0.7)
            if mode == "ABORT" and np.isfinite(crash_s):
                ax.axvline(crash_s, color=colors[mode], linestyle="-", linewidth=1.4, alpha=0.8)

        if np.isfinite(reference_warning_s):
            ax.axvline(reference_warning_s, color="#111827", linestyle=":", linewidth=1.4, alpha=0.85)

        ax.set_title(feature.name, fontsize=10)
        ax.set_xlabel("Time from run start (s)")
        ax.set_ylabel("Raw feature value")
        ax.grid(alpha=0.22)

    for ax in axes[n:]:
        ax.axis("off")

    handles = [
        plt.Line2D([0], [0], color=colors["NOMINAL"], lw=2, label="Nominal"),
        plt.Line2D([0], [0], color=colors["CONTROL"], lw=2, label="Control"),
        plt.Line2D([0], [0], color=colors["ABORT"], lw=2, label="Abort"),
        plt.Line2D([0], [0], color="#2563EB", lw=1.2, linestyle="--", label="Pilot warning"),
        plt.Line2D([0], [0], color="#DC2626", lw=1.4, linestyle="-", label="Crash"),
        plt.Line2D([0], [0], color="#111827", lw=1.4, linestyle=":", label="Original ITC warning"),
    ]
    fig.legend(handles=handles, loc="upper center", ncol=6, frameon=False, bbox_to_anchor=(0.5, 1.02))
    fig.suptitle(title, fontsize=17)
    fig.savefig(out_path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def interpolate_to_grid(series_df: pd.DataFrame, grid_s: np.ndarray) -> np.ndarray:
    if series_df.empty:
        return np.full_like(grid_s, np.nan, dtype=float)
    part = series_df.copy()
    part = part.dropna(subset=["time_s"])
    part = part.sort_values("time_s")
    vals = pd.to_numeric(part["value"], errors="coerce").to_numpy(dtype=float)
    ts = pd.to_numeric(part["time_s"], errors="coerce").to_numpy(dtype=float)
    keep = np.isfinite(ts) & np.isfinite(vals)
    ts = ts[keep]
    vals = vals[keep]
    if len(ts) == 0:
        return np.full_like(grid_s, np.nan, dtype=float)
    if len(ts) == 1:
        return np.full_like(grid_s, vals[0], dtype=float)
    return np.interp(grid_s, ts, vals, left=vals[0], right=vals[-1])


def plot_feature_heatmaps(
    out_path: Path,
    title: str,
    selected_features: list[FeatureSpec],
    case_series: dict[str, dict[str, pd.DataFrame]],
    case_meta: dict[str, dict[str, float | str]],
    reference_warning_s: float,
) -> None:
    abort_case = str(case_meta["ABORT"]["case_id"])
    control_case = str(case_meta["CONTROL"]["case_id"])
    nominal_case = str(case_meta["NOMINAL"]["case_id"])

    grids = []
    max_time = 0.0
    for feature in selected_features:
        for case_id in [nominal_case, control_case, abort_case]:
            df = case_series[case_id][feature.name]
            if not df.empty:
                max_time = max(max_time, float(df["time_s"].max()))
    if max_time <= 0:
        return
    grid_s = np.arange(0.0, max_time + 1.0, 1.0, dtype=float)

    def build_matrix(case_id: str) -> np.ndarray:
        rows = []
        for feature in selected_features:
            nominal = case_series[nominal_case][feature.name]
            center, scale = robust_scale(nominal["value"])
            target = case_series[case_id][feature.name]
            aligned = interpolate_to_grid(target, grid_s)
            rows.append(np.clip((aligned - center) / scale, -6.0, 6.0))
        return np.asarray(rows, dtype=float)

    mats = {
        "CONTROL": build_matrix(control_case),
        "ABORT": build_matrix(abort_case),
    }

    fig, axes = plt.subplots(2, 1, figsize=(14, 1.0 + 0.65 * len(selected_features) * 2), sharex=True, constrained_layout=True)
    feature_labels = [feature.name for feature in selected_features]
    for ax, mode in zip(axes, ["CONTROL", "ABORT"]):
        mat = mats[mode]
        im = ax.imshow(
            mat,
            aspect="auto",
            origin="lower",
            cmap="coolwarm",
            extent=[grid_s.min(), grid_s.max(), -0.5, len(feature_labels) - 0.5],
            vmin=-4.0,
            vmax=4.0,
        )
        ax.set_yticks(range(len(feature_labels)))
        ax.set_yticklabels(feature_labels, fontsize=9)
        ax.set_title(f"{mode.title()} robust z-score vs nominal", fontsize=11)
        warning_s = float(case_meta[mode].get("warning_s", float("nan")))
        crash_s = float(case_meta[mode].get("crash_s", float("nan")))
        if np.isfinite(warning_s):
            ax.axvline(warning_s, color="#111827", linestyle="--", linewidth=1.4)
        if mode == "ABORT" and np.isfinite(crash_s):
            ax.axvline(crash_s, color="#DC2626", linestyle="-", linewidth=1.5)
        if np.isfinite(reference_warning_s):
            ax.axvline(reference_warning_s, color="#16A34A", linestyle=":", linewidth=1.3)
    axes[-1].set_xlabel("Time from run start (s)")
    cbar = fig.colorbar(im, ax=axes, location="right", shrink=0.9)
    cbar.set_label("Feature deviation (robust z-score)")
    fig.suptitle(title, fontsize=17)
    fig.savefig(out_path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def plot_feature_storyboard(
    out_path: Path,
    title: str,
    selected_features: list[FeatureSpec],
    case_series: dict[str, dict[str, pd.DataFrame]],
    case_meta: dict[str, dict[str, float | str]],
    reference_warning_s: float,
    z_threshold: float,
) -> None:
    if not selected_features:
        return

    nominal_case = str(case_meta["NOMINAL"]["case_id"])
    control_case = str(case_meta["CONTROL"]["case_id"])
    abort_case = str(case_meta["ABORT"]["case_id"])
    pilot_warning_s = float(case_meta["ABORT"].get("warning_s", float("nan")))
    crash_s = float(case_meta["ABORT"].get("crash_s", float("nan")))
    lead_time_s = crash_s - pilot_warning_s if np.isfinite(crash_s) and np.isfinite(pilot_warning_s) else float("nan")

    n = len(selected_features)
    fig, axes = plt.subplots(nrows=n, ncols=1, figsize=(14, 2.25 * n + 1.2), sharex=True, constrained_layout=True)
    if not isinstance(axes, np.ndarray):
        axes = np.asarray([axes])

    control_color = "#94A3B8"
    abort_color = "#355C7D"
    threshold_color = "#EF4444"
    reference_color = "#111827"
    pilot_color = "#F59E0B"
    crash_color = "#DC2626"

    for ax, feature in zip(axes, selected_features):
        nominal_series = case_series[nominal_case][feature.name]
        control_series = case_series[control_case][feature.name]
        abort_series = case_series[abort_case][feature.name]

        center, scale = robust_scale(nominal_series["value"])
        control_z = smooth_series(robust_z_series(control_series, center, scale).rename(columns={"zscore": "value"}))
        abort_z = smooth_series(robust_z_series(abort_series, center, scale).rename(columns={"zscore": "value"}))
        control_z = control_z.rename(columns={"value": "zscore"})
        abort_z = abort_z.rename(columns={"value": "zscore"})

        if not control_z.empty:
            ax.plot(control_z["time_s"], control_z["zscore"], color=control_color, linewidth=1.7, alpha=0.95)
        if not abort_z.empty:
            ax.plot(abort_z["time_s"], abort_z["zscore"], color=abort_color, linewidth=2.15, alpha=0.98)

        ax.axhline(0.0, color="#CBD5E1", linewidth=0.9, alpha=0.8)
        ax.axhline(z_threshold, color=threshold_color, linestyle="--", linewidth=1.2, alpha=0.85)
        ax.axhline(-z_threshold, color=threshold_color, linestyle="--", linewidth=0.9, alpha=0.45)

        if np.isfinite(reference_warning_s):
            ax.axvline(reference_warning_s, color=reference_color, linestyle=":", linewidth=1.35, alpha=0.9)
        if np.isfinite(pilot_warning_s):
            ax.axvspan(max(0.0, pilot_warning_s - 2.0), pilot_warning_s + 2.0, color="#FDE68A", alpha=0.23)
            ax.axvline(pilot_warning_s, color=pilot_color, linestyle="--", linewidth=1.5, alpha=0.95)
        if np.isfinite(crash_s):
            ax.axvline(crash_s, color=crash_color, linestyle="-", linewidth=1.6, alpha=0.95)

        ax.set_ylabel("Robust z", fontsize=10)
        ax.set_title(feature.name, fontsize=11, loc="left", fontweight="bold")
        ax.grid(axis="y", alpha=0.2)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    axes[-1].set_xlabel("Time from run start (s)")
    if np.isfinite(reference_warning_s):
        axes[0].annotate(
            f"Original warning {reference_warning_s:.0f}s",
            xy=(reference_warning_s, 0.98),
            xycoords=("data", "axes fraction"),
            xytext=(5, -6),
            textcoords="offset points",
            fontsize=10,
            color=reference_color,
            va="top",
            ha="left",
        )
    if np.isfinite(pilot_warning_s):
        axes[0].annotate(
            f"Pilot warning {pilot_warning_s:.0f}s",
            xy=(pilot_warning_s, 0.98),
            xycoords=("data", "axes fraction"),
            xytext=(5, -20),
            textcoords="offset points",
            fontsize=10,
            color=pilot_color,
            va="top",
            ha="left",
        )
    if np.isfinite(crash_s):
        crash_text = f"Crash {crash_s:.1f}s"
        if np.isfinite(lead_time_s):
            crash_text += f" | lead {lead_time_s:.1f}s"
        axes[0].annotate(
            crash_text,
            xy=(crash_s, 0.98),
            xycoords=("data", "axes fraction"),
            xytext=(5, -34),
            textcoords="offset points",
            fontsize=10,
            color=crash_color,
            va="top",
            ha="left",
        )

    handles = [
        plt.Line2D([0], [0], color=abort_color, lw=2.2, label="Abort robust z-score"),
        plt.Line2D([0], [0], color=control_color, lw=1.8, label="Control robust z-score"),
        plt.Line2D([0], [0], color=threshold_color, lw=1.2, linestyle="--", label=f"Divergence threshold (|z|={z_threshold:.1f})"),
        plt.Line2D([0], [0], color=reference_color, lw=1.4, linestyle=":", label="Original ITC warning"),
        plt.Line2D([0], [0], color=pilot_color, lw=1.5, linestyle="--", label="Crash-pilot warning"),
        plt.Line2D([0], [0], color=crash_color, lw=1.6, linestyle="-", label="Real crash"),
    ]
    fig.legend(handles=handles, loc="upper center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 1.02))
    fig.suptitle(title, fontsize=18, fontweight="bold")
    fig.savefig(out_path, dpi=240, bbox_inches="tight")
    plt.close(fig)


def feature_report(
    out_path: Path,
    workload: str,
    base_stressor: str,
    config: str,
    reference_warning_s: float,
    rows: pd.DataFrame,
) -> None:
    lines = [
        f"# Feature-Level Warning-to-Crash Analysis",
        "",
        f"- Workload: `{workload}`",
        f"- Stressor family: `{base_stressor}`",
        f"- Config: `{CONFIG_LABELS.get(config, config)}`",
        f"- Original ITC warning: `{reference_warning_s:.1f}s`" if np.isfinite(reference_warning_s) else "- Original ITC warning: unavailable",
        "",
        "## Feature onset summary",
        "",
        markdown_table(rows),
        "",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")


def run_feature_analysis(
    dataset_root: Path,
    result_dir: Path,
    warning_dir: Path,
    out_dir: Path,
    reference_warning_csv: Path | None,
    max_features: int,
    z_threshold: float,
) -> pd.DataFrame:
    result_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    case_inventory = load_csv(dataset_root / "case_inventory.csv")
    diag_df = load_csv(result_dir / "case_diagnosis_summary.csv")
    warning_df = load_csv(warning_dir / "early_warning_case_summary.csv")
    crash_align_df = load_csv(warning_dir / "early_warning_crash_alignment.csv")
    reference_warning_df = load_csv(reference_warning_csv) if reference_warning_csv else pd.DataFrame()

    if case_inventory.empty or warning_df.empty:
        return pd.DataFrame()

    config = choose_final_config(diag_df, warning_df)
    final_warning = warning_df[warning_df["config"].astype(str) == config].copy()
    final_align = crash_align_df[crash_align_df["config"].astype(str) == config].copy()
    final_diag = diag_df[diag_df["config"].astype(str) == config].copy()

    groups = (
        case_inventory[
            case_inventory["base_stressor"].astype(str).ne("NOMINAL")
            & case_inventory["crash_mode"].astype(str).ne("NONE")
        ][["workload", "base_stressor"]]
        .drop_duplicates()
        .sort_values(["workload", "base_stressor"])
    )

    all_rows: list[dict[str, object]] = []
    bridge_rows: list[dict[str, object]] = []
    figure_dir = out_dir / "figures"
    figure_dir.mkdir(parents=True, exist_ok=True)

    for item in groups.itertuples(index=False):
        workload = str(item.workload)
        base_stressor = str(item.base_stressor)
        nominal_case = f"{workload}__NOMINAL"
        control_case = f"{workload}__{base_stressor}_CONTROL"
        abort_case = f"{workload}__{base_stressor}_ABORT"
        case_ids = [nominal_case, control_case, abort_case]

        features = [
            feature
            for feature in candidate_features(
                workload=workload,
                base_stressor=base_stressor,
                warning_df=final_warning,
                diag_df=final_diag,
                reference_warning_df=reference_warning_df,
                config=config,
            )
            if feature_available(dataset_root, case_ids, feature)
        ]
        selected_features = features[:max_features]
        if not selected_features:
            continue

        ref_row = reference_warning_df[reference_warning_df["case_id"].astype(str) == f"{workload}__{base_stressor}"]
        reference_warning_s = float(pd.to_numeric(ref_row["first_warning_s"], errors="coerce").iloc[0]) if not ref_row.empty else float("nan")

        meta_rows = final_align[final_align["case_id"].astype(str).isin(case_ids)].copy()
        case_meta: dict[str, dict[str, float | str]] = {}
        ref_top_feature = ""
        ref_top_feature_2 = ""
        for case_id, mode in [(nominal_case, "NOMINAL"), (control_case, "CONTROL"), (abort_case, "ABORT")]:
            row = meta_rows[meta_rows["case_id"].astype(str) == case_id]
            if row.empty:
                case_meta[mode] = {"case_id": case_id, "warning_s": float("nan"), "crash_s": float("nan")}
                continue
            row0 = row.iloc[0]
            case_meta[mode] = {
                "case_id": case_id,
                "warning_s": float(pd.to_numeric(pd.Series([row0.get("first_warning_s")]), errors="coerce").iloc[0]),
                "crash_s": float(pd.to_numeric(pd.Series([row0.get("crash_time_s")]), errors="coerce").iloc[0]),
            }
        if not ref_row.empty:
            ref_top_feature = str(ref_row.iloc[0].get("warning_top_feature_1", "") or "")
            ref_top_feature_2 = str(ref_row.iloc[0].get("warning_top_feature_2", "") or "")

        case_series: dict[str, dict[str, pd.DataFrame]] = {}
        for case_id in case_ids:
            case_series[case_id] = {}
            for feature in selected_features:
                case_series[case_id][feature.name] = load_feature_series(dataset_root, case_id, feature)

        for feature in selected_features:
            nominal_series = case_series[nominal_case][feature.name]
            center, scale = robust_scale(nominal_series["value"])
            for mode, case_id in [("CONTROL", control_case), ("ABORT", abort_case)]:
                series_df = case_series[case_id][feature.name]
                warning_s = float(case_meta[mode]["warning_s"])
                crash_s = float(case_meta[mode]["crash_s"])
                all_rows.append(
                    {
                        "workload": workload,
                        "base_stressor": base_stressor,
                        "case_id": case_id,
                        "mode": mode,
                        "feature_name": feature.name,
                        "tier": feature.tier,
                        "column_name": feature.column,
                        "reference_warning_s": reference_warning_s,
                        "pilot_warning_s": warning_s,
                        "crash_time_s": crash_s,
                        "feature_first_divergence_s": first_divergence_time(series_df, center, scale, z_threshold),
                        "feature_value_at_warning": nearest_value(series_df, warning_s),
                        "feature_value_pre_crash": value_pre_crash(series_df, crash_s),
                        "nominal_median": center,
                        "nominal_scale": scale,
                        "peak_abs_z": float(
                            np.nanmax(
                                np.abs((pd.to_numeric(series_df["value"], errors="coerce").to_numpy(dtype=float) - center) / scale)
                            )
                        )
                        if not series_df.empty
                        else float("nan"),
                    }
                )

        group_tag = f"{workload.lower()}__{base_stressor.lower()}"
        storyboard_path = figure_dir / f"fig_feature_storyboard__{group_tag}.png"
        panel_path = figure_dir / f"feature_trajectories__{group_tag}.png"
        heatmap_path = figure_dir / f"feature_heatmap__{group_tag}.png"
        report_path = out_dir / f"FEATURE_CRASH_REPORT__{group_tag}.md"

        bridge_rows.append(
            {
                "workload": workload,
                "base_stressor": base_stressor,
                "original_case_id": f"{workload}__{base_stressor}",
                "original_warning_s": reference_warning_s,
                "original_top_feature_1": ref_top_feature,
                "original_top_feature_2": ref_top_feature_2,
                "pilot_control_case_id": control_case,
                "pilot_abort_case_id": abort_case,
                "pilot_warning_s": float(case_meta["ABORT"]["warning_s"]),
                "crash_time_s": float(case_meta["ABORT"]["crash_s"]),
                "warning_shift_s": (
                    float(case_meta["ABORT"]["warning_s"]) - reference_warning_s
                    if np.isfinite(reference_warning_s) and np.isfinite(float(case_meta["ABORT"]["warning_s"]))
                    else float("nan")
                ),
                "lead_time_s": (
                    float(case_meta["ABORT"]["crash_s"]) - float(case_meta["ABORT"]["warning_s"])
                    if np.isfinite(float(case_meta["ABORT"]["crash_s"])) and np.isfinite(float(case_meta["ABORT"]["warning_s"]))
                    else float("nan")
                ),
            }
        )

        plot_feature_storyboard(
            out_path=storyboard_path,
            title=f"{workload} / {base_stressor}: matched warning-to-crash feature storyboard",
            selected_features=selected_features,
            case_series=case_series,
            case_meta=case_meta,
            reference_warning_s=reference_warning_s,
            z_threshold=z_threshold,
        )

        plot_feature_panels(
            out_path=panel_path,
            title=f"{workload} / {base_stressor}: feature trajectories from anomaly to crash",
            selected_features=selected_features,
            case_series=case_series,
            case_meta=case_meta,
            reference_warning_s=reference_warning_s,
        )
        plot_feature_heatmaps(
            out_path=heatmap_path,
            title=f"{workload} / {base_stressor}: feature deviation heatmaps",
            selected_features=selected_features,
            case_series=case_series,
            case_meta=case_meta,
            reference_warning_s=reference_warning_s,
        )

        group_rows = pd.DataFrame([row for row in all_rows if row["workload"] == workload and row["base_stressor"] == base_stressor])
        feature_report(
            out_path=report_path,
            workload=workload,
            base_stressor=base_stressor,
            config=config,
            reference_warning_s=reference_warning_s,
            rows=group_rows,
        )

    out_df = pd.DataFrame(all_rows)
    if not out_df.empty:
        out_df = out_df.sort_values(["workload", "base_stressor", "mode", "tier", "feature_name"]).reset_index(drop=True)
        out_df.to_csv(out_dir / "feature_onset_summary.csv", index=False)
    bridge_df = pd.DataFrame(bridge_rows)
    if not bridge_df.empty:
        bridge_df = bridge_df.sort_values(["workload", "base_stressor"]).reset_index(drop=True)
        bridge_df.to_csv(out_dir / "warning_bridge_summary.csv", index=False)

    status = {
        "dataset_root": str(dataset_root),
        "result_dir": str(result_dir),
        "warning_dir": str(warning_dir),
        "reference_warning_csv": str(reference_warning_csv) if reference_warning_csv else "",
        "config": config,
        "groups_analyzed": sorted({f"{row['workload']}__{row['base_stressor']}" for row in all_rows}),
        "rows_written": int(len(out_df)),
        "bridge_rows_written": int(len(bridge_df)),
        "z_threshold": float(z_threshold),
    }
    (out_dir / "feature_crash_status.json").write_text(json.dumps(status, indent=2), encoding="utf-8")
    return out_df


def default_reference_warning_csv(dataset_root: Path) -> Path | None:
    itc_root = discover_itc_dataset_root(dataset_root)
    if itc_root is None:
        return None
    path = itc_root / "results_itc_paper" / "mixed" / "early_warning_case_summary.csv"
    return path if path.exists() else None


def parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="Generate feature-level warning-to-crash plots for DICE crash pilots.")
    ap.add_argument("--dataset_root", "--dataset-root", dest="dataset_root", type=Path, required=True)
    ap.add_argument("--result_dir", "--result-dir", dest="result_dir", type=Path, required=True)
    ap.add_argument("--warning_dir", "--warning-dir", dest="warning_dir", type=Path, required=True)
    ap.add_argument("--out_dir", "--out-dir", dest="out_dir", type=Path, required=True)
    ap.add_argument("--reference_warning_csv", "--reference-warning-csv", dest="reference_warning_csv", type=Path, default=None)
    ap.add_argument("--max_features", "--max-features", dest="max_features", type=int, default=6)
    ap.add_argument("--z_threshold", "--z-threshold", dest="z_threshold", type=float, default=2.5)
    return ap


def main() -> None:
    args = parser().parse_args()
    reference_warning_csv = args.reference_warning_csv if args.reference_warning_csv else default_reference_warning_csv(args.dataset_root)
    out_df = run_feature_analysis(
        dataset_root=args.dataset_root,
        result_dir=args.result_dir,
        warning_dir=args.warning_dir,
        out_dir=args.out_dir,
        reference_warning_csv=reference_warning_csv,
        max_features=max(1, int(args.max_features)),
        z_threshold=float(args.z_threshold),
    )
    print(f"[OK] feature-level rows: {len(out_df)}")
    print(f"[OK] wrote feature analysis to: {args.out_dir}")
    if reference_warning_csv:
        print(f"[OK] original ITC reference warning csv: {reference_warning_csv}")


if __name__ == "__main__":
    main()
