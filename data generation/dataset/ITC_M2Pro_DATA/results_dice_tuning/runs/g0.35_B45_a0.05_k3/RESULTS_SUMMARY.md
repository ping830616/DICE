# DICE Full Retrain Results

## Setup
- Feature profile: mixed ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_core_5hz.csv', 'tier2': 'tier2_core_5hz.csv'})
- Protocol: global, benign-only fit/calibration, block_B=45, alpha=0.05, persist_k=3, gain=0.35
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
          mixed             tier0       24          46          2.428952   0.8000 0.931899         1.0        1.0            0.0            0.3              0.005889              0.012124                      0.0                 0.006696
          mixed       tier0_tier1       24          57          2.825465   0.8250 0.951460         1.0        1.0            0.0            0.5              0.000047              0.000116                      0.0                 0.000054
          mixed tier0_tier1_tier2       24          64          3.143032   0.8375 0.957016         1.0        1.0            0.0            0.5              0.000049              0.000126                      0.0                 0.000061
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
          mixed   ATOMIC   0.7500 0.770833         1.0        1.0          0.000049          0.000097                  0.0             0.000053       1.937856      0.000047         53.961498         0.000053
          mixed   BRANCH   0.9375 0.950000         1.0        1.0          0.000049          0.000199                  0.0             0.000133       3.951456      0.000149        134.165269         0.000133
          mixed    CACHE   0.8125 0.804167         1.0        1.0          0.000049          0.000100                  0.0             0.000061       1.997613      0.000050         61.760581         0.000061
          mixed    MEMBW   0.9375 0.950000         1.0        1.0          0.000049          0.000157                  0.0             0.000089       3.129080      0.000108         89.582295         0.000089
          mixed      TLB   0.7500 0.679167         1.0        1.0          0.000049          0.000112                  0.0             0.000050       2.238399      0.000063         50.736001         0.000050
