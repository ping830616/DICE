# DICE Full Retrain Results

## Setup
- Feature profile: mixed ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_core_5hz.csv', 'tier2': 'tier2_core_5hz.csv'})
- Protocol: global, benign-only fit/calibration, block_B=120, alpha=0.05, persist_k=3, gain=0.2
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
          mixed             tier0       24          46          2.234342   0.7875 0.921899         1.0        1.0            0.0           0.30              0.006765              0.015573                      0.0                 0.009038
          mixed       tier0_tier1       24          57          2.671632   0.8125 0.940232         1.0        1.0            0.0           0.45              0.000046              0.000115                      0.0                 0.000063
          mixed tier0_tier1_tier2       24          64          2.971436   0.8125 0.940232         1.0        1.0            0.0           0.45              0.000050              0.000126                      0.0                 0.000064
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
          mixed   ATOMIC   0.8125 0.804167         1.0        1.0           0.00005          0.000107                  0.0             0.000064       2.126073      0.000057         65.337386         0.000064
          mixed   BRANCH   0.8125 0.804167         1.0        1.0           0.00005          0.000170                  0.0             0.000116       3.365939      0.000120        117.418495         0.000116
          mixed    CACHE   0.8125 0.804167         1.0        1.0           0.00005          0.000107                  0.0             0.000060       2.118398      0.000057         61.186098         0.000060
          mixed    MEMBW   0.8750 0.887500         1.0        1.0           0.00005          0.000167                  0.0             0.000095       3.294063      0.000117         95.733495         0.000095
          mixed      TLB   0.7500 0.679167         1.0        1.0           0.00005          0.000110                  0.0             0.000056       2.189005      0.000061         57.398850         0.000056
