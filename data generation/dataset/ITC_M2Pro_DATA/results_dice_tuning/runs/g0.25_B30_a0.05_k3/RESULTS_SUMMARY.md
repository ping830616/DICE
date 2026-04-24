# DICE Full Retrain Results

## Setup
- Feature profile: mixed ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_core_5hz.csv', 'tier2': 'tier2_core_5hz.csv'})
- Protocol: global, benign-only fit/calibration, block_B=30, alpha=0.05, persist_k=3, gain=0.25
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
          mixed             tier0       24          46          2.550011   0.8000 0.931899         1.0        1.0           0.25           0.30              0.008101              0.016247                      0.0                 0.009068
          mixed       tier0_tier1       24          57          2.904898   0.8375 0.957016         1.0        1.0           0.25           0.55              0.000048              0.000115                      0.0                 0.000057
          mixed tier0_tier1_tier2       24          64          3.257194   0.8500 0.962016         1.0        1.0           0.25           0.55              0.000050              0.000124                      0.0                 0.000061
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
          mixed   ATOMIC   0.7500 0.770833         1.0        1.0           0.00005          0.000091                  0.0             0.000044       1.803572      0.000041         45.295751         0.000044
          mixed   BRANCH   0.9375 0.950000         1.0        1.0           0.00005          0.000195                  0.0             0.000130       3.831547      0.000145        130.630705         0.000130
          mixed    CACHE   0.8125 0.804167         1.0        1.0           0.00005          0.000102                  0.0             0.000061       2.016082      0.000052         61.983423         0.000061
          mixed    MEMBW   0.9375 0.950000         1.0        1.0           0.00005          0.000148                  0.0             0.000081       2.911749      0.000098         81.916446         0.000081
          mixed      TLB   0.8125 0.804167         1.0        1.0           0.00005          0.000111                  0.0             0.000043       2.179604      0.000060         44.443985         0.000043
