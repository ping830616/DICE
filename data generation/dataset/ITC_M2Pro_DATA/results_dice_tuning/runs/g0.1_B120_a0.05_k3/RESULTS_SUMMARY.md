# DICE Full Retrain Results

## Setup
- Feature profile: mixed ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_core_5hz.csv', 'tier2': 'tier2_core_5hz.csv'})
- Protocol: global, benign-only fit/calibration, block_B=120, alpha=0.05, persist_k=3, gain=0.1
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
          mixed             tier0       24          46          2.243499   0.7875 0.921899         1.0        1.0            0.0           0.30              0.011026              0.024926                      0.0                 0.014395
          mixed       tier0_tier1       24          57          2.742755   0.8125 0.940232         1.0        1.0            0.0           0.45              0.000045              0.000115                      0.0                 0.000061
          mixed tier0_tier1_tier2       24          64          3.124999   0.8125 0.940232         1.0        1.0            0.0           0.45              0.000049              0.000123                      0.0                 0.000062
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
          mixed   ATOMIC   0.8125 0.804167         1.0        1.0          0.000049          0.000106                  0.0             0.000062       2.145296      0.000057         63.066331         0.000062
          mixed   BRANCH   0.8750 0.887500         1.0        1.0          0.000049          0.000161                  0.0             0.000113       3.257478      0.000112        113.529192         0.000113
          mixed    CACHE   0.8125 0.804167         1.0        1.0          0.000049          0.000103                  0.0             0.000058       2.096765      0.000055         58.638997         0.000058
          mixed    MEMBW   0.8125 0.804167         1.0        1.0          0.000049          0.000156                  0.0             0.000086       3.155025      0.000107         87.284465         0.000086
          mixed      TLB   0.7500 0.679167         1.0        1.0          0.000049          0.000102                  0.0             0.000056       2.070911      0.000053         56.513478         0.000056
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
            tier0       20      0.35      0.60          0.35  0.321429               0.024604                 0.015035           mixed
      tier0_tier1       20      0.30      0.65          0.30  0.201399               0.018485                 0.014237           mixed
tier0_tier1_tier2       20      0.40      0.65          0.40  0.353333               0.015631                 0.008884           mixed
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.15      0.45          0.15  0.147475               0.024902                 0.020440           mixed
      tier0_tier1       20      0.10      0.30          0.10  0.100000               0.037147                 0.018582           mixed
tier0_tier1_tier2       20      0.20      0.45          0.20  0.156364               0.022658                 0.018591           mixed
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.25      0.50          0.25  0.208889               0.023231                 0.021749           mixed
      tier0_tier1       20      0.25      0.55          0.25  0.247143               0.018156                 0.013988           mixed
tier0_tier1_tier2       20      0.30      0.60          0.30  0.279870               0.014331                 0.011126           mixed
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.60      0.85      0.500000  0.421818               0.034753                 0.038507           mixed
      tier0_tier1       20      0.50      0.80      0.444444  0.356745               0.023875                 0.022902           mixed
tier0_tier1_tier2       20      0.55      0.70      0.527778  0.487302               0.023631                 0.022181           mixed
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.20      0.60         0.4          0.20  0.181538      0.50          0.50            0.200000            0.700000                0.133333            0.166667              -0.012055                -0.001969            0.017807              0.013199           0.009908       -0.014112           mixed
      tier0_tier1       20      0.20      0.70         0.4          0.20  0.158681      0.65          0.35            0.307692            0.769231                0.350000            0.251429               0.007179                 0.007155            0.018869              0.015883           0.011150        0.009797           mixed
tier0_tier1_tier2       20      0.15      0.65         0.3          0.15  0.130476      0.50          0.50            0.200000            0.600000                0.200000            0.146667               0.001925                 0.003614            0.019185              0.017619           0.011855        0.019971           mixed
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.15      0.45         0.4          0.15  0.123810      0.60          0.40            0.083333            0.416667                0.066667                0.08              -0.010978                 0.007178            0.017807              0.013199           0.009908       -0.043635           mixed
      tier0_tier1       20      0.15      0.25         0.4          0.15  0.109091      0.60          0.40            0.250000            0.333333                0.200000                0.18               0.001001                 0.009998            0.018869              0.015883           0.011150       -0.032748           mixed
