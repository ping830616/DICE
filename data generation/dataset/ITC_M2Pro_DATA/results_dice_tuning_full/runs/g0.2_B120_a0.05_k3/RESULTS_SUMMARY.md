# DICE Full Retrain Results

## Setup
- Feature profile: full ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_full_5hz.csv', 'tier2': 'tier2_full_5hz.csv'})
- Protocol: global, benign-only fit/calibration, block_B=120, alpha=0.05, persist_k=3, gain=0.2
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
           full             tier0       24          46          2.092265   0.7875 0.921899         1.0        1.0            0.0            0.3              0.006765              0.015573                      0.0                 0.009038
           full       tier0_tier1       24          64          2.841334   0.7875 0.941423         1.0        1.0            0.0            0.5              0.010226              0.029677                      0.0                 0.014689
           full tier0_tier1_tier2       24          75          3.424029   0.9625 0.992487         1.0        1.0            0.0            0.9              0.003231              0.008700                      0.0                 0.005177
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc  pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
           full   ATOMIC   0.9375    0.95         1.0        1.0          0.003231          0.008707                  0.0             0.004781       2.694339      0.005476       4782.269391         0.004781
           full   BRANCH   1.0000    1.00         1.0        1.0          0.003231          0.008247                  0.0             0.005910       2.552123      0.005016       5911.447010         0.005910
           full    CACHE   0.9375    0.95         1.0        1.0          0.003231          0.011330                  0.0             0.007784       3.505806      0.008099       7785.023444         0.007784
           full    MEMBW   1.0000    1.00         1.0        1.0          0.003231          0.009544                  0.0             0.006091       2.953264      0.006313       6091.922803         0.006091
           full      TLB   0.9375    0.95         1.0        1.0          0.003231          0.007191                  0.0             0.004632       2.225176      0.003960       4633.109326         0.004632
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
            tier0       20      0.35      0.55          0.35  0.298485               0.028863                 0.022491            full
      tier0_tier1       20      0.20      0.55          0.20  0.177143               0.015067                 0.009764            full
tier0_tier1_tier2       20      0.30      0.50          0.30  0.206667               0.022307                 0.019372            full
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20       0.1      0.65           0.1  0.080808               0.016001                 0.013306            full
      tier0_tier1       20       0.3      0.45           0.3  0.257143               0.024308                 0.018015            full
tier0_tier1_tier2       20       0.2      0.40           0.2  0.196032               0.017082                 0.015797            full
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20       0.3      0.60           0.3  0.290476               0.016814                 0.015255            full
      tier0_tier1       20       0.3      0.45           0.3  0.286061               0.019406                 0.016182            full
tier0_tier1_tier2       20       0.4      0.55           0.4  0.352222               0.013209                 0.009323            full
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.60      0.85      0.500000  0.421818               0.038932                 0.039527            full
      tier0_tier1       20      0.45      0.85      0.361111  0.307359               0.020196                 0.016610            full
tier0_tier1_tier2       20      0.50      0.95      0.555556  0.508772               0.017230                 0.014107            full
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.40      0.60        0.55          0.40  0.326061      0.45          0.55            0.444444            0.555556                0.400000            0.293333              -0.013403                -0.006152            0.016781              0.016474           0.009515        0.021043            full
      tier0_tier1       20      0.30      0.60        0.40          0.30  0.303810      0.65          0.35            0.153846            0.461538                0.150000            0.160000               0.011134                 0.013245            0.024183              0.023918           0.010400        0.000000            full
tier0_tier1_tier2       20      0.25      0.45        0.35          0.25  0.168889      0.60          0.40            0.250000            0.416667                0.333333            0.180000               0.013275                 0.016218            0.020262              0.019255           0.006040        0.037158            full
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.40      0.60        0.55          0.40  0.355556      0.70          0.30            0.500000            0.714286                0.466667            0.420476              -0.017391                 0.000721            0.016781              0.016474           0.009515       -0.105647            full
      tier0_tier1       20      0.35      0.55        0.40          0.35  0.342222      0.55          0.45            0.272727            0.454545                0.200000            0.226667              -0.003781                 0.000474            0.024183              0.023918           0.010400        0.041610            full
