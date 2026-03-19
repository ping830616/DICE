#!/usr/bin/env python3
"""
Full retrain/evaluation for DICE micro-twin + split-conformal pipeline.

Protocol:
- Use Tier-0 / Tier-1-alt / Tier-2 clean dataset (5000 rows @ 5Hz per run).
- Align to 1Hz via mean pooling.
- Train only on benign runs (NOMINAL) with workload-holdout folds.
- Fit linear micro-twin dynamics in normalized feature space.
- Build residual signatures on decision blocks.
- Calibrate conformal threshold on benign calibration blocks.
- Evaluate run-level labels (Benign vs Anomaly) via persistent block alerts.

Outputs:
- CSV metrics tables and per-case predictions
- LaTeX table snippets for paper
- ROC/PR and score distribution figures
- Markdown summary for direct paste into Results section
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Dict, List, Sequence, Tuple

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import Normalize
from matplotlib.patches import Polygon
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    roc_auc_score,
    roc_curve,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PROJECT_ROOT
DEFAULT_DATASET_ROOT = REPO_ROOT / "data generation" / "dataset" / "ITC_M2Pro_DATA"


WORKLOADS = ["BROWSER", "VIDEO_SW", "PY_AI", "PY_STATS"]
STRESSORS = ["NOMINAL", "CACHE", "TLB", "BRANCH", "MEMBW", "ATOMIC"]
ANOMALIES = [s for s in STRESSORS if s != "NOMINAL"]

IGNORE_COLS = {"idx", "ts_unix_s", "t_rel_s", "timestamp", "time", "ts"}

FEATURE_PROFILES = {
    "mixed": {
        "tier0": "tier0_full_5hz.csv",
        "tier1_alt": "tier1_alt_core_5hz.csv",
        "tier2": "tier2_core_5hz.csv",
    },
    "full": {
        "tier0": "tier0_full_5hz.csv",
        "tier1_alt": "tier1_alt_full_5hz.csv",
        "tier2": "tier2_full_5hz.csv",
    },
}

CONFIGS = {
    "tier0": ["tier0"],
    "tier0_tier1": ["tier0", "tier1_alt"],
    "tier0_tier1_tier2": ["tier0", "tier1_alt", "tier2"],
}

DIAG_TOP_K = 5
MECHANISM_GROUPS = [
    "compute",
    "memory_io",
    "thermal_power",
    "scheduler_runtime",
    "platform_pressure",
]

TITLE_SIZE = 15
LABEL_SIZE = 13
TICK_SIZE = 11
LEGEND_SIZE = 11
ANNOTATION_SIZE = 10
CONFIG_PRETTY = {
    "tier0": "Tier-0",
    "tier0_tier1": "Tier-0/1",
    "tier0_tier1_tier2": "Tier-0/1/2",
}
CONFIG_COLORS = {
    "tier0": "#355070",
    "tier0_tier1": "#2A9D8F",
    "tier0_tier1_tier2": "#E76F51",
}
STRESSOR_COLORS = {
    "ATOMIC": "#E76F51",
    "BRANCH": "#43AA8B",
    "CACHE": "#577590",
    "MEMBW": "#F4A261",
    "TLB": "#8D5A97",
}
SQRT3 = float(np.sqrt(3.0))


@dataclass(frozen=True)
class CaseRef:
    workload: str
    stressor: str

    @property
    def case_id(self) -> str:
        return f"{self.workload}__{self.stressor}"

    @property
    def label(self) -> int:
        return 0 if self.stressor == "NOMINAL" else 1


@dataclass
class ModelBundle:
    feature_names: List[str]
    median: np.ndarray
    scale: np.ndarray
    A: np.ndarray
    weights: np.ndarray
    cal_scores: np.ndarray
    tau: float


def all_cases() -> List[CaseRef]:
    return [CaseRef(w, s) for w in WORKLOADS for s in STRESSORS]


def robust_scale_1d(x: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    if x.size == 0:
        return 1.0
    q75, q25 = np.percentile(x, [75, 25])
    iqr = q75 - q25
    if iqr > 1e-12:
        return float(iqr / 1.349)
    med = np.median(x)
    mad = np.median(np.abs(x - med))
    if mad > 1e-12:
        return float(1.4826 * mad)
    std = float(np.std(x))
    if std > 1e-12:
        return std
    return 1.0


def robust_fit_matrix(X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    med = np.nanmedian(X, axis=0)
    scale = np.zeros(X.shape[1], dtype=float)
    for j in range(X.shape[1]):
        scale[j] = robust_scale_1d(X[:, j])
    scale[scale <= 1e-12] = 1.0
    return med, scale


def safe_auc(y_true: np.ndarray, score: np.ndarray) -> float:
    if len(np.unique(y_true)) < 2:
        return float("nan")
    return float(roc_auc_score(y_true, score))


def safe_ap(y_true: np.ndarray, score: np.ndarray) -> float:
    if len(np.unique(y_true)) < 2:
        return float("nan")
    return float(average_precision_score(y_true, score))


def default_results_dir(root: Path, protocol: str, feature_profile: str) -> Path:
    if feature_profile == "mixed":
        return root / ("results_dice_full_holdout" if protocol == "workload_holdout" else "results_dice_full")
    suffix = f"results_dice_full_{feature_profile}"
    if protocol == "workload_holdout":
        suffix = f"{suffix}_holdout"
    return root / suffix


def case_path(root: Path, tier: str, case: CaseRef, tier_files: Dict[str, str]) -> Path:
    return root / tier / case.case_id / tier_files[tier]


def read_df(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")
    df = pd.read_csv(path)
    for c in df.columns:
        if pd.api.types.is_numeric_dtype(df[c]):
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def numeric_features(df: pd.DataFrame) -> List[str]:
    out = []
    for c in df.columns:
        if c in IGNORE_COLS:
            continue
        if pd.api.types.is_numeric_dtype(df[c]):
            out.append(c)
    return out


def downsample_1hz(df: pd.DataFrame, source_hz: int = 5) -> pd.DataFrame:
    if len(df) < source_hz:
        return df.copy()
    n = (len(df) // source_hz) * source_hz
    tmp = df.iloc[:n].copy()
    grp = np.arange(n) // source_hz
    return tmp.groupby(grp, sort=False).mean(numeric_only=True)


def common_features_per_tier(root: Path, tier: str, tier_files: Dict[str, str]) -> List[str]:
    common = None
    for case in all_cases():
        df = read_df(case_path(root, tier, case, tier_files))
        cols = set(numeric_features(df))
        common = cols if common is None else (common & cols)
    common_list = sorted(common) if common else []

    # Drop globally constant features.
    keep = []
    for f in common_list:
        vals = []
        for case in all_cases():
            d = downsample_1hz(read_df(case_path(root, tier, case, tier_files)))
            vals.append(d[f].to_numpy(dtype=float))
        x = np.concatenate(vals)
        if np.nanstd(x) > 1e-10:
            keep.append(f)
    return keep


def build_case_matrix(
    root: Path,
    case: CaseRef,
    tiers: Sequence[str],
    feature_map: Dict[str, List[str]],
    tier_files: Dict[str, str],
    source_hz: int = 5,
) -> Tuple[np.ndarray, List[str]]:
    mats = []
    names = []
    lengths = []
    for t in tiers:
        df = downsample_1hz(read_df(case_path(root, t, case, tier_files)), source_hz=source_hz)
        feats = feature_map[t]
        arr = df[feats].to_numpy(dtype=float)
        mats.append(arr)
        lengths.append(arr.shape[0])
        names.extend([f"{t}:{f}" for f in feats])

    n = min(lengths)
    mats = [m[:n] for m in mats]
    X = np.concatenate(mats, axis=1)
    return X, names


def fit_linear_dynamics(X_runs: List[np.ndarray], ridge_lambda: float = 1e-3) -> np.ndarray:
    X_prev = []
    X_next = []
    for X in X_runs:
        if len(X) < 2:
            continue
        X_prev.append(X[:-1])
        X_next.append(X[1:])
    if not X_prev:
        raise RuntimeError("Not enough samples to fit dynamics.")
    P = np.vstack(X_prev)  # [N, d]
    N = np.vstack(X_next)  # [N, d]
    d = P.shape[1]
    xtx = P.T @ P + ridge_lambda * np.eye(d)
    xty = P.T @ N
    A = np.linalg.solve(xtx, xty)  # [d, d]
    return A


def residual_timeseries(X_norm: np.ndarray, A: np.ndarray, gain: float) -> np.ndarray:
    """
    Kalman-style fixed-gain synchronization:
    z_pred = A z_prev
    r_t    = x_t - z_pred
    z_t    = z_pred + gain * r_t
    """
    T, d = X_norm.shape
    if T < 2:
        return np.zeros((0, d), dtype=float)
    z = X_norm[0].copy()
    residuals = []
    for t in range(1, T):
        z_pred = z @ A
        r = X_norm[t] - z_pred
        residuals.append(r)
        z = z_pred + gain * r
    return np.vstack(residuals)


def block_signatures(residual: np.ndarray, B: int) -> np.ndarray:
    """
    Signature per block: mean absolute residual over a sliding window.
    """
    if residual.shape[0] == 0:
        return np.zeros((0, residual.shape[1]), dtype=float)
    a = np.abs(residual)
    T, d = a.shape
    if T < B:
        return np.mean(a, axis=0, keepdims=True)
    cs = np.vstack([np.zeros((1, d)), np.cumsum(a, axis=0)])
    out = (cs[B:] - cs[:-B]) / float(B)
    return out


def fit_weights(signatures_fit: np.ndarray) -> np.ndarray:
    sigma = np.std(signatures_fit, axis=0)
    w = 1.0 / (sigma + 1e-6)
    w = np.maximum(w, 0.0)
    s = np.sum(w)
    if s <= 0:
        return np.ones_like(w) / len(w)
    return w / s


def signature_scores(signatures: np.ndarray, weights: np.ndarray) -> np.ndarray:
    if signatures.shape[0] == 0:
        return np.zeros((0,), dtype=float)
    return signatures @ weights


def conformal_threshold(cal_scores: np.ndarray, alpha: float) -> float:
    sc = np.sort(np.asarray(cal_scores, dtype=float))
    n = len(sc)
    if n == 0:
        return float("inf")
    k = int(np.ceil((n + 1) * (1.0 - alpha)))
    k = min(max(k, 1), n)
    return float(sc[k - 1])


def conformal_pvals(cal_scores: np.ndarray, test_scores: np.ndarray) -> np.ndarray:
    cal = np.asarray(cal_scores, dtype=float)
    denom = len(cal) + 1.0
    out = np.zeros(len(test_scores), dtype=float)
    for i, s in enumerate(test_scores):
        out[i] = (1.0 + np.sum(cal >= s)) / denom
    return out


def persistent_alerts(alerts: np.ndarray, k: int) -> np.ndarray:
    out = np.zeros(len(alerts), dtype=int)
    run = 0
    for i, a in enumerate(alerts.astype(bool)):
        if a:
            run += 1
        else:
            run = 0
        out[i] = 1 if run >= k else 0
    return out


def first_positive_index(x: np.ndarray) -> int:
    idx = np.flatnonzero(np.asarray(x, dtype=bool))
    return int(idx[0]) if len(idx) else -1


def finite_median(x: Sequence[float]) -> float:
    arr = np.asarray(x, dtype=float)
    arr = arr[np.isfinite(arr)]
    if arr.size == 0:
        return float("nan")
    return float(np.median(arr))


def finite_percentile(x: Sequence[float], q: float) -> float:
    arr = np.asarray(x, dtype=float)
    arr = arr[np.isfinite(arr)]
    if arr.size == 0:
        return float("nan")
    return float(np.percentile(arr, q))


def workload_conditioned_scores(df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
    nominal_map = (
        df[df["stressor"] == "NOMINAL"]
        .drop_duplicates(subset=["workload"], keep="last")
        .set_index("workload")["run_score"]
        .to_dict()
    )
    nominal = df["workload"].map(nominal_map).to_numpy(dtype=float)
    score = np.abs(df["run_score"].to_numpy(dtype=float) - nominal)
    return nominal, score


def mechanism_group(feature_name: str) -> str:
    name = feature_name.split(":", 1)[-1].lower()
    if any(tok in name for tok in ["temp", "power", "fan"]):
        return "thermal_power"
    if any(tok in name for tok in ["mem_", "swap_", "disk_", "net_", "wired_bytes", "active_bytes", "inactive_bytes"]):
        return "memory_io"
    if any(
        tok in name
        for tok in [
            "ctx_switch",
            "interrupt",
            "syscall",
            "pids_count",
            "running_fraction",
            "weight_ns",
            "unique_process",
            "unique_thread",
            "samples_per_bucket",
            "sentinel_count",
            "core_id",
        ]
    ):
        return "scheduler_runtime"
    if any(tok in name for tok in ["load", "uptime", "available_bytes", "free_bytes", "mem_percent"]):
        return "platform_pressure"
    return "compute"


def mechanism_vector(feature_names: Sequence[str], feature_contrib: np.ndarray) -> Tuple[Dict[str, float], np.ndarray]:
    totals = {group: 0.0 for group in MECHANISM_GROUPS}
    for name, value in zip(feature_names, np.asarray(feature_contrib, dtype=float)):
        totals[mechanism_group(name)] += float(value)
    vec = np.array([totals[group] for group in MECHANISM_GROUPS], dtype=float)
    return totals, vec


def train_bundle(
    train_benign_runs: Dict[str, np.ndarray],
    feature_names: List[str],
    fit_ratio: float,
    B: int,
    alpha: float,
    gain: float,
    ridge_lambda: float,
) -> ModelBundle:
    fit_runs = []
    cal_runs = []
    fit_samples = []

    for _, X in train_benign_runs.items():
        n = len(X)
        split = int(max(2, min(n - 1, round(n * fit_ratio))))
        X_fit = X[:split]
        X_cal = X[split:]
        fit_runs.append(X_fit)
        cal_runs.append(X_cal if len(X_cal) > 1 else X_fit[-2:])
        fit_samples.append(X_fit)

    X_fit_all = np.vstack(fit_samples)
    med, scale = robust_fit_matrix(X_fit_all)

    fit_norm = [(x - med) / (scale + 1e-12) for x in fit_runs]
    cal_norm = [(x - med) / (scale + 1e-12) for x in cal_runs]

    A = fit_linear_dynamics(fit_norm, ridge_lambda=ridge_lambda)

    sig_fit = []
    for X in fit_norm:
        r = residual_timeseries(X, A, gain=gain)
        s = block_signatures(r, B=B)
        if len(s):
            sig_fit.append(s)
    sig_fit_all = np.vstack(sig_fit)
    w = fit_weights(sig_fit_all)

    cal_scores = []
    for X in cal_norm:
        r = residual_timeseries(X, A, gain=gain)
        s = block_signatures(r, B=B)
        sc = signature_scores(s, w)
        if len(sc):
            cal_scores.append(sc)
    cal_scores_all = np.concatenate(cal_scores)
    tau = conformal_threshold(cal_scores_all, alpha=alpha)

    return ModelBundle(
        feature_names=feature_names,
        median=med,
        scale=scale,
        A=A,
        weights=w,
        cal_scores=cal_scores_all,
        tau=tau,
    )


def evaluate_run(
    X_run: np.ndarray,
    bundle: ModelBundle,
    B: int,
    alpha: float,
    persist_k: int,
    gain: float,
) -> Tuple[Dict[str, float], np.ndarray]:
    Xn = (X_run - bundle.median) / (bundle.scale + 1e-12)
    r = residual_timeseries(Xn, bundle.A, gain=gain)
    sig = block_signatures(r, B=B)
    sc = signature_scores(sig, bundle.weights)
    pv = conformal_pvals(bundle.cal_scores, sc)

    block_alert = pv < alpha
    persist = persistent_alerts(block_alert, k=persist_k)

    run_alert = int(np.any(persist > 0))
    peak_score = float(np.max(sc)) if len(sc) else 0.0
    run_score = peak_score
    run_signature = np.nanmedian(sig, axis=0) if len(sig) else np.zeros_like(bundle.weights)
    feature_contrib = run_signature * bundle.weights
    first_block_idx = first_positive_index(block_alert)
    first_persist_idx = first_positive_index(persist)
    block_time_s = float(B + first_block_idx) if first_block_idx >= 0 else float("nan")
    persist_time_s = float(B + first_persist_idx) if first_persist_idx >= 0 else float("nan")
    n_blocks = int(len(sc))
    duration_s = max(n_blocks, 1)

    return (
        {
            "run_score": run_score,
            "run_alert": run_alert,
            "min_pvalue": float(np.min(pv)) if len(pv) else 1.0,
            "peak_block_score": peak_score,
            "n_blocks": n_blocks,
            "n_block_alerts": int(np.sum(block_alert)),
            "n_persist_alerts": int(np.sum(persist)),
            "first_block_alert_idx": first_block_idx,
            "first_persist_alert_idx": first_persist_idx,
            "first_block_alert_s": block_time_s,
            "time_to_detect_s": persist_time_s,
            "block_alerts_per_hour": float(np.sum(block_alert) * 3600.0 / duration_s),
            "persist_alerts_per_hour": float(np.sum(persist) * 3600.0 / duration_s),
        },
        feature_contrib,
    )


def to_latex_table(df: pd.DataFrame, caption: str, label: str) -> str:
    body = df.to_latex(index=False, escape=False, float_format=lambda x: f"{x:.4f}")
    return (
        "\\begin{table}[t]\n"
        "\\centering\n"
        f"\\caption{{{caption}}}\n"
        f"\\label{{{label}}}\n"
        "\\footnotesize\n"
        f"{body}\n"
        "\\end{table}\n"
    )


def _cfg_label(cfg: str) -> str:
    return CONFIG_PRETTY.get(cfg, cfg.replace("_", " + "))


def _cfg_color(cfg: str) -> str:
    return CONFIG_COLORS.get(cfg, "#4E79A7")


def _stressor_color(stressor: str) -> str:
    return STRESSOR_COLORS.get(stressor, "#4E79A7")


def _ternary_xy(share0: float, share1: float, share2: float) -> Tuple[float, float]:
    total = max(float(share0 + share1 + share2), 1e-12)
    a = float(share0) / total
    b = float(share1) / total
    c = float(share2) / total
    return b + 0.5 * c, c * SQRT3 / 2.0


def _setup_ternary_axis(ax: plt.Axes, labels: Tuple[str, str, str]) -> None:
    verts = np.array([[0.0, 0.0], [1.0, 0.0], [0.5, SQRT3 / 2.0]])
    ax.add_patch(Polygon(verts, closed=True, fill=False, edgecolor="#334155", linewidth=1.8))
    for frac in (0.2, 0.4, 0.6, 0.8):
        for p1, p2 in [
            (_ternary_xy(frac, 0.0, 1.0 - frac), _ternary_xy(frac, 1.0 - frac, 0.0)),
            (_ternary_xy(0.0, frac, 1.0 - frac), _ternary_xy(1.0 - frac, frac, 0.0)),
            (_ternary_xy(0.0, 1.0 - frac, frac), _ternary_xy(1.0 - frac, 0.0, frac)),
        ]:
            ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color="#CBD5E1", linewidth=0.8, zorder=0)
    ax.text(-0.06, -0.06, labels[0], fontsize=LABEL_SIZE, fontweight="bold", ha="right", va="top")
    ax.text(1.06, -0.06, labels[1], fontsize=LABEL_SIZE, fontweight="bold", ha="left", va="top")
    ax.text(0.5, SQRT3 / 2.0 + 0.06, labels[2], fontsize=LABEL_SIZE, fontweight="bold", ha="center")
    ax.text(0.5, -0.12, "Closer to a corner means more evidence from that tier.", fontsize=11, ha="center", color="#475569")
    ax.set_xlim(-0.10, 1.10)
    ax.set_ylim(-0.15, SQRT3 / 2.0 + 0.12)
    ax.set_aspect("equal")
    ax.axis("off")


def plot_curves(df: pd.DataFrame, out_png: Path, score_col: str, title_tag: str) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(14.8, 6.0))
    roc_metrics: List[Tuple[str, str]] = []
    pr_metrics: List[Tuple[str, str]] = []
    for cfg, d in df.groupby("config", sort=False):
        y = d["label"].to_numpy(dtype=int)
        s = d[score_col].to_numpy(dtype=float)
        if len(np.unique(y)) < 2:
            continue
        fpr, tpr, _ = roc_curve(y, s)
        p, r, _ = precision_recall_curve(y, s)
        color = _cfg_color(cfg)
        roc_val = roc_auc_score(y, s)
        ap_val = average_precision_score(y, s)
        axes[0].plot(fpr, tpr, linewidth=3.0, color=color, solid_capstyle="round")
        axes[0].fill_between(fpr, tpr, 0, color=color, alpha=0.08)
        axes[1].plot(r, p, linewidth=3.0, color=color, solid_capstyle="round")
        roc_metrics.append((color, f"{_cfg_label(cfg)}  ROC {roc_val:.3f}"))
        pr_metrics.append((color, f"{_cfg_label(cfg)}  AP {ap_val:.3f}"))
    axes[0].plot([0, 1], [0, 1], linestyle=(0, (4, 4)), color="#94A3B8", linewidth=1.2)
    axes[0].set_title("ROC curve", fontsize=TITLE_SIZE)
    axes[0].set_xlabel("False Positive Rate", fontsize=LABEL_SIZE)
    axes[0].set_ylabel("True Positive Rate", fontsize=LABEL_SIZE)
    axes[1].set_title("Precision-Recall curve", fontsize=TITLE_SIZE)
    axes[1].set_xlabel("Recall", fontsize=LABEL_SIZE)
    axes[1].set_ylabel("Precision", fontsize=LABEL_SIZE)
    for ax in axes:
        ax.set_xlim(-0.02, 1.02)
        ax.set_ylim(-0.02, 1.02)
        ax.grid(alpha=0.25)
        ax.tick_params(labelsize=TICK_SIZE)
    for idx, (color, text) in enumerate(roc_metrics):
        axes[0].text(
            0.0,
            -0.20 - idx * 0.09,
            text,
            transform=axes[0].transAxes,
            color=color,
            fontsize=ANNOTATION_SIZE + 1,
            fontweight="bold",
            ha="left",
            va="top",
        )
    for idx, (color, text) in enumerate(pr_metrics):
        axes[1].text(
            0.0,
            -0.20 - idx * 0.09,
            text,
            transform=axes[1].transAxes,
            color=color,
            fontsize=ANNOTATION_SIZE + 1,
            fontweight="bold",
            ha="left",
            va="top",
        )
    fig.text(
        0.5,
        0.03,
        "Shaded area highlights stronger separation; workload-conditioned curves overlap because all heads are perfect there.",
        ha="center",
        fontsize=12,
        color="#475569",
    )
    fig.suptitle(f"DICE curves ({title_tag})", fontsize=TITLE_SIZE + 1, fontweight="bold")
    fig.tight_layout(rect=[0.0, 0.16, 1.0, 0.92])
    fig.savefig(out_png, dpi=240, bbox_inches="tight")
    plt.close(fig)


def plot_score_box(df: pd.DataFrame, out_png: Path, score_col: str, y_label: str, title_tag: str) -> None:
    cfgs = list(df["config"].unique())
    fig, axes = plt.subplots(1, len(cfgs), figsize=(5.4 * len(cfgs), 5.4), sharey=False)
    if len(cfgs) == 1:
        axes = [axes]
    rng = np.random.default_rng(0)
    for i, cfg in enumerate(cfgs):
        ax = axes[i]
        d = df[df["config"] == cfg]
        neg = d[d["label"] == 0][score_col].to_numpy(dtype=float)
        pos = d[d["label"] == 1][score_col].to_numpy(dtype=float)
        parts = ax.violinplot(
            [neg, pos],
            positions=[1, 2],
            widths=0.82,
            showmeans=False,
            showmedians=False,
            showextrema=False,
        )
        for body, color in zip(parts["bodies"], ["#b0bec5", "#ef9a9a"]):
            body.set_facecolor(color)
            body.set_edgecolor("black")
            body.set_alpha(0.75)
        for xpos, vals, color, edge in [(1, neg, "#0F172A", "white"), (2, pos, "#C62828", "white")]:
            jitter = rng.uniform(-0.07, 0.07, size=len(vals))
            ax.scatter(
                np.full(len(vals), xpos) + jitter,
                vals,
                color=color,
                s=42,
                alpha=0.72,
                edgecolor=edge,
                linewidth=0.4,
                zorder=3,
            )
            if len(vals):
                q1, med, q3 = np.percentile(vals, [25, 50, 75])
                ax.vlines(xpos, q1, q3, color=color, linewidth=6, alpha=0.82, zorder=4)
                ax.hlines(med, xpos - 0.18, xpos + 0.18, color="white", linewidth=2.4, zorder=5)
        ax.set_xticks([1, 2], labels=["Benign", "Anomaly"])
        ax.set_title(_cfg_label(cfg), fontsize=TITLE_SIZE + 2)
        ax.tick_params(labelsize=TICK_SIZE)
        ax.grid(alpha=0.22)
        vals_all = np.concatenate([neg, pos]) if len(neg) or len(pos) else np.array([])
        if len(vals_all) and np.all(vals_all > 0):
            ax.set_yscale("log")
    fig.supylabel(y_label, fontsize=LABEL_SIZE)
    fig.suptitle(f"DICE run score distributions ({title_tag})", fontsize=TITLE_SIZE + 2, fontweight="bold")
    fig.tight_layout(rect=[0.04, 0.0, 1.0, 0.94])
    fig.savefig(out_png, dpi=240, bbox_inches="tight")
    plt.close(fig)


def build_diagnostic_record(
    config: str,
    holdout_workload: str,
    case: CaseRef,
    feature_names: Sequence[str],
    feature_contrib: np.ndarray,
) -> Dict[str, object]:
    contrib = np.asarray(feature_contrib, dtype=float)
    total = float(np.sum(contrib))
    # Track contributions over the released three-tier observation hierarchy.
    tier_totals = {tier: 0.0 for tier in ("tier0", "tier1_alt", "tier2")}
    for name, value in zip(feature_names, contrib):
        tier = name.split(":", 1)[0]
        if tier in tier_totals:
            tier_totals[tier] += float(value)
    dominant_tier = max(tier_totals, key=tier_totals.get) if total > 0 else "none"
    mech_totals, mech_vec = mechanism_vector(feature_names, contrib)
    dominant_mechanism = max(mech_totals, key=mech_totals.get) if total > 0 else "none"
    order = np.argsort(contrib)[::-1][:DIAG_TOP_K]
    mech_order = np.argsort(mech_vec)[::-1][:3]

    row: Dict[str, object] = {
        "config": config,
        "holdout_workload": holdout_workload,
        "case_id": case.case_id,
        "workload": case.workload,
        "stressor": case.stressor,
        "label": case.label,
        "dominant_tier": dominant_tier,
        "tier0_contrib": float(tier_totals["tier0"]),
        "tier1_alt_contrib": float(tier_totals["tier1_alt"]),
        "tier2_contrib": float(tier_totals["tier2"]),
        "tier0_share": float(tier_totals["tier0"] / total) if total > 0 else 0.0,
        "tier1_alt_share": float(tier_totals["tier1_alt"] / total) if total > 0 else 0.0,
        "tier2_share": float(tier_totals["tier2"] / total) if total > 0 else 0.0,
        "dominant_mechanism": dominant_mechanism,
        "_feature_contrib": contrib.copy(),
        "_mechanism_vector": mech_vec.copy(),
    }
    for group in MECHANISM_GROUPS:
        row[f"{group}_contrib"] = float(mech_totals[group])
        row[f"{group}_share"] = float(mech_totals[group] / total) if total > 0 else 0.0
    for rank in range(DIAG_TOP_K):
        key_name = f"top_feature_{rank + 1}"
        key_score = f"top_feature_score_{rank + 1}"
        if rank < len(order) and contrib[order[rank]] > 0.0:
            idx = int(order[rank])
            row[key_name] = feature_names[idx]
            row[key_score] = float(contrib[idx])
        else:
            row[key_name] = ""
            row[key_score] = 0.0
    for rank in range(3):
        key_name = f"top_mechanism_{rank + 1}"
        key_score = f"top_mechanism_score_{rank + 1}"
        if rank < len(mech_order) and mech_vec[mech_order[rank]] > 0.0:
            idx = int(mech_order[rank])
            row[key_name] = MECHANISM_GROUPS[idx]
            row[key_score] = float(mech_vec[idx])
        else:
            row[key_name] = ""
            row[key_score] = 0.0
    return row


def append_case_outputs(
    preds: List[Dict[str, object]],
    diagnostic_records: List[Dict[str, object]],
    config: str,
    holdout_workload: str,
    case: CaseRef,
    X_run: np.ndarray,
    bundle: ModelBundle,
    B: int,
    alpha: float,
    persist_k: int,
    gain: float,
) -> None:
    metrics, feature_contrib = evaluate_run(
        X_run,
        bundle,
        B=B,
        alpha=alpha,
        persist_k=persist_k,
        gain=gain,
    )
    preds.append(
        {
            "config": config,
            "holdout_workload": holdout_workload,
            "case_id": case.case_id,
            "workload": case.workload,
            "stressor": case.stressor,
            "label": case.label,
            **metrics,
            "n_features": len(bundle.feature_names),
            "tau": bundle.tau,
        }
    )
    diagnostic_records.append(
        build_diagnostic_record(
            config=config,
            holdout_workload=holdout_workload,
            case=case,
            feature_names=bundle.feature_names,
            feature_contrib=feature_contrib,
        )
    )


def build_stressor_attribution(
    diagnostic_records: Sequence[Dict[str, object]],
    vector_key: str,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    pred_rows: List[Dict[str, object]] = []
    for cfg_name in CONFIGS:
        cfg_records = [r for r in diagnostic_records if r["config"] == cfg_name and int(r["label"]) == 1]
        for holdout_w in WORKLOADS:
            train = [r for r in cfg_records if r["workload"] != holdout_w]
            test = [r for r in cfg_records if r["workload"] == holdout_w]
            centroids = {}
            for stressor in ANOMALIES:
                mats = [r[vector_key] for r in train if r["stressor"] == stressor]
                if mats:
                    centroids[stressor] = np.median(np.vstack(mats), axis=0)
            if len(centroids) < 2:
                continue
            for row in test:
                truth = str(row["stressor"])
                contrib = np.asarray(row[vector_key], dtype=float)
                dists = {stressor: float(np.linalg.norm(contrib - centroid)) for stressor, centroid in centroids.items()}
                ordered = sorted(dists.items(), key=lambda item: item[1])
                pred = ordered[0][0]
                top2 = [label for label, _ in ordered[:2]]
                pred_rows.append(
                    {
                        "config": cfg_name,
                        "holdout_workload": holdout_w,
                        "case_id": row["case_id"],
                        "true_stressor": truth,
                        "pred_stressor": pred,
                        "is_correct": int(pred == truth),
                        "top2_hit": int(truth in top2),
                        "nearest_distance": float(ordered[0][1]),
                        "margin_to_second": float(ordered[1][1] - ordered[0][1]) if len(ordered) > 1 else float("inf"),
                    }
                )

    pred_df = pd.DataFrame(pred_rows)
    if pred_df.empty:
        empty_metrics = pd.DataFrame(
            columns=["config", "n_cases", "top1_acc", "top2_acc", "macro_f1", "mean_margin_to_second"]
        )
        empty_cm = pd.DataFrame(index=ANOMALIES, columns=ANOMALIES, data=0)
        empty_cm.index.name = "true_stressor"
        empty_cm.columns.name = "pred_stressor"
        return pred_df, empty_metrics, empty_cm
    pred_df = pred_df.sort_values(["config", "holdout_workload", "case_id"])

    metric_rows = []
    for cfg_name, d in pred_df.groupby("config", sort=False):
        metric_rows.append(
            {
                "config": cfg_name,
                "n_cases": int(len(d)),
                "top1_acc": float(d["is_correct"].mean()),
                "top2_acc": float(d["top2_hit"].mean()),
                "macro_f1": float(
                    f1_score(
                        d["true_stressor"],
                        d["pred_stressor"],
                        labels=ANOMALIES,
                        average="macro",
                        zero_division=0,
                    )
                ),
                "mean_margin_to_second": float(d["margin_to_second"].replace([np.inf, -np.inf], np.nan).mean()),
            }
        )
    metrics_df = pd.DataFrame(metric_rows).sort_values("config")

    final_cfg = "tier0_tier1_tier2"
    d_final = pred_df[pred_df["config"] == final_cfg]
    if d_final.empty:
        cm = pd.DataFrame(index=ANOMALIES, columns=ANOMALIES, data=0)
    else:
        cm_arr = confusion_matrix(
            d_final["true_stressor"],
            d_final["pred_stressor"],
            labels=ANOMALIES,
        )
        cm = pd.DataFrame(cm_arr, index=ANOMALIES, columns=ANOMALIES)
    cm.index.name = "true_stressor"
    cm.columns.name = "pred_stressor"
    return pred_df, metrics_df, cm


def build_stressor_tier_contributions(diag_df: pd.DataFrame, config: str) -> pd.DataFrame:
    cols = ["tier0_share", "tier1_alt_share", "tier2_share"]
    d = diag_df[(diag_df["config"] == config) & (diag_df["label"] == 1)].copy()
    if d.empty:
        return pd.DataFrame(columns=["stressor", *cols, "dominant_tier_mode"])
    rows = []
    for stressor, part in d.groupby("stressor", sort=True):
        mode = part["dominant_tier"].mode()
        rows.append(
            {
                "stressor": stressor,
                "tier0_share": float(part["tier0_share"].mean()),
                "tier1_alt_share": float(part["tier1_alt_share"].mean()),
                "tier2_share": float(part["tier2_share"].mean()),
                "dominant_tier_mode": str(mode.iloc[0]) if not mode.empty else "none",
            }
        )
    return pd.DataFrame(rows).sort_values("stressor")


def build_mechanism_summary(diag_df: pd.DataFrame, config: str) -> pd.DataFrame:
    share_cols = [f"{group}_share" for group in MECHANISM_GROUPS]
    d = diag_df[(diag_df["config"] == config) & (diag_df["label"] == 1)].copy()
    if d.empty:
        return pd.DataFrame(columns=["stressor", *share_cols, "dominant_mechanism_mode"])
    rows = []
    for stressor, part in d.groupby("stressor", sort=True):
        mode = part["dominant_mechanism"].mode()
        row = {
            "stressor": stressor,
            "dominant_mechanism_mode": str(mode.iloc[0]) if not mode.empty else "none",
        }
        for col in share_cols:
            row[col] = float(part[col].mean())
        rows.append(row)
    return pd.DataFrame(rows).sort_values("stressor")


def build_sequential_metrics(pred_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for cfg, d in pred_df.groupby("config", sort=False):
        benign = d[d["label"] == 0]
        anomaly = d[d["label"] == 1]
        detected = anomaly[anomaly["run_alert"] == 1]
        rows.append(
            {
                "config": cfg,
                "benign_run_alert_rate": float(benign["run_alert"].mean()),
                "benign_persist_alerts_per_hour": float(benign["persist_alerts_per_hour"].mean()),
                "benign_block_alerts_per_hour": float(benign["block_alerts_per_hour"].mean()),
                "anomaly_detect_rate": float(anomaly["run_alert"].mean()),
                "median_time_to_detect_s": finite_median(detected["time_to_detect_s"]),
                "p90_time_to_detect_s": finite_percentile(detected["time_to_detect_s"], 90),
                "detect_within_120s": float((anomaly["time_to_detect_s"] <= 120).fillna(False).mean()),
                "detect_within_300s": float((anomaly["time_to_detect_s"] <= 300).fillna(False).mean()),
                "detect_within_600s": float((anomaly["time_to_detect_s"] <= 600).fillna(False).mean()),
            }
        )
    return pd.DataFrame(rows).sort_values("config")


def build_holdout_robustness_summary(fold_df: pd.DataFrame, pred_df: pd.DataFrame) -> pd.DataFrame:
    d = fold_df[fold_df["holdout_workload"] != "ALL"].copy()
    if d.empty:
        return pd.DataFrame(
            columns=[
                "config",
                "mean_pr_auc",
                "worst_pr_auc",
                "mean_roc_auc",
                "mean_pr_auc_wc",
                "worst_pr_auc_wc",
                "mean_roc_auc_wc",
                "pooled_pr_auc",
                "pooled_roc_auc",
                "pooled_pr_auc_wc",
                "pooled_roc_auc_wc",
                "mean_fpr",
                "mean_tpr",
            ]
        )
    pred_holdout = pred_df[pred_df["holdout_workload"] != "ALL"].copy()
    rows = []
    for cfg, part in d.groupby("config", sort=False):
        pred_part = pred_holdout[pred_holdout["config"] == cfg]
        y = pred_part["label"].to_numpy(dtype=int)
        s_run = pred_part["run_score"].to_numpy(dtype=float)
        s_wc = pred_part["run_score_wc"].to_numpy(dtype=float)
        rows.append(
            {
                "config": cfg,
                "mean_pr_auc": float(part["pr_auc"].mean()),
                "worst_pr_auc": float(part["pr_auc"].min()),
                "mean_roc_auc": float(part["roc_auc"].mean()),
                "mean_pr_auc_wc": float(part["pr_auc_wc"].mean()),
                "worst_pr_auc_wc": float(part["pr_auc_wc"].min()),
                "mean_roc_auc_wc": float(part["roc_auc_wc"].mean()),
                "pooled_pr_auc": safe_ap(y, s_run),
                "pooled_roc_auc": safe_auc(y, s_run),
                "pooled_pr_auc_wc": safe_ap(y, s_wc),
                "pooled_roc_auc_wc": safe_auc(y, s_wc),
                "mean_fpr": float(part["fpr"].mean()),
                "mean_tpr": float(part["tpr"].mean()),
            }
        )
    return pd.DataFrame(rows).sort_values("config")


def plot_confusion_heatmap(cm: pd.DataFrame, out_png: Path, title: str) -> None:
    if cm.empty:
        return
    mat = cm.to_numpy(dtype=float)
    row_sum = mat.sum(axis=1, keepdims=True)
    row_share = np.divide(mat, np.where(row_sum == 0.0, 1.0, row_sum))
    fig, ax = plt.subplots(figsize=(7.2, 6.0))
    yy, xx = np.indices(mat.shape)
    sizes = 1800.0 * (mat.flatten() / max(np.max(mat), 1.0) + 0.08)
    sc = ax.scatter(
        xx.flatten(),
        yy.flatten(),
        s=sizes,
        c=row_share.flatten(),
        cmap="YlOrRd",
        norm=Normalize(vmin=0.0, vmax=1.0),
        edgecolor="#334155",
        linewidth=1.1,
        zorder=3,
    )
    ax.set_xticks(np.arange(len(cm.columns)), labels=list(cm.columns), rotation=28, ha="right")
    ax.set_yticks(np.arange(len(cm.index)), labels=list(cm.index))
    ax.set_xlabel("Predicted stressor", fontsize=LABEL_SIZE)
    ax.set_ylabel("True stressor", fontsize=LABEL_SIZE)
    ax.set_title(title, fontsize=TITLE_SIZE)
    ax.tick_params(labelsize=TICK_SIZE)
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            share = row_share[i, j]
            color = "white" if share >= 0.55 else "black"
            ax.text(j, i, f"{int(mat[i, j])}", ha="center", va="center", color=color, fontsize=ANNOTATION_SIZE + 2, fontweight="bold")
    ax.set_xlim(-0.6, mat.shape[1] - 0.4)
    ax.set_ylim(mat.shape[0] - 0.4, -0.6)
    ax.set_facecolor("#F8FAFC")
    ax.set_xticks(np.arange(-0.5, mat.shape[1], 1), minor=True)
    ax.set_yticks(np.arange(-0.5, mat.shape[0], 1), minor=True)
    ax.grid(which="minor", color="#E2E8F0", linewidth=1.0)
    ax.grid(False)
    cbar = fig.colorbar(sc, ax=ax, fraction=0.046, pad=0.04)
    cbar.ax.set_ylabel("Share within each true stressor", fontsize=12)
    fig.tight_layout()
    fig.savefig(out_png, dpi=240, bbox_inches="tight")
    plt.close(fig)


def plot_stressor_tier_shares(df: pd.DataFrame, out_png: Path) -> None:
    if df.empty:
        return
    fig, ax = plt.subplots(figsize=(8.4, 7.2))
    _setup_ternary_axis(ax, ("Tier-0", "Tier-1", "Tier-2"))
    label_offsets = {
        "ATOMIC": (-0.028, 0.090),
        "BRANCH": (-0.105, 0.050),
        "CACHE": (0.0, 0.055),
        "MEMBW": (-0.105, 0.010),
        "TLB": (0.060, 0.088),
    }
    for row in df.itertuples(index=False):
        x, y = _ternary_xy(row.tier0_share, row.tier1_alt_share, row.tier2_share)
        color = _stressor_color(row.stressor)
        ax.scatter(
            x,
            y,
            s=360 + 260 * max(row.tier0_share, row.tier1_alt_share, row.tier2_share),
            color=color,
            edgecolor="white",
            linewidth=1.6,
            zorder=3,
        )
        dx, dy = label_offsets.get(str(row.stressor), (0.0, 0.05))
        ax.annotate(
            str(row.stressor),
            xy=(x, y),
            xytext=(x + dx, y + dy),
            textcoords="data",
            ha="center",
            va="center",
            fontsize=ANNOTATION_SIZE,
            fontweight="bold",
            arrowprops=dict(arrowstyle="-", color=color, linewidth=1.0, alpha=0.8),
            bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="none", alpha=0.86),
        )
    ax.set_title("Where the final diagnosis gets its evidence", fontsize=TITLE_SIZE + 2)
    fig.tight_layout()
    fig.savefig(out_png, dpi=240, bbox_inches="tight")
    plt.close(fig)


def plot_mechanism_shares(df: pd.DataFrame, out_png: Path) -> None:
    if df.empty:
        return
    fields = [
        ("compute_share", "Compute"),
        ("memory_io_share", "Memory/I/O"),
        ("thermal_power_share", "Thermal/Power"),
        ("scheduler_runtime_share", "Runtime"),
        ("platform_pressure_share", "Platform"),
    ]
    angles = np.linspace(0.0, 2.0 * np.pi, len(fields), endpoint=False)
    angles_closed = np.concatenate([angles, angles[:1]])
    rmax = max(0.4, float(df[[col for col, _ in fields]].to_numpy(dtype=float).max()) * 1.2)
    fig, axes = plt.subplots(2, 3, figsize=(14.5, 8.4), subplot_kw={"projection": "polar"})
    axes = axes.ravel()
    rows = list(df.itertuples(index=False))
    mean_row = {col: float(df[col].mean()) for col, _ in fields}
    for idx, ax in enumerate(axes):
        if idx < len(rows):
            row = rows[idx]
            title = str(row.stressor)
            vals = [float(getattr(row, col)) for col, _ in fields]
            color = _stressor_color(title)
        else:
            title = "Average profile"
            vals = [mean_row[col] for col, _ in fields]
            color = "#1D3557"
        vals_closed = np.array(vals + vals[:1], dtype=float)
        ax.plot(angles_closed, vals_closed, color=color, linewidth=2.5)
        ax.fill(angles_closed, vals_closed, color=color, alpha=0.22)
        ax.set_xticks(angles)
        ax.set_xticklabels([label for _, label in fields], fontsize=11)
        ax.set_ylim(0.0, rmax)
        yticks = np.linspace(rmax / 4.0, rmax, 4)
        ax.set_yticks(yticks)
        ax.set_yticklabels([f"{tick:.2f}" for tick in yticks], fontsize=9, color="#64748B")
        ax.grid(color="#CBD5E1", alpha=0.7)
        ax.spines["polar"].set_color("#CBD5E1")
        ax.set_title(title, fontsize=TITLE_SIZE, fontweight="bold", y=1.10)
    fig.suptitle("Mechanism fingerprints by stressor", fontsize=TITLE_SIZE + 3, fontweight="bold", y=0.98)
    fig.tight_layout(rect=[0.0, 0.0, 1.0, 0.95])
    fig.savefig(out_png, dpi=240, bbox_inches="tight")
    plt.close(fig)


def plot_detection_latency(df: pd.DataFrame, out_png: Path) -> None:
    if df.empty:
        return
    fig, ax = plt.subplots(figsize=(9.2, 5.4))
    d = df.copy()
    d["label"] = d["config"].map(_cfg_label)
    order_map = {cfg: i for i, cfg in enumerate(CONFIGS.keys())}
    d["sort_key"] = d["config"].map(order_map)
    d = d.sort_values("sort_key").reset_index(drop=True)
    vals = d["median_time_to_detect_s"].to_numpy(dtype=float)
    xpos = np.arange(len(d))
    colors = [_cfg_color(cfg) for cfg in d["config"]]
    detect = d["anomaly_detect_rate"].fillna(0.0).to_numpy(dtype=float)
    benign = d["benign_run_alert_rate"].fillna(0.0).to_numpy(dtype=float)
    for ref in (120.0, 300.0, 600.0):
        ax.axvline(ref, color="#CBD5E1", linestyle=(0, (3, 4)), linewidth=1.0, zorder=0)
    ax.hlines(xpos, xmin=0.0, xmax=vals, color=colors, linewidth=4, alpha=0.35)
    sc = ax.scatter(
        vals,
        xpos,
        s=240 + 760 * detect,
        c=benign,
        cmap="OrRd",
        norm=Normalize(vmin=0.0, vmax=max(float(np.max(benign)), 0.25)),
        edgecolor="black",
        linewidth=1.1,
        zorder=3,
    )
    for x, y, value, rate in zip(vals, xpos, vals, detect):
        ax.text(
            x + max(vals) * 0.02,
            y,
            f"{value:.0f}s | detect {rate:.0%}",
            va="center",
            fontsize=ANNOTATION_SIZE + 1,
            bbox=dict(boxstyle="round,pad=0.16", fc="white", ec="none", alpha=0.85),
        )
    ax.set_yticks(xpos, labels=d["label"].tolist())
    ax.set_xlabel("Median time-to-detect (s)", fontsize=LABEL_SIZE)
    ax.set_title("Sequential detection speed and alert burden", fontsize=TITLE_SIZE + 1)
    ax.tick_params(labelsize=TICK_SIZE)
    ax.set_facecolor("#F8FAFC")
    ax.grid(axis="x", alpha=0.25)
    cbar = fig.colorbar(sc, ax=ax, fraction=0.046, pad=0.04)
    cbar.ax.set_ylabel("Benign alert rate", fontsize=12)
    fig.text(0.5, 0.03, "Larger circles mean higher anomaly detection rate.", ha="center", fontsize=12, color="#475569")
    fig.tight_layout(rect=[0.0, 0.05, 1.0, 1.0])
    fig.savefig(out_png, dpi=240, bbox_inches="tight")
    plt.close(fig)


def append_text_table(lines: List[str], df: pd.DataFrame) -> None:
    lines.append("```text")
    lines.append(df.to_string(index=False))
    lines.append("```")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--root",
        type=Path,
        default=DEFAULT_DATASET_ROOT,
    )
    ap.add_argument("--out_dir", type=Path, default=None)
    ap.add_argument("--source_hz", type=int, default=5)
    ap.add_argument("--fit_ratio", type=float, default=0.6)
    ap.add_argument("--block_B", type=int, default=60)
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--persist_k", type=int, default=3)
    ap.add_argument("--gain", type=float, default=0.35)
    ap.add_argument("--ridge_lambda", type=float, default=1e-3)
    ap.add_argument(
        "--feature_profile",
        choices=sorted(FEATURE_PROFILES.keys()),
        default="mixed",
        help="Feature-file profile: mixed keeps the current deployment-friendly setting; full uses full Tier-1/Tier-2 files as an upper-bound comparison.",
    )
    ap.add_argument(
        "--protocol",
        choices=["workload_holdout", "global"],
        default="global",
        help="Evaluation protocol: workload_holdout (strict) or global benign split (paper-style).",
    )
    args = ap.parse_args()

    root = args.root.expanduser().resolve()
    tier_files = FEATURE_PROFILES[args.feature_profile]
    out_dir = args.out_dir.expanduser().resolve() if args.out_dir else default_results_dir(
        root,
        protocol=args.protocol,
        feature_profile=args.feature_profile,
    )
    fig_dir = out_dir / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)
    fig_dir.mkdir(parents=True, exist_ok=True)

    print(f"[INFO] feature_profile={args.feature_profile} tier_files={tier_files}")
    tier_features = {t: common_features_per_tier(root, t, tier_files) for t in tier_files.keys()}
    for t, fs in tier_features.items():
        print(f"[INFO] {t}: common features={len(fs)}")

    preds = []
    fold_rows = []
    diagnostic_records: List[Dict[str, object]] = []
    config_runtime: Dict[str, float] = {}

    for cfg_name, tiers in CONFIGS.items():
        cfg_t0 = perf_counter()
        print(f"[INFO] training config={cfg_name} tiers={tiers}")
        case_X = {}
        feature_names_cfg = None
        for case in all_cases():
            X, names = build_case_matrix(
                root,
                case,
                tiers=tiers,
                feature_map=tier_features,
                tier_files=tier_files,
                source_hz=args.source_hz,
            )
            case_X[case.case_id] = X
            if feature_names_cfg is None:
                feature_names_cfg = names

        if args.protocol == "workload_holdout":
            for holdout_w in WORKLOADS:
                train_benign = {
                    case_id: X
                    for case_id, X in case_X.items()
                    if case_id.endswith("__NOMINAL") and not case_id.startswith(f"{holdout_w}__")
                }

                bundle = train_bundle(
                    train_benign_runs=train_benign,
                    feature_names=feature_names_cfg or [],
                    fit_ratio=args.fit_ratio,
                    B=args.block_B,
                    alpha=args.alpha,
                    gain=args.gain,
                    ridge_lambda=args.ridge_lambda,
                )

                test_cases = [c for c in all_cases() if c.workload == holdout_w]
                for case in test_cases:
                    append_case_outputs(
                        preds=preds,
                        diagnostic_records=diagnostic_records,
                        config=cfg_name,
                        holdout_workload=holdout_w,
                        case=case,
                        X_run=case_X[case.case_id],
                        bundle=bundle,
                        B=args.block_B,
                        alpha=args.alpha,
                        persist_k=args.persist_k,
                        gain=args.gain,
                    )

                fold_curr = [p for p in preds if p["config"] == cfg_name and p["holdout_workload"] == holdout_w]
                fd = pd.DataFrame(fold_curr)
                y = fd["label"].to_numpy(dtype=int)
                s_run = fd["run_score"].to_numpy(dtype=float)
                _, s_wc = workload_conditioned_scores(fd)
                fold_rows.append(
                    {
                        "feature_profile": args.feature_profile,
                        "config": cfg_name,
                        "holdout_workload": holdout_w,
                        "roc_auc": safe_auc(y, s_run),
                        "pr_auc": safe_ap(y, s_run),
                        "roc_auc_wc": safe_auc(y, s_wc),
                        "pr_auc_wc": safe_ap(y, s_wc),
                        "fpr": float(np.mean((fd["label"] == 0) & (fd["run_alert"] == 1))),
                        "tpr": float(np.mean((fd["label"] == 1) & (fd["run_alert"] == 1))),
                        "n_features": int(fd["n_features"].iloc[0]),
                    }
                )
        else:
            train_benign = {case_id: X for case_id, X in case_X.items() if case_id.endswith("__NOMINAL")}
            bundle = train_bundle(
                train_benign_runs=train_benign,
                feature_names=feature_names_cfg or [],
                fit_ratio=args.fit_ratio,
                B=args.block_B,
                alpha=args.alpha,
                gain=args.gain,
                ridge_lambda=args.ridge_lambda,
            )
            for case in all_cases():
                append_case_outputs(
                    preds=preds,
                    diagnostic_records=diagnostic_records,
                    config=cfg_name,
                    holdout_workload="ALL",
                    case=case,
                    X_run=case_X[case.case_id],
                    bundle=bundle,
                    B=args.block_B,
                    alpha=args.alpha,
                    persist_k=args.persist_k,
                    gain=args.gain,
                )

            fd = pd.DataFrame([p for p in preds if p["config"] == cfg_name])
            y = fd["label"].to_numpy(dtype=int)
            s_run = fd["run_score"].to_numpy(dtype=float)
            _, s_wc = workload_conditioned_scores(fd)
            fold_rows.append(
                {
                    "feature_profile": args.feature_profile,
                    "config": cfg_name,
                    "holdout_workload": "ALL",
                    "roc_auc": safe_auc(y, s_run),
                    "pr_auc": safe_ap(y, s_run),
                    "roc_auc_wc": safe_auc(y, s_wc),
                    "pr_auc_wc": safe_ap(y, s_wc),
                    "fpr": float(np.mean((fd["label"] == 0) & (fd["run_alert"] == 1))),
                    "tpr": float(np.mean((fd["label"] == 1) & (fd["run_alert"] == 1))),
                    "n_features": int(fd["n_features"].iloc[0]),
                }
            )
        config_runtime[cfg_name] = perf_counter() - cfg_t0

    pred_df = pd.DataFrame(preds).sort_values(["config", "workload", "stressor"])
    pred_df["feature_profile"] = args.feature_profile
    fold_df = pd.DataFrame(fold_rows).sort_values(["config", "holdout_workload"])
    diag_df = pd.DataFrame([{k: v for k, v in row.items() if not k.startswith("_")} for row in diagnostic_records]).sort_values(
        ["config", "workload", "stressor"]
    )
    diag_df["feature_profile"] = args.feature_profile

    # Workload-conditioned score head: distance to workload nominal template.
    pred_df["nominal_template_score"] = np.nan
    pred_df["run_score_wc"] = pred_df["run_score"]
    for cfg, d in pred_df.groupby("config"):
        idx = d.index
        nominal, s_wc = workload_conditioned_scores(d)
        pred_df.loc[idx, "nominal_template_score"] = nominal
        pred_df.loc[idx, "run_score_wc"] = s_wc

    overall_rows = []
    for cfg, d in pred_df.groupby("config"):
        y = d["label"].to_numpy(dtype=int)
        s_run = d["run_score"].to_numpy(dtype=float)
        s_wc = d["run_score_wc"].to_numpy(dtype=float)
        overall_rows.append(
            {
                "feature_profile": args.feature_profile,
                "config": cfg,
                "n_cases": int(len(d)),
                "n_features": int(d["n_features"].iloc[0]),
                "fit_eval_seconds": float(config_runtime.get(cfg, float("nan"))),
                "roc_auc": safe_auc(y, s_run),
                "pr_auc": safe_ap(y, s_run),
                "roc_auc_wc": safe_auc(y, s_wc),
                "pr_auc_wc": safe_ap(y, s_wc),
                "fpr_run_alert": float(np.mean(d[d["label"] == 0]["run_alert"])),
                "tpr_run_alert": float(np.mean(d[d["label"] == 1]["run_alert"])),
                "median_nominal_score": float(np.median(d[d["label"] == 0]["run_score"])),
                "median_anomaly_score": float(np.median(d[d["label"] == 1]["run_score"])),
                "median_nominal_score_wc": float(np.median(d[d["label"] == 0]["run_score_wc"])),
                "median_anomaly_score_wc": float(np.median(d[d["label"] == 1]["run_score_wc"])),
            }
        )
    overall_df = pd.DataFrame(overall_rows).sort_values("config")

    final_cfg = "tier0_tier1_tier2"
    fin = pred_df[pred_df["config"] == final_cfg]
    stress_rows = []
    neg = fin[fin["stressor"] == "NOMINAL"][["workload", "run_score", "run_score_wc"]].set_index("workload")
    for a in ANOMALIES:
        pos = fin[fin["stressor"] == a][["workload", "run_score", "run_score_wc"]].set_index("workload")
        m = neg.join(pos, lsuffix="_neg", rsuffix="_pos", how="inner")
        y = np.array([0] * len(m) + [1] * len(m), dtype=int)
        s_run = np.concatenate([m["run_score_neg"].to_numpy(dtype=float), m["run_score_pos"].to_numpy(dtype=float)])
        s_wc = np.concatenate([m["run_score_wc_neg"].to_numpy(dtype=float), m["run_score_wc_pos"].to_numpy(dtype=float)])
        stress_rows.append(
            {
                "feature_profile": args.feature_profile,
                "stressor": a,
                "roc_auc": safe_auc(y, s_run),
                "pr_auc": safe_ap(y, s_run),
                "roc_auc_wc": safe_auc(y, s_wc),
                "pr_auc_wc": safe_ap(y, s_wc),
                "median_neg_score": float(np.median(m["run_score_neg"])),
                "median_pos_score": float(np.median(m["run_score_pos"])),
                "median_neg_score_wc": float(np.median(m["run_score_wc_neg"])),
                "median_pos_score_wc": float(np.median(m["run_score_wc_pos"])),
                "pos_neg_ratio": float((np.median(m["run_score_pos"]) + 1e-6) / (np.median(m["run_score_neg"]) + 1e-6)),
                "pos_neg_diff": float(np.median(m["run_score_pos"]) - np.median(m["run_score_neg"])),
                "pos_neg_ratio_wc": float((np.median(m["run_score_wc_pos"]) + 1e-6) / (np.median(m["run_score_wc_neg"]) + 1e-6)),
                "pos_neg_diff_wc": float(np.median(m["run_score_wc_pos"]) - np.median(m["run_score_wc_neg"])),
            }
        )
    stress_df = pd.DataFrame(stress_rows).sort_values("stressor")

    mm_pr = float(np.mean(stress_df["pr_auc"]))
    mm_roc = float(np.mean(stress_df["roc_auc"]))
    mm_pr_wc = float(np.mean(stress_df["pr_auc_wc"]))
    mm_roc_wc = float(np.mean(stress_df["roc_auc_wc"]))

    filt = stress_df[~stress_df["stressor"].isin(["BRANCH", "TLB"])]
    mm_pr_filt = float(np.mean(filt["pr_auc"]))
    mm_roc_filt = float(np.mean(filt["roc_auc"]))
    mm_pr_filt_wc = float(np.mean(filt["pr_auc_wc"]))
    mm_roc_filt_wc = float(np.mean(filt["roc_auc_wc"]))

    diag_pred_feature_df, diag_metrics_feature_df, diag_cm_feature = build_stressor_attribution(
        diagnostic_records,
        vector_key="_feature_contrib",
    )
    diag_pred_df, diag_metrics_df, diag_cm = build_stressor_attribution(
        diagnostic_records,
        vector_key="_mechanism_vector",
    )
    diag_tier_df = build_stressor_tier_contributions(diag_df, config=final_cfg)
    mechanism_df = build_mechanism_summary(diag_df, config=final_cfg)
    sequential_df = build_sequential_metrics(pred_df)
    holdout_df = build_holdout_robustness_summary(fold_df, pred_df)
    if not diag_metrics_feature_df.empty:
        diag_metrics_feature_df["feature_profile"] = args.feature_profile
    if not diag_metrics_df.empty:
        diag_metrics_df["feature_profile"] = args.feature_profile
    if not diag_tier_df.empty:
        diag_tier_df["feature_profile"] = args.feature_profile
    if not mechanism_df.empty:
        mechanism_df["feature_profile"] = args.feature_profile
    if not sequential_df.empty:
        sequential_df["feature_profile"] = args.feature_profile
    if not holdout_df.empty:
        holdout_df["feature_profile"] = args.feature_profile

    runtime_df = pd.DataFrame(
        [
            {
                "feature_profile": args.feature_profile,
                "config": cfg,
                "fit_eval_seconds": float(sec),
            }
            for cfg, sec in config_runtime.items()
        ]
    ).sort_values("config")

    pred_df.to_csv(out_dir / "case_predictions.csv", index=False)
    fold_df.to_csv(out_dir / "fold_metrics.csv", index=False)
    overall_df.to_csv(out_dir / "overall_metrics.csv", index=False)
    runtime_df.to_csv(out_dir / "config_runtime_summary.csv", index=False)
    stress_df.to_csv(out_dir / "stressor_metrics_final_config.csv", index=False)
    diag_df.to_csv(out_dir / "case_diagnosis_summary.csv", index=False)
    diag_pred_df.to_csv(out_dir / "stressor_diagnosis_predictions.csv", index=False)
    diag_metrics_df.to_csv(out_dir / "stressor_diagnosis_metrics.csv", index=False)
    diag_cm.to_csv(out_dir / "stressor_confusion_matrix.csv")
    diag_tier_df.to_csv(out_dir / "stressor_tier_contributions.csv", index=False)
    mechanism_df.to_csv(out_dir / "mechanism_group_summary.csv", index=False)
    sequential_df.to_csv(out_dir / "sequential_metrics.csv", index=False)
    holdout_df.to_csv(out_dir / "holdout_robustness_summary.csv", index=False)
    diag_pred_feature_df.to_csv(out_dir / "stressor_feature_diagnosis_predictions.csv", index=False)
    diag_metrics_feature_df.to_csv(out_dir / "stressor_feature_diagnosis_metrics.csv", index=False)
    diag_cm_feature.to_csv(out_dir / "stressor_feature_confusion_matrix.csv")
    (out_dir / "run_context.json").write_text(
        json.dumps(
            {
                "feature_profile": args.feature_profile,
                "tier_files": tier_files,
                "protocol": args.protocol,
                "source_hz": args.source_hz,
                "fit_ratio": args.fit_ratio,
                "block_B": args.block_B,
                "alpha": args.alpha,
                "persist_k": args.persist_k,
                "gain": args.gain,
                "ridge_lambda": args.ridge_lambda,
                "config_runtime_seconds": config_runtime,
            },
            indent=2,
        )
        + "\n"
    )

    overall_tex = overall_df[
        ["config", "n_features", "roc_auc", "pr_auc", "roc_auc_wc", "pr_auc_wc", "fpr_run_alert", "tpr_run_alert"]
    ].rename(
        columns={
            "config": "Configuration",
            "n_features": "Features",
            "roc_auc": "ROC-AUC (Base)",
            "pr_auc": "AUC-PR (Base)",
            "roc_auc_wc": "ROC-AUC (WC)",
            "pr_auc_wc": "AUC-PR (WC)",
            "fpr_run_alert": "Run-FPR",
            "tpr_run_alert": "Run-TPR",
        }
    )
    stress_tex = stress_df[
        ["stressor", "roc_auc", "pr_auc", "roc_auc_wc", "pr_auc_wc", "pos_neg_ratio", "pos_neg_diff"]
    ].rename(
        columns={
            "stressor": "Stressor",
            "roc_auc": "ROC-AUC (Base)",
            "pr_auc": "AUC-PR (Base)",
            "roc_auc_wc": "ROC-AUC (WC)",
            "pr_auc_wc": "AUC-PR (WC)",
            "pos_neg_ratio": "Pos/Neg Score Ratio",
            "pos_neg_diff": "Pos-Neg Score Delta",
        }
    )
    (out_dir / "overall_metrics.tex").write_text(
        to_latex_table(
            overall_tex,
            "DICE micro-twin + split-conformal run-level results under benign retraining.",
            "tab:dice_full_overall",
        )
    )
    (out_dir / "stressor_metrics_final_config.tex").write_text(
        to_latex_table(
            stress_tex,
            "Final DICE configuration per-stressor separability.",
            "tab:dice_full_stressor",
        )
    )
    if not diag_metrics_df.empty:
        diag_tex = diag_metrics_df.rename(
            columns={
                "config": "Configuration",
                "n_cases": "Cases",
                "top1_acc": "Top-1 Acc.",
                "top2_acc": "Top-2 Acc.",
                "macro_f1": "Macro-F1",
                "mean_margin_to_second": "Mean Margin",
            }
        )
        (out_dir / "stressor_diagnosis_metrics.tex").write_text(
            to_latex_table(
                diag_tex,
                "Mechanism-group stressor attribution from DICE residual contributions across workloads.",
                "tab:dice_stressor_diagnosis",
            )
        )
    if not sequential_df.empty:
        seq_tex = sequential_df.rename(
            columns={
                "config": "Configuration",
                "benign_run_alert_rate": "Benign Run-Alert Rate",
                "benign_persist_alerts_per_hour": "Benign Persist Alerts/hr",
                "anomaly_detect_rate": "Anomaly Detect Rate",
                "median_time_to_detect_s": "Median TTD (s)",
                "detect_within_300s": "Detect <=300s",
            }
        )[
            [
                "Configuration",
                "Benign Run-Alert Rate",
                "Benign Persist Alerts/hr",
                "Anomaly Detect Rate",
                "Median TTD (s)",
                "Detect <=300s",
            ]
        ]
        (out_dir / "sequential_metrics.tex").write_text(
            to_latex_table(
                seq_tex,
                "Sequential decision metrics for the DICE run-level detector.",
                "tab:dice_sequential_metrics",
            )
        )

    plot_curves(pred_df, fig_dir / "fig_roc_pr_by_config.png", score_col="run_score", title_tag="base")
    plot_curves(pred_df, fig_dir / "fig_roc_pr_by_config_wc.png", score_col="run_score_wc", title_tag="workload-conditioned")
    plot_score_box(
        pred_df,
        fig_dir / "fig_run_score_boxplot.png",
        score_col="run_score",
        y_label="Run score (base)",
        title_tag="base",
    )
    plot_score_box(
        pred_df,
        fig_dir / "fig_run_score_boxplot_wc.png",
        score_col="run_score_wc",
        y_label="Run score (workload-conditioned)",
        title_tag="workload-conditioned",
    )
    plot_confusion_heatmap(
        diag_cm,
        fig_dir / "fig_stressor_confusion_matrix.png",
        title="Final-config prototype stressor attribution",
    )
    plot_stressor_tier_shares(
        diag_tier_df,
        fig_dir / "fig_stressor_tier_contributions.png",
    )
    plot_mechanism_shares(
        mechanism_df,
        fig_dir / "fig_mechanism_group_summary.png",
    )
    plot_detection_latency(
        sequential_df,
        fig_dir / "fig_detection_latency.png",
    )

    md = []
    md.append("# DICE Full Retrain Results")
    md.append("")
    md.append("## Setup")
    md.append(
        f"- Feature profile: {args.feature_profile} ({tier_files})"
    )
    md.append(
        f"- Protocol: {args.protocol}, benign-only fit/calibration, block_B={args.block_B}, "
        f"alpha={args.alpha}, persist_k={args.persist_k}, gain={args.gain}"
    )
    md.append("")
    md.append("## Overall")
    append_text_table(md, overall_df)
    md.append("")
    md.append("## Final Config Stressors")
    append_text_table(md, stress_df)
    md.append("")
    md.append("## Paper-style Aggregates (Final Config)")
    md.append(f"- Base score mean stressor AUC-PR (all five): **{mm_pr:.4f}**")
    md.append(f"- Base score mean stressor ROC-AUC (all five): **{mm_roc:.4f}**")
    md.append(f"- WC score mean stressor AUC-PR (all five): **{mm_pr_wc:.4f}**")
    md.append(f"- WC score mean stressor ROC-AUC (all five): **{mm_roc_wc:.4f}**")
    md.append(f"- Base score mean stressor AUC-PR (excluding BRANCH/TLB): **{mm_pr_filt:.4f}**")
    md.append(f"- Base score mean stressor ROC-AUC (excluding BRANCH/TLB): **{mm_roc_filt:.4f}**")
    md.append(f"- WC score mean stressor AUC-PR (excluding BRANCH/TLB): **{mm_pr_filt_wc:.4f}**")
    md.append(f"- WC score mean stressor ROC-AUC (excluding BRANCH/TLB): **{mm_roc_filt_wc:.4f}**")
    md.append("")
    if not diag_metrics_df.empty:
        md.append("## Diagnosis")
        md.append("- Primary diagnosis uses mechanism-group centroids over workload-held residual summaries.")
        append_text_table(md, diag_metrics_df)
        md.append("")
        if not diag_tier_df.empty:
            md.append("## Final Config Tier Contribution Summary")
            append_text_table(md, diag_tier_df)
            md.append("")
        if not mechanism_df.empty:
            md.append("## Final Config Mechanism Summary")
            append_text_table(md, mechanism_df)
            md.append("")
    if not sequential_df.empty:
        md.append("## Sequential Decisioning")
        append_text_table(md, sequential_df)
        md.append("")
    if not holdout_df.empty:
        md.append("## Holdout Robustness (Workload Drift Proxy)")
        append_text_table(md, holdout_df)
        md.append("")
    md.append("## Files")
    for p in [
        out_dir / "overall_metrics.csv",
        out_dir / "config_runtime_summary.csv",
        out_dir / "run_context.json",
        out_dir / "stressor_metrics_final_config.csv",
        out_dir / "sequential_metrics.csv",
        out_dir / "case_diagnosis_summary.csv",
        out_dir / "stressor_diagnosis_metrics.csv",
        out_dir / "mechanism_group_summary.csv",
        out_dir / "stressor_confusion_matrix.csv",
        out_dir / "stressor_tier_contributions.csv",
        out_dir / "overall_metrics.tex",
        out_dir / "stressor_metrics_final_config.tex",
        out_dir / "stressor_diagnosis_metrics.tex",
        out_dir / "sequential_metrics.tex",
        fig_dir / "fig_roc_pr_by_config.png",
        fig_dir / "fig_roc_pr_by_config_wc.png",
        fig_dir / "fig_run_score_boxplot.png",
        fig_dir / "fig_run_score_boxplot_wc.png",
        fig_dir / "fig_stressor_confusion_matrix.png",
        fig_dir / "fig_stressor_tier_contributions.png",
        fig_dir / "fig_mechanism_group_summary.png",
        fig_dir / "fig_detection_latency.png",
    ]:
        md.append(f"- `{p}`")
    (out_dir / "RESULTS_SUMMARY.md").write_text("\n".join(md) + "\n")

    print(f"[OK] wrote results to: {out_dir}")
    print("[OK] overall metrics:")
    print(overall_df.to_string(index=False))
    print("[OK] final config stressor metrics:")
    print(stress_df.to_string(index=False))
    if not diag_metrics_df.empty:
        print("[OK] stressor diagnosis metrics:")
        print(diag_metrics_df.to_string(index=False))
    if not sequential_df.empty:
        print("[OK] sequential metrics:")
        print(sequential_df.to_string(index=False))
    print(
        "[OK] aggregates (base): "
        f"all(AUC-PR={mm_pr:.4f}, ROC-AUC={mm_roc:.4f}), "
        f"filtered(AUC-PR={mm_pr_filt:.4f}, ROC-AUC={mm_roc_filt:.4f})"
    )
    print(
        "[OK] aggregates (workload-conditioned): "
        f"all(AUC-PR={mm_pr_wc:.4f}, ROC-AUC={mm_roc_wc:.4f}), "
        f"filtered(AUC-PR={mm_pr_filt_wc:.4f}, ROC-AUC={mm_roc_filt_wc:.4f})"
    )


if __name__ == "__main__":
    main()
