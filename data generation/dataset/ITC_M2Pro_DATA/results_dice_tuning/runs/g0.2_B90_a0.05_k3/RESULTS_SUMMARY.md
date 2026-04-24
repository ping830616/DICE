# DICE Full Retrain Results

## Setup
- Feature profile: mixed ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_core_5hz.csv', 'tier2': 'tier2_core_5hz.csv'})
- Protocol: global, benign-only fit/calibration, block_B=90, alpha=0.05, persist_k=3, gain=0.2
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
          mixed             tier0       24          46          2.285314   0.7875 0.921899         1.0        1.0            0.0           0.30              0.007469              0.016853                      0.0                 0.009301
          mixed       tier0_tier1       24          57          2.740578   0.8250 0.947375         1.0        1.0            0.0           0.45              0.000043              0.000108                      0.0                 0.000059
          mixed tier0_tier1_tier2       24          64          3.129152   0.8375 0.953625         1.0        1.0            0.0           0.45              0.000047              0.000118                      0.0                 0.000060
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
          mixed   ATOMIC   0.8125 0.804167         1.0        1.0          0.000047          0.000102                  0.0             0.000059       2.150438      0.000055         59.959619         0.000059
          mixed   BRANCH   0.9375 0.950000         1.0        1.0          0.000047          0.000162                  0.0             0.000115       3.395832      0.000115        115.513921         0.000115
          mixed    CACHE   0.8125 0.804167         1.0        1.0          0.000047          0.000101                  0.0             0.000058       2.131999      0.000054         59.051912         0.000058
          mixed    MEMBW   0.8750 0.887500         1.0        1.0          0.000047          0.000168                  0.0             0.000099       3.513341      0.000121        100.139550         0.000099
          mixed      TLB   0.7500 0.679167         1.0        1.0          0.000047          0.000108                  0.0             0.000055       2.272683      0.000061         56.456030         0.000055
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
            tier0       20      0.35      0.55          0.35  0.298485               0.028785                 0.022897           mixed
      tier0_tier1       20      0.35      0.70          0.35  0.261197               0.020232                 0.013753           mixed
tier0_tier1_tier2       20      0.45      0.75          0.45  0.441197               0.018890                 0.015125           mixed
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.20       0.6          0.20  0.206364               0.016440                 0.013867           mixed
      tier0_tier1       20      0.15       0.4          0.15  0.128205               0.044891                 0.016997           mixed
tier0_tier1_tier2       20      0.15       0.5          0.15  0.155556               0.037383                 0.019553           mixed
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.25      0.65          0.25  0.230000               0.017301                 0.014619           mixed
      tier0_tier1       20      0.30      0.60          0.30  0.298730               0.015710                 0.014322           mixed
tier0_tier1_tier2       20      0.25      0.65          0.25  0.235556               0.011929                 0.010947           mixed
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.60      0.90      0.500000  0.421818               0.037043                 0.037773           mixed
      tier0_tier1       20      0.45      0.80      0.416667  0.335664               0.027930                 0.029044           mixed
tier0_tier1_tier2       20      0.50      0.75      0.500000  0.449084               0.027620                 0.027758           mixed
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.40      0.55        0.55          0.40  0.354921      0.45          0.55            0.444444            0.555556                0.500000            0.293333              -0.008579                 0.005026            0.015910              0.015894           0.011619        0.092305           mixed
      tier0_tier1       20      0.25      0.65        0.35          0.25  0.196537      0.75          0.25            0.266667            0.666667                0.266667            0.212698              -0.001733                 0.000863            0.021347              0.019235           0.010553       -0.072389           mixed
tier0_tier1_tier2       20      0.45      0.75        0.35          0.45  0.412468      0.50          0.50            0.600000            0.900000                0.600000            0.593333               0.007035                 0.004916            0.018140              0.014871           0.014223        0.116141           mixed
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.40       0.6        0.55          0.40  0.362698       0.6           0.4            0.416667            0.666667                0.333333            0.295238              -0.017785                 0.004778            0.015910              0.015894           0.011619       -0.069478           mixed
      tier0_tier1       20      0.25       0.4        0.35          0.25  0.172727       0.6           0.4            0.333333            0.500000                0.266667            0.233333              -0.040144                -0.005154            0.021347              0.019235           0.010553       -0.160967           mixed
