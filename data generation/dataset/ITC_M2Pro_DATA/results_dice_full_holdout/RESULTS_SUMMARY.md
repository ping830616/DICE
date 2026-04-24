# DICE Full Retrain Results

## Setup
- Feature profile: mixed ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_core_5hz.csv', 'tier2': 'tier2_core_5hz.csv'})
- Protocol: workload_holdout, benign-only fit/calibration, block_B=45, alpha=0.1, persist_k=1, gain=0.2
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
          mixed             tier0       24          46          2.483713   0.3625 0.774642         1.0        1.0            1.0            0.9              0.094935              0.072643                      0.0                 0.019657
          mixed       tier0_tier1       24          57          2.999823   0.4000 0.820213         1.0        1.0            1.0            0.9              0.000404              0.000328                      0.0                 0.000100
          mixed tier0_tier1_tier2       24          64          3.472337   0.3625 0.806501         1.0        1.0            1.0            0.9              0.000606              0.000320                      0.0                 0.000132
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
          mixed   ATOMIC   0.1875 0.415476         1.0        1.0          0.000606          0.000184                  0.0             0.000474       0.305386     -0.000422        474.652042         0.000474
          mixed   BRANCH   0.3125 0.451190         1.0        1.0          0.000606          0.000334                  0.0             0.000140       0.551976     -0.000272        140.943330         0.000140
          mixed    CACHE   0.7500 0.830357         1.0        1.0          0.000606          2.230472                  0.0             0.151568    3674.012310      2.229866     151569.082615         0.151568
          mixed    MEMBW   0.2500 0.433333         1.0        1.0          0.000606          0.000299                  0.0             0.000434       0.494689     -0.000307        435.013642         0.000434
          mixed      TLB   0.3125 0.451190         1.0        1.0          0.000606          0.000291                  0.0             0.000073       0.480715     -0.000315         73.886095         0.000073
