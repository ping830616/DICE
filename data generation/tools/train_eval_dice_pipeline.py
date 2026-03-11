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
    precision_recall_curve,
    roc_auc_score,
    roc_curve,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET_ROOT = PROJECT_ROOT / "dataset" / "ITC_M2Pro_DATA"


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
) -> Dict[str, float]:
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

    return {
        "run_score": run_score,
        "run_alert": run_alert,
        "min_pvalue": float(np.min(pv)) if len(pv) else 1.0,
        "peak_block_score": peak_score,
        "n_blocks": int(len(sc)),
        "n_block_alerts": int(np.sum(block_alert)),
        "n_persist_alerts": int(np.sum(persist)),
    }


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
                    out = evaluate_run(
                        case_X[case.case_id],
                        bundle,
                        B=args.block_B,
                        alpha=args.alpha,
                        persist_k=args.persist_k,
                        gain=args.gain,
                    )
                    preds.append(
                        {
                            "config": cfg_name,
                            "holdout_workload": holdout_w,
                            "case_id": case.case_id,
                            "workload": case.workload,
                            "stressor": case.stressor,
                            "label": case.label,
                            **out,
                            "n_features": len(bundle.feature_names),
                            "tau": bundle.tau,
                        }
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
                out = evaluate_run(
                    case_X[case.case_id],
                    bundle,
                    B=args.block_B,
                    alpha=args.alpha,
                    persist_k=args.persist_k,
                    gain=args.gain,
                )
                preds.append(
                    {
                        "config": cfg_name,
                        "holdout_workload": "ALL",
                        "case_id": case.case_id,
                        "workload": case.workload,
                        "stressor": case.stressor,
                        "label": case.label,
                        **out,
                        "n_features": len(bundle.feature_names),
                        "tau": bundle.tau,
                    }
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

    pred_df.to_csv(out_dir / "case_predictions.csv", index=False)
    fold_df.to_csv(out_dir / "fold_metrics.csv", index=False)
    overall_df.to_csv(out_dir / "overall_metrics.csv", index=False)
    stress_df.to_csv(out_dir / "stressor_metrics_final_config.csv", index=False)

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
    md.append("## Files")
    for p in [
        out_dir / "overall_metrics.csv",
        out_dir / "stressor_metrics_final_config.csv",
        out_dir / "overall_metrics.tex",
        out_dir / "stressor_metrics_final_config.tex",
        fig_dir / "fig_roc_pr_by_config.png",
        fig_dir / "fig_roc_pr_by_config_wc.png",
        fig_dir / "fig_run_score_boxplot.png",
        fig_dir / "fig_run_score_boxplot_wc.png",
    ]:
        md.append(f"- `{p}`")
    (out_dir / "RESULTS_SUMMARY.md").write_text("\n".join(md) + "\n")

    print(f"[OK] wrote results to: {out_dir}")
    print("[OK] overall metrics:")
    print(overall_df.to_string(index=False))
    print("[OK] final config stressor metrics:")
    print(stress_df.to_string(index=False))
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
