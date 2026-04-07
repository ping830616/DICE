# DICE Full Retrain Results

## Setup
- Feature profile: mixed ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_core_5hz.csv', 'tier2': 'tier2_core_5hz.csv'})
- Protocol: global, benign-only fit/calibration, block_B=20, alpha=0.05, persist_k=3, gain=0.2
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
          mixed             tier0       24          46          2.281377   0.7625 0.917472         1.0        1.0           0.25           0.35              0.010371              0.020111                      0.0                 0.011191
          mixed       tier0_tier1       24          57          2.855701   0.8250 0.955040         1.0        1.0           0.25           0.60              0.000050              0.000115                      0.0                 0.000049
          mixed tier0_tier1_tier2       24          64          3.201818   0.8375 0.957016         1.0        1.0           0.25           0.65              0.000053              0.000123                      0.0                 0.000057
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
          mixed   ATOMIC   0.7500 0.770833         1.0        1.0          0.000053          0.000091                  0.0             0.000039       1.719544      0.000039         39.699483         0.000039
          mixed   BRANCH   0.9375 0.950000         1.0        1.0          0.000053          0.000184                  0.0             0.000123       3.446586      0.000132        124.486304         0.000123
          mixed    CACHE   0.8125 0.804167         1.0        1.0          0.000053          0.000107                  0.0             0.000062       2.013049      0.000054         63.163822         0.000062
          mixed    MEMBW   0.8750 0.887500         1.0        1.0          0.000053          0.000140                  0.0             0.000074       2.625851      0.000087         75.482156         0.000074
          mixed      TLB   0.8125 0.804167         1.0        1.0          0.000053          0.000095                  0.0             0.000042       1.780858      0.000042         43.486688         0.000042
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
            tier0       20       0.3      0.55           0.3  0.242424               0.027180                 0.022863           mixed
      tier0_tier1       20       0.4      0.75           0.4  0.347863               0.018229                 0.011980           mixed
tier0_tier1_tier2       20       0.5      0.70           0.5  0.536508               0.017064                 0.013406           mixed
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.25      0.50          0.25  0.233333               0.015828                 0.014921           mixed
      tier0_tier1       20      0.15      0.30          0.15  0.123810               0.104447                 0.044257           mixed
tier0_tier1_tier2       20      0.10      0.35          0.10  0.114286               0.100369                 0.018417           mixed
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.25      0.60          0.25  0.217778               0.013545                 0.010480           mixed
      tier0_tier1       20      0.35      0.65          0.35  0.337143               0.012856                 0.010566           mixed
tier0_tier1_tier2       20      0.20      0.55          0.20  0.187143               0.011457                 0.008798           mixed
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.55      0.85      0.472222  0.398551               0.034527                 0.038891           mixed
      tier0_tier1       20      0.50      0.80      0.444444  0.356745               0.025474                 0.030448           mixed
tier0_tier1_tier2       20      0.55      0.75      0.527778  0.487179               0.025498                 0.025939           mixed
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.40      0.55        0.45          0.40  0.368889      0.35          0.65            0.428571            0.428571                0.333333            0.213333               0.005885                 0.013386            0.013892              0.016292           0.014967        0.117755           mixed
      tier0_tier1       20      0.35      0.70        0.40          0.35  0.309091      0.65          0.35            0.384615            0.692308                0.350000            0.335556              -0.000565                 0.000085            0.023709              0.026588           0.012959       -0.035875           mixed
tier0_tier1_tier2       20      0.35      0.70        0.35          0.35  0.306593      0.55          0.45            0.454545            0.909091                0.466667            0.426667              -0.003765                 0.001608            0.023977              0.018618           0.017578        0.061272           mixed
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20       0.4      0.55        0.45           0.4  0.396032      0.65          0.35            0.384615            0.538462                0.300000            0.271429              -0.013257                 0.004914            0.013892              0.016292           0.014967       -0.019756           mixed
      tier0_tier1       20       0.3      0.35        0.40           0.3  0.201399      0.80          0.20            0.375000            0.437500                0.300000            0.240000              -0.060834                -0.021310            0.023709              0.026588           0.012959       -0.274043           mixed
