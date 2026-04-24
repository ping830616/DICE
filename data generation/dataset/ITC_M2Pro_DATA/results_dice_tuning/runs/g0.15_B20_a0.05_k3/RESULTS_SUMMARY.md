# DICE Full Retrain Results

## Setup
- Feature profile: mixed ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_core_5hz.csv', 'tier2': 'tier2_core_5hz.csv'})
- Protocol: global, benign-only fit/calibration, block_B=20, alpha=0.05, persist_k=3, gain=0.15
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
          mixed             tier0       24          46          2.433113   0.7750 0.919734         1.0        1.0           0.25           0.35              0.012338              0.024416                      0.0                 0.013168
          mixed       tier0_tier1       24          57          2.902841   0.8125 0.949484         1.0        1.0           0.25           0.60              0.000048              0.000113                      0.0                 0.000050
          mixed tier0_tier1_tier2       24          64          3.431419   0.8500 0.962016         1.0        1.0           0.25           0.70              0.000051              0.000121                      0.0                 0.000055
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
          mixed   ATOMIC   0.7500 0.770833         1.0        1.0          0.000051          0.000091                  0.0             0.000036       1.779291      0.000040         37.067749         0.000036
          mixed   BRANCH   0.9375 0.950000         1.0        1.0          0.000051          0.000181                  0.0             0.000126       3.535604      0.000131        127.069706         0.000126
          mixed    CACHE   0.8125 0.804167         1.0        1.0          0.000051          0.000106                  0.0             0.000059       2.068950      0.000055         59.665385         0.000059
          mixed    MEMBW   0.9375 0.950000         1.0        1.0          0.000051          0.000139                  0.0             0.000075       2.706158      0.000088         76.213878         0.000075
          mixed      TLB   0.8125 0.804167         1.0        1.0          0.000051          0.000093                  0.0             0.000041       1.826548      0.000043         42.176918         0.000041
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
            tier0       20      0.30      0.50          0.30  0.232900               0.027057                 0.021266           mixed
      tier0_tier1       20      0.30      0.65          0.30  0.279365               0.016818                 0.011249           mixed
tier0_tier1_tier2       20      0.45      0.75          0.45  0.475824               0.015371                 0.012125           mixed
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.20      0.55          0.20  0.190476               0.018105                 0.015524           mixed
      tier0_tier1       20      0.15      0.30          0.15  0.133333               0.100939                 0.043731           mixed
tier0_tier1_tier2       20      0.05      0.35          0.05  0.066667               0.102228                 0.017929           mixed
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.25       0.5          0.25  0.234444               0.016625                 0.012293           mixed
      tier0_tier1       20      0.25       0.6          0.25  0.263333               0.015969                 0.012711           mixed
tier0_tier1_tier2       20      0.25       0.6          0.25  0.222727               0.014014                 0.010177           mixed
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.60      0.85      0.500000  0.416667               0.033374                 0.036584           mixed
      tier0_tier1       20      0.50      0.75      0.444444  0.356745               0.023727                 0.028466           mixed
tier0_tier1_tier2       20      0.55      0.70      0.527778  0.487179               0.024254                 0.024585           mixed
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.40      0.55        0.45          0.40  0.331313      0.55          0.45            0.454545            0.545455                0.400000            0.280000               0.002982                 0.011714            0.016072              0.018454           0.013413        0.097723           mixed
      tier0_tier1       20      0.35      0.65        0.35          0.35  0.309091      0.65          0.35            0.384615            0.615385                0.366667            0.348889              -0.000707                 0.001152            0.025729              0.025581           0.013925        0.007204           mixed
tier0_tier1_tier2       20      0.30      0.75        0.35          0.30  0.280519      0.45          0.55            0.444444            0.888889                0.500000            0.360000               0.001328                 0.005038            0.024669              0.022873           0.012618        0.087108           mixed
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.40      0.65        0.45          0.40  0.396032       0.6           0.4            0.333333            0.583333                0.266667            0.237143              -0.013357                 0.006452            0.016072              0.018454           0.013413       -0.040325           mixed
      tier0_tier1       20      0.30      0.35        0.35          0.30  0.201399       0.7           0.3            0.357143            0.428571                0.283333            0.233333              -0.059706                -0.020758            0.025729              0.025581           0.013925       -0.200232           mixed
