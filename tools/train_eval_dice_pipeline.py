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
from typing import Dict, List, Sequence, Tuple

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
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

TIER_FILE = {
    "tier0": "tier0_full_5hz.csv",
    "tier1_alt": "tier1_alt_core_5hz.csv",
    "tier2": "tier2_core_5hz.csv",
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


def case_path(root: Path, tier: str, case: CaseRef) -> Path:
    return root / tier / case.case_id / TIER_FILE[tier]


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


def common_features_per_tier(root: Path, tier: str) -> List[str]:
    common = None
    for case in all_cases():
        df = read_df(case_path(root, tier, case))
        cols = set(numeric_features(df))
        common = cols if common is None else (common & cols)
    common_list = sorted(common) if common else []

    # Drop globally constant features.
    keep = []
    for f in common_list:
        vals = []
        for case in all_cases():
            d = downsample_1hz(read_df(case_path(root, tier, case)))
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
    source_hz: int = 5,
) -> Tuple[np.ndarray, List[str]]:
    mats = []
    names = []
    lengths = []
    for t in tiers:
        df = downsample_1hz(read_df(case_path(root, t, case)), source_hz=source_hz)
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


def plot_curves(df: pd.DataFrame, out_png: Path, score_col: str, title_tag: str) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    for cfg, d in df.groupby("config"):
        y = d["label"].to_numpy(dtype=int)
        s = d[score_col].to_numpy(dtype=float)
        if len(np.unique(y)) < 2:
            continue
        fpr, tpr, _ = roc_curve(y, s)
        p, r, _ = precision_recall_curve(y, s)
        axes[0].plot(fpr, tpr, linewidth=2, label=f"{cfg} (AUC={roc_auc_score(y, s):.3f})")
        axes[1].plot(r, p, linewidth=2, label=f"{cfg} (AP={average_precision_score(y, s):.3f})")
    axes[0].plot([0, 1], [0, 1], "k--", linewidth=1)
    axes[0].set_title("ROC curve")
    axes[0].set_xlabel("False Positive Rate")
    axes[0].set_ylabel("True Positive Rate")
    axes[1].set_title("Precision-Recall curve")
    axes[1].set_xlabel("Recall")
    axes[1].set_ylabel("Precision")
    for ax in axes:
        ax.grid(alpha=0.25)
        ax.legend(frameon=True, fontsize=10)
    fig.suptitle(f"DICE curves ({title_tag})")
    fig.tight_layout()
    fig.savefig(out_png, dpi=240, bbox_inches="tight")
    plt.close(fig)


def plot_score_box(df: pd.DataFrame, out_png: Path, score_col: str, y_label: str, title_tag: str) -> None:
    cfgs = list(df["config"].unique())
    fig, axes = plt.subplots(1, len(cfgs), figsize=(5.0 * len(cfgs), 4.8), sharey=False)
    if len(cfgs) == 1:
        axes = [axes]
    for i, cfg in enumerate(cfgs):
        ax = axes[i]
        d = df[df["config"] == cfg]
        neg = d[d["label"] == 0][score_col].to_numpy(dtype=float)
        pos = d[d["label"] == 1][score_col].to_numpy(dtype=float)
        bp = ax.boxplot([neg, pos], tick_labels=["Benign", "Anomaly"], patch_artist=True)
        for patch, color in zip(bp["boxes"], ["#9e9e9e", "#ef9a9a"]):
            patch.set_facecolor(color)
            patch.set_alpha(0.8)
        ax.scatter(np.repeat(1, len(neg)), neg, color="black", s=22, alpha=0.8)
        ax.scatter(np.repeat(2, len(pos)), pos, color="#c62828", s=22, alpha=0.7)
        ax.set_title(cfg)
        ax.set_ylabel(y_label)
        ax.grid(alpha=0.22)
    fig.suptitle(f"DICE run score distributions ({title_tag})")
    fig.tight_layout()
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
    tier_totals = {tier: 0.0 for tier in TIER_FILE}
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


