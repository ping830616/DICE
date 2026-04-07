# DICE Full Retrain Results

## Setup
- Feature profile: full ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_full_5hz.csv', 'tier2': 'tier2_full_5hz.csv'})
- Protocol: global, benign-only fit/calibration, block_B=120, alpha=0.05, persist_k=3, gain=0.5
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
           full             tier0       24          46          2.109874   0.8000 0.931899         1.0        1.0            0.0           0.30              0.003338              0.007402                      0.0                 0.004208
           full       tier0_tier1       24          64          2.779868   0.7875 0.941423         1.0        1.0            0.0           0.50              0.004931              0.016102                      0.0                 0.007755
           full tier0_tier1_tier2       24          75          3.380133   0.9375 0.986769         1.0        1.0            0.0           0.85              0.002611              0.007684                      0.0                 0.004107
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc  pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
           full   ATOMIC   0.8750  0.8875         1.0        1.0          0.002611          0.006980                  0.0             0.003071       2.672314      0.004369       3072.191917         0.003071
           full   BRANCH   1.0000  1.0000         1.0        1.0          0.002611          0.007612                  0.0             0.005312       2.914071      0.005000       5313.460718         0.005312
           full    CACHE   0.9375  0.9500         1.0        1.0          0.002611          0.009365                  0.0             0.006106       3.585308      0.006754       6107.387794         0.006106
           full    MEMBW   1.0000  1.0000         1.0        1.0          0.002611          0.008193                  0.0             0.005111       3.136536      0.005582       5111.685271         0.005111
           full      TLB   0.8750  0.8875         1.0        1.0          0.002611          0.006174                  0.0             0.003834       2.363770      0.003563       3834.946823         0.003834
