# DICE Full Retrain Results

## Setup
- Feature profile: mixed ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_core_5hz.csv', 'tier2': 'tier2_core_5hz.csv'})
- Protocol: global, benign-only fit/calibration, block_B=90, alpha=0.05, persist_k=3, gain=0.1
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
          mixed             tier0       24          46          2.422984   0.7875 0.921899         1.0        1.0            0.0           0.30              0.011990              0.026694                      0.0                 0.014837
          mixed       tier0_tier1       24          57          2.991450   0.8125 0.940232         1.0        1.0            0.0           0.45              0.000042              0.000106                      0.0                 0.000055
          mixed tier0_tier1_tier2       24          64          3.223553   0.8250 0.947375         1.0        1.0            0.0           0.45              0.000046              0.000115                      0.0                 0.000057
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
          mixed   ATOMIC   0.8125 0.804167         1.0        1.0          0.000046          0.000100                  0.0             0.000057       2.156985      0.000054         57.512817         0.000057
          mixed   BRANCH   0.8750 0.887500         1.0        1.0          0.000046          0.000154                  0.0             0.000110       3.294865      0.000108        110.960521         0.000110
          mixed    CACHE   0.8125 0.804167         1.0        1.0          0.000046          0.000098                  0.0             0.000054       2.102494      0.000052         55.267549         0.000054
          mixed    MEMBW   0.8750 0.887500         1.0        1.0          0.000046          0.000157                  0.0             0.000090       3.366495      0.000111         91.348269         0.000090
          mixed      TLB   0.7500 0.679167         1.0        1.0          0.000046          0.000100                  0.0             0.000053       2.145543      0.000054         54.474031         0.000053