def build_holdout_robustness_summary(fold_df: pd.DataFrame) -> pd.DataFrame:
    d = fold_df[fold_df["holdout_workload"] != "ALL"].copy()
    if d.empty:
        return pd.DataFrame(columns=["config", "mean_pr_auc", "worst_pr_auc", "mean_roc_auc", "mean_fpr", "mean_tpr"])
    rows = []
    for cfg, part in d.groupby("config", sort=False):
        rows.append(
            {
                "config": cfg,
                "mean_pr_auc": float(part["pr_auc"].mean()),
                "worst_pr_auc": float(part["pr_auc"].min()),
                "mean_roc_auc": float(part["roc_auc"].mean()),
                "mean_fpr": float(part["fpr"].mean()),
                "mean_tpr": float(part["tpr"].mean()),
            }
        )
    return pd.DataFrame(rows).sort_values("config")


def plot_confusion_heatmap(cm: pd.DataFrame, out_png: Path, title: str) -> None:
    if cm.empty:
        return
    mat = cm.to_numpy(dtype=float)
    fig, ax = plt.subplots(figsize=(6.2, 5.2))
    im = ax.imshow(mat, cmap="Blues")
    ax.set_xticks(np.arange(len(cm.columns)), labels=list(cm.columns), rotation=30, ha="right")
    ax.set_yticks(np.arange(len(cm.index)), labels=list(cm.index))
    ax.set_xlabel("Predicted stressor")
    ax.set_ylabel("True stressor")
    ax.set_title(title)
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            color = "white" if mat[i, j] >= max(1.0, np.max(mat) * 0.55) else "black"
            ax.text(j, i, f"{int(mat[i, j])}", ha="center", va="center", color=color, fontsize=10)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    fig.savefig(out_png, dpi=240, bbox_inches="tight")
    plt.close(fig)


def plot_stressor_tier_shares(df: pd.DataFrame, out_png: Path) -> None:
    if df.empty:
        return
    fig, ax = plt.subplots(figsize=(7.4, 4.8))
    x = np.arange(len(df))
    bottom = np.zeros(len(df), dtype=float)
    series = [
        ("tier0_share", "Tier-0", "#78909c"),
        ("tier1_alt_share", "Tier-1", "#81c784"),
        ("tier2_share", "Tier-2", "#ffb74d"),
    ]
    for col, label, color in series:
        vals = df[col].to_numpy(dtype=float)
        ax.bar(x, vals, bottom=bottom, label=label, color=color, edgecolor="white", linewidth=0.8)
        bottom += vals
    ax.set_xticks(x, labels=df["stressor"].tolist())
    ax.set_ylim(0.0, 1.0)
    ax.set_ylabel("Mean contribution share")
    ax.set_title("Final-config diagnosis contribution share by tier")
    ax.legend(frameon=True)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(out_png, dpi=240, bbox_inches="tight")
    plt.close(fig)


def plot_mechanism_shares(df: pd.DataFrame, out_png: Path) -> None:
    if df.empty:
        return
    fig, ax = plt.subplots(figsize=(8.6, 5.0))
    x = np.arange(len(df))
    bottom = np.zeros(len(df), dtype=float)
    series = [
        ("compute_share", "Compute", "#5c6bc0"),
        ("memory_io_share", "Memory/I/O", "#26a69a"),
        ("thermal_power_share", "Thermal/Power", "#ef5350"),
        ("scheduler_runtime_share", "Scheduler/Runtime", "#8d6e63"),
        ("platform_pressure_share", "Platform Pressure", "#78909c"),
    ]
    for col, label, color in series:
        vals = df[col].to_numpy(dtype=float)
        ax.bar(x, vals, bottom=bottom, label=label, color=color, edgecolor="white", linewidth=0.8)
        bottom += vals
    ax.set_xticks(x, labels=df["stressor"].tolist())
    ax.set_ylim(0.0, 1.0)
    ax.set_ylabel("Mean mechanism share")
    ax.set_title("Final-config mechanism diagnosis share by stressor")
    ax.legend(frameon=True, ncol=2)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(out_png, dpi=240, bbox_inches="tight")
    plt.close(fig)