tier0_tier1_tier2       20      0.30      0.40        0.35          0.30  0.237143      0.60          0.40            0.333333            0.416667                0.300000            0.260000              -0.007124                 0.000132            0.020262              0.019255           0.006040       -0.074299            full
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0  conf_0.00              0.000000      10      0.50          0.50            0.500000            0.600000                0.400000            0.310000            full
            tier0    trained              0.021043       9      0.45          0.55            0.555556            0.666667                0.500000            0.310000            full
            tier0  conf_0.05              0.050000       6      0.30          0.70            0.500000            0.500000                0.500000            0.293333            full
            tier0  conf_0.10              0.100000       5      0.25          0.75            0.600000            0.600000                0.500000            0.293333            full
            tier0  conf_0.15              0.150000       4      0.20          0.80            0.500000            0.500000                0.333333            0.160000            full
            tier0  conf_0.20              0.200000       3      0.15          0.85            0.666667            0.666667                0.500000            0.160000            full
            tier0  conf_0.25              0.250000       3      0.15          0.85            0.666667            0.666667                0.500000            0.160000            full
      tier0_tier1    trained              0.000000      12      0.60          0.40            0.166667            0.500000                0.150000            0.160000            full
      tier0_tier1  conf_0.00              0.000000      12      0.60          0.40            0.166667            0.500000                0.150000            0.160000            full
      tier0_tier1  conf_0.05              0.050000      10      0.50          0.50            0.200000            0.500000                0.166667            0.180000            full
      tier0_tier1  conf_0.10              0.100000       6      0.30          0.70            0.000000            0.333333                0.000000            0.000000            full
      tier0_tier1  conf_0.15              0.150000       4      0.20          0.80            0.000000            0.500000                0.000000            0.000000            full
      tier0_tier1  conf_0.20              0.200000       1      0.05          0.95            0.000000            1.000000                0.000000            0.000000            full
      tier0_tier1  conf_0.25              0.250000       1      0.05          0.95            0.000000            1.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.00              0.000000      16      0.80          0.20            0.250000            0.437500                0.250000            0.172308            full
tier0_tier1_tier2    trained              0.037158      14      0.70          0.30            0.285714            0.500000                0.250000            0.192308            full
tier0_tier1_tier2  conf_0.05              0.050000      14      0.70          0.30            0.285714            0.500000                0.250000            0.192308            full
tier0_tier1_tier2  conf_0.10              0.100000       9      0.45          0.55            0.222222            0.555556                0.300000            0.183333            full
tier0_tier1_tier2  conf_0.15              0.150000       4      0.20          0.80            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.20              0.200000       3      0.15          0.85            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.25              0.250000       2      0.10          0.90            0.000000            0.000000                0.000000            0.000000            full
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained             -0.105647      13      0.65          0.35            0.461538            0.692308                0.433333            0.387143            full
            tier0  conf_0.00              0.000000      11      0.55          0.45            0.363636            0.636364                0.266667            0.230000            full
            tier0  conf_0.05              0.050000       7      0.35          0.65            0.428571            0.571429                0.333333            0.260000            full
            tier0  conf_0.10              0.100000       4      0.20          0.80            0.250000            0.500000                0.333333            0.200000            full
            tier0  conf_0.15              0.150000       3      0.15          0.85            0.333333            0.666667                0.500000            0.200000            full
            tier0  conf_0.20              0.200000       2      0.10          0.90            0.500000            1.000000                0.500000            0.200000            full
            tier0  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN            full
      tier0_tier1  conf_0.00              0.000000      11      0.55          0.45            0.363636            0.454545                0.366667            0.290476            full
      tier0_tier1    trained              0.041610       7      0.35          0.65            0.428571            0.571429                0.400000            0.333333            full
      tier0_tier1  conf_0.05              0.050000       7      0.35          0.65            0.428571            0.571429                0.400000            0.333333            full
      tier0_tier1  conf_0.10              0.100000       6      0.30          0.70            0.333333            0.500000                0.300000            0.200000            full
      tier0_tier1  conf_0.15              0.150000       4      0.20          0.80            0.000000            0.250000                0.000000            0.000000            full
      tier0_tier1  conf_0.20              0.200000       4      0.20          0.80            0.000000            0.250000                0.000000            0.000000            full
      tier0_tier1  conf_0.25              0.250000       3      0.15          0.85            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2    trained             -0.074299      14      0.70          0.30            0.357143            0.428571                0.316667            0.279365            full
