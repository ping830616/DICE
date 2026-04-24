# DICE Full Retrain Results

## Setup
- Feature profile: full ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_full_5hz.csv', 'tier2': 'tier2_full_5hz.csv'})
- Protocol: global, benign-only fit/calibration, block_B=90, alpha=0.05, persist_k=3, gain=0.5
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
           full             tier0       24          46          2.354540   0.8000 0.931899         1.0        1.0            0.0           0.30              0.003716              0.008096                      0.0                 0.004455
           full       tier0_tier1       24          64          2.995111   0.7875 0.941423         1.0        1.0            0.0           0.55              0.005292              0.017654                      0.0                 0.008124
           full tier0_tier1_tier2       24          75          3.481432   0.9375 0.986769         1.0        1.0            0.0           0.90              0.002562              0.007302                      0.0                 0.003926
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc  pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
           full   ATOMIC   0.8750  0.8875         1.0        1.0          0.002562          0.006738                  0.0             0.002973       2.629229      0.004176       2974.156277         0.002973
           full   BRANCH   1.0000  1.0000         1.0        1.0          0.002562          0.007673                  0.0             0.005376       2.994078      0.005111       5377.096675         0.005376
           full    CACHE   0.9375  0.9500         1.0        1.0          0.002562          0.008977                  0.0             0.005819       3.502829      0.006415       5819.729147         0.005819
           full    MEMBW   1.0000  1.0000         1.0        1.0          0.002562          0.007784                  0.0             0.004726       3.037281      0.005222       4727.404808         0.004726
           full      TLB   0.8750  0.8875         1.0        1.0          0.002562          0.005928                  0.0             0.003842       2.313360      0.003366       3843.313310         0.003842
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
            tier0       20      0.40      0.55          0.40  0.307071               0.023274                 0.016414            full
      tier0_tier1       20      0.25      0.30          0.25  0.158974               0.015402                 0.010286            full
tier0_tier1_tier2       20      0.30      0.40          0.30  0.200000               0.026896                 0.024541            full
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.30      0.65          0.30  0.273895               0.014237                 0.013629            full
      tier0_tier1       20      0.15      0.45          0.15  0.139683               0.017679                 0.011853            full
tier0_tier1_tier2       20      0.25      0.30          0.25  0.248254               0.018647                 0.017180            full
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.35      0.65          0.35  0.361429               0.014288                 0.014917            full
      tier0_tier1       20      0.35      0.55          0.35  0.269091               0.019963                 0.019137            full
tier0_tier1_tier2       20      0.35      0.60          0.35  0.287013               0.014058                 0.012021            full
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.55      0.75      0.472222  0.398551               0.032838                 0.034712            full
      tier0_tier1       20      0.40      0.70      0.333333  0.293040               0.027970                 0.031869            full
tier0_tier1_tier2       20      0.45      0.95      0.583333  0.458333               0.018958                 0.017157            full
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.25      0.55        0.25          0.25  0.210000       0.3           0.7                0.50            0.666667                0.416667            0.260000               0.005851                 0.005954            0.012952              0.011791           0.011123        0.111110            full
      tier0_tier1       20      0.20      0.45        0.60          0.20  0.177778       0.5           0.5                0.20            0.400000                0.166667            0.146667              -0.005316                 0.000481            0.020970              0.020802           0.009632       -0.060534            full
tier0_tier1_tier2       20      0.20      0.40        0.40          0.20  0.153333       0.6           0.4                0.25            0.333333                0.233333            0.168889               0.009413                 0.014438            0.019603              0.014732           0.011273        0.102015            full
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.20       0.5        0.25          0.20  0.166667      0.85          0.15            0.176471            0.529412                0.150000            0.133333               0.000472                 0.009441            0.012952              0.011791           0.011123       -0.044233            full
      tier0_tier1       20      0.25       0.5        0.60          0.25  0.217094      0.65          0.35            0.153846            0.461538                0.166667            0.124444              -0.012774                 0.001972            0.020970              0.020802           0.009632       -0.000648            full
