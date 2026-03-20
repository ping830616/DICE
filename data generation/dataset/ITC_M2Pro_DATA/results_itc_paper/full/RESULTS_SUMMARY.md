# DICE Full Retrain Results

## Setup
- Feature profile: mixed ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_core_5hz.csv', 'tier2': 'tier2_core_5hz.csv'})
- Protocol: global, benign-only fit/calibration, block_B=60, alpha=0.05, persist_k=3, gain=0.35

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
          mixed             tier0       24          46          0.824228   0.8000 0.931899         1.0        1.0           0.25           0.30              0.005518              0.011960                      0.0                 0.006561
          mixed       tier0_tier1       24          57          1.035311   0.8250 0.951460         1.0        1.0           0.25           0.45              0.000045              0.000110                      0.0                 0.000056
          mixed tier0_tier1_tier2       24          64          1.300356   0.8375 0.953625         1.0        1.0           0.25           0.45              0.000048              0.000119                      0.0                 0.000062
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
          mixed   ATOMIC   0.8125 0.804167         1.0        1.0          0.000048          0.000099                  0.0             0.000057       2.051449      0.000051         58.378895         0.000057
          mixed   BRANCH   0.9375 0.950000         1.0        1.0          0.000048          0.000186                  0.0             0.000125       3.845005      0.000138        125.990235         0.000125
          mixed    CACHE   0.8125 0.804167         1.0        1.0          0.000048          0.000100                  0.0             0.000061       2.081700      0.000053         61.971078         0.000061
          mixed    MEMBW   0.8750 0.887500         1.0        1.0          0.000048          0.000161                  0.0             0.000093       3.325768      0.000113         93.724244         0.000093
          mixed      TLB   0.7500 0.679167         1.0        1.0          0.000048          0.000113                  0.0             0.000054       2.347351      0.000066         54.690889         0.000054
```

## Paper-style Aggregates (Final Config)
- Base score mean stressor AUC-PR (all five): **0.8250**
- Base score mean stressor ROC-AUC (all five): **0.8375**
- WC score mean stressor AUC-PR (all five): **1.0000**
- WC score mean stressor ROC-AUC (all five): **1.0000**
- Base score mean stressor AUC-PR (excluding BRANCH/TLB): **0.8319**
- Base score mean stressor ROC-AUC (excluding BRANCH/TLB): **0.8333**
- WC score mean stressor AUC-PR (excluding BRANCH/TLB): **1.0000**
- WC score mean stressor ROC-AUC (excluding BRANCH/TLB): **1.0000**

## Diagnosis
- Primary diagnosis uses mechanism-group centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  macro_f1  mean_margin_to_second feature_profile
            tier0       20       0.3      0.55  0.218182               0.000511           mixed
      tier0_tier1       20       0.2      0.45  0.180000               0.000003           mixed
tier0_tier1_tier2       20       0.2      0.50  0.174315               0.000004           mixed
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.808226         0.089461     0.102314              tier0           mixed
  BRANCH     0.854443         0.055837     0.089720              tier0           mixed
   CACHE     0.607782         0.319386     0.072832              tier0           mixed
   MEMBW     0.860856         0.062421     0.076723              tier0           mixed
     TLB     0.805354         0.092454     0.102192              tier0           mixed
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC               memory_io       0.184195         0.414212             0.052629                 0.246516                 0.102448           mixed
  BRANCH               memory_io       0.156923         0.443255             0.030963                 0.229030                 0.139830           mixed
   CACHE               memory_io       0.393999         0.295624             0.044716                 0.178524                 0.087137           mixed
   MEMBW               memory_io       0.150287         0.463995             0.035492                 0.209598                 0.140627           mixed
     TLB               memory_io       0.204439         0.401318             0.049066                 0.235087                 0.110091           mixed
```

## Sequential Decisioning
```text
           config  benign_run_alert_rate  benign_persist_alerts_per_hour  benign_block_alerts_per_hour  anomaly_detect_rate  median_time_to_detect_s  p90_time_to_detect_s  detect_within_120s  detect_within_300s  detect_within_600s feature_profile
            tier0                   0.25                       70.851064                     72.765957                 0.30                     74.5                 715.5                 0.2                 0.2                0.20           mixed
      tier0_tier1                   0.25                       69.893617                     71.808511                 0.45                     62.0                 710.8                 0.3                 0.3                0.35           mixed
tier0_tier1_tier2                   0.25                       67.978723                     69.893617                 0.45                     62.0                 586.4                 0.3                 0.3                0.40           mixed
```

## Files
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/overall_metrics.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/config_runtime_summary.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/run_context.json`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/sequential_metrics.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/mechanism_group_summary.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/overall_metrics.tex`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/sequential_metrics.tex`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/figures/fig_detection_latency.png`
