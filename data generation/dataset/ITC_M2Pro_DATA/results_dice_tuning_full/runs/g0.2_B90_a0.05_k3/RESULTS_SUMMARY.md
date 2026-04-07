# DICE Full Retrain Results

## Setup
- Feature profile: full ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_full_5hz.csv', 'tier2': 'tier2_full_5hz.csv'})
- Protocol: global, benign-only fit/calibration, block_B=90, alpha=0.05, persist_k=3, gain=0.2
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
           full             tier0       24          46          2.104064   0.7875 0.921899         1.0        1.0            0.0           0.30              0.007469              0.016853                      0.0                 0.009301
           full       tier0_tier1       24          64          2.755167   0.7875 0.941423         1.0        1.0            0.0           0.50              0.010952              0.032657                      0.0                 0.015514
           full tier0_tier1_tier2       24          75          3.315065   0.9625 0.992487         1.0        1.0            0.0           0.95              0.003144              0.008741                      0.0                 0.004927
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc  pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
           full   ATOMIC   0.9375    0.95         1.0        1.0          0.003144          0.008271                  0.0             0.004589       2.630457      0.005127       4589.928163         0.004589
           full   BRANCH   1.0000    1.00         1.0        1.0          0.003144          0.008186                  0.0             0.005874       2.603522      0.005043       5875.427194         0.005874
           full    CACHE   0.9375    0.95         1.0        1.0          0.003144          0.010768                  0.0             0.007335       3.424447      0.007624       7335.758211         0.007335
           full    MEMBW   1.0000    1.00         1.0        1.0          0.003144          0.009186                  0.0             0.005862       2.921366      0.006042       5862.753724         0.005862
           full      TLB   0.9375    0.95         1.0        1.0          0.003144          0.006824                  0.0             0.004514       2.170159      0.003680       4515.478490         0.004514
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
            tier0       20      0.35      0.55          0.35  0.298485               0.028785                 0.022897            full
      tier0_tier1       20      0.20      0.45          0.20  0.177143               0.015047                 0.009917            full
tier0_tier1_tier2       20      0.30      0.55          0.30  0.206667               0.021357                 0.018252            full
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.20       0.6          0.20  0.206364               0.016440                 0.013867            full
      tier0_tier1       20      0.20       0.5          0.20  0.218254               0.018946                 0.011307            full
tier0_tier1_tier2       20      0.15       0.4          0.15  0.134444               0.019505                 0.012339            full
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.25      0.65          0.25  0.230000               0.017301                 0.014619            full
      tier0_tier1       20      0.30      0.55          0.30  0.286061               0.019472                 0.016575            full
tier0_tier1_tier2       20      0.45      0.55          0.45  0.416508               0.014270                 0.009711            full
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20       0.6       0.9      0.500000  0.421818               0.037043                 0.037773            full
      tier0_tier1       20       0.4       0.8      0.333333  0.279365               0.020626                 0.018746            full
tier0_tier1_tier2       20       0.5       0.9      0.555556  0.508772               0.016437                 0.013681            full
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.40      0.55        0.55          0.40  0.354921      0.45          0.55            0.444444            0.555556                0.500000            0.293333              -0.008579                 0.005026            0.015910              0.015894           0.011619        0.092305            full
      tier0_tier1       20      0.35      0.60        0.45          0.35  0.360952      0.85          0.15            0.294118            0.588235                0.283333            0.320000               0.012178                 0.012293            0.022644              0.022581           0.009018       -0.037993            full
tier0_tier1_tier2       20      0.25      0.50        0.30          0.25  0.168889      0.60          0.40            0.250000            0.500000                0.333333            0.180000               0.012822                 0.016733            0.019837              0.018174           0.008984        0.032502            full
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.40      0.60        0.55          0.40  0.362698      0.60          0.40            0.416667            0.666667                0.333333            0.295238              -0.017785                 0.004778            0.015910              0.015894           0.011619       -0.069478            full
      tier0_tier1       20      0.30      0.45        0.45          0.30  0.313333      0.50          0.50            0.300000            0.400000                0.250000            0.280000               0.000793                 0.005953            0.022644              0.022581           0.009018        0.025047            full