tier0_tier1_tier2  conf_0.00              0.000000      11      0.55          0.45            0.272727            0.363636                0.250000            0.247619            full
tier0_tier1_tier2  conf_0.05              0.050000       4      0.20          0.80            0.250000            0.250000                0.166667            0.133333            full
tier0_tier1_tier2  conf_0.10              0.100000       4      0.20          0.80            0.250000            0.250000                0.166667            0.133333            full
tier0_tier1_tier2  conf_0.15              0.150000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.20              0.200000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN            full
```

## Diagnosis Mode Comparison
- Whole-run and post-alert-window diagnosis are exported together so the diagnosis mode can be evaluated directly.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile diagnosis_target    diagnosis_mode  family_acc  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau                       status  min_class_count  min_group_count    group_key  include_workload
            tier0       20      0.35      0.55      0.350000  0.298485               0.028863                 0.022491            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.20      0.55      0.200000  0.177143               0.015067                 0.009764            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.30      0.50      0.300000  0.206667               0.022307                 0.019372            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.10      0.65      0.100000  0.080808               0.016001                 0.013306            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.30      0.45      0.300000  0.257143               0.024308                 0.018015            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.20      0.40      0.200000  0.196032               0.017082                 0.015797            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.40      0.60      0.400000  0.326061              -0.013403                -0.006152            full     hierarchical         whole_run        0.55      0.45          0.55            0.444444            0.555556                0.400000            0.293333            0.016781              0.016474           0.009515        0.021043                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.30      0.60      0.300000  0.303810               0.011134                 0.013245            full     hierarchical         whole_run        0.40      0.65          0.35            0.153846            0.461538                0.150000            0.160000            0.024183              0.023918           0.010400        0.000000                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.25      0.45      0.250000  0.168889               0.013275                 0.016218            full     hierarchical         whole_run        0.35      0.60          0.40            0.250000            0.416667                0.333333            0.180000            0.020262              0.019255           0.006040        0.037158                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.40      0.60      0.400000  0.355556              -0.017391                 0.000721            full     hierarchical post_alert_window        0.55      0.70          0.30            0.500000            0.714286                0.466667            0.420476            0.016781              0.016474           0.009515       -0.105647                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.35      0.55      0.350000  0.342222              -0.003781                 0.000474            full     hierarchical post_alert_window        0.40      0.55          0.45            0.272727            0.454545                0.200000            0.226667            0.024183              0.023918           0.010400        0.041610                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.30      0.40      0.300000  0.237143              -0.007124                 0.000132            full     hierarchical post_alert_window        0.35      0.60          0.40            0.333333            0.416667                0.300000            0.260000            0.020262              0.019255           0.006040       -0.074299                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.60      0.85      0.500000  0.421818               0.038932                 0.039527            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.45      0.85      0.361111  0.307359               0.020196                 0.016610            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.50      0.95      0.555556  0.508772               0.017230                 0.014107            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.612250         0.262774     0.124976              tier0            full
  BRANCH     0.637631         0.222413     0.139956              tier0            full
   CACHE     0.496125         0.208840     0.295035              tier0            full
   MEMBW     0.657235         0.231388     0.111377              tier0            full
     TLB     0.580837         0.280098     0.139066              tier0            full
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC                 compute       0.335180         0.328648             0.096212                 0.114854                 0.125105            full
  BRANCH               memory_io       0.302125         0.399327             0.070122                 0.140153                 0.088273            full
   CACHE                 compute       0.471961         0.309721             0.059556                 0.081725                 0.077037            full
   MEMBW               memory_io       0.309949         0.370560             0.085180                 0.113469                 0.120842            full
     TLB               memory_io       0.337290         0.348382             0.096269                 0.114534                 0.103525            full
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
            tier0                    0.0                             0.0                           0.0                  0.3                    122.0                 650.0                 0.0                0.20                0.25            full
      tier0_tier1                    0.0                             0.0                           0.0                  0.5                    122.0                 519.4                 0.0                0.35                0.45            full
tier0_tier1_tier2                    0.0                             0.0                           0.0                  0.9                    122.0                 616.1                 0.0                0.65                0.75            full
```

## Files
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B120_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B120_a0.05_k3/config_runtime_summary.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B120_a0.05_k3/run_context.json`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B120_a0.05_k3/case_inventory.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B120_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B120_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B120_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B120_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B120_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B120_a0.05_k3/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B120_a0.05_k3/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B120_a0.05_k3/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B120_a0.05_k3/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B120_a0.05_k3/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B120_a0.05_k3/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B120_a0.05_k3/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B120_a0.05_k3/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B120_a0.05_k3/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B120_a0.05_k3/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B120_a0.05_k3/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B120_a0.05_k3/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B120_a0.05_k3/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B120_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B120_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B120_a0.05_k3/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B120_a0.05_k3/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B120_a0.05_k3/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B120_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B120_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B120_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B120_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B120_a0.05_k3/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B120_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B120_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B120_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B120_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B120_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B120_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B120_a0.05_k3/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B120_a0.05_k3/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B120_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B120_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B120_a0.05_k3/figures/fig_detection_latency.png`
