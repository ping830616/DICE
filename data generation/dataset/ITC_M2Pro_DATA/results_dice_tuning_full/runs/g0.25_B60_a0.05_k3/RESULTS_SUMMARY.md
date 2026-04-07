# DICE Full Retrain Results

## Setup
- Feature profile: full ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_full_5hz.csv', 'tier2': 'tier2_full_5hz.csv'})
- Protocol: global, benign-only fit/calibration, block_B=60, alpha=0.05, persist_k=3, gain=0.25
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
           full             tier0       24          46          2.191753   0.8000 0.931899         1.0        1.0            0.0           0.30              0.007173              0.015654                      0.0                 0.008507
           full       tier0_tier1       24          64          2.846141   0.8125 0.953228         1.0        1.0            0.0           0.55              0.009965              0.032138                      0.0                 0.015404
           full tier0_tier1_tier2       24          75          3.444138   0.9750 0.995119         1.0        1.0            0.0           0.95              0.002915              0.008199                      0.0                 0.004739
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc  pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
           full   ATOMIC   0.9375    0.95         1.0        1.0          0.002915          0.007701                  0.0             0.004182       2.641065      0.004786       4182.570521         0.004182
           full   BRANCH   1.0000    1.00         1.0        1.0          0.002915          0.008590                  0.0             0.006194       2.945804      0.005675       6195.036303         0.006194
           full    CACHE   0.9375    0.95         1.0        1.0          0.002915          0.010003                  0.0             0.006697       3.430465      0.007088       6698.240269         0.006697
           full    MEMBW   1.0000    1.00         1.0        1.0          0.002915          0.009001                  0.0             0.005297       3.086872      0.006086       5297.699873         0.005297
           full      TLB   1.0000    1.00         1.0        1.0          0.002915          0.006641                  0.0             0.004552       2.277434      0.003725       4553.076502         0.004552
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
            tier0       20       0.3      0.60           0.3  0.238961               0.026441                 0.020305            full
      tier0_tier1       20       0.2      0.35           0.2  0.190476               0.013305                 0.008044            full
tier0_tier1_tier2       20       0.3      0.45           0.3  0.206667               0.021344                 0.018120            full
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.10      0.55          0.10  0.116364               0.015435                 0.008309            full
      tier0_tier1       20      0.15      0.35          0.15  0.124444               0.042079                 0.035580            full
tier0_tier1_tier2       20      0.15      0.35          0.15  0.147143               0.020347                 0.020110            full
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.25      0.65          0.25  0.223333               0.014232                 0.009951            full
      tier0_tier1       20      0.20      0.50          0.20  0.152727               0.020532                 0.018368            full
tier0_tier1_tier2       20      0.30      0.60          0.30  0.241616               0.015417                 0.011460            full
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.60      0.80      0.500000  0.421818               0.033640                 0.033806            full
      tier0_tier1       20      0.45      0.75      0.361111  0.307359               0.021342                 0.023310            full
tier0_tier1_tier2       20      0.50      0.95      0.555556  0.495951               0.016190                 0.014027            full
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.45       0.7        0.45          0.45  0.360000      0.40          0.60            0.500000            0.750000                0.400000            0.314286              -0.010155                 0.005073            0.014656              0.016687           0.012266        0.073714            full
      tier0_tier1       20      0.20       0.4        0.45          0.20  0.215873      0.55          0.45            0.090909            0.272727                0.100000            0.080000               0.008655                 0.006293            0.022549              0.020302           0.008737        0.014487            full
tier0_tier1_tier2       20      0.25       0.4        0.40          0.25  0.180000      0.65          0.35            0.230769            0.384615                0.333333            0.180000               0.014373                 0.017242            0.019712              0.016558           0.009485        0.053279            full
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.35      0.65        0.45          0.35  0.303810      0.50          0.50            0.200000            0.600000                0.133333            0.146667              -0.015250                -0.000026            0.014656              0.016687           0.012266       -0.068627            full
      tier0_tier1       20      0.15      0.40        0.45          0.15  0.118681      0.55          0.45            0.090909            0.363636                0.066667            0.044444              -0.008663                 0.009384            0.022549              0.020302           0.008737        0.069486            full
