# DICE Full Retrain Results

## Setup
- Feature profile: mixed ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_core_5hz.csv', 'tier2': 'tier2_core_5hz.csv'})
- Protocol: global, benign-only fit/calibration, block_B=20, alpha=0.05, persist_k=3, gain=0.35
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
          mixed             tier0       24          46          2.414570   0.7625 0.917472         1.0        1.0           0.25           0.35              0.007060              0.013378                      0.0                 0.007368
          mixed       tier0_tier1       24          57          2.971582   0.8125 0.949484         1.0        1.0           0.25           0.60              0.000055              0.000118                      0.0                 0.000053
          mixed tier0_tier1_tier2       24          64          3.396376   0.8375 0.957016         1.0        1.0           0.25           0.65              0.000058              0.000126                      0.0                 0.000058
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
          mixed   ATOMIC   0.7500 0.770833         1.0        1.0          0.000058          0.000094                  0.0             0.000042       1.601945      0.000036         42.515187         0.000042
          mixed   BRANCH   0.9375 0.950000         1.0        1.0          0.000058          0.000189                  0.0             0.000116       3.214551      0.000131        116.553832         0.000116
          mixed    CACHE   0.8125 0.804167         1.0        1.0          0.000058          0.000112                  0.0             0.000069       1.917893      0.000054         70.421561         0.000069
          mixed    MEMBW   0.8750 0.887500         1.0        1.0          0.000058          0.000143                  0.0             0.000072       2.428192      0.000084         73.126851         0.000072
          mixed      TLB   0.8125 0.804167         1.0        1.0          0.000058          0.000099                  0.0             0.000044       1.683867      0.000040         44.992610         0.000044