tier0_tier1_tier2       20      0.25      0.35        0.30          0.25  0.174603      0.65          0.35            0.230769            0.307692                0.200000            0.160000               0.002658                 0.000333            0.019837              0.018174           0.008984       -0.013077            full
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0  conf_0.00              0.000000      12      0.60          0.40            0.500000            0.583333                0.466667            0.376667            full
            tier0  conf_0.05              0.050000       8      0.40          0.60            0.500000            0.500000                0.500000            0.320000            full
            tier0    trained              0.092305       7      0.35          0.65            0.428571            0.428571                0.500000            0.293333            full
            tier0  conf_0.10              0.100000       6      0.30          0.70            0.500000            0.500000                0.500000            0.293333            full
            tier0  conf_0.15              0.150000       5      0.25          0.75            0.600000            0.600000                0.500000            0.293333            full
            tier0  conf_0.20              0.200000       3      0.15          0.85            0.666667            0.666667                0.500000            0.160000            full
            tier0  conf_0.25              0.250000       3      0.15          0.85            0.666667            0.666667                0.500000            0.160000            full
      tier0_tier1    trained             -0.037993      18      0.90          0.10            0.333333            0.555556                0.350000            0.353016            full
      tier0_tier1  conf_0.00              0.000000      13      0.65          0.35            0.230769            0.538462                0.183333            0.194286            full
      tier0_tier1  conf_0.05              0.050000      10      0.50          0.50            0.200000            0.500000                0.166667            0.180000            full
      tier0_tier1  conf_0.10              0.100000       7      0.35          0.65            0.000000            0.285714                0.000000            0.000000            full
      tier0_tier1  conf_0.15              0.150000       4      0.20          0.80            0.000000            0.500000                0.000000            0.000000            full
      tier0_tier1  conf_0.20              0.200000       1      0.05          0.95            0.000000            1.000000                0.000000            0.000000            full
      tier0_tier1  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN            full
tier0_tier1_tier2  conf_0.00              0.000000      16      0.80          0.20            0.250000            0.500000                0.250000            0.172308            full
tier0_tier1_tier2    trained              0.032502      14      0.70          0.30            0.285714            0.571429                0.250000            0.192308            full
tier0_tier1_tier2  conf_0.05              0.050000      14      0.70          0.30            0.285714            0.571429                0.250000            0.192308            full
tier0_tier1_tier2  conf_0.10              0.100000      10      0.50          0.50            0.300000            0.700000                0.300000            0.213333            full
tier0_tier1_tier2  conf_0.15              0.150000       4      0.20          0.80            0.000000            0.250000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.20              0.200000       3      0.15          0.85            0.000000            0.333333                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.25              0.250000       2      0.10          0.90            0.000000            0.500000                0.000000            0.000000            full
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained             -0.069478      12      0.60          0.40            0.416667            0.666667                0.333333            0.295238            full
            tier0  conf_0.00              0.000000      12      0.60          0.40            0.416667            0.666667                0.333333            0.295238            full
            tier0  conf_0.05              0.050000       8      0.40          0.60            0.375000            0.625000                0.266667            0.240000            full
            tier0  conf_0.10              0.100000       4      0.20          0.80            0.250000            0.500000                0.333333            0.200000            full
            tier0  conf_0.15              0.150000       3      0.15          0.85            0.333333            0.666667                0.500000            0.200000            full
            tier0  conf_0.20              0.200000       1      0.05          0.95            0.000000            1.000000                0.000000            0.000000            full
            tier0  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN            full
      tier0_tier1  conf_0.00              0.000000      12      0.60          0.40            0.250000            0.416667                0.183333            0.226667            full
      tier0_tier1    trained              0.025047      10      0.50          0.50            0.300000            0.400000                0.250000            0.280000            full
      tier0_tier1  conf_0.05              0.050000       8      0.40          0.60            0.250000            0.375000                0.208333            0.200000            full
      tier0_tier1  conf_0.10              0.100000       5      0.25          0.75            0.000000            0.200000                0.000000            0.000000            full
      tier0_tier1  conf_0.15              0.150000       5      0.25          0.75            0.000000            0.200000                0.000000            0.000000            full
      tier0_tier1  conf_0.20              0.200000       4      0.20          0.80            0.000000            0.000000                0.000000            0.000000            full
      tier0_tier1  conf_0.25              0.250000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2    trained             -0.013077      12      0.60          0.40            0.250000            0.333333                0.233333            0.200000            full