tier0_tier1_tier2       20      0.25      0.40        0.40          0.25  0.192308      0.75          0.25            0.200000            0.333333                0.200000            0.160000              -0.000138                 0.011895            0.019712              0.016558           0.009485       -0.115002            full
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0  conf_0.00              0.000000      11      0.55          0.45            0.454545            0.727273                0.400000            0.293333            full
            tier0  conf_0.05              0.050000       9      0.45          0.55            0.555556            0.666667                0.400000            0.293333            full
            tier0    trained              0.073714       7      0.35          0.65            0.571429            0.571429                0.400000            0.293333            full
            tier0  conf_0.10              0.100000       5      0.25          0.75            0.600000            0.600000                0.500000            0.293333            full
            tier0  conf_0.15              0.150000       3      0.15          0.85            0.666667            0.666667                0.500000            0.160000            full
            tier0  conf_0.20              0.200000       2      0.10          0.90            1.000000            1.000000                1.000000            0.200000            full
            tier0  conf_0.25              0.250000       2      0.10          0.90            1.000000            1.000000                1.000000            0.200000            full
      tier0_tier1  conf_0.00              0.000000      14      0.70          0.30            0.142857            0.285714                0.166667            0.146667            full
      tier0_tier1    trained              0.014487      13      0.65          0.35            0.153846            0.230769                0.166667            0.146667            full
      tier0_tier1  conf_0.05              0.050000       8      0.40          0.60            0.000000            0.125000                0.000000            0.000000            full
      tier0_tier1  conf_0.10              0.100000       8      0.40          0.60            0.000000            0.125000                0.000000            0.000000            full
      tier0_tier1  conf_0.15              0.150000       5      0.25          0.75            0.000000            0.200000                0.000000            0.000000            full
      tier0_tier1  conf_0.20              0.200000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000            full
      tier0_tier1  conf_0.25              0.250000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.00              0.000000      17      0.85          0.15            0.235294            0.352941                0.250000            0.172308            full
tier0_tier1_tier2  conf_0.05              0.050000      15      0.75          0.25            0.266667            0.400000                0.250000            0.192308            full
tier0_tier1_tier2    trained              0.053279      14      0.70          0.30            0.285714            0.428571                0.250000            0.192308            full
tier0_tier1_tier2  conf_0.10              0.100000      10      0.50          0.50            0.300000            0.500000                0.300000            0.213333            full
tier0_tier1_tier2  conf_0.15              0.150000       5      0.25          0.75            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.20              0.200000       3      0.15          0.85            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.25              0.250000       2      0.10          0.90            0.000000            0.000000                0.000000            0.000000            full
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained             -0.068627      13      0.65          0.35            0.307692            0.692308                0.333333            0.293333            full
            tier0  conf_0.00              0.000000      11      0.55          0.45            0.181818            0.636364                0.133333            0.146667            full
            tier0  conf_0.05              0.050000       7      0.35          0.65            0.285714            0.571429                0.333333            0.233333            full
            tier0  conf_0.10              0.100000       5      0.25          0.75            0.200000            0.600000                0.250000            0.133333            full
            tier0  conf_0.15              0.150000       5      0.25          0.75            0.200000            0.600000                0.250000            0.133333            full
            tier0  conf_0.20              0.200000       4      0.20          0.80            0.250000            0.500000                0.333333            0.133333            full
            tier0  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN            full
      tier0_tier1  conf_0.00              0.000000      13      0.65          0.35            0.153846            0.461538                0.100000            0.088889            full
      tier0_tier1  conf_0.05              0.050000      10      0.50          0.50            0.100000            0.400000                0.066667            0.066667            full
      tier0_tier1    trained              0.069486      10      0.50          0.50            0.100000            0.400000                0.066667            0.066667            full
      tier0_tier1  conf_0.10              0.100000       8      0.40          0.60            0.000000            0.375000                0.000000            0.000000            full
      tier0_tier1  conf_0.15              0.150000       7      0.35          0.65            0.000000            0.285714                0.000000            0.000000            full
      tier0_tier1  conf_0.20              0.200000       6      0.30          0.70            0.000000            0.333333                0.000000            0.000000            full
      tier0_tier1  conf_0.25              0.250000       4      0.20          0.80            0.000000            0.250000                0.000000            0.000000            full
