# DICE Full Retrain Results

## Setup
- Feature profile: mixed ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_core_5hz.csv', 'tier2': 'tier2_core_5hz.csv'})
- Protocol: global, benign-only fit/calibration, block_B=90, alpha=0.05, persist_k=3, gain=0.25
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
          mixed             tier0       24          46          2.157282   0.8000 0.931899         1.0        1.0            0.0           0.30              0.006348              0.014291                      0.0                 0.007905
          mixed       tier0_tier1       24          57          2.617313   0.8250 0.947375         1.0        1.0            0.0           0.45              0.000044              0.000109                      0.0                 0.000061
          mixed tier0_tier1_tier2       24          64          2.962150   0.8375 0.953625         1.0        1.0            0.0           0.45              0.000047              0.000119                      0.0                 0.000062
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
          mixed   ATOMIC   0.8125 0.804167         1.0        1.0          0.000047          0.000103                  0.0             0.000060       2.145371      0.000055         60.741983         0.000060
          mixed   BRANCH   0.9375 0.950000         1.0        1.0          0.000047          0.000168                  0.0             0.000117       3.487550      0.000120        117.700024         0.000117
          mixed    CACHE   0.8125 0.804167         1.0        1.0          0.000047          0.000103                  0.0             0.000060       2.140819      0.000055         60.631321         0.000060
          mixed    MEMBW   0.8750 0.887500         1.0        1.0          0.000047          0.000171                  0.0             0.000103       3.558995      0.000124        103.759194         0.000103
          mixed      TLB   0.7500 0.679167         1.0        1.0          0.000047          0.000111                  0.0             0.000056       2.317173      0.000064         57.324381         0.000056
