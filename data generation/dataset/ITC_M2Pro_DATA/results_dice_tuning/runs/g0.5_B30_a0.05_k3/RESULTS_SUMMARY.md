# DICE Full Retrain Results

## Setup
- Feature profile: mixed ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_core_5hz.csv', 'tier2': 'tier2_core_5hz.csv'})
- Protocol: global, benign-only fit/calibration, block_B=30, alpha=0.05, persist_k=3, gain=0.5
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
          mixed             tier0       24          46          2.632345   0.7750 0.919734         1.0        1.0           0.25           0.30              0.004801              0.009448                      0.0                 0.005130
          mixed       tier0_tier1       24          57          2.862142   0.8125 0.949484         1.0        1.0           0.25           0.55              0.000053              0.000122                      0.0                 0.000054
          mixed tier0_tier1_tier2       24          64          3.200074   0.8375 0.957016         1.0        1.0           0.25           0.55              0.000056              0.000133                      0.0                 0.000060
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
          mixed   ATOMIC   0.7500 0.770833         1.0        1.0          0.000056          0.000095                  0.0             0.000047       1.677669      0.000039         47.994996         0.000047
          mixed   BRANCH   0.9375 0.950000         1.0        1.0          0.000056          0.000202                  0.0             0.000118       3.550726      0.000146        119.161856         0.000118
          mixed    CACHE   0.8125 0.804167         1.0        1.0          0.000056          0.000109                  0.0             0.000068       1.929380      0.000053         68.839442         0.000068
          mixed    MEMBW   0.8750 0.887500         1.0        1.0          0.000056          0.000148                  0.0             0.000077       2.616265      0.000092         78.313392         0.000077
          mixed      TLB   0.8125 0.804167         1.0        1.0          0.000056          0.000116                  0.0             0.000037       2.058098      0.000060         37.816629         0.000037