```

## Paper-style Aggregates (Final Config)
- Base score mean stressor AUC-PR (all five): **0.8558**
- Base score mean stressor ROC-AUC (all five): **0.8500**
- WC score mean stressor AUC-PR (all five): **1.0000**
- WC score mean stressor ROC-AUC (all five): **1.0000**
- Base score mean stressor AUC-PR (excluding BRANCH/TLB): **0.8417**
- Base score mean stressor ROC-AUC (excluding BRANCH/TLB): **0.8333**
- WC score mean stressor AUC-PR (excluding BRANCH/TLB): **1.0000**
- WC score mean stressor ROC-AUC (excluding BRANCH/TLB): **1.0000**

## Diagnosis
- Feature-level diagnosis uses normalized whole-run residual-attribution prototypes as the default paper-facing result, with diagnosis-only filtering that removes monotonic counters and downweights generic memory-state features.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.30      0.65          0.30  0.238961               0.026699                 0.019982           mixed
      tier0_tier1       20      0.30      0.70          0.30  0.216117               0.020004                 0.013065           mixed
tier0_tier1_tier2       20      0.55      0.70          0.55  0.553260               0.018853                 0.015809           mixed
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.25      0.50          0.25  0.243175               0.016909                 0.011354           mixed
      tier0_tier1       20      0.15      0.35          0.15  0.128205               0.111738                 0.066647           mixed
tier0_tier1_tier2       20      0.10      0.35          0.10  0.100000               0.098441                 0.027835           mixed
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.25      0.65          0.25  0.214444               0.012582                 0.007010           mixed
      tier0_tier1       20      0.30      0.65          0.30  0.299697               0.012032                 0.008008           mixed
tier0_tier1_tier2       20      0.45      0.60          0.45  0.444444               0.011534                 0.009729           mixed
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.55      0.80      0.472222  0.398551               0.034380                 0.037193           mixed
      tier0_tier1       20      0.50      0.75      0.444444  0.356745               0.025184                 0.026770           mixed
tier0_tier1_tier2       20      0.55      0.75      0.583333  0.531039               0.026259                 0.026862           mixed
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.35      0.65        0.55          0.35  0.303377      0.45          0.55            0.444444            0.666667                0.333333            0.260000              -0.000316                 0.011054            0.013405              0.013555           0.010002        0.124961           mixed
      tier0_tier1       20      0.25      0.65        0.45          0.25  0.195556      0.60          0.40            0.333333            0.666667                0.466667            0.266667               0.002748                 0.005418            0.020520              0.017128           0.013185        0.033980           mixed
tier0_tier1_tier2       20      0.45      0.70        0.30          0.45  0.423810      0.50          0.50            0.500000            0.900000                0.466667            0.366667               0.007495                 0.005760            0.020975              0.015792           0.016887        0.085678           mixed
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.35      0.55        0.55          0.35  0.343333      0.45          0.55            0.222222            0.444444                0.133333            0.088889              -0.025085                 0.004003            0.013405              0.013555           0.010002        0.020563           mixed
      tier0_tier1       20      0.25      0.35        0.45          0.25  0.170629      0.65          0.35            0.307692            0.384615                0.266667            0.222222              -0.048362                 0.001553            0.020520              0.017128           0.013185       -0.224394           mixed
tier0_tier1_tier2       20      0.15      0.30        0.30          0.15  0.117172      0.40          0.60            0.000000            0.250000                0.000000            0.000000               0.027553                 0.005487            0.020975              0.015792           0.016887        0.367151           mixed
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0  conf_0.00              0.000000      13      0.65          0.35            0.384615            0.692308                0.283333            0.269091           mixed
            tier0  conf_0.05              0.050000      11      0.55          0.45            0.454545            0.727273                0.283333            0.269091           mixed
            tier0  conf_0.10              0.100000       8      0.40          0.60            0.500000            0.625000                0.416667            0.274286           mixed
            tier0    trained              0.124961       5      0.25          0.75            0.600000            0.600000                0.555556            0.260000           mixed
            tier0  conf_0.15              0.150000       3      0.15          0.85            0.666667            0.666667                0.666667            0.160000           mixed
            tier0  conf_0.20              0.200000       3      0.15          0.85            0.666667            0.666667                0.666667            0.160000           mixed
            tier0  conf_0.25              0.250000       3      0.15          0.85            0.666667            0.666667                0.666667            0.160000           mixed
      tier0_tier1  conf_0.00              0.000000      14      0.70          0.30            0.285714            0.642857                0.400000            0.246032           mixed
      tier0_tier1    trained              0.033980       9      0.45          0.55            0.333333            0.555556                0.400000            0.200000           mixed
      tier0_tier1  conf_0.05              0.050000       9      0.45          0.55            0.333333            0.555556                0.400000            0.200000           mixed
      tier0_tier1  conf_0.10              0.100000       6      0.30          0.70            0.333333            0.500000                0.500000            0.266667           mixed
      tier0_tier1  conf_0.15              0.150000       5      0.25          0.75            0.200000            0.400000                0.333333            0.066667           mixed
      tier0_tier1  conf_0.20              0.200000       4      0.20          0.80            0.250000            0.500000                0.333333            0.080000           mixed
      tier0_tier1  conf_0.25              0.250000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.00              0.000000      15      0.75          0.25            0.533333            0.666667                0.600000            0.529091           mixed
tier0_tier1_tier2  conf_0.05              0.050000       9      0.45          0.55            0.555556            0.666667                0.583333            0.400000           mixed
tier0_tier1_tier2    trained              0.085678       6      0.30          0.70            0.500000            0.666667                0.444444            0.214286           mixed
tier0_tier1_tier2  conf_0.10              0.100000       6      0.30          0.70            0.500000            0.666667                0.444444            0.214286           mixed
tier0_tier1_tier2  conf_0.15              0.150000       5      0.25          0.75            0.400000            0.600000                0.333333            0.114286           mixed
tier0_tier1_tier2  conf_0.20              0.200000       4      0.20          0.80            0.500000            0.750000                0.333333            0.133333           mixed
tier0_tier1_tier2  conf_0.25              0.250000       1      0.05          0.95            1.000000            1.000000                1.000000            0.200000           mixed
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0  conf_0.00              0.000000      12      0.60          0.40            0.333333            0.500000                0.300000            0.246667           mixed
            tier0    trained              0.020563      11      0.55          0.45            0.363636            0.545455                0.300000            0.280000           mixed
            tier0  conf_0.05              0.050000       6      0.30          0.70            0.166667            0.500000                0.125000            0.057143           mixed
            tier0  conf_0.10              0.100000       2      0.10          0.90            0.500000            1.000000                0.500000            0.133333           mixed
            tier0  conf_0.15              0.150000       1      0.05          0.95            1.000000            1.000000                1.000000            0.200000           mixed
            tier0  conf_0.20              0.200000       1      0.05          0.95            1.000000            1.000000                1.000000            0.200000           mixed
            tier0  conf_0.25              0.250000       1      0.05          0.95            1.000000            1.000000                1.000000            0.200000           mixed
      tier0_tier1    trained             -0.224394      14      0.70          0.30            0.357143            0.428571                0.283333            0.238889           mixed
      tier0_tier1  conf_0.00              0.000000      11      0.55          0.45            0.181818            0.272727                0.200000            0.157143           mixed
      tier0_tier1  conf_0.05              0.050000       9      0.45          0.55            0.111111            0.222222                0.100000            0.057143           mixed
      tier0_tier1  conf_0.10              0.100000       7      0.35          0.65            0.142857            0.142857                0.200000            0.066667           mixed
      tier0_tier1  conf_0.15              0.150000       6      0.30          0.70            0.166667            0.166667                0.200000            0.066667           mixed
      tier0_tier1  conf_0.20              0.200000       5      0.25          0.75            0.000000            0.000000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.25              0.250000       4      0.20          0.80            0.000000            0.000000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.00              0.000000      14      0.70          0.30            0.142857            0.285714                0.116667            0.123810           mixed
tier0_tier1_tier2  conf_0.05              0.050000       8      0.40          0.60            0.000000            0.250000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.10              0.100000       6      0.30          0.70            0.000000            0.333333                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.15              0.150000       4      0.20          0.80            0.000000            0.500000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.20              0.200000       4      0.20          0.80            0.000000            0.500000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.25              0.250000       4      0.20          0.80            0.000000            0.500000                0.000000            0.000000           mixed
tier0_tier1_tier2    trained              0.367151       4      0.20          0.80            0.000000            0.500000                0.000000            0.000000           mixed
```

