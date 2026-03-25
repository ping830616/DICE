# DICE Full Retrain Results

## Setup
- Protocol: workload_holdout, benign-only fit/calibration, block_B=60, alpha=0.02, persist_k=1, gain=0.35

## Overall
```text
           config  n_cases  n_features  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
            tier0       24          46   0.3500 0.767142         1.0        1.0            1.0           0.85              0.076633              0.051016                      0.0                 0.014080
      tier0_tier1       24          64   0.2250 0.721826         1.0        1.0            1.0           0.90              0.184327              0.105880                      0.0                 0.040936
tier0_tier1_tier2       24          75   0.2375 0.750397         1.0        1.0            1.0           1.00              0.084786              0.022955                      0.0                 0.041397
```

## Final Config Stressors
```text
stressor  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
  ATOMIC   0.1250 0.394643         1.0        1.0          0.084786          0.012987                  0.0             0.071798       0.153189     -0.071798      71799.368580         0.071798
  BRANCH   0.1875 0.412500         1.0        1.0          0.084786          0.024924                  0.0             0.056298       0.293974     -0.059862      56299.133364         0.056298
   CACHE   0.5000 0.642857         1.0        1.0          0.084786          0.075822                  0.0             0.008964       0.894273     -0.008964       8965.273714         0.008964
   MEMBW   0.1875 0.415476         1.0        1.0          0.084786          0.018453                  0.0             0.028373       0.217655     -0.066333      28374.028300         0.028373
     TLB   0.1875 0.412500         1.0        1.0          0.084786          0.023595                  0.0             0.048312       0.278293     -0.061191      48313.354102         0.048312
```

## Paper-style Aggregates (Final Config)
- Base score mean stressor AUC-PR (all five): **0.4556**
- Base score mean stressor ROC-AUC (all five): **0.2375**
- WC score mean stressor AUC-PR (all five): **1.0000**
- WC score mean stressor ROC-AUC (all five): **1.0000**
- Base score mean stressor AUC-PR (excluding BRANCH/TLB): **0.4843**
- Base score mean stressor ROC-AUC (excluding BRANCH/TLB): **0.2708**
- WC score mean stressor AUC-PR (excluding BRANCH/TLB): **1.0000**
- WC score mean stressor ROC-AUC (excluding BRANCH/TLB): **1.0000**

## Diagnosis
- Primary diagnosis uses workload-held, L1-normalized mechanism-group centroids over DICE residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second
            tier0       20      0.20      0.35          0.20  0.114286               0.059473                 0.048437
      tier0_tier1       20      0.10      0.30          0.10  0.073016               0.015241                 0.013707
tier0_tier1_tier2       20      0.35      0.45          0.35  0.332424               0.015608                 0.009500
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode
  ATOMIC     0.671727         0.164048     0.164225              tier0
  BRANCH     0.678137         0.207843     0.114020              tier0
   CACHE     0.445934         0.233897     0.320170              tier0
   MEMBW     0.610973         0.285093     0.103934              tier0
     TLB     0.651263         0.258037     0.090700              tier0
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share
  ATOMIC               memory_io       0.271682         0.404823             0.053546                 0.158704                 0.111245
  BRANCH               memory_io       0.224321         0.432364             0.060187                 0.174231                 0.108897
   CACHE               memory_io       0.214160         0.281898             0.101388                 0.346513                 0.056041
   MEMBW               memory_io       0.264837         0.383267             0.114273                 0.143756                 0.093867
     TLB               memory_io       0.219033         0.474675             0.079741                 0.153855                 0.072697
```

## Sequential Decisioning
```text
           config  benign_run_alert_rate  benign_run_keep_rate  benign_persist_alerts_per_hour  benign_block_alerts_per_hour  anomaly_detect_rate  median_time_to_detect_s  p90_time_to_detect_s  detect_within_120s  detect_within_300s  detect_within_600s
            tier0                    1.0                   0.0                     2850.319149                   2850.319149                 0.85                     60.0                 213.6                0.75                0.75                0.80
      tier0_tier1                    1.0                   0.0                     3600.000000                   3600.000000                 0.90                     60.0                  60.0                0.90                0.90                0.90
tier0_tier1_tier2                    1.0                   0.0                     3600.000000                   3600.000000                 1.00                     60.0                  60.0                0.95                0.95                0.95
```

## Holdout Robustness (Workload Drift Proxy)
```text
           config  mean_pr_auc  worst_pr_auc  mean_roc_auc  mean_pr_auc_wc  worst_pr_auc_wc  mean_roc_auc_wc  pooled_pr_auc  pooled_roc_auc  pooled_pr_auc_wc  pooled_roc_auc_wc  mean_fpr  mean_tpr  pooled_fpr  pooled_tpr  pooled_benign_keep_rate
            tier0       0.7825          0.71          0.25             1.0              1.0              1.0       0.767142          0.3500               1.0                1.0       1.0      0.85         1.0        0.85                      0.0
      tier0_tier1       0.7825          0.71          0.25             1.0              1.0              1.0       0.721826          0.2250               1.0                1.0       1.0      0.90         1.0        0.90                      0.0
tier0_tier1_tier2       0.8075          0.71          0.30             1.0              1.0              1.0       0.750397          0.2375               1.0                1.0       1.0      1.00         1.0        1.00                      0.0
```

## Files
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/overall_metrics.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/case_block_traces.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/sequential_metrics.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/mechanism_group_summary.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/overall_metrics.tex`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/sequential_metrics.tex`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/figures/fig_detection_latency.png`
