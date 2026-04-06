# DICE Full Retrain Results

## Setup
- Protocol: global, benign-only fit/calibration, block_B=60, alpha=0.1, persist_k=5, gain=0.35

## Overall
```text
           config  n_cases  n_features  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
            tier0       24          46   0.8000 0.931899         1.0        1.0           0.25           0.40              0.005518              0.011960                      0.0                 0.006561
      tier0_tier1       24          64   0.8125 0.953228         1.0        1.0           0.25           0.75              0.007632              0.025279                      0.0                 0.012091
tier0_tier1_tier2       24          75   0.9625 0.992487         1.0        1.0           0.25           0.95              0.002745              0.007758                      0.0                 0.004477
```

## Final Config Stressors
```text
stressor  roc_auc  pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
  ATOMIC   0.9375    0.95         1.0        1.0          0.002745          0.007338                  0.0             0.003616       2.673188      0.004594       3616.521699         0.003616
  BRANCH   1.0000    1.00         1.0        1.0          0.002745          0.008554                  0.0             0.006106       3.115745      0.005809       6107.151211         0.006106
   CACHE   0.9375    0.95         1.0        1.0          0.002745          0.009510                  0.0             0.006258       3.464252      0.006766       6258.861362         0.006258
   MEMBW   1.0000    1.00         1.0        1.0          0.002745          0.008411                  0.0             0.005014       3.063753      0.005666       5015.121731         0.005014
     TLB   0.9375    0.95         1.0        1.0          0.002745          0.006549                  0.0             0.004389       2.385593      0.003804       4390.351793         0.004389
```

## Paper-style Aggregates (Final Config)
- Base score mean stressor AUC-PR (all five): **0.9700**
- Base score mean stressor ROC-AUC (all five): **0.9625**
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
            tier0       20       0.3      0.45           0.3  0.246234               0.027015                 0.019692
      tier0_tier1       20       0.2      0.55           0.2  0.190000               0.017925                 0.015908
tier0_tier1_tier2       20       0.2      0.25           0.2  0.190476               0.016374                 0.014851
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode
  ATOMIC     0.723023         0.191438     0.085539              tier0
  BRANCH     0.768118         0.142386     0.089496              tier0
   CACHE     0.610494         0.150398     0.239108              tier0
   MEMBW     0.763509         0.164771     0.071721              tier0
     TLB     0.716579         0.193724     0.089697              tier0
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share
  ATOMIC               memory_io       0.242173         0.301407             0.071890                 0.234369                 0.150161
  BRANCH               memory_io       0.196092         0.355768             0.048742                 0.252996                 0.146401
   CACHE               memory_io       0.368998         0.309717             0.047776                 0.182750                 0.090759
   MEMBW               memory_io       0.211481         0.344232             0.065318                 0.227248                 0.151721
     TLB               memory_io       0.229205         0.320330             0.074520                 0.233959                 0.141985
```

## Sequential Decisioning
```text
           config  benign_run_alert_rate  benign_run_keep_rate  benign_persist_alerts_per_hour  benign_block_alerts_per_hour  anomaly_detect_rate  median_time_to_detect_s  p90_time_to_detect_s  detect_within_120s  detect_within_300s  detect_within_600s
            tier0                   0.25                  0.75                      149.361702                    153.191489                 0.40                     65.5                 672.6                0.25                0.25                0.30
      tier0_tier1                   0.25                  0.75                      138.829787                    142.659574                 0.75                     64.0                 757.2                0.50                0.55                0.55
tier0_tier1_tier2                   0.25                  0.75                      135.000000                    139.787234                 0.95                     64.0                 406.4                0.75                0.80                0.90
```

## Files
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B60_a0.1_k5/overall_metrics.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B60_a0.1_k5/case_block_traces.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B60_a0.1_k5/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B60_a0.1_k5/sequential_metrics.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B60_a0.1_k5/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B60_a0.1_k5/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B60_a0.1_k5/mechanism_group_summary.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B60_a0.1_k5/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B60_a0.1_k5/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B60_a0.1_k5/overall_metrics.tex`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B60_a0.1_k5/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B60_a0.1_k5/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B60_a0.1_k5/sequential_metrics.tex`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B60_a0.1_k5/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B60_a0.1_k5/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B60_a0.1_k5/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B60_a0.1_k5/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B60_a0.1_k5/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B60_a0.1_k5/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B60_a0.1_k5/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B60_a0.1_k5/figures/fig_detection_latency.png`
