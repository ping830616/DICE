# DICE Full Retrain Results

## Setup
- Feature profile: full ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_full_5hz.csv', 'tier2': 'tier2_full_5hz.csv'})
- Protocol: global, benign-only fit/calibration, block_B=90, alpha=0.05, persist_k=3, gain=0.15
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
           full             tier0       24          46          2.220184   0.7875 0.921899         1.0        1.0            0.0           0.30              0.009117              0.020492                      0.0                 0.011347
           full       tier0_tier1       24          64          2.844551   0.8000 0.943234         1.0        1.0            0.0           0.50              0.013615              0.038475                      0.0                 0.018582
           full tier0_tier1_tier2       24          75          3.425494   0.9625 0.992487         1.0        1.0            0.0           0.95              0.003163              0.008619                      0.0                 0.004989
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc  pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
           full   ATOMIC   0.9375    0.95         1.0        1.0          0.003163          0.008284                  0.0             0.004860       2.618579      0.005121       4861.204493         0.004860
           full   BRANCH   1.0000    1.00         1.0        1.0          0.003163          0.007946                  0.0             0.005733       2.511641      0.004783       5733.815016         0.005733
           full    CACHE   0.9375    0.95         1.0        1.0          0.003163          0.010718                  0.0             0.007395       3.387724      0.007555       7396.065053         0.007395
           full    MEMBW   1.0000    1.00         1.0        1.0          0.003163          0.009084                  0.0             0.005905       2.871201      0.005921       5906.447994         0.005905
           full      TLB   0.9375    0.95         1.0        1.0          0.003163          0.006747                  0.0             0.004472       2.132644      0.003584       4473.322345         0.004472