```

## Paper-style Aggregates (Final Config)
- Base score mean stressor AUC-PR (all five): **0.8125**
- Base score mean stressor ROC-AUC (all five): **0.8250**
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
            tier0       20      0.35       0.6          0.35  0.321429               0.022551                 0.016912           mixed
      tier0_tier1       20      0.25       0.5          0.25  0.165714               0.016127                 0.014359           mixed
tier0_tier1_tier2       20      0.30       0.7          0.30  0.274237               0.013597                 0.009472           mixed
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.15      0.50          0.15  0.151111               0.020194                 0.020269           mixed
      tier0_tier1       20      0.10      0.30          0.10  0.113333               0.042498                 0.019750           mixed
tier0_tier1_tier2       20      0.20      0.35          0.20  0.206667               0.040357                 0.022623           mixed
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20       0.2      0.50           0.2  0.180808               0.024125                 0.021510           mixed
      tier0_tier1       20       0.2      0.50           0.2  0.190000               0.018805                 0.016068           mixed
tier0_tier1_tier2       20       0.3      0.55           0.3  0.273810               0.014265                 0.011002           mixed
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.60      0.85      0.500000  0.421818               0.032658                 0.035832           mixed
      tier0_tier1       20      0.45      0.80      0.416667  0.335664               0.022386                 0.025161           mixed
tier0_tier1_tier2       20      0.55      0.70      0.527778  0.487302               0.021819                 0.022140           mixed
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.20      0.55        0.45          0.20  0.210808      0.60          0.40            0.250000            0.583333                0.233333            0.246667              -0.006411                 0.002514            0.017141              0.015516           0.011790       -0.016482           mixed
      tier0_tier1       20      0.25      0.50        0.40          0.25  0.200000      0.55          0.45            0.363636            0.454545                0.366667            0.274286               0.000909                 0.003781            0.020549              0.020196           0.008505        0.029110           mixed
tier0_tier1_tier2       20      0.15      0.70        0.40          0.15  0.130476      0.55          0.45            0.272727            0.727273                0.266667            0.226667               0.002201                 0.003207            0.020383              0.017764           0.013788        0.049679           mixed
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.20      0.45        0.45          0.20  0.200649       0.7           0.3            0.214286            0.428571                0.200000            0.190476              -0.009702                 0.014315            0.017141              0.015516           0.011790       -0.087669           mixed
      tier0_tier1       20      0.25      0.35        0.40          0.25  0.165035       0.6           0.4            0.250000            0.416667                0.233333            0.168889              -0.014062                -0.004465            0.020549              0.020196           0.008505       -0.081453           mixed
tier0_tier1_tier2       20      0.15      0.25        0.40          0.15  0.109091       0.7           0.3            0.142857            0.214286                0.100000            0.088889              -0.001936                 0.005024            0.020383              0.017764           0.013788       -0.017765           mixed
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained             -0.016482      14      0.70          0.30            0.214286            0.571429                0.200000            0.223810           mixed
            tier0  conf_0.00              0.000000      13      0.65          0.35            0.230769            0.538462                0.233333            0.257143           mixed
            tier0  conf_0.05              0.050000       7      0.35          0.65            0.285714            0.428571                0.333333            0.180000           mixed
            tier0  conf_0.10              0.100000       6      0.30          0.70            0.333333            0.500000                0.375000            0.200000           mixed
            tier0  conf_0.15              0.150000       4      0.20          0.80            0.500000            0.750000                0.500000            0.233333           mixed
            tier0  conf_0.20              0.200000       1      0.05          0.95            1.000000            1.000000                1.000000            0.200000           mixed
            tier0  conf_0.25              0.250000       1      0.05          0.95            1.000000            1.000000                1.000000            0.200000           mixed
      tier0_tier1  conf_0.00              0.000000      13      0.65          0.35            0.230769            0.461538                0.266667            0.168889           mixed
      tier0_tier1    trained              0.029110       9      0.45          0.55            0.222222            0.555556                0.266667            0.146667           mixed
      tier0_tier1  conf_0.05              0.050000       8      0.40          0.60            0.250000            0.500000                0.300000            0.180000           mixed
      tier0_tier1  conf_0.10              0.100000       5      0.25          0.75            0.200000            0.600000                0.200000            0.100000           mixed
      tier0_tier1  conf_0.15              0.150000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.20              0.200000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
      tier0_tier1  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
tier0_tier1_tier2  conf_0.00              0.000000      16      0.80          0.20            0.125000            0.687500                0.133333            0.106667           mixed
tier0_tier1_tier2    trained              0.049679       6      0.30          0.70            0.166667            0.666667                0.200000            0.066667           mixed
tier0_tier1_tier2  conf_0.05              0.050000       6      0.30          0.70            0.166667            0.666667                0.200000            0.066667           mixed
tier0_tier1_tier2  conf_0.10              0.100000       3      0.15          0.85            0.333333            0.666667                0.333333            0.100000           mixed
tier0_tier1_tier2  conf_0.15              0.150000       3      0.15          0.85            0.333333            0.666667                0.333333            0.100000           mixed
tier0_tier1_tier2  conf_0.20              0.200000       1      0.05          0.95            1.000000            1.000000                1.000000            0.200000           mixed
tier0_tier1_tier2  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained             -0.087669      14      0.70          0.30            0.214286            0.428571                0.200000            0.190476           mixed
            tier0  conf_0.00              0.000000      14      0.70          0.30            0.214286            0.428571                0.200000            0.190476           mixed
            tier0  conf_0.05              0.050000      12      0.60          0.40            0.250000            0.500000                0.266667            0.217143           mixed
            tier0  conf_0.10              0.100000       9      0.45          0.55            0.222222            0.444444                0.333333            0.200000           mixed
            tier0  conf_0.15              0.150000       3      0.15          0.85            0.666667            1.000000                0.750000            0.333333           mixed
            tier0  conf_0.20              0.200000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
            tier0  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
      tier0_tier1    trained             -0.081453      12      0.60          0.40            0.250000            0.416667                0.233333            0.180952           mixed
      tier0_tier1  conf_0.00              0.000000       9      0.45          0.55            0.111111            0.222222                0.125000            0.100000           mixed
      tier0_tier1  conf_0.05              0.050000       6      0.30          0.70            0.000000            0.166667                0.000000            0.000000           mixed
      tier0_tier1  conf_0.10              0.100000       6      0.30          0.70            0.000000            0.166667                0.000000            0.000000           mixed
      tier0_tier1  conf_0.15              0.150000       4      0.20          0.80            0.000000            0.250000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.20              0.200000       3      0.15          0.85            0.000000            0.333333                0.000000            0.000000           mixed
      tier0_tier1  conf_0.25              0.250000       3      0.15          0.85            0.000000            0.333333                0.000000            0.000000           mixed
tier0_tier1_tier2    trained             -0.017765      14      0.70          0.30            0.142857            0.214286                0.100000            0.100000           mixed
tier0_tier1_tier2  conf_0.00              0.000000      13      0.65          0.35            0.153846            0.153846                0.100000            0.114286           mixed
tier0_tier1_tier2  conf_0.05              0.050000       9      0.45          0.55            0.000000            0.000000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.10              0.100000       8      0.40          0.60            0.000000            0.000000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.15              0.150000       4      0.20          0.80            0.000000            0.000000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.20              0.200000       3      0.15          0.85            0.000000            0.000000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.25              0.250000       2      0.10          0.90            0.000000            0.000000                0.000000            0.000000           mixed
```