def plot_detection_latency(df: pd.DataFrame, out_png: Path) -> None:
    if df.empty:
        return
    fig, ax = plt.subplots(figsize=(7.0, 4.8))
    vals = df["median_time_to_detect_s"].to_numpy(dtype=float)
    ax.bar(df["config"], vals, color=["#90a4ae", "#66bb6a", "#ffa726"][: len(df)])
    ax.set_ylabel("Median time-to-detect (s)")
    ax.set_title("Sequential detection latency by observation head")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
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
        "--protocol",
        choices=["workload_holdout", "global"],
        default="global",
        help="Evaluation protocol: workload_holdout (strict) or global benign split (paper-style).",
    )
    args = ap.parse_args()

    root = args.root.expanduser().resolve()
    out_dir = args.out_dir.expanduser().resolve() if args.out_dir else root / "results_dice_full"
    fig_dir = out_dir / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)
    fig_dir.mkdir(parents=True, exist_ok=True)

    tier_features = {t: common_features_per_tier(root, t) for t in TIER_FILE.keys()}
    for t, fs in tier_features.items():
        print(f"[INFO] {t}: common features={len(fs)}")

    preds = []
    fold_rows = []
    diagnostic_records: List[Dict[str, object]] = []

    for cfg_name, tiers in CONFIGS.items():
        print(f"[INFO] training config={cfg_name} tiers={tiers}")
        case_X = {}
        feature_names_cfg = None
        for case in all_cases():
            X, names = build_case_matrix(
                root,
                case,
                tiers=tiers,
                feature_map=tier_features,
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
                fold_rows.append(
                    {
                        "config": cfg_name,
                        "holdout_workload": holdout_w,
                        "roc_auc": safe_auc(y, s_run),
                        "pr_auc": safe_ap(y, s_run),
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
            fold_rows.append(
                {
                    "config": cfg_name,
                    "holdout_workload": "ALL",
                    "roc_auc": safe_auc(y, s_run),
                    "pr_auc": safe_ap(y, s_run),
                    "fpr": float(np.mean((fd["label"] == 0) & (fd["run_alert"] == 1))),
                    "tpr": float(np.mean((fd["label"] == 1) & (fd["run_alert"] == 1))),
                    "n_features": int(fd["n_features"].iloc[0]),
                }
            )

    pred_df = pd.DataFrame(preds).sort_values(["config", "workload", "stressor"])
    fold_df = pd.DataFrame(fold_rows).sort_values(["config", "holdout_workload"])
    diag_df = pd.DataFrame([{k: v for k, v in row.items() if not k.startswith("_")} for row in diagnostic_records]).sort_values(
        ["config", "workload", "stressor"]
    )

    # Workload-conditioned score head: distance to workload nominal template.
    pred_df["nominal_template_score"] = np.nan
    pred_df["run_score_wc"] = pred_df["run_score"]
    for cfg, d in pred_df.groupby("config"):
        base = d[d["stressor"] == "NOMINAL"].set_index("workload")["run_score"].to_dict()
        idx = d.index
        pred_df.loc[idx, "nominal_template_score"] = d["workload"].map(base).to_numpy(dtype=float)
        pred_df.loc[idx, "run_score_wc"] = np.abs(
            pred_df.loc[idx, "run_score"].to_numpy(dtype=float)
            - pred_df.loc[idx, "nominal_template_score"].to_numpy(dtype=float)
        )

    overall_rows = []
    for cfg, d in pred_df.groupby("config"):
        y = d["label"].to_numpy(dtype=int)
        s_run = d["run_score"].to_numpy(dtype=float)
        s_wc = d["run_score_wc"].to_numpy(dtype=float)
        overall_rows.append(
            {
                "config": cfg,
                "n_cases": int(len(d)),
                "n_features": int(d["n_features"].iloc[0]),
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
    holdout_df = build_holdout_robustness_summary(fold_df)

    pred_df.to_csv(out_dir / "case_predictions.csv", index=False)
    fold_df.to_csv(out_dir / "fold_metrics.csv", index=False)
    overall_df.to_csv(out_dir / "overall_metrics.csv", index=False)
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