tier0_tier1_tier2       20      0.15      0.25        0.35          0.15  0.106667       0.6           0.4            0.083333            0.250000                0.066667            0.050000               0.021494                 0.001140            0.024669              0.022873           0.012618       -0.010199           mixed
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0  conf_0.00              0.000000      13      0.65          0.35            0.384615            0.461538                0.350000            0.269091           mixed
            tier0  conf_0.05              0.050000      11      0.55          0.45            0.454545            0.545455                0.400000            0.280000           mixed
            tier0    trained              0.097723       8      0.40          0.60            0.500000            0.500000                0.400000            0.274286           mixed
            tier0  conf_0.10              0.100000       8      0.40          0.60            0.500000            0.500000                0.400000            0.274286           mixed
            tier0  conf_0.15              0.150000       6      0.30          0.70            0.500000            0.500000                0.400000            0.260000           mixed
            tier0  conf_0.20              0.200000       4      0.20          0.80            0.500000            0.500000                0.333333            0.160000           mixed
            tier0  conf_0.25              0.250000       3      0.15          0.85            0.666667            0.666667                0.500000            0.200000           mixed
      tier0_tier1  conf_0.00              0.000000      13      0.65          0.35            0.307692            0.615385                0.316667            0.283810           mixed
      tier0_tier1    trained              0.007204      12      0.60          0.40            0.333333            0.583333                0.333333            0.317143           mixed
      tier0_tier1  conf_0.05              0.050000       5      0.25          0.75            0.200000            0.600000                0.333333            0.066667           mixed
      tier0_tier1  conf_0.10              0.100000       5      0.25          0.75            0.200000            0.600000                0.333333            0.066667           mixed
      tier0_tier1  conf_0.15              0.150000       5      0.25          0.75            0.200000            0.600000                0.333333            0.066667           mixed
      tier0_tier1  conf_0.20              0.200000       1      0.05          0.95            1.000000            1.000000                1.000000            0.200000           mixed
      tier0_tier1  conf_0.25              0.250000       1      0.05          0.95            1.000000            1.000000                1.000000            0.200000           mixed
tier0_tier1_tier2  conf_0.00              0.000000      14      0.70          0.30            0.357143            0.714286                0.300000            0.305397           mixed
tier0_tier1_tier2  conf_0.05              0.050000       8      0.40          0.60            0.250000            0.750000                0.300000            0.257143           mixed
tier0_tier1_tier2    trained              0.087108       5      0.25          0.75            0.400000            0.600000                0.500000            0.280000           mixed
tier0_tier1_tier2  conf_0.10              0.100000       4      0.20          0.80            0.250000            0.500000                0.333333            0.080000           mixed
tier0_tier1_tier2  conf_0.15              0.150000       1      0.05          0.95            1.000000            1.000000                1.000000            0.200000           mixed
tier0_tier1_tier2  conf_0.20              0.200000       1      0.05          0.95            1.000000            1.000000                1.000000            0.200000           mixed
tier0_tier1_tier2  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained             -0.040325      13      0.65          0.35            0.307692            0.615385                0.233333            0.223810           mixed
            tier0  conf_0.00              0.000000      13      0.65          0.35            0.307692            0.615385                0.233333            0.223810           mixed
            tier0  conf_0.05              0.050000       9      0.45          0.55            0.444444            0.555556                0.400000            0.313333           mixed
            tier0  conf_0.10              0.100000       5      0.25          0.75            0.400000            0.400000                0.222222            0.160000           mixed
            tier0  conf_0.15              0.150000       3      0.15          0.85            0.666667            0.666667                0.500000            0.200000           mixed
            tier0  conf_0.20              0.200000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
            tier0  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
      tier0_tier1    trained             -0.200232      15      0.75          0.25            0.400000            0.466667                0.300000            0.253333           mixed
      tier0_tier1  conf_0.00              0.000000       9      0.45          0.55            0.222222            0.222222                0.375000            0.213333           mixed
      tier0_tier1  conf_0.05              0.050000       6      0.30          0.70            0.000000            0.000000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.10              0.100000       4      0.20          0.80            0.000000            0.000000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.15              0.150000       4      0.20          0.80            0.000000            0.000000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.20              0.200000       3      0.15          0.85            0.000000            0.000000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.25              0.250000       3      0.15          0.85            0.000000            0.000000                0.000000            0.000000           mixed