```

## Paper-style Aggregates (Final Config)
- Base score mean stressor AUC-PR (all five): **0.9450**
- Base score mean stressor ROC-AUC (all five): **0.9375**
- WC score mean stressor AUC-PR (all five): **1.0000**
- WC score mean stressor ROC-AUC (all five): **1.0000**
- Base score mean stressor AUC-PR (excluding BRANCH/TLB): **0.9458**
- Base score mean stressor ROC-AUC (excluding BRANCH/TLB): **0.9375**
- WC score mean stressor AUC-PR (excluding BRANCH/TLB): **1.0000**
- WC score mean stressor ROC-AUC (excluding BRANCH/TLB): **1.0000**

## Diagnosis
- Feature-level diagnosis uses normalized whole-run residual-attribution prototypes as the default paper-facing result, with diagnosis-only filtering that removes monotonic counters and downweights generic memory-state features.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.40      0.60          0.40  0.307071               0.023727                 0.016085            full
      tier0_tier1       20      0.25      0.35          0.25  0.166667               0.014552                 0.007955            full
tier0_tier1_tier2       20      0.30      0.40          0.30  0.214286               0.028555                 0.023590            full
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.20       0.7          0.20  0.184444               0.014868                 0.011616            full
      tier0_tier1       20      0.15       0.4          0.15  0.130159               0.024047                 0.012804            full
tier0_tier1_tier2       20      0.20       0.4          0.20  0.189394               0.019061                 0.018219            full
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.35      0.65          0.35  0.361429               0.015151                 0.015689            full
      tier0_tier1       20      0.30      0.55          0.30  0.233333               0.020678                 0.020297            full
tier0_tier1_tier2       20      0.35      0.60          0.35  0.268065               0.013921                 0.012613            full
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.55      0.70      0.472222  0.398551               0.034618                 0.037063            full
      tier0_tier1       20      0.45      0.70      0.361111  0.314685               0.027451                 0.030720            full
tier0_tier1_tier2       20      0.45      0.95      0.583333  0.458333               0.020300                 0.017104            full
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.20      0.60        0.30          0.20  0.175253      0.30          0.70            0.500000            0.666667                0.416667            0.260000              -0.000550                 0.006776            0.013412              0.011867           0.008813        0.102427            full
      tier0_tier1       20      0.25      0.45        0.60          0.25  0.217172      0.70          0.30            0.214286            0.428571                0.166667            0.137143              -0.000606                 0.005324            0.020956              0.020402           0.015570       -0.009634            full
tier0_tier1_tier2       20      0.25      0.45        0.35          0.25  0.180000      0.75          0.25            0.266667            0.400000                0.250000            0.180000               0.014226                 0.018862            0.018701              0.015768           0.011391        0.084375            full
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.15      0.60        0.30          0.15  0.130769       0.8           0.2            0.125000            0.625000                0.116667            0.107143              -0.000678                 0.009325            0.013412              0.011867           0.008813       -0.006064            full
      tier0_tier1       20      0.25      0.45        0.60          0.25  0.218681       0.6           0.4            0.166667            0.416667                0.166667            0.130000              -0.003586                 0.003092            0.020956              0.020402           0.015570        0.005221            full
tier0_tier1_tier2       20      0.30      0.50        0.35          0.30  0.273260       0.8           0.2            0.250000            0.437500                0.250000            0.226667              -0.000376                 0.004234            0.018701              0.015768           0.011391       -0.137239            full
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0  conf_0.00              0.000000      12      0.60          0.40            0.250000            0.500000                0.250000            0.171429            full
            tier0  conf_0.05              0.050000       9      0.45          0.55            0.333333            0.555556                0.291667            0.194286            full
            tier0  conf_0.10              0.100000       5      0.25          0.75            0.400000            0.600000                0.222222            0.114286            full
            tier0    trained              0.102427       5      0.25          0.75            0.400000            0.600000                0.222222            0.114286            full
            tier0  conf_0.15              0.150000       4      0.20          0.80            0.500000            0.750000                0.333333            0.133333            full
            tier0  conf_0.20              0.200000       4      0.20          0.80            0.500000            0.750000                0.333333            0.133333            full
            tier0  conf_0.25              0.250000       3      0.15          0.85            0.333333            0.666667                0.250000            0.100000            full
      tier0_tier1    trained             -0.009634      14      0.70          0.30            0.214286            0.428571                0.166667            0.138889            full
      tier0_tier1  conf_0.00              0.000000      14      0.70          0.30            0.214286            0.428571                0.166667            0.138889            full
      tier0_tier1  conf_0.05              0.050000       8      0.40          0.60            0.375000            0.500000                0.250000            0.194286            full
      tier0_tier1  conf_0.10              0.100000       4      0.20          0.80            0.000000            0.250000                0.000000            0.000000            full
      tier0_tier1  conf_0.15              0.150000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000            full
      tier0_tier1  conf_0.20              0.200000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000            full
      tier0_tier1  conf_0.25              0.250000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.00              0.000000      17      0.85          0.15            0.235294            0.411765                0.250000            0.172308            full
tier0_tier1_tier2  conf_0.05              0.050000      13      0.65          0.35            0.230769            0.461538                0.200000            0.109091            full
tier0_tier1_tier2    trained              0.084375      11      0.55          0.45            0.272727            0.454545                0.200000            0.109091            full
tier0_tier1_tier2  conf_0.10              0.100000       9      0.45          0.55            0.333333            0.444444                0.200000            0.109091            full
tier0_tier1_tier2  conf_0.15              0.150000       6      0.30          0.70            0.166667            0.166667                0.250000            0.066667            full
tier0_tier1_tier2  conf_0.20              0.200000       4      0.20          0.80            0.250000            0.250000                0.250000            0.080000            full
tier0_tier1_tier2  conf_0.25              0.250000       3      0.15          0.85            0.333333            0.333333                0.333333            0.100000            full
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained             -0.006064      15      0.75          0.25            0.133333            0.600000                0.116667            0.107143            full
            tier0  conf_0.00              0.000000      15      0.75          0.25            0.133333            0.600000                0.116667            0.107143            full
            tier0  conf_0.05              0.050000      10      0.50          0.50            0.200000            0.700000                0.166667            0.160000            full
            tier0  conf_0.10              0.100000       8      0.40          0.60            0.250000            0.875000                0.266667            0.200000            full
            tier0  conf_0.15              0.150000       5      0.25          0.75            0.200000            1.000000                0.111111            0.100000            full
            tier0  conf_0.20              0.200000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN            full
            tier0  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN            full
      tier0_tier1  conf_0.00              0.000000      12      0.60          0.40            0.166667            0.416667                0.166667            0.130000            full
      tier0_tier1    trained              0.005221      12      0.60          0.40            0.166667            0.416667                0.166667            0.130000            full
      tier0_tier1  conf_0.05              0.050000       7      0.35          0.65            0.142857            0.571429                0.125000            0.080000            full
      tier0_tier1  conf_0.10              0.100000       5      0.25          0.75            0.000000            0.400000                0.000000            0.000000            full
      tier0_tier1  conf_0.15              0.150000       3      0.15          0.85            0.000000            0.333333                0.000000            0.000000            full
      tier0_tier1  conf_0.20              0.200000       3      0.15          0.85            0.000000            0.333333                0.000000            0.000000            full
      tier0_tier1  conf_0.25              0.250000       2      0.10          0.90            0.000000            0.500000                0.000000            0.000000            full
tier0_tier1_tier2    trained             -0.137239      18      0.90          0.10            0.277778            0.444444                0.300000            0.274286            full
tier0_tier1_tier2  conf_0.00              0.000000      13      0.65          0.35            0.230769            0.384615                0.266667            0.260000            full
tier0_tier1_tier2  conf_0.05              0.050000       7      0.35          0.65            0.285714            0.285714                0.250000            0.266667            full
tier0_tier1_tier2  conf_0.10              0.100000       6      0.30          0.70            0.333333            0.333333                0.375000            0.333333            full
tier0_tier1_tier2  conf_0.15              0.150000       3      0.15          0.85            0.333333            0.333333                0.333333            0.200000            full
tier0_tier1_tier2  conf_0.20              0.200000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN            full
```

