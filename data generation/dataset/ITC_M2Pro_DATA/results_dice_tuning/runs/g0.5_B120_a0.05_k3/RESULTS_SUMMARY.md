# DICE Full Retrain Results

## Setup
- Feature profile: mixed ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_core_5hz.csv', 'tier2': 'tier2_core_5hz.csv'})
- Protocol: global, benign-only fit/calibration, block_B=120, alpha=0.05, persist_k=3, gain=0.5
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
          mixed             tier0       24          46          2.166551   0.8000 0.931899         1.0        1.0            0.0           0.30              0.003338              0.007402                      0.0                 0.004208
          mixed       tier0_tier1       24          57          2.538163   0.8375 0.953625         1.0        1.0            0.0           0.45              0.000047              0.000116                      0.0                 0.000066
          mixed tier0_tier1_tier2       24          64          2.876629   0.8375 0.953625         1.0        1.0            0.0           0.45              0.000051              0.000129                      0.0                 0.000070
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
          mixed   ATOMIC   0.8125 0.804167         1.0        1.0          0.000051          0.000110                  0.0             0.000069       2.137644      0.000059         69.657704         0.000069
          mixed   BRANCH   0.9375 0.950000         1.0        1.0          0.000051          0.000184                  0.0             0.000123       3.565877      0.000133        123.965309         0.000123
          mixed    CACHE   0.8125 0.804167         1.0        1.0          0.000051          0.000111                  0.0             0.000065       2.151682      0.000060         66.088545         0.000065
          mixed    MEMBW   0.8750 0.887500         1.0        1.0          0.000051          0.000180                  0.0             0.000109       3.484057      0.000129        109.658500         0.000109
          mixed      TLB   0.7500 0.679167         1.0        1.0          0.000051          0.000123                  0.0             0.000059       2.389586      0.000072         60.062863         0.000059
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
            tier0       20       0.4      0.60           0.4  0.307071               0.023727                 0.016085           mixed
      tier0_tier1       20       0.3      0.55           0.3  0.184615               0.027171                 0.027846           mixed
tier0_tier1_tier2       20       0.4      0.60           0.4  0.348065               0.024920                 0.024870           mixed
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.20      0.70          0.20  0.184444               0.014868                 0.011616           mixed
      tier0_tier1       20      0.15      0.30          0.15  0.111111               0.041779                 0.027155           mixed
tier0_tier1_tier2       20      0.10      0.45          0.10  0.100000               0.030473                 0.013705           mixed
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.35      0.65          0.35  0.361429               0.015151                 0.015689           mixed
      tier0_tier1       20      0.30      0.50          0.30  0.260000               0.015997                 0.011297           mixed
tier0_tier1_tier2       20      0.20      0.70          0.20  0.175253               0.016541                 0.013261           mixed
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.55      0.70      0.472222  0.398551               0.034618                 0.037063           mixed
      tier0_tier1       20      0.45      0.65      0.416667  0.333333               0.026768                 0.027400           mixed
tier0_tier1_tier2       20      0.50      0.80      0.611111  0.495487               0.030900                 0.024472           mixed
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.20       0.6        0.30          0.20  0.175253      0.30          0.70            0.500000            0.666667                0.416667            0.260000              -0.000550                 0.006776            0.013412              0.011867           0.008813        0.102427           mixed
      tier0_tier1       20      0.25       0.5        0.25          0.25  0.208889      0.70          0.30            0.285714            0.500000                0.300000            0.226032               0.013020                 0.021809            0.016879              0.015895           0.014433        0.072312           mixed
tier0_tier1_tier2       20      0.20       0.4        0.35          0.20  0.191919      0.55          0.45            0.181818            0.454545                0.166667            0.160000               0.015257                 0.022884            0.017893              0.014710           0.010221        0.042249           mixed
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.15      0.60        0.30          0.15  0.130769       0.8           0.2            0.125000            0.625000                0.116667            0.107143              -0.000678                 0.009325            0.013412              0.011867           0.008813       -0.006064           mixed
      tier0_tier1       20      0.15      0.35        0.25          0.15  0.125253       0.6           0.4            0.166667            0.416667                0.133333            0.150000              -0.014299                 0.006988            0.016879              0.015895           0.014433       -0.064085           mixed
