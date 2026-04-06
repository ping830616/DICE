# DICE Full Retrain Results

## Setup
- Feature profile: mixed ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_core_5hz.csv', 'tier2': 'tier2_core_5hz.csv'})
- Protocol: global, benign-only fit/calibration, block_B=20, alpha=0.05, persist_k=3, gain=0.25
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
          mixed             tier0       24          46          2.450757   0.7625 0.917472         1.0        1.0           0.25           0.35              0.008961              0.017210                      0.0                 0.009635
          mixed       tier0_tier1       24          57          2.975348   0.8250 0.955040         1.0        1.0           0.25           0.60              0.000052              0.000116                      0.0                 0.000050
          mixed tier0_tier1_tier2       24          64          3.317711   0.8375 0.957016         1.0        1.0           0.25           0.65              0.000055              0.000125                      0.0                 0.000058
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
          mixed   ATOMIC   0.7500 0.770833         1.0        1.0          0.000055          0.000092                  0.0             0.000040       1.672209      0.000037         41.131783         0.000040
          mixed   BRANCH   0.9375 0.950000         1.0        1.0          0.000055          0.000186                  0.0             0.000121       3.361856      0.000132        121.699325         0.000121
          mixed    CACHE   0.8125 0.804167         1.0        1.0          0.000055          0.000109                  0.0             0.000065       1.972706      0.000054         65.920411         0.000065
          mixed    MEMBW   0.8750 0.887500         1.0        1.0          0.000055          0.000141                  0.0             0.000074       2.554187      0.000087         74.774157         0.000074
          mixed      TLB   0.8125 0.804167         1.0        1.0          0.000055          0.000096                  0.0             0.000043       1.743278      0.000041         44.226742         0.000043
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
            tier0       20      0.30      0.65          0.30  0.248485               0.026242                 0.023077           mixed
      tier0_tier1       20      0.30      0.70          0.30  0.216117               0.019695                 0.010781           mixed
tier0_tier1_tier2       20      0.55      0.70          0.55  0.553260               0.017800                 0.014305           mixed
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.25      0.45          0.25  0.243175               0.016344                 0.016186           mixed
      tier0_tier1       20      0.15      0.35          0.15  0.128205               0.105896                 0.049638           mixed
tier0_tier1_tier2       20      0.10      0.45          0.10  0.110769               0.104877                 0.029479           mixed
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.25      0.55          0.25  0.217778               0.012318                 0.006776           mixed
      tier0_tier1       20      0.20      0.65          0.20  0.193333               0.012441                 0.007793           mixed
tier0_tier1_tier2       20      0.40      0.55          0.40  0.377143               0.012247                 0.007345           mixed
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.55      0.80      0.472222  0.398551               0.034342                 0.037228           mixed
      tier0_tier1       20      0.55      0.80      0.527778  0.499301               0.025015                 0.027232           mixed
tier0_tier1_tier2       20      0.55      0.75      0.583333  0.531039               0.025692                 0.025601           mixed
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.35      0.65        0.50          0.35  0.277980      0.35          0.65            0.428571            0.714286                0.333333            0.226667               0.002023                 0.009380            0.012265              0.010666           0.011619        0.138387           mixed
      tier0_tier1       20      0.30      0.65        0.45          0.30  0.231111      0.60          0.40            0.333333            0.583333                0.433333            0.288889               0.002121                 0.004887            0.021518              0.018759           0.015154        0.032589           mixed
tier0_tier1_tier2       20      0.40      0.70        0.30          0.40  0.383810      0.60          0.40            0.500000            0.833333                0.533333            0.494286              -0.001253                 0.001839            0.021992              0.017876           0.014019        0.003193           mixed
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.35       0.5        0.50          0.35  0.352222      0.50          0.50            0.200000            0.300000                0.116667            0.107143              -0.022038                 0.002707            0.012265              0.010666           0.011619        0.044987           mixed
      tier0_tier1       20      0.25       0.3        0.45          0.25  0.170629      0.80          0.20            0.312500            0.375000                0.250000            0.200000              -0.047843                 0.001432            0.021518              0.018759           0.015154       -0.256500           mixed
