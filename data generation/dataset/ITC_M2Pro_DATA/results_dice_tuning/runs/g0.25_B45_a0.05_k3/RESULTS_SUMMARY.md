# DICE Full Retrain Results

## Setup
- Feature profile: mixed ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_core_5hz.csv', 'tier2': 'tier2_core_5hz.csv'})
- Protocol: global, benign-only fit/calibration, block_B=45, alpha=0.05, persist_k=3, gain=0.25
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
          mixed             tier0       24          46          2.353312   0.8125 0.940232         1.0        1.0            0.0            0.3              0.007649              0.015906                      0.0                 0.008537
          mixed       tier0_tier1       24          57          3.194008   0.8375 0.957016         1.0        1.0            0.0            0.5              0.000045              0.000111                      0.0                 0.000052
          mixed tier0_tier1_tier2       24          64          3.241024   0.8375 0.957016         1.0        1.0            0.0            0.5              0.000047              0.000119                      0.0                 0.000058
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
          mixed   ATOMIC   0.7500 0.770833         1.0        1.0          0.000047          0.000095                  0.0             0.000050       1.974880      0.000047         51.127665         0.000050
          mixed   BRANCH   0.9375 0.950000         1.0        1.0          0.000047          0.000188                  0.0             0.000128       3.894489      0.000140        129.139092         0.000128
          mixed    CACHE   0.8125 0.804167         1.0        1.0          0.000047          0.000097                  0.0             0.000058       2.031066      0.000050         58.672651         0.000058
          mixed    MEMBW   0.9375 0.950000         1.0        1.0          0.000047          0.000157                  0.0             0.000089       3.253036      0.000109         90.204820         0.000089
          mixed      TLB   0.7500 0.679167         1.0        1.0          0.000047          0.000110                  0.0             0.000051       2.282392      0.000062         52.248331         0.000051
