from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score


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
