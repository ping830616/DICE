# DICE Results/Analysis Auto-Summary

## Key Findings
- Best run-level AUC-PR tier: **Tier-0** (AUC-PR=1.0000, ROC-AUC=1.0000).
- Strongest stressors (mean AUC-PR across tiers): **ATOMIC, BRANCH, CACHE**.
- Hardest stressors (mean AUC-PR across tiers): **MEMBW, ATOMIC**.

## Suggested Results Narrative
Across the 24-run Apple dataset, AF-index separation is consistently visible between nominal and anomalous runs in all telemetry tiers. Tier-aware scoring indicates that anomaly/nominal score ratios remain above 1.0 in every tier, confirming stable separability under the fixed collection protocol. Per-stressor analysis shows stronger separation for ATOMIC, CACHE, and MEMBW, while BRANCH and TLB remain comparatively harder due to weaker host-visible signatures. These observations match the expected mechanism-level difficulty ordering in software-driven stressors.

## Generated Figures
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_analysis/figures/fig_af_timeseries_tier0.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_analysis/figures/fig_af_timeseries_tier1_alt.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_analysis/figures/fig_af_timeseries_tier2.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_analysis/figures/fig_heatmap_roc_auc.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_analysis/figures/fig_heatmap_pr_auc.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_analysis/figures/fig_run_score_distributions.png`

## Generated Tables
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_analysis/table_overall_metrics.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_analysis/table_stressor_metrics.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_analysis/table_workload_summary.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_analysis/table_feature_inventory.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_analysis/table_overall_metrics.tex`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_analysis/table_stressor_metrics.tex`
