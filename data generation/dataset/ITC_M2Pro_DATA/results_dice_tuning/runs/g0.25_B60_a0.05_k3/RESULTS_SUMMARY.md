# DICE Full Retrain Results

## Setup
- Feature profile: mixed ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_core_5hz.csv', 'tier2': 'tier2_core_5hz.csv'})
- Protocol: global, benign-only fit/calibration, block_B=60, alpha=0.05, persist_k=3, gain=0.25
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
          mixed             tier0       24          46          2.360792    0.800 0.931899         1.0        1.0            0.0           0.30              0.007173              0.015654                      0.0                 0.008507
          mixed       tier0_tier1       24          57          2.895620    0.825 0.951460         1.0        1.0            0.0           0.45              0.000043              0.000106                      0.0                 0.000056
          mixed tier0_tier1_tier2       24          64          3.274262    0.850 0.959180         1.0        1.0            0.0           0.45              0.000046              0.000114                      0.0                 0.000061
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
          mixed   ATOMIC   0.8125 0.804167         1.0        1.0          0.000046          0.000097                  0.0             0.000055       2.096684      0.000051         56.196556         0.000055
          mixed   BRANCH   0.9375 0.950000         1.0        1.0          0.000046          0.000175                  0.0             0.000121       3.757095      0.000129        121.905302         0.000121
          mixed    CACHE   0.8125 0.804167         1.0        1.0          0.000046          0.000098                  0.0             0.000058       2.121607      0.000053         59.281920         0.000058
          mixed    MEMBW   0.9375 0.950000         1.0        1.0          0.000046          0.000161                  0.0             0.000093       3.449099      0.000115         94.464915         0.000093
          mixed      TLB   0.7500 0.679167         1.0        1.0          0.000046          0.000111                  0.0             0.000055       2.389326      0.000065         56.116173         0.000055