tier0_tier1_tier2       20      0.10       0.3        0.30          0.10  0.061538      0.65          0.35            0.076923            0.307692                0.066667            0.050000              -0.002817                 0.001690            0.021992              0.017876           0.014019       -0.123028           mixed
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0  conf_0.00              0.000000      13      0.65          0.35            0.384615            0.692308                0.283333            0.242424           mixed
            tier0  conf_0.05              0.050000      11      0.55          0.45            0.454545            0.727273                0.283333            0.242424           mixed
            tier0  conf_0.10              0.100000       9      0.45          0.55            0.444444            0.666667                0.333333            0.233333           mixed
            tier0    trained              0.138387       5      0.25          0.75            0.600000            0.600000                0.555556            0.266667           mixed
            tier0  conf_0.15              0.150000       5      0.25          0.75            0.600000            0.600000                0.555556            0.266667           mixed
            tier0  conf_0.20              0.200000       3      0.15          0.85            0.666667            0.666667                0.666667            0.160000           mixed
            tier0  conf_0.25              0.250000       3      0.15          0.85            0.666667            0.666667                0.666667            0.160000           mixed
      tier0_tier1  conf_0.00              0.000000      12      0.60          0.40            0.250000            0.583333                0.333333            0.155556           mixed
      tier0_tier1    trained              0.032589       9      0.45          0.55            0.333333            0.444444                0.333333            0.188889           mixed
      tier0_tier1  conf_0.05              0.050000       7      0.35          0.65            0.285714            0.428571                0.375000            0.190476           mixed
      tier0_tier1  conf_0.10              0.100000       6      0.30          0.70            0.333333            0.500000                0.500000            0.266667           mixed
      tier0_tier1  conf_0.15              0.150000       5      0.25          0.75            0.200000            0.400000                0.333333            0.066667           mixed
      tier0_tier1  conf_0.20              0.200000       4      0.20          0.80            0.250000            0.500000                0.333333            0.080000           mixed
      tier0_tier1  conf_0.25              0.250000       2      0.10          0.90            0.500000            0.500000                0.500000            0.133333           mixed
tier0_tier1_tier2  conf_0.00              0.000000      13      0.65          0.35            0.538462            0.692308                0.600000            0.540000           mixed
tier0_tier1_tier2    trained              0.003193      13      0.65          0.35            0.538462            0.692308                0.600000            0.540000           mixed
tier0_tier1_tier2  conf_0.05              0.050000       7      0.35          0.65            0.571429            0.714286                0.583333            0.380000           mixed
tier0_tier1_tier2  conf_0.10              0.100000       4      0.20          0.80            0.250000            0.500000                0.333333            0.080000           mixed
tier0_tier1_tier2  conf_0.15              0.150000       3      0.15          0.85            0.333333            0.666667                0.333333            0.100000           mixed
tier0_tier1_tier2  conf_0.20              0.200000       3      0.15          0.85            0.333333            0.666667                0.333333            0.100000           mixed
tier0_tier1_tier2  conf_0.25              0.250000       1      0.05          0.95            1.000000            1.000000                1.000000            0.200000           mixed
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0  conf_0.00              0.000000      12      0.60          0.40            0.333333            0.416667                0.266667            0.272222           mixed
            tier0    trained              0.044987       6      0.30          0.70            0.333333            0.500000                0.333333            0.146667           mixed
            tier0  conf_0.05              0.050000       6      0.30          0.70            0.333333            0.500000                0.333333            0.146667           mixed
            tier0  conf_0.10              0.100000       6      0.30          0.70            0.333333            0.500000                0.333333            0.146667           mixed
            tier0  conf_0.15              0.150000       2      0.10          0.90            0.500000            0.500000                0.500000            0.200000           mixed
            tier0  conf_0.20              0.200000       2      0.10          0.90            0.500000            0.500000                0.500000            0.200000           mixed
            tier0  conf_0.25              0.250000       1      0.05          0.95            1.000000            1.000000                1.000000            0.200000           mixed
      tier0_tier1    trained             -0.256500      16      0.80          0.20            0.312500            0.375000                0.250000            0.200000           mixed
      tier0_tier1  conf_0.00              0.000000      12      0.60          0.40            0.250000            0.250000                0.233333            0.190476           mixed
      tier0_tier1  conf_0.05              0.050000       9      0.45          0.55            0.111111            0.111111                0.100000            0.057143           mixed
      tier0_tier1  conf_0.10              0.100000       7      0.35          0.65            0.000000            0.000000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.15              0.150000       5      0.25          0.75            0.000000            0.000000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.20              0.200000       4      0.20          0.80            0.000000            0.000000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.25              0.250000       4      0.20          0.80            0.000000            0.000000                0.000000            0.000000           mixed