```

## Paper-style Aggregates (Final Config)
- Base score mean stressor AUC-PR (all five): **0.7958**
- Base score mean stressor ROC-AUC (all five): **0.8125**
- WC score mean stressor AUC-PR (all five): **1.0000**
- WC score mean stressor ROC-AUC (all five): **1.0000**
- Base score mean stressor AUC-PR (excluding BRANCH/TLB): **0.8319**
- Base score mean stressor ROC-AUC (excluding BRANCH/TLB): **0.8333**
- WC score mean stressor AUC-PR (excluding BRANCH/TLB): **1.0000**
- WC score mean stressor ROC-AUC (excluding BRANCH/TLB): **1.0000**

## Diagnosis
- Feature-level diagnosis uses normalized whole-run residual-attribution prototypes as the default paper-facing result, with diagnosis-only filtering that removes monotonic counters and downweights generic memory-state features.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.35      0.55          0.35  0.298485               0.028863                 0.022491           mixed
      tier0_tier1       20      0.35      0.70          0.35  0.261197               0.021865                 0.016298           mixed
tier0_tier1_tier2       20      0.50      0.75          0.50  0.486593               0.020173                 0.014637           mixed
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.10      0.65          0.10  0.080808               0.016001                 0.013306           mixed
      tier0_tier1       20      0.15      0.40          0.15  0.118681               0.037188                 0.014102           mixed
tier0_tier1_tier2       20      0.15      0.40          0.15  0.155556               0.030633                 0.011520           mixed
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.30       0.6          0.30  0.290476               0.016814                 0.015255           mixed
      tier0_tier1       20      0.25       0.6          0.25  0.243506               0.016873                 0.015452           mixed
tier0_tier1_tier2       20      0.25       0.6          0.25  0.248889               0.011815                 0.008523           mixed
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.60      0.85      0.500000  0.421818               0.038932                 0.039527           mixed
      tier0_tier1       20      0.45      0.80      0.416667  0.335664               0.029477                 0.031343           mixed
tier0_tier1_tier2       20      0.50      0.75      0.500000  0.449084               0.028531                 0.027860           mixed
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20       0.4      0.60        0.55           0.4  0.326061      0.45          0.55            0.444444            0.555556                0.400000            0.293333              -0.013403                -0.006152            0.016781              0.016474           0.009515        0.021043           mixed
      tier0_tier1       20       0.3      0.65        0.35           0.3  0.229451      0.80          0.20            0.312500            0.687500                0.283333            0.232900               0.002089                 0.002884            0.021201              0.019323           0.011681       -0.094583           mixed
tier0_tier1_tier2       20       0.5      0.80        0.40           0.5  0.490476      0.40          0.60            0.625000            0.875000                0.500000            0.500000               0.010363                 0.006133            0.017483              0.014972           0.013040        0.136079           mixed
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.40      0.60        0.55          0.40  0.355556      0.70          0.30            0.500000            0.714286                0.466667            0.420476              -0.017391                 0.000721            0.016781              0.016474           0.009515       -0.105647           mixed
      tier0_tier1       20      0.25      0.40        0.35          0.25  0.166667      0.60          0.40            0.250000            0.500000                0.200000            0.168889              -0.029098                 0.001863            0.021201              0.019323           0.011681       -0.126217           mixed
tier0_tier1_tier2       20      0.20      0.45        0.40          0.20  0.177143      0.55          0.45            0.181818            0.363636                0.133333            0.114286               0.007133                 0.005923            0.017483              0.014972           0.013040        0.049867           mixed
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0  conf_0.00              0.000000      10      0.50          0.50            0.500000            0.600000                0.400000            0.310000           mixed
            tier0    trained              0.021043       9      0.45          0.55            0.555556            0.666667                0.500000            0.310000           mixed
            tier0  conf_0.05              0.050000       6      0.30          0.70            0.500000            0.500000                0.500000            0.293333           mixed
            tier0  conf_0.10              0.100000       5      0.25          0.75            0.600000            0.600000                0.500000            0.293333           mixed
            tier0  conf_0.15              0.150000       4      0.20          0.80            0.500000            0.500000                0.333333            0.160000           mixed
            tier0  conf_0.20              0.200000       3      0.15          0.85            0.666667            0.666667                0.500000            0.160000           mixed
            tier0  conf_0.25              0.250000       3      0.15          0.85            0.666667            0.666667                0.500000            0.160000           mixed
      tier0_tier1    trained             -0.094583      16      0.80          0.20            0.312500            0.687500                0.283333            0.232900           mixed
      tier0_tier1  conf_0.00              0.000000      12      0.60          0.40            0.333333            0.666667                0.270833            0.175758           mixed
      tier0_tier1  conf_0.05              0.050000       8      0.40          0.60            0.375000            0.750000                0.250000            0.120000           mixed
      tier0_tier1  conf_0.10              0.100000       7      0.35          0.65            0.285714            0.714286                0.250000            0.100000           mixed
      tier0_tier1  conf_0.15              0.150000       5      0.25          0.75            0.400000            0.600000                0.333333            0.114286           mixed
      tier0_tier1  conf_0.20              0.200000       4      0.20          0.80            0.250000            0.500000                0.333333            0.080000           mixed
      tier0_tier1  conf_0.25              0.250000       2      0.10          0.90            0.000000            0.500000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.00              0.000000      15      0.75          0.25            0.533333            0.800000                0.550000            0.535758           mixed
tier0_tier1_tier2  conf_0.05              0.050000       8      0.40          0.60            0.375000            0.750000                0.333333            0.188889           mixed
tier0_tier1_tier2  conf_0.10              0.100000       8      0.40          0.60            0.375000            0.750000                0.333333            0.188889           mixed
tier0_tier1_tier2    trained              0.136079       5      0.25          0.75            0.400000            0.600000                0.333333            0.114286           mixed
tier0_tier1_tier2  conf_0.15              0.150000       4      0.20          0.80            0.500000            0.500000                0.333333            0.133333           mixed
tier0_tier1_tier2  conf_0.20              0.200000       3      0.15          0.85            0.666667            0.666667                0.500000            0.160000           mixed
tier0_tier1_tier2  conf_0.25              0.250000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000           mixed
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained             -0.105647      13      0.65          0.35            0.461538            0.692308                0.433333            0.387143           mixed
            tier0  conf_0.00              0.000000      11      0.55          0.45            0.363636            0.636364                0.266667            0.230000           mixed
            tier0  conf_0.05              0.050000       7      0.35          0.65            0.428571            0.571429                0.333333            0.260000           mixed
            tier0  conf_0.10              0.100000       4      0.20          0.80            0.250000            0.500000                0.333333            0.200000           mixed
            tier0  conf_0.15              0.150000       3      0.15          0.85            0.333333            0.666667                0.500000            0.200000           mixed
            tier0  conf_0.20              0.200000       2      0.10          0.90            0.500000            1.000000                0.500000            0.200000           mixed
            tier0  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
      tier0_tier1    trained             -0.126217      13      0.65          0.35            0.307692            0.538462                0.233333            0.203175           mixed
      tier0_tier1  conf_0.00              0.000000      12      0.60          0.40            0.250000            0.500000                0.200000            0.168889           mixed
      tier0_tier1  conf_0.05              0.050000       7      0.35          0.65            0.142857            0.571429                0.111111            0.066667           mixed
      tier0_tier1  conf_0.10              0.100000       3      0.15          0.85            0.000000            0.666667                0.000000            0.000000           mixed
      tier0_tier1  conf_0.15              0.150000       3      0.15          0.85            0.000000            0.666667                0.000000            0.000000           mixed
      tier0_tier1  conf_0.20              0.200000       2      0.10          0.90            0.000000            0.500000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.25              0.250000       2      0.10          0.90            0.000000            0.500000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.00              0.000000      15      0.75          0.25            0.133333            0.400000                0.200000            0.180000           mixed
tier0_tier1_tier2    trained              0.049867       8      0.40          0.60            0.000000            0.250000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.05              0.050000       8      0.40          0.60            0.000000            0.250000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.10              0.100000       5      0.25          0.75            0.000000            0.200000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.15              0.150000       4      0.20          0.80            0.000000            0.250000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.20              0.200000       3      0.15          0.85            0.000000            0.333333                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.25              0.250000       3      0.15          0.85            0.000000            0.333333                0.000000            0.000000           mixed
```