```

## Paper-style Aggregates (Final Config)
- Base score mean stressor AUC-PR (all five): **0.8308**
- Base score mean stressor ROC-AUC (all five): **0.8375**
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
            tier0       20      0.40       0.6          0.40  0.322424               0.023627                 0.017760           mixed
      tier0_tier1       20      0.35       0.6          0.35  0.251282               0.023481                 0.022677           mixed
tier0_tier1_tier2       20      0.50       0.6          0.50  0.486593               0.020523                 0.017932           mixed
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.30      0.50          0.30  0.310476               0.014794                 0.009653           mixed
      tier0_tier1       20      0.10      0.25          0.10  0.057143               0.081732                 0.058573           mixed
tier0_tier1_tier2       20      0.15      0.45          0.15  0.166667               0.058515                 0.016402           mixed
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.30      0.65          0.30  0.310173               0.013796                 0.010189           mixed
      tier0_tier1       20      0.25      0.50          0.25  0.294286               0.015080                 0.011552           mixed
tier0_tier1_tier2       20      0.35      0.60          0.35  0.345397               0.014062                 0.007958           mixed
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.55      0.80      0.472222  0.398551               0.032268                 0.032995           mixed
      tier0_tier1       20      0.50      0.70      0.444444  0.356745               0.026297                 0.030281           mixed
tier0_tier1_tier2       20      0.45      0.75      0.527778  0.444042               0.026904                 0.027831           mixed
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.40      0.60        0.35          0.40  0.370476      0.45          0.55            0.555556            0.777778                0.450000            0.430000               0.014015                 0.011171            0.011727              0.009446           0.014349        0.125742           mixed
      tier0_tier1       20      0.35      0.65        0.40          0.35  0.311111      0.55          0.45            0.454545            0.636364                0.466667            0.333333               0.010066                 0.017724            0.017906              0.013852           0.012959        0.088179           mixed
tier0_tier1_tier2       20      0.45      0.60        0.25          0.45  0.443203      0.50          0.50            0.500000            0.700000                0.500000            0.513333               0.010868                 0.015615            0.019131              0.014823           0.014722        0.094990           mixed
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.30      0.50        0.35          0.30  0.259740      0.80          0.20            0.250000            0.437500                0.233333            0.203175               0.001378                 0.008998            0.011727              0.009446           0.014349       -0.062553           mixed
      tier0_tier1       20      0.15      0.40        0.40          0.15  0.112727      0.65          0.35            0.153846            0.384615                0.166667            0.137143               0.014431                 0.026569            0.017906              0.013852           0.012959       -0.161691           mixed
tier0_tier1_tier2       20      0.20      0.45        0.25          0.20  0.186667      0.55          0.45            0.090909            0.363636                0.100000            0.100000               0.003921                 0.009762            0.019131              0.014823           0.014722       -0.063803           mixed
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0  conf_0.00              0.000000      17      0.85          0.15            0.411765            0.588235                0.450000            0.346667           mixed
            tier0  conf_0.05              0.050000      14      0.70          0.30            0.428571            0.642857                0.483333            0.355556           mixed
            tier0  conf_0.10              0.100000       8      0.40          0.60            0.500000            0.625000                0.312500            0.233333           mixed
            tier0    trained              0.125742       5      0.25          0.75            0.600000            0.800000                0.375000            0.150000           mixed
            tier0  conf_0.15              0.150000       5      0.25          0.75            0.600000            0.800000                0.375000            0.150000           mixed
            tier0  conf_0.20              0.200000       5      0.25          0.75            0.600000            0.800000                0.375000            0.150000           mixed
            tier0  conf_0.25              0.250000       4      0.20          0.80            0.750000            1.000000                0.500000            0.171429           mixed
      tier0_tier1  conf_0.00              0.000000      15      0.75          0.25            0.333333            0.600000                0.383333            0.246667           mixed
      tier0_tier1  conf_0.05              0.050000      12      0.60          0.40            0.333333            0.583333                0.400000            0.203175           mixed
      tier0_tier1    trained              0.088179      10      0.50          0.50            0.300000            0.500000                0.400000            0.180000           mixed
      tier0_tier1  conf_0.10              0.100000       9      0.45          0.55            0.333333            0.444444                0.400000            0.194286           mixed
      tier0_tier1  conf_0.15              0.150000       5      0.25          0.75            0.400000            0.600000                0.400000            0.233333           mixed
      tier0_tier1  conf_0.20              0.200000       2      0.10          0.90            0.000000            0.500000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.25              0.250000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.00              0.000000      16      0.80          0.20            0.500000            0.625000                0.550000            0.520000           mixed
tier0_tier1_tier2  conf_0.05              0.050000      12      0.60          0.40            0.416667            0.583333                0.433333            0.355556           mixed
tier0_tier1_tier2    trained              0.094990       8      0.40          0.60            0.375000            0.625000                0.416667            0.233333           mixed
tier0_tier1_tier2  conf_0.10              0.100000       8      0.40          0.60            0.375000            0.625000                0.416667            0.233333           mixed
tier0_tier1_tier2  conf_0.15              0.150000       6      0.30          0.70            0.500000            0.833333                0.500000            0.266667           mixed
tier0_tier1_tier2  conf_0.20              0.200000       3      0.15          0.85            0.666667            0.666667                0.500000            0.160000           mixed
tier0_tier1_tier2  conf_0.25              0.250000       1      0.05          0.95            1.000000            1.000000                1.000000            0.200000           mixed
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained             -0.062553      16      0.80          0.20            0.250000            0.437500                0.233333            0.203175           mixed
            tier0  conf_0.00              0.000000      16      0.80          0.20            0.250000            0.437500                0.233333            0.203175           mixed
            tier0  conf_0.05              0.050000      10      0.50          0.50            0.200000            0.300000                0.166667            0.160000           mixed
            tier0  conf_0.10              0.100000       6      0.30          0.70            0.333333            0.333333                0.333333            0.200000           mixed
            tier0  conf_0.15              0.150000       4      0.20          0.80            0.500000            0.500000                0.666667            0.333333           mixed
            tier0  conf_0.20              0.200000       3      0.15          0.85            0.333333            0.333333                0.500000            0.200000           mixed
            tier0  conf_0.25              0.250000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000           mixed
      tier0_tier1    trained             -0.161691      14      0.70          0.30            0.071429            0.357143                0.066667            0.050000           mixed
      tier0_tier1  conf_0.00              0.000000      14      0.70          0.30            0.071429            0.357143                0.066667            0.050000           mixed
      tier0_tier1  conf_0.05              0.050000      11      0.55          0.45            0.090909            0.363636                0.100000            0.066667           mixed
      tier0_tier1  conf_0.10              0.100000      10      0.50          0.50            0.100000            0.300000                0.200000            0.080000           mixed
      tier0_tier1  conf_0.15              0.150000      10      0.50          0.50            0.100000            0.300000                0.200000            0.080000           mixed
      tier0_tier1  conf_0.20              0.200000       8      0.40          0.60            0.125000            0.375000                0.200000            0.100000           mixed
      tier0_tier1  conf_0.25              0.250000       7      0.35          0.65            0.000000            0.285714                0.000000            0.000000           mixed
tier0_tier1_tier2    trained             -0.063803      15      0.75          0.25            0.200000            0.466667                0.216667            0.216667           mixed
tier0_tier1_tier2  conf_0.00              0.000000      14      0.70          0.30            0.142857            0.428571                0.150000            0.150000           mixed
tier0_tier1_tier2  conf_0.05              0.050000       9      0.45          0.55            0.000000            0.333333                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.10              0.100000       6      0.30          0.70            0.000000            0.333333                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.15              0.150000       6      0.30          0.70            0.000000            0.333333                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.20              0.200000       4      0.20          0.80            0.000000            0.500000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.25              0.250000       4      0.20          0.80            0.000000            0.500000                0.000000            0.000000           mixed
```

