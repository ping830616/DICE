# DICE Full Retrain Results

## Setup
- Feature profile: full ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_full_5hz.csv', 'tier2': 'tier2_full_5hz.csv'})
- Protocol: global, benign-only fit/calibration, block_B=45, alpha=0.05, persist_k=3, gain=0.35
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
           full             tier0       24          46          2.430252   0.8000 0.931899         1.0        1.0            0.0           0.30              0.005889              0.012124                      0.0                 0.006696
           full       tier0_tier1       24          64          3.067263   0.8125 0.953228         1.0        1.0            0.0           0.60              0.008440              0.025909                      0.0                 0.012058
           full tier0_tier1_tier2       24          75          3.644295   0.9625 0.992487         1.0        1.0            0.0           0.95              0.002719              0.007716                      0.0                 0.004140
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc  pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
           full   ATOMIC   0.9375    0.95         1.0        1.0          0.002719          0.006976                  0.0             0.003324       2.564863      0.004257       3324.783922         0.003324
           full   BRANCH   1.0000    1.00         1.0        1.0          0.002719          0.009031                  0.0             0.006325       3.320564      0.006312       6325.775078         0.006325
           full    CACHE   0.9375    0.95         1.0        1.0          0.002719          0.009163                  0.0             0.005905       3.368950      0.006444       5906.326363         0.005905
           full    MEMBW   1.0000    1.00         1.0        1.0          0.002719          0.008220                  0.0             0.004841       3.022308      0.005501       4841.804875         0.004841
           full      TLB   0.9375    0.95         1.0        1.0          0.002719          0.006827                  0.0             0.004454       2.510087      0.004108       4455.157588         0.004454
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
            tier0       20       0.4      0.60           0.4  0.322424               0.023627                 0.017760            full
      tier0_tier1       20       0.2      0.35           0.2  0.164103               0.013289                 0.008843            full
tier0_tier1_tier2       20       0.3      0.40           0.3  0.200000               0.023110                 0.021560            full
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.30      0.50          0.30  0.310476               0.014794                 0.009653            full
      tier0_tier1       20      0.15      0.35          0.15  0.137143               0.068158                 0.041642            full
tier0_tier1_tier2       20      0.10      0.20          0.10  0.084444               0.014473                 0.012398            full
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.30      0.65          0.30  0.310173               0.013796                 0.010189            full
      tier0_tier1       20      0.25      0.55          0.25  0.180000               0.021246                 0.015080            full
tier0_tier1_tier2       20      0.30      0.55          0.30  0.241616               0.015822                 0.011144            full
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.55      0.80      0.472222  0.398551               0.032268                 0.032995            full
      tier0_tier1       20      0.45      0.75      0.361111  0.305463               0.024725                 0.028474            full
tier0_tier1_tier2       20      0.55      0.90      0.638889  0.542328               0.016821                 0.015217            full
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.40       0.6        0.35          0.40  0.370476      0.45          0.55            0.555556            0.777778                0.450000                0.43               0.014015                 0.011171            0.011727              0.009446           0.014349        0.125742            full
      tier0_tier1       20      0.20       0.5        0.55          0.20  0.190476      0.40          0.60            0.250000            0.500000                0.266667                0.30              -0.002340                 0.005813            0.021054              0.020950           0.011108        0.026185            full
tier0_tier1_tier2       20      0.25       0.4        0.50          0.25  0.175000      0.60          0.40            0.250000            0.333333                0.333333                0.18               0.015113                 0.019776            0.020133              0.014861           0.009429        0.086700            full
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.30      0.50        0.35          0.30  0.259740       0.8           0.2            0.250000            0.437500                0.233333            0.203175               0.001378                 0.008998            0.011727              0.009446           0.014349       -0.062553            full
      tier0_tier1       20      0.20      0.45        0.55          0.20  0.150427       0.3           0.7            0.166667            0.500000                0.125000            0.080000              -0.014982                 0.011664            0.021054              0.020950           0.011108        0.105158            full
