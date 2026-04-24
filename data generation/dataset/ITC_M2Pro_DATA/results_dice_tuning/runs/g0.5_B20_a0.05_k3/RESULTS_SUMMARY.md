# DICE Full Retrain Results

## Setup
- Feature profile: mixed ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_core_5hz.csv', 'tier2': 'tier2_core_5hz.csv'})
- Protocol: global, benign-only fit/calibration, block_B=20, alpha=0.05, persist_k=3, gain=0.5
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
          mixed             tier0       24          46          2.449419   0.7500 0.904972         1.0        1.0           0.25           0.35              0.005420              0.010185                      0.0                 0.005339
          mixed       tier0_tier1       24          57          2.926400   0.7875 0.940972         1.0        1.0           0.25           0.60              0.000059              0.000121                      0.0                 0.000055
          mixed tier0_tier1_tier2       24          64          3.697687   0.8000 0.947222         1.0        1.0           0.25           0.65              0.000062              0.000129                      0.0                 0.000060
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
          mixed   ATOMIC   0.6875 0.747024         1.0        1.0          0.000062          0.000097                  0.0             0.000043       1.551213      0.000035         43.979848         0.000043
          mixed   BRANCH   0.9375 0.950000         1.0        1.0          0.000062          0.000190                  0.0             0.000108       3.020297      0.000128        108.974138         0.000108
          mixed    CACHE   0.7500 0.770833         1.0        1.0          0.000062          0.000118                  0.0             0.000074       1.875413      0.000055         74.907667         0.000074
          mixed    MEMBW   0.8125 0.804167         1.0        1.0          0.000062          0.000146                  0.0             0.000069       2.319179      0.000084         69.612383         0.000069
          mixed      TLB   0.8125 0.804167         1.0        1.0          0.000062          0.000101                  0.0             0.000045       1.612738      0.000039         45.518116         0.000045
