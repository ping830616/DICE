from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score

CFG_LABEL = {
    "tier0": "Tier-0",
    "tier0_tier1": "Tier-0/1",
    "tier0_tier1_tier2": "Tier-0/1/2",
}


def _cfg_labels(values: pd.Series) -> list[str]:
    return [CFG_LABEL.get(str(v), str(v)) for v in values]


def render_tier_correlation_dashboard(
    out_full: Path,
    paper_full: Path,
    paper_fig: Path,
) -> tuple[pd.DataFrame, pd.DataFrame, Path]:
    tier_case = pd.read_csv(out_full / "case_diagnosis_summary.csv")
    tier_final = tier_case[tier_case["config"] == "tier0_tier1_tier2"].copy()
    tier_cols = ["tier0_share", "tier1_alt_share", "tier2_share"]

    tier_corr = tier_final[tier_cols].corr().round(4)
    tier_corr.to_csv(paper_full / "tier_share_correlation.csv")

    stressor_tier = tier_final.groupby("stressor", sort=False)[tier_cols].mean().reset_index()
    stressor_tier.to_csv(paper_full / "stressor_tier_share_summary.csv", index=False)

    tier_final["ternary_x"] = tier_final["tier1_alt_share"] + 0.5 * tier_final["tier2_share"]
    tier_final["ternary_y"] = (np.sqrt(3.0) / 2.0) * tier_final["tier2_share"]

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    im = axes[0].imshow(tier_corr.values, cmap="coolwarm", vmin=-1.0, vmax=1.0)
    axes[0].set_xticks(range(3), ["Tier-0", "Tier-1", "Tier-2"], rotation=30, ha="right")
    axes[0].set_yticks(range(3), ["Tier-0", "Tier-1", "Tier-2"])
    axes[0].set_title("Tier-share correlation")
    for i in range(3):
        for j in range(3):
            axes[0].text(j, i, f"{tier_corr.iloc[i, j]:.2f}", ha="center", va="center", color="black")
    fig.colorbar(im, ax=axes[0], fraction=0.046, pad=0.04)

    x = np.arange(len(stressor_tier))
    axes[1].bar(x, stressor_tier["tier0_share"], label="Tier-0")
    axes[1].bar(x, stressor_tier["tier1_alt_share"], bottom=stressor_tier["tier0_share"], label="Tier-1")
    axes[1].bar(
        x,
        stressor_tier["tier2_share"],
        bottom=stressor_tier["tier0_share"] + stressor_tier["tier1_alt_share"],
        label="Tier-2",
    )
    axes[1].set_xticks(x, stressor_tier["stressor"], rotation=30, ha="right")
    axes[1].set_ylim(0.0, 1.0)
    axes[1].set_title("Mean tier evidence by stressor")
    axes[1].legend(loc="upper right")

    triangle = np.array(
        [
            [0.0, 0.0],
            [1.0, 0.0],
            [0.5, np.sqrt(3.0) / 2.0],
            [0.0, 0.0],
        ]
    )
    axes[2].plot(triangle[:, 0], triangle[:, 1], color="black")
    for stressor, d in tier_final.groupby("stressor", sort=False):
        axes[2].scatter(d["ternary_x"], d["ternary_y"], s=36, alpha=0.8, label=stressor)
    axes[2].text(-0.04, -0.03, "Tier-0")
    axes[2].text(1.01, -0.03, "Tier-1")
    axes[2].text(0.46, np.sqrt(3.0) / 2.0 + 0.03, "Tier-2")
    axes[2].set_title("Per-case tier composition")
    axes[2].set_xticks([])
    axes[2].set_yticks([])
    axes[2].legend(loc="upper right", fontsize=7)

    fig.tight_layout()
    png = paper_fig / "fig_tier_correlation_dashboard.png"
    fig.savefig(png, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return tier_corr, stressor_tier, png


def render_bootstrap_confidence(
    case_pred: pd.DataFrame,
    paper_full: Path,
    paper_fig: Path,
    samples: int = 1000,
    seed: int = 0,
) -> tuple[pd.DataFrame, Path]:
    rng = np.random.default_rng(seed)
    rows: list[dict[str, float | str]] = []

    for cfg, d in case_pred.groupby("config", sort=False):
        stats: list[dict[str, float]] = []
        for _ in range(samples):
            sample = d.sample(n=len(d), replace=True, random_state=int(rng.integers(1 << 32)))
            if sample["label"].nunique() < 2:
                continue
            benign = sample[sample["label"] == 0]
            anomaly = sample[sample["label"] == 1]
            stats.append(
                {
                    "roc_auc_wc": roc_auc_score(sample["label"], sample["run_score_wc"]),
                    "pr_auc_wc": average_precision_score(sample["label"], sample["run_score_wc"]),
                    "benign_run_false_alarm_rate": benign["run_alert"].mean(),
                    "anomaly_run_detection_rate": anomaly["run_alert"].mean(),
                    "median_time_to_detect_s": anomaly.loc[
                        anomaly["run_alert"] == 1, "time_to_detect_s"
                    ].median(),
                }
            )

        boot = pd.DataFrame(stats)
        rows.append(
            {
                "config": cfg,
                "roc_auc_wc_lo": boot["roc_auc_wc"].quantile(0.025),
                "roc_auc_wc_hi": boot["roc_auc_wc"].quantile(0.975),
                "pr_auc_wc_lo": boot["pr_auc_wc"].quantile(0.025),
                "pr_auc_wc_hi": boot["pr_auc_wc"].quantile(0.975),
                "fpr_lo": boot["benign_run_false_alarm_rate"].quantile(0.025),
                "fpr_hi": boot["benign_run_false_alarm_rate"].quantile(0.975),
                "detect_lo": boot["anomaly_run_detection_rate"].quantile(0.025),
                "detect_hi": boot["anomaly_run_detection_rate"].quantile(0.975),
                "ttd_lo": boot["median_time_to_detect_s"].quantile(0.025),
                "ttd_hi": boot["median_time_to_detect_s"].quantile(0.975),
            }
        )

    out = pd.DataFrame(rows)
    out.to_csv(paper_full / "bootstrap_confidence_intervals.csv", index=False)

    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    x = np.arange(len(out))

    pr_mid = (out["pr_auc_wc_lo"] + out["pr_auc_wc_hi"]) / 2.0
    pr_err = np.vstack([pr_mid - out["pr_auc_wc_lo"], out["pr_auc_wc_hi"] - pr_mid])
    axes[0].errorbar(x, pr_mid, yerr=pr_err, fmt="o", capsize=4)
    axes[0].set_xticks(x, out["config"], rotation=30, ha="right")
    axes[0].set_title("Bootstrap AUC-PR CI")

    fpr_mid = (out["fpr_lo"] + out["fpr_hi"]) / 2.0
    fpr_err = np.vstack([fpr_mid - out["fpr_lo"], out["fpr_hi"] - fpr_mid])
    axes[1].errorbar(x, fpr_mid, yerr=fpr_err, fmt="o", capsize=4)
    axes[1].set_xticks(x, out["config"], rotation=30, ha="right")
    axes[1].set_title("Bootstrap benign-FPR CI")

    ttd_mid = (out["ttd_lo"] + out["ttd_hi"]) / 2.0
    ttd_err = np.vstack([ttd_mid - out["ttd_lo"], out["ttd_hi"] - ttd_mid])
    axes[2].errorbar(x, ttd_mid, yerr=ttd_err, fmt="o", capsize=4)
    axes[2].set_xticks(x, out["config"], rotation=30, ha="right")
    axes[2].set_title("Bootstrap time-to-detect CI")

    fig.tight_layout()
    png = paper_fig / "fig_bootstrap_confidence_intervals.png"
    fig.savefig(png, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out, png


def export_llm_case_cards(
    out_full: Path,
    appendix_full: Path,
) -> pd.DataFrame:
    case_diag = pd.read_csv(out_full / "case_diagnosis_summary.csv")
    cards = case_diag[case_diag["config"] == "tier0_tier1_tier2"].copy()
    cards = cards[
        [
            "case_id",
            "workload",
            "stressor",
            "dominant_tier",
            "dominant_mechanism",
            "top_feature_1",
            "top_feature_score_1",
            "top_mechanism_1",
            "top_mechanism_score_1",
        ]
    ].copy()
    cards["llm_summary_prompt"] = (
        "Summarize this DICE anomaly case for a reviewer. "
        "Case=" + cards["case_id"]
        + "; workload=" + cards["workload"]
        + "; stressor=" + cards["stressor"]
        + "; dominant tier=" + cards["dominant_tier"]
        + "; dominant mechanism=" + cards["dominant_mechanism"]
        + "; top feature=" + cards["top_feature_1"].astype(str)
        + "; top mechanism=" + cards["top_mechanism_1"].astype(str)
    )
    cards.to_csv(appendix_full / "llm_case_cards.csv", index=False)
    return cards


def render_paper_performance_stack(
    case_pred: pd.DataFrame,
    overall_full: pd.DataFrame,
    sequential: pd.DataFrame,
    reliability: pd.DataFrame,
    paper_full: Path,
    paper_fig: Path,
) -> tuple[pd.DataFrame, Path]:
    summary = (
        overall_full[
            [
                "config",
                "roc_auc",
                "pr_auc",
                "roc_auc_wc",
                "pr_auc_wc",
                "median_nominal_score_wc",
                "median_anomaly_score_wc",
            ]
        ]
        .merge(
            sequential[
                [
                    "config",
                    "anomaly_detect_rate",
                    "median_time_to_detect_s",
                ]
            ],
            on="config",
        )
        .merge(
            reliability[
                [
                    "config",
                    "target_alpha",
                    "benign_block_false_alarm_rate",
                ]
            ],
            on="config",
        )
    )
    summary["config_label"] = _cfg_labels(summary["config"])
    summary["reliability_margin"] = summary["target_alpha"] - summary["benign_block_false_alarm_rate"]
    summary.to_csv(paper_full / "paper_performance_stack_summary.csv", index=False)

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    final = case_pred[case_pred["config"] == "tier0_tier1_tier2"].copy()
    benign = final[final["label"] == 0]["run_score_wc"].to_numpy(dtype=float)
    anomaly = final[final["label"] == 1]["run_score_wc"].to_numpy(dtype=float)
    bp = axes[0, 0].boxplot([benign, anomaly], labels=["Benign", "Anomaly"], patch_artist=True)
    for patch, color in zip(bp["boxes"], ["#2563eb", "#dc2626"]):
        patch.set_facecolor(color)
        patch.set_alpha(0.75)
    axes[0, 0].set_title("A. Final-head score separation")
    axes[0, 0].set_ylabel("Workload-conditioned run score")

    base_color = "#94a3b8"
    wc_color = "#0f766e"
    for _, row in summary.iterrows():
        axes[0, 1].scatter(row["roc_auc"], row["pr_auc"], color=base_color, s=70)
        axes[0, 1].scatter(row["roc_auc_wc"], row["pr_auc_wc"], color=wc_color, s=90)
        axes[0, 1].annotate(
            row["config_label"],
            (row["roc_auc_wc"], row["pr_auc_wc"]),
            textcoords="offset points",
            xytext=(6, 6),
        )
        axes[0, 1].plot([row["roc_auc"], row["roc_auc_wc"]], [row["pr_auc"], row["pr_auc_wc"]], color="#475569")
    axes[0, 1].set_xlabel("Run-level ROC-AUC")
    axes[0, 1].set_ylabel("Run-level Average Precision")
    axes[0, 1].set_title("B. Digital-twin score refinement")

    x = np.arange(len(summary))
    axes[1, 0].bar(x, summary["benign_block_false_alarm_rate"], color="#f59e0b")
    axes[1, 0].axhline(float(summary["target_alpha"].iloc[0]), color="black", linestyle="--", linewidth=1.2)
    axes[1, 0].set_xticks(x, summary["config_label"], rotation=30, ha="right")
    axes[1, 0].set_ylabel("Empirical benign block FAR")
    axes[1, 0].set_title("C. Calibrated reliability")

    bars = axes[1, 1].bar(x, summary["anomaly_detect_rate"], color="#16a34a", label="Detection rate")
    ax2 = axes[1, 1].twinx()
    ax2.plot(x, summary["median_time_to_detect_s"], color="#1d4ed8", marker="o", linewidth=2, label="Median TTD")
    axes[1, 1].set_xticks(x, summary["config_label"], rotation=30, ha="right")
    axes[1, 1].set_ylabel("Run-level detection rate")
    ax2.set_ylabel("Median time-to-detect (s)")
    axes[1, 1].set_title("D. Operational decision performance")
    axes[1, 1].legend([bars], ["Detection rate"], loc="upper left")
    ax2.legend(loc="upper right")

    fig.tight_layout()
    png = paper_fig / "fig_paper_performance_stack.png"
    fig.savefig(png, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return summary, png


def render_explainability_dashboard(
    out_full: Path,
    paper_full: Path,
    paper_fig: Path,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, Path]:
    tier_contrib = pd.read_csv(out_full / "stressor_tier_contributions.csv")
    mechanism = pd.read_csv(out_full / "mechanism_group_summary.csv")
    cm = pd.read_csv(out_full / "stressor_confusion_matrix.csv", index_col=0)

    tier_contrib.to_csv(paper_full / "paper_tier_contribution_summary.csv", index=False)
    mechanism.to_csv(paper_full / "paper_mechanism_summary.csv", index=False)
    cm.to_csv(paper_full / "paper_stressor_confusion_matrix.csv")

    fig, axes = plt.subplots(1, 3, figsize=(17, 5))

    x = np.arange(len(tier_contrib))
    axes[0].bar(x, tier_contrib["tier0_share"], label="Tier-0")
    axes[0].bar(x, tier_contrib["tier1_alt_share"], bottom=tier_contrib["tier0_share"], label="Tier-1")
    axes[0].bar(
        x,
        tier_contrib["tier2_share"],
        bottom=tier_contrib["tier0_share"] + tier_contrib["tier1_alt_share"],
        label="Tier-2",
    )
    axes[0].set_xticks(x, tier_contrib["stressor"], rotation=30, ha="right")
    axes[0].set_ylim(0.0, 1.0)
    axes[0].set_title("A. Tier contribution by stressor")
    axes[0].legend(loc="upper right")

    mech_cols = [
        "compute_share",
        "memory_io_share",
        "thermal_power_share",
        "scheduler_runtime_share",
        "platform_pressure_share",
    ]
    bottom = np.zeros(len(mechanism))
    colors = ["#0f766e", "#1d4ed8", "#dc2626", "#9333ea", "#b45309"]
    for col, color in zip(mech_cols, colors):
        axes[1].bar(np.arange(len(mechanism)), mechanism[col], bottom=bottom, label=col.replace("_share", ""), color=color)
        bottom += mechanism[col].to_numpy(dtype=float)
    axes[1].set_xticks(np.arange(len(mechanism)), mechanism["stressor"], rotation=30, ha="right")
    axes[1].set_ylim(0.0, 1.0)
    axes[1].set_title("B. Mechanism evidence by stressor")
    axes[1].legend(loc="upper right", fontsize=7)

    im = axes[2].imshow(cm.values, cmap="Blues")
    axes[2].set_xticks(range(len(cm.columns)), list(cm.columns), rotation=30, ha="right")
    axes[2].set_yticks(range(len(cm.index)), list(cm.index))
    axes[2].set_title("C. Stressor diagnosis confusion")
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            axes[2].text(j, i, str(int(cm.iloc[i, j])), ha="center", va="center", color="black")
    fig.colorbar(im, ax=axes[2], fraction=0.046, pad=0.04)

    fig.tight_layout()
    png = paper_fig / "fig_paper_explainability_dashboard.png"
    fig.savefig(png, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return tier_contrib, mechanism, cm, png


def render_portability_dashboard(
    frontier: pd.DataFrame,
    holdout: pd.DataFrame,
    bootstrap_ci: pd.DataFrame,
    paper_full: Path,
    paper_fig: Path,
) -> tuple[pd.DataFrame, Path]:
    view = frontier.copy()
    view["config_label"] = _cfg_labels(view["config"])
    holdout_view = holdout.copy()
    holdout_view["config_label"] = _cfg_labels(holdout_view["config"])
    boot_view = bootstrap_ci.copy()
    boot_view["config_label"] = _cfg_labels(boot_view["config"])

    portability_summary = view[
        [
            "config",
            "config_label",
            "n_features",
            "portable_pr_auc",
            "holdout_worst_pr_auc",
            "reliability_margin",
            "joint_detection_diagnosis",
        ]
    ].copy()
    portability_summary.to_csv(paper_full / "paper_portability_summary.csv", index=False)

    fig, axes = plt.subplots(1, 3, figsize=(17, 5))

    scatter = axes[0].scatter(
        view["n_features"],
        view["portable_pr_auc"],
        s=view["joint_detection_diagnosis"].fillna(0.0) * 1800 + 140,
        c=view["reliability_margin"],
        cmap="viridis",
        edgecolor="black",
        linewidth=0.8,
    )
    for _, row in view.iterrows():
        axes[0].annotate(row["config_label"], (row["n_features"], row["portable_pr_auc"]), textcoords="offset points", xytext=(6, 6))
    axes[0].set_xlabel("Median active features")
    axes[0].set_ylabel("Portable AUC-PR")
    axes[0].set_title("A. Observability-portability frontier")
    fig.colorbar(scatter, ax=axes[0], fraction=0.046, pad=0.04)

    x = np.arange(len(holdout_view))
    width = 0.35
    axes[1].bar(x - width / 2.0, holdout_view["mean_pr_auc"], width=width, label="Mean holdout PR")
    axes[1].bar(x + width / 2.0, holdout_view["worst_pr_auc"], width=width, label="Worst holdout PR")
    axes[1].set_xticks(x, holdout_view["config_label"], rotation=30, ha="right")
    axes[1].set_ylim(0.0, 1.05)
    axes[1].set_title("B. Holdout portability")
    axes[1].legend(loc="upper right")

    x = np.arange(len(boot_view))
    pr_mid = (boot_view["pr_auc_wc_lo"] + boot_view["pr_auc_wc_hi"]) / 2.0
    pr_err = np.vstack([pr_mid - boot_view["pr_auc_wc_lo"], boot_view["pr_auc_wc_hi"] - pr_mid])
    axes[2].errorbar(x, pr_mid, yerr=pr_err, fmt="o", capsize=4, color="#1d4ed8", label="AP CI")
    det_mid = (boot_view["detect_lo"] + boot_view["detect_hi"]) / 2.0
    det_err = np.vstack([det_mid - boot_view["detect_lo"], boot_view["detect_hi"] - det_mid])
    axes[2].errorbar(x, det_mid, yerr=det_err, fmt="o", capsize=4, color="#16a34a", label="Detect-rate CI")
    axes[2].set_xticks(x, boot_view["config_label"], rotation=30, ha="right")
    axes[2].set_ylim(0.0, 1.05)
    axes[2].set_title("C. Bootstrap uncertainty")
    axes[2].legend(loc="lower right")

    fig.tight_layout()
    png = paper_fig / "fig_paper_portability_dashboard.png"
    fig.savefig(png, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return portability_summary, png