tier0_tier1_tier2       20       0.1      0.25        0.35           0.1  0.053333      0.55          0.45            0.090909            0.272727                0.066667            0.050000              -0.004988                -0.002790            0.023977              0.018618           0.017578        0.197999           mixed
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0  conf_0.00              0.000000      15      0.75          0.25            0.400000            0.533333                0.350000            0.333333           mixed
            tier0  conf_0.05              0.050000      12      0.60          0.40            0.416667            0.583333                0.366667            0.355556           mixed
            tier0  conf_0.10              0.100000       9      0.45          0.55            0.444444            0.555556                0.333333            0.233333           mixed
            tier0    trained              0.117755       8      0.40          0.60            0.500000            0.500000                0.333333            0.247619           mixed
            tier0  conf_0.15              0.150000       5      0.25          0.75            0.400000            0.400000                0.222222            0.133333           mixed
            tier0  conf_0.20              0.200000       4      0.20          0.80            0.500000            0.500000                0.333333            0.133333           mixed
            tier0  conf_0.25              0.250000       3      0.15          0.85            0.666667            0.666667                0.666667            0.160000           mixed
      tier0_tier1    trained             -0.035875      14      0.70          0.30            0.428571            0.714286                0.383333            0.368889           mixed
      tier0_tier1  conf_0.00              0.000000      12      0.60          0.40            0.416667            0.666667                0.437500            0.368889           mixed
      tier0_tier1  conf_0.05              0.050000       5      0.25          0.75            0.200000            0.600000                0.333333            0.066667           mixed
      tier0_tier1  conf_0.10              0.100000       5      0.25          0.75            0.200000            0.600000                0.333333            0.066667           mixed
      tier0_tier1  conf_0.15              0.150000       5      0.25          0.75            0.200000            0.600000                0.333333            0.066667           mixed
      tier0_tier1  conf_0.20              0.200000       4      0.20          0.80            0.250000            0.750000                0.333333            0.080000           mixed
      tier0_tier1  conf_0.25              0.250000       1      0.05          0.95            1.000000            1.000000                1.000000            0.200000           mixed
tier0_tier1_tier2  conf_0.00              0.000000      12      0.60          0.40            0.500000            0.750000                0.433333            0.426667           mixed
tier0_tier1_tier2  conf_0.05              0.050000       5      0.25          0.75            0.600000            0.800000                0.625000            0.433333           mixed
tier0_tier1_tier2    trained              0.061272       5      0.25          0.75            0.600000            0.800000                0.625000            0.433333           mixed
tier0_tier1_tier2  conf_0.10              0.100000       4      0.20          0.80            0.500000            0.750000                0.500000            0.233333           mixed
tier0_tier1_tier2  conf_0.15              0.150000       3      0.15          0.85            0.333333            0.666667                0.333333            0.100000           mixed
tier0_tier1_tier2  conf_0.20              0.200000       1      0.05          0.95            1.000000            1.000000                1.000000            0.200000           mixed
tier0_tier1_tier2  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained             -0.019756      14      0.70          0.30            0.357143            0.500000                0.300000            0.260317           mixed
            tier0  conf_0.00              0.000000      14      0.70          0.30            0.357143            0.500000                0.300000            0.260317           mixed
            tier0  conf_0.05              0.050000       9      0.45          0.55            0.444444            0.666667                0.458333            0.314286           mixed
            tier0  conf_0.10              0.100000       5      0.25          0.75            0.600000            0.600000                0.666667            0.433333           mixed
            tier0  conf_0.15              0.150000       2      0.10          0.90            0.500000            0.500000                0.500000            0.200000           mixed
            tier0  conf_0.20              0.200000       2      0.10          0.90            0.500000            0.500000                0.500000            0.200000           mixed
            tier0  conf_0.25              0.250000       1      0.05          0.95            1.000000            1.000000                1.000000            0.200000           mixed
      tier0_tier1    trained             -0.274043      16      0.80          0.20            0.375000            0.437500                0.300000            0.240000           mixed
      tier0_tier1  conf_0.00              0.000000       9      0.45          0.55            0.222222            0.222222                0.375000            0.213333           mixed
      tier0_tier1  conf_0.05              0.050000       5      0.25          0.75            0.000000            0.000000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.10              0.100000       5      0.25          0.75            0.000000            0.000000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.15              0.150000       4      0.20          0.80            0.000000            0.000000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.20              0.200000       3      0.15          0.85            0.000000            0.000000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.25              0.250000       3      0.15          0.85            0.000000            0.000000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.00              0.000000      10      0.50          0.50            0.000000            0.100000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.05              0.050000       6      0.30          0.70            0.000000            0.166667                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.10              0.100000       3      0.15          0.85            0.000000            0.333333                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.15              0.150000       3      0.15          0.85            0.000000            0.333333                0.000000            0.000000           mixed