## Diagnosis Mode Comparison
- Whole-run and post-alert-window diagnosis are exported together so the diagnosis mode can be evaluated directly.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile diagnosis_target    diagnosis_mode  family_acc  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau                       status  min_class_count  min_group_count    group_key  include_workload
            tier0       20      0.40      0.60      0.400000  0.322424               0.023627                 0.017760           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.35      0.60      0.350000  0.251282               0.023481                 0.022677           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.50      0.60      0.500000  0.486593               0.020523                 0.017932           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.30      0.50      0.300000  0.310476               0.014794                 0.009653           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.10      0.25      0.100000  0.057143               0.081732                 0.058573           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.15      0.45      0.150000  0.166667               0.058515                 0.016402           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.40      0.60      0.400000  0.370476               0.014015                 0.011171           mixed     hierarchical         whole_run        0.35      0.45          0.55            0.555556            0.777778                0.450000            0.430000            0.011727              0.009446           0.014349        0.125742                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.35      0.65      0.350000  0.311111               0.010066                 0.017724           mixed     hierarchical         whole_run        0.40      0.55          0.45            0.454545            0.636364                0.466667            0.333333            0.017906              0.013852           0.012959        0.088179                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.45      0.60      0.450000  0.443203               0.010868                 0.015615           mixed     hierarchical         whole_run        0.25      0.50          0.50            0.500000            0.700000                0.500000            0.513333            0.019131              0.014823           0.014722        0.094990                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.30      0.50      0.300000  0.259740               0.001378                 0.008998           mixed     hierarchical post_alert_window        0.35      0.80          0.20            0.250000            0.437500                0.233333            0.203175            0.011727              0.009446           0.014349       -0.062553                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.15      0.40      0.150000  0.112727               0.014431                 0.026569           mixed     hierarchical post_alert_window        0.40      0.65          0.35            0.153846            0.384615                0.166667            0.137143            0.017906              0.013852           0.012959       -0.161691                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.20      0.45      0.200000  0.186667               0.003921                 0.009762           mixed     hierarchical post_alert_window        0.25      0.55          0.45            0.090909            0.363636                0.100000            0.100000            0.019131              0.014823           0.014722       -0.063803                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.55      0.80      0.472222  0.398551               0.032268                 0.032995           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.50      0.70      0.444444  0.356745               0.026297                 0.030281           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.45      0.75      0.527778  0.444042               0.026904                 0.027831           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.720017         0.128596     0.151387              tier0           mixed
  BRANCH     0.772435         0.084498     0.143067              tier0           mixed
   CACHE     0.548643         0.346820     0.104537              tier0           mixed
   MEMBW     0.787505         0.091702     0.120793              tier0           mixed
     TLB     0.715111         0.130174     0.154715              tier0           mixed
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC               memory_io       0.264735         0.410057             0.078412                 0.214130                 0.032666           mixed
  BRANCH               memory_io       0.243513         0.468147             0.047872                 0.197469                 0.042999           mixed
   CACHE               memory_io       0.460850         0.286663             0.063974                 0.143750                 0.044763           mixed
   MEMBW               memory_io       0.227676         0.492691             0.054600                 0.170320                 0.054713           mixed
     TLB               memory_io       0.297365         0.405168             0.070595                 0.198697                 0.028175           mixed
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
            tier0                    0.0                             0.0                      1.884817                  0.3                     63.5                 617.5                 0.2                 0.2                0.25           mixed
      tier0_tier1                    0.0                             0.0                      0.000000                  0.5                     64.5                 834.6                 0.3                 0.3                0.40           mixed
tier0_tier1_tier2                    0.0                             0.0                      0.000000                  0.5                     63.0                 833.7                 0.3                 0.3                0.40           mixed
```

## Files
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B45_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B45_a0.05_k3/config_runtime_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B45_a0.05_k3/run_context.json`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B45_a0.05_k3/case_inventory.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B45_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B45_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B45_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B45_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B45_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B45_a0.05_k3/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B45_a0.05_k3/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B45_a0.05_k3/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B45_a0.05_k3/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B45_a0.05_k3/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B45_a0.05_k3/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B45_a0.05_k3/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B45_a0.05_k3/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B45_a0.05_k3/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B45_a0.05_k3/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B45_a0.05_k3/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B45_a0.05_k3/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B45_a0.05_k3/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B45_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B45_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B45_a0.05_k3/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B45_a0.05_k3/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B45_a0.05_k3/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B45_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B45_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B45_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B45_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B45_a0.05_k3/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B45_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B45_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B45_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B45_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B45_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B45_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B45_a0.05_k3/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B45_a0.05_k3/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B45_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B45_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B45_a0.05_k3/figures/fig_detection_latency.png`
