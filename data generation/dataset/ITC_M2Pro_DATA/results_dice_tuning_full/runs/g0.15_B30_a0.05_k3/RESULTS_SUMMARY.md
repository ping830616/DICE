# DICE Full Retrain Results

## Setup
- Protocol: global, benign-only fit/calibration, block_B=30, alpha=0.05, persist_k=3, gain=0.15

## Overall
```text
           config  n_cases  n_features  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
            tier0       24          46   0.8000 0.931899         1.0        1.0           0.25           0.30              0.011353              0.023357                      0.0                 0.012710
      tier0_tier1       24          64   0.8375 0.960040         1.0        1.0           0.25           0.70              0.017081              0.048509                      0.0                 0.022866
tier0_tier1_tier2       24          75   0.9750 0.995119         1.0        1.0           0.25           0.95              0.002866              0.007781                      0.0                 0.004498
```

## Final Config Stressors
```text
stressor  roc_auc  pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
  ATOMIC   0.9375    0.95         1.0        1.0          0.002866          0.007229                  0.0             0.004334       2.522159      0.004364       4334.912663         0.004334
  BRANCH   1.0000    1.00         1.0        1.0          0.002866          0.009559                  0.0             0.006835       3.334957      0.006694       6835.645447         0.006835
   CACHE   0.9375    0.95         1.0        1.0          0.002866          0.009274                  0.0             0.006087       3.235287      0.006408       6087.919391         0.006087
   MEMBW   1.0000    1.00         1.0        1.0          0.002866          0.008810                  0.0             0.004991       3.073580      0.005944       4991.718049         0.004991
     TLB   1.0000    1.00         1.0        1.0          0.002866          0.007220                  0.0             0.004785       2.518785      0.004354       4785.542585         0.004785
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
            tier0       20      0.35      0.55          0.35  0.296032               0.023233                 0.012121
      tier0_tier1       20      0.15      0.30          0.15  0.133333               0.017716                 0.020307
tier0_tier1_tier2       20      0.20      0.35          0.20  0.180000               0.013748                 0.014086
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode
  ATOMIC     0.681364         0.189436     0.129201              tier0
  BRANCH     0.736356         0.141913     0.121731              tier0
   CACHE     0.548038         0.141951     0.310011              tier0
   MEMBW     0.731517         0.158110     0.110373              tier0
     TLB     0.672201         0.194235     0.133563              tier0
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share
  ATOMIC               memory_io       0.275793         0.279909             0.082602                 0.216540                 0.145156
  BRANCH               memory_io       0.217488         0.334410             0.054685                 0.246970                 0.146446
   CACHE                 compute       0.427084         0.269580             0.051829                 0.167022                 0.084484
   MEMBW               memory_io       0.241437         0.318930             0.067803                 0.218482                 0.153348
     TLB               memory_io       0.266106         0.292666             0.082546                 0.219672                 0.139010
```

## Sequential Decisioning
```text
           config  benign_run_alert_rate  benign_run_keep_rate  benign_persist_alerts_per_hour  benign_block_alerts_per_hour  anomaly_detect_rate  median_time_to_detect_s  p90_time_to_detect_s  detect_within_120s  detect_within_300s  detect_within_600s
            tier0                   0.25                  0.75                       64.948454                     69.587629                 0.30                     54.0                 603.5                0.20                0.20                0.25
      tier0_tier1                   0.25                  0.75                       66.804124                     68.659794                 0.70                     41.0                 771.3                0.50                0.50                0.55
tier0_tier1_tier2                   0.25                  0.75                       64.948454                     67.731959                 0.95                     32.0                 575.2                0.75                0.75                0.85
```

## Files
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/figures/fig_detection_latency.png`