```

## Paper-style Aggregates (Final Config)
- Base score mean stressor AUC-PR (all five): **0.8308**
- Base score mean stressor ROC-AUC (all five): **0.8375**
- WC score mean stressor AUC-PR (all five): **1.0000**
- WC score mean stressor ROC-AUC (all five): **1.0000**
- Base score mean stressor AUC-PR (excluding BRANCH/TLB): **0.8417**
- Base score mean stressor ROC-AUC (excluding BRANCH/TLB): **0.8333**
- WC score mean stressor AUC-PR (excluding BRANCH/TLB): **1.0000**
- WC score mean stressor ROC-AUC (excluding BRANCH/TLB): **1.0000**

## Diagnosis
- Feature-level diagnosis uses normalized whole-run residual-attribution prototypes as the default paper-facing result, with diagnosis-only filtering that removes monotonic counters and downweights generic memory-state features.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.30      0.55          0.30  0.238961               0.026338                 0.020373           mixed
      tier0_tier1       20      0.30      0.70          0.30  0.216117               0.020276                 0.016724           mixed
tier0_tier1_tier2       20      0.55      0.70          0.55  0.553260               0.019271                 0.016577           mixed
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.15      0.55          0.15  0.113333               0.016387                 0.009409           mixed
      tier0_tier1       20      0.15      0.25          0.15  0.118681               0.082632                 0.057340           mixed
tier0_tier1_tier2       20      0.15      0.45          0.15  0.150649               0.062709                 0.021101           mixed
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.25      0.70          0.25  0.223333               0.013553                 0.008810           mixed
      tier0_tier1       20      0.35      0.65          0.35  0.335931               0.012289                 0.007855           mixed
tier0_tier1_tier2       20      0.45      0.60          0.45  0.444444               0.011146                 0.007614           mixed
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.55      0.80      0.472222  0.398551               0.033323                 0.034916           mixed
      tier0_tier1       20      0.50      0.75      0.444444  0.356745               0.025680                 0.029230           mixed
tier0_tier1_tier2       20      0.55      0.75      0.583333  0.531039               0.026703                 0.028362           mixed
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.40      0.65        0.45          0.40  0.318182      0.35          0.65            0.571429            0.857143                0.416667            0.274286              -0.010578                -0.008828            0.014524              0.015935           0.013378        0.106067           mixed
      tier0_tier1       20      0.25      0.70        0.50          0.25  0.201616      0.55          0.45            0.363636            0.727273                0.466667            0.280952               0.004972                 0.005556            0.020290              0.017518           0.017363        0.028751           mixed
tier0_tier1_tier2       20      0.45      0.70        0.30          0.45  0.423810      0.40          0.60            0.625000            1.000000                0.500000            0.438095               0.007374                 0.007074            0.020148              0.013558           0.020589        0.124988           mixed
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.35      0.60        0.45          0.35  0.296537      0.45          0.55            0.222222            0.444444                0.133333            0.146667              -0.018654                -0.002906            0.014524              0.015935           0.013378       -0.081446           mixed
      tier0_tier1       20      0.25      0.30        0.50          0.25  0.175758      0.65          0.35            0.230769            0.230769                0.233333            0.188889              -0.014220                 0.004399            0.020290              0.017518           0.017363       -0.083350           mixed
tier0_tier1_tier2       20      0.15      0.45        0.30          0.15  0.112727      0.30          0.70            0.000000            0.166667                0.000000            0.000000               0.001796                 0.011053            0.020148              0.013558           0.020589        0.263435           mixed
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0  conf_0.00              0.000000      10      0.50          0.50            0.400000            0.700000                0.333333            0.247619           mixed
            tier0  conf_0.05              0.050000       8      0.40          0.60            0.500000            0.750000                0.416667            0.247619           mixed
            tier0  conf_0.10              0.100000       6      0.30          0.70            0.500000            0.666667                0.375000            0.233333           mixed
            tier0    trained              0.106067       6      0.30          0.70            0.500000            0.666667                0.375000            0.233333           mixed
            tier0  conf_0.15              0.150000       4      0.20          0.80            0.500000            0.750000                0.333333            0.133333           mixed
            tier0  conf_0.20              0.200000       3      0.15          0.85            0.666667            1.000000                0.500000            0.160000           mixed
            tier0  conf_0.25              0.250000       2      0.10          0.90            1.000000            1.000000                1.000000            0.200000           mixed
      tier0_tier1  conf_0.00              0.000000      14      0.70          0.30            0.214286            0.642857                0.233333            0.138889           mixed
      tier0_tier1    trained              0.028751      10      0.50          0.50            0.300000            0.600000                0.400000            0.180000           mixed
      tier0_tier1  conf_0.05              0.050000       9      0.45          0.55            0.333333            0.555556                0.400000            0.200000           mixed
      tier0_tier1  conf_0.10              0.100000       7      0.35          0.65            0.285714            0.571429                0.400000            0.200000           mixed
      tier0_tier1  conf_0.15              0.150000       5      0.25          0.75            0.200000            0.400000                0.333333            0.066667           mixed
      tier0_tier1  conf_0.20              0.200000       3      0.15          0.85            0.333333            0.666667                0.333333            0.100000           mixed
      tier0_tier1  conf_0.25              0.250000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.00              0.000000      15      0.75          0.25            0.533333            0.666667                0.600000            0.529091           mixed
tier0_tier1_tier2  conf_0.05              0.050000       9      0.45          0.55            0.555556            0.666667                0.583333            0.420000           mixed
tier0_tier1_tier2  conf_0.10              0.100000       5      0.25          0.75            0.400000            0.600000                0.333333            0.114286           mixed
tier0_tier1_tier2    trained              0.124988       5      0.25          0.75            0.400000            0.600000                0.333333            0.114286           mixed
tier0_tier1_tier2  conf_0.15              0.150000       5      0.25          0.75            0.400000            0.600000                0.333333            0.114286           mixed
tier0_tier1_tier2  conf_0.20              0.200000       4      0.20          0.80            0.500000            0.750000                0.333333            0.133333           mixed
tier0_tier1_tier2  conf_0.25              0.250000       1      0.05          0.95            1.000000            1.000000                1.000000            0.200000           mixed
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained             -0.081446      12      0.60          0.40            0.333333            0.583333                0.333333            0.293333           mixed
            tier0  conf_0.00              0.000000      11      0.55          0.45            0.272727            0.545455                0.233333            0.226667           mixed
            tier0  conf_0.05              0.050000       5      0.25          0.75            0.200000            0.400000                0.166667            0.100000           mixed
            tier0  conf_0.10              0.100000       4      0.20          0.80            0.250000            0.250000                0.333333            0.133333           mixed
            tier0  conf_0.15              0.150000       4      0.20          0.80            0.250000            0.250000                0.333333            0.133333           mixed
            tier0  conf_0.20              0.200000       3      0.15          0.85            0.333333            0.333333                0.500000            0.200000           mixed
            tier0  conf_0.25              0.250000       2      0.10          0.90            0.000000            0.000000                0.000000            0.000000           mixed
      tier0_tier1    trained             -0.083350      13      0.65          0.35            0.230769            0.230769                0.233333            0.188889           mixed
      tier0_tier1  conf_0.00              0.000000      12      0.60          0.40            0.166667            0.166667                0.200000            0.157143           mixed
      tier0_tier1  conf_0.05              0.050000       9      0.45          0.55            0.111111            0.111111                0.200000            0.066667           mixed
      tier0_tier1  conf_0.10              0.100000       9      0.45          0.55            0.111111            0.111111                0.200000            0.066667           mixed
      tier0_tier1  conf_0.15              0.150000       7      0.35          0.65            0.000000            0.000000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.20              0.200000       5      0.25          0.75            0.000000            0.000000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.25              0.250000       5      0.25          0.75            0.000000            0.000000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.00              0.000000      14      0.70          0.30            0.142857            0.428571                0.116667            0.116667           mixed
tier0_tier1_tier2  conf_0.05              0.050000      10      0.50          0.50            0.000000            0.400000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.10              0.100000       5      0.25          0.75            0.000000            0.400000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.15              0.150000       5      0.25          0.75            0.000000            0.400000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.20              0.200000       4      0.20          0.80            0.000000            0.500000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.25              0.250000       4      0.20          0.80            0.000000            0.500000                0.000000            0.000000           mixed
tier0_tier1_tier2    trained              0.263435       4      0.20          0.80            0.000000            0.500000                0.000000            0.000000           mixed
```

