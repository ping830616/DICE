#!/usr/bin/env python3
"""
Uncertainty-aware DICE ensemble evaluation.

This experiment estimates digital-twin uncertainty by fitting a bootstrap
ensemble of benign-trained micro-twins and measuring disagreement on run scores.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import tempfile
from time import perf_counter

import numpy as np
import pandas as pd

from train_eval_dice_pipeline import (
    CONFIGS,
    FEATURE_PROFILES,
    all_cases,
    build_case_matrix,
    common_features_per_tier,
    evaluate_run,
    safe_ap,
    safe_auc,
    train_bundle,
    workload_conditioned_scores,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET_ROOT = PROJECT_ROOT / "data generation" / "dataset" / "ITC_M2Pro_DATA"

os.environ.setdefault("MPLCONFIGDIR", tempfile.mkdtemp(prefix="dice-uncertainty-mpl-"))
os.environ.setdefault("MPLBACKEND", "Agg")


def paper_dir(root: Path, profile: str) -> Path:
    out = root / "results_itc_paper" / profile
    out.mkdir(parents=True, exist_ok=True)
    return out


def log_score_std(x: np.ndarray | float) -> np.ndarray | float:
    arr = np.maximum(np.asarray(x, dtype=float), 0.0)
    out = np.log10(1.0 + arr)
    if np.isscalar(x):
        return float(out)
    return out


def bootstrap_train_runs(train_benign_runs: dict[str, np.ndarray], rng: np.random.Generator) -> dict[str, np.ndarray]:
    keys = sorted(train_benign_runs)
    sampled = rng.choice(keys, size=len(keys), replace=True)
    return {f"boot_{i}_{key}": train_benign_runs[str(key)] for i, key in enumerate(sampled)}


def summarize_uncertainty(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for protocol, protocol_df in df.groupby("protocol", sort=False):
        for config, part in protocol_df.groupby("config", sort=False):
            if part.empty:
                continue
            y = part["label"].to_numpy(dtype=int)
            s_mean = part["run_score_mean"].to_numpy(dtype=float)
            s_wc_mean = part["run_score_wc_mean"].to_numpy(dtype=float)
            u = part["run_score_std"].to_numpy(dtype=float)
            u_log = part["run_score_std_log10"].to_numpy(dtype=float)
            benign_u = part.loc[part["label"] == 0, "run_score_std"].to_numpy(dtype=float)
            anomaly_u = part.loc[part["label"] == 1, "run_score_std"].to_numpy(dtype=float)
            benign_u_log = part.loc[part["label"] == 0, "run_score_std_log10"].to_numpy(dtype=float)
            anomaly_u_log = part.loc[part["label"] == 1, "run_score_std_log10"].to_numpy(dtype=float)
            gate = float(np.quantile(benign_u, 0.95)) if len(benign_u) else float("nan")
            gate_log = float(np.quantile(benign_u_log, 0.95)) if len(benign_u_log) else float("nan")
            rows.append(
                {
                    "protocol": protocol,
                    "config": config,
                    "n_cases": int(len(part)),
                    "n_features": int(part["n_features"].iloc[0]),
                    "roc_auc_mean_score": safe_auc(y, s_mean),
                    "pr_auc_mean_score": safe_ap(y, s_mean),
                    "roc_auc_wc_mean_score": safe_auc(y, s_wc_mean),
                    "pr_auc_wc_mean_score": safe_ap(y, s_wc_mean),
                    "uncertainty_auc": safe_auc(y, u),
                    "uncertainty_pr_auc": safe_ap(y, u),
                    "uncertainty_log_auc": safe_auc(y, u_log),
                    "uncertainty_log_pr_auc": safe_ap(y, u_log),
                    "benign_mean_score_std": float(np.nanmean(benign_u)) if len(benign_u) else float("nan"),
                    "anomaly_mean_score_std": float(np.nanmean(anomaly_u)) if len(anomaly_u) else float("nan"),
                    "benign_p95_score_std": gate,
                    "benign_over_p95_rate": float(np.mean(benign_u > gate)) if len(benign_u) and np.isfinite(gate) else float("nan"),
                    "anomaly_over_benign_p95_rate": float(np.mean(anomaly_u > gate)) if len(anomaly_u) and np.isfinite(gate) else float("nan"),
                    "benign_mean_log_score_std": float(np.nanmean(benign_u_log)) if len(benign_u_log) else float("nan"),
                    "anomaly_mean_log_score_std": float(np.nanmean(anomaly_u_log)) if len(anomaly_u_log) else float("nan"),
                    "benign_p95_log_score_std": gate_log,
                    "benign_over_p95_log_rate": float(np.mean(benign_u_log > gate_log)) if len(benign_u_log) and np.isfinite(gate_log) else float("nan"),
                    "anomaly_over_benign_p95_log_rate": float(np.mean(anomaly_u_log > gate_log)) if len(anomaly_u_log) and np.isfinite(gate_log) else float("nan"),
                    "mean_alert_probability_benign": float(part.loc[part["label"] == 0, "run_alert_mean"].mean()),
                    "mean_alert_probability_anomaly": float(part.loc[part["label"] == 1, "run_alert_mean"].mean()),
                }
            )
    return pd.DataFrame(rows).sort_values(["protocol", "config"]).reset_index(drop=True)


def summarize_uncertainty_by_holdout(df: pd.DataFrame) -> pd.DataFrame:
    d = df[df["protocol"] == "workload_holdout"].copy()
    if d.empty:
        return pd.DataFrame()
    rows = []
    for config, cfg_df in d.groupby("config", sort=False):
        for workload, part in cfg_df.groupby("holdout_workload", sort=False):
            benign_u = part.loc[part["label"] == 0, "run_score_std"].to_numpy(dtype=float)
            anomaly_u = part.loc[part["label"] == 1, "run_score_std"].to_numpy(dtype=float)
            benign_u_log = part.loc[part["label"] == 0, "run_score_std_log10"].to_numpy(dtype=float)
            anomaly_u_log = part.loc[part["label"] == 1, "run_score_std_log10"].to_numpy(dtype=float)
            rows.append(
                {
                    "config": config,
                    "holdout_workload": workload,
                    "n_cases": int(len(part)),
                    "mean_run_score_std": float(part["run_score_std"].mean()),
                    "mean_log_run_score_std": float(part["run_score_std_log10"].mean()),
                    "benign_mean_score_std": float(np.nanmean(benign_u)) if len(benign_u) else float("nan"),
                    "anomaly_mean_score_std": float(np.nanmean(anomaly_u)) if len(anomaly_u) else float("nan"),
                    "benign_mean_log_score_std": float(np.nanmean(benign_u_log)) if len(benign_u_log) else float("nan"),
                    "anomaly_mean_log_score_std": float(np.nanmean(anomaly_u_log)) if len(anomaly_u_log) else float("nan"),
                    "uncertainty_auc": safe_auc(part["label"].to_numpy(dtype=int), part["run_score_std"].to_numpy(dtype=float)),
                    "uncertainty_log_auc": safe_auc(part["label"].to_numpy(dtype=int), part["run_score_std_log10"].to_numpy(dtype=float)),
                    "roc_auc_mean_score": safe_auc(part["label"].to_numpy(dtype=int), part["run_score_mean"].to_numpy(dtype=float)),
                }
            )
    return pd.DataFrame(rows).sort_values(["config", "holdout_workload"]).reset_index(drop=True)


def add_workload_conditioned_means(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["nominal_template_score_mean"] = np.nan
    out["run_score_wc_mean"] = out["run_score_mean"]
    group_cols = ["protocol", "config"]
    if "holdout_workload" in out.columns:
        group_cols = ["protocol", "config", "holdout_workload"]
    for _, part in out.groupby(group_cols, sort=False):
        nominal, wc = workload_conditioned_scores(
            part[["workload", "stressor", "run_score_mean"]].rename(columns={"run_score_mean": "run_score"})
        )
        out.loc[part.index, "nominal_template_score_mean"] = nominal
        out.loc[part.index, "run_score_wc_mean"] = wc
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=DEFAULT_DATASET_ROOT)
    ap.add_argument("--feature_profile", choices=sorted(FEATURE_PROFILES.keys()), required=True)
    ap.add_argument("--source_hz", type=int, default=5)
    ap.add_argument("--fit_ratio", type=float, default=0.6)
    ap.add_argument("--block_B", type=int, default=60)
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--persist_k", type=int, default=3)
    ap.add_argument("--gain", type=float, default=0.35)
    ap.add_argument("--ridge_lambda", type=float, default=1e-3)
    ap.add_argument("--ensemble_size", type=int, default=12)
    ap.add_argument("--bootstrap_seed", type=int, default=11)
    args = ap.parse_args()

    root = args.root.expanduser().resolve()
    tier_files = FEATURE_PROFILES[args.feature_profile]
    out_dir = paper_dir(root, args.feature_profile)

    t0 = perf_counter()
    tier_features = {t: common_features_per_tier(root, t, tier_files) for t in tier_files.keys()}
    case_X_by_cfg: dict[str, dict[str, np.ndarray]] = {}
    feature_names_by_cfg: dict[str, list[str]] = {}
    for cfg_name, tiers in CONFIGS.items():
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
        case_X_by_cfg[cfg_name] = case_X
        feature_names_by_cfg[cfg_name] = feature_names_cfg or []

    rows = []
    rng = np.random.default_rng(args.bootstrap_seed)

    for protocol in ["global", "workload_holdout"]:
        for cfg_name in CONFIGS:
            case_X = case_X_by_cfg[cfg_name]
            feature_names = feature_names_by_cfg[cfg_name]
            if protocol == "global":
                train_nominal = {
                    case.case_id: case_X[case.case_id]
                    for case in all_cases()
                    if case.stressor == "NOMINAL"
                }
                test_cases = list(all_cases())
                holdouts = [("ALL", train_nominal, test_cases)]
            else:
                holdouts = []
                for holdout_workload in sorted({case.workload for case in all_cases()}):
                    train_nominal = {
                        case.case_id: case_X[case.case_id]
                        for case in all_cases()
                        if case.stressor == "NOMINAL" and case.workload != holdout_workload
                    }
                    test_cases = [case for case in all_cases() if case.workload == holdout_workload]
                    holdouts.append((holdout_workload, train_nominal, test_cases))

            for holdout_workload, train_nominal, test_cases in holdouts:
                case_records = {}
                for ensemble_idx in range(args.ensemble_size):
                    boot_runs = bootstrap_train_runs(train_nominal, rng)
                    bundle = train_bundle(
                        train_benign_runs=boot_runs,
                        feature_names=feature_names,
                        fit_ratio=args.fit_ratio,
                        B=args.block_B,
                        alpha=args.alpha,
                        gain=args.gain,
                        ridge_lambda=args.ridge_lambda,
                    )
                    for case in test_cases:
                        metrics, _, _, _ = evaluate_run(
                            case_X[case.case_id],
                            bundle,
                            B=args.block_B,
                            alpha=args.alpha,
                            persist_k=args.persist_k,
                            gain=args.gain,
                        )
                        rec = case_records.setdefault(
                            case.case_id,
                            {
                                "feature_profile": args.feature_profile,
                                "protocol": protocol,
                                "config": cfg_name,
                                "holdout_workload": holdout_workload,
                                "case_id": case.case_id,
                                "workload": case.workload,
                                "stressor": case.stressor,
                                "label": case.label,
                                "n_features": len(feature_names),
                                "_run_score": [],
                                "_run_alert": [],
                                "_min_pvalue": [],
                            },
                        )
                        rec["_run_score"].append(float(metrics["run_score"]))
                        rec["_run_alert"].append(float(metrics["run_alert"]))
                        rec["_min_pvalue"].append(float(metrics["min_pvalue"]))

                for rec in case_records.values():
                    score_arr = np.asarray(rec.pop("_run_score"), dtype=float)
                    alert_arr = np.asarray(rec.pop("_run_alert"), dtype=float)
                    pval_arr = np.asarray(rec.pop("_min_pvalue"), dtype=float)
                    rec["ensemble_size"] = int(len(score_arr))
                    rec["run_score_mean"] = float(np.mean(score_arr))
                    rec["run_score_std"] = float(np.std(score_arr))
                    rec["run_score_std_log10"] = float(log_score_std(rec["run_score_std"]))
                    rec["run_score_cv"] = float(np.std(score_arr) / (np.mean(score_arr) + 1e-12))
                    rec["run_alert_mean"] = float(np.mean(alert_arr))
                    rec["min_pvalue_mean"] = float(np.mean(pval_arr))
                    rec["min_pvalue_std"] = float(np.std(pval_arr))
                    rows.append(rec)

    case_df = pd.DataFrame(rows).sort_values(["protocol", "config", "holdout_workload", "workload", "stressor"]).reset_index(drop=True)
    case_df = add_workload_conditioned_means(case_df)
    summary_df = summarize_uncertainty(case_df)
    by_holdout_df = summarize_uncertainty_by_holdout(case_df)

    case_csv = out_dir / "uncertainty_case_predictions.csv"
    summary_csv = out_dir / "uncertainty_summary.csv"
    holdout_csv = out_dir / "uncertainty_holdout_summary.csv"
    context_json = out_dir / "uncertainty_context.json"

    case_df.to_csv(case_csv, index=False)
    summary_df.to_csv(summary_csv, index=False)
    by_holdout_df.to_csv(holdout_csv, index=False)
    context_json.write_text(
        json.dumps(
            {
                "feature_profile": args.feature_profile,
                "dataset_root": str(root),
                "ensemble_size": int(args.ensemble_size),
                "bootstrap_seed": int(args.bootstrap_seed),
                "fit_ratio": float(args.fit_ratio),
                "block_B": int(args.block_B),
                "alpha": float(args.alpha),
                "persist_k": int(args.persist_k),
                "gain": float(args.gain),
                "ridge_lambda": float(args.ridge_lambda),
                "elapsed_s": round(perf_counter() - t0, 3),
            },
            indent=2,
        )
        + "\n"
    )

    print("[OK] wrote:", case_csv)
    print("[OK] wrote:", summary_csv)
    print("[OK] wrote:", holdout_csv)
    print("[OK] wrote:", context_json)
    if not summary_df.empty:
        print(summary_df.to_string(index=False))


if __name__ == "__main__":
    main()
