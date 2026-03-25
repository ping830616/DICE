# DICE Full Retrain Results

## Setup
- Protocol: global, benign-only fit/calibration, block_B=30, alpha=0.05, persist_k=3, gain=0.5

## Overall
```text
           config  n_cases  n_features  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
            tier0       24          46   0.7750 0.919734         1.0        1.0           0.25           0.30              0.004801              0.009448                      0.0                 0.005130
      tier0_tier1       24          64   0.8125 0.949484         1.0        1.0           0.25           0.70              0.008005              0.020517                      0.0                 0.009483
tier0_tier1_tier2       24          75   0.9500 0.989710         1.0        1.0           0.25           0.95              0.002613              0.007015                      0.0                 0.003896
```

## Final Config Stressors
```text
stressor  roc_auc  pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
  ATOMIC   0.9375    0.95         1.0        1.0          0.002613          0.006055                  0.0             0.002501       2.316324      0.003441       2502.082079         0.002501
  BRANCH   0.9375    0.95         1.0        1.0          0.002613          0.009909                  0.0             0.006662       3.790594      0.007295       6662.736786         0.006662
   CACHE   0.9375    0.95         1.0        1.0          0.002613          0.007893                  0.0             0.004813       3.019452      0.005279       4814.254339         0.004813
   MEMBW   1.0000    1.00         1.0        1.0          0.002613          0.007191                  0.0             0.004055       2.750854      0.004577       4056.493493         0.004055
     TLB   0.9375    0.95         1.0        1.0          0.002613          0.007335                  0.0             0.004386       2.806032      0.004722       4386.506057         0.004386
```

## Paper-style Aggregates (Final Config)
- Base score mean stressor AUC-PR (all five): **0.9600**
- Base score mean stressor ROC-AUC (all five): **0.9500**
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
            tier0       20      0.40      0.40          0.40  0.307071               0.023877                 0.013793
      tier0_tier1       20      0.25      0.55          0.25  0.195455               0.015679                 0.013409
tier0_tier1_tier2       20      0.15      0.25          0.15  0.118681               0.017027                 0.015336
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode
  ATOMIC     0.720224         0.190928     0.088847              tier0
  BRANCH     0.764035         0.140988     0.094977              tier0
   CACHE     0.617670         0.148140     0.234190              tier0
   MEMBW     0.755930         0.169339     0.074731              tier0
     TLB     0.714338         0.192136     0.093526              tier0
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share
  ATOMIC               memory_io       0.246570         0.296367             0.074956                 0.238434                 0.143673
  BRANCH               memory_io       0.202766         0.348017             0.051436                 0.257344                 0.140437
   CACHE               memory_io       0.366202         0.307723             0.051143                 0.187428                 0.087504
   MEMBW               memory_io       0.217678         0.338399             0.070732                 0.229976                 0.143215
     TLB               memory_io       0.233908         0.314458             0.079547                 0.236450                 0.135637
```

## Sequential Decisioning
```text
           config  benign_run_alert_rate  benign_run_keep_rate  benign_persist_alerts_per_hour  benign_block_alerts_per_hour  anomaly_detect_rate  median_time_to_detect_s  p90_time_to_detect_s  detect_within_120s  detect_within_300s  detect_within_600s
            tier0                   0.25                  0.75                       70.515464                     73.298969                 0.30                     51.5                 608.0                0.20                0.20                0.25
      tier0_tier1                   0.25                  0.75                       65.876289                     67.731959                 0.70                     58.5                 777.3                0.45                0.45                0.50
tier0_tier1_tier2                   0.25                  0.75                       64.948454                     67.731959                 0.95                     32.0                 769.6                0.65                0.65                0.75
```

## Files
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/figures/fig_detection_latency.png`
