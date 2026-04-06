# DICE Full Retrain Results

## Setup
- Feature profile: mixed ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_core_5hz.csv', 'tier2': 'tier2_core_5hz.csv'})
- Protocol: global, benign-only fit/calibration, block_B=90, alpha=0.05, persist_k=3, gain=0.5
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
          mixed             tier0       24          46          2.283023   0.8000 0.931899         1.0        1.0            0.0           0.30              0.003716              0.008096                      0.0                 0.004455
          mixed       tier0_tier1       24          57          2.813232   0.8250 0.951460         1.0        1.0            0.0           0.45              0.000046              0.000112                      0.0                 0.000065
          mixed tier0_tier1_tier2       24          64          3.174183   0.8375 0.953625         1.0        1.0            0.0           0.45              0.000050              0.000122                      0.0                 0.000069
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
          mixed   ATOMIC   0.8125 0.804167         1.0        1.0           0.00005          0.000104                  0.0             0.000062       2.076524      0.000055         62.904962         0.000062
          mixed   BRANCH   0.9375 0.950000         1.0        1.0           0.00005          0.000185                  0.0             0.000122       3.676434      0.000136        122.782079         0.000122
          mixed    CACHE   0.8125 0.804167         1.0        1.0           0.00005          0.000105                  0.0             0.000063       2.102527      0.000056         64.103957         0.000063
          mixed    MEMBW   0.8750 0.887500         1.0        1.0           0.00005          0.000169                  0.0             0.000101       3.366121      0.000120        101.579609         0.000101
          mixed      TLB   0.7500 0.679167         1.0        1.0           0.00005          0.000121                  0.0             0.000059       2.400754      0.000071         60.158234         0.000059
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
            tier0       20       0.4      0.55           0.4  0.307071               0.023274                 0.016414           mixed
      tier0_tier1       20       0.3      0.55           0.3  0.184615               0.025832                 0.025567           mixed
tier0_tier1_tier2       20       0.4      0.60           0.4  0.345641               0.023417                 0.021452           mixed
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20       0.3      0.65           0.3  0.273895               0.014237                 0.013629           mixed
      tier0_tier1       20       0.2      0.40           0.2  0.142857               0.042802                 0.026612           mixed
tier0_tier1_tier2       20       0.1      0.45           0.1  0.114286               0.034426                 0.013925           mixed
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.35      0.65          0.35  0.361429               0.014288                 0.014917           mixed
      tier0_tier1       20      0.25      0.50          0.25  0.234286               0.015461                 0.011837           mixed
tier0_tier1_tier2       20      0.20      0.60          0.20  0.186364               0.015354                 0.013832           mixed
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.55      0.75      0.472222  0.398551               0.032838                 0.034712           mixed
      tier0_tier1       20      0.45      0.65      0.416667  0.333333               0.026477                 0.027923           mixed
tier0_tier1_tier2       20      0.45      0.75      0.527778  0.450142               0.030328                 0.024632           mixed
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.25      0.55        0.25          0.25  0.210000      0.30          0.70            0.500000            0.666667                0.416667            0.260000               0.005851                 0.005954            0.012952              0.011791           0.011123        0.111110           mixed
      tier0_tier1       20      0.20      0.45        0.25          0.20  0.173333      0.70          0.30            0.214286            0.428571                0.233333            0.187143               0.012953                 0.021257            0.016822              0.014916           0.013838        0.067772           mixed
tier0_tier1_tier2       20      0.30      0.55        0.30          0.30  0.269394      0.45          0.55            0.333333            0.555556                0.333333            0.293333               0.010090                 0.020269            0.017265              0.015865           0.011205        0.085355           mixed
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.20       0.5        0.25          0.20  0.166667      0.85          0.15            0.176471            0.529412                0.150000            0.133333               0.000472                 0.009441            0.012952              0.011791           0.011123       -0.044233           mixed
      tier0_tier1       20      0.15       0.4        0.25          0.15  0.128889      0.55          0.45            0.090909            0.454545                0.066667            0.100000              -0.014006                 0.007802            0.016822              0.014916           0.013838       -0.043730           mixed
