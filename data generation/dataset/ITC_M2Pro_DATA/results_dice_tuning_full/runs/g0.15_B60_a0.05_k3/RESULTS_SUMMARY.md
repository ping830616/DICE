# DICE Full Retrain Results

## Setup
- Protocol: global, benign-only fit/calibration, block_B=60, alpha=0.05, persist_k=3, gain=0.15

## Overall
```text
           config  n_cases  n_features  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
            tier0       24          46    0.800 0.931899         1.0        1.0           0.25           0.30              0.010299              0.022580                      0.0                 0.012186
      tier0_tier1       24          64    0.825 0.955040         1.0        1.0           0.25           0.60              0.014716              0.044738                      0.0                 0.021226
tier0_tier1_tier2       24          75    0.975 0.995119         1.0        1.0           0.25           0.95              0.002984              0.008435                      0.0                 0.004672
```

## Final Config Stressors
```text
stressor  roc_auc  pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
  ATOMIC   0.9375    0.95         1.0        1.0          0.002984          0.007824                  0.0             0.004750       2.621902      0.004841       4751.003497         0.004750
  BRANCH   1.0000    1.00         1.0        1.0          0.002984          0.008193                  0.0             0.005968       2.745351      0.005209       5968.938741         0.005968
   CACHE   0.9375    0.95         1.0        1.0          0.002984          0.010088                  0.0             0.006896       3.380611      0.007105       6897.392999         0.006896
   MEMBW   1.0000    1.00         1.0        1.0          0.002984          0.009096                  0.0             0.005540       3.048122      0.006113       5540.846322         0.005540
     TLB   1.0000    1.00         1.0        1.0          0.002984          0.006385                  0.0             0.004491       2.139838      0.003402       4492.364059         0.004491
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
            tier0       20      0.30       0.6          0.30  0.246667               0.021697                 0.011510
      tier0_tier1       20      0.15       0.3          0.15  0.138889               0.017931                 0.015283
tier0_tier1_tier2       20      0.20       0.3          0.20  0.180000               0.013066                 0.013235
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode
  ATOMIC     0.694261         0.188042     0.117697              tier0
  BRANCH     0.747410         0.142250     0.110340              tier0
   CACHE     0.559342         0.143949     0.296709              tier0
   MEMBW     0.744261         0.156257     0.099482              tier0
     TLB     0.685265         0.193566     0.121169              tier0
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share
  ATOMIC               memory_io       0.267022         0.289932             0.075814                 0.214759                 0.152473
  BRANCH               memory_io       0.210805         0.345284             0.050496                 0.242058                 0.151357
   CACHE               memory_io       0.416860         0.280502             0.047627                 0.166090                 0.088921
   MEMBW               memory_io       0.233546         0.327621             0.062115                 0.216044                 0.160674
     TLB               memory_io       0.257214         0.304097             0.075521                 0.217173                 0.145995
```

## Sequential Decisioning
```text
           config  benign_run_alert_rate  benign_run_keep_rate  benign_persist_alerts_per_hour  benign_block_alerts_per_hour  anomaly_detect_rate  median_time_to_detect_s  p90_time_to_detect_s  detect_within_120s  detect_within_300s  detect_within_600s
            tier0                   0.25                  0.75                       65.106383                     67.021277                 0.30                     75.5                 726.5                0.20                 0.2                0.20
      tier0_tier1                   0.25                  0.75                       63.191489                     65.106383                 0.60                     78.0                 813.3                0.40                 0.4                0.45
tier0_tier1_tier2                   0.25                  0.75                       62.234043                     64.148936                 0.95                     62.0                 668.6                0.65                 0.7                0.80
```

## Files
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B60_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B60_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B60_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B60_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B60_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B60_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B60_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B60_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B60_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B60_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B60_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B60_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B60_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B60_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B60_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B60_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B60_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B60_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B60_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B60_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B60_a0.05_k3/figures/fig_detection_latency.png`