```

## Paper-style Aggregates (Final Config)
- Base score mean stressor AUC-PR (all five): **0.8433**
- Base score mean stressor ROC-AUC (all five): **0.8375**
- WC score mean stressor AUC-PR (all five): **1.0000**
- WC score mean stressor ROC-AUC (all five): **1.0000**
- Base score mean stressor AUC-PR (excluding BRANCH/TLB): **0.8208**
- Base score mean stressor ROC-AUC (excluding BRANCH/TLB): **0.8125**
- WC score mean stressor AUC-PR (excluding BRANCH/TLB): **1.0000**
- WC score mean stressor ROC-AUC (excluding BRANCH/TLB): **1.0000**

## Diagnosis
- Feature-level diagnosis uses normalized whole-run residual-attribution prototypes as the default paper-facing result, with diagnosis-only filtering that removes monotonic counters and downweights generic memory-state features.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.40       0.5          0.40  0.338889               0.022843                 0.017983           mixed
      tier0_tier1       20      0.30       0.5          0.30  0.184615               0.024303                 0.024967           mixed
tier0_tier1_tier2       20      0.45       0.6          0.45  0.425641               0.020482                 0.015911           mixed
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.15      0.50          0.15  0.154286               0.016017                 0.014935           mixed
      tier0_tier1       20      0.20      0.30          0.20  0.100000               0.092513                 0.036153           mixed
tier0_tier1_tier2       20      0.15      0.45          0.15  0.166667               0.092862                 0.027745           mixed
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20       0.4      0.60           0.4  0.403175               0.010773                 0.006097           mixed
      tier0_tier1       20       0.2      0.50           0.2  0.203175               0.018643                 0.014759           mixed
tier0_tier1_tier2       20       0.2      0.45           0.2  0.205556               0.013800                 0.008608           mixed
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.50      0.75      0.444444  0.378788               0.028843                 0.031042           mixed
      tier0_tier1       20      0.50      0.65      0.444444  0.354978               0.025320                 0.026886           mixed
tier0_tier1_tier2       20      0.45      0.75      0.527778  0.444042               0.028117                 0.029644           mixed
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.25      0.50         0.4          0.25  0.197980      0.35          0.65            0.428571            0.571429                0.333333            0.260000               0.013267                 0.011441            0.008541              0.007048           0.009274        0.159320           mixed
      tier0_tier1       20      0.25      0.40         0.3          0.25  0.200000      0.45          0.55            0.222222            0.333333                0.200000            0.114286               0.015091                 0.024562            0.016402              0.013132           0.011895        0.118495           mixed
tier0_tier1_tier2       20      0.30      0.45         0.3          0.30  0.301587      0.65          0.35            0.384615            0.538462                0.433333            0.374286               0.009221                 0.008953            0.017361              0.013510           0.008600       -0.034957           mixed
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.15      0.40         0.4          0.15  0.144444      0.80          0.20               0.125            0.312500                0.116667            0.111111              -0.000754                 0.012707            0.008541              0.007048           0.009274       -0.076248           mixed
      tier0_tier1       20      0.10      0.25         0.3          0.10  0.100000      0.55          0.45               0.000            0.090909                0.000000            0.000000               0.062501                 0.021620            0.016402              0.013132           0.011895        0.037212           mixed
tier0_tier1_tier2       20      0.10      0.35         0.3          0.10  0.107143      0.45          0.55               0.000            0.222222                0.000000            0.000000               0.032257                 0.013770            0.017361              0.013510           0.008600        0.137980           mixed
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0  conf_0.00              0.000000      16      0.80          0.20            0.312500            0.437500                0.312500            0.197980           mixed
            tier0  conf_0.05              0.050000      11      0.55          0.45            0.454545            0.545455                0.354167            0.234286           mixed
            tier0  conf_0.10              0.100000       8      0.40          0.60            0.500000            0.625000                0.312500            0.220000           mixed
            tier0  conf_0.15              0.150000       6      0.30          0.70            0.500000            0.666667                0.250000            0.133333           mixed
            tier0    trained              0.159320       6      0.30          0.70            0.500000            0.666667                0.250000            0.133333           mixed
            tier0  conf_0.20              0.200000       5      0.25          0.75            0.600000            0.600000                0.375000            0.150000           mixed
            tier0  conf_0.25              0.250000       5      0.25          0.75            0.600000            0.600000                0.375000            0.150000           mixed
      tier0_tier1  conf_0.00              0.000000      16      0.80          0.20            0.187500            0.312500                0.200000            0.109091           mixed
      tier0_tier1  conf_0.05              0.050000      12      0.60          0.40            0.250000            0.333333                0.200000            0.133333           mixed
      tier0_tier1  conf_0.10              0.100000      11      0.55          0.45            0.181818            0.272727                0.200000            0.114286           mixed
      tier0_tier1    trained              0.118495      10      0.50          0.50            0.200000            0.200000                0.200000            0.133333           mixed
      tier0_tier1  conf_0.15              0.150000       9      0.45          0.55            0.222222            0.222222                0.200000            0.133333           mixed
      tier0_tier1  conf_0.20              0.200000       4      0.20          0.80            0.250000            0.250000                0.250000            0.200000           mixed
      tier0_tier1  conf_0.25              0.250000       2      0.10          0.90            0.000000            0.000000                0.000000            0.000000           mixed
tier0_tier1_tier2    trained             -0.034957      16      0.80          0.20            0.312500            0.437500                0.383333            0.331429           mixed
tier0_tier1_tier2  conf_0.00              0.000000      15      0.75          0.25            0.333333            0.466667                0.383333            0.351429           mixed
tier0_tier1_tier2  conf_0.05              0.050000      10      0.50          0.50            0.300000            0.400000                0.300000            0.266667           mixed
tier0_tier1_tier2  conf_0.10              0.100000       7      0.35          0.65            0.285714            0.428571                0.400000            0.333333           mixed
tier0_tier1_tier2  conf_0.15              0.150000       5      0.25          0.75            0.200000            0.400000                0.250000            0.133333           mixed
tier0_tier1_tier2  conf_0.20              0.200000       2      0.10          0.90            0.000000            0.500000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.25              0.250000       2      0.10          0.90            0.000000            0.500000                0.000000            0.000000           mixed
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained             -0.076248      15      0.75          0.25            0.133333            0.333333                0.145833            0.111111           mixed
            tier0  conf_0.00              0.000000      15      0.75          0.25            0.133333            0.333333                0.145833            0.111111           mixed
            tier0  conf_0.05              0.050000      12      0.60          0.40            0.166667            0.333333                0.208333            0.123810           mixed
            tier0  conf_0.10              0.100000       8      0.40          0.60            0.250000            0.500000                0.375000            0.180000           mixed
            tier0  conf_0.15              0.150000       5      0.25          0.75            0.400000            0.400000                0.500000            0.300000           mixed
            tier0  conf_0.20              0.200000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
            tier0  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
      tier0_tier1  conf_0.00              0.000000      15      0.75          0.25            0.000000            0.133333                0.000000            0.000000           mixed
      tier0_tier1    trained              0.037212      12      0.60          0.40            0.000000            0.083333                0.000000            0.000000           mixed
      tier0_tier1  conf_0.05              0.050000      11      0.55          0.45            0.000000            0.090909                0.000000            0.000000           mixed
      tier0_tier1  conf_0.10              0.100000      10      0.50          0.50            0.000000            0.100000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.15              0.150000       9      0.45          0.55            0.000000            0.111111                0.000000            0.000000           mixed
      tier0_tier1  conf_0.20              0.200000       8      0.40          0.60            0.000000            0.125000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.25              0.250000       8      0.40          0.60            0.000000            0.125000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.00              0.000000      15      0.75          0.25            0.066667            0.333333                0.100000            0.080000           mixed
tier0_tier1_tier2  conf_0.05              0.050000      12      0.60          0.40            0.083333            0.416667                0.100000            0.133333           mixed
tier0_tier1_tier2  conf_0.10              0.100000       7      0.35          0.65            0.000000            0.285714                0.000000            0.000000           mixed
tier0_tier1_tier2    trained              0.137980       6      0.30          0.70            0.000000            0.333333                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.15              0.150000       6      0.30          0.70            0.000000            0.333333                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.20              0.200000       5      0.25          0.75            0.000000            0.400000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.25              0.250000       5      0.25          0.75            0.000000            0.400000                0.000000            0.000000           mixed
```

