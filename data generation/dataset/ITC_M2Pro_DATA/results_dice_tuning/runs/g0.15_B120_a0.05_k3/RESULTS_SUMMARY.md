# DICE Full Retrain Results

## Setup
- Feature profile: mixed ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_core_5hz.csv', 'tier2': 'tier2_core_5hz.csv'})
- Protocol: global, benign-only fit/calibration, block_B=120, alpha=0.05, persist_k=3, gain=0.15
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
          mixed             tier0       24          46          2.155559   0.7875 0.921899         1.0        1.0            0.0           0.30              0.008313              0.019020                      0.0                 0.011024
          mixed       tier0_tier1       24          57          2.561393   0.8000 0.931899         1.0        1.0            0.0           0.45              0.000046              0.000115                      0.0                 0.000062
          mixed tier0_tier1_tier2       24          64          2.938144   0.8125 0.940232         1.0        1.0            0.0           0.45              0.000049              0.000125                      0.0                 0.000063
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
          mixed   ATOMIC   0.8125 0.804167         1.0        1.0          0.000049          0.000107                  0.0             0.000063       2.137409      0.000057         64.345702         0.000063
          mixed   BRANCH   0.8750 0.887500         1.0        1.0          0.000049          0.000166                  0.0             0.000114       3.323183      0.000117        115.488643         0.000114
          mixed    CACHE   0.8125 0.804167         1.0        1.0          0.000049          0.000105                  0.0             0.000059       2.107179      0.000056         59.903064         0.000059
          mixed    MEMBW   0.8125 0.804167         1.0        1.0          0.000049          0.000162                  0.0             0.000091       3.233267      0.000113         91.849716         0.000091
          mixed      TLB   0.7500 0.679167         1.0        1.0          0.000049          0.000107                  0.0             0.000056       2.133707      0.000057         56.855305         0.000056