```

## Paper-style Aggregates (Final Config)
- Base score mean stressor AUC-PR (all five): **0.8433**
- Base score mean stressor ROC-AUC (all five): **0.8375**
- WC score mean stressor AUC-PR (all five): **1.0000**
- WC score mean stressor ROC-AUC (all five): **1.0000**
- Base score mean stressor AUC-PR (excluding BRANCH/TLB): **0.8208**
- Base score mean stressor ROC-AUC (excluding BRANCH/TLB): **0.8125**
- WC score mean stressor AUC-PR (excluding BRANCH/TLB): **1.0000**
- WC score mean stressor ROC-AUC (excluding BRANCH/TLB): **1.0000**

## Diagnosis
- Feature-level diagnosis uses normalized whole-run residual-attribution prototypes as the default paper-facing result, with diagnosis-only filtering that removes monotonic counters and downweights generic memory-state features.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.40      0.60          0.40  0.351429               0.023892                 0.020545           mixed
      tier0_tier1       20      0.35      0.55          0.35  0.251282               0.022614                 0.021380           mixed
tier0_tier1_tier2       20      0.50      0.60          0.50  0.485641               0.019200                 0.016231           mixed
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20       0.3      0.45           0.3  0.297143               0.016699                 0.013017           mixed
      tier0_tier1       20       0.1      0.25           0.1  0.057143               0.103865                 0.039541           mixed
tier0_tier1_tier2       20       0.1      0.45           0.1  0.110769               0.101945                 0.024355           mixed
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.25      0.50          0.25  0.253030               0.011428                 0.008250           mixed
      tier0_tier1       20      0.20      0.50          0.20  0.214286               0.016216                 0.013442           mixed
tier0_tier1_tier2       20      0.30      0.55          0.30  0.278730               0.014985                 0.011810           mixed
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.55      0.85      0.472222  0.398551               0.032455                 0.033880           mixed
      tier0_tier1       20      0.50      0.75      0.444444  0.354978               0.026260                 0.028743           mixed
tier0_tier1_tier2       20      0.45      0.75      0.527778  0.444042               0.025981                 0.030157           mixed
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.45      0.65        0.40          0.45  0.419091      0.35          0.65            0.571429            0.857143                    0.40            0.333333               0.010322                 0.011049            0.008769              0.006465           0.007508        0.175733           mixed
      tier0_tier1       20      0.35      0.55        0.35          0.35  0.308283      0.70          0.30            0.428571            0.571429                    0.55            0.414286               0.011029                 0.013762            0.018229              0.015853           0.014027        0.050047           mixed
tier0_tier1_tier2       20      0.45      0.60        0.20          0.45  0.439394      0.40          0.60            0.625000            0.750000                    0.70            0.633333               0.010993                 0.009183            0.019688              0.014517           0.015036        0.092867           mixed
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.35      0.55        0.40          0.35  0.319394      0.60          0.40            0.333333            0.416667                0.283333            0.235556              -0.010081                 0.007995            0.008769              0.006465           0.007508       -0.016645           mixed
      tier0_tier1       20      0.10      0.25        0.35          0.10  0.080000      0.75          0.25            0.133333            0.266667                0.133333            0.100000               0.041606                 0.012913            0.018229              0.015853           0.014027       -0.118033           mixed
tier0_tier1_tier2       20      0.20      0.35        0.20          0.20  0.195556      0.50          0.50            0.000000            0.200000                0.000000            0.000000               0.037506                 0.009938            0.019688              0.014517           0.015036        0.034765           mixed
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0  conf_0.00              0.000000      15      0.75          0.25            0.466667            0.600000                0.500000            0.459091           mixed
            tier0  conf_0.05              0.050000      12      0.60          0.40            0.500000            0.666667                0.550000            0.450000           mixed
            tier0  conf_0.10              0.100000       6      0.30          0.70            0.666667            0.666667                0.583333            0.283333           mixed
            tier0  conf_0.15              0.150000       5      0.25          0.75            0.800000            0.800000                0.875000            0.304762           mixed
            tier0    trained              0.175733       4      0.20          0.80            0.750000            0.750000                0.750000            0.171429           mixed
            tier0  conf_0.20              0.200000       4      0.20          0.80            0.750000            0.750000                0.750000            0.171429           mixed
            tier0  conf_0.25              0.250000       4      0.20          0.80            0.750000            0.750000                0.750000            0.171429           mixed
      tier0_tier1  conf_0.00              0.000000      15      0.75          0.25            0.333333            0.466667                0.383333            0.244444           mixed
      tier0_tier1  conf_0.05              0.050000      11      0.55          0.45            0.272727            0.363636                0.300000            0.157143           mixed
      tier0_tier1    trained              0.050047      11      0.55          0.45            0.272727            0.363636                0.300000            0.157143           mixed
      tier0_tier1  conf_0.10              0.100000       9      0.45          0.55            0.333333            0.333333                0.400000            0.200000           mixed
      tier0_tier1  conf_0.15              0.150000       5      0.25          0.75            0.400000            0.400000                0.500000            0.280000           mixed
      tier0_tier1  conf_0.20              0.200000       4      0.20          0.80            0.250000            0.250000                0.333333            0.080000           mixed
      tier0_tier1  conf_0.25              0.250000       2      0.10          0.90            0.000000            0.000000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.00              0.000000      16      0.80          0.20            0.500000            0.625000                0.550000            0.506667           mixed
tier0_tier1_tier2  conf_0.05              0.050000      12      0.60          0.40            0.500000            0.666667                0.466667            0.393333           mixed
tier0_tier1_tier2    trained              0.092867       8      0.40          0.60            0.375000            0.625000                0.416667            0.233333           mixed
tier0_tier1_tier2  conf_0.10              0.100000       8      0.40          0.60            0.375000            0.625000                0.416667            0.233333           mixed
tier0_tier1_tier2  conf_0.15              0.150000       6      0.30          0.70            0.333333            0.666667                0.222222            0.114286           mixed
tier0_tier1_tier2  conf_0.20              0.200000       4      0.20          0.80            0.500000            0.750000                0.333333            0.133333           mixed
tier0_tier1_tier2  conf_0.25              0.250000       1      0.05          0.95            1.000000            1.000000                1.000000            0.200000           mixed
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained             -0.016645      14      0.70          0.30            0.285714            0.428571                0.216667            0.206061           mixed
            tier0  conf_0.00              0.000000      14      0.70          0.30            0.285714            0.428571                0.216667            0.206061           mixed
            tier0  conf_0.05              0.050000       9      0.45          0.55            0.222222            0.444444                0.312500            0.213333           mixed
            tier0  conf_0.10              0.100000       4      0.20          0.80            0.500000            0.500000                0.500000            0.266667           mixed
            tier0  conf_0.15              0.150000       2      0.10          0.90            0.500000            0.500000                0.500000            0.200000           mixed
            tier0  conf_0.20              0.200000       2      0.10          0.90            0.500000            0.500000                0.500000            0.200000           mixed
            tier0  conf_0.25              0.250000       2      0.10          0.90            0.500000            0.500000                0.500000            0.200000           mixed
      tier0_tier1    trained             -0.118033      15      0.75          0.25            0.066667            0.200000                0.066667            0.080000           mixed
      tier0_tier1  conf_0.00              0.000000      14      0.70          0.30            0.000000            0.142857                0.000000            0.000000           mixed
      tier0_tier1  conf_0.05              0.050000      11      0.55          0.45            0.000000            0.090909                0.000000            0.000000           mixed
      tier0_tier1  conf_0.10              0.100000       8      0.40          0.60            0.000000            0.125000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.15              0.150000       8      0.40          0.60            0.000000            0.125000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.20              0.200000       7      0.35          0.65            0.000000            0.142857                0.000000            0.000000           mixed
      tier0_tier1  conf_0.25              0.250000       5      0.25          0.75            0.000000            0.200000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.00              0.000000      14      0.70          0.30            0.142857            0.357143                0.150000            0.150000           mixed
tier0_tier1_tier2    trained              0.034765      11      0.55          0.45            0.181818            0.454545                0.150000            0.190476           mixed
tier0_tier1_tier2  conf_0.05              0.050000       9      0.45          0.55            0.222222            0.555556                0.166667            0.213333           mixed
tier0_tier1_tier2  conf_0.10              0.100000       6      0.30          0.70            0.166667            0.500000                0.100000            0.133333           mixed
tier0_tier1_tier2  conf_0.15              0.150000       4      0.20          0.80            0.000000            0.500000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.20              0.200000       4      0.20          0.80            0.000000            0.500000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.25              0.250000       4      0.20          0.80            0.000000            0.500000                0.000000            0.000000           mixed
```