```

## Paper-style Aggregates (Final Config)
- Base score mean stressor AUC-PR (all five): **0.5163**
- Base score mean stressor ROC-AUC (all five): **0.3625**
- WC score mean stressor AUC-PR (all five): **1.0000**
- WC score mean stressor ROC-AUC (all five): **1.0000**
- Base score mean stressor AUC-PR (excluding BRANCH/TLB): **0.5597**
- Base score mean stressor ROC-AUC (excluding BRANCH/TLB): **0.3958**
- WC score mean stressor AUC-PR (excluding BRANCH/TLB): **1.0000**
- WC score mean stressor ROC-AUC (excluding BRANCH/TLB): **1.0000**

## Diagnosis
- Feature-level diagnosis uses normalized whole-run residual-attribution prototypes as the default paper-facing result, with diagnosis-only filtering that removes monotonic counters and downweights generic memory-state features.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.20      0.55          0.20  0.171429               0.012219                 0.009179           mixed
      tier0_tier1       20      0.25      0.65          0.25  0.216667               0.021765                 0.018885           mixed
tier0_tier1_tier2       20      0.25      0.60          0.25  0.205556               0.032220                 0.021885           mixed
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.25      0.45          0.25  0.191409               0.027439                 0.027951           mixed
      tier0_tier1       20      0.25      0.55          0.25  0.202727               0.018355                 0.013132           mixed
tier0_tier1_tier2       20      0.25      0.55          0.25  0.202597               0.021490                 0.019757           mixed
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.10      0.40          0.10  0.075214               0.007338                 0.006631           mixed
      tier0_tier1       20      0.25      0.45          0.25  0.203810               0.022794                 0.020699           mixed
tier0_tier1_tier2       20      0.25      0.45          0.25  0.152727               0.014700                 0.013049           mixed
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.45      0.75      0.416667  0.415152               0.036886                 0.028002           mixed
      tier0_tier1       20      0.50      0.85      0.500000  0.479365               0.043834                 0.035136           mixed
tier0_tier1_tier2       20      0.45      0.80      0.472222  0.433333               0.028194                 0.027326           mixed
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.15       0.5        0.25          0.15  0.114286       0.9           0.1            0.166667            0.500000                0.166667            0.123810               0.011448                 0.009179            0.009456              0.008503           0.012198             0.0           mixed
      tier0_tier1       20      0.25       0.5        0.30          0.25  0.211616       0.7           0.3            0.214286            0.428571                0.200000            0.157143              -0.002621                 0.003679            0.012528              0.015208           0.005615             0.0           mixed
tier0_tier1_tier2       20      0.15       0.5        0.25          0.15  0.111111       0.5           0.5            0.100000            0.400000                0.100000            0.100000              -0.010509                -0.003592            0.021425              0.019452           0.012607             0.0           mixed
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.20      0.40        0.25          0.20  0.161345      0.80          0.20            0.250000            0.437500                0.233333            0.194872               0.005666                 0.005677            0.009456              0.008503           0.012198        0.000000           mixed
      tier0_tier1       20      0.15      0.55        0.30          0.15  0.075000      0.50          0.50            0.100000            0.400000                0.200000            0.066667               0.001147                 0.009264            0.012528              0.015208           0.005615        0.038770           mixed
tier0_tier1_tier2       20      0.20      0.50        0.25          0.20  0.080000      0.55          0.45            0.181818            0.454545                0.200000            0.088889              -0.002682                 0.000229            0.021425              0.019452           0.012607        0.002831           mixed
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained                  0.00      18      0.90          0.10            0.166667            0.500000                0.166667            0.123810           mixed
            tier0  conf_0.00                  0.00      18      0.90          0.10            0.166667            0.500000                0.166667            0.123810           mixed
            tier0  conf_0.05                  0.05       8      0.40          0.60            0.125000            0.375000                0.100000            0.050000           mixed
            tier0  conf_0.10                  0.10       3      0.15          0.85            0.333333            0.666667                0.250000            0.133333           mixed
            tier0  conf_0.15                  0.15       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
            tier0  conf_0.20                  0.20       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
            tier0  conf_0.25                  0.25       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
      tier0_tier1    trained                  0.00      14      0.70          0.30            0.214286            0.428571                0.200000            0.157143           mixed
      tier0_tier1  conf_0.00                  0.00      14      0.70          0.30            0.214286            0.428571                0.200000            0.157143           mixed
      tier0_tier1  conf_0.05                  0.05       7      0.35          0.65            0.142857            0.571429                0.200000            0.100000           mixed
      tier0_tier1  conf_0.10                  0.10       3      0.15          0.85            0.333333            0.666667                0.333333            0.100000           mixed
      tier0_tier1  conf_0.15                  0.15       2      0.10          0.90            0.500000            1.000000                0.500000            0.133333           mixed
      tier0_tier1  conf_0.20                  0.20       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
      tier0_tier1  conf_0.25                  0.25       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
tier0_tier1_tier2    trained                  0.00      10      0.50          0.50            0.100000            0.400000                0.100000            0.100000           mixed
tier0_tier1_tier2  conf_0.00                  0.00      10      0.50          0.50            0.100000            0.400000                0.100000            0.100000           mixed
tier0_tier1_tier2  conf_0.05                  0.05       6      0.30          0.70            0.000000            0.500000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.10                  0.10       3      0.15          0.85            0.000000            0.333333                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.15                  0.15       2      0.10          0.90            0.000000            0.000000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.20                  0.20       2      0.10          0.90            0.000000            0.000000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.25                  0.25       2      0.10          0.90            0.000000            0.000000                0.000000            0.000000           mixed
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained              0.000000      16      0.80          0.20            0.250000            0.437500                0.233333            0.194872           mixed
            tier0  conf_0.00              0.000000      16      0.80          0.20            0.250000            0.437500                0.233333            0.194872           mixed
            tier0  conf_0.05              0.050000       8      0.40          0.60            0.125000            0.375000                0.100000            0.057143           mixed
            tier0  conf_0.10              0.100000       7      0.35          0.65            0.142857            0.428571                0.125000            0.066667           mixed
            tier0  conf_0.15              0.150000       3      0.15          0.85            0.000000            0.333333                0.000000            0.000000           mixed
            tier0  conf_0.20              0.200000       3      0.15          0.85            0.000000            0.333333                0.000000            0.000000           mixed
            tier0  conf_0.25              0.250000       2      0.10          0.90            0.000000            0.500000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.00              0.000000      12      0.60          0.40            0.083333            0.500000                0.200000            0.066667           mixed
      tier0_tier1    trained              0.038770       9      0.45          0.55            0.111111            0.444444                0.200000            0.066667           mixed
      tier0_tier1  conf_0.05              0.050000       8      0.40          0.60            0.125000            0.375000                0.200000            0.066667           mixed
      tier0_tier1  conf_0.10              0.100000       8      0.40          0.60            0.125000            0.375000                0.200000            0.066667           mixed
      tier0_tier1  conf_0.15              0.150000       5      0.25          0.75            0.200000            0.400000                0.250000            0.080000           mixed
      tier0_tier1  conf_0.20              0.200000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
      tier0_tier1  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
tier0_tier1_tier2  conf_0.00              0.000000      12      0.60          0.40            0.166667            0.500000                0.200000            0.080000           mixed
tier0_tier1_tier2    trained              0.002831      12      0.60          0.40            0.166667            0.500000                0.200000            0.080000           mixed
tier0_tier1_tier2  conf_0.05              0.050000       6      0.30          0.70            0.166667            0.500000                0.200000            0.066667           mixed
tier0_tier1_tier2  conf_0.10              0.100000       6      0.30          0.70            0.166667            0.500000                0.200000            0.066667           mixed
tier0_tier1_tier2  conf_0.15              0.150000       5      0.25          0.75            0.200000            0.600000                0.250000            0.080000           mixed
tier0_tier1_tier2  conf_0.20              0.200000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
tier0_tier1_tier2  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
```