```

## Paper-style Aggregates (Final Config)
- Base score mean stressor AUC-PR (all five): **0.7958**
- Base score mean stressor ROC-AUC (all five): **0.8125**
- WC score mean stressor AUC-PR (all five): **1.0000**
- WC score mean stressor ROC-AUC (all five): **1.0000**
- Base score mean stressor AUC-PR (excluding BRANCH/TLB): **0.8042**
- Base score mean stressor ROC-AUC (excluding BRANCH/TLB): **0.8125**
- WC score mean stressor AUC-PR (excluding BRANCH/TLB): **1.0000**
- WC score mean stressor ROC-AUC (excluding BRANCH/TLB): **1.0000**

## Diagnosis
- Feature-level diagnosis uses normalized whole-run residual-attribution prototypes as the default paper-facing result, with diagnosis-only filtering that removes monotonic counters and downweights generic memory-state features.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.35      0.55          0.35  0.306234               0.028197                 0.023666           mixed
      tier0_tier1       20      0.30      0.65          0.30  0.231746               0.019247                 0.010459           mixed
tier0_tier1_tier2       20      0.40      0.75          0.40  0.352381               0.017588                 0.008712           mixed
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.10      0.60          0.10  0.076364               0.018010                 0.009924           mixed
      tier0_tier1       20      0.15      0.40          0.15  0.118681               0.038375                 0.016308           mixed
tier0_tier1_tier2       20      0.10      0.45          0.10  0.090000               0.019277                 0.012507           mixed
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.20      0.55          0.20  0.180808               0.020531                 0.020687           mixed
      tier0_tier1       20      0.25      0.55          0.25  0.243506               0.019054                 0.015044           mixed
tier0_tier1_tier2       20      0.30      0.60          0.30  0.269841               0.013412                 0.011805           mixed
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.60      0.85      0.500000  0.421818               0.038620                 0.039412           mixed
      tier0_tier1       20      0.45      0.75      0.416667  0.335664               0.027851                 0.029243           mixed
tier0_tier1_tier2       20      0.50      0.70      0.500000  0.448622               0.026458                 0.028681           mixed
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.30      0.50        0.50          0.30  0.295556      0.40          0.60            0.250000            0.375000                0.300000            0.266667              -0.010040                 0.002182            0.017115              0.017564           0.011609        0.054628           mixed
      tier0_tier1       20      0.30      0.70        0.30          0.30  0.222178      0.65          0.35            0.307692            0.692308                0.366667            0.246667              -0.002429                 0.001619            0.020705              0.019509           0.008036       -0.000871           mixed
tier0_tier1_tier2       20      0.35      0.75        0.35          0.35  0.323260      0.50          0.50            0.600000            0.900000                0.600000            0.560000               0.014859                 0.007206            0.017966              0.015530           0.016111        0.148623           mixed
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.25       0.6        0.50          0.25  0.231111      0.65          0.35            0.230769            0.692308                     0.2            0.168889              -0.015668                 0.004746            0.017115              0.017564           0.011609       -0.038478           mixed
      tier0_tier1       20      0.20       0.4        0.30          0.20  0.132308      0.65          0.35            0.230769            0.461538                     0.2            0.168889              -0.015026                 0.003922            0.020705              0.019509           0.008036       -0.034518           mixed
tier0_tier1_tier2       20      0.15       0.4        0.35          0.15  0.124444      0.55          0.45            0.181818            0.363636                     0.2            0.123810               0.001997                 0.008565            0.017966              0.015530           0.016111        0.061084           mixed
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0  conf_0.00              0.000000      11      0.55          0.45            0.363636            0.454545                0.333333            0.314286           mixed
            tier0  conf_0.05              0.050000       6      0.30          0.70            0.333333            0.333333                0.375000            0.233333           mixed
            tier0    trained              0.054628       6      0.30          0.70            0.333333            0.333333                0.375000            0.233333           mixed
            tier0  conf_0.10              0.100000       6      0.30          0.70            0.333333            0.333333                0.375000            0.233333           mixed
            tier0  conf_0.15              0.150000       5      0.25          0.75            0.400000            0.400000                0.500000            0.266667           mixed
            tier0  conf_0.20              0.200000       2      0.10          0.90            0.500000            0.500000                0.500000            0.133333           mixed
            tier0  conf_0.25              0.250000       2      0.10          0.90            0.500000            0.500000                0.500000            0.133333           mixed
      tier0_tier1    trained             -0.000871      11      0.55          0.45            0.272727            0.727273                0.266667            0.166667           mixed
      tier0_tier1  conf_0.00              0.000000      11      0.55          0.45            0.272727            0.727273                0.266667            0.166667           mixed
      tier0_tier1  conf_0.05              0.050000       6      0.30          0.70            0.333333            0.666667                0.250000            0.114286           mixed
      tier0_tier1  conf_0.10              0.100000       4      0.20          0.80            0.250000            0.500000                0.333333            0.080000           mixed
      tier0_tier1  conf_0.15              0.150000       3      0.15          0.85            0.333333            0.666667                0.333333            0.100000           mixed
      tier0_tier1  conf_0.20              0.200000       2      0.10          0.90            0.000000            0.500000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.25              0.250000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.00              0.000000      17      0.85          0.15            0.352941            0.764706                0.350000            0.280952           mixed
tier0_tier1_tier2  conf_0.05              0.050000       8      0.40          0.60            0.375000            0.625000                0.300000            0.222222           mixed
tier0_tier1_tier2  conf_0.10              0.100000       8      0.40          0.60            0.375000            0.625000                0.300000            0.222222           mixed
tier0_tier1_tier2    trained              0.148623       5      0.25          0.75            0.600000            0.600000                0.500000            0.266667           mixed
tier0_tier1_tier2  conf_0.15              0.150000       5      0.25          0.75            0.600000            0.600000                0.500000            0.266667           mixed
tier0_tier1_tier2  conf_0.20              0.200000       4      0.20          0.80            0.500000            0.500000                0.333333            0.133333           mixed
tier0_tier1_tier2  conf_0.25              0.250000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000           mixed
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained             -0.038478      13      0.65          0.35            0.230769            0.692308                0.200000            0.168889           mixed
            tier0  conf_0.00              0.000000      13      0.65          0.35            0.230769            0.692308                0.200000            0.168889           mixed
            tier0  conf_0.05              0.050000       7      0.35          0.65            0.285714            0.857143                0.200000            0.133333           mixed
            tier0  conf_0.10              0.100000       4      0.20          0.80            0.250000            0.750000                0.333333            0.133333           mixed
            tier0  conf_0.15              0.150000       2      0.10          0.90            0.000000            0.500000                0.000000            0.000000           mixed
            tier0  conf_0.20              0.200000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000           mixed
            tier0  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
      tier0_tier1    trained             -0.034518      12      0.60          0.40            0.166667            0.416667                0.166667            0.137143           mixed
      tier0_tier1  conf_0.00              0.000000      12      0.60          0.40            0.166667            0.416667                0.166667            0.137143           mixed
      tier0_tier1  conf_0.05              0.050000       7      0.35          0.65            0.000000            0.428571                0.000000            0.000000           mixed
      tier0_tier1  conf_0.10              0.100000       4      0.20          0.80            0.000000            0.500000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.15              0.150000       4      0.20          0.80            0.000000            0.500000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.20              0.200000       4      0.20          0.80            0.000000            0.500000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.25              0.250000       3      0.15          0.85            0.000000            0.333333                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.00              0.000000      18      0.90          0.10            0.166667            0.444444                0.150000            0.133333           mixed
tier0_tier1_tier2  conf_0.05              0.050000       6      0.30          0.70            0.166667            0.166667                0.111111            0.100000           mixed
tier0_tier1_tier2    trained              0.061084       4      0.20          0.80            0.000000            0.000000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.10              0.100000       3      0.15          0.85            0.000000            0.000000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.15              0.150000       2      0.10          0.90            0.000000            0.000000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.20              0.200000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
tier0_tier1_tier2  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
```

