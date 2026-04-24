# DICE Full Retrain Results

## Setup
- Feature profile: full ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_full_5hz.csv', 'tier2': 'tier2_full_5hz.csv'})
- Protocol: global, benign-only fit/calibration, block_B=30, alpha=0.05, persist_k=3, gain=0.15
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
           full             tier0       24          46          2.336001   0.8000 0.931899         1.0        1.0           0.25           0.30              0.011353              0.023357                      0.0                 0.012710
           full       tier0_tier1       24          64          3.024285   0.8375 0.960040         1.0        1.0           0.00           0.65              0.017081              0.048509                      0.0                 0.022866
           full tier0_tier1_tier2       24          75          3.631685   0.9750 0.995119         1.0        1.0           0.00           0.95              0.002866              0.007781                      0.0                 0.004498
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc  pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
           full   ATOMIC   0.9375    0.95         1.0        1.0          0.002866          0.007229                  0.0             0.004334       2.522159      0.004364       4334.912663         0.004334
           full   BRANCH   1.0000    1.00         1.0        1.0          0.002866          0.009559                  0.0             0.006835       3.334957      0.006694       6835.645447         0.006835
           full    CACHE   0.9375    0.95         1.0        1.0          0.002866          0.009274                  0.0             0.006087       3.235287      0.006408       6087.919391         0.006087
           full    MEMBW   1.0000    1.00         1.0        1.0          0.002866          0.008810                  0.0             0.004991       3.073580      0.005944       4991.718049         0.004991
           full      TLB   1.0000    1.00         1.0        1.0          0.002866          0.007220                  0.0             0.004785       2.518785      0.004354       4785.542585         0.004785