## Diagnosis Mode Comparison
- Whole-run and post-alert-window diagnosis are exported together so the diagnosis mode can be evaluated directly.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile diagnosis_target    diagnosis_mode  family_acc  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau                       status  min_class_count  min_group_count    group_key  include_workload
            tier0       20      0.40      0.60      0.400000  0.351429               0.023892                 0.020545           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.35      0.55      0.350000  0.251282               0.022614                 0.021380           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.50      0.60      0.500000  0.485641               0.019200                 0.016231           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.30      0.45      0.300000  0.297143               0.016699                 0.013017           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.10      0.25      0.100000  0.057143               0.103865                 0.039541           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.10      0.45      0.100000  0.110769               0.101945                 0.024355           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.45      0.65      0.450000  0.419091               0.010322                 0.011049           mixed     hierarchical         whole_run        0.40      0.35          0.65            0.571429            0.857143                0.400000            0.333333            0.008769              0.006465           0.007508        0.175733                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.35      0.55      0.350000  0.308283               0.011029                 0.013762           mixed     hierarchical         whole_run        0.35      0.70          0.30            0.428571            0.571429                0.550000            0.414286            0.018229              0.015853           0.014027        0.050047                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.45      0.60      0.450000  0.439394               0.010993                 0.009183           mixed     hierarchical         whole_run        0.20      0.40          0.60            0.625000            0.750000                0.700000            0.633333            0.019688              0.014517           0.015036        0.092867                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.35      0.55      0.350000  0.319394              -0.010081                 0.007995           mixed     hierarchical post_alert_window        0.40      0.60          0.40            0.333333            0.416667                0.283333            0.235556            0.008769              0.006465           0.007508       -0.016645                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.10      0.25      0.100000  0.080000               0.041606                 0.012913           mixed     hierarchical post_alert_window        0.35      0.75          0.25            0.133333            0.266667                0.133333            0.100000            0.018229              0.015853           0.014027       -0.118033                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.20      0.35      0.200000  0.195556               0.037506                 0.009938           mixed     hierarchical post_alert_window        0.20      0.50          0.50            0.000000            0.200000                0.000000            0.000000            0.019688              0.014517           0.015036        0.034765                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.55      0.85      0.472222  0.398551               0.032455                 0.033880           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.50      0.75      0.444444  0.354978               0.026260                 0.028743           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.45      0.75      0.527778  0.444042               0.025981                 0.030157           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.713771         0.130858     0.155370              tier0           mixed
  BRANCH     0.761680         0.084884     0.153436              tier0           mixed
   CACHE     0.541166         0.348866     0.109967              tier0           mixed
   MEMBW     0.773637         0.092752     0.133612              tier0           mixed
     TLB     0.699873         0.133484     0.166643              tier0           mixed
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC               memory_io       0.265400         0.400960             0.083115                 0.221376                 0.029149           mixed
  BRANCH               memory_io       0.250477         0.450214             0.050150                 0.212261                 0.036898           mixed
   CACHE               memory_io       0.466187         0.274435             0.067732                 0.151800                 0.039847           mixed
   MEMBW               memory_io       0.234034         0.471277             0.057966                 0.187462                 0.049261           mixed
     TLB               memory_io       0.303235         0.382119             0.076486                 0.213608                 0.024552           mixed
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
            tier0                   0.25                        2.755102                      4.591837                 0.35                     70.0                 550.6                0.25                0.25                0.30           mixed
      tier0_tier1                   0.25                        2.755102                      4.591837                 0.60                     78.0                 784.1                0.35                0.35                0.50           mixed
tier0_tier1_tier2                   0.25                        2.755102                      4.591837                 0.65                     43.0                 750.4                0.45                0.45                0.55           mixed
```

## Files
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B20_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B20_a0.05_k3/config_runtime_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B20_a0.05_k3/run_context.json`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B20_a0.05_k3/case_inventory.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B20_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B20_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B20_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B20_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B20_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B20_a0.05_k3/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B20_a0.05_k3/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B20_a0.05_k3/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B20_a0.05_k3/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B20_a0.05_k3/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B20_a0.05_k3/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B20_a0.05_k3/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B20_a0.05_k3/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B20_a0.05_k3/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B20_a0.05_k3/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B20_a0.05_k3/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B20_a0.05_k3/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B20_a0.05_k3/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B20_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B20_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B20_a0.05_k3/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B20_a0.05_k3/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B20_a0.05_k3/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B20_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B20_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B20_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B20_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B20_a0.05_k3/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B20_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B20_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B20_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B20_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B20_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B20_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B20_a0.05_k3/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B20_a0.05_k3/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B20_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B20_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B20_a0.05_k3/figures/fig_detection_latency.png`