## Diagnosis Mode Comparison
- Whole-run and post-alert-window diagnosis are exported together so the diagnosis mode can be evaluated directly.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile diagnosis_target    diagnosis_mode  family_acc  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau                       status  min_class_count  min_group_count    group_key  include_workload
            tier0       20      0.35      0.55      0.350000  0.306234               0.028197                 0.023666           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.30      0.65      0.300000  0.231746               0.019247                 0.010459           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.40      0.75      0.400000  0.352381               0.017588                 0.008712           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.10      0.60      0.100000  0.076364               0.018010                 0.009924           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.15      0.40      0.150000  0.118681               0.038375                 0.016308           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.10      0.45      0.100000  0.090000               0.019277                 0.012507           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.30      0.50      0.300000  0.295556              -0.010040                 0.002182           mixed     hierarchical         whole_run        0.50      0.40          0.60            0.250000            0.375000                0.300000            0.266667            0.017115              0.017564           0.011609        0.054628                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.30      0.70      0.300000  0.222178              -0.002429                 0.001619           mixed     hierarchical         whole_run        0.30      0.65          0.35            0.307692            0.692308                0.366667            0.246667            0.020705              0.019509           0.008036       -0.000871                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.35      0.75      0.350000  0.323260               0.014859                 0.007206           mixed     hierarchical         whole_run        0.35      0.50          0.50            0.600000            0.900000                0.600000            0.560000            0.017966              0.015530           0.016111        0.148623                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.25      0.60      0.250000  0.231111              -0.015668                 0.004746           mixed     hierarchical post_alert_window        0.50      0.65          0.35            0.230769            0.692308                0.200000            0.168889            0.017115              0.017564           0.011609       -0.038478                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.20      0.40      0.200000  0.132308              -0.015026                 0.003922           mixed     hierarchical post_alert_window        0.30      0.65          0.35            0.230769            0.461538                0.200000            0.168889            0.020705              0.019509           0.008036       -0.034518                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.15      0.40      0.150000  0.124444               0.001997                 0.008565           mixed     hierarchical post_alert_window        0.35      0.55          0.45            0.181818            0.363636                0.200000            0.123810            0.017966              0.015530           0.016111        0.061084                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.60      0.85      0.500000  0.421818               0.038620                 0.039412           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.45      0.75      0.416667  0.335664               0.027851                 0.029243           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.50      0.70      0.500000  0.448622               0.026458                 0.028681           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.706696         0.158836     0.134468              tier0           mixed
  BRANCH     0.780409         0.093815     0.125776              tier0           mixed
   CACHE     0.552313         0.354888     0.092798              tier0           mixed
   MEMBW     0.798805         0.101281     0.099914              tier0           mixed
     TLB     0.720855         0.147203     0.131942              tier0           mixed
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC               memory_io       0.259295         0.425865             0.091775                 0.183649                 0.039415           mixed
  BRANCH               memory_io       0.229464         0.504946             0.048575                 0.165999                 0.051017           mixed
   CACHE               memory_io       0.457763         0.300314             0.064752                 0.120567                 0.056603           mixed
   MEMBW               memory_io       0.219752         0.521778             0.054974                 0.138140                 0.065356           mixed
     TLB               memory_io       0.286703         0.445267             0.072892                 0.162577                 0.032560           mixed
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
            tier0                    0.0                             0.0                           0.0                 0.30                    122.0                 660.0                 0.0                0.20                0.25           mixed
      tier0_tier1                    0.0                             0.0                           0.0                 0.45                    122.0                 550.0                 0.0                0.30                0.40           mixed
tier0_tier1_tier2                    0.0                             0.0                           0.0                 0.45                    122.0                 858.2                 0.0                0.25                0.35           mixed
```

## Files
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B120_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B120_a0.05_k3/config_runtime_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B120_a0.05_k3/run_context.json`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B120_a0.05_k3/case_inventory.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B120_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B120_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B120_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B120_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B120_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B120_a0.05_k3/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B120_a0.05_k3/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B120_a0.05_k3/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B120_a0.05_k3/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B120_a0.05_k3/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B120_a0.05_k3/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B120_a0.05_k3/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B120_a0.05_k3/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B120_a0.05_k3/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B120_a0.05_k3/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B120_a0.05_k3/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B120_a0.05_k3/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B120_a0.05_k3/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B120_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B120_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B120_a0.05_k3/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B120_a0.05_k3/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B120_a0.05_k3/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B120_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B120_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B120_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B120_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B120_a0.05_k3/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B120_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B120_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B120_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B120_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B120_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B120_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B120_a0.05_k3/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B120_a0.05_k3/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B120_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B120_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B120_a0.05_k3/figures/fig_detection_latency.png`