tier0_tier1_tier2       20      0.30       0.4        0.40          0.30  0.283983      0.75          0.25            0.266667            0.400000                0.266667            0.254444              -0.001112                 0.003561            0.019603              0.014732           0.011273       -0.141417            full
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0  conf_0.00              0.000000      13      0.65          0.35            0.307692            0.461538                0.270833            0.190476            full
            tier0  conf_0.05              0.050000       9      0.45          0.55            0.444444            0.555556                0.312500            0.213333            full
            tier0  conf_0.10              0.100000       7      0.35          0.65            0.571429            0.571429                0.416667            0.233333            full
            tier0    trained              0.111110       6      0.30          0.70            0.500000            0.500000                0.250000            0.133333            full
            tier0  conf_0.15              0.150000       5      0.25          0.75            0.600000            0.600000                0.375000            0.150000            full
            tier0  conf_0.20              0.200000       5      0.25          0.75            0.600000            0.600000                0.375000            0.150000            full
            tier0  conf_0.25              0.250000       4      0.20          0.80            0.750000            0.750000                0.500000            0.171429            full
      tier0_tier1    trained             -0.060534      15      0.75          0.25            0.133333            0.333333                0.133333            0.107143            full
      tier0_tier1  conf_0.00              0.000000      11      0.55          0.45            0.181818            0.363636                0.166667            0.157143            full
      tier0_tier1  conf_0.05              0.050000       7      0.35          0.65            0.285714            0.428571                0.277778            0.180000            full
      tier0_tier1  conf_0.10              0.100000       5      0.25          0.75            0.000000            0.200000                0.000000            0.000000            full
      tier0_tier1  conf_0.15              0.150000       2      0.10          0.90            0.000000            0.000000                0.000000            0.000000            full
      tier0_tier1  conf_0.20              0.200000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000            full
      tier0_tier1  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN            full
tier0_tier1_tier2  conf_0.00              0.000000      16      0.80          0.20            0.187500            0.375000                0.200000            0.146667            full
tier0_tier1_tier2  conf_0.05              0.050000      12      0.60          0.40            0.166667            0.416667                0.133333            0.080000            full
tier0_tier1_tier2  conf_0.10              0.100000       9      0.45          0.55            0.222222            0.444444                0.200000            0.088889            full
tier0_tier1_tier2    trained              0.102015       9      0.45          0.55            0.222222            0.444444                0.200000            0.088889            full
tier0_tier1_tier2  conf_0.15              0.150000       5      0.25          0.75            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.20              0.200000       4      0.20          0.80            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.25              0.250000       2      0.10          0.90            0.000000            0.000000                0.000000            0.000000            full
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained             -0.044233      16      0.80          0.20            0.187500            0.500000                0.150000            0.133333            full
            tier0  conf_0.00              0.000000      16      0.80          0.20            0.187500            0.500000                0.150000            0.133333            full
            tier0  conf_0.05              0.050000      10      0.50          0.50            0.200000            0.500000                0.166667            0.146667            full
            tier0  conf_0.10              0.100000       9      0.45          0.55            0.222222            0.555556                0.200000            0.180000            full
            tier0  conf_0.15              0.150000       3      0.15          0.85            0.000000            0.333333                0.000000            0.000000            full
            tier0  conf_0.20              0.200000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000            full
            tier0  conf_0.25              0.250000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000            full
      tier0_tier1    trained             -0.000648      11      0.55          0.45            0.181818            0.545455                0.200000            0.157143            full
      tier0_tier1  conf_0.00              0.000000      11      0.55          0.45            0.181818            0.545455                0.200000            0.157143            full
      tier0_tier1  conf_0.05              0.050000       6      0.30          0.70            0.166667            0.500000                0.250000            0.100000            full
      tier0_tier1  conf_0.10              0.100000       5      0.25          0.75            0.000000            0.400000                0.000000            0.000000            full
      tier0_tier1  conf_0.15              0.150000       2      0.10          0.90            0.000000            0.000000                0.000000            0.000000            full
      tier0_tier1  conf_0.20              0.200000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000            full
      tier0_tier1  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN            full
