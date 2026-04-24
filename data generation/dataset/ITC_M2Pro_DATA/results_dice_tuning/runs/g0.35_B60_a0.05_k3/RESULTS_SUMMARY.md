# DICE Full Retrain Results

## Setup
- Feature profile: mixed ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_core_5hz.csv', 'tier2': 'tier2_core_5hz.csv'})
- Protocol: global, benign-only fit/calibration, block_B=60, alpha=0.05, persist_k=3, gain=0.35
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
          mixed             tier0       24          46          2.375338   0.8000 0.931899         1.0        1.0            0.0           0.30              0.005518              0.011960                      0.0                 0.006561
          mixed       tier0_tier1       24          57          2.876548   0.8250 0.951460         1.0        1.0            0.0           0.45              0.000045              0.000110                      0.0                 0.000056
          mixed tier0_tier1_tier2       24          64          3.342101   0.8375 0.953625         1.0        1.0            0.0           0.45              0.000048              0.000119                      0.0                 0.000062
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
          mixed   ATOMIC   0.8125 0.804167         1.0        1.0          0.000048          0.000099                  0.0             0.000057       2.051449      0.000051         58.378895         0.000057
          mixed   BRANCH   0.9375 0.950000         1.0        1.0          0.000048          0.000186                  0.0             0.000125       3.845005      0.000138        125.990235         0.000125
          mixed    CACHE   0.8125 0.804167         1.0        1.0          0.000048          0.000100                  0.0             0.000061       2.081700      0.000053         61.971078         0.000061
          mixed    MEMBW   0.8750 0.887500         1.0        1.0          0.000048          0.000161                  0.0             0.000093       3.325768      0.000113         93.724244         0.000093
          mixed      TLB   0.7500 0.679167         1.0        1.0          0.000048          0.000113                  0.0             0.000054       2.347351      0.000066         54.690889         0.000054
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
            tier0       20      0.40       0.6          0.40  0.322424               0.023811                 0.018228           mixed
      tier0_tier1       20      0.35       0.6          0.35  0.251282               0.023807                 0.021163           mixed
tier0_tier1_tier2       20      0.45       0.6          0.45  0.425641               0.021160                 0.018960           mixed
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.30      0.65          0.30  0.276667               0.016615                 0.017499           mixed
      tier0_tier1       20      0.10      0.35          0.10  0.053333               0.064610                 0.034712           mixed
tier0_tier1_tier2       20      0.15      0.40          0.15  0.150649               0.052217                 0.020459           mixed
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.30      0.65          0.30  0.310173               0.014184                 0.010994           mixed
      tier0_tier1       20      0.25      0.50          0.25  0.283175               0.014274                 0.010998           mixed
tier0_tier1_tier2       20      0.35      0.60          0.35  0.345397               0.014208                 0.012064           mixed
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.55      0.75      0.472222  0.398551               0.032695                 0.033616           mixed
      tier0_tier1       20      0.50      0.70      0.444444  0.356745               0.027100                 0.031473           mixed
tier0_tier1_tier2       20      0.45      0.75      0.527778  0.444042               0.026839                 0.028020           mixed
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.45      0.65        0.45          0.45  0.435556      0.45          0.55            0.555556            0.777778                0.450000            0.430000               0.011926                 0.011056            0.012342              0.010159           0.011432        0.123634           mixed
      tier0_tier1       20      0.35      0.60        0.40          0.35  0.308283      0.55          0.45            0.454545            0.636364                0.466667            0.333333               0.010101                 0.018397            0.017334              0.011810           0.011451        0.061681           mixed
tier0_tier1_tier2       20      0.45      0.60        0.30          0.45  0.439394      0.50          0.50            0.500000            0.700000                0.500000            0.513333               0.010455                 0.018089            0.018342              0.016915           0.011451        0.085697           mixed
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.30      0.65        0.45          0.30  0.225758       0.9           0.1            0.277778            0.666667                0.266667            0.203535               0.004742                 0.017499            0.012342              0.010159           0.011432       -0.068487           mixed
      tier0_tier1       20      0.15      0.45        0.40          0.15  0.120000       0.6           0.4            0.166667            0.583333                0.166667            0.133333               0.009998                 0.011177            0.017334              0.011810           0.011451        0.061167           mixed
