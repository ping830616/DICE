#!/usr/bin/env python3
"""Aggregate workload-matched crash pilots into an ITC-study crash bridge."""

from __future__ import annotations

import argparse
import json
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import patches
import numpy as np
import pandas as pd


WORKLOAD_ORDER = ["BROWSER", "VIDEO_SW", "PY_AI", "PY_STATS"]
STRESSOR_ORDER = ["ATOMIC", "BRANCH", "CACHE", "MEMBW", "TLB", "NOMINAL"]
GENERIC_CRASH_COLUMNS = {"uptime_s"}


def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def workload_key(name: str) -> tuple[int, str]:
    return (WORKLOAD_ORDER.index(name), name) if name in WORKLOAD_ORDER else (len(WORKLOAD_ORDER), name)


def stressor_key(name: str) -> tuple[int, str]:
    return (STRESSOR_ORDER.index(name), name) if name in STRESSOR_ORDER else (len(STRESSOR_ORDER), name)


def ordered_sort(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df.copy()
    out = df.copy()
    out["_workload_order"] = out["workload"].astype(str).map(lambda value: workload_key(value)[0])
    out["_stressor_order"] = out["stressor"].astype(str).map(lambda value: stressor_key(value)[0])
    out = out.sort_values(["_workload_order", "_stressor_order", "case_id"]).drop(columns=["_workload_order", "_stressor_order"])
    return out.reset_index(drop=True)


def shorten_feature(value: object) -> str:
    text = str(value or "").strip()
    if not text or text.lower() == "nan":
        return ""
    return text.replace("tier0:", "T0:").replace("tier1_alt:", "T1:").replace("tier2:", "T2:")


def format_feature_pair(first: object, second: object) -> str:
    items = [shorten_feature(first), shorten_feature(second)]
    items = [item for item in items if item]
    if not items:
        return "—"
    return "\n".join(items)


def wrap_cell(text: str, width: int = 22) -> str:
    if text == "—":
        return text
    parts = [part for part in str(text).split("\n") if part]
    wrapped: list[str] = []
    for part in parts:
        wrapped.extend(textwrap.wrap(part, width=width) or [part])
    return "\n".join(wrapped)


def pick_peak_features(feature_df: pd.DataFrame) -> dict[str, object]:
    cols = {
        "crash_peak_feature_1": "",
        "crash_peak_feature_1_peak_abs_z": float("nan"),
        "crash_peak_feature_1_first_divergence_s": float("nan"),
        "crash_peak_feature_1_value_pre_crash": float("nan"),
        "crash_peak_feature_2": "",
        "crash_peak_feature_2_peak_abs_z": float("nan"),
        "crash_peak_feature_2_first_divergence_s": float("nan"),
        "crash_peak_feature_2_value_pre_crash": float("nan"),
    }
    if feature_df.empty:
        return cols

    abort_df = feature_df[feature_df["mode"].astype(str) == "ABORT"].copy()
    if abort_df.empty:
        return cols

    abort_df["is_generic"] = abort_df["column_name"].astype(str).isin(GENERIC_CRASH_COLUMNS)
    abort_df["missing_divergence"] = ~pd.to_numeric(abort_df["feature_first_divergence_s"], errors="coerce").notna()
    abort_df["peak_abs_z"] = pd.to_numeric(abort_df["peak_abs_z"], errors="coerce")
    abort_df["feature_first_divergence_s"] = pd.to_numeric(abort_df["feature_first_divergence_s"], errors="coerce")
    abort_df["feature_value_pre_crash"] = pd.to_numeric(abort_df["feature_value_pre_crash"], errors="coerce")
    abort_df = abort_df.sort_values(
        ["is_generic", "peak_abs_z", "missing_divergence", "feature_first_divergence_s", "feature_name"],
        ascending=[True, False, True, True, True],
    )
    abort_df = abort_df.drop_duplicates(subset=["feature_name"], keep="first").reset_index(drop=True)

    for rank in [1, 2]:
        if len(abort_df) < rank:
            continue
        row = abort_df.iloc[rank - 1]
        cols[f"crash_peak_feature_{rank}"] = str(row.get("feature_name", "") or "")
        cols[f"crash_peak_feature_{rank}_peak_abs_z"] = float(row.get("peak_abs_z", np.nan))
        cols[f"crash_peak_feature_{rank}_first_divergence_s"] = float(row.get("feature_first_divergence_s", np.nan))
        cols[f"crash_peak_feature_{rank}_value_pre_crash"] = float(row.get("feature_value_pre_crash", np.nan))
    return cols


def collect_pilot_rows(pilot_root: Path, profile: str) -> list[dict[str, object]]:
    feature_dir = pilot_root / "results_feature_crash_analysis" / profile
    bridge_csv = feature_dir / "warning_bridge_summary.csv"
    feature_csv = feature_dir / "feature_onset_summary.csv"
    pilot_warning_csv = pilot_root / "results_workload_crash_paper" / profile / "early_warning_case_summary.csv"
    if not bridge_csv.exists():
        return []

    bridge_df = load_csv(bridge_csv)
    feature_df = load_csv(feature_csv)
    pilot_warning_df = load_csv(pilot_warning_csv)
    rows: list[dict[str, object]] = []

    for record in bridge_df.to_dict(orient="records"):
        workload = str(record.get("workload", "") or "")
        stressor = str(record.get("base_stressor", "") or "")
        abort_case = str(record.get("pilot_abort_case_id", "") or "")
        control_case = str(record.get("pilot_control_case_id", "") or "")
        case_feature_df = feature_df[
            (feature_df["workload"].astype(str) == workload)
            & (feature_df["base_stressor"].astype(str) == stressor)
        ].copy()
        peak_cols = pick_peak_features(case_feature_df)

        abort_warning = pilot_warning_df[pilot_warning_df["case_id"].astype(str) == abort_case]
        abort_row = abort_warning.iloc[0] if not abort_warning.empty else pd.Series(dtype=object)

        feature_storyboard_path = feature_dir / "figures" / f"fig_feature_storyboard__{workload.lower()}__{stressor.lower()}.png"

        rows.append(
            {
                "pilot_root_name": pilot_root.name,
                "pilot_root_path": str(pilot_root),
                "pilot_root_mtime": float(bridge_csv.stat().st_mtime),
                "workload": workload,
                "stressor": stressor,
                "original_case_id": str(record.get("original_case_id", "") or ""),
                "original_anomaly_warning_s": float(pd.to_numeric(pd.Series([record.get("original_anomaly_warning_s")]), errors="coerce").iloc[0]),
                "original_top_feature_1": str(record.get("original_top_feature_1", "") or ""),
                "original_top_feature_2": str(record.get("original_top_feature_2", "") or ""),
                "crash_pilot_control_case_id": control_case,
                "crash_pilot_abort_case_id": abort_case,
                "crash_pilot_anomaly_warning_s": float(
                    pd.to_numeric(pd.Series([record.get("crash_pilot_anomaly_warning_s")]), errors="coerce").iloc[0]
                ),
                "crash_time_s": float(pd.to_numeric(pd.Series([record.get("crash_time_s")]), errors="coerce").iloc[0]),
                "lead_time_s": float(pd.to_numeric(pd.Series([record.get("lead_time_s")]), errors="coerce").iloc[0]),
                "anomaly_warning_shift_s": float(
                    pd.to_numeric(pd.Series([record.get("anomaly_warning_shift_s")]), errors="coerce").iloc[0]
                ),
                "crash_pilot_warning_dominant_tier": str(abort_row.get("warning_dominant_tier", "") or ""),
                "crash_pilot_warning_dominant_mechanism": str(abort_row.get("warning_dominant_mechanism", "") or ""),
                "crash_pilot_warning_top_feature_1": str(abort_row.get("warning_top_feature_1", "") or ""),
                "crash_pilot_warning_top_feature_2": str(abort_row.get("warning_top_feature_2", "") or ""),
                "feature_storyboard_path": str(feature_storyboard_path) if feature_storyboard_path.exists() else "",
                **peak_cols,
            }
        )
    return rows


def choose_latest_pilots(pilot_rows: list[dict[str, object]]) -> pd.DataFrame:
    if not pilot_rows:
        return pd.DataFrame()
    df = pd.DataFrame(pilot_rows)
    df = df.sort_values(["original_case_id", "pilot_root_mtime"], ascending=[True, False]).drop_duplicates(
        subset=["original_case_id"], keep="first"
    )
    return df.reset_index(drop=True)


def build_full_summary(itc_root: Path, profile: str, pilot_df: pd.DataFrame) -> pd.DataFrame:
    original_csv = itc_root / "results_itc_paper" / profile / "early_warning_case_summary.csv"
    original_df = load_csv(original_csv)
    if original_df.empty:
        return pd.DataFrame()

    base = pd.DataFrame(
        {
            "case_id": original_df["case_id"].astype(str),
            "workload": original_df["workload"].astype(str),
            "stressor": original_df["stressor"].astype(str),
            "label": pd.to_numeric(original_df["label"], errors="coerce"),
            "warning_available": pd.to_numeric(original_df.get("warning_available"), errors="coerce"),
            "original_anomaly_warning_s": pd.to_numeric(original_df["first_warning_s"], errors="coerce"),
            "original_warning_dominant_tier": original_df.get("warning_dominant_tier", "").astype(str),
            "original_warning_dominant_mechanism": original_df.get("warning_dominant_mechanism", "").astype(str),
            "original_top_feature_1": original_df.get("warning_top_feature_1", "").astype(str),
            "original_top_feature_2": original_df.get("warning_top_feature_2", "").astype(str),
        }
    )
    base["original_case_id"] = base["case_id"]

    if pilot_df.empty:
        base["has_crash_pilot"] = 0
        return ordered_sort(base)

    merged = base.merge(
        pilot_df.drop(columns=["workload", "stressor", "original_top_feature_1", "original_top_feature_2", "original_anomaly_warning_s"]),
        on="original_case_id",
        how="left",
    )
    merged["has_crash_pilot"] = merged["crash_pilot_anomaly_warning_s"].notna().astype(int)
    return ordered_sort(merged)


def build_report(out_path: Path, profile: str, full_df: pd.DataFrame, matched_df: pd.DataFrame) -> None:
    lines = [
        "# ITC-Study Crash Bridge Report",
        "",
        f"- Feature profile: `{profile}`",
        f"- Original ITC cases: `{int(len(full_df))}`",
        f"- Matched crash-pilot cases: `{int(len(matched_df))}`",
        f"- Matched workloads: `{', '.join(sorted(matched_df['workload'].astype(str).unique()))}`" if not matched_df.empty else "- Matched workloads: none",
        "",
    ]
    if matched_df.empty:
        lines.append("No matched crash-pilot cases are available yet.")
    else:
        show_cols = [
            "original_case_id",
            "original_anomaly_warning_s",
            "crash_pilot_anomaly_warning_s",
            "crash_time_s",
            "lead_time_s",
            "original_top_feature_1",
            "crash_pilot_warning_top_feature_1",
            "crash_peak_feature_1",
        ]
        lines.extend(
            [
                "## Matched ITC-study bridge cases",
                "",
                markdown_table(matched_df[show_cols]),
                "",
            ]
        )
    out_path.write_text("\n".join(lines), encoding="utf-8")


def markdown_table(df: pd.DataFrame) -> str:
    cols = [str(col) for col in df.columns]
    header = "| " + " | ".join(cols) + " |"
    rule = "| " + " | ".join(["---"] * len(cols)) + " |"
    rows = []
    for record in df.to_dict(orient="records"):
        vals = ["" if pd.isna(record.get(col)) else str(record.get(col)) for col in cols]
        rows.append("| " + " | ".join(vals) + " |")
    return "\n".join([header, rule, *rows])


def plot_timeline(matched_df: pd.DataFrame, out_path: Path) -> None:
    if matched_df.empty:
        return
    plot_df = ordered_sort(matched_df)
    labels = [f"{row.workload} / {row.stressor}" for row in plot_df.itertuples(index=False)]
    y = np.arange(len(plot_df), dtype=float)
    xmax = float(np.nanmax(pd.to_numeric(plot_df["crash_time_s"], errors="coerce").to_numpy(dtype=float)))
    xmax = max(xmax, float(np.nanmax(pd.to_numeric(plot_df["crash_pilot_anomaly_warning_s"], errors="coerce").to_numpy(dtype=float))))
    xmax = max(xmax, float(np.nanmax(pd.to_numeric(plot_df["original_anomaly_warning_s"], errors="coerce").to_numpy(dtype=float))))
    xmax = xmax + max(20.0, 0.08 * xmax)

    fig, ax = plt.subplots(figsize=(13.5, 1.3 * len(plot_df) + 1.8), constrained_layout=True)
    for idx, row in enumerate(plot_df.itertuples(index=False)):
        orig = float(getattr(row, "original_anomaly_warning_s", np.nan))
        pilot = float(getattr(row, "crash_pilot_anomaly_warning_s", np.nan))
        crash = float(getattr(row, "crash_time_s", np.nan))
        if np.isfinite(orig) and np.isfinite(pilot):
            ax.plot([orig, pilot], [idx, idx], color="#111827", linestyle=":", linewidth=1.2, alpha=0.85)
        if np.isfinite(pilot) and np.isfinite(crash):
            ax.plot([pilot, crash], [idx, idx], color="#16A34A", linestyle="-", linewidth=2.2, alpha=0.95)
        if np.isfinite(orig):
            ax.scatter(orig, idx, s=75, color="#111827", marker="o", zorder=4, label="Original anomaly warning" if idx == 0 else "")
        if np.isfinite(pilot):
            ax.scatter(pilot, idx, s=85, color="#F59E0B", marker="D", zorder=5, label="Crash-pilot anomaly warning" if idx == 0 else "")
        if np.isfinite(crash):
            ax.scatter(crash, idx, s=100, color="#DC2626", marker="X", zorder=6, label="Real crash" if idx == 0 else "")
        lead = float(getattr(row, "lead_time_s", np.nan))
        if np.isfinite(lead):
            ax.text(crash + 3.0, idx, f"lead {lead:.1f}s", va="center", ha="left", fontsize=9, color="#166534")

    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=10)
    ax.set_xlabel("Time from run start (s)")
    ax.set_title("ITC-study bridge: original anomaly warning, crash-pilot anomaly warning, and crash time", fontsize=15)
    ax.set_xlim(0.0, xmax)
    ax.grid(axis="x", alpha=0.25)
    ax.invert_yaxis()
    ax.legend(loc="upper right", frameon=False)
    fig.savefig(out_path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def plot_feature_table(matched_df: pd.DataFrame, out_path: Path) -> None:
    if matched_df.empty:
        return
    plot_df = ordered_sort(matched_df)
    rows = len(plot_df)
    col_labels = [
        "Case",
        "Original ITC warning\nfeatures",
        "Crash-pilot warning\nfeatures",
        "Abort pre-crash\npeak features",
        "Lead time",
    ]
    widths = [0.20, 0.24, 0.24, 0.24, 0.08]
    x_edges = np.cumsum([0.0, *widths])

    fig, ax = plt.subplots(figsize=(16, 0.82 * rows + 1.8), constrained_layout=True)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, rows + 1)
    ax.axis("off")

    for col_idx, label in enumerate(col_labels):
        x0 = x_edges[col_idx]
        width = widths[col_idx]
        ax.add_patch(patches.Rectangle((x0, rows), width, 1.0, facecolor="#E5E7EB", edgecolor="#CBD5E1"))
        ax.text(x0 + width / 2, rows + 0.5, label, ha="center", va="center", fontsize=10, fontweight="bold")

    for row_idx, row in enumerate(plot_df.itertuples(index=False)):
        y0 = rows - row_idx - 1
        fill = "#F8FAFC" if row_idx % 2 == 0 else "#FFFFFF"
        values = [
            f"{row.workload} / {row.stressor}",
            wrap_cell(format_feature_pair(getattr(row, "original_top_feature_1", ""), getattr(row, "original_top_feature_2", ""))),
            wrap_cell(
                format_feature_pair(
                    getattr(row, "crash_pilot_warning_top_feature_1", ""),
                    getattr(row, "crash_pilot_warning_top_feature_2", ""),
                )
            ),
            wrap_cell(
                format_feature_pair(
                    getattr(row, "crash_peak_feature_1", ""),
                    getattr(row, "crash_peak_feature_2", ""),
                )
            ),
            f"{float(getattr(row, 'lead_time_s', np.nan)):.1f}s" if np.isfinite(float(getattr(row, "lead_time_s", np.nan))) else "—",
        ]
        for col_idx, value in enumerate(values):
            x0 = x_edges[col_idx]
            width = widths[col_idx]
            cell_fill = fill
            if col_idx == 4 and value != "—":
                cell_fill = "#DCFCE7"
            ax.add_patch(patches.Rectangle((x0, y0), width, 1.0, facecolor=cell_fill, edgecolor="#CBD5E1"))
            ha = "left" if col_idx < 4 else "center"
            xpos = x0 + 0.012 if col_idx < 4 else x0 + width / 2
            ax.text(xpos, y0 + 0.5, value, ha=ha, va="center", fontsize=9.4, family="monospace" if col_idx > 0 else None)

    ax.set_title("ITC-study bridge: feature continuity from the original study to matched crash pilots", fontsize=15, pad=12)
    fig.savefig(out_path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def run_itc_study_crash_bridge(itc_root: Path, pilots_root: Path, out_dir: Path, profile: str) -> dict[str, object]:
    out_dir.mkdir(parents=True, exist_ok=True)

    pilot_roots = sorted([path for path in pilots_root.glob("data_workload_crash_*") if path.is_dir()])
    pilot_rows: list[dict[str, object]] = []
    skipped: list[str] = []
    for pilot_root in pilot_roots:
        rows = collect_pilot_rows(pilot_root=pilot_root, profile=profile)
        if rows:
            pilot_rows.extend(rows)
        else:
            skipped.append(pilot_root.name)

    pilot_df = choose_latest_pilots(pilot_rows)
    full_df = build_full_summary(itc_root=itc_root, profile=profile, pilot_df=pilot_df)
    matched_df = full_df[full_df.get("has_crash_pilot", 0).fillna(0).astype(int) == 1].copy()
    matched_df = ordered_sort(matched_df)

    summary_csv = out_dir / "itc_study_bridge_summary.csv"
    matched_csv = out_dir / "itc_study_bridge_matched_cases.csv"
    report_md = out_dir / "ITC_STUDY_CRASH_BRIDGE_REPORT.md"
    timeline_png = out_dir / "fig_itc_study_crash_bridge_timeline.png"
    feature_png = out_dir / "fig_itc_study_crash_bridge_features.png"

    if not full_df.empty:
        full_df.to_csv(summary_csv, index=False)
    if not matched_df.empty:
        matched_df.to_csv(matched_csv, index=False)
        plot_timeline(matched_df, timeline_png)
        plot_feature_table(matched_df, feature_png)
    build_report(report_md, profile=profile, full_df=full_df, matched_df=matched_df)

    status = {
        "itc_root": str(itc_root),
        "pilots_root": str(pilots_root),
        "out_dir": str(out_dir),
        "profile": profile,
        "pilot_roots_found": [str(path) for path in pilot_roots],
        "skipped_pilots": skipped,
        "matched_cases": int(len(matched_df)),
        "summary_csv": str(summary_csv),
        "matched_csv": str(matched_csv),
        "report_md": str(report_md),
        "timeline_png": str(timeline_png) if timeline_png.exists() else "",
        "feature_png": str(feature_png) if feature_png.exists() else "",
    }
    (out_dir / "itc_study_crash_bridge_status.json").write_text(json.dumps(status, indent=2), encoding="utf-8")
    return status


def parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="Aggregate workload-matched crash pilots into an ITC-study crash bridge.")
    ap.add_argument("--itc_root", "--itc-root", dest="itc_root", type=Path, required=True)
    ap.add_argument("--pilots_root", "--pilots-root", dest="pilots_root", type=Path, required=True)
    ap.add_argument("--out_dir", "--out-dir", dest="out_dir", type=Path, required=True)
    ap.add_argument("--feature_profile", "--feature-profile", dest="feature_profile", default="mixed")
    return ap


def main() -> None:
    args = parser().parse_args()
    status = run_itc_study_crash_bridge(
        itc_root=args.itc_root,
        pilots_root=args.pilots_root,
        out_dir=args.out_dir,
        profile=str(args.feature_profile),
    )
    print("[OK] matched ITC-study crash cases:", status["matched_cases"])
    print("[OK] wrote ITC-study bridge outputs to:", status["out_dir"] if "out_dir" in status else str(args.out_dir))


if __name__ == "__main__":
    main()
