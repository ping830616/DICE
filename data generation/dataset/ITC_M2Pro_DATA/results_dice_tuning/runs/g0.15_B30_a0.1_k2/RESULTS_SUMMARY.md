# DICE Full Retrain Results

## Setup
- Protocol: global, benign-only fit/calibration, block_B=30, alpha=0.1, persist_k=2, gain=0.15

## Overall
```text
           config  n_cases  n_features  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
            tier0       24          46   0.8000 0.931899         1.0        1.0           0.25           0.45              0.011353              0.023357                      0.0                 0.012710
      tier0_tier1       24          57   0.8375 0.957016         1.0        1.0           0.25           0.80              0.000044              0.000113                      0.0                 0.000052
tier0_tier1_tier2       24          64   0.8500 0.962016         1.0        1.0           0.25           0.85              0.000047              0.000120                      0.0                 0.000056
```

## Final Config Stressors
```text
stressor  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
  ATOMIC   0.7500 0.770833         1.0        1.0          0.000047          0.000091                  0.0             0.000041       1.916407      0.000044         41.947972         0.000041
  BRANCH   0.9375 0.950000         1.0        1.0          0.000047          0.000189                  0.0             0.000135       3.977285      0.000142        135.948580         0.000135
   CACHE   0.8125 0.804167         1.0        1.0          0.000047          0.000100                  0.0             0.000056       2.100190      0.000053         57.030674         0.000056
   MEMBW   0.9375 0.950000         1.0        1.0          0.000047          0.000145                  0.0             0.000081       3.057149      0.000098         82.293975         0.000081
     TLB   0.8125 0.804167         1.0        1.0          0.000047          0.000107                  0.0             0.000046       2.259590      0.000060         47.374077         0.000046
```

## Paper-style Aggregates (Final Config)
- Base score mean stressor AUC-PR (all five): **0.8558**
- Base score mean stressor ROC-AUC (all five): **0.8500**
- WC score mean stressor AUC-PR (all five): **1.0000**
- WC score mean stressor ROC-AUC (all five): **1.0000**
- Base score mean stressor AUC-PR (excluding BRANCH/TLB): **0.8417**
- Base score mean stressor ROC-AUC (excluding BRANCH/TLB): **0.8333**
- WC score mean stressor AUC-PR (excluding BRANCH/TLB): **1.0000**
- WC score mean stressor ROC-AUC (excluding BRANCH/TLB): **1.0000**

## Diagnosis
- Primary diagnosis uses workload-held, L1-normalized mechanism-group centroids over DICE residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second
            tier0       20      0.35      0.55          0.35  0.296032               0.023233                 0.012121
      tier0_tier1       20      0.35      0.60          0.35  0.324964               0.027674                 0.022788
tier0_tier1_tier2       20      0.20      0.60          0.20  0.186325               0.020602                 0.017080
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode
  ATOMIC     0.783538         0.110571     0.105891              tier0
  BRANCH     0.842307         0.060327     0.097366              tier0
   CACHE     0.592885         0.328298     0.078817              tier0
   MEMBW     0.849692         0.066260     0.084048              tier0
     TLB     0.780410         0.107274     0.112315              tier0
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share
  ATOMIC               memory_io       0.184536         0.394842             0.070658                 0.239712                 0.110252
  BRANCH               memory_io       0.160318         0.424381             0.035049                 0.227163                 0.153089
   CACHE               memory_io       0.404680         0.274133             0.053131                 0.172144                 0.095911
   MEMBW               memory_io       0.158691         0.441345             0.039693                 0.209385                 0.150886
     TLB               memory_io       0.213046         0.381194             0.061835                 0.228513                 0.115411
```

## Sequential Decisioning
```text
           config  benign_run_alert_rate  benign_run_keep_rate  benign_persist_alerts_per_hour  benign_block_alerts_per_hour  anomaly_detect_rate  median_time_to_detect_s  p90_time_to_detect_s  detect_within_120s  detect_within_300s  detect_within_600s
            tier0                   0.25                  0.75                      140.103093                    141.030928                 0.45                     31.0                 607.0                 0.3                 0.3                 0.4
      tier0_tier1                   0.25                  0.75                      139.175258                    140.103093                 0.80                    236.5                 849.0                 0.4                 0.4                 0.6
tier0_tier1_tier2                   0.25                  0.75                      139.175258                    140.103093                 0.85                     73.0                 702.0                 0.5                 0.5                 0.7
```

## Files
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.1_k2/overall_metrics.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.1_k2/case_block_traces.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.1_k2/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.1_k2/sequential_metrics.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.1_k2/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.1_k2/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.1_k2/mechanism_group_summary.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.1_k2/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.1_k2/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.1_k2/overall_metrics.tex`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.1_k2/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.1_k2/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.1_k2/sequential_metrics.tex`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.1_k2/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.1_k2/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.1_k2/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.1_k2/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.1_k2/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.1_k2/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.1_k2/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.1_k2/figures/fig_detection_latency.png`
