# DICE Full Retrain Results

## Setup
- Feature profile: mixed ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_core_5hz.csv', 'tier2': 'tier2_core_5hz.csv'})
- Protocol: workload_holdout, benign-only fit/calibration, block_B=60, alpha=0.05, persist_k=3, gain=0.35

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
          mixed             tier0       24          46          1.023773    0.350 0.767142         1.0        1.0            1.0            0.9              0.076633              0.051016                      0.0                 0.014080
          mixed       tier0_tier1       24          57          1.225900    0.375 0.800137         1.0        1.0            1.0            0.9              0.000508              0.000374                      0.0                 0.000136
          mixed tier0_tier1_tier2       24          64          1.248791    0.350 0.802612         1.0        1.0            1.0            0.9              0.000692              0.000365                      0.0                 0.000168
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
          mixed   ATOMIC   0.1250 0.394643         1.0        1.0          0.000692          0.000215                  0.0             0.000533       0.311828     -0.000477        534.051752         0.000533
          mixed   BRANCH   0.3125 0.451190         1.0        1.0          0.000692          0.000373                  0.0             0.000206       0.539605     -0.000319        206.512614         0.000206
          mixed    CACHE   0.7500 0.830357         1.0        1.0          0.000692          2.123404                  0.0             0.105620    3065.692203      2.122713     105620.525343         0.105620
          mixed    MEMBW   0.2500 0.433333         1.0        1.0          0.000692          0.000357                  0.0             0.000477       0.517388     -0.000334        477.739278         0.000477
          mixed      TLB   0.3125 0.451190         1.0        1.0          0.000692          0.000349                  0.0             0.000107       0.505830     -0.000342        107.693073         0.000107
```

## Paper-style Aggregates (Final Config)
- Base score mean stressor AUC-PR (all five): **0.5121**
- Base score mean stressor ROC-AUC (all five): **0.3500**
- WC score mean stressor AUC-PR (all five): **1.0000**
- WC score mean stressor ROC-AUC (all five): **1.0000**
- Base score mean stressor AUC-PR (excluding BRANCH/TLB): **0.5528**
- Base score mean stressor ROC-AUC (excluding BRANCH/TLB): **0.3750**
- WC score mean stressor AUC-PR (excluding BRANCH/TLB): **1.0000**
- WC score mean stressor ROC-AUC (excluding BRANCH/TLB): **1.0000**

## Diagnosis
- Primary diagnosis uses mechanism-group centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  macro_f1  mean_margin_to_second feature_profile
            tier0       20      0.25      0.35  0.205714               0.001629           mixed
      tier0_tier1       20      0.25      0.50  0.175000               0.000012           mixed
tier0_tier1_tier2       20      0.25      0.50  0.190476               0.000014           mixed
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.846634         0.051085     0.102281              tier0           mixed
  BRANCH     0.888947         0.051871     0.059182              tier0           mixed
   CACHE     0.441247         0.291025     0.267727              tier0           mixed
   MEMBW     0.826098         0.115767     0.058135              tier0           mixed
     TLB     0.893228         0.065017     0.041756              tier0           mixed
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC               memory_io       0.146658         0.479563             0.026562                 0.241468                 0.105749           mixed
  BRANCH               memory_io       0.132264         0.482039             0.024197                 0.242335                 0.119166           mixed
   CACHE               memory_io       0.359472         0.188395             0.020246                 0.376185                 0.055703           mixed
   MEMBW               memory_io       0.136175         0.462861             0.086294                 0.208710                 0.105960           mixed
     TLB               memory_io       0.154640         0.488215             0.031460                 0.236073                 0.089612           mixed
```

## Sequential Decisioning
```text
           config  benign_run_alert_rate  benign_persist_alerts_per_hour  benign_block_alerts_per_hour  anomaly_detect_rate  median_time_to_detect_s  p90_time_to_detect_s  detect_within_120s  detect_within_300s  detect_within_600s feature_profile
            tier0                    1.0                     2852.234043                   2859.893617                  0.9                     62.0                  81.5                 0.8                 0.9                 0.9           mixed
      tier0_tier1                    1.0                     3592.340426                   3600.000000                  0.9                     62.0                  62.0                 0.9                 0.9                 0.9           mixed
tier0_tier1_tier2                    1.0                     3592.340426                   3600.000000                  0.9                     62.0                  62.0                 0.9                 0.9                 0.9           mixed
```

## Holdout Robustness (Workload Drift Proxy)
```text
           config  mean_pr_auc  worst_pr_auc  mean_roc_auc  mean_pr_auc_wc  worst_pr_auc_wc  mean_roc_auc_wc  pooled_pr_auc  pooled_roc_auc  pooled_pr_auc_wc  pooled_roc_auc_wc  mean_fpr  mean_tpr feature_profile
            tier0     0.782500          0.71          0.25             1.0              1.0              1.0       0.767142           0.350               1.0                1.0  0.166667      0.75           mixed
      tier0_tier1     0.824167          0.71          0.35             1.0              1.0              1.0       0.800137           0.375               1.0                1.0  0.166667      0.75           mixed
tier0_tier1_tier2     0.874167          0.81          0.45             1.0              1.0              1.0       0.802612           0.350               1.0                1.0  0.166667      0.75           mixed
```

## Files
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/overall_metrics.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/config_runtime_summary.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/run_context.json`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/sequential_metrics.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/mechanism_group_summary.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/overall_metrics.tex`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/sequential_metrics.tex`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/figures/fig_detection_latency.png`