## Diagnosis Mode Comparison
- Whole-run and post-alert-window diagnosis are exported together so the diagnosis mode can be evaluated directly.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile diagnosis_target    diagnosis_mode  family_acc  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau                       status  min_class_count  min_group_count    group_key  include_workload
            tier0       20      0.35      0.55      0.350000  0.298485               0.028863                 0.022491           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.35      0.70      0.350000  0.261197               0.021865                 0.016298           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.50      0.75      0.500000  0.486593               0.020173                 0.014637           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.10      0.65      0.100000  0.080808               0.016001                 0.013306           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.15      0.40      0.150000  0.118681               0.037188                 0.014102           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.15      0.40      0.150000  0.155556               0.030633                 0.011520           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.40      0.60      0.400000  0.326061              -0.013403                -0.006152           mixed     hierarchical         whole_run        0.55      0.45          0.55            0.444444            0.555556                0.400000            0.293333            0.016781              0.016474           0.009515        0.021043                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.30      0.65      0.300000  0.229451               0.002089                 0.002884           mixed     hierarchical         whole_run        0.35      0.80          0.20            0.312500            0.687500                0.283333            0.232900            0.021201              0.019323           0.011681       -0.094583                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.50      0.80      0.500000  0.490476               0.010363                 0.006133           mixed     hierarchical         whole_run        0.40      0.40          0.60            0.625000            0.875000                0.500000            0.500000            0.017483              0.014972           0.013040        0.136079                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.40      0.60      0.400000  0.355556              -0.017391                 0.000721           mixed     hierarchical post_alert_window        0.55      0.70          0.30            0.500000            0.714286                0.466667            0.420476            0.016781              0.016474           0.009515       -0.105647                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.25      0.40      0.250000  0.166667              -0.029098                 0.001863           mixed     hierarchical post_alert_window        0.35      0.60          0.40            0.250000            0.500000                0.200000            0.168889            0.021201              0.019323           0.011681       -0.126217                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.20      0.45      0.200000  0.177143               0.007133                 0.005923           mixed     hierarchical post_alert_window        0.40      0.55          0.45            0.181818            0.363636                0.133333            0.114286            0.017483              0.014972           0.013040        0.049867                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.60      0.85      0.500000  0.421818               0.038932                 0.039527           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.45      0.80      0.416667  0.335664               0.029477                 0.031343           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.50      0.75      0.500000  0.449084               0.028531                 0.027860           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.713943         0.149801     0.136256              tier0           mixed
  BRANCH     0.783385         0.091255     0.125359              tier0           mixed
   CACHE     0.554263         0.352904     0.092833              tier0           mixed
   MEMBW     0.799599         0.100126     0.100275              tier0           mixed
     TLB     0.725046         0.142601     0.132353              tier0           mixed
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC               memory_io       0.256653         0.431160             0.086058                 0.187909                 0.038220           mixed
  BRANCH               memory_io       0.228154         0.508197             0.046980                 0.167413                 0.049256           mixed
   CACHE               memory_io       0.454559         0.305226             0.063484                 0.122495                 0.054235           mixed
   MEMBW               memory_io       0.216203         0.527384             0.054299                 0.139370                 0.062744           mixed
     TLB               memory_io       0.285170         0.447761             0.070019                 0.165430                 0.031620           mixed