tier0_tier1_tier2    trained             -0.141417      19      0.95          0.05            0.263158            0.368421                0.266667            0.257316            full
tier0_tier1_tier2  conf_0.00              0.000000      12      0.60          0.40            0.250000            0.250000                0.300000            0.244444            full
tier0_tier1_tier2  conf_0.05              0.050000       7      0.35          0.65            0.285714            0.285714                0.375000            0.333333            full
tier0_tier1_tier2  conf_0.10              0.100000       6      0.30          0.70            0.333333            0.333333                0.375000            0.333333            full
tier0_tier1_tier2  conf_0.15              0.150000       4      0.20          0.80            0.250000            0.250000                0.333333            0.200000            full
tier0_tier1_tier2  conf_0.20              0.200000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.25              0.250000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000            full
```

## Diagnosis Mode Comparison
- Whole-run and post-alert-window diagnosis are exported together so the diagnosis mode can be evaluated directly.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile diagnosis_target    diagnosis_mode  family_acc  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau                       status  min_class_count  min_group_count    group_key  include_workload
            tier0       20      0.40      0.55      0.400000  0.307071               0.023274                 0.016414            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.25      0.30      0.250000  0.158974               0.015402                 0.010286            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.30      0.40      0.300000  0.200000               0.026896                 0.024541            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.30      0.65      0.300000  0.273895               0.014237                 0.013629            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.15      0.45      0.150000  0.139683               0.017679                 0.011853            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.25      0.30      0.250000  0.248254               0.018647                 0.017180            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.25      0.55      0.250000  0.210000               0.005851                 0.005954            full     hierarchical         whole_run        0.25      0.30          0.70            0.500000            0.666667                0.416667            0.260000            0.012952              0.011791           0.011123        0.111110                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.20      0.45      0.200000  0.177778              -0.005316                 0.000481            full     hierarchical         whole_run        0.60      0.50          0.50            0.200000            0.400000                0.166667            0.146667            0.020970              0.020802           0.009632       -0.060534                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.20      0.40      0.200000  0.153333               0.009413                 0.014438            full     hierarchical         whole_run        0.40      0.60          0.40            0.250000            0.333333                0.233333            0.168889            0.019603              0.014732           0.011273        0.102015                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.20      0.50      0.200000  0.166667               0.000472                 0.009441            full     hierarchical post_alert_window        0.25      0.85          0.15            0.176471            0.529412                0.150000            0.133333            0.012952              0.011791           0.011123       -0.044233                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.25      0.50      0.250000  0.217094              -0.012774                 0.001972            full     hierarchical post_alert_window        0.60      0.65          0.35            0.153846            0.461538                0.166667            0.124444            0.020970              0.020802           0.009632       -0.000648                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.30      0.40      0.300000  0.283983              -0.001112                 0.003561            full     hierarchical post_alert_window        0.40      0.75          0.25            0.266667            0.400000                0.266667            0.254444            0.019603              0.014732           0.011273       -0.141417                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.55      0.75      0.472222  0.398551               0.032838                 0.034712            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.40      0.70      0.333333  0.293040               0.027970                 0.031869            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.45      0.95      0.583333  0.458333               0.018958                 0.017157            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.627953         0.266043     0.106004              tier0            full
  BRANCH     0.661271         0.213958     0.124771              tier0            full
   CACHE     0.543753         0.210010     0.246236              tier0            full
   MEMBW     0.668201         0.238943     0.092856              tier0            full
     TLB     0.609768         0.272962     0.117270              tier0            full
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC               memory_io       0.323027         0.346266             0.091698                 0.123693                 0.115317            full
  BRANCH               memory_io       0.291332         0.405155             0.067330                 0.150369                 0.085814            full
   CACHE               memory_io       0.431627         0.337183             0.061561                 0.095069                 0.074560            full
   MEMBW               memory_io       0.297009         0.386534             0.089684                 0.120001                 0.106772            full
     TLB               memory_io       0.319400         0.365738             0.096412                 0.123640                 0.094809            full
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
            tier0                    0.0                             0.0                           0.0                 0.30                     92.0                 716.5                0.20                0.20                 0.2            full
      tier0_tier1                    0.0                             0.0                           0.0                 0.55                     92.0                 837.0                0.30                0.40                 0.4            full
tier0_tier1_tier2                    0.0                             0.0                           0.0                 0.90                     92.0                 809.3                0.55                0.55                 0.6            full
```

## Files
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B90_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B90_a0.05_k3/config_runtime_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B90_a0.05_k3/run_context.json`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B90_a0.05_k3/case_inventory.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B90_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B90_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B90_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B90_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B90_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B90_a0.05_k3/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B90_a0.05_k3/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B90_a0.05_k3/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B90_a0.05_k3/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B90_a0.05_k3/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B90_a0.05_k3/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B90_a0.05_k3/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B90_a0.05_k3/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B90_a0.05_k3/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B90_a0.05_k3/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B90_a0.05_k3/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B90_a0.05_k3/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B90_a0.05_k3/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B90_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B90_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B90_a0.05_k3/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B90_a0.05_k3/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B90_a0.05_k3/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B90_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B90_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B90_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B90_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B90_a0.05_k3/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B90_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B90_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B90_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B90_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B90_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B90_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B90_a0.05_k3/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B90_a0.05_k3/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B90_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B90_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B90_a0.05_k3/figures/fig_detection_latency.png`