tier0_tier1_tier2       20      0.05      0.35        0.35          0.05  0.044444       0.6           0.4            0.083333            0.333333                0.100000            0.080000              -0.008456                 0.005321            0.017893              0.014710           0.010221       -0.073017           mixed
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0  conf_0.00              0.000000      12      0.60          0.40            0.250000            0.500000                0.250000            0.171429           mixed
            tier0  conf_0.05              0.050000       9      0.45          0.55            0.333333            0.555556                0.291667            0.194286           mixed
            tier0  conf_0.10              0.100000       5      0.25          0.75            0.400000            0.600000                0.222222            0.114286           mixed
            tier0    trained              0.102427       5      0.25          0.75            0.400000            0.600000                0.222222            0.114286           mixed
            tier0  conf_0.15              0.150000       4      0.20          0.80            0.500000            0.750000                0.333333            0.133333           mixed
            tier0  conf_0.20              0.200000       4      0.20          0.80            0.500000            0.750000                0.333333            0.133333           mixed
            tier0  conf_0.25              0.250000       3      0.15          0.85            0.333333            0.666667                0.250000            0.100000           mixed
      tier0_tier1  conf_0.00              0.000000      15      0.75          0.25            0.200000            0.400000                0.300000            0.137143           mixed
      tier0_tier1  conf_0.05              0.050000      12      0.60          0.40            0.250000            0.416667                0.333333            0.155556           mixed
      tier0_tier1    trained              0.072312      11      0.55          0.45            0.272727            0.454545                0.333333            0.168889           mixed
      tier0_tier1  conf_0.10              0.100000      10      0.50          0.50            0.300000            0.500000                0.333333            0.188889           mixed
      tier0_tier1  conf_0.15              0.150000       7      0.35          0.65            0.142857            0.285714                0.125000            0.057143           mixed
      tier0_tier1  conf_0.20              0.200000       6      0.30          0.70            0.166667            0.333333                0.125000            0.066667           mixed
      tier0_tier1  conf_0.25              0.250000       2      0.10          0.90            0.000000            0.500000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.00              0.000000      15      0.75          0.25            0.266667            0.400000                0.366667            0.257778           mixed
tier0_tier1_tier2    trained              0.042249      12      0.60          0.40            0.250000            0.416667                0.350000            0.210000           mixed
tier0_tier1_tier2  conf_0.05              0.050000      12      0.60          0.40            0.250000            0.416667                0.350000            0.210000           mixed
tier0_tier1_tier2  conf_0.10              0.100000      11      0.55          0.45            0.272727            0.363636                0.366667            0.250000           mixed
tier0_tier1_tier2  conf_0.15              0.150000       7      0.35          0.65            0.142857            0.285714                0.250000            0.066667           mixed
tier0_tier1_tier2  conf_0.20              0.200000       5      0.25          0.75            0.200000            0.400000                0.250000            0.066667           mixed
tier0_tier1_tier2  conf_0.25              0.250000       2      0.10          0.90            0.000000            0.500000                0.000000            0.000000           mixed
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained             -0.006064      15      0.75          0.25            0.133333            0.600000                0.116667            0.107143           mixed
            tier0  conf_0.00              0.000000      15      0.75          0.25            0.133333            0.600000                0.116667            0.107143           mixed
            tier0  conf_0.05              0.050000      10      0.50          0.50            0.200000            0.700000                0.166667            0.160000           mixed
            tier0  conf_0.10              0.100000       8      0.40          0.60            0.250000            0.875000                0.266667            0.200000           mixed
            tier0  conf_0.15              0.150000       5      0.25          0.75            0.200000            1.000000                0.111111            0.100000           mixed
            tier0  conf_0.20              0.200000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
            tier0  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
      tier0_tier1    trained             -0.064085      13      0.65          0.35            0.076923            0.307692                0.050000            0.044444           mixed
      tier0_tier1  conf_0.00              0.000000      13      0.65          0.35            0.076923            0.307692                0.050000            0.044444           mixed
      tier0_tier1  conf_0.05              0.050000       9      0.45          0.55            0.111111            0.333333                0.066667            0.057143           mixed
      tier0_tier1  conf_0.10              0.100000       7      0.35          0.65            0.142857            0.428571                0.125000            0.080000           mixed
      tier0_tier1  conf_0.15              0.150000       4      0.20          0.80            0.000000            0.500000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.20              0.200000       3      0.15          0.85            0.000000            0.333333                0.000000            0.000000           mixed
      tier0_tier1  conf_0.25              0.250000       3      0.15          0.85            0.000000            0.333333                0.000000            0.000000           mixed