```

## Supervised Diagnosis
- This path is intended for expanded anomaly sets with repeated runs per workload-stressor pair. It is skipped automatically until each stressor has enough samples.
```text
           config                       status  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  min_class_count  min_group_count    group_key  include_workload feature_profile
            tier0 skipped_insufficient_samples       20       NaN       NaN           NaN       NaN                4                4 base_case_id                 1           mixed
      tier0_tier1 skipped_insufficient_samples       20       NaN       NaN           NaN       NaN                4                4 base_case_id                 1           mixed
tier0_tier1_tier2 skipped_insufficient_samples       20       NaN       NaN           NaN       NaN                4                4 base_case_id                 1           mixed
```

## Sequential Decisioning
```text
           config  benign_run_alert_rate  benign_persist_alerts_per_hour  benign_block_alerts_per_hour  anomaly_detect_rate  median_time_to_detect_s  p90_time_to_detect_s  detect_within_120s  detect_within_300s  detect_within_600s feature_profile
            tier0                    0.0                             0.0                           0.0                 0.30                    122.0                 650.0                 0.0                 0.2                0.25           mixed
      tier0_tier1                    0.0                             0.0                           0.0                 0.45                    122.0                 550.6                 0.0                 0.3                0.40           mixed
tier0_tier1_tier2                    0.0                             0.0                           0.0                 0.45                    122.0                 544.8                 0.0                 0.3                0.40           mixed
```

## Files
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B120_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B120_a0.05_k3/config_runtime_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B120_a0.05_k3/run_context.json`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B120_a0.05_k3/case_inventory.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B120_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B120_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B120_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B120_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B120_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B120_a0.05_k3/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B120_a0.05_k3/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B120_a0.05_k3/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B120_a0.05_k3/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B120_a0.05_k3/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B120_a0.05_k3/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B120_a0.05_k3/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B120_a0.05_k3/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B120_a0.05_k3/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B120_a0.05_k3/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B120_a0.05_k3/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B120_a0.05_k3/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B120_a0.05_k3/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B120_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B120_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B120_a0.05_k3/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B120_a0.05_k3/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B120_a0.05_k3/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B120_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B120_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B120_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B120_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B120_a0.05_k3/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B120_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B120_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B120_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B120_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B120_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B120_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B120_a0.05_k3/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B120_a0.05_k3/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B120_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B120_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B120_a0.05_k3/figures/fig_detection_latency.png`