## Diagnosis Mode Comparison
- Whole-run and post-alert-window diagnosis are exported together so the diagnosis mode can be evaluated directly.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile diagnosis_target    diagnosis_mode  family_acc  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau                       status  min_class_count  min_group_count    group_key  include_workload
            tier0       20      0.40      0.60      0.400000  0.307071               0.023727                 0.016085            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.25      0.35      0.250000  0.166667               0.014552                 0.007955            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.30      0.40      0.300000  0.214286               0.028555                 0.023590            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.20      0.70      0.200000  0.184444               0.014868                 0.011616            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.15      0.40      0.150000  0.130159               0.024047                 0.012804            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.20      0.40      0.200000  0.189394               0.019061                 0.018219            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.20      0.60      0.200000  0.175253              -0.000550                 0.006776            full     hierarchical         whole_run        0.30      0.30          0.70            0.500000            0.666667                0.416667            0.260000            0.013412              0.011867           0.008813        0.102427                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.25      0.45      0.250000  0.217172              -0.000606                 0.005324            full     hierarchical         whole_run        0.60      0.70          0.30            0.214286            0.428571                0.166667            0.137143            0.020956              0.020402           0.015570       -0.009634                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.25      0.45      0.250000  0.180000               0.014226                 0.018862            full     hierarchical         whole_run        0.35      0.75          0.25            0.266667            0.400000                0.250000            0.180000            0.018701              0.015768           0.011391        0.084375                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.15      0.60      0.150000  0.130769              -0.000678                 0.009325            full     hierarchical post_alert_window        0.30      0.80          0.20            0.125000            0.625000                0.116667            0.107143            0.013412              0.011867           0.008813       -0.006064                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.25      0.45      0.250000  0.218681              -0.003586                 0.003092            full     hierarchical post_alert_window        0.60      0.60          0.40            0.166667            0.416667                0.166667            0.130000            0.020956              0.020402           0.015570        0.005221                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.30      0.50      0.300000  0.273260              -0.000376                 0.004234            full     hierarchical post_alert_window        0.35      0.80          0.20            0.250000            0.437500                0.250000            0.226667            0.018701              0.015768           0.011391       -0.137239                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.55      0.70      0.472222  0.398551               0.034618                 0.037063            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.45      0.70      0.361111  0.314685               0.027451                 0.030720            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.45      0.95      0.583333  0.458333               0.020300                 0.017104            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.631896         0.267179     0.100925              tier0            full
  BRANCH     0.664592         0.216356     0.119053              tier0            full
   CACHE     0.548654         0.213069     0.238277              tier0            full
   MEMBW     0.671419         0.240140     0.088441              tier0            full
     TLB     0.613671         0.274661     0.111669              tier0            full
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC               memory_io       0.315948         0.359206             0.087438                 0.119144                 0.118264            full
  BRANCH               memory_io       0.285518         0.419288             0.064598                 0.144181                 0.086414            full
   CACHE               memory_io       0.422703         0.350762             0.058794                 0.092209                 0.075532            full
   MEMBW               memory_io       0.290841         0.398276             0.086333                 0.116209                 0.108341            full
     TLB               memory_io       0.311878         0.380515             0.092139                 0.118994                 0.096474            full