```

## Paper-style Aggregates (Final Config)
- Base score mean stressor AUC-PR (all five): **0.9800**
- Base score mean stressor ROC-AUC (all five): **0.9750**
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
            tier0       20      0.30      0.55          0.30  0.232900               0.027017                 0.021021            full
      tier0_tier1       20      0.25      0.50          0.25  0.257143               0.014869                 0.013183            full
tier0_tier1_tier2       20      0.35      0.55          0.35  0.256667               0.018436                 0.018142            full
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.25      0.50          0.25  0.212727               0.017396                 0.014295            full
      tier0_tier1       20      0.10      0.25          0.10  0.100000               0.099244                 0.043607            full
tier0_tier1_tier2       20      0.10      0.15          0.10  0.080000               0.027526                 0.019765            full
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.25      0.55          0.25  0.226364               0.016676                 0.010039            full
      tier0_tier1       20      0.30      0.65          0.30  0.226667               0.018908                 0.015155            full
tier0_tier1_tier2       20      0.40      0.60          0.40  0.370346               0.016561                 0.013429            full
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20       0.6      0.85      0.500000  0.421818               0.034120                 0.036788            full
      tier0_tier1       20       0.5      0.85      0.444444  0.447343               0.016332                 0.012214            full
tier0_tier1_tier2       20       0.5      0.90      0.611111  0.540196               0.014800                 0.013177            full
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.40      0.60         0.5          0.40  0.331313       0.5           0.5                0.40            0.500000                0.400000            0.260000               0.001758                 0.011079            0.016657              0.017394           0.012575        0.113357            full
      tier0_tier1       20      0.35      0.55         0.5          0.35  0.374286       0.6           0.4                0.25            0.500000                0.233333            0.277778               0.011036                 0.010779            0.021357              0.016792           0.006667        0.036422            full
tier0_tier1_tier2       20      0.20      0.45         0.4          0.20  0.157143       0.6           0.4                0.25            0.583333                0.333333            0.213333               0.013617                 0.015775            0.020789              0.018969           0.008422        0.043865            full
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20       0.4      0.65         0.5           0.4  0.364444      0.55          0.45            0.272727            0.454545                0.150000            0.120000              -0.014215                 0.006782            0.016657              0.017394           0.012575        0.004508            full
      tier0_tier1       20       0.2      0.35         0.5           0.2  0.164444      0.25          0.75            0.200000            0.400000                0.250000            0.133333              -0.011528                 0.029993            0.021357              0.016792           0.006667        0.487302            full
tier0_tier1_tier2       20       0.2      0.30         0.4           0.2  0.150427      0.55          0.45            0.090909            0.272727                0.066667            0.044444              -0.011516                -0.012884            0.020789              0.018969           0.008422       -0.104271            full
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0  conf_0.00              0.000000      13      0.65          0.35            0.384615            0.538462                0.350000            0.269091            full
            tier0  conf_0.05              0.050000      11      0.55          0.45            0.454545            0.545455                0.400000            0.280000            full
            tier0  conf_0.10              0.100000       6      0.30          0.70            0.500000            0.500000                0.400000            0.260000            full
            tier0    trained              0.113357       6      0.30          0.70            0.500000            0.500000                0.400000            0.260000            full
            tier0  conf_0.15              0.150000       6      0.30          0.70            0.500000            0.500000                0.400000            0.260000            full
            tier0  conf_0.20              0.200000       4      0.20          0.80            0.500000            0.500000                0.333333            0.160000            full
            tier0  conf_0.25              0.250000       3      0.15          0.85            0.666667            0.666667                0.500000            0.200000            full
      tier0_tier1  conf_0.00              0.000000      15      0.75          0.25            0.333333            0.533333                0.350000            0.344286            full
      tier0_tier1    trained              0.036422      12      0.60          0.40            0.333333            0.583333                0.300000            0.283333            full
      tier0_tier1  conf_0.05              0.050000      10      0.50          0.50            0.300000            0.600000                0.233333            0.210000            full
      tier0_tier1  conf_0.10              0.100000       6      0.30          0.70            0.000000            0.500000                0.000000            0.000000            full
      tier0_tier1  conf_0.15              0.150000       2      0.10          0.90            0.000000            1.000000                0.000000            0.000000            full
      tier0_tier1  conf_0.20              0.200000       2      0.10          0.90            0.000000            1.000000                0.000000            0.000000            full
      tier0_tier1  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN            full
tier0_tier1_tier2  conf_0.00              0.000000      17      0.85          0.15            0.235294            0.470588                0.233333            0.200000            full
tier0_tier1_tier2    trained              0.043865      12      0.60          0.40            0.250000            0.583333                0.200000            0.200000            full
tier0_tier1_tier2  conf_0.05              0.050000      12      0.60          0.40            0.250000            0.583333                0.200000            0.200000            full
tier0_tier1_tier2  conf_0.10              0.100000      10      0.50          0.50            0.300000            0.700000                0.300000            0.213333            full
tier0_tier1_tier2  conf_0.15              0.150000       5      0.25          0.75            0.000000            0.600000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.20              0.200000       3      0.15          0.85            0.000000            0.333333                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.25              0.250000       2      0.10          0.90            0.000000            0.500000                0.000000            0.000000            full
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0  conf_0.00              0.000000      13      0.65          0.35            0.307692            0.538462                0.216667            0.200000            full
            tier0    trained              0.004508      13      0.65          0.35            0.307692            0.538462                0.216667            0.200000            full
            tier0  conf_0.05              0.050000       9      0.45          0.55            0.222222            0.444444                0.133333            0.114286            full
            tier0  conf_0.10              0.100000       5      0.25          0.75            0.400000            0.400000                0.250000            0.200000            full
            tier0  conf_0.15              0.150000       2      0.10          0.90            0.500000            0.500000                0.500000            0.200000            full
            tier0  conf_0.20              0.200000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN            full
            tier0  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN            full
      tier0_tier1  conf_0.00              0.000000      14      0.70          0.30            0.142857            0.357143                0.150000            0.146667            full
      tier0_tier1  conf_0.05              0.050000      14      0.70          0.30            0.142857            0.357143                0.150000            0.146667            full
      tier0_tier1  conf_0.10              0.100000      10      0.50          0.50            0.000000            0.300000                0.000000            0.000000            full
      tier0_tier1  conf_0.15              0.150000       8      0.40          0.60            0.000000            0.250000                0.000000            0.000000            full
      tier0_tier1  conf_0.20              0.200000       7      0.35          0.65            0.000000            0.285714                0.000000            0.000000            full
      tier0_tier1  conf_0.25              0.250000       5      0.25          0.75            0.000000            0.200000                0.000000            0.000000            full
      tier0_tier1    trained              0.487302       2      0.10          0.90            0.000000            0.500000                0.000000            0.000000            full
tier0_tier1_tier2    trained             -0.104271      15      0.75          0.25            0.133333            0.266667                0.133333            0.120000            full
tier0_tier1_tier2  conf_0.00              0.000000       9      0.45          0.55            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.05              0.050000       7      0.35          0.65            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.10              0.100000       5      0.25          0.75            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.15              0.150000       4      0.20          0.80            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.20              0.200000       2      0.10          0.90            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.25              0.250000       2      0.10          0.90            0.000000            0.000000                0.000000            0.000000            full
```