```

## Paper-style Aggregates (Final Config)
- Base score mean stressor AUC-PR (all five): **0.8250**
- Base score mean stressor ROC-AUC (all five): **0.8375**
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
            tier0       20       0.3      0.55           0.3  0.238961               0.028284                 0.020219           mixed
      tier0_tier1       20       0.3      0.70           0.3  0.215035               0.022051                 0.018369           mixed
tier0_tier1_tier2       20       0.5      0.70           0.5  0.486593               0.021621                 0.017731           mixed
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20       0.2      0.65           0.2  0.206364               0.016862                 0.016438           mixed
      tier0_tier1       20       0.2      0.45           0.2  0.119444               0.017514                 0.015126           mixed
tier0_tier1_tier2       20       0.1      0.50           0.1  0.088889               0.037326                 0.016220           mixed
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20       0.3      0.70           0.3  0.269697               0.014770                 0.010523           mixed
      tier0_tier1       20       0.3      0.60           0.3  0.282540               0.013532                 0.009863           mixed
tier0_tier1_tier2       20       0.4      0.65           0.4  0.403175               0.012137                 0.007454           mixed
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.60      0.80      0.500000  0.421818               0.036571                 0.036803           mixed
      tier0_tier1       20      0.45      0.85      0.416667  0.335664               0.027952                 0.031391           mixed
tier0_tier1_tier2       20      0.55      0.75      0.583333  0.531039               0.028550                 0.029516           mixed
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.40       0.6        0.50          0.40  0.328889      0.20          0.80            0.500000            0.500000                0.500000            0.200000              -0.008487                 0.009020            0.015457              0.017402           0.013086        0.110110           mixed
      tier0_tier1       20      0.20       0.7        0.35          0.20  0.152727      0.60          0.40            0.250000            0.666667                0.233333            0.188889               0.002608                 0.002779            0.018348              0.014240           0.013198        0.048086           mixed
tier0_tier1_tier2       20      0.45       0.7        0.35          0.45  0.426234      0.55          0.45            0.545455            0.818182                0.566667            0.546667               0.007227                 0.010546            0.018528              0.012859           0.011496        0.106161           mixed
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.45      0.65        0.50          0.45  0.396667      0.75          0.25            0.533333            0.733333                0.533333            0.465714              -0.013412                 0.002462            0.015457              0.017402           0.013086       -0.084028           mixed
      tier0_tier1       20      0.25      0.45        0.35          0.25  0.191111      0.75          0.25            0.266667            0.400000                0.266667            0.210000              -0.020761                 0.004761            0.018348              0.014240           0.013198       -0.062449           mixed
tier0_tier1_tier2       20      0.15      0.55        0.35          0.15  0.109091      0.40          0.60            0.125000            0.375000                0.100000            0.100000              -0.007021                 0.007271            0.018528              0.012859           0.011496        0.141954           mixed
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0  conf_0.00              0.000000      12      0.60          0.40            0.416667            0.583333                0.400000            0.293333           mixed
            tier0  conf_0.05              0.050000      10      0.50          0.50            0.500000            0.600000                0.400000            0.293333           mixed
            tier0  conf_0.10              0.100000       6      0.30          0.70            0.500000            0.500000                0.500000            0.293333           mixed
            tier0    trained              0.110110       6      0.30          0.70            0.500000            0.500000                0.500000            0.293333           mixed
            tier0  conf_0.15              0.150000       4      0.20          0.80            0.500000            0.500000                0.333333            0.160000           mixed
            tier0  conf_0.20              0.200000       3      0.15          0.85            0.666667            0.666667                0.500000            0.160000           mixed
            tier0  conf_0.25              0.250000       2      0.10          0.90            1.000000            1.000000                1.000000            0.200000           mixed
      tier0_tier1  conf_0.00              0.000000      13      0.65          0.35            0.153846            0.615385                0.133333            0.088889           mixed
      tier0_tier1    trained              0.048086       8      0.40          0.60            0.250000            0.500000                0.250000            0.100000           mixed
      tier0_tier1  conf_0.05              0.050000       8      0.40          0.60            0.250000            0.500000                0.250000            0.100000           mixed
      tier0_tier1  conf_0.10              0.100000       7      0.35          0.65            0.285714            0.571429                0.250000            0.100000           mixed
      tier0_tier1  conf_0.15              0.150000       5      0.25          0.75            0.200000            0.400000                0.333333            0.066667           mixed
      tier0_tier1  conf_0.20              0.200000       3      0.15          0.85            0.000000            0.000000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.25              0.250000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.00              0.000000      14      0.70          0.30            0.571429            0.714286                0.650000            0.560000           mixed
tier0_tier1_tier2  conf_0.05              0.050000      10      0.50          0.50            0.500000            0.600000                0.458333            0.353333           mixed
tier0_tier1_tier2  conf_0.10              0.100000       6      0.30          0.70            0.333333            0.500000                0.333333            0.100000           mixed
tier0_tier1_tier2    trained              0.106161       6      0.30          0.70            0.333333            0.500000                0.333333            0.100000           mixed
tier0_tier1_tier2  conf_0.15              0.150000       5      0.25          0.75            0.400000            0.600000                0.333333            0.114286           mixed
tier0_tier1_tier2  conf_0.20              0.200000       4      0.20          0.80            0.500000            0.500000                0.333333            0.133333           mixed
tier0_tier1_tier2  conf_0.25              0.250000       2      0.10          0.90            0.500000            0.500000                0.500000            0.133333           mixed
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained             -0.084028      14      0.70          0.30            0.500000            0.714286                0.500000            0.431429           mixed
            tier0  conf_0.00              0.000000      11      0.55          0.45            0.454545            0.636364                0.366667            0.331429           mixed
            tier0  conf_0.05              0.050000       7      0.35          0.65            0.142857            0.428571                0.200000            0.133333           mixed
            tier0  conf_0.10              0.100000       6      0.30          0.70            0.166667            0.500000                0.250000            0.133333           mixed
            tier0  conf_0.15              0.150000       6      0.30          0.70            0.166667            0.500000                0.250000            0.133333           mixed
            tier0  conf_0.20              0.200000       1      0.05          0.95            1.000000            1.000000                1.000000            0.200000           mixed
            tier0  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
      tier0_tier1    trained             -0.062449      14      0.70          0.30            0.214286            0.357143                0.200000            0.130000           mixed
      tier0_tier1  conf_0.00              0.000000      13      0.65          0.35            0.230769            0.384615                0.200000            0.130000           mixed
      tier0_tier1  conf_0.05              0.050000       7      0.35          0.65            0.142857            0.142857                0.125000            0.057143           mixed
      tier0_tier1  conf_0.10              0.100000       3      0.15          0.85            0.000000            0.000000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.15              0.150000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.20              0.200000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.25              0.250000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.00              0.000000      13      0.65          0.35            0.076923            0.538462                0.100000            0.100000           mixed
tier0_tier1_tier2  conf_0.05              0.050000       8      0.40          0.60            0.000000            0.500000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.10              0.100000       5      0.25          0.75            0.000000            0.200000                0.000000            0.000000           mixed
tier0_tier1_tier2    trained              0.141954       4      0.20          0.80            0.000000            0.250000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.15              0.150000       4      0.20          0.80            0.000000            0.250000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.20              0.200000       3      0.15          0.85            0.000000            0.333333                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.25              0.250000       3      0.15          0.85            0.000000            0.333333                0.000000            0.000000           mixed
```