## Diagnosis Mode Comparison
- Whole-run and post-alert-window diagnosis are exported together so the diagnosis mode can be evaluated directly.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile diagnosis_target    diagnosis_mode  family_acc  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau                       status  min_class_count  min_group_count    group_key  include_workload
            tier0       20      0.35      0.60      0.350000  0.321429               0.022551                 0.016912           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.25      0.50      0.250000  0.165714               0.016127                 0.014359           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.30      0.70      0.300000  0.274237               0.013597                 0.009472           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.15      0.50      0.150000  0.151111               0.020194                 0.020269           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.10      0.30      0.100000  0.113333               0.042498                 0.019750           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.20      0.35      0.200000  0.206667               0.040357                 0.022623           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.20      0.55      0.200000  0.210808              -0.006411                 0.002514           mixed     hierarchical         whole_run        0.45      0.60          0.40            0.250000            0.583333                0.233333            0.246667            0.017141              0.015516           0.011790       -0.016482                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.25      0.50      0.250000  0.200000               0.000909                 0.003781           mixed     hierarchical         whole_run        0.40      0.55          0.45            0.363636            0.454545                0.366667            0.274286            0.020549              0.020196           0.008505        0.029110                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.15      0.70      0.150000  0.130476               0.002201                 0.003207           mixed     hierarchical         whole_run        0.40      0.55          0.45            0.272727            0.727273                0.266667            0.226667            0.020383              0.017764           0.013788        0.049679                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.20      0.45      0.200000  0.200649              -0.009702                 0.014315           mixed     hierarchical post_alert_window        0.45      0.70          0.30            0.214286            0.428571                0.200000            0.190476            0.017141              0.015516           0.011790       -0.087669                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.25      0.35      0.250000  0.165035              -0.014062                -0.004465           mixed     hierarchical post_alert_window        0.40      0.60          0.40            0.250000            0.416667                0.233333            0.168889            0.020549              0.020196           0.008505       -0.081453                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.15      0.25      0.150000  0.109091              -0.001936                 0.005024           mixed     hierarchical post_alert_window        0.40      0.70          0.30            0.142857            0.214286                0.100000            0.088889            0.020383              0.017764           0.013788       -0.017765                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.60      0.85      0.500000  0.421818               0.032658                 0.035832           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.45      0.80      0.416667  0.335664               0.022386                 0.025161           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.55      0.70      0.527778  0.487302               0.021819                 0.022140           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.692346         0.170034     0.137621              tier0           mixed
  BRANCH     0.770036         0.097270     0.132694              tier0           mixed
   CACHE     0.546836         0.357463     0.095701              tier0           mixed
   MEMBW     0.792702         0.100979     0.106318              tier0           mixed
     TLB     0.708246         0.152522     0.139232              tier0           mixed
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC               memory_io       0.266812         0.406400             0.101099                 0.186763                 0.038927           mixed
  BRANCH               memory_io       0.240361         0.481557             0.051830                 0.174112                 0.052141           mixed
   CACHE                 compute       0.467672         0.282975             0.067467                 0.122818                 0.059068           mixed
   MEMBW               memory_io       0.233914         0.495440             0.056297                 0.146492                 0.067858           mixed
     TLB               memory_io       0.294226         0.422818             0.079316                 0.169315                 0.034325           mixed
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
            tier0                    0.0                             0.0                           0.0                 0.30                     95.5                 768.5                 0.2                 0.2                 0.2           mixed
      tier0_tier1                    0.0                             0.0                           0.0                 0.45                     92.0                 625.0                 0.3                 0.3                 0.4           mixed
tier0_tier1_tier2                    0.0                             0.0                           0.0                 0.45                     92.0                 548.8                 0.3                 0.3                 0.4           mixed
```

## Files
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B90_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B90_a0.05_k3/config_runtime_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B90_a0.05_k3/run_context.json`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B90_a0.05_k3/case_inventory.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B90_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B90_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B90_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B90_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B90_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B90_a0.05_k3/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B90_a0.05_k3/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B90_a0.05_k3/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B90_a0.05_k3/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B90_a0.05_k3/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B90_a0.05_k3/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B90_a0.05_k3/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B90_a0.05_k3/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B90_a0.05_k3/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B90_a0.05_k3/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B90_a0.05_k3/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B90_a0.05_k3/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B90_a0.05_k3/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B90_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B90_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B90_a0.05_k3/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B90_a0.05_k3/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B90_a0.05_k3/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B90_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B90_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B90_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B90_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B90_a0.05_k3/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B90_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B90_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B90_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B90_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B90_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B90_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B90_a0.05_k3/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B90_a0.05_k3/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B90_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B90_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B90_a0.05_k3/figures/fig_detection_latency.png`