```

## Paper-style Aggregates (Final Config)
- Base score mean stressor AUC-PR (all five): **0.9700**
- Base score mean stressor ROC-AUC (all five): **0.9625**
- WC score mean stressor AUC-PR (all five): **1.0000**
- WC score mean stressor ROC-AUC (all five): **1.0000**
- Base score mean stressor AUC-PR (excluding BRANCH/TLB): **0.9667**
- Base score mean stressor ROC-AUC (excluding BRANCH/TLB): **0.9583**
- WC score mean stressor AUC-PR (excluding BRANCH/TLB): **1.0000**
- WC score mean stressor ROC-AUC (excluding BRANCH/TLB): **1.0000**

## Diagnosis
- Feature-level diagnosis uses normalized whole-run residual-attribution prototypes as the default paper-facing result, with diagnosis-only filtering that removes monotonic counters and downweights generic memory-state features.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.40      0.55          0.40  0.348485               0.027146                 0.025305            full
      tier0_tier1       20      0.25      0.60          0.25  0.257143               0.016226                 0.014019            full
tier0_tier1_tier2       20      0.30      0.55          0.30  0.220952               0.019784                 0.015865            full
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.20      0.55          0.20  0.169697               0.016044                 0.010919            full
      tier0_tier1       20      0.25      0.50          0.25  0.258254               0.018970                 0.009751            full
tier0_tier1_tier2       20      0.20      0.40          0.20  0.207792               0.015162                 0.012094            full
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.20      0.45          0.20  0.190649               0.021017                 0.019769            full
      tier0_tier1       20      0.30      0.60          0.30  0.272727               0.017931                 0.011494            full
tier0_tier1_tier2       20      0.45      0.60          0.45  0.416508               0.014074                 0.010055            full
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20       0.6      0.90      0.500000  0.421818               0.036861                 0.039022            full
      tier0_tier1       20       0.5      0.85      0.444444  0.447343               0.017520                 0.011730            full
tier0_tier1_tier2       20       0.5      0.90      0.611111  0.540196               0.015279                 0.012481            full
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.35      0.50        0.45          0.35  0.315556      0.55          0.45            0.454545            0.454545                0.333333            0.266667              -0.005416                 0.003019            0.016424              0.018444           0.012757        0.037822            full
      tier0_tier1       20      0.35      0.65        0.50          0.35  0.374286      0.90          0.10            0.333333            0.666667                0.333333            0.364444               0.013473                 0.014180            0.023841              0.021242           0.010804       -0.030762            full
tier0_tier1_tier2       20      0.20      0.45        0.35          0.20  0.157143      0.70          0.30            0.285714            0.500000                0.266667            0.206061               0.013214                 0.011216            0.020164              0.018797           0.009789        0.019700            full
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.25      0.50        0.45          0.25  0.206234      0.70          0.30            0.285714            0.500000                0.266667            0.186667              -0.015539                 0.003534            0.016424              0.018444           0.012757       -0.074605            full
      tier0_tier1       20      0.35      0.55        0.50          0.35  0.320000      0.65          0.35            0.307692            0.461538                0.333333            0.296667               0.004272                 0.005631            0.023841              0.021242           0.010804        0.033748            full
tier0_tier1_tier2       20      0.25      0.35        0.35          0.25  0.200000      0.75          0.25            0.200000            0.333333                0.183333            0.168889               0.002172                 0.002588            0.020164              0.018797           0.009789       -0.097433            full
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0  conf_0.00              0.000000      12      0.60          0.40            0.500000            0.500000                0.433333            0.366667            full
            tier0    trained              0.037822       9      0.45          0.55            0.333333            0.333333                0.333333            0.213333            full
            tier0  conf_0.05              0.050000       9      0.45          0.55            0.333333            0.333333                0.333333            0.213333            full
            tier0  conf_0.10              0.100000       7      0.35          0.65            0.428571            0.428571                0.416667            0.233333            full
            tier0  conf_0.15              0.150000       6      0.30          0.70            0.500000            0.500000                0.416667            0.233333            full
            tier0  conf_0.20              0.200000       4      0.20          0.80            0.500000            0.500000                0.333333            0.133333            full
            tier0  conf_0.25              0.250000       1      0.05          0.95            1.000000            1.000000                1.000000            0.200000            full
      tier0_tier1    trained             -0.030762      17      0.85          0.15            0.352941            0.647059                0.366667            0.383175            full
      tier0_tier1  conf_0.00              0.000000      15      0.75          0.25            0.333333            0.666667                0.350000            0.344286            full
      tier0_tier1  conf_0.05              0.050000      12      0.60          0.40            0.250000            0.666667                0.266667            0.230000            full
      tier0_tier1  conf_0.10              0.100000       7      0.35          0.65            0.142857            0.571429                0.100000            0.133333            full
      tier0_tier1  conf_0.15              0.150000       3      0.15          0.85            0.000000            0.666667                0.000000            0.000000            full
      tier0_tier1  conf_0.20              0.200000       2      0.10          0.90            0.000000            1.000000                0.000000            0.000000            full
      tier0_tier1  conf_0.25              0.250000       1      0.05          0.95            0.000000            1.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.00              0.000000      17      0.85          0.15            0.235294            0.470588                0.233333            0.200000            full
tier0_tier1_tier2    trained              0.019700      15      0.75          0.25            0.200000            0.466667                0.200000            0.166667            full
tier0_tier1_tier2  conf_0.05              0.050000      10      0.50          0.50            0.300000            0.700000                0.300000            0.213333            full
tier0_tier1_tier2  conf_0.10              0.100000      10      0.50          0.50            0.300000            0.700000                0.300000            0.213333            full
tier0_tier1_tier2  conf_0.15              0.150000       5      0.25          0.75            0.000000            0.400000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.20              0.200000       3      0.15          0.85            0.000000            0.333333                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.25              0.250000       2      0.10          0.90            0.000000            0.500000                0.000000            0.000000            full
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained             -0.074605      14      0.70          0.30            0.285714            0.500000                0.266667            0.186667            full
            tier0  conf_0.00              0.000000      14      0.70          0.30            0.285714            0.500000                0.266667            0.186667            full
            tier0  conf_0.05              0.050000       8      0.40          0.60            0.500000            0.750000                0.333333            0.251429            full
            tier0  conf_0.10              0.100000       6      0.30          0.70            0.666667            0.833333                0.666667            0.300000            full
            tier0  conf_0.15              0.150000       2      0.10          0.90            0.000000            0.500000                0.000000            0.000000            full
            tier0  conf_0.20              0.200000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN            full
            tier0  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN            full
      tier0_tier1  conf_0.00              0.000000      13      0.65          0.35            0.307692            0.461538                0.416667            0.297143            full
      tier0_tier1    trained              0.033748      10      0.50          0.50            0.300000            0.400000                0.333333            0.237143            full
      tier0_tier1  conf_0.05              0.050000       8      0.40          0.60            0.250000            0.375000                0.266667            0.166667            full
      tier0_tier1  conf_0.10              0.100000       6      0.30          0.70            0.166667            0.333333                0.200000            0.066667            full
      tier0_tier1  conf_0.15              0.150000       5      0.25          0.75            0.000000            0.200000                0.000000            0.000000            full
      tier0_tier1  conf_0.20              0.200000       4      0.20          0.80            0.000000            0.250000                0.000000            0.000000            full
      tier0_tier1  conf_0.25              0.250000       2      0.10          0.90            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2    trained             -0.097433      17      0.85          0.15            0.235294            0.294118                0.216667            0.183333            full
tier0_tier1_tier2  conf_0.00              0.000000      12      0.60          0.40            0.250000            0.333333                0.233333            0.216667            full
tier0_tier1_tier2  conf_0.05              0.050000       7      0.35          0.65            0.142857            0.142857                0.200000            0.066667            full
tier0_tier1_tier2  conf_0.10              0.100000       4      0.20          0.80            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.15              0.150000       4      0.20          0.80            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.20              0.200000       4      0.20          0.80            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.25              0.250000       2      0.10          0.90            0.000000            0.000000                0.000000            0.000000            full
```