## Diagnosis Mode Comparison
- Whole-run and post-alert-window diagnosis are exported together so the diagnosis mode can be evaluated directly.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile diagnosis_target    diagnosis_mode  family_acc  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau                       status  min_class_count  min_group_count    group_key  include_workload
            tier0       20      0.20      0.55      0.200000  0.171429               0.012219                 0.009179           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.25      0.65      0.250000  0.216667               0.021765                 0.018885           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.25      0.60      0.250000  0.205556               0.032220                 0.021885           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.25      0.45      0.250000  0.191409               0.027439                 0.027951           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.25      0.55      0.250000  0.202727               0.018355                 0.013132           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.25      0.55      0.250000  0.202597               0.021490                 0.019757           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.15      0.50      0.150000  0.114286               0.011448                 0.009179           mixed     hierarchical         whole_run        0.25      0.90          0.10            0.166667            0.500000                0.166667            0.123810            0.009456              0.008503           0.012198        0.000000                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.25      0.50      0.250000  0.211616              -0.002621                 0.003679           mixed     hierarchical         whole_run        0.30      0.70          0.30            0.214286            0.428571                0.200000            0.157143            0.012528              0.015208           0.005615        0.000000                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.15      0.50      0.150000  0.111111              -0.010509                -0.003592           mixed     hierarchical         whole_run        0.25      0.50          0.50            0.100000            0.400000                0.100000            0.100000            0.021425              0.019452           0.012607        0.000000                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.20      0.40      0.200000  0.161345               0.005666                 0.005677           mixed     hierarchical post_alert_window        0.25      0.80          0.20            0.250000            0.437500                0.233333            0.194872            0.009456              0.008503           0.012198        0.000000                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.15      0.55      0.150000  0.075000               0.001147                 0.009264           mixed     hierarchical post_alert_window        0.30      0.50          0.50            0.100000            0.400000                0.200000            0.066667            0.012528              0.015208           0.005615        0.038770                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.20      0.50      0.200000  0.080000              -0.002682                 0.000229           mixed     hierarchical post_alert_window        0.25      0.55          0.45            0.181818            0.454545                0.200000            0.088889            0.021425              0.019452           0.012607        0.002831                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.45      0.75      0.416667  0.415152               0.036886                 0.028002           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.50      0.85      0.500000  0.479365               0.043834                 0.035136           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.45      0.80      0.472222  0.433333               0.028194                 0.027326           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.763753         0.088201     0.148046              tier0           mixed
  BRANCH     0.814678         0.087263     0.098059              tier0           mixed
   CACHE     0.413926         0.308316     0.277757              tier0           mixed
   MEMBW     0.729898         0.177239     0.092864              tier0           mixed
     TLB     0.829353         0.100665     0.069982              tier0           mixed
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC               memory_io       0.227318         0.470141             0.048276                 0.204135                 0.050130           mixed
  BRANCH               memory_io       0.224181         0.513090             0.040820                 0.170525                 0.051384           mixed
   CACHE               memory_io       0.418138         0.216071             0.027568                 0.318398                 0.019826           mixed
   MEMBW               memory_io       0.212782         0.480044             0.130417                 0.144766                 0.031991           mixed
     TLB               memory_io       0.248574         0.517397             0.048622                 0.145044                 0.040364           mixed
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
            tier0                    1.0                     2906.387435                   2906.387435                  0.9                     45.0                  45.0                 0.9                 0.9                 0.9           mixed
      tier0_tier1                    1.0                     3600.000000                   3600.000000                  0.9                     45.0                  45.0                 0.9                 0.9                 0.9           mixed
tier0_tier1_tier2                    1.0                     3600.000000                   3600.000000                  0.9                     45.0                  45.0                 0.9                 0.9                 0.9           mixed
```

## Holdout Robustness (Workload Drift Proxy)
```text
           config  mean_pr_auc  worst_pr_auc  mean_roc_auc  mean_pr_auc_wc  worst_pr_auc_wc  mean_roc_auc_wc  pooled_pr_auc  pooled_roc_auc  pooled_pr_auc_wc  pooled_roc_auc_wc  mean_fpr  mean_tpr feature_profile
            tier0     0.824167          0.71          0.35             1.0              1.0              1.0       0.774642          0.3625               1.0                1.0  0.166667      0.75           mixed
      tier0_tier1     0.849167          0.71          0.40             1.0              1.0              1.0       0.820213          0.4000               1.0                1.0  0.166667      0.75           mixed
tier0_tier1_tier2     0.874167          0.81          0.45             1.0              1.0              1.0       0.806501          0.3625               1.0                1.0  0.166667      0.75           mixed
```

## Files
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/overall_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/config_runtime_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/run_context.json`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/case_inventory.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/case_block_traces.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/sequential_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/mechanism_group_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/overall_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/sequential_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/figures/fig_detection_latency.png`