tier0_tier1_tier2    trained             -0.123028      15      0.75          0.25            0.133333            0.400000                0.100000            0.080000           mixed
tier0_tier1_tier2  conf_0.00              0.000000      11      0.55          0.45            0.000000            0.181818                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.05              0.050000       6      0.30          0.70            0.000000            0.333333                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.10              0.100000       4      0.20          0.80            0.000000            0.500000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.15              0.150000       3      0.15          0.85            0.000000            0.333333                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.20              0.200000       3      0.15          0.85            0.000000            0.333333                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.25              0.250000       3      0.15          0.85            0.000000            0.333333                0.000000            0.000000           mixed
```

## Diagnosis Mode Comparison
- Whole-run and post-alert-window diagnosis are exported together so the diagnosis mode can be evaluated directly.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile diagnosis_target    diagnosis_mode  family_acc  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau                       status  min_class_count  min_group_count    group_key  include_workload
            tier0       20      0.30      0.65      0.300000  0.248485               0.026242                 0.023077           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.30      0.70      0.300000  0.216117               0.019695                 0.010781           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.55      0.70      0.550000  0.553260               0.017800                 0.014305           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.25      0.45      0.250000  0.243175               0.016344                 0.016186           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.15      0.35      0.150000  0.128205               0.105896                 0.049638           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.10      0.45      0.100000  0.110769               0.104877                 0.029479           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.35      0.65      0.350000  0.277980               0.002023                 0.009380           mixed     hierarchical         whole_run        0.50      0.35          0.65            0.428571            0.714286                0.333333            0.226667            0.012265              0.010666           0.011619        0.138387                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.30      0.65      0.300000  0.231111               0.002121                 0.004887           mixed     hierarchical         whole_run        0.45      0.60          0.40            0.333333            0.583333                0.433333            0.288889            0.021518              0.018759           0.015154        0.032589                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.40      0.70      0.400000  0.383810              -0.001253                 0.001839           mixed     hierarchical         whole_run        0.30      0.60          0.40            0.500000            0.833333                0.533333            0.494286            0.021992              0.017876           0.014019        0.003193                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.35      0.50      0.350000  0.352222              -0.022038                 0.002707           mixed     hierarchical post_alert_window        0.50      0.50          0.50            0.200000            0.300000                0.116667            0.107143            0.012265              0.010666           0.011619        0.044987                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.25      0.30      0.250000  0.170629              -0.047843                 0.001432           mixed     hierarchical post_alert_window        0.45      0.80          0.20            0.312500            0.375000                0.250000            0.200000            0.021518              0.018759           0.015154       -0.256500                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.10      0.30      0.100000  0.061538              -0.002817                 0.001690           mixed     hierarchical post_alert_window        0.30      0.65          0.35            0.076923            0.307692                0.066667            0.050000            0.021992              0.017876           0.014019       -0.123028                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.55      0.80      0.472222  0.398551               0.034342                 0.037228           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.55      0.80      0.527778  0.499301               0.025015                 0.027232           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.55      0.75      0.583333  0.531039               0.025692                 0.025601           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.698959         0.143226     0.157815              tier0           mixed
  BRANCH     0.755511         0.088509     0.155979              tier0           mixed
   CACHE     0.534376         0.354234     0.111390              tier0           mixed
   MEMBW     0.768732         0.096530     0.134739              tier0           mixed
     TLB     0.689795         0.141984     0.168221              tier0           mixed
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC               memory_io       0.264390         0.395419             0.092366                 0.218386                 0.029439           mixed
  BRANCH               memory_io       0.250192         0.448756             0.051835                 0.210721                 0.038496           mixed
   CACHE               memory_io       0.469466         0.267250             0.071759                 0.149362                 0.042163           mixed
   MEMBW               memory_io       0.236750         0.467406             0.060078                 0.184887                 0.050879           mixed
     TLB               memory_io       0.305014         0.378108             0.081795                 0.210563                 0.024520           mixed
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
            tier0                   0.25                        2.755102                      4.591837                 0.35                     71.0                 551.2                0.25                0.25                0.30           mixed
      tier0_tier1                   0.25                        2.755102                      4.591837                 0.60                     78.5                 784.1                0.35                0.35                0.50           mixed
tier0_tier1_tier2                   0.25                        2.755102                      4.591837                 0.65                     43.0                 750.4                0.45                0.45                0.55           mixed
```

## Files
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B20_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B20_a0.05_k3/config_runtime_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B20_a0.05_k3/run_context.json`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B20_a0.05_k3/case_inventory.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B20_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B20_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B20_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B20_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B20_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B20_a0.05_k3/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B20_a0.05_k3/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B20_a0.05_k3/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B20_a0.05_k3/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B20_a0.05_k3/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B20_a0.05_k3/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B20_a0.05_k3/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B20_a0.05_k3/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B20_a0.05_k3/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B20_a0.05_k3/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B20_a0.05_k3/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B20_a0.05_k3/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B20_a0.05_k3/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B20_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B20_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B20_a0.05_k3/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B20_a0.05_k3/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B20_a0.05_k3/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B20_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B20_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B20_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B20_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B20_a0.05_k3/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B20_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B20_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B20_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B20_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B20_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B20_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B20_a0.05_k3/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B20_a0.05_k3/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B20_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B20_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B20_a0.05_k3/figures/fig_detection_latency.png`
