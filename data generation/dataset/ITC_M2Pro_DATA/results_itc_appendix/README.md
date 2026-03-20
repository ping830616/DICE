# ITC AI Appendix Bundle

ITC allows an AI-focused appendix of up to six pages in addition to the main paper.
This folder collects the portable supporting artifacts that fit that appendix role.

Recommended appendix sections:
1. Strict workload-holdout validation from `holdout/`.
2. Sequential false-alarm and time-to-detect detail from `full/sequential_metrics.csv`.
3. Diagnosis detail from `full/case_diagnosis_summary.csv`, `full/stressor_confusion_matrix.csv`, and feature-space diagnostics.
4. Tier and mechanism contribution analysis from `full/stressor_tier_contributions.csv` and `full/mechanism_group_summary.csv`.
5. Optional hyperparameter sensitivity from `tuning/` if generated.
6. Data quality, feature inventory, and reproducibility files.

Primary files copied into this bundle:
- `analysis/table_feature_inventory.csv`
- `analysis/table_case_quality.csv`
- `analysis/table_run_scores.csv`
- `analysis/fig_heatmap_roc_auc.png`
- `analysis/fig_af_timeseries_tier0.png`
- `analysis/fig_af_timeseries_tier1_alt.png`
- `analysis/fig_af_timeseries_tier2.png`
- `full/case_predictions.csv`
- `full/case_diagnosis_summary.csv`
- `full/stressor_diagnosis_predictions.csv`
- `full/stressor_confusion_matrix.csv`
- `full/stressor_tier_contributions.csv`
- `full/mechanism_group_summary.csv`
- `full/sequential_metrics.csv`
- `full/stressor_feature_diagnosis_predictions.csv`
- `full/stressor_feature_diagnosis_metrics.csv`
- `full/stressor_feature_confusion_matrix.csv`
- `full/overall_metrics.csv`
- `full/stressor_metrics_final_config.csv`
- `full/stressor_diagnosis_metrics.csv`
- `holdout/fold_metrics.csv`
- `holdout/case_predictions.csv`
- `holdout/overall_metrics.csv`
- `holdout/holdout_robustness_summary.csv`
- `holdout/RESULTS_SUMMARY.md`
- `holdout/fig_roc_pr_by_config_wc.png`
- `reproducibility/run_manifest.json`