```

## Paper-style Aggregates (Final Config)
- Base score mean stressor AUC-PR (all five): **0.8152**
- Base score mean stressor ROC-AUC (all five): **0.8000**
- WC score mean stressor AUC-PR (all five): **1.0000**
- WC score mean stressor ROC-AUC (all five): **1.0000**
- Base score mean stressor AUC-PR (excluding BRANCH/TLB): **0.7740**
- Base score mean stressor ROC-AUC (excluding BRANCH/TLB): **0.7500**
- WC score mean stressor AUC-PR (excluding BRANCH/TLB): **1.0000**
- WC score mean stressor ROC-AUC (excluding BRANCH/TLB): **1.0000**

## Diagnosis
- Feature-level diagnosis uses normalized whole-run residual-attribution prototypes as the default paper-facing result, with diagnosis-only filtering that removes monotonic counters and downweights generic memory-state features.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20       0.4      0.50           0.4  0.330000               0.022591                 0.016832           mixed
      tier0_tier1       20       0.3      0.55           0.3  0.185714               0.023694                 0.024242           mixed
tier0_tier1_tier2       20       0.4      0.55           0.4  0.345641               0.018871                 0.014763           mixed
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.20      0.50          0.20  0.220000               0.020132                 0.015452           mixed
      tier0_tier1       20      0.15      0.30          0.15  0.080000               0.099354                 0.047921           mixed
tier0_tier1_tier2       20      0.15      0.35          0.15  0.169697               0.097900                 0.023442           mixed
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20       0.4      0.60           0.4  0.397619               0.009762                 0.006702           mixed
      tier0_tier1       20       0.2      0.50           0.2  0.203175               0.017341                 0.013016           mixed
tier0_tier1_tier2       20       0.2      0.45           0.2  0.190476               0.014113                 0.007449           mixed
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.50      0.75      0.444444  0.378788               0.027245                 0.029276           mixed
      tier0_tier1       20      0.50      0.65      0.444444  0.354978               0.024979                 0.023919           mixed
tier0_tier1_tier2       20      0.45      0.75      0.527778  0.444042               0.027615                 0.030785           mixed
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.30      0.55         0.4          0.30  0.257143      0.35          0.65            0.428571            0.571429                0.333333            0.240000               0.013389                 0.010936            0.007829              0.006043           0.006901        0.167812           mixed
      tier0_tier1       20      0.20      0.45         0.3          0.20  0.168889      0.45          0.55            0.222222            0.333333                0.300000            0.213333               0.011320                 0.019113            0.015241              0.011208           0.012304        0.088746           mixed
tier0_tier1_tier2       20      0.25      0.40         0.3          0.25  0.238889      0.60          0.40            0.333333            0.416667                0.366667            0.300000               0.005869                 0.006525            0.017166              0.014849           0.006629       -0.031348           mixed
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.20      0.50         0.4          0.20  0.208889      0.80          0.20            0.187500            0.500000                0.166667            0.177143               0.003955                 0.012553            0.007829              0.006043           0.006901       -0.091720           mixed
      tier0_tier1       20      0.10      0.25         0.3          0.10  0.088889      0.55          0.45            0.090909            0.181818                0.100000            0.133333               0.058141                 0.009995            0.015241              0.011208           0.012304        0.029987           mixed
tier0_tier1_tier2       20      0.15      0.35         0.3          0.15  0.146667      0.55          0.45            0.000000            0.181818                0.000000            0.000000               0.039660                 0.013520            0.017166              0.014849           0.006629        0.097393           mixed
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0  conf_0.00              0.000000      17      0.85          0.15            0.352941            0.529412                  0.4500            0.300000           mixed
            tier0  conf_0.05              0.050000      11      0.55          0.45            0.545455            0.636364                  0.5500            0.400000           mixed
            tier0  conf_0.10              0.100000       7      0.35          0.65            0.714286            0.857143                  0.6875            0.483333           mixed
            tier0  conf_0.15              0.150000       5      0.25          0.75            0.600000            0.800000                  0.3750            0.150000           mixed
            tier0    trained              0.167812       5      0.25          0.75            0.600000            0.800000                  0.3750            0.150000           mixed
            tier0  conf_0.20              0.200000       4      0.20          0.80            0.750000            0.750000                  0.7500            0.171429           mixed
            tier0  conf_0.25              0.250000       4      0.20          0.80            0.750000            0.750000                  0.7500            0.171429           mixed
      tier0_tier1  conf_0.00              0.000000      15      0.75          0.25            0.133333            0.333333                  0.2000            0.100000           mixed
      tier0_tier1  conf_0.05              0.050000      12      0.60          0.40            0.166667            0.250000                  0.2000            0.100000           mixed
      tier0_tier1    trained              0.088746      10      0.50          0.50            0.100000            0.200000                  0.2000            0.080000           mixed
      tier0_tier1  conf_0.10              0.100000      10      0.50          0.50            0.100000            0.200000                  0.2000            0.080000           mixed
      tier0_tier1  conf_0.15              0.150000       8      0.40          0.60            0.125000            0.125000                  0.2000            0.100000           mixed
      tier0_tier1  conf_0.20              0.200000       3      0.15          0.85            0.000000            0.000000                  0.0000            0.000000           mixed
      tier0_tier1  conf_0.25              0.250000       2      0.10          0.90            0.000000            0.000000                  0.0000            0.000000           mixed
tier0_tier1_tier2    trained             -0.031348      15      0.75          0.25            0.266667            0.333333                  0.3500            0.283333           mixed
tier0_tier1_tier2  conf_0.00              0.000000      13      0.65          0.35            0.230769            0.307692                  0.2500            0.183333           mixed
tier0_tier1_tier2  conf_0.05              0.050000       9      0.45          0.55            0.222222            0.222222                  0.2000            0.133333           mixed
tier0_tier1_tier2  conf_0.10              0.100000       6      0.30          0.70            0.166667            0.166667                  0.2500            0.133333           mixed
tier0_tier1_tier2  conf_0.15              0.150000       4      0.20          0.80            0.000000            0.000000                  0.0000            0.000000           mixed
tier0_tier1_tier2  conf_0.20              0.200000       2      0.10          0.90            0.000000            0.000000                  0.0000            0.000000           mixed
tier0_tier1_tier2  conf_0.25              0.250000       1      0.05          0.95            0.000000            0.000000                  0.0000            0.000000           mixed
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained             -0.091720      16      0.80          0.20            0.187500            0.500000                0.166667            0.177143           mixed
            tier0  conf_0.00              0.000000      16      0.80          0.20            0.187500            0.500000                0.166667            0.177143           mixed
            tier0  conf_0.05              0.050000      12      0.60          0.40            0.250000            0.583333                0.350000            0.257778           mixed
            tier0  conf_0.10              0.100000       8      0.40          0.60            0.375000            0.500000                0.458333            0.300000           mixed
            tier0  conf_0.15              0.150000       6      0.30          0.70            0.500000            0.666667                0.583333            0.413333           mixed
            tier0  conf_0.20              0.200000       1      0.05          0.95            0.000000            1.000000                0.000000            0.000000           mixed
            tier0  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
      tier0_tier1  conf_0.00              0.000000      14      0.70          0.30            0.000000            0.142857                0.000000            0.000000           mixed
      tier0_tier1    trained              0.029987      11      0.55          0.45            0.000000            0.181818                0.000000            0.000000           mixed
      tier0_tier1  conf_0.05              0.050000       9      0.45          0.55            0.000000            0.111111                0.000000            0.000000           mixed
      tier0_tier1  conf_0.10              0.100000       8      0.40          0.60            0.000000            0.125000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.15              0.150000       7      0.35          0.65            0.000000            0.142857                0.000000            0.000000           mixed
      tier0_tier1  conf_0.20              0.200000       7      0.35          0.65            0.000000            0.142857                0.000000            0.000000           mixed
      tier0_tier1  conf_0.25              0.250000       6      0.30          0.70            0.000000            0.166667                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.00              0.000000      14      0.70          0.30            0.071429            0.285714                0.100000            0.100000           mixed
tier0_tier1_tier2  conf_0.05              0.050000      10      0.50          0.50            0.000000            0.300000                0.000000            0.000000           mixed
tier0_tier1_tier2    trained              0.097393       8      0.40          0.60            0.000000            0.250000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.10              0.100000       8      0.40          0.60            0.000000            0.250000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.15              0.150000       6      0.30          0.70            0.000000            0.333333                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.20              0.200000       5      0.25          0.75            0.000000            0.400000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.25              0.250000       5      0.25          0.75            0.000000            0.400000                0.000000            0.000000           mixed
```

