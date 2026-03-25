# DICE Full Retrain Results

## Setup
- Protocol: global, benign-only fit/calibration, block_B=60, alpha=0.05, persist_k=3, gain=0.25

## Overall
```text
           config  n_cases  n_features  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
            tier0       24          46   0.8000 0.931899         1.0        1.0           0.25           0.30              0.007173              0.015654                      0.0                 0.008507
      tier0_tier1       24          64   0.8125 0.953228         1.0        1.0           0.25           0.55              0.009965              0.032138                      0.0                 0.015404
tier0_tier1_tier2       24          75   0.9750 0.995119         1.0        1.0           0.25           0.95              0.002915              0.008199                      0.0                 0.004739
```

## Final Config Stressors
```text
stressor  roc_auc  pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
  ATOMIC   0.9375    0.95         1.0        1.0          0.002915          0.007701                  0.0             0.004182       2.641065      0.004786       4182.570521         0.004182
  BRANCH   1.0000    1.00         1.0        1.0          0.002915          0.008590                  0.0             0.006194       2.945804      0.005675       6195.036303         0.006194
   CACHE   0.9375    0.95         1.0        1.0          0.002915          0.010003                  0.0             0.006697       3.430465      0.007088       6698.240269         0.006697
   MEMBW   1.0000    1.00         1.0        1.0          0.002915          0.009001                  0.0             0.005297       3.086872      0.006086       5297.699873         0.005297
     TLB   1.0000    1.00         1.0        1.0          0.002915          0.006641                  0.0             0.004552       2.277434      0.003725       4553.076502         0.004552
```

## Paper-style Aggregates (Final Config)
- Base score mean stressor AUC-PR (all five): **0.9800**
- Base score mean stressor ROC-AUC (all five): **0.9750**
- WC score mean stressor AUC-PR (all five): **1.0000**
- WC score mean stressor ROC-AUC (all five): **1.0000**
- Base score mean stressor AUC-PR (excluding BRANCH/TLB): **0.9667**
- Base score mean stressor ROC-AUC (excluding BRANCH/TLB): **0.9583**
- WC score mean stressor AUC-PR (excluding BRANCH/TLB): **1.0000**
- WC score mean stressor ROC-AUC (excluding BRANCH/TLB): **1.0000**

## Diagnosis
- Primary diagnosis uses workload-held, L1-normalized mechanism-group centroids over DICE residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second
            tier0       20      0.35      0.55          0.35  0.303810               0.026041                 0.018025
      tier0_tier1       20      0.15      0.35          0.15  0.134444               0.017810                 0.016449
tier0_tier1_tier2       20      0.20      0.30          0.20  0.194872               0.015090                 0.011815
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode
  ATOMIC     0.714586         0.191286     0.094128              tier0
  BRANCH     0.761113         0.143475     0.095412              tier0
   CACHE     0.591081         0.149188     0.259731              tier0
   MEMBW     0.758414         0.162174     0.079412              tier0
     TLB     0.706509         0.194907     0.098584              tier0
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share
  ATOMIC               memory_io       0.249458         0.296646             0.074068                 0.228291                 0.151537
  BRANCH               memory_io       0.199504         0.352749             0.049778                 0.249926                 0.148043
   CACHE               memory_io       0.386691         0.299307             0.047705                 0.176323                 0.089974
   MEMBW               memory_io       0.217051         0.339395             0.064473                 0.224511                 0.154570
     TLB               memory_io       0.236898         0.314887             0.075104                 0.229159                 0.143953
```

## Sequential Decisioning
```text
           config  benign_run_alert_rate  benign_run_keep_rate  benign_persist_alerts_per_hour  benign_block_alerts_per_hour  anomaly_detect_rate  median_time_to_detect_s  p90_time_to_detect_s  detect_within_120s  detect_within_300s  detect_within_600s
            tier0                   0.25                  0.75                       67.978723                     69.893617                 0.30                     75.0                 723.5                0.20                0.20                 0.2
      tier0_tier1                   0.25                  0.75                       63.191489                     65.106383                 0.55                     62.0                 835.0                0.35                0.35                 0.4
tier0_tier1_tier2                   0.25                  0.75                       62.234043                     64.148936                 0.95                     62.0                 795.2                0.60                0.65                 0.7
```

## Files
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/figures/fig_detection_latency.png`
