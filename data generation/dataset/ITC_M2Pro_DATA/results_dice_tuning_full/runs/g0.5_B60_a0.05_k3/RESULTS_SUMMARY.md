# DICE Full Retrain Results

## Setup
- Protocol: global, benign-only fit/calibration, block_B=60, alpha=0.05, persist_k=3, gain=0.5

## Overall
```text
           config  n_cases  n_features  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
            tier0       24          46   0.8000 0.931899         1.0        1.0           0.25           0.30              0.004166              0.008967                      0.0                 0.005044
      tier0_tier1       24          64   0.8125 0.953228         1.0        1.0           0.25           0.55              0.006032              0.019312                      0.0                 0.008957
tier0_tier1_tier2       24          75   0.9500 0.989710         1.0        1.0           0.25           0.95              0.002511              0.007089                      0.0                 0.003931
```

## Final Config Stressors
```text
stressor  roc_auc  pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
  ATOMIC   0.9375    0.95         1.0        1.0          0.002511          0.006502                  0.0             0.002902       2.588342      0.003990       2902.509223         0.002902
  BRANCH   0.9375    0.95         1.0        1.0          0.002511          0.008147                  0.0             0.005706       3.243333      0.005636       5706.509101         0.005706
   CACHE   0.9375    0.95         1.0        1.0          0.002511          0.008541                  0.0             0.005448       3.399866      0.006029       5449.422493         0.005448
   MEMBW   1.0000    1.00         1.0        1.0          0.002511          0.007479                  0.0             0.004461       2.977336      0.004968       4462.357423         0.004461
     TLB   0.9375    0.95         1.0        1.0          0.002511          0.006201                  0.0             0.003983       2.468447      0.003689       3983.945282         0.003983
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
            tier0       20      0.30      0.40          0.30  0.237296               0.024326                 0.018161
      tier0_tier1       20      0.20      0.55          0.20  0.174444               0.015328                 0.012527
tier0_tier1_tier2       20      0.15      0.25          0.15  0.118681               0.018493                 0.016391
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode
  ATOMIC     0.729021         0.190216     0.080763              tier0
  BRANCH     0.772207         0.141498     0.086295              tier0
   CACHE     0.629146         0.151631     0.219223              tier0
   MEMBW     0.765667         0.166573     0.067760              tier0
     TLB     0.723997         0.191286     0.084717              tier0
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share
  ATOMIC               memory_io       0.238255         0.308476             0.067929                 0.235608                 0.149730
  BRANCH               memory_io       0.196209         0.358465             0.047003                 0.252373                 0.145950
   CACHE               memory_io       0.352159         0.322219             0.047477                 0.186295                 0.091851
   MEMBW               memory_io       0.210212         0.348663             0.064557                 0.227464                 0.149104
     TLB               memory_io       0.226098         0.326407             0.072292                 0.234098                 0.141106
```

## Sequential Decisioning
```text
           config  benign_run_alert_rate  benign_run_keep_rate  benign_persist_alerts_per_hour  benign_block_alerts_per_hour  anomaly_detect_rate  median_time_to_detect_s  p90_time_to_detect_s  detect_within_120s  detect_within_300s  detect_within_600s
            tier0                   0.25                  0.75                       72.765957                     74.680851                 0.30                     73.5                 734.0                0.20                0.20                0.20
      tier0_tier1                   0.25                  0.75                       65.106383                     67.021277                 0.55                     62.0                 836.0                0.35                0.40                0.40
tier0_tier1_tier2                   0.25                  0.75                       64.148936                     66.063830                 0.95                     62.0                 819.8                0.65                0.65                0.65
```

## Files
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B60_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B60_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B60_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B60_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B60_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B60_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B60_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B60_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B60_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B60_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B60_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B60_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B60_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B60_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B60_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B60_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B60_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B60_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B60_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B60_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B60_a0.05_k3/figures/fig_detection_latency.png`