## Diagnosis Mode Comparison
- Whole-run and post-alert-window diagnosis are exported together so the diagnosis mode can be evaluated directly.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile diagnosis_target    diagnosis_mode  family_acc  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau                       status  min_class_count  min_group_count    group_key  include_workload
            tier0       20      0.30      0.55      0.300000  0.238961               0.026338                 0.020373           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.30      0.70      0.300000  0.216117               0.020276                 0.016724           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.55      0.70      0.550000  0.553260               0.019271                 0.016577           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.15      0.55      0.150000  0.113333               0.016387                 0.009409           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.15      0.25      0.150000  0.118681               0.082632                 0.057340           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.15      0.45      0.150000  0.150649               0.062709                 0.021101           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.40      0.65      0.400000  0.318182              -0.010578                -0.008828           mixed     hierarchical         whole_run        0.45      0.35          0.65            0.571429            0.857143                0.416667            0.274286            0.014524              0.015935           0.013378        0.106067                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.25      0.70      0.250000  0.201616               0.004972                 0.005556           mixed     hierarchical         whole_run        0.50      0.55          0.45            0.363636            0.727273                0.466667            0.280952            0.020290              0.017518           0.017363        0.028751                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.45      0.70      0.450000  0.423810               0.007374                 0.007074           mixed     hierarchical         whole_run        0.30      0.40          0.60            0.625000            1.000000                0.500000            0.438095            0.020148              0.013558           0.020589        0.124988                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.35      0.60      0.350000  0.296537              -0.018654                -0.002906           mixed     hierarchical post_alert_window        0.45      0.45          0.55            0.222222            0.444444                0.133333            0.146667            0.014524              0.015935           0.013378       -0.081446                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.25      0.30      0.250000  0.175758              -0.014220                 0.004399           mixed     hierarchical post_alert_window        0.50      0.65          0.35            0.230769            0.230769                0.233333            0.188889            0.020290              0.017518           0.017363       -0.083350                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.15      0.45      0.150000  0.112727               0.001796                 0.011053           mixed     hierarchical post_alert_window        0.30      0.30          0.70            0.000000            0.166667                0.000000            0.000000            0.020148              0.013558           0.020589        0.263435                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.55      0.80      0.472222  0.398551               0.033323                 0.034916           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.50      0.75      0.444444  0.356745               0.025680                 0.029230           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.55      0.75      0.583333  0.531039               0.026703                 0.028362           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.707212         0.140407     0.152381              tier0           mixed
  BRANCH     0.767655         0.087950     0.144394              tier0           mixed
   CACHE     0.543268         0.351438     0.105294              tier0           mixed
   MEMBW     0.784100         0.094965     0.120935              tier0           mixed
     TLB     0.706677         0.137987     0.155336              tier0           mixed
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC               memory_io       0.263485         0.405715             0.087017                 0.210435                 0.033348           mixed
  BRANCH               memory_io       0.243181         0.467882             0.049441                 0.195016                 0.044481           mixed
   CACHE               memory_io       0.464158         0.280200             0.067204                 0.140934                 0.047505           mixed
   MEMBW               memory_io       0.230084         0.489533             0.056291                 0.167447                 0.056644           mixed
     TLB               memory_io       0.299008         0.402442             0.075206                 0.194993                 0.028350           mixed
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
            tier0                    0.0                             0.0                           0.0                  0.3                     64.0                 619.0                 0.2                 0.2                0.25           mixed
      tier0_tier1                    0.0                             0.0                           0.0                  0.5                     65.0                 836.4                 0.3                 0.3                0.40           mixed
tier0_tier1_tier2                    0.0                             0.0                           0.0                  0.5                     63.5                 834.6                 0.3                 0.3                0.40           mixed
```

## Files
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B45_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B45_a0.05_k3/config_runtime_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B45_a0.05_k3/run_context.json`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B45_a0.05_k3/case_inventory.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B45_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B45_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B45_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B45_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B45_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B45_a0.05_k3/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B45_a0.05_k3/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B45_a0.05_k3/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B45_a0.05_k3/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B45_a0.05_k3/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B45_a0.05_k3/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B45_a0.05_k3/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B45_a0.05_k3/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B45_a0.05_k3/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B45_a0.05_k3/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B45_a0.05_k3/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B45_a0.05_k3/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B45_a0.05_k3/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B45_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B45_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B45_a0.05_k3/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B45_a0.05_k3/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B45_a0.05_k3/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B45_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B45_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B45_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B45_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B45_a0.05_k3/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B45_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B45_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B45_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B45_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B45_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B45_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B45_a0.05_k3/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B45_a0.05_k3/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B45_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B45_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B45_a0.05_k3/figures/fig_detection_latency.png`