tier0_tier1_tier2    trained              0.197999       3      0.15          0.85            0.000000            0.333333                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.20              0.200000       3      0.15          0.85            0.000000            0.333333                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.25              0.250000       3      0.15          0.85            0.000000            0.333333                0.000000            0.000000           mixed
```

## Diagnosis Mode Comparison
- Whole-run and post-alert-window diagnosis are exported together so the diagnosis mode can be evaluated directly.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile diagnosis_target    diagnosis_mode  family_acc  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau                       status  min_class_count  min_group_count    group_key  include_workload
            tier0       20      0.30      0.55      0.300000  0.242424               0.027180                 0.022863           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.40      0.75      0.400000  0.347863               0.018229                 0.011980           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.50      0.70      0.500000  0.536508               0.017064                 0.013406           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.25      0.50      0.250000  0.233333               0.015828                 0.014921           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.15      0.30      0.150000  0.123810               0.104447                 0.044257           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.10      0.35      0.100000  0.114286               0.100369                 0.018417           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.40      0.55      0.400000  0.368889               0.005885                 0.013386           mixed     hierarchical         whole_run        0.45      0.35          0.65            0.428571            0.428571                0.333333            0.213333            0.013892              0.016292           0.014967        0.117755                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.35      0.70      0.350000  0.309091              -0.000565                 0.000085           mixed     hierarchical         whole_run        0.40      0.65          0.35            0.384615            0.692308                0.350000            0.335556            0.023709              0.026588           0.012959       -0.035875                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.35      0.70      0.350000  0.306593              -0.003765                 0.001608           mixed     hierarchical         whole_run        0.35      0.55          0.45            0.454545            0.909091                0.466667            0.426667            0.023977              0.018618           0.017578        0.061272                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.40      0.55      0.400000  0.396032              -0.013257                 0.004914           mixed     hierarchical post_alert_window        0.45      0.65          0.35            0.384615            0.538462                0.300000            0.271429            0.013892              0.016292           0.014967       -0.019756                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.30      0.35      0.300000  0.201399              -0.060834                -0.021310           mixed     hierarchical post_alert_window        0.40      0.80          0.20            0.375000            0.437500                0.300000            0.240000            0.023709              0.026588           0.012959       -0.274043                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.10      0.25      0.100000  0.053333              -0.004988                -0.002790           mixed     hierarchical post_alert_window        0.35      0.55          0.45            0.090909            0.272727                0.066667            0.050000            0.023977              0.018618           0.017578        0.197999                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.55      0.85      0.472222  0.398551               0.034527                 0.038891           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.50      0.80      0.444444  0.356745               0.025474                 0.030448           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.55      0.75      0.527778  0.487179               0.025498                 0.025939           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.689232         0.152286     0.158482              tier0           mixed
  BRANCH     0.751005         0.091328     0.157667              tier0           mixed
   CACHE     0.530613         0.357157     0.112230              tier0           mixed
   MEMBW     0.765636         0.098830     0.135534              tier0           mixed
     TLB     0.683804         0.147341     0.168855              tier0           mixed
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC               memory_io       0.265342         0.389668             0.099019                 0.216490                 0.029480           mixed
  BRANCH               memory_io       0.250881         0.445887             0.053401                 0.210118                 0.039713           mixed
   CACHE               memory_io       0.472650         0.261787             0.073773                 0.147922                 0.043867           mixed
   MEMBW               memory_io       0.239564         0.462425             0.061390                 0.184065                 0.052556           mixed
     TLB               memory_io       0.306479         0.374670             0.085184                 0.208716                 0.024951           mixed
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
            tier0                   0.25                        2.755102                      4.591837                 0.35                     72.0                 550.6                0.25                0.25                0.30           mixed
      tier0_tier1                   0.25                        2.755102                      4.591837                 0.60                     57.0                 784.1                0.40                0.40                0.50           mixed
tier0_tier1_tier2                   0.25                        2.755102                      4.591837                 0.65                     30.0                 750.4                0.45                0.45                0.55           mixed
```

## Files
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B20_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B20_a0.05_k3/config_runtime_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B20_a0.05_k3/run_context.json`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B20_a0.05_k3/case_inventory.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B20_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B20_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B20_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B20_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B20_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B20_a0.05_k3/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B20_a0.05_k3/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B20_a0.05_k3/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B20_a0.05_k3/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B20_a0.05_k3/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B20_a0.05_k3/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B20_a0.05_k3/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B20_a0.05_k3/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B20_a0.05_k3/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B20_a0.05_k3/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B20_a0.05_k3/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B20_a0.05_k3/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B20_a0.05_k3/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B20_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B20_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B20_a0.05_k3/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B20_a0.05_k3/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B20_a0.05_k3/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B20_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B20_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B20_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B20_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B20_a0.05_k3/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B20_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B20_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B20_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B20_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B20_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B20_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B20_a0.05_k3/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B20_a0.05_k3/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B20_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B20_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.2_B20_a0.05_k3/figures/fig_detection_latency.png`