## Diagnosis Mode Comparison
- Whole-run and post-alert-window diagnosis are exported together so the diagnosis mode can be evaluated directly.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile diagnosis_target    diagnosis_mode  family_acc  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau                       status  min_class_count  min_group_count    group_key  include_workload
            tier0       20      0.40      0.50      0.400000  0.338889               0.022843                 0.017983           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.30      0.50      0.300000  0.184615               0.024303                 0.024967           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.45      0.60      0.450000  0.425641               0.020482                 0.015911           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.15      0.50      0.150000  0.154286               0.016017                 0.014935           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.20      0.30      0.200000  0.100000               0.092513                 0.036153           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.15      0.45      0.150000  0.166667               0.092862                 0.027745           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.25      0.50      0.250000  0.197980               0.013267                 0.011441           mixed     hierarchical         whole_run         0.4      0.35          0.65            0.428571            0.571429                0.333333            0.260000            0.008541              0.007048           0.009274        0.159320                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.25      0.40      0.250000  0.200000               0.015091                 0.024562           mixed     hierarchical         whole_run         0.3      0.45          0.55            0.222222            0.333333                0.200000            0.114286            0.016402              0.013132           0.011895        0.118495                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.30      0.45      0.300000  0.301587               0.009221                 0.008953           mixed     hierarchical         whole_run         0.3      0.65          0.35            0.384615            0.538462                0.433333            0.374286            0.017361              0.013510           0.008600       -0.034957                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.15      0.40      0.150000  0.144444              -0.000754                 0.012707           mixed     hierarchical post_alert_window         0.4      0.80          0.20            0.125000            0.312500                0.116667            0.111111            0.008541              0.007048           0.009274       -0.076248                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.10      0.25      0.100000  0.100000               0.062501                 0.021620           mixed     hierarchical post_alert_window         0.3      0.55          0.45            0.000000            0.090909                0.000000            0.000000            0.016402              0.013132           0.011895        0.037212                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.10      0.35      0.100000  0.107143               0.032257                 0.013770           mixed     hierarchical post_alert_window         0.3      0.45          0.55            0.000000            0.222222                0.000000            0.000000            0.017361              0.013510           0.008600        0.137980                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.50      0.75      0.444444  0.378788               0.028843                 0.031042           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.50      0.65      0.444444  0.354978               0.025320                 0.026886           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.45      0.75      0.527778  0.444042               0.028117                 0.029644           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.728695         0.120271     0.151035              tier0           mixed
  BRANCH     0.771084         0.081823     0.147093              tier0           mixed
   CACHE     0.551216         0.342206     0.106578              tier0           mixed
   MEMBW     0.783455         0.088840     0.127705              tier0           mixed
     TLB     0.717485         0.123071     0.159444              tier0           mixed
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC               memory_io       0.269257         0.405413             0.073702                 0.221017                 0.030611           mixed
  BRANCH               memory_io       0.251467         0.453980             0.048239                 0.208641                 0.037673           mixed
   CACHE               memory_io       0.464077         0.282903             0.061853                 0.151349                 0.039818           mixed
   MEMBW               memory_io       0.232681         0.477421             0.055061                 0.184100                 0.050737           mixed
     TLB               memory_io       0.300643         0.392968             0.069198                 0.210420                 0.026771           mixed
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
            tier0                   0.25                        0.927835                      2.783505                 0.30                     51.5                 608.0                 0.2                 0.2                0.25           mixed
      tier0_tier1                   0.25                        0.927835                      2.783505                 0.55                     72.0                 817.0                 0.3                 0.3                0.45           mixed
tier0_tier1_tier2                   0.25                        0.927835                      2.783505                 0.55                     71.0                 817.0                 0.3                 0.3                0.45           mixed
```

## Files
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B30_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B30_a0.05_k3/config_runtime_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B30_a0.05_k3/run_context.json`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B30_a0.05_k3/case_inventory.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B30_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B30_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B30_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B30_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B30_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B30_a0.05_k3/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B30_a0.05_k3/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B30_a0.05_k3/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B30_a0.05_k3/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B30_a0.05_k3/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B30_a0.05_k3/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B30_a0.05_k3/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B30_a0.05_k3/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B30_a0.05_k3/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B30_a0.05_k3/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B30_a0.05_k3/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B30_a0.05_k3/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B30_a0.05_k3/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B30_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B30_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B30_a0.05_k3/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B30_a0.05_k3/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B30_a0.05_k3/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B30_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B30_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B30_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B30_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B30_a0.05_k3/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B30_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B30_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B30_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B30_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B30_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B30_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B30_a0.05_k3/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B30_a0.05_k3/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B30_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B30_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B30_a0.05_k3/figures/fig_detection_latency.png`