## Diagnosis Mode Comparison
- Whole-run and post-alert-window diagnosis are exported together so the diagnosis mode can be evaluated directly.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile diagnosis_target    diagnosis_mode  family_acc  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau                       status  min_class_count  min_group_count    group_key  include_workload
            tier0       20      0.40      0.50      0.400000  0.330000               0.022591                 0.016832           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.30      0.55      0.300000  0.185714               0.023694                 0.024242           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.40      0.55      0.400000  0.345641               0.018871                 0.014763           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.20      0.50      0.200000  0.220000               0.020132                 0.015452           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.15      0.30      0.150000  0.080000               0.099354                 0.047921           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.15      0.35      0.150000  0.169697               0.097900                 0.023442           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.30      0.55      0.300000  0.257143               0.013389                 0.010936           mixed     hierarchical         whole_run         0.4      0.35          0.65            0.428571            0.571429                0.333333            0.240000            0.007829              0.006043           0.006901        0.167812                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.20      0.45      0.200000  0.168889               0.011320                 0.019113           mixed     hierarchical         whole_run         0.3      0.45          0.55            0.222222            0.333333                0.300000            0.213333            0.015241              0.011208           0.012304        0.088746                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.25      0.40      0.250000  0.238889               0.005869                 0.006525           mixed     hierarchical         whole_run         0.3      0.60          0.40            0.333333            0.416667                0.366667            0.300000            0.017166              0.014849           0.006629       -0.031348                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.20      0.50      0.200000  0.208889               0.003955                 0.012553           mixed     hierarchical post_alert_window         0.4      0.80          0.20            0.187500            0.500000                0.166667            0.177143            0.007829              0.006043           0.006901       -0.091720                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.10      0.25      0.100000  0.088889               0.058141                 0.009995           mixed     hierarchical post_alert_window         0.3      0.55          0.45            0.090909            0.181818                0.100000            0.133333            0.015241              0.011208           0.012304        0.029987                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.15      0.35      0.150000  0.146667               0.039660                 0.013520           mixed     hierarchical post_alert_window         0.3      0.55          0.45            0.000000            0.181818                0.000000            0.000000            0.017166              0.014849           0.006629        0.097393                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.50      0.75      0.444444  0.378788               0.027245                 0.029276           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.50      0.65      0.444444  0.354978               0.024979                 0.023919           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.45      0.75      0.527778  0.444042               0.027615                 0.030785           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.727567         0.121258     0.151175              tier0           mixed
  BRANCH     0.767099         0.081978     0.150923              tier0           mixed
   CACHE     0.548396         0.343195     0.108409              tier0           mixed
   MEMBW     0.777459         0.089556     0.132985              tier0           mixed
     TLB     0.710801         0.125196     0.164004              tier0           mixed
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC               memory_io       0.269991         0.402892             0.075215                 0.223474                 0.028428           mixed
  BRANCH               memory_io       0.253949         0.446650             0.048910                 0.215102                 0.035390           mixed
   CACHE               memory_io       0.466152         0.278230             0.063330                 0.154988                 0.037300           mixed
   MEMBW               memory_io       0.235356         0.468436             0.056251                 0.192005                 0.047951           mixed
     TLB               memory_io       0.303443         0.382812             0.071577                 0.216891                 0.025278           mixed
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
            tier0                   0.25                        2.755102                      4.591837                 0.35                     70.0                 554.8                0.25                0.25                0.30           mixed
      tier0_tier1                   0.25                        2.755102                      4.591837                 0.60                     77.0                 784.1                0.35                0.35                0.50           mixed
tier0_tier1_tier2                   0.25                        2.755102                      4.591837                 0.65                     70.0                 750.4                0.40                0.40                0.55           mixed
```

## Files
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B20_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B20_a0.05_k3/config_runtime_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B20_a0.05_k3/run_context.json`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B20_a0.05_k3/case_inventory.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B20_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B20_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B20_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B20_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B20_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B20_a0.05_k3/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B20_a0.05_k3/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B20_a0.05_k3/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B20_a0.05_k3/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B20_a0.05_k3/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B20_a0.05_k3/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B20_a0.05_k3/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B20_a0.05_k3/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B20_a0.05_k3/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B20_a0.05_k3/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B20_a0.05_k3/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B20_a0.05_k3/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B20_a0.05_k3/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B20_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B20_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B20_a0.05_k3/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B20_a0.05_k3/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B20_a0.05_k3/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B20_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B20_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B20_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B20_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B20_a0.05_k3/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B20_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B20_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B20_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B20_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B20_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B20_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B20_a0.05_k3/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B20_a0.05_k3/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B20_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B20_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B20_a0.05_k3/figures/fig_detection_latency.png`