tier0_tier1_tier2       20      0.10      0.35         0.3          0.10  0.066667      0.85          0.15            0.117647            0.352941                0.100000                0.08              -0.006755                 0.012467            0.019185              0.017619           0.011855       -0.116454           mixed
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained             -0.014112      11      0.55          0.45            0.181818            0.636364                0.166667            0.190476           mixed
            tier0  conf_0.00              0.000000      10      0.50          0.50            0.200000            0.600000                0.208333            0.190476           mixed
            tier0  conf_0.05              0.050000       8      0.40          0.60            0.250000            0.625000                0.208333            0.200000           mixed
            tier0  conf_0.10              0.100000       6      0.30          0.70            0.166667            0.500000                0.083333            0.066667           mixed
            tier0  conf_0.15              0.150000       3      0.15          0.85            0.333333            0.666667                0.250000            0.100000           mixed
            tier0  conf_0.20              0.200000       1      0.05          0.95            1.000000            1.000000                1.000000            0.200000           mixed
            tier0  conf_0.25              0.250000       1      0.05          0.95            1.000000            1.000000                1.000000            0.200000           mixed
      tier0_tier1  conf_0.00              0.000000      15      0.75          0.25            0.200000            0.733333                0.266667            0.146667           mixed
      tier0_tier1    trained              0.009797      13      0.65          0.35            0.230769            0.692308                0.300000            0.188889           mixed
      tier0_tier1  conf_0.05              0.050000      10      0.50          0.50            0.200000            0.800000                0.300000            0.157143           mixed
      tier0_tier1  conf_0.10              0.100000       7      0.35          0.65            0.142857            0.857143                0.200000            0.066667           mixed
      tier0_tier1  conf_0.15              0.150000       4      0.20          0.80            0.250000            0.750000                0.250000            0.080000           mixed
      tier0_tier1  conf_0.20              0.200000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
tier0_tier1_tier2  conf_0.00              0.000000      15      0.75          0.25            0.133333            0.600000                0.133333            0.106667           mixed
tier0_tier1_tier2    trained              0.019971      10      0.50          0.50            0.200000            0.500000                0.300000            0.166667           mixed
tier0_tier1_tier2  conf_0.05              0.050000       6      0.30          0.70            0.166667            0.500000                0.200000            0.066667           mixed
tier0_tier1_tier2  conf_0.10              0.100000       3      0.15          0.85            0.333333            0.333333                0.333333            0.100000           mixed
tier0_tier1_tier2  conf_0.15              0.150000       3      0.15          0.85            0.333333            0.333333                0.333333            0.100000           mixed
tier0_tier1_tier2  conf_0.20              0.200000       3      0.15          0.85            0.333333            0.333333                0.333333            0.100000           mixed
tier0_tier1_tier2  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained             -0.043635      13      0.65          0.35            0.153846            0.461538                0.133333            0.130000           mixed
            tier0  conf_0.00              0.000000      12      0.60          0.40            0.083333            0.416667                0.066667            0.080000           mixed
            tier0  conf_0.05              0.050000      10      0.50          0.50            0.100000            0.500000                0.100000            0.100000           mixed
            tier0  conf_0.10              0.100000       8      0.40          0.60            0.125000            0.625000                0.125000            0.100000           mixed
            tier0  conf_0.15              0.150000       6      0.30          0.70            0.000000            0.500000                0.000000            0.000000           mixed
            tier0  conf_0.20              0.200000       3      0.15          0.85            0.000000            0.666667                0.000000            0.000000           mixed
            tier0  conf_0.25              0.250000       1      0.05          0.95            0.000000            1.000000                0.000000            0.000000           mixed
      tier0_tier1    trained             -0.032748      15      0.75          0.25            0.200000            0.333333                0.166667            0.150000           mixed
      tier0_tier1  conf_0.00              0.000000      14      0.70          0.30            0.142857            0.285714                0.100000            0.100000           mixed
      tier0_tier1  conf_0.05              0.050000       9      0.45          0.55            0.111111            0.222222                0.083333            0.080000           mixed
      tier0_tier1  conf_0.10              0.100000       6      0.30          0.70            0.000000            0.166667                0.000000            0.000000           mixed
      tier0_tier1  conf_0.15              0.150000       4      0.20          0.80            0.000000            0.250000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.20              0.200000       3      0.15          0.85            0.000000            0.333333                0.000000            0.000000           mixed
      tier0_tier1  conf_0.25              0.250000       3      0.15          0.85            0.000000            0.333333                0.000000            0.000000           mixed