## Diagnosis Mode Comparison
- Whole-run and post-alert-window diagnosis are exported together so the diagnosis mode can be evaluated directly.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile diagnosis_target    diagnosis_mode  family_acc  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau                       status  min_class_count  min_group_count    group_key  include_workload
            tier0       20      0.30      0.65      0.300000  0.238961               0.026699                 0.019982           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.30      0.70      0.300000  0.216117               0.020004                 0.013065           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.55      0.70      0.550000  0.553260               0.018853                 0.015809           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.25      0.50      0.250000  0.243175               0.016909                 0.011354           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.15      0.35      0.150000  0.128205               0.111738                 0.066647           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.10      0.35      0.100000  0.100000               0.098441                 0.027835           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.35      0.65      0.350000  0.303377              -0.000316                 0.011054           mixed     hierarchical         whole_run        0.55      0.45          0.55            0.444444            0.666667                0.333333            0.260000            0.013405              0.013555           0.010002        0.124961                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.25      0.65      0.250000  0.195556               0.002748                 0.005418           mixed     hierarchical         whole_run        0.45      0.60          0.40            0.333333            0.666667                0.466667            0.266667            0.020520              0.017128           0.013185        0.033980                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.45      0.70      0.450000  0.423810               0.007495                 0.005760           mixed     hierarchical         whole_run        0.30      0.50          0.50            0.500000            0.900000                0.466667            0.366667            0.020975              0.015792           0.016887        0.085678                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.35      0.55      0.350000  0.343333              -0.025085                 0.004003           mixed     hierarchical post_alert_window        0.55      0.45          0.55            0.222222            0.444444                0.133333            0.088889            0.013405              0.013555           0.010002        0.020563                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.25      0.35      0.250000  0.170629              -0.048362                 0.001553           mixed     hierarchical post_alert_window        0.45      0.65          0.35            0.307692            0.384615                0.266667            0.222222            0.020520              0.017128           0.013185       -0.224394                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.15      0.30      0.150000  0.117172               0.027553                 0.005487           mixed     hierarchical post_alert_window        0.30      0.40          0.60            0.000000            0.250000                0.000000            0.000000            0.020975              0.015792           0.016887        0.367151                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.55      0.80      0.472222  0.398551               0.034380                 0.037193           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.50      0.75      0.444444  0.356745               0.025184                 0.026770           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.55      0.75      0.583333  0.531039               0.026259                 0.026862           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.702236         0.141467     0.156297              tier0           mixed
  BRANCH     0.761602         0.087725     0.150673              tier0           mixed
   CACHE     0.538547         0.352738     0.108715              tier0           mixed
   MEMBW     0.776454         0.095384     0.128161              tier0           mixed
     TLB     0.698605         0.139289     0.162106              tier0           mixed
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC               memory_io       0.263514         0.399824             0.090116                 0.215379                 0.031168           mixed
  BRANCH               memory_io       0.247107         0.457390             0.050833                 0.203286                 0.041385           mixed
   CACHE               memory_io       0.467015         0.273239             0.069823                 0.145337                 0.044586           mixed
   MEMBW               memory_io       0.233434         0.478486             0.058523                 0.176247                 0.053310           mixed
     TLB               memory_io       0.302111         0.389933             0.078887                 0.202975                 0.026094           mixed
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
            tier0                   0.25                        0.927835                      2.783505                 0.30                     53.0                 605.5                0.20                0.20                0.25           mixed
      tier0_tier1                   0.25                        0.927835                      2.783505                 0.55                     76.0                 818.0                0.30                0.30                0.45           mixed
tier0_tier1_tier2                   0.25                        0.927835                      2.783505                 0.55                     42.0                 817.0                0.35                0.35                0.45           mixed
```

## Files
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B30_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B30_a0.05_k3/config_runtime_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B30_a0.05_k3/run_context.json`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B30_a0.05_k3/case_inventory.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B30_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B30_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B30_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B30_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B30_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B30_a0.05_k3/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B30_a0.05_k3/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B30_a0.05_k3/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B30_a0.05_k3/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B30_a0.05_k3/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B30_a0.05_k3/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B30_a0.05_k3/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B30_a0.05_k3/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B30_a0.05_k3/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B30_a0.05_k3/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B30_a0.05_k3/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B30_a0.05_k3/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B30_a0.05_k3/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B30_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B30_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B30_a0.05_k3/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B30_a0.05_k3/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B30_a0.05_k3/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B30_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B30_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B30_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B30_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B30_a0.05_k3/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B30_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B30_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B30_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B30_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B30_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B30_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B30_a0.05_k3/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B30_a0.05_k3/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B30_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B30_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B30_a0.05_k3/figures/fig_detection_latency.png`