tier0_tier1_tier2  conf_0.00              0.000000      12      0.60          0.40            0.250000            0.333333                0.233333            0.200000            full
tier0_tier1_tier2  conf_0.05              0.050000       8      0.40          0.60            0.250000            0.250000                0.200000            0.180000            full
tier0_tier1_tier2  conf_0.10              0.100000       7      0.35          0.65            0.142857            0.142857                0.100000            0.080000            full
tier0_tier1_tier2  conf_0.15              0.150000       4      0.20          0.80            0.250000            0.250000                0.166667            0.100000            full
tier0_tier1_tier2  conf_0.20              0.200000       2      0.10          0.90            0.500000            0.500000                0.500000            0.200000            full
tier0_tier1_tier2  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN            full
```

## Diagnosis Mode Comparison
- Whole-run and post-alert-window diagnosis are exported together so the diagnosis mode can be evaluated directly.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile diagnosis_target    diagnosis_mode  family_acc  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau                       status  min_class_count  min_group_count    group_key  include_workload
            tier0       20      0.35      0.55      0.350000  0.298485               0.028785                 0.022897            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.20      0.45      0.200000  0.177143               0.015047                 0.009917            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.30      0.55      0.300000  0.206667               0.021357                 0.018252            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.20      0.60      0.200000  0.206364               0.016440                 0.013867            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.20      0.50      0.200000  0.218254               0.018946                 0.011307            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.15      0.40      0.150000  0.134444               0.019505                 0.012339            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.40      0.55      0.400000  0.354921              -0.008579                 0.005026            full     hierarchical         whole_run        0.55      0.45          0.55            0.444444            0.555556                0.500000            0.293333            0.015910              0.015894           0.011619        0.092305                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.35      0.60      0.350000  0.360952               0.012178                 0.012293            full     hierarchical         whole_run        0.45      0.85          0.15            0.294118            0.588235                0.283333            0.320000            0.022644              0.022581           0.009018       -0.037993                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.25      0.50      0.250000  0.168889               0.012822                 0.016733            full     hierarchical         whole_run        0.30      0.60          0.40            0.250000            0.500000                0.333333            0.180000            0.019837              0.018174           0.008984        0.032502                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.40      0.60      0.400000  0.362698              -0.017785                 0.004778            full     hierarchical post_alert_window        0.55      0.60          0.40            0.416667            0.666667                0.333333            0.295238            0.015910              0.015894           0.011619       -0.069478                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.30      0.45      0.300000  0.313333               0.000793                 0.005953            full     hierarchical post_alert_window        0.45      0.50          0.50            0.300000            0.400000                0.250000            0.280000            0.022644              0.022581           0.009018        0.025047                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.25      0.35      0.250000  0.174603               0.002658                 0.000333            full     hierarchical post_alert_window        0.30      0.65          0.35            0.230769            0.307692                0.200000            0.160000            0.019837              0.018174           0.008984       -0.013077                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.60      0.90      0.500000  0.421818               0.037043                 0.037773            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.40      0.80      0.333333  0.279365               0.020626                 0.018746            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.50      0.90      0.555556  0.508772               0.016437                 0.013681            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.605756         0.261956     0.132287              tier0            full
  BRANCH     0.632375         0.220232     0.147393              tier0            full
   CACHE     0.491379         0.205721     0.302900              tier0            full
   MEMBW     0.651094         0.230733     0.118173              tier0            full
     TLB     0.575323         0.277735     0.146943              tier0            full
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC                 compute       0.342269         0.317818             0.100563                 0.119162                 0.120188            full
  BRANCH               memory_io       0.307701         0.386360             0.073142                 0.146238                 0.086559            full
   CACHE                 compute       0.479209         0.298870             0.062282                 0.084580                 0.075059            full
   MEMBW               memory_io       0.316478         0.359582             0.088987                 0.117300                 0.117654            full
     TLB                 compute       0.344290         0.335495             0.100665                 0.118866                 0.100685            full
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
            tier0                    0.0                             0.0                           0.0                 0.30                     94.5                 723.0                0.20                0.20                 0.2            full
      tier0_tier1                    0.0                             0.0                           0.0                 0.50                     92.0                 690.3                0.35                0.35                 0.4            full
tier0_tier1_tier2                    0.0                             0.0                           0.0                 0.95                     92.0                 821.8                0.60                0.60                 0.7            full
```

## Files
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B90_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B90_a0.05_k3/config_runtime_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B90_a0.05_k3/run_context.json`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B90_a0.05_k3/case_inventory.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B90_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B90_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B90_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B90_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B90_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B90_a0.05_k3/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B90_a0.05_k3/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B90_a0.05_k3/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B90_a0.05_k3/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B90_a0.05_k3/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B90_a0.05_k3/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B90_a0.05_k3/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B90_a0.05_k3/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B90_a0.05_k3/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B90_a0.05_k3/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B90_a0.05_k3/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B90_a0.05_k3/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B90_a0.05_k3/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B90_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B90_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B90_a0.05_k3/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B90_a0.05_k3/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B90_a0.05_k3/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B90_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B90_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B90_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B90_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B90_a0.05_k3/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B90_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B90_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B90_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B90_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B90_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B90_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B90_a0.05_k3/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B90_a0.05_k3/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B90_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B90_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B90_a0.05_k3/figures/fig_detection_latency.png`