tier0_tier1_tier2    trained             -0.116454      15      0.75          0.25            0.133333            0.333333                0.100000            0.088889           mixed
tier0_tier1_tier2  conf_0.00              0.000000      14      0.70          0.30            0.142857            0.357143                0.100000            0.088889           mixed
tier0_tier1_tier2  conf_0.05              0.050000      12      0.60          0.40            0.166667            0.333333                0.100000            0.088889           mixed
tier0_tier1_tier2  conf_0.10              0.100000       4      0.20          0.80            0.000000            0.250000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.15              0.150000       2      0.10          0.90            0.000000            0.000000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.20              0.200000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
tier0_tier1_tier2  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
```

## Diagnosis Mode Comparison
- Whole-run and post-alert-window diagnosis are exported together so the diagnosis mode can be evaluated directly.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile diagnosis_target    diagnosis_mode  family_acc  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau                       status  min_class_count  min_group_count    group_key  include_workload
            tier0       20      0.35      0.60      0.350000  0.321429               0.024604                 0.015035           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.30      0.65      0.300000  0.201399               0.018485                 0.014237           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.40      0.65      0.400000  0.353333               0.015631                 0.008884           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.15      0.45      0.150000  0.147475               0.024902                 0.020440           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.10      0.30      0.100000  0.100000               0.037147                 0.018582           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.20      0.45      0.200000  0.156364               0.022658                 0.018591           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.20      0.60      0.200000  0.181538              -0.012055                -0.001969           mixed     hierarchical         whole_run         0.4      0.50          0.50            0.200000            0.700000                0.133333            0.166667            0.017807              0.013199           0.009908       -0.014112                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.20      0.70      0.200000  0.158681               0.007179                 0.007155           mixed     hierarchical         whole_run         0.4      0.65          0.35            0.307692            0.769231                0.350000            0.251429            0.018869              0.015883           0.011150        0.009797                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.15      0.65      0.150000  0.130476               0.001925                 0.003614           mixed     hierarchical         whole_run         0.3      0.50          0.50            0.200000            0.600000                0.200000            0.146667            0.019185              0.017619           0.011855        0.019971                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.15      0.45      0.150000  0.123810              -0.010978                 0.007178           mixed     hierarchical post_alert_window         0.4      0.60          0.40            0.083333            0.416667                0.066667            0.080000            0.017807              0.013199           0.009908       -0.043635                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.15      0.25      0.150000  0.109091               0.001001                 0.009998           mixed     hierarchical post_alert_window         0.4      0.60          0.40            0.250000            0.333333                0.200000            0.180000            0.018869              0.015883           0.011150       -0.032748                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.10      0.35      0.100000  0.066667              -0.006755                 0.012467           mixed     hierarchical post_alert_window         0.3      0.85          0.15            0.117647            0.352941                0.100000            0.080000            0.019185              0.017619           0.011855       -0.116454                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.60      0.85      0.500000  0.421818               0.034753                 0.038507           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.50      0.80      0.444444  0.356745               0.023875                 0.022902           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.55      0.70      0.527778  0.487302               0.023631                 0.022181           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.700125         0.168471     0.131404              tier0           mixed
  BRANCH     0.776857         0.096767     0.126376              tier0           mixed
   CACHE     0.551784         0.356539     0.091677              tier0           mixed
   MEMBW     0.799139         0.101585     0.099276              tier0           mixed
     TLB     0.716018         0.152058     0.131924              tier0           mixed
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC               memory_io       0.263818         0.418306             0.097571                 0.178706                 0.041600           mixed
  BRANCH               memory_io       0.232860         0.497362             0.050651                 0.165806                 0.053321           mixed
   CACHE               memory_io       0.462021         0.294366             0.065778                 0.117884                 0.059951           mixed
   MEMBW               memory_io       0.226684         0.511151             0.055429                 0.137554                 0.069182           mixed
     TLB               memory_io       0.288303         0.440160             0.076346                 0.160592                 0.034600           mixed
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
            tier0                    0.0                             0.0                           0.0                 0.30                    122.0                 689.0                 0.0                0.20                0.25           mixed
      tier0_tier1                    0.0                             0.0                           0.0                 0.45                    122.0                 916.6                 0.0                0.25                0.35           mixed
tier0_tier1_tier2                    0.0                             0.0                           0.0                 0.45                    122.0                 884.8                 0.0                0.30                0.35           mixed
```

## Files
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B120_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B120_a0.05_k3/config_runtime_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B120_a0.05_k3/run_context.json`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B120_a0.05_k3/case_inventory.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B120_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B120_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B120_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B120_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B120_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B120_a0.05_k3/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B120_a0.05_k3/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B120_a0.05_k3/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B120_a0.05_k3/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B120_a0.05_k3/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B120_a0.05_k3/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B120_a0.05_k3/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B120_a0.05_k3/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B120_a0.05_k3/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B120_a0.05_k3/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B120_a0.05_k3/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B120_a0.05_k3/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B120_a0.05_k3/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B120_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B120_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B120_a0.05_k3/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B120_a0.05_k3/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B120_a0.05_k3/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B120_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B120_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B120_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B120_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B120_a0.05_k3/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B120_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B120_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B120_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B120_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B120_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B120_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B120_a0.05_k3/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B120_a0.05_k3/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B120_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B120_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B120_a0.05_k3/figures/fig_detection_latency.png`
