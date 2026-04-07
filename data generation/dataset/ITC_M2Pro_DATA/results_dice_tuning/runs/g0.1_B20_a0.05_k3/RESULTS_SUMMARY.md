# DICE Full Retrain Results

## Setup
- Feature profile: mixed ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_core_5hz.csv', 'tier2': 'tier2_core_5hz.csv'})
- Protocol: global, benign-only fit/calibration, block_B=20, alpha=0.05, persist_k=3, gain=0.1
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
          mixed             tier0       24          46          2.466143   0.7750 0.919734         1.0        1.0           0.25           0.35              0.015544              0.031791                      0.0                 0.016567
          mixed       tier0_tier1       24          57          2.844188   0.8375 0.960040         1.0        1.0           0.25           0.65              0.000046              0.000111                      0.0                 0.000046
          mixed tier0_tier1_tier2       24          64          3.323650   0.8625 0.966561         1.0        1.0           0.25           0.70              0.000048              0.000119                      0.0                 0.000056
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
          mixed   ATOMIC   0.7500 0.770833         1.0        1.0          0.000048          0.000090                  0.0             0.000031       1.855192      0.000042         32.499921         0.000031
          mixed   BRANCH   0.9375 0.950000         1.0        1.0          0.000048          0.000176                  0.0             0.000128       3.617638      0.000128        128.522829         0.000128
          mixed    CACHE   0.8750 0.887500         1.0        1.0          0.000048          0.000105                  0.0             0.000059       2.151560      0.000056         59.887528         0.000059
          mixed    MEMBW   0.9375 0.950000         1.0        1.0          0.000048          0.000136                  0.0             0.000076       2.800264      0.000088         76.962551         0.000076
          mixed      TLB   0.8125 0.804167         1.0        1.0          0.000048          0.000092                  0.0             0.000043       1.887477      0.000044         44.081982         0.000043