tier0_tier1_tier2       20      0.20      0.40        0.30          0.20  0.186667       0.4           0.6            0.000000            0.125000                0.000000            0.000000              -0.001141                 0.006517            0.018342              0.016915           0.011451        0.014201           mixed
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0  conf_0.00              0.000000      15      0.75          0.25            0.466667            0.666667                0.450000            0.413333           mixed
            tier0  conf_0.05              0.050000      14      0.70          0.30            0.500000            0.714286                0.483333            0.422222           mixed
            tier0  conf_0.10              0.100000       8      0.40          0.60            0.500000            0.625000                0.312500            0.233333           mixed
            tier0    trained              0.123634       5      0.25          0.75            0.600000            0.800000                0.375000            0.150000           mixed
            tier0  conf_0.15              0.150000       5      0.25          0.75            0.600000            0.800000                0.375000            0.150000           mixed
            tier0  conf_0.20              0.200000       5      0.25          0.75            0.600000            0.800000                0.375000            0.150000           mixed
            tier0  conf_0.25              0.250000       4      0.20          0.80            0.750000            1.000000                0.500000            0.171429           mixed
      tier0_tier1  conf_0.00              0.000000      15      0.75          0.25            0.333333            0.533333                0.383333            0.244444           mixed
      tier0_tier1  conf_0.05              0.050000      12      0.60          0.40            0.333333            0.500000                0.400000            0.200000           mixed
      tier0_tier1    trained              0.061681      11      0.55          0.45            0.363636            0.454545                0.400000            0.214286           mixed
      tier0_tier1  conf_0.10              0.100000      10      0.50          0.50            0.400000            0.500000                0.400000            0.233333           mixed
      tier0_tier1  conf_0.15              0.150000       6      0.30          0.70            0.333333            0.500000                0.400000            0.213333           mixed
      tier0_tier1  conf_0.20              0.200000       2      0.10          0.90            0.000000            0.500000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.25              0.250000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.00              0.000000      14      0.70          0.30            0.500000            0.642857                0.550000            0.515556           mixed
tier0_tier1_tier2  conf_0.05              0.050000      12      0.60          0.40            0.416667            0.583333                0.433333            0.355556           mixed
tier0_tier1_tier2    trained              0.085697      10      0.50          0.50            0.400000            0.600000                0.433333            0.333333           mixed
tier0_tier1_tier2  conf_0.10              0.100000       9      0.45          0.55            0.333333            0.555556                0.333333            0.200000           mixed
tier0_tier1_tier2  conf_0.15              0.150000       7      0.35          0.65            0.428571            0.714286                0.500000            0.247619           mixed
tier0_tier1_tier2  conf_0.20              0.200000       3      0.15          0.85            0.666667            0.666667                0.500000            0.160000           mixed
tier0_tier1_tier2  conf_0.25              0.250000       1      0.05          0.95            1.000000            1.000000                1.000000            0.200000           mixed
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained             -0.068487      17      0.85          0.15            0.294118            0.647059                0.266667            0.209091           mixed
            tier0  conf_0.00              0.000000      16      0.80          0.20            0.250000            0.625000                0.250000            0.188889           mixed
            tier0  conf_0.05              0.050000      12      0.60          0.40            0.166667            0.583333                0.166667            0.133333           mixed
            tier0  conf_0.10              0.100000      12      0.60          0.40            0.166667            0.583333                0.166667            0.133333           mixed
            tier0  conf_0.15              0.150000       5      0.25          0.75            0.200000            0.600000                0.250000            0.133333           mixed
            tier0  conf_0.20              0.200000       4      0.20          0.80            0.250000            0.500000                0.333333            0.133333           mixed
            tier0  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
      tier0_tier1  conf_0.00              0.000000      14      0.70          0.30            0.071429            0.428571                0.066667            0.050000           mixed
      tier0_tier1  conf_0.05              0.050000       9      0.45          0.55            0.111111            0.444444                0.200000            0.080000           mixed
      tier0_tier1    trained              0.061167       9      0.45          0.55            0.111111            0.444444                0.200000            0.080000           mixed
      tier0_tier1  conf_0.10              0.100000       9      0.45          0.55            0.111111            0.444444                0.200000            0.080000           mixed
      tier0_tier1  conf_0.15              0.150000       9      0.45          0.55            0.111111            0.444444                0.200000            0.080000           mixed
      tier0_tier1  conf_0.20              0.200000       7      0.35          0.65            0.142857            0.571429                0.250000            0.100000           mixed
      tier0_tier1  conf_0.25              0.250000       5      0.25          0.75            0.000000            0.600000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.00              0.000000      14      0.70          0.30            0.142857            0.357143                0.150000            0.150000           mixed