tier0_tier1_tier2    trained             -0.115002      17      0.85          0.15            0.235294            0.352941                0.233333            0.194286            full
tier0_tier1_tier2  conf_0.00              0.000000      13      0.65          0.35            0.153846            0.307692                0.200000            0.166667            full
tier0_tier1_tier2  conf_0.05              0.050000      10      0.50          0.50            0.100000            0.200000                0.100000            0.080000            full
tier0_tier1_tier2  conf_0.10              0.100000       4      0.20          0.80            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.15              0.150000       3      0.15          0.85            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.20              0.200000       3      0.15          0.85            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.25              0.250000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000            full
```

## Diagnosis Mode Comparison
- Whole-run and post-alert-window diagnosis are exported together so the diagnosis mode can be evaluated directly.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile diagnosis_target    diagnosis_mode  family_acc  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau                       status  min_class_count  min_group_count    group_key  include_workload
            tier0       20      0.30      0.60      0.300000  0.238961               0.026441                 0.020305            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.20      0.35      0.200000  0.190476               0.013305                 0.008044            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.30      0.45      0.300000  0.206667               0.021344                 0.018120            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.10      0.55      0.100000  0.116364               0.015435                 0.008309            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.15      0.35      0.150000  0.124444               0.042079                 0.035580            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.15      0.35      0.150000  0.147143               0.020347                 0.020110            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.45      0.70      0.450000  0.360000              -0.010155                 0.005073            full     hierarchical         whole_run        0.45      0.40          0.60            0.500000            0.750000                0.400000            0.314286            0.014656              0.016687           0.012266        0.073714                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.20      0.40      0.200000  0.215873               0.008655                 0.006293            full     hierarchical         whole_run        0.45      0.55          0.45            0.090909            0.272727                0.100000            0.080000            0.022549              0.020302           0.008737        0.014487                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.25      0.40      0.250000  0.180000               0.014373                 0.017242            full     hierarchical         whole_run        0.40      0.65          0.35            0.230769            0.384615                0.333333            0.180000            0.019712              0.016558           0.009485        0.053279                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.35      0.65      0.350000  0.303810              -0.015250                -0.000026            full     hierarchical post_alert_window        0.45      0.50          0.50            0.200000            0.600000                0.133333            0.146667            0.014656              0.016687           0.012266       -0.068627                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.15      0.40      0.150000  0.118681              -0.008663                 0.009384            full     hierarchical post_alert_window        0.45      0.55          0.45            0.090909            0.363636                0.066667            0.044444            0.022549              0.020302           0.008737        0.069486                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.25      0.40      0.250000  0.192308              -0.000138                 0.011895            full     hierarchical post_alert_window        0.40      0.75          0.25            0.200000            0.333333                0.200000            0.160000            0.019712              0.016558           0.009485       -0.115002                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.60      0.80      0.500000  0.421818               0.033640                 0.033806            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.45      0.75      0.361111  0.307359               0.021342                 0.023310            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.50      0.95      0.555556  0.495951               0.016190                 0.014027            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.603629         0.265673     0.130699              tier0            full
  BRANCH     0.630318         0.220637     0.149045              tier0            full
   CACHE     0.496157         0.207190     0.296653              tier0            full
   MEMBW     0.647315         0.236171     0.116514              tier0            full
     TLB     0.575625         0.278822     0.145553              tier0            full
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC                 compute       0.341690         0.312416             0.105339                 0.124709                 0.115846            full
  BRANCH               memory_io       0.307620         0.376338             0.077296                 0.154432                 0.084314            full
   CACHE                 compute       0.474730         0.296518             0.066293                 0.089760                 0.072700            full
   MEMBW               memory_io       0.316895         0.353556             0.095156                 0.122254                 0.112139            full
     TLB                 compute       0.342338         0.329030             0.106441                 0.125643                 0.096549            full
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
            tier0                    0.0                             0.0                           0.0                 0.30                     75.0                 723.5                0.20                0.20                 0.2            full
      tier0_tier1                    0.0                             0.0                           0.0                 0.55                     62.0                 835.0                0.35                0.35                 0.4            full
tier0_tier1_tier2                    0.0                             0.0                           0.0                 0.95                     62.0                 798.4                0.60                0.65                 0.7            full
```

## Files
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/config_runtime_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/run_context.json`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/case_inventory.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B60_a0.05_k3/figures/fig_detection_latency.png`