```

## Supervised Diagnosis
- This path is intended for expanded anomaly sets with repeated runs per workload-stressor pair. It is skipped automatically until each stressor has enough samples.
```text
           config                       status  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  min_class_count  min_group_count    group_key  include_workload feature_profile
            tier0 skipped_insufficient_samples       20       NaN       NaN           NaN       NaN                4                4 base_case_id                 1            full
      tier0_tier1 skipped_insufficient_samples       20       NaN       NaN           NaN       NaN                4                4 base_case_id                 1            full
tier0_tier1_tier2 skipped_insufficient_samples       20       NaN       NaN           NaN       NaN                4                4 base_case_id                 1            full
```

## Sequential Decisioning
```text
           config  benign_run_alert_rate  benign_persist_alerts_per_hour  benign_block_alerts_per_hour  anomaly_detect_rate  median_time_to_detect_s  p90_time_to_detect_s  detect_within_120s  detect_within_300s  detect_within_600s feature_profile
            tier0                    0.0                             0.0                           0.0                 0.30                    122.0                 644.0                 0.0                0.20                0.25            full
      tier0_tier1                    0.0                             0.0                           0.0                 0.50                    122.0                 760.6                 0.0                0.40                0.40            full
tier0_tier1_tier2                    0.0                             0.0                           0.0                 0.85                    122.0                 793.8                 0.0                0.55                0.65            full
```

## Files
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B120_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B120_a0.05_k3/config_runtime_summary.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B120_a0.05_k3/run_context.json`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B120_a0.05_k3/case_inventory.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B120_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B120_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B120_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B120_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B120_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B120_a0.05_k3/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B120_a0.05_k3/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B120_a0.05_k3/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B120_a0.05_k3/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B120_a0.05_k3/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B120_a0.05_k3/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B120_a0.05_k3/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B120_a0.05_k3/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B120_a0.05_k3/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B120_a0.05_k3/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B120_a0.05_k3/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B120_a0.05_k3/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B120_a0.05_k3/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B120_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B120_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B120_a0.05_k3/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B120_a0.05_k3/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B120_a0.05_k3/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B120_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B120_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B120_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B120_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B120_a0.05_k3/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B120_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B120_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B120_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B120_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B120_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B120_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B120_a0.05_k3/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B120_a0.05_k3/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B120_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B120_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B120_a0.05_k3/figures/fig_detection_latency.png`