## Diagnosis Mode Comparison
- Whole-run and post-alert-window diagnosis are exported together so the diagnosis mode can be evaluated directly.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile diagnosis_target    diagnosis_mode  family_acc  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau                       status  min_class_count  min_group_count    group_key  include_workload
            tier0       20      0.30      0.55      0.300000  0.238961               0.028284                 0.020219           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.30      0.70      0.300000  0.215035               0.022051                 0.018369           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.50      0.70      0.500000  0.486593               0.021621                 0.017731           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.20      0.65      0.200000  0.206364               0.016862                 0.016438           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.20      0.45      0.200000  0.119444               0.017514                 0.015126           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.10      0.50      0.100000  0.088889               0.037326                 0.016220           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.40      0.60      0.400000  0.328889              -0.008487                 0.009020           mixed     hierarchical         whole_run        0.50      0.20          0.80            0.500000            0.500000                0.500000            0.200000            0.015457              0.017402           0.013086        0.110110                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.20      0.70      0.200000  0.152727               0.002608                 0.002779           mixed     hierarchical         whole_run        0.35      0.60          0.40            0.250000            0.666667                0.233333            0.188889            0.018348              0.014240           0.013198        0.048086                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.45      0.70      0.450000  0.426234               0.007227                 0.010546           mixed     hierarchical         whole_run        0.35      0.55          0.45            0.545455            0.818182                0.566667            0.546667            0.018528              0.012859           0.011496        0.106161                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.45      0.65      0.450000  0.396667              -0.013412                 0.002462           mixed     hierarchical post_alert_window        0.50      0.75          0.25            0.533333            0.733333                0.533333            0.465714            0.015457              0.017402           0.013086       -0.084028                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.25      0.45      0.250000  0.191111              -0.020761                 0.004761           mixed     hierarchical post_alert_window        0.35      0.75          0.25            0.266667            0.400000                0.266667            0.210000            0.018348              0.014240           0.013198       -0.062449                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.15      0.55      0.150000  0.109091              -0.007021                 0.007271           mixed     hierarchical post_alert_window        0.35      0.40          0.60            0.125000            0.375000                0.100000            0.100000            0.018528              0.012859           0.011496        0.141954                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.60      0.80      0.500000  0.421818               0.036571                 0.036803           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.45      0.85      0.416667  0.335664               0.027952                 0.031391           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.55      0.75      0.583333  0.531039               0.028550                 0.029516           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.716157         0.141939     0.141903              tier0           mixed
  BRANCH     0.780118         0.088616     0.131266              tier0           mixed
   CACHE     0.552461         0.350813     0.096726              tier0           mixed
   MEMBW     0.794959         0.097653     0.107388              tier0           mixed
     TLB     0.722188         0.138037     0.139775              tier0           mixed
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC               memory_io       0.259343         0.422713             0.082763                 0.198144                 0.037037           mixed
  BRANCH               memory_io       0.235346         0.493712             0.046635                 0.177283                 0.047024           mixed
   CACHE               memory_io       0.456778         0.298989             0.063051                 0.129860                 0.051322           mixed
   MEMBW               memory_io       0.220922         0.515744             0.054233                 0.149767                 0.059334           mixed
     TLB               memory_io       0.289837         0.432536             0.069880                 0.177016                 0.030730           mixed
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
            tier0                    0.0                             0.0                           0.0                 0.30                     94.0                 698.5                 0.2                 0.2                0.25           mixed
      tier0_tier1                    0.0                             0.0                           0.0                 0.45                     92.0                 666.4                 0.3                 0.3                0.35           mixed
tier0_tier1_tier2                    0.0                             0.0                           0.0                 0.45                     92.0                 544.6                 0.3                 0.3                0.40           mixed
```

## Files
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B90_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B90_a0.05_k3/config_runtime_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B90_a0.05_k3/run_context.json`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B90_a0.05_k3/case_inventory.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B90_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B90_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B90_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B90_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B90_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B90_a0.05_k3/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B90_a0.05_k3/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B90_a0.05_k3/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B90_a0.05_k3/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B90_a0.05_k3/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B90_a0.05_k3/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B90_a0.05_k3/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B90_a0.05_k3/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B90_a0.05_k3/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B90_a0.05_k3/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B90_a0.05_k3/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B90_a0.05_k3/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B90_a0.05_k3/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B90_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B90_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B90_a0.05_k3/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B90_a0.05_k3/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B90_a0.05_k3/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B90_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B90_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B90_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B90_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B90_a0.05_k3/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B90_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B90_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B90_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B90_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B90_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B90_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B90_a0.05_k3/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B90_a0.05_k3/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B90_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B90_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B90_a0.05_k3/figures/fig_detection_latency.png`