## Diagnosis Mode Comparison
- Whole-run and post-alert-window diagnosis are exported together so the diagnosis mode can be evaluated directly.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile diagnosis_target    diagnosis_mode  family_acc  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau                       status  min_class_count  min_group_count    group_key  include_workload
            tier0       20      0.40      0.55      0.400000  0.348485               0.027146                 0.025305            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.25      0.60      0.250000  0.257143               0.016226                 0.014019            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.30      0.55      0.300000  0.220952               0.019784                 0.015865            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.20      0.55      0.200000  0.169697               0.016044                 0.010919            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.25      0.50      0.250000  0.258254               0.018970                 0.009751            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.20      0.40      0.200000  0.207792               0.015162                 0.012094            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.35      0.50      0.350000  0.315556              -0.005416                 0.003019            full     hierarchical         whole_run        0.45      0.55          0.45            0.454545            0.454545                0.333333            0.266667            0.016424              0.018444           0.012757        0.037822                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.35      0.65      0.350000  0.374286               0.013473                 0.014180            full     hierarchical         whole_run        0.50      0.90          0.10            0.333333            0.666667                0.333333            0.364444            0.023841              0.021242           0.010804       -0.030762                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.20      0.45      0.200000  0.157143               0.013214                 0.011216            full     hierarchical         whole_run        0.35      0.70          0.30            0.285714            0.500000                0.266667            0.206061            0.020164              0.018797           0.009789        0.019700                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.25      0.50      0.250000  0.206234              -0.015539                 0.003534            full     hierarchical post_alert_window        0.45      0.70          0.30            0.285714            0.500000                0.266667            0.186667            0.016424              0.018444           0.012757       -0.074605                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.35      0.55      0.350000  0.320000               0.004272                 0.005631            full     hierarchical post_alert_window        0.50      0.65          0.35            0.307692            0.461538                0.333333            0.296667            0.023841              0.021242           0.010804        0.033748                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.25      0.35      0.250000  0.200000               0.002172                 0.002588            full     hierarchical post_alert_window        0.35      0.75          0.25            0.200000            0.333333                0.183333            0.168889            0.020164              0.018797           0.009789       -0.097433                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.60      0.90      0.500000  0.421818               0.036861                 0.039022            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.50      0.85      0.444444  0.447343               0.017520                 0.011730            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.50      0.90      0.611111  0.540196               0.015279                 0.012481            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.592782         0.256936     0.150282              tier0            full
  BRANCH     0.621062         0.218951     0.159987              tier0            full
   CACHE     0.473228         0.200147     0.326625              tier0            full
   MEMBW     0.640637         0.224938     0.134426              tier0            full
     TLB     0.560996         0.273824     0.165180              tier0            full
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC                 compute       0.353808         0.308875             0.101396                 0.117083                 0.118838            full
  BRANCH               memory_io       0.318456         0.377781             0.073957                 0.145257                 0.084548            full
   CACHE                 compute       0.497654         0.284795             0.061902                 0.082468                 0.073180            full
   MEMBW                 compute       0.330246         0.347178             0.086715                 0.116330                 0.119532            full
     TLB                 compute       0.359776         0.322762             0.100404                 0.117030                 0.100028            full
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
            tier0                    0.0                             0.0                           0.0                 0.30                     95.0                 729.0                0.20                0.20                 0.2            full
      tier0_tier1                    0.0                             0.0                           0.0                 0.50                     92.0                 685.9                0.35                0.35                 0.4            full
tier0_tier1_tier2                    0.0                             0.0                           0.0                 0.95                     92.0                 671.4                0.65                0.65                 0.8            full
```

## Files
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B90_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B90_a0.05_k3/config_runtime_summary.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B90_a0.05_k3/run_context.json`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B90_a0.05_k3/case_inventory.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B90_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B90_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B90_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B90_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B90_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B90_a0.05_k3/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B90_a0.05_k3/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B90_a0.05_k3/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B90_a0.05_k3/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B90_a0.05_k3/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B90_a0.05_k3/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B90_a0.05_k3/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B90_a0.05_k3/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B90_a0.05_k3/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B90_a0.05_k3/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B90_a0.05_k3/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B90_a0.05_k3/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B90_a0.05_k3/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B90_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B90_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B90_a0.05_k3/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B90_a0.05_k3/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B90_a0.05_k3/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B90_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B90_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B90_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B90_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B90_a0.05_k3/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B90_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B90_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B90_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B90_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B90_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B90_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B90_a0.05_k3/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B90_a0.05_k3/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B90_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B90_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B90_a0.05_k3/figures/fig_detection_latency.png`