tier0_tier1_tier2       20      0.15       0.5        0.35          0.15  0.120000       0.6           0.4            0.083333            0.416667                0.066667            0.057143               0.006944                 0.010122            0.018140              0.014871           0.014223        0.073964           mixed
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0  conf_0.00              0.000000      12      0.60          0.40            0.500000            0.583333                0.466667            0.376667           mixed
            tier0  conf_0.05              0.050000       8      0.40          0.60            0.500000            0.500000                0.500000            0.320000           mixed
            tier0    trained              0.092305       7      0.35          0.65            0.428571            0.428571                0.500000            0.293333           mixed
            tier0  conf_0.10              0.100000       6      0.30          0.70            0.500000            0.500000                0.500000            0.293333           mixed
            tier0  conf_0.15              0.150000       5      0.25          0.75            0.600000            0.600000                0.500000            0.293333           mixed
            tier0  conf_0.20              0.200000       3      0.15          0.85            0.666667            0.666667                0.500000            0.160000           mixed
            tier0  conf_0.25              0.250000       3      0.15          0.85            0.666667            0.666667                0.500000            0.160000           mixed
      tier0_tier1    trained             -0.072389      15      0.75          0.25            0.266667            0.666667                0.266667            0.212698           mixed
      tier0_tier1  conf_0.00              0.000000      11      0.55          0.45            0.272727            0.636364                0.250000            0.155556           mixed
      tier0_tier1  conf_0.05              0.050000       7      0.35          0.65            0.285714            0.714286                0.250000            0.100000           mixed
      tier0_tier1  conf_0.10              0.100000       6      0.30          0.70            0.166667            0.666667                0.250000            0.066667           mixed
      tier0_tier1  conf_0.15              0.150000       4      0.20          0.80            0.250000            0.500000                0.333333            0.080000           mixed
      tier0_tier1  conf_0.20              0.200000       4      0.20          0.80            0.250000            0.500000                0.333333            0.080000           mixed
      tier0_tier1  conf_0.25              0.250000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.00              0.000000      14      0.70          0.30            0.500000            0.785714                0.450000            0.447619           mixed
tier0_tier1_tier2  conf_0.05              0.050000       7      0.35          0.65            0.428571            0.714286                0.444444            0.200000           mixed
tier0_tier1_tier2  conf_0.10              0.100000       7      0.35          0.65            0.428571            0.714286                0.444444            0.200000           mixed
tier0_tier1_tier2    trained              0.116141       7      0.35          0.65            0.428571            0.714286                0.444444            0.200000           mixed
tier0_tier1_tier2  conf_0.15              0.150000       4      0.20          0.80            0.500000            0.500000                0.333333            0.133333           mixed
tier0_tier1_tier2  conf_0.20              0.200000       3      0.15          0.85            0.666667            0.666667                0.500000            0.160000           mixed
tier0_tier1_tier2  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained             -0.069478      12      0.60          0.40            0.416667            0.666667                0.333333            0.295238           mixed
            tier0  conf_0.00              0.000000      12      0.60          0.40            0.416667            0.666667                0.333333            0.295238           mixed
            tier0  conf_0.05              0.050000       8      0.40          0.60            0.375000            0.625000                0.266667            0.240000           mixed
            tier0  conf_0.10              0.100000       4      0.20          0.80            0.250000            0.500000                0.333333            0.200000           mixed
            tier0  conf_0.15              0.150000       3      0.15          0.85            0.333333            0.666667                0.500000            0.200000           mixed
            tier0  conf_0.20              0.200000       1      0.05          0.95            0.000000            1.000000                0.000000            0.000000           mixed
            tier0  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
      tier0_tier1    trained             -0.160967      12      0.60          0.40            0.333333            0.500000                0.266667            0.247619           mixed
      tier0_tier1  conf_0.00              0.000000      10      0.50          0.50            0.300000            0.500000                0.291667            0.247619           mixed
      tier0_tier1  conf_0.05              0.050000       6      0.30          0.70            0.166667            0.500000                0.166667            0.080000           mixed
      tier0_tier1  conf_0.10              0.100000       5      0.25          0.75            0.000000            0.400000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.15              0.150000       2      0.10          0.90            0.000000            0.500000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.20              0.200000       2      0.10          0.90            0.000000            0.500000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.25              0.250000       2      0.10          0.90            0.000000            0.500000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.00              0.000000      14      0.70          0.30            0.071429            0.428571                0.066667            0.080000           mixed