tier0_tier1_tier2    trained             -0.073017      15      0.75          0.25            0.066667            0.400000                0.200000            0.066667           mixed
tier0_tier1_tier2  conf_0.00              0.000000      15      0.75          0.25            0.066667            0.400000                0.200000            0.066667           mixed
tier0_tier1_tier2  conf_0.05              0.050000       9      0.45          0.55            0.111111            0.222222                0.200000            0.100000           mixed
tier0_tier1_tier2  conf_0.10              0.100000       5      0.25          0.75            0.200000            0.400000                0.250000            0.200000           mixed
tier0_tier1_tier2  conf_0.15              0.150000       3      0.15          0.85            0.333333            0.666667                0.333333            0.200000           mixed
tier0_tier1_tier2  conf_0.20              0.200000       2      0.10          0.90            0.000000            0.500000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.25              0.250000       2      0.10          0.90            0.000000            0.500000                0.000000            0.000000           mixed
```

## Diagnosis Mode Comparison
- Whole-run and post-alert-window diagnosis are exported together so the diagnosis mode can be evaluated directly.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile diagnosis_target    diagnosis_mode  family_acc  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau                       status  min_class_count  min_group_count    group_key  include_workload
            tier0       20      0.40      0.60      0.400000  0.307071               0.023727                 0.016085           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.30      0.55      0.300000  0.184615               0.027171                 0.027846           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.40      0.60      0.400000  0.348065               0.024920                 0.024870           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.20      0.70      0.200000  0.184444               0.014868                 0.011616           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.15      0.30      0.150000  0.111111               0.041779                 0.027155           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.10      0.45      0.100000  0.100000               0.030473                 0.013705           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.20      0.60      0.200000  0.175253              -0.000550                 0.006776           mixed     hierarchical         whole_run        0.30      0.30          0.70            0.500000            0.666667                0.416667            0.260000            0.013412              0.011867           0.008813        0.102427                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.25      0.50      0.250000  0.208889               0.013020                 0.021809           mixed     hierarchical         whole_run        0.25      0.70          0.30            0.285714            0.500000                0.300000            0.226032            0.016879              0.015895           0.014433        0.072312                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.20      0.40      0.200000  0.191919               0.015257                 0.022884           mixed     hierarchical         whole_run        0.35      0.55          0.45            0.181818            0.454545                0.166667            0.160000            0.017893              0.014710           0.010221        0.042249                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.15      0.60      0.150000  0.130769              -0.000678                 0.009325           mixed     hierarchical post_alert_window        0.30      0.80          0.20            0.125000            0.625000                0.116667            0.107143            0.013412              0.011867           0.008813       -0.006064                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.15      0.35      0.150000  0.125253              -0.014299                 0.006988           mixed     hierarchical post_alert_window        0.25      0.60          0.40            0.166667            0.416667                0.133333            0.150000            0.016879              0.015895           0.014433       -0.064085                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.05      0.35      0.050000  0.044444              -0.008456                 0.005321           mixed     hierarchical post_alert_window        0.35      0.60          0.40            0.083333            0.333333                0.100000            0.080000            0.017893              0.014710           0.010221       -0.073017                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.55      0.70      0.472222  0.398551               0.034618                 0.037063           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.45      0.65      0.416667  0.333333               0.026768                 0.027400           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.50      0.80      0.611111  0.495487               0.030900                 0.024472           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.742036         0.122005     0.135959              tier0           mixed
  BRANCH     0.791629         0.083479     0.124893              tier0           mixed
   CACHE     0.563407         0.343767     0.092826              tier0           mixed
   MEMBW     0.804738         0.091818     0.103444              tier0           mixed
     TLB     0.743856         0.122896     0.133248              tier0           mixed
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC               memory_io       0.260851         0.436064             0.067344                 0.199660                 0.036080           mixed
  BRANCH               memory_io       0.233212         0.502235             0.043807                 0.177031                 0.043715           mixed
   CACHE               memory_io       0.447754         0.317064             0.057444                 0.131972                 0.045766           mixed
   MEMBW               memory_io       0.212989         0.530381             0.051401                 0.150865                 0.054364           mixed
     TLB               memory_io       0.281579         0.448684             0.060517                 0.177799                 0.031422           mixed
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
            tier0                    0.0                             0.0                           0.0                 0.30                    122.0                 644.0                 0.0                 0.2                0.25           mixed
      tier0_tier1                    0.0                             0.0                           0.0                 0.45                    122.0                 717.4                 0.0                 0.3                0.35           mixed
tier0_tier1_tier2                    0.0                             0.0                           0.0                 0.45                    122.0                 600.6                 0.0                 0.3                0.40           mixed
```

## Files
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B120_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B120_a0.05_k3/config_runtime_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B120_a0.05_k3/run_context.json`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B120_a0.05_k3/case_inventory.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B120_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B120_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B120_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B120_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B120_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B120_a0.05_k3/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B120_a0.05_k3/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B120_a0.05_k3/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B120_a0.05_k3/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B120_a0.05_k3/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B120_a0.05_k3/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B120_a0.05_k3/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B120_a0.05_k3/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B120_a0.05_k3/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B120_a0.05_k3/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B120_a0.05_k3/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B120_a0.05_k3/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B120_a0.05_k3/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B120_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B120_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B120_a0.05_k3/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B120_a0.05_k3/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B120_a0.05_k3/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B120_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B120_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B120_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B120_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B120_a0.05_k3/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B120_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B120_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B120_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B120_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B120_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B120_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B120_a0.05_k3/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B120_a0.05_k3/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B120_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B120_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B120_a0.05_k3/figures/fig_detection_latency.png`