```

## Paper-style Aggregates (Final Config)
- Base score mean stressor AUC-PR (all five): **0.8725**
- Base score mean stressor ROC-AUC (all five): **0.8625**
- WC score mean stressor AUC-PR (all five): **1.0000**
- WC score mean stressor ROC-AUC (all five): **1.0000**
- Base score mean stressor AUC-PR (excluding BRANCH/TLB): **0.8694**
- Base score mean stressor ROC-AUC (excluding BRANCH/TLB): **0.8542**
- WC score mean stressor AUC-PR (excluding BRANCH/TLB): **1.0000**
- WC score mean stressor ROC-AUC (excluding BRANCH/TLB): **1.0000**

## Diagnosis
- Feature-level diagnosis uses normalized whole-run residual-attribution prototypes as the default paper-facing result, with diagnosis-only filtering that removes monotonic counters and downweights generic memory-state features.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20       0.3       0.5           0.3  0.252727               0.023169                 0.013994           mixed
      tier0_tier1       20       0.2       0.6           0.2  0.141538               0.015968                 0.016441           mixed
tier0_tier1_tier2       20       0.4       0.8           0.4  0.412698               0.013529                 0.014401           mixed
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.30      0.60          0.30  0.260678               0.013100                 0.008894           mixed
      tier0_tier1       20      0.10      0.30          0.10  0.057143               0.096955                 0.039756           mixed
tier0_tier1_tier2       20      0.05      0.35          0.05  0.066667               0.100092                 0.026248           mixed
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.35      0.55          0.35  0.350649               0.017861                 0.012884           mixed
      tier0_tier1       20      0.20      0.55          0.20  0.214141               0.020233                 0.015488           mixed
tier0_tier1_tier2       20      0.25      0.60          0.25  0.225397               0.016706                 0.014024           mixed
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.55      0.90      0.527778  0.434343               0.033342                 0.041977           mixed
      tier0_tier1       20      0.50      0.75      0.444444  0.356745               0.020891                 0.018331           mixed
tier0_tier1_tier2       20      0.50      0.70      0.500000  0.449084               0.020834                 0.018464           mixed
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.35      0.50        0.45          0.35  0.273535      0.40          0.60            0.500000            0.500000                0.400000            0.274286               0.005354                 0.006796            0.016357              0.014942           0.013009        0.124782           mixed
      tier0_tier1       20      0.30      0.55        0.40          0.30  0.237296      0.50          0.50            0.400000            0.700000                0.466667            0.327619              -0.005856                -0.000222            0.027478              0.028051           0.013125        0.001014           mixed
tier0_tier1_tier2       20      0.30      0.75        0.35          0.30  0.296061      0.45          0.55            0.333333            0.888889                0.400000            0.313333               0.003126                 0.004583            0.024411              0.024726           0.015086        0.081106           mixed
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.40      0.75        0.45          0.40  0.387143      0.55          0.45            0.363636            0.636364                0.466667            0.370476              -0.014445                 0.003167            0.016357              0.014942           0.013009       -0.060356           mixed
      tier0_tier1       20      0.30      0.35        0.40          0.30  0.185714      0.70          0.30            0.428571            0.500000                0.350000            0.253333              -0.099147                -0.032376            0.027478              0.028051           0.013125       -0.228956           mixed
tier0_tier1_tier2       20      0.15      0.30        0.35          0.15  0.106667      0.60          0.40            0.000000            0.250000                0.000000            0.000000               0.020547                 0.002547            0.024411              0.024726           0.015086       -0.023268           mixed
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0  conf_0.00              0.000000      15      0.75          0.25            0.333333            0.400000                0.350000            0.242424           mixed
            tier0  conf_0.05              0.050000      10      0.50          0.50            0.500000            0.500000                0.350000            0.293333           mixed
            tier0  conf_0.10              0.100000       6      0.30          0.70            0.500000            0.500000                0.400000            0.260000           mixed
            tier0    trained              0.124782       5      0.25          0.75            0.600000            0.600000                0.500000            0.293333           mixed
            tier0  conf_0.15              0.150000       5      0.25          0.75            0.600000            0.600000                0.500000            0.293333           mixed
            tier0  conf_0.20              0.200000       3      0.15          0.85            0.666667            0.666667                0.500000            0.200000           mixed
            tier0  conf_0.25              0.250000       3      0.15          0.85            0.666667            0.666667                0.500000            0.200000           mixed
      tier0_tier1  conf_0.00              0.000000      11      0.55          0.45            0.272727            0.545455                0.366667            0.270476           mixed
      tier0_tier1    trained              0.001014      11      0.55          0.45            0.272727            0.545455                0.366667            0.270476           mixed
      tier0_tier1  conf_0.05              0.050000       6      0.30          0.70            0.333333            0.666667                0.444444            0.166667           mixed
      tier0_tier1  conf_0.10              0.100000       5      0.25          0.75            0.200000            0.600000                0.333333            0.066667           mixed
      tier0_tier1  conf_0.15              0.150000       2      0.10          0.90            0.500000            1.000000                0.500000            0.133333           mixed
      tier0_tier1  conf_0.20              0.200000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
      tier0_tier1  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
tier0_tier1_tier2  conf_0.00              0.000000      16      0.80          0.20            0.312500            0.750000                0.300000            0.297619           mixed
tier0_tier1_tier2  conf_0.05              0.050000       8      0.40          0.60            0.250000            0.750000                0.200000            0.190476           mixed
tier0_tier1_tier2    trained              0.081106       5      0.25          0.75            0.200000            0.600000                0.250000            0.080000           mixed
tier0_tier1_tier2  conf_0.10              0.100000       3      0.15          0.85            0.333333            0.666667                0.333333            0.100000           mixed
tier0_tier1_tier2  conf_0.15              0.150000       1      0.05          0.95            1.000000            1.000000                1.000000            0.200000           mixed
tier0_tier1_tier2  conf_0.20              0.200000       1      0.05          0.95            1.000000            1.000000                1.000000            0.200000           mixed
tier0_tier1_tier2  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained             -0.060356      13      0.65          0.35            0.307692            0.692308                0.312500            0.222222           mixed
            tier0  conf_0.00              0.000000      13      0.65          0.35            0.307692            0.692308                0.312500            0.222222           mixed
            tier0  conf_0.05              0.050000       6      0.30          0.70            0.333333            0.500000                0.375000            0.266667           mixed
            tier0  conf_0.10              0.100000       3      0.15          0.85            0.333333            0.333333                0.250000            0.133333           mixed
            tier0  conf_0.15              0.150000       1      0.05          0.95            1.000000            1.000000                1.000000            0.200000           mixed
            tier0  conf_0.20              0.200000       1      0.05          0.95            1.000000            1.000000                1.000000            0.200000           mixed
            tier0  conf_0.25              0.250000       1      0.05          0.95            1.000000            1.000000                1.000000            0.200000           mixed
      tier0_tier1    trained             -0.228956      15      0.75          0.25            0.400000            0.466667                0.350000            0.240000           mixed
      tier0_tier1  conf_0.00              0.000000       7      0.35          0.65            0.142857            0.142857                0.333333            0.080000           mixed
      tier0_tier1  conf_0.05              0.050000       4      0.20          0.80            0.000000            0.000000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.10              0.100000       4      0.20          0.80            0.000000            0.000000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.15              0.150000       3      0.15          0.85            0.000000            0.000000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.20              0.200000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
tier0_tier1_tier2    trained             -0.023268      12      0.60          0.40            0.000000            0.250000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.00              0.000000      12      0.60          0.40            0.000000            0.250000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.05              0.050000       7      0.35          0.65            0.000000            0.285714                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.10              0.100000       6      0.30          0.70            0.000000            0.333333                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.15              0.150000       4      0.20          0.80            0.000000            0.500000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.20              0.200000       4      0.20          0.80            0.000000            0.500000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.25              0.250000       4      0.20          0.80            0.000000            0.500000                0.000000            0.000000           mixed
```