tier0_tier1_tier2  conf_0.05              0.050000      10      0.50          0.50            0.000000            0.400000                0.000000            0.000000           mixed
tier0_tier1_tier2    trained              0.073964       9      0.45          0.55            0.000000            0.333333                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.10              0.100000       7      0.35          0.65            0.000000            0.285714                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.15              0.150000       4      0.20          0.80            0.000000            0.250000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.20              0.200000       4      0.20          0.80            0.000000            0.250000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.25              0.250000       4      0.20          0.80            0.000000            0.250000                0.000000            0.000000           mixed
```

## Diagnosis Mode Comparison
- Whole-run and post-alert-window diagnosis are exported together so the diagnosis mode can be evaluated directly.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile diagnosis_target    diagnosis_mode  family_acc  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau                       status  min_class_count  min_group_count    group_key  include_workload
            tier0       20      0.35      0.55      0.350000  0.298485               0.028785                 0.022897           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.35      0.70      0.350000  0.261197               0.020232                 0.013753           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.45      0.75      0.450000  0.441197               0.018890                 0.015125           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.20      0.60      0.200000  0.206364               0.016440                 0.013867           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.15      0.40      0.150000  0.128205               0.044891                 0.016997           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.15      0.50      0.150000  0.155556               0.037383                 0.019553           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.40      0.55      0.400000  0.354921              -0.008579                 0.005026           mixed     hierarchical         whole_run        0.55      0.45          0.55            0.444444            0.555556                0.500000            0.293333            0.015910              0.015894           0.011619        0.092305                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.25      0.65      0.250000  0.196537              -0.001733                 0.000863           mixed     hierarchical         whole_run        0.35      0.75          0.25            0.266667            0.666667                0.266667            0.212698            0.021347              0.019235           0.010553       -0.072389                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.45      0.75      0.450000  0.412468               0.007035                 0.004916           mixed     hierarchical         whole_run        0.35      0.50          0.50            0.600000            0.900000                0.600000            0.593333            0.018140              0.014871           0.014223        0.116141                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.40      0.60      0.400000  0.362698              -0.017785                 0.004778           mixed     hierarchical post_alert_window        0.55      0.60          0.40            0.416667            0.666667                0.333333            0.295238            0.015910              0.015894           0.011619       -0.069478                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.25      0.40      0.250000  0.172727              -0.040144                -0.005154           mixed     hierarchical post_alert_window        0.35      0.60          0.40            0.333333            0.500000                0.266667            0.233333            0.021347              0.019235           0.010553       -0.160967                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.15      0.50      0.150000  0.120000               0.006944                 0.010122           mixed     hierarchical post_alert_window        0.35      0.60          0.40            0.083333            0.416667                0.066667            0.057143            0.018140              0.014871           0.014223        0.073964                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.60      0.90      0.500000  0.421818               0.037043                 0.037773           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.45      0.80      0.416667  0.335664               0.027930                 0.029044           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.50      0.75      0.500000  0.449084               0.027620                 0.027758           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.708811         0.149805     0.141384              tier0           mixed
  BRANCH     0.777600         0.090895     0.131504              tier0           mixed
   CACHE     0.550426         0.352865     0.096709              tier0           mixed
   MEMBW     0.793425         0.099404     0.107172              tier0           mixed
     TLB     0.718073         0.142456     0.139471              tier0           mixed
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC               memory_io       0.260363         0.419736             0.087890                 0.195100                 0.036911           mixed
  BRANCH               memory_io       0.235557         0.492518             0.047909                 0.175790                 0.048227           mixed
   CACHE               memory_io       0.459978         0.294514             0.064531                 0.127852                 0.053125           mixed
   MEMBW               memory_io       0.223178         0.512096             0.055175                 0.148318                 0.061233           mixed
     TLB               memory_io       0.291179         0.431024             0.072493                 0.174211                 0.031093           mixed
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
            tier0                    0.0                             0.0                           0.0                 0.30                     94.5                 723.0                 0.2                 0.2                0.20           mixed
      tier0_tier1                    0.0                             0.0                           0.0                 0.45                     92.0                 657.8                 0.3                 0.3                0.35           mixed
tier0_tier1_tier2                    0.0                             0.0                           0.0                 0.45                     92.0                 544.6                 0.3                 0.3                0.40           mixed
```

## Files
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B90_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B90_a0.05_k3/config_runtime_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B90_a0.05_k3/run_context.json`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B90_a0.05_k3/case_inventory.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B90_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B90_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B90_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B90_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B90_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B90_a0.05_k3/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B90_a0.05_k3/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B90_a0.05_k3/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B90_a0.05_k3/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B90_a0.05_k3/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B90_a0.05_k3/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B90_a0.05_k3/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B90_a0.05_k3/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B90_a0.05_k3/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B90_a0.05_k3/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B90_a0.05_k3/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B90_a0.05_k3/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B90_a0.05_k3/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B90_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B90_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B90_a0.05_k3/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B90_a0.05_k3/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B90_a0.05_k3/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B90_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B90_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B90_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B90_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B90_a0.05_k3/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B90_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B90_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B90_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B90_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B90_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B90_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B90_a0.05_k3/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B90_a0.05_k3/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B90_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B90_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B90_a0.05_k3/figures/fig_detection_latency.png`