```

## Paper-style Aggregates (Final Config)
- Base score mean stressor AUC-PR (all five): **0.8375**
- Base score mean stressor ROC-AUC (all five): **0.8500**
- WC score mean stressor AUC-PR (all five): **1.0000**
- WC score mean stressor ROC-AUC (all five): **1.0000**
- Base score mean stressor AUC-PR (excluding BRANCH/TLB): **0.8528**
- Base score mean stressor ROC-AUC (excluding BRANCH/TLB): **0.8542**
- WC score mean stressor AUC-PR (excluding BRANCH/TLB): **1.0000**
- WC score mean stressor ROC-AUC (excluding BRANCH/TLB): **1.0000**

## Diagnosis
- Feature-level diagnosis uses normalized whole-run residual-attribution prototypes as the default paper-facing result, with diagnosis-only filtering that removes monotonic counters and downweights generic memory-state features.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20       0.3       0.6           0.3  0.238961               0.026441                 0.020305           mixed
      tier0_tier1       20       0.3       0.7           0.3  0.216117               0.021460                 0.018014           mixed
tier0_tier1_tier2       20       0.5       0.7           0.5  0.486593               0.020164                 0.018984           mixed
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.10      0.55          0.10  0.116364               0.015435                 0.008309           mixed
      tier0_tier1       20      0.15      0.30          0.15  0.123810               0.064039                 0.022758           mixed
tier0_tier1_tier2       20      0.15      0.40          0.15  0.166667               0.053777                 0.017473           mixed
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.25      0.65          0.25  0.223333               0.014232                 0.009951           mixed
      tier0_tier1       20      0.30      0.65          0.30  0.296061               0.012855                 0.008546           mixed
tier0_tier1_tier2       20      0.40      0.65          0.40  0.403175               0.011146                 0.009581           mixed
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.60      0.80      0.500000  0.421818               0.033640                 0.033806           mixed
      tier0_tier1       20      0.50      0.80      0.444444  0.356745               0.027035                 0.031163           mixed
tier0_tier1_tier2       20      0.55      0.75      0.583333  0.531039               0.027217                 0.027831           mixed
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.45       0.7        0.45          0.45  0.360000      0.40          0.60            0.500000            0.750000                0.400000            0.314286              -0.010155                 0.005073            0.014656              0.016687           0.012266        0.073714           mixed
      tier0_tier1       20      0.20       0.7        0.45          0.20  0.152727      0.55          0.45            0.272727            0.727273                0.266667            0.214286               0.002933                 0.003947            0.018993              0.017402           0.016377        0.024609           mixed
tier0_tier1_tier2       20      0.55       0.7        0.30          0.55  0.536710      0.45          0.55            0.777778            0.888889                0.800000            0.766667               0.010383                 0.010834            0.018943              0.014202           0.019706        0.111015           mixed
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.35      0.65        0.45          0.35  0.303810      0.50          0.50            0.200000            0.600000                0.133333            0.146667              -0.015250                -0.000026            0.014656              0.016687           0.012266       -0.068627           mixed
      tier0_tier1       20      0.25      0.30        0.45          0.25  0.172727      0.55          0.45            0.272727            0.272727                0.233333            0.194286              -0.018507                 0.002179            0.018993              0.017402           0.016377       -0.072744           mixed
tier0_tier1_tier2       20      0.20      0.40        0.30          0.20  0.200000      0.45          0.55            0.000000            0.111111                0.000000            0.000000               0.015287                 0.015327            0.018943              0.014202           0.019706        0.080544           mixed
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0  conf_0.00              0.000000      11      0.55          0.45            0.454545            0.727273                0.400000            0.293333           mixed
            tier0  conf_0.05              0.050000       9      0.45          0.55            0.555556            0.666667                0.400000            0.293333           mixed
            tier0    trained              0.073714       7      0.35          0.65            0.571429            0.571429                0.400000            0.293333           mixed
            tier0  conf_0.10              0.100000       5      0.25          0.75            0.600000            0.600000                0.500000            0.293333           mixed
            tier0  conf_0.15              0.150000       3      0.15          0.85            0.666667            0.666667                0.500000            0.160000           mixed
            tier0  conf_0.20              0.200000       2      0.10          0.90            1.000000            1.000000                1.000000            0.200000           mixed
            tier0  conf_0.25              0.250000       2      0.10          0.90            1.000000            1.000000                1.000000            0.200000           mixed
      tier0_tier1  conf_0.00              0.000000      13      0.65          0.35            0.153846            0.615385                0.133333            0.088889           mixed
      tier0_tier1    trained              0.024609      11      0.55          0.45            0.181818            0.636364                0.200000            0.100000           mixed
      tier0_tier1  conf_0.05              0.050000       8      0.40          0.60            0.250000            0.500000                0.250000            0.100000           mixed
      tier0_tier1  conf_0.10              0.100000       6      0.30          0.70            0.166667            0.500000                0.250000            0.066667           mixed
      tier0_tier1  conf_0.15              0.150000       5      0.25          0.75            0.200000            0.400000                0.333333            0.066667           mixed
      tier0_tier1  conf_0.20              0.200000       3      0.15          0.85            0.333333            0.333333                0.500000            0.100000           mixed
      tier0_tier1  conf_0.25              0.250000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.00              0.000000      17      0.85          0.15            0.588235            0.705882                0.633333            0.596710           mixed
tier0_tier1_tier2  conf_0.05              0.050000      11      0.55          0.45            0.545455            0.636364                0.566667            0.486667           mixed
tier0_tier1_tier2  conf_0.10              0.100000       7      0.35          0.65            0.428571            0.571429                0.444444            0.200000           mixed
tier0_tier1_tier2    trained              0.111015       6      0.30          0.70            0.333333            0.500000                0.333333            0.100000           mixed
tier0_tier1_tier2  conf_0.15              0.150000       5      0.25          0.75            0.400000            0.600000                0.333333            0.114286           mixed
tier0_tier1_tier2  conf_0.20              0.200000       4      0.20          0.80            0.500000            0.500000                0.333333            0.133333           mixed
tier0_tier1_tier2  conf_0.25              0.250000       1      0.05          0.95            1.000000            1.000000                1.000000            0.200000           mixed
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained             -0.068627      13      0.65          0.35            0.307692            0.692308                0.333333            0.293333           mixed
            tier0  conf_0.00              0.000000      11      0.55          0.45            0.181818            0.636364                0.133333            0.146667           mixed
            tier0  conf_0.05              0.050000       7      0.35          0.65            0.285714            0.571429                0.333333            0.233333           mixed
            tier0  conf_0.10              0.100000       5      0.25          0.75            0.200000            0.600000                0.250000            0.133333           mixed
            tier0  conf_0.15              0.150000       5      0.25          0.75            0.200000            0.600000                0.250000            0.133333           mixed
            tier0  conf_0.20              0.200000       4      0.20          0.80            0.250000            0.500000                0.333333            0.133333           mixed
            tier0  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
      tier0_tier1    trained             -0.072744      12      0.60          0.40            0.166667            0.166667                0.200000            0.146667           mixed
      tier0_tier1  conf_0.00              0.000000      11      0.55          0.45            0.181818            0.181818                0.200000            0.166667           mixed
      tier0_tier1  conf_0.05              0.050000       8      0.40          0.60            0.125000            0.125000                0.200000            0.080000           mixed
      tier0_tier1  conf_0.10              0.100000       8      0.40          0.60            0.125000            0.125000                0.200000            0.080000           mixed
      tier0_tier1  conf_0.15              0.150000       6      0.30          0.70            0.000000            0.000000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.20              0.200000       5      0.25          0.75            0.000000            0.000000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.25              0.250000       4      0.20          0.80            0.000000            0.000000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.00              0.000000      15      0.75          0.25            0.133333            0.333333                0.150000            0.177778           mixed
tier0_tier1_tier2  conf_0.05              0.050000      12      0.60          0.40            0.000000            0.250000                0.000000            0.000000           mixed
tier0_tier1_tier2    trained              0.080544       9      0.45          0.55            0.000000            0.222222                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.10              0.100000       7      0.35          0.65            0.000000            0.285714                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.15              0.150000       7      0.35          0.65            0.000000            0.285714                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.20              0.200000       4      0.20          0.80            0.000000            0.250000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.25              0.250000       4      0.20          0.80            0.000000            0.250000                0.000000            0.000000           mixed
```