tier0_tier1_tier2       20      0.25      0.35        0.50          0.25  0.181197       0.7           0.3            0.214286            0.357143                0.200000            0.160000              -0.004224                -0.003999            0.020133              0.014861           0.009429       -0.179199            full
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0  conf_0.00              0.000000      17      0.85          0.15            0.411765            0.588235                0.450000            0.346667            full
            tier0  conf_0.05              0.050000      14      0.70          0.30            0.428571            0.642857                0.483333            0.355556            full
            tier0  conf_0.10              0.100000       8      0.40          0.60            0.500000            0.625000                0.312500            0.233333            full
            tier0    trained              0.125742       5      0.25          0.75            0.600000            0.800000                0.375000            0.150000            full
            tier0  conf_0.15              0.150000       5      0.25          0.75            0.600000            0.800000                0.375000            0.150000            full
            tier0  conf_0.20              0.200000       5      0.25          0.75            0.600000            0.800000                0.375000            0.150000            full
            tier0  conf_0.25              0.250000       4      0.20          0.80            0.750000            1.000000                0.500000            0.171429            full
      tier0_tier1  conf_0.00              0.000000      13      0.65          0.35            0.153846            0.384615                0.166667            0.146667            full
      tier0_tier1    trained              0.026185      11      0.55          0.45            0.090909            0.363636                0.100000            0.080000            full
      tier0_tier1  conf_0.05              0.050000       6      0.30          0.70            0.000000            0.333333                0.000000            0.000000            full
      tier0_tier1  conf_0.10              0.100000       5      0.25          0.75            0.000000            0.200000                0.000000            0.000000            full
      tier0_tier1  conf_0.15              0.150000       4      0.20          0.80            0.000000            0.250000                0.000000            0.000000            full
      tier0_tier1  conf_0.20              0.200000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000            full
      tier0_tier1  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN            full
tier0_tier1_tier2  conf_0.00              0.000000      17      0.85          0.15            0.235294            0.352941                0.250000            0.165714            full
tier0_tier1_tier2  conf_0.05              0.050000      16      0.80          0.20            0.250000            0.375000                0.250000            0.172308            full
tier0_tier1_tier2    trained              0.086700      11      0.55          0.45            0.272727            0.454545                0.200000            0.100000            full
tier0_tier1_tier2  conf_0.10              0.100000      11      0.55          0.45            0.272727            0.454545                0.200000            0.100000            full
tier0_tier1_tier2  conf_0.15              0.150000       6      0.30          0.70            0.166667            0.333333                0.200000            0.066667            full
tier0_tier1_tier2  conf_0.20              0.200000       3      0.15          0.85            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.25              0.250000       2      0.10          0.90            0.000000            0.000000                0.000000            0.000000            full
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained             -0.062553      16      0.80          0.20            0.250000            0.437500                0.233333            0.203175            full
            tier0  conf_0.00              0.000000      16      0.80          0.20            0.250000            0.437500                0.233333            0.203175            full
            tier0  conf_0.05              0.050000      10      0.50          0.50            0.200000            0.300000                0.166667            0.160000            full
            tier0  conf_0.10              0.100000       6      0.30          0.70            0.333333            0.333333                0.333333            0.200000            full
            tier0  conf_0.15              0.150000       4      0.20          0.80            0.500000            0.500000                0.666667            0.333333            full
            tier0  conf_0.20              0.200000       3      0.15          0.85            0.333333            0.333333                0.500000            0.200000            full
            tier0  conf_0.25              0.250000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000            full
      tier0_tier1  conf_0.00              0.000000      11      0.55          0.45            0.181818            0.545455                0.133333            0.100000            full
      tier0_tier1  conf_0.05              0.050000      10      0.50          0.50            0.200000            0.600000                0.166667            0.114286            full
      tier0_tier1  conf_0.10              0.100000       9      0.45          0.55            0.222222            0.666667                0.250000            0.133333            full
      tier0_tier1    trained              0.105158       9      0.45          0.55            0.222222            0.666667                0.250000            0.133333            full
      tier0_tier1  conf_0.15              0.150000       7      0.35          0.65            0.000000            0.571429                0.000000            0.000000            full
      tier0_tier1  conf_0.20              0.200000       5      0.25          0.75            0.000000            0.400000                0.000000            0.000000            full
      tier0_tier1  conf_0.25              0.250000       4      0.20          0.80            0.000000            0.500000                0.000000            0.000000            full