tier0_tier1_tier2       20      0.10       0.4        0.30          0.10  0.106667      0.55          0.45            0.090909            0.363636                0.200000            0.133333              -0.015734                 0.006637            0.017265              0.015865           0.011205       -0.069742           mixed
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0  conf_0.00              0.000000      13      0.65          0.35            0.307692            0.461538                0.270833            0.190476           mixed
            tier0  conf_0.05              0.050000       9      0.45          0.55            0.444444            0.555556                0.312500            0.213333           mixed
            tier0  conf_0.10              0.100000       7      0.35          0.65            0.571429            0.571429                0.416667            0.233333           mixed
            tier0    trained              0.111110       6      0.30          0.70            0.500000            0.500000                0.250000            0.133333           mixed
            tier0  conf_0.15              0.150000       5      0.25          0.75            0.600000            0.600000                0.375000            0.150000           mixed
            tier0  conf_0.20              0.200000       5      0.25          0.75            0.600000            0.600000                0.375000            0.150000           mixed
            tier0  conf_0.25              0.250000       4      0.20          0.80            0.750000            0.750000                0.500000            0.171429           mixed
      tier0_tier1  conf_0.00              0.000000      15      0.75          0.25            0.133333            0.333333                0.250000            0.101587           mixed
      tier0_tier1  conf_0.05              0.050000      12      0.60          0.40            0.166667            0.333333                0.266667            0.116667           mixed
      tier0_tier1    trained              0.067772      11      0.55          0.45            0.181818            0.363636                0.266667            0.130000           mixed
      tier0_tier1  conf_0.10              0.100000      10      0.50          0.50            0.200000            0.400000                0.300000            0.137143           mixed
      tier0_tier1  conf_0.15              0.150000       7      0.35          0.65            0.142857            0.285714                0.125000            0.057143           mixed
      tier0_tier1  conf_0.20              0.200000       6      0.30          0.70            0.166667            0.333333                0.125000            0.066667           mixed
      tier0_tier1  conf_0.25              0.250000       1      0.05          0.95            0.000000            1.000000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.00              0.000000      14      0.70          0.30            0.357143            0.571429                0.450000            0.335556           mixed
tier0_tier1_tier2  conf_0.05              0.050000      11      0.55          0.45            0.363636            0.454545                0.433333            0.322222           mixed
tier0_tier1_tier2    trained              0.085355      11      0.55          0.45            0.363636            0.454545                0.433333            0.322222           mixed
tier0_tier1_tier2  conf_0.10              0.100000      11      0.55          0.45            0.363636            0.454545                0.433333            0.322222           mixed
tier0_tier1_tier2  conf_0.15              0.150000       7      0.35          0.65            0.285714            0.428571                0.250000            0.114286           mixed
tier0_tier1_tier2  conf_0.20              0.200000       4      0.20          0.80            0.500000            0.750000                0.333333            0.133333           mixed
tier0_tier1_tier2  conf_0.25              0.250000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000           mixed
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained             -0.044233      16      0.80          0.20            0.187500            0.500000                0.150000            0.133333           mixed
            tier0  conf_0.00              0.000000      16      0.80          0.20            0.187500            0.500000                0.150000            0.133333           mixed
            tier0  conf_0.05              0.050000      10      0.50          0.50            0.200000            0.500000                0.166667            0.146667           mixed
            tier0  conf_0.10              0.100000       9      0.45          0.55            0.222222            0.555556                0.200000            0.180000           mixed
            tier0  conf_0.15              0.150000       3      0.15          0.85            0.000000            0.333333                0.000000            0.000000           mixed
            tier0  conf_0.20              0.200000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000           mixed
            tier0  conf_0.25              0.250000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000           mixed
      tier0_tier1    trained             -0.043730      14      0.70          0.30            0.071429            0.357143                0.050000            0.044444           mixed
      tier0_tier1  conf_0.00              0.000000      14      0.70          0.30            0.071429            0.357143                0.050000            0.044444           mixed
      tier0_tier1  conf_0.05              0.050000       9      0.45          0.55            0.000000            0.333333                0.000000            0.000000           mixed
      tier0_tier1  conf_0.10              0.100000       6      0.30          0.70            0.000000            0.500000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.15              0.150000       5      0.25          0.75            0.000000            0.400000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.20              0.200000       3      0.15          0.85            0.000000            0.666667                0.000000            0.000000           mixed
      tier0_tier1  conf_0.25              0.250000       3      0.15          0.85            0.000000            0.666667                0.000000            0.000000           mixed