## Diagnosis Mode Comparison
- Whole-run and post-alert-window diagnosis are exported together so the diagnosis mode can be evaluated directly.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile diagnosis_target    diagnosis_mode  family_acc  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau                       status  min_class_count  min_group_count    group_key  include_workload
            tier0       20      0.30      0.60      0.300000  0.238961               0.026441                 0.020305           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.30      0.70      0.300000  0.216117               0.021460                 0.018014           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.50      0.70      0.500000  0.486593               0.020164                 0.018984           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.10      0.55      0.100000  0.116364               0.015435                 0.008309           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.15      0.30      0.150000  0.123810               0.064039                 0.022758           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.15      0.40      0.150000  0.166667               0.053777                 0.017473           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.45      0.70      0.450000  0.360000              -0.010155                 0.005073           mixed     hierarchical         whole_run        0.45      0.40          0.60            0.500000            0.750000                0.400000            0.314286            0.014656              0.016687           0.012266        0.073714                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.20      0.70      0.200000  0.152727               0.002933                 0.003947           mixed     hierarchical         whole_run        0.45      0.55          0.45            0.272727            0.727273                0.266667            0.214286            0.018993              0.017402           0.016377        0.024609                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.55      0.70      0.550000  0.536710               0.010383                 0.010834           mixed     hierarchical         whole_run        0.30      0.45          0.55            0.777778            0.888889                0.800000            0.766667            0.018943              0.014202           0.019706        0.111015                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.35      0.65      0.350000  0.303810              -0.015250                -0.000026           mixed     hierarchical post_alert_window        0.45      0.50          0.50            0.200000            0.600000                0.133333            0.146667            0.014656              0.016687           0.012266       -0.068627                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.25      0.30      0.250000  0.172727              -0.018507                 0.002179           mixed     hierarchical post_alert_window        0.45      0.55          0.45            0.272727            0.272727                0.233333            0.194286            0.018993              0.017402           0.016377       -0.072744                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.20      0.40      0.200000  0.200000               0.015287                 0.015327           mixed     hierarchical post_alert_window        0.30      0.45          0.55            0.000000            0.111111                0.000000            0.000000            0.018943              0.014202           0.019706        0.080544                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.60      0.80      0.500000  0.421818               0.033640                 0.033806           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.50      0.80      0.444444  0.356745               0.027035                 0.031163           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.55      0.75      0.583333  0.531039               0.027217                 0.027831           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.710837         0.140096     0.149067              tier0           mixed
  BRANCH     0.771144         0.089282     0.139575              tier0           mixed
   CACHE     0.546323         0.351194     0.102482              tier0           mixed
   MEMBW     0.788097         0.096136     0.115767              tier0           mixed
     TLB     0.712062         0.138111     0.149827              tier0           mixed
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC               memory_io       0.261920         0.411509             0.085006                 0.206132                 0.035433           mixed
  BRANCH               memory_io       0.240934         0.475541             0.048978                 0.188636                 0.045911           mixed
   CACHE               memory_io       0.461489         0.286090             0.065409                 0.137383                 0.049629           mixed
   MEMBW               memory_io       0.227347         0.497795             0.055327                 0.161084                 0.058446           mixed
     TLB               memory_io       0.296566         0.412255             0.072929                 0.188576                 0.029673           mixed
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
            tier0                    0.0                             0.0                           0.0                 0.30                     75.0                 723.5                 0.2                 0.2                0.20           mixed
      tier0_tier1                    0.0                             0.0                           0.0                 0.45                     62.0                 678.2                 0.3                 0.3                0.35           mixed
tier0_tier1_tier2                    0.0                             0.0                           0.0                 0.45                     62.0                 541.8                 0.3                 0.3                0.40           mixed
```

## Files
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B60_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B60_a0.05_k3/config_runtime_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B60_a0.05_k3/run_context.json`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B60_a0.05_k3/case_inventory.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B60_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B60_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B60_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B60_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B60_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B60_a0.05_k3/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B60_a0.05_k3/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B60_a0.05_k3/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B60_a0.05_k3/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B60_a0.05_k3/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B60_a0.05_k3/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B60_a0.05_k3/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B60_a0.05_k3/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B60_a0.05_k3/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B60_a0.05_k3/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B60_a0.05_k3/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B60_a0.05_k3/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B60_a0.05_k3/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B60_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B60_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B60_a0.05_k3/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B60_a0.05_k3/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B60_a0.05_k3/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B60_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B60_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B60_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B60_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B60_a0.05_k3/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B60_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B60_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B60_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B60_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B60_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B60_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B60_a0.05_k3/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B60_a0.05_k3/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B60_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B60_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B60_a0.05_k3/figures/fig_detection_latency.png`