tier0_tier1_tier2    trained             -0.010199      12      0.60          0.40            0.000000            0.166667                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.00              0.000000      12      0.60          0.40            0.000000            0.166667                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.05              0.050000       9      0.45          0.55            0.000000            0.111111                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.10              0.100000       5      0.25          0.75            0.000000            0.200000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.15              0.150000       5      0.25          0.75            0.000000            0.200000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.20              0.200000       5      0.25          0.75            0.000000            0.200000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.25              0.250000       4      0.20          0.80            0.000000            0.250000                0.000000            0.000000           mixed
```

## Diagnosis Mode Comparison
- Whole-run and post-alert-window diagnosis are exported together so the diagnosis mode can be evaluated directly.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile diagnosis_target    diagnosis_mode  family_acc  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau                       status  min_class_count  min_group_count    group_key  include_workload
            tier0       20      0.30      0.50      0.300000  0.232900               0.027057                 0.021266           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.30      0.65      0.300000  0.279365               0.016818                 0.011249           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.45      0.75      0.450000  0.475824               0.015371                 0.012125           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.20      0.55      0.200000  0.190476               0.018105                 0.015524           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.15      0.30      0.150000  0.133333               0.100939                 0.043731           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.05      0.35      0.050000  0.066667               0.102228                 0.017929           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.40      0.55      0.400000  0.331313               0.002982                 0.011714           mixed     hierarchical         whole_run        0.45      0.55          0.45            0.454545            0.545455                0.400000            0.280000            0.016072              0.018454           0.013413        0.097723                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.35      0.65      0.350000  0.309091              -0.000707                 0.001152           mixed     hierarchical         whole_run        0.35      0.65          0.35            0.384615            0.615385                0.366667            0.348889            0.025729              0.025581           0.013925        0.007204                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.30      0.75      0.300000  0.280519               0.001328                 0.005038           mixed     hierarchical         whole_run        0.35      0.45          0.55            0.444444            0.888889                0.500000            0.360000            0.024669              0.022873           0.012618        0.087108                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.40      0.65      0.400000  0.396032              -0.013357                 0.006452           mixed     hierarchical post_alert_window        0.45      0.60          0.40            0.333333            0.583333                0.266667            0.237143            0.016072              0.018454           0.013413       -0.040325                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.30      0.35      0.300000  0.201399              -0.059706                -0.020758           mixed     hierarchical post_alert_window        0.35      0.70          0.30            0.357143            0.428571                0.283333            0.233333            0.025729              0.025581           0.013925       -0.200232                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.15      0.25      0.150000  0.106667               0.021494                 0.001140           mixed     hierarchical post_alert_window        0.35      0.60          0.40            0.083333            0.250000                0.066667            0.050000            0.024669              0.022873           0.012618       -0.010199                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.60      0.85      0.500000  0.416667               0.033374                 0.036584           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.50      0.75      0.444444  0.356745               0.023727                 0.028466           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.55      0.70      0.527778  0.487179               0.024254                 0.024585           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.677830         0.163204     0.158966              tier0           mixed
  BRANCH     0.745700         0.094817     0.159483              tier0           mixed
   CACHE     0.526981         0.360076     0.112943              tier0           mixed
   MEMBW     0.762546         0.101186     0.136267              tier0           mixed
     TLB     0.677032         0.153564     0.169403              tier0           mixed
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC               memory_io       0.267843         0.381478             0.106770                 0.214114                 0.029795           mixed
  BRANCH               memory_io       0.252408         0.440354             0.055420                 0.209842                 0.041977           mixed
   CACHE               memory_io       0.476437         0.255028             0.075713                 0.146282                 0.046539           mixed
   MEMBW               memory_io       0.244223         0.454151             0.062631                 0.183589                 0.055405           mixed
     TLB               memory_io       0.307750         0.369922             0.089371                 0.206468                 0.026488           mixed
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
            tier0                   0.25                        2.755102                      4.591837                 0.35                     42.0                 378.4                0.30                0.30                0.30           mixed
      tier0_tier1                   0.25                        2.755102                      4.591837                 0.60                     57.0                 784.1                0.40                0.40                0.50           mixed
tier0_tier1_tier2                   0.25                        2.755102                      4.591837                 0.70                     36.0                 886.0                0.45                0.45                0.55           mixed
```

## Files
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B20_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B20_a0.05_k3/config_runtime_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B20_a0.05_k3/run_context.json`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B20_a0.05_k3/case_inventory.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B20_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B20_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B20_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B20_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B20_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B20_a0.05_k3/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B20_a0.05_k3/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B20_a0.05_k3/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B20_a0.05_k3/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B20_a0.05_k3/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B20_a0.05_k3/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B20_a0.05_k3/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B20_a0.05_k3/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B20_a0.05_k3/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B20_a0.05_k3/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B20_a0.05_k3/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B20_a0.05_k3/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B20_a0.05_k3/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B20_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B20_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B20_a0.05_k3/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B20_a0.05_k3/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B20_a0.05_k3/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B20_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B20_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B20_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B20_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B20_a0.05_k3/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B20_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B20_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B20_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B20_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B20_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B20_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B20_a0.05_k3/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B20_a0.05_k3/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B20_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B20_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B20_a0.05_k3/figures/fig_detection_latency.png`