tier0_tier1_tier2    trained             -0.069742      14      0.70          0.30            0.071429            0.428571                0.200000            0.133333           mixed
tier0_tier1_tier2  conf_0.00              0.000000      14      0.70          0.30            0.071429            0.428571                0.200000            0.133333           mixed
tier0_tier1_tier2  conf_0.05              0.050000       8      0.40          0.60            0.125000            0.250000                0.250000            0.200000           mixed
tier0_tier1_tier2  conf_0.10              0.100000       5      0.25          0.75            0.200000            0.400000                0.250000            0.200000           mixed
tier0_tier1_tier2  conf_0.15              0.150000       4      0.20          0.80            0.250000            0.500000                0.333333            0.200000           mixed
tier0_tier1_tier2  conf_0.20              0.200000       2      0.10          0.90            0.000000            0.500000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.25              0.250000       2      0.10          0.90            0.000000            0.500000                0.000000            0.000000           mixed
```

## Diagnosis Mode Comparison
- Whole-run and post-alert-window diagnosis are exported together so the diagnosis mode can be evaluated directly.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile diagnosis_target    diagnosis_mode  family_acc  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau                       status  min_class_count  min_group_count    group_key  include_workload
            tier0       20      0.40      0.55      0.400000  0.307071               0.023274                 0.016414           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.30      0.55      0.300000  0.184615               0.025832                 0.025567           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.40      0.60      0.400000  0.345641               0.023417                 0.021452           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.30      0.65      0.300000  0.273895               0.014237                 0.013629           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.20      0.40      0.200000  0.142857               0.042802                 0.026612           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.10      0.45      0.100000  0.114286               0.034426                 0.013925           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.25      0.55      0.250000  0.210000               0.005851                 0.005954           mixed     hierarchical         whole_run        0.25      0.30          0.70            0.500000            0.666667                0.416667            0.260000            0.012952              0.011791           0.011123        0.111110                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.20      0.45      0.200000  0.173333               0.012953                 0.021257           mixed     hierarchical         whole_run        0.25      0.70          0.30            0.214286            0.428571                0.233333            0.187143            0.016822              0.014916           0.013838        0.067772                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.30      0.55      0.300000  0.269394               0.010090                 0.020269           mixed     hierarchical         whole_run        0.30      0.45          0.55            0.333333            0.555556                0.333333            0.293333            0.017265              0.015865           0.011205        0.085355                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.20      0.50      0.200000  0.166667               0.000472                 0.009441           mixed     hierarchical post_alert_window        0.25      0.85          0.15            0.176471            0.529412                0.150000            0.133333            0.012952              0.011791           0.011123       -0.044233                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.15      0.40      0.150000  0.128889              -0.014006                 0.007802           mixed     hierarchical post_alert_window        0.25      0.55          0.45            0.090909            0.454545                0.066667            0.100000            0.016822              0.014916           0.013838       -0.043730                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.10      0.40      0.100000  0.106667              -0.015734                 0.006637           mixed     hierarchical post_alert_window        0.30      0.55          0.45            0.090909            0.363636                0.200000            0.133333            0.017265              0.015865           0.011205       -0.069742                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.55      0.75      0.472222  0.398551               0.032838                 0.034712           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.45      0.65      0.416667  0.333333               0.026477                 0.027923           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.45      0.75      0.527778  0.450142               0.030328                 0.024632           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.738823         0.121557     0.139620              tier0           mixed
  BRANCH     0.786606         0.083102     0.130292              tier0           mixed
   CACHE     0.561482         0.342443     0.096075              tier0           mixed
   MEMBW     0.799683         0.090869     0.109448              tier0           mixed
     TLB     0.737688         0.122935     0.139376              tier0           mixed
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC               memory_io       0.265155         0.425388             0.068657                 0.205676                 0.035124           mixed
  BRANCH               memory_io       0.239751         0.487631             0.044518                 0.184526                 0.043574           mixed
   CACHE               memory_io       0.453630         0.307523             0.057138                 0.136889                 0.044820           mixed
   MEMBW               memory_io       0.220225         0.514546             0.051603                 0.159098                 0.054528           mixed
     TLB               memory_io       0.288527         0.432756             0.062219                 0.185624                 0.030873           mixed
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
            tier0                    0.0                             0.0                           0.0                 0.30                     92.0                 716.5                 0.2                 0.2                0.20           mixed
      tier0_tier1                    0.0                             0.0                           0.0                 0.45                     92.0                 750.2                 0.3                 0.3                0.35           mixed
tier0_tier1_tier2                    0.0                             0.0                           0.0                 0.45                     92.0                 700.0                 0.3                 0.3                0.35           mixed
```

## Files
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B90_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B90_a0.05_k3/config_runtime_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B90_a0.05_k3/run_context.json`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B90_a0.05_k3/case_inventory.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B90_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B90_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B90_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B90_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B90_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B90_a0.05_k3/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B90_a0.05_k3/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B90_a0.05_k3/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B90_a0.05_k3/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B90_a0.05_k3/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B90_a0.05_k3/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B90_a0.05_k3/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B90_a0.05_k3/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B90_a0.05_k3/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B90_a0.05_k3/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B90_a0.05_k3/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B90_a0.05_k3/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B90_a0.05_k3/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B90_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B90_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B90_a0.05_k3/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B90_a0.05_k3/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B90_a0.05_k3/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B90_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B90_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B90_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B90_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B90_a0.05_k3/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B90_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B90_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B90_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B90_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B90_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B90_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B90_a0.05_k3/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B90_a0.05_k3/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B90_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B90_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B90_a0.05_k3/figures/fig_detection_latency.png`
