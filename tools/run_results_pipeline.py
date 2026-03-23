#!/usr/bin/env python3
"""
Terminal-first orchestration for reproducible DICE results generation.

This replaces the notebook workflow with a deterministic CLI wrapper that:
- runs the paper-style results analysis script
- runs the full DICE retrain/evaluation pipeline
- optionally runs workload-holdout evaluation
- optionally runs the tuning sweep
- records a runtime manifest with dataset hash and package versions
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PROJECT_ROOT
DEFAULT_DATASET_ROOT = REPO_ROOT / "data generation" / "dataset" / "ITC_M2Pro_DATA"
ANALYSIS_SCRIPT = PROJECT_ROOT / "tools" / "generate_results_analysis.py"
FULL_SCRIPT = PROJECT_ROOT / "tools" / "train_eval_dice_pipeline.py"

STAGE1_GAINS = [0.15, 0.25, 0.35, 0.50]
STAGE1_BLOCKS = [30, 60, 90, 120]
STAGE2_ALPHAS = [0.01, 0.02, 0.05, 0.10]
STAGE2_PERSISTS = [1, 2, 3, 5]


def deterministic_env() -> Dict[str, str]:
    env = os.environ.copy()
    settings = {
        "MPLCONFIGDIR": env.get("MPLCONFIGDIR", tempfile.mkdtemp(prefix="dice-mpl-")),
        "MPLBACKEND": env.get("MPLBACKEND", "Agg"),
        "OPENBLAS_NUM_THREADS": env.get("OPENBLAS_NUM_THREADS", "1"),
        "OMP_NUM_THREADS": env.get("OMP_NUM_THREADS", "1"),
        "MKL_NUM_THREADS": env.get("MKL_NUM_THREADS", "1"),
        "NUMEXPR_NUM_THREADS": env.get("NUMEXPR_NUM_THREADS", "1"),
        "VECLIB_MAXIMUM_THREADS": env.get("VECLIB_MAXIMUM_THREADS", "1"),
        "BLIS_NUM_THREADS": env.get("BLIS_NUM_THREADS", "1"),
        "PYTHONHASHSEED": env.get("PYTHONHASHSEED", "0"),
    }
    env.update(settings)
    os.environ.update(settings)
    return env


def dataset_tree_sha256(root: Path) -> Dict[str, object]:
    hasher = hashlib.sha256()
    count = 0
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        rel = path.relative_to(root).as_posix()
        top_level = rel.split("/", 1)[0]
        if top_level.startswith("results_"):
            continue
        hasher.update(rel.encode("utf-8"))
        with path.open("rb") as handle:
            while True:
                chunk = handle.read(1024 * 1024)
                if not chunk:
                    break
                hasher.update(chunk)
        count += 1
    return {"file_count": count, "sha256": hasher.hexdigest()}


def file_sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()


def package_versions() -> Dict[str, str]:
    packages = [
        "matplotlib",
        "numpy",
        "pandas",
        "psutil",
        "scikit-learn",
        "scipy",
        "joblib",
        "threadpoolctl",
        "python-dateutil",
        "pytz",
        "tzdata",
    ]
    return {pkg.replace("-", "_"): importlib.metadata.version(pkg) for pkg in packages}


def json_ready(value: object) -> object:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(k): json_ready(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_ready(v) for v in value]
    return value


def run_checked(cmd: List[str], env: Dict[str, str], cwd: Path) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(cmd, cwd=str(cwd), env=env, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(
            f"Command failed with exit code {proc.returncode}: {' '.join(cmd)}\n"
            f"STDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    return proc


def ensure_dataset_root(root: Path) -> None:
    needed = [
        root / "tier0",
        root / "tier1_alt",
        root / "tier2",
        root / "no_nan_report.json",
    ]
    missing = [str(p) for p in needed if not p.exists()]
    if missing:
        raise FileNotFoundError(f"Dataset root is missing required files/folders: {missing}")


def run_analysis(root: Path, env: Dict[str, str], source_hz: int) -> Path:
    out_dir = root / "results_analysis"
    cmd = [
        sys.executable,
        str(ANALYSIS_SCRIPT),
        "--root",
        str(root),
        "--source_hz",
        str(source_hz),
        "--out_dir",
        str(out_dir),
    ]
    run_checked(cmd, env=env, cwd=PROJECT_ROOT)
    return out_dir


def run_full(
    root: Path,
    env: Dict[str, str],
    protocol: str,
    source_hz: int,
    fit_ratio: float,
    block_B: int,
    alpha: float,
    persist_k: int,
    gain: float,
    ridge_lambda: float,
    out_dir: Optional[Path] = None,
) -> Path:
    resolved_out = out_dir if out_dir else (
        root / ("results_dice_full_holdout" if protocol == "workload_holdout" else "results_dice_full")
    )
    cmd = [
        sys.executable,
        str(FULL_SCRIPT),
        "--root",
        str(root),
        "--protocol",
        protocol,
        "--source_hz",
        str(source_hz),
        "--fit_ratio",
        str(fit_ratio),
        "--block_B",
        str(block_B),
        "--alpha",
        str(alpha),
        "--persist_k",
        str(persist_k),
        "--gain",
        str(gain),
        "--ridge_lambda",
        str(ridge_lambda),
        "--out_dir",
        str(resolved_out),
    ]
    run_checked(cmd, env=env, cwd=PROJECT_ROOT)
    return resolved_out


def run_tuning(
    root: Path,
    env: Dict[str, str],
    source_hz: int,
    fit_ratio: float,
    ridge_lambda: float,
) -> Path:
    out_tune = root / "results_dice_tuning"
    out_runs = out_tune / "runs"
    out_tune.mkdir(parents=True, exist_ok=True)
    out_runs.mkdir(parents=True, exist_ok=True)

    summary_rows = []
    alpha_fixed = 0.05
    persist_fixed = 3

    for gain in STAGE1_GAINS:
        for block_B in STAGE1_BLOCKS:
            tag = f"g{gain}_B{block_B}_a{alpha_fixed}_k{persist_fixed}"
            out_dir = out_runs / tag
            try:
                run_full(
                    root=root,
                    env=env,
                    protocol="global",
                    source_hz=source_hz,
                    fit_ratio=fit_ratio,
                    block_B=block_B,
                    alpha=alpha_fixed,
                    persist_k=persist_fixed,
                    gain=gain,
                    ridge_lambda=ridge_lambda,
                    out_dir=out_dir,
                )
            except RuntimeError:
                summary_rows.append(
                    {
                        "stage": "gain_block",
                        "gain": gain,
                        "block_B": block_B,
                        "alpha": alpha_fixed,
                        "persist_k": persist_fixed,
                        "status": "fail",
                    }
                )
                continue

            overall = pd.read_csv(out_dir / "overall_metrics.csv")
            row = overall[overall["config"] == "tier0_tier1_tier2"].iloc[0]
            summary_rows.append(
                {
                    "stage": "gain_block",
                    "gain": gain,
                    "block_B": block_B,
                    "alpha": alpha_fixed,
                    "persist_k": persist_fixed,
                    "status": "ok",
                    "roc_auc": float(row["roc_auc"]),
                    "pr_auc": float(row["pr_auc"]),
                    "roc_auc_wc": float(row["roc_auc_wc"]),
                    "pr_auc_wc": float(row["pr_auc_wc"]),
                    "fpr_run_alert": float(row["fpr_run_alert"]),
                    "tpr_run_alert": float(row["tpr_run_alert"]),
                    "out_dir": str(out_dir),
                }
            )

    stage1 = pd.DataFrame([r for r in summary_rows if r.get("stage") == "gain_block" and r.get("status") == "ok"])
    if stage1.empty:
        raise RuntimeError("Tuning stage 1 produced no successful runs.")

    best = stage1.sort_values(["roc_auc", "pr_auc", "tpr_run_alert"], ascending=False).iloc[0]
    best_gain = float(best["gain"])
    best_block = int(best["block_B"])

    for alpha in STAGE2_ALPHAS:
        for persist_k in STAGE2_PERSISTS:
            tag = f"g{best_gain}_B{best_block}_a{alpha}_k{persist_k}"
            out_dir = out_runs / tag
            try:
                run_full(
                    root=root,
                    env=env,
                    protocol="global",
                    source_hz=source_hz,
                    fit_ratio=fit_ratio,
                    block_B=best_block,
                    alpha=alpha,
                    persist_k=persist_k,
                    gain=best_gain,
                    ridge_lambda=ridge_lambda,
                    out_dir=out_dir,
                )
            except RuntimeError:
                summary_rows.append(
                    {
                        "stage": "alpha_persist",
                        "gain": best_gain,
                        "block_B": best_block,
                        "alpha": alpha,
                        "persist_k": persist_k,
                        "status": "fail",
                    }
                )
                continue

            overall = pd.read_csv(out_dir / "overall_metrics.csv")
            row = overall[overall["config"] == "tier0_tier1_tier2"].iloc[0]
            summary_rows.append(
                {
                    "stage": "alpha_persist",
                    "gain": best_gain,
                    "block_B": best_block,
                    "alpha": alpha,
                    "persist_k": persist_k,
                    "status": "ok",
                    "roc_auc": float(row["roc_auc"]),
                    "pr_auc": float(row["pr_auc"]),
                    "roc_auc_wc": float(row["roc_auc_wc"]),
                    "pr_auc_wc": float(row["pr_auc_wc"]),
                    "fpr_run_alert": float(row["fpr_run_alert"]),
                    "tpr_run_alert": float(row["tpr_run_alert"]),
                    "out_dir": str(out_dir),
                }
            )

    summary = pd.DataFrame(summary_rows)
    stage1 = summary[(summary["stage"] == "gain_block") & (summary["status"] == "ok")].copy()
    stage2 = summary[(summary["stage"] == "alpha_persist") & (summary["status"] == "ok")].copy()
    if stage2.empty:
        raise RuntimeError("Tuning stage 2 produced no successful runs.")

    stage1.to_csv(out_tune / "sweep_stage1_gain_block.csv", index=False)
    stage2.to_csv(out_tune / "sweep_stage2_alpha_persist.csv", index=False)
    summary.to_csv(out_tune / "sweep_summary_all.csv", index=False)

    feasible = stage2[stage2["fpr_run_alert"] <= 0.25]
    if feasible.empty:
        feasible = stage2
    recommended = feasible.sort_values(["tpr_run_alert", "roc_auc", "pr_auc"], ascending=False).iloc[0]
    rec = {
        "gain": float(recommended["gain"]),
        "block_B": int(recommended["block_B"]),
        "alpha": float(recommended["alpha"]),
        "persist_k": int(recommended["persist_k"]),
        "out_dir": str(recommended["out_dir"]),
    }

    (out_tune / "recommended_config.json").write_text(json.dumps(rec, indent=2))
    rec_out = Path(rec["out_dir"])
    pd.read_csv(rec_out / "overall_metrics.csv").to_csv(out_tune / "recommended_overall_metrics.csv", index=False)
    pd.read_csv(rec_out / "stressor_metrics_final_config.csv").to_csv(
        out_tune / "recommended_stressor_metrics.csv", index=False
    )
    pd.read_csv(rec_out / "fold_metrics.csv").to_csv(out_tune / "recommended_fold_metrics.csv", index=False)
    return out_tune


def write_manifest(
    manifest_dir: Path,
    root: Path,
    env: Dict[str, str],
    args: argparse.Namespace,
    outputs: Dict[str, str],
) -> None:
    manifest_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "analysis_root": str(PROJECT_ROOT),
        "repo_root": str(REPO_ROOT),
        "dataset_root": str(root),
        "dataset_digest": dataset_tree_sha256(root),
        "python": {
            "executable": sys.executable,
            "version": sys.version,
        },
        "platform": {
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor(),
        },
        "package_versions": package_versions(),
        "deterministic_env": {
            key: env[key]
            for key in [
                "MPLCONFIGDIR",
                "MPLBACKEND",
                "OPENBLAS_NUM_THREADS",
                "OMP_NUM_THREADS",
                "MKL_NUM_THREADS",
                "NUMEXPR_NUM_THREADS",
                "VECLIB_MAXIMUM_THREADS",
                "BLIS_NUM_THREADS",
                "PYTHONHASHSEED",
            ]
        },
        "environment_files": {
            name: {"path": str(path), "sha256": file_sha256(path)}
            for name, path in {
                "requirements_txt": PROJECT_ROOT / "requirements.txt",
                "environment_yml": PROJECT_ROOT / "environment.yml",
            }.items()
            if path.exists()
        },
        "parameters": json_ready(vars(args)),
        "outputs": outputs,
    }
    (manifest_dir / "run_manifest.json").write_text(json.dumps(json_ready(manifest), indent=2), encoding="utf-8")


def copy_output(src: Path, bundle_root: Path, rel_dst: str) -> Optional[str]:
    if not src.exists():
        return None
    dst = bundle_root / rel_dst
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return str(dst)


def package_itc_submission(root: Path, outputs: Dict[str, str]) -> Dict[str, str]:
    paper_dir = root / "results_itc_paper"
    appendix_dir = root / "results_itc_appendix"
    paper_dir.mkdir(parents=True, exist_ok=True)
    appendix_dir.mkdir(parents=True, exist_ok=True)

    analysis_dir = Path(outputs["results_analysis"]) if "results_analysis" in outputs else None
    full_dir = Path(outputs["results_dice_full"]) if "results_dice_full" in outputs else None
    holdout_dir = Path(outputs["results_dice_full_holdout"]) if "results_dice_full_holdout" in outputs else None
    tuning_dir = Path(outputs["results_dice_tuning"]) if "results_dice_tuning" in outputs else None
    manifest_path = root / "results_portable" / "run_manifest.json"

    copied_paper: List[str] = []
    copied_appendix: List[str] = []

    def maybe_copy(base: Optional[Path], bundle_root: Path, rel_src: str, rel_dst: str, copied: List[str]) -> None:
        if base is None:
            return
        out = copy_output(base / rel_src, bundle_root, rel_dst)
        if out:
            copied.append(rel_dst)

    if analysis_dir:
        for rel in [
            "table_overall_metrics.csv",
            "table_stressor_metrics.csv",
            "table_workload_summary.csv",
            "table_overall_metrics.tex",
            "table_stressor_metrics.tex",
            "RESULTS_SUMMARY.md",
            "figures/fig_heatmap_pr_auc.png",
            "figures/fig_run_score_distributions.png",
            "figures/fig_af_timeseries_tier2.png",
        ]:
            maybe_copy(analysis_dir, paper_dir, rel, f"analysis/{Path(rel).name}", copied_paper)
        for rel in [
            "table_feature_inventory.csv",
            "table_case_quality.csv",
            "table_run_scores.csv",
            "figures/fig_heatmap_roc_auc.png",
            "figures/fig_af_timeseries_tier0.png",
            "figures/fig_af_timeseries_tier1_alt.png",
            "figures/fig_af_timeseries_tier2.png",
        ]:
            maybe_copy(analysis_dir, appendix_dir, rel, f"analysis/{Path(rel).name}", copied_appendix)

    if full_dir:
        for rel in [
            "overall_metrics.csv",
            "stressor_metrics_final_config.csv",
            "sequential_metrics.csv",
            "stressor_diagnosis_metrics.csv",
            "mechanism_group_summary.csv",
            "overall_metrics.tex",
            "stressor_metrics_final_config.tex",
            "sequential_metrics.tex",
            "stressor_diagnosis_metrics.tex",
            "RESULTS_SUMMARY.md",
            "figures/fig_roc_pr_by_config_wc.png",
            "figures/fig_run_score_boxplot_wc.png",
            "figures/fig_detection_latency.png",
            "figures/fig_stressor_confusion_matrix.png",
            "figures/fig_stressor_tier_contributions.png",
            "figures/fig_mechanism_group_summary.png",
        ]:
            maybe_copy(full_dir, paper_dir, rel, f"full/{Path(rel).name}", copied_paper)
        for rel in [
            "case_predictions.csv",
            "case_diagnosis_summary.csv",
            "stressor_diagnosis_predictions.csv",
            "stressor_confusion_matrix.csv",
            "stressor_tier_contributions.csv",
            "mechanism_group_summary.csv",
            "sequential_metrics.csv",
            "stressor_feature_diagnosis_predictions.csv",
            "stressor_feature_diagnosis_metrics.csv",
            "stressor_feature_confusion_matrix.csv",
            "overall_metrics.csv",
            "stressor_metrics_final_config.csv",
            "stressor_diagnosis_metrics.csv",
        ]:
            maybe_copy(full_dir, appendix_dir, rel, f"full/{Path(rel).name}", copied_appendix)

    if holdout_dir:
        for rel in [
            "fold_metrics.csv",
            "case_predictions.csv",
            "overall_metrics.csv",
            "holdout_robustness_summary.csv",
            "RESULTS_SUMMARY.md",
            "figures/fig_roc_pr_by_config_wc.png",
        ]:
            maybe_copy(holdout_dir, appendix_dir, rel, f"holdout/{Path(rel).name}", copied_appendix)

    if tuning_dir:
        for rel in [
            "recommended_config.json",
            "recommended_overall_metrics.csv",
            "recommended_stressor_metrics.csv",
            "recommended_fold_metrics.csv",
            "sweep_stage1_gain_block.csv",
            "sweep_stage2_alpha_persist.csv",
            "sweep_summary_all.csv",
        ]:
            maybe_copy(tuning_dir, appendix_dir, rel, f"tuning/{Path(rel).name}", copied_appendix)

    if manifest_path.exists():
        out_paper = copy_output(manifest_path, paper_dir, "reproducibility/run_manifest.json")
        out_appendix = copy_output(manifest_path, appendix_dir, "reproducibility/run_manifest.json")
        if out_paper:
            copied_paper.append("reproducibility/run_manifest.json")
        if out_appendix:
            copied_appendix.append("reproducibility/run_manifest.json")

    paper_readme = [
        "# ITC Main Paper Bundle",
        "",
        "This folder collects the portable result artifacts intended for the main ITC paper.",
        "",
        "Suggested main-paper content:",
        "- System framing and tier-aware methodology in the paper body.",
        "- Core performance tables from `analysis/` and `full/`.",
        "- Sequential decision support from `full/sequential_metrics.csv`.",
        "- Mechanism-level diagnosis from `full/stressor_diagnosis_metrics.csv` and the diagnosis figures.",
        "- Reproducibility hash in `reproducibility/run_manifest.json`.",
        "",
        "Primary files copied into this bundle:",
    ]
    paper_readme.extend([f"- `{path}`" for path in copied_paper])
    (paper_dir / "README.md").write_text("\n".join(paper_readme) + "\n", encoding="utf-8")

    appendix_readme = [
        "# ITC AI Appendix Bundle",
        "",
        "ITC allows an AI-focused appendix of up to six pages in addition to the main paper.",
        "This folder collects the portable supporting artifacts that fit that appendix role.",
        "",
        "Recommended appendix sections:",
        "1. Strict workload-holdout validation from `holdout/`.",
        "2. Sequential false-alarm and time-to-detect detail from `full/sequential_metrics.csv`.",
        "3. Diagnosis detail from `full/case_diagnosis_summary.csv`, `full/stressor_confusion_matrix.csv`, and feature-space diagnostics.",
        "4. Tier and mechanism contribution analysis from `full/stressor_tier_contributions.csv` and `full/mechanism_group_summary.csv`.",
        "5. Optional hyperparameter sensitivity from `tuning/` if generated.",
        "6. Data quality, feature inventory, and reproducibility files.",
        "",
        "Primary files copied into this bundle:",
    ]
    appendix_readme.extend([f"- `{path}`" for path in copied_appendix])
    (appendix_dir / "README.md").write_text("\n".join(appendix_readme) + "\n", encoding="utf-8")

    return {
        "results_itc_paper": str(paper_dir),
        "results_itc_appendix": str(appendix_dir),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Run the DICE results pipeline from the terminal.")
    ap.add_argument("--root", type=Path, default=DEFAULT_DATASET_ROOT, help="Dataset root to analyze.")
    ap.add_argument("--source_hz", type=int, default=5)
    ap.add_argument("--fit_ratio", type=float, default=0.6)
    ap.add_argument("--block_B", type=int, default=60)
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--persist_k", type=int, default=3)
    ap.add_argument("--gain", type=float, default=0.35)
    ap.add_argument("--ridge_lambda", type=float, default=1e-3)
    ap.add_argument("--skip_analysis", action="store_true", help="Do not run generate_results_analysis.py.")
    ap.add_argument("--skip_full", action="store_true", help="Do not run the global full DICE pipeline.")
    ap.add_argument("--run_holdout", action="store_true", help="Also run workload-holdout evaluation.")
    ap.add_argument("--run_tuning", action="store_true", help="Also run the compact tuning sweep.")
    ap.add_argument(
        "--package_itc",
        action="store_true",
        help="Generate main-paper and AI-appendix result bundles; implies holdout but not tuning.",
    )
    args = ap.parse_args()

    root = args.root.expanduser().resolve()
    ensure_dataset_root(root)
    env = deterministic_env()

    if args.package_itc:
        args.skip_analysis = False
        args.skip_full = False
        args.run_holdout = True

    outputs: Dict[str, str] = {}
    if not args.skip_analysis:
        outputs["results_analysis"] = str(run_analysis(root=root, env=env, source_hz=args.source_hz))
    if not args.skip_full:
        outputs["results_dice_full"] = str(
            run_full(
                root=root,
                env=env,
                protocol="global",
                source_hz=args.source_hz,
                fit_ratio=args.fit_ratio,
                block_B=args.block_B,
                alpha=args.alpha,
                persist_k=args.persist_k,
                gain=args.gain,
                ridge_lambda=args.ridge_lambda,
            )
        )
    if args.run_holdout:
        outputs["results_dice_full_holdout"] = str(
            run_full(
                root=root,
                env=env,
                protocol="workload_holdout",
                source_hz=args.source_hz,
                fit_ratio=args.fit_ratio,
                block_B=args.block_B,
                alpha=args.alpha,
                persist_k=args.persist_k,
                gain=args.gain,
                ridge_lambda=args.ridge_lambda,
            )
        )
    if args.run_tuning:
        outputs["results_dice_tuning"] = str(
            run_tuning(
                root=root,
                env=env,
                source_hz=args.source_hz,
                fit_ratio=args.fit_ratio,
                ridge_lambda=args.ridge_lambda,
            )
        )

    manifest_dir = root / "results_portable"
    write_manifest(manifest_dir=manifest_dir, root=root, env=env, args=args, outputs=outputs)
    if args.package_itc:
        outputs.update(package_itc_submission(root=root, outputs=outputs))
        write_manifest(manifest_dir=manifest_dir, root=root, env=env, args=args, outputs=outputs)
    print(f"[OK] wrote reproducibility manifest to: {manifest_dir / 'run_manifest.json'}")
    for name, path in outputs.items():
        print(f"[OK] {name}: {path}")


if __name__ == "__main__":
    main()