tier0_tier1_tier2    trained             -0.179199      20      1.00          0.00            0.250000            0.350000                0.250000            0.181197            full
tier0_tier1_tier2  conf_0.00              0.000000      10      0.50          0.50            0.100000            0.200000                0.100000            0.080000            full
tier0_tier1_tier2  conf_0.05              0.050000       5      0.25          0.75            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.10              0.100000       2      0.10          0.90            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.15              0.150000       2      0.10          0.90            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.20              0.200000       2      0.10          0.90            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.25              0.250000       2      0.10          0.90            0.000000            0.000000                0.000000            0.000000            full
```

## Diagnosis Mode Comparison
- Whole-run and post-alert-window diagnosis are exported together so the diagnosis mode can be evaluated directly.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile diagnosis_target    diagnosis_mode  family_acc  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau                       status  min_class_count  min_group_count    group_key  include_workload
            tier0       20      0.40      0.60      0.400000  0.322424               0.023627                 0.017760            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.20      0.35      0.200000  0.164103               0.013289                 0.008843            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.30      0.40      0.300000  0.200000               0.023110                 0.021560            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.30      0.50      0.300000  0.310476               0.014794                 0.009653            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.15      0.35      0.150000  0.137143               0.068158                 0.041642            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.10      0.20      0.100000  0.084444               0.014473                 0.012398            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.40      0.60      0.400000  0.370476               0.014015                 0.011171            full     hierarchical         whole_run        0.35      0.45          0.55            0.555556            0.777778                0.450000            0.430000            0.011727              0.009446           0.014349        0.125742                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.20      0.50      0.200000  0.190476              -0.002340                 0.005813            full     hierarchical         whole_run        0.55      0.40          0.60            0.250000            0.500000                0.266667            0.300000            0.021054              0.020950           0.011108        0.026185                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.25      0.40      0.250000  0.175000               0.015113                 0.019776            full     hierarchical         whole_run        0.50      0.60          0.40            0.250000            0.333333                0.333333            0.180000            0.020133              0.014861           0.009429        0.086700                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.30      0.50      0.300000  0.259740               0.001378                 0.008998            full     hierarchical post_alert_window        0.35      0.80          0.20            0.250000            0.437500                0.233333            0.203175            0.011727              0.009446           0.014349       -0.062553                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.20      0.45      0.200000  0.150427              -0.014982                 0.011664            full     hierarchical post_alert_window        0.55      0.30          0.70            0.166667            0.500000                0.125000            0.080000            0.021054              0.020950           0.011108        0.105158                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.25      0.35      0.250000  0.181197              -0.004224                -0.003999            full     hierarchical post_alert_window        0.50      0.70          0.30            0.214286            0.357143                0.200000            0.160000            0.020133              0.014861           0.009429       -0.179199                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.55      0.80      0.472222  0.398551               0.032268                 0.032995            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.45      0.75      0.361111  0.305463               0.024725                 0.028474            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.55      0.90      0.638889  0.542328               0.016821                 0.015217            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.607572         0.267644     0.124784              tier0            full
  BRANCH     0.638178         0.216466     0.145356              tier0            full
   CACHE     0.511269         0.206308     0.282423              tier0            full
   MEMBW     0.649773         0.240220     0.110008              tier0            full
     TLB     0.584036         0.277310     0.138654              tier0            full
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC                 compute       0.339457         0.314384             0.106741                 0.129138                 0.110281            full
  BRANCH               memory_io       0.304739         0.375171             0.077596                 0.161020                 0.081474            full
   CACHE                 compute       0.463317         0.301541             0.068827                 0.095927                 0.070388            full
   MEMBW               memory_io       0.313249         0.355708             0.099705                 0.125632                 0.105707            full
     TLB                 compute       0.336584         0.331269             0.110212                 0.130689                 0.091246            full
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
            tier0                    0.0                             0.0                      1.884817                 0.30                     63.5                 617.5                0.20                0.20                0.25            full
      tier0_tier1                    0.0                             0.0                      0.000000                 0.60                     47.5                 807.4                0.45                0.45                0.45            full
tier0_tier1_tier2                    0.0                             0.0                      0.000000                 0.95                     47.0                 780.0                0.65                0.65                0.75            full
```

## Files
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B45_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B45_a0.05_k3/config_runtime_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B45_a0.05_k3/run_context.json`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B45_a0.05_k3/case_inventory.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B45_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B45_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B45_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B45_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B45_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B45_a0.05_k3/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B45_a0.05_k3/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B45_a0.05_k3/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B45_a0.05_k3/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B45_a0.05_k3/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B45_a0.05_k3/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B45_a0.05_k3/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B45_a0.05_k3/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B45_a0.05_k3/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B45_a0.05_k3/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B45_a0.05_k3/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B45_a0.05_k3/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B45_a0.05_k3/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B45_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B45_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B45_a0.05_k3/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B45_a0.05_k3/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B45_a0.05_k3/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B45_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B45_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B45_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B45_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B45_a0.05_k3/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B45_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B45_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B45_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B45_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B45_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B45_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B45_a0.05_k3/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B45_a0.05_k3/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B45_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B45_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B45_a0.05_k3/figures/fig_detection_latency.png`