## Diagnosis Mode Comparison
- Whole-run and post-alert-window diagnosis are exported together so the diagnosis mode can be evaluated directly.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile diagnosis_target    diagnosis_mode  family_acc  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau                       status  min_class_count  min_group_count    group_key  include_workload
            tier0       20      0.30      0.50      0.300000  0.252727               0.023169                 0.013994           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.20      0.60      0.200000  0.141538               0.015968                 0.016441           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.40      0.80      0.400000  0.412698               0.013529                 0.014401           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.30      0.60      0.300000  0.260678               0.013100                 0.008894           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.10      0.30      0.100000  0.057143               0.096955                 0.039756           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.05      0.35      0.050000  0.066667               0.100092                 0.026248           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.35      0.50      0.350000  0.273535               0.005354                 0.006796           mixed     hierarchical         whole_run        0.45      0.40          0.60            0.500000            0.500000                0.400000            0.274286            0.016357              0.014942           0.013009        0.124782                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.30      0.55      0.300000  0.237296              -0.005856                -0.000222           mixed     hierarchical         whole_run        0.40      0.50          0.50            0.400000            0.700000                0.466667            0.327619            0.027478              0.028051           0.013125        0.001014                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.30      0.75      0.300000  0.296061               0.003126                 0.004583           mixed     hierarchical         whole_run        0.35      0.45          0.55            0.333333            0.888889                0.400000            0.313333            0.024411              0.024726           0.015086        0.081106                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.40      0.75      0.400000  0.387143              -0.014445                 0.003167           mixed     hierarchical post_alert_window        0.45      0.55          0.45            0.363636            0.636364                0.466667            0.370476            0.016357              0.014942           0.013009       -0.060356                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.30      0.35      0.300000  0.185714              -0.099147                -0.032376           mixed     hierarchical post_alert_window        0.40      0.70          0.30            0.428571            0.500000                0.350000            0.253333            0.027478              0.028051           0.013125       -0.228956                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.15      0.30      0.150000  0.106667               0.020547                 0.002547           mixed     hierarchical post_alert_window        0.35      0.60          0.40            0.000000            0.250000                0.000000            0.000000            0.024411              0.024726           0.015086       -0.023268                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.55      0.90      0.527778  0.434343               0.033342                 0.041977           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.50      0.75      0.444444  0.356745               0.020891                 0.018331           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.50      0.70      0.500000  0.449084               0.020834                 0.018464           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.665601         0.176286     0.158114              tier0           mixed
  BRANCH     0.739443         0.099424     0.161133              tier0           mixed
   CACHE     0.524488         0.363048     0.112464              tier0           mixed
   MEMBW     0.760548         0.103140     0.136312              tier0           mixed
     TLB     0.670449         0.159734     0.169818              tier0           mixed
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC               memory_io       0.272733         0.369736             0.115627                 0.211112                 0.030792           mixed
  BRANCH               memory_io       0.255539         0.430103             0.058353                 0.209586                 0.046420           mixed
   CACHE                 compute       0.480693         0.247055             0.077496                 0.143498                 0.051258           mixed
   MEMBW               memory_io       0.251915         0.440287             0.063841                 0.183052                 0.060905           mixed
     TLB               memory_io       0.308037         0.364120             0.093756                 0.204238                 0.029849           mixed
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
            tier0                   0.25                        2.755102                      4.591837                 0.35                     33.0                 377.8                0.30                0.30                0.30           mixed
      tier0_tier1                   0.25                        2.755102                      4.591837                 0.65                     33.0                 897.8                0.40                0.40                0.50           mixed
tier0_tier1_tier2                   0.25                        2.755102                      4.591837                 0.70                     36.0                 854.8                0.45                0.45                0.55           mixed
```

## Files
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B20_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B20_a0.05_k3/config_runtime_summary.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B20_a0.05_k3/run_context.json`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B20_a0.05_k3/case_inventory.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B20_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B20_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B20_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B20_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B20_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B20_a0.05_k3/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B20_a0.05_k3/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B20_a0.05_k3/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B20_a0.05_k3/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B20_a0.05_k3/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B20_a0.05_k3/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B20_a0.05_k3/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B20_a0.05_k3/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B20_a0.05_k3/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B20_a0.05_k3/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B20_a0.05_k3/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B20_a0.05_k3/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B20_a0.05_k3/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B20_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B20_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B20_a0.05_k3/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B20_a0.05_k3/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B20_a0.05_k3/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B20_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B20_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B20_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B20_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B20_a0.05_k3/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B20_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B20_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B20_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B20_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B20_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B20_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B20_a0.05_k3/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B20_a0.05_k3/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B20_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B20_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B20_a0.05_k3/figures/fig_detection_latency.png`