tier0_tier1_tier2    trained              0.014201      13      0.65          0.35            0.153846            0.384615                0.150000            0.150000           mixed
tier0_tier1_tier2  conf_0.05              0.050000       9      0.45          0.55            0.000000            0.222222                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.10              0.100000       7      0.35          0.65            0.000000            0.285714                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.15              0.150000       6      0.30          0.70            0.000000            0.333333                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.20              0.200000       4      0.20          0.80            0.000000            0.500000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.25              0.250000       3      0.15          0.85            0.000000            0.333333                0.000000            0.000000           mixed
```

## Diagnosis Mode Comparison
- Whole-run and post-alert-window diagnosis are exported together so the diagnosis mode can be evaluated directly.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile diagnosis_target    diagnosis_mode  family_acc  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau                       status  min_class_count  min_group_count    group_key  include_workload
            tier0       20      0.40      0.60      0.400000  0.322424               0.023811                 0.018228           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.35      0.60      0.350000  0.251282               0.023807                 0.021163           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.45      0.60      0.450000  0.425641               0.021160                 0.018960           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.30      0.65      0.300000  0.276667               0.016615                 0.017499           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.10      0.35      0.100000  0.053333               0.064610                 0.034712           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.15      0.40      0.150000  0.150649               0.052217                 0.020459           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.45      0.65      0.450000  0.435556               0.011926                 0.011056           mixed     hierarchical         whole_run        0.45      0.45          0.55            0.555556            0.777778                0.450000            0.430000            0.012342              0.010159           0.011432        0.123634                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.35      0.60      0.350000  0.308283               0.010101                 0.018397           mixed     hierarchical         whole_run        0.40      0.55          0.45            0.454545            0.636364                0.466667            0.333333            0.017334              0.011810           0.011451        0.061681                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.45      0.60      0.450000  0.439394               0.010455                 0.018089           mixed     hierarchical         whole_run        0.30      0.50          0.50            0.500000            0.700000                0.500000            0.513333            0.018342              0.016915           0.011451        0.085697                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.30      0.65      0.300000  0.225758               0.004742                 0.017499           mixed     hierarchical post_alert_window        0.45      0.90          0.10            0.277778            0.666667                0.266667            0.203535            0.012342              0.010159           0.011432       -0.068487                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.15      0.45      0.150000  0.120000               0.009998                 0.011177           mixed     hierarchical post_alert_window        0.40      0.60          0.40            0.166667            0.583333                0.166667            0.133333            0.017334              0.011810           0.011451        0.061167                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.20      0.40      0.200000  0.186667              -0.001141                 0.006517           mixed     hierarchical post_alert_window        0.30      0.40          0.60            0.000000            0.125000                0.000000            0.000000            0.018342              0.016915           0.011451        0.014201                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.55      0.75      0.472222  0.398551               0.032695                 0.033616           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.50      0.70      0.444444  0.356745               0.027100                 0.031473           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.45      0.75      0.527778  0.444042               0.026839                 0.028020           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.723017         0.128796     0.148187              tier0           mixed
  BRANCH     0.775531         0.085774     0.138694              tier0           mixed
   CACHE     0.551264         0.346847     0.101889              tier0           mixed
   MEMBW     0.791023         0.093060     0.115917              tier0           mixed
     TLB     0.719920         0.130665     0.149415              tier0           mixed
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC               memory_io       0.263212         0.415215             0.076794                 0.210069                 0.034710           mixed
  BRANCH               memory_io       0.241431         0.475588             0.047408                 0.191360                 0.044214           mixed
   CACHE               memory_io       0.458535         0.292201             0.062231                 0.140374                 0.046658           mixed
   MEMBW               memory_io       0.224762         0.501137             0.053835                 0.163923                 0.056343           mixed
     TLB               memory_io       0.295093         0.414425             0.068664                 0.192482                 0.029335           mixed
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
            tier0                    0.0                             0.0                           0.0                 0.30                     74.5                 715.5                 0.2                 0.2                0.20           mixed
      tier0_tier1                    0.0                             0.0                           0.0                 0.45                     62.0                 710.8                 0.3                 0.3                0.35           mixed
tier0_tier1_tier2                    0.0                             0.0                           0.0                 0.45                     62.0                 586.4                 0.3                 0.3                0.40           mixed
```

## Files
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B60_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B60_a0.05_k3/config_runtime_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B60_a0.05_k3/run_context.json`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B60_a0.05_k3/case_inventory.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B60_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B60_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B60_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B60_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B60_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B60_a0.05_k3/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B60_a0.05_k3/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B60_a0.05_k3/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B60_a0.05_k3/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B60_a0.05_k3/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B60_a0.05_k3/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B60_a0.05_k3/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B60_a0.05_k3/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B60_a0.05_k3/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B60_a0.05_k3/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B60_a0.05_k3/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B60_a0.05_k3/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B60_a0.05_k3/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B60_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B60_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B60_a0.05_k3/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B60_a0.05_k3/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B60_a0.05_k3/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B60_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B60_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B60_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B60_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B60_a0.05_k3/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B60_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B60_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B60_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B60_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B60_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B60_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B60_a0.05_k3/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B60_a0.05_k3/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B60_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B60_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B60_a0.05_k3/figures/fig_detection_latency.png`