## Diagnosis Mode Comparison
- Whole-run and post-alert-window diagnosis are exported together so the diagnosis mode can be evaluated directly.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile diagnosis_target    diagnosis_mode  family_acc  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau                       status  min_class_count  min_group_count    group_key  include_workload
            tier0       20      0.30      0.55      0.300000  0.232900               0.027017                 0.021021            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.25      0.50      0.250000  0.257143               0.014869                 0.013183            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.35      0.55      0.350000  0.256667               0.018436                 0.018142            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.25      0.50      0.250000  0.212727               0.017396                 0.014295            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.10      0.25      0.100000  0.100000               0.099244                 0.043607            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.10      0.15      0.100000  0.080000               0.027526                 0.019765            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.40      0.60      0.400000  0.331313               0.001758                 0.011079            full     hierarchical         whole_run         0.5      0.50          0.50            0.400000            0.500000                0.400000            0.260000            0.016657              0.017394           0.012575        0.113357                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.35      0.55      0.350000  0.374286               0.011036                 0.010779            full     hierarchical         whole_run         0.5      0.60          0.40            0.250000            0.500000                0.233333            0.277778            0.021357              0.016792           0.006667        0.036422                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.20      0.45      0.200000  0.157143               0.013617                 0.015775            full     hierarchical         whole_run         0.4      0.60          0.40            0.250000            0.583333                0.333333            0.213333            0.020789              0.018969           0.008422        0.043865                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.40      0.65      0.400000  0.364444              -0.014215                 0.006782            full     hierarchical post_alert_window         0.5      0.55          0.45            0.272727            0.454545                0.150000            0.120000            0.016657              0.017394           0.012575        0.004508                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.20      0.35      0.200000  0.164444              -0.011528                 0.029993            full     hierarchical post_alert_window         0.5      0.25          0.75            0.200000            0.400000                0.250000            0.133333            0.021357              0.016792           0.006667        0.487302                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.20      0.30      0.200000  0.150427              -0.011516                -0.012884            full     hierarchical post_alert_window         0.4      0.55          0.45            0.090909            0.272727                0.066667            0.044444            0.020789              0.018969           0.008422       -0.104271                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.60      0.85      0.500000  0.421818               0.034120                 0.036788            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.50      0.85      0.444444  0.447343               0.016332                 0.012214            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.50      0.90      0.611111  0.540196               0.014800                 0.013177            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.563001         0.260171     0.176828              tier0            full
  BRANCH     0.594604         0.217812     0.187583              tier0            full
   CACHE     0.451418         0.196368     0.352214              tier0            full
   MEMBW     0.610561         0.229346     0.160093              tier0            full
     TLB     0.533280         0.273183     0.193537              tier0            full
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC                 compute       0.373081         0.282464             0.115836                 0.124186                 0.104433            full
  BRANCH                 compute       0.333450         0.344772             0.084686                 0.163732                 0.073360            full
   CACHE                 compute       0.515622         0.258497             0.071742                 0.089564                 0.064575            full
   MEMBW                 compute       0.349434         0.320043             0.099573                 0.125783                 0.105167            full
     TLB                 compute       0.378401         0.291180             0.115163                 0.128051                 0.087205            full
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
            tier0                   0.25                        0.927835                      2.783505                 0.30                     54.0                 603.5                0.20                0.20                0.25            full
      tier0_tier1                   0.00                        0.000000                      0.927835                 0.65                     40.0                 753.4                0.50                0.50                0.55            full
tier0_tier1_tier2                   0.00                        0.000000                      0.000000                 0.95                     32.0                 583.2                0.75                0.75                0.85            full
```

## Files
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/config_runtime_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/run_context.json`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/case_inventory.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B30_a0.05_k3/figures/fig_detection_latency.png`
