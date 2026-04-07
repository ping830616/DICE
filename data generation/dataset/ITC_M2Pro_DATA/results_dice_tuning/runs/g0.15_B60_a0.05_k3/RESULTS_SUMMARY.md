# DICE Full Retrain Results

## Setup
- Feature profile: mixed ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_core_5hz.csv', 'tier2': 'tier2_core_5hz.csv'})
- Protocol: global, benign-only fit/calibration, block_B=60, alpha=0.05, persist_k=3, gain=0.15
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
          mixed             tier0       24          46          2.266811    0.800 0.931899         1.0        1.0            0.0           0.30              0.010299              0.022580                      0.0                 0.012186
          mixed       tier0_tier1       24          57          2.747028    0.825 0.951460         1.0        1.0            0.0           0.45              0.000041              0.000103                      0.0                 0.000053
          mixed tier0_tier1_tier2       24          64          3.187577    0.850 0.959180         1.0        1.0            0.0           0.45              0.000044              0.000110                      0.0                 0.000060
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
          mixed   ATOMIC   0.8125 0.804167         1.0        1.0          0.000044          0.000095                  0.0             0.000051       2.154426      0.000052         52.178094         0.000051
          mixed   BRANCH   0.9375 0.950000         1.0        1.0          0.000044          0.000161                  0.0             0.000116       3.619867      0.000117        116.846772         0.000116
          mixed    CACHE   0.8125 0.804167         1.0        1.0          0.000044          0.000096                  0.0             0.000055       2.159280      0.000052         55.710210         0.000055
          mixed    MEMBW   0.9375 0.950000         1.0        1.0          0.000044          0.000159                  0.0             0.000094       3.581621      0.000116         94.729133         0.000094
          mixed      TLB   0.7500 0.679167         1.0        1.0          0.000044          0.000106                  0.0             0.000056       2.390205      0.000062         56.806176         0.000056
```

## Paper-style Aggregates (Final Config)
- Base score mean stressor AUC-PR (all five): **0.8375**
- Base score mean stressor ROC-AUC (all five): **0.8500**
- WC score mean stressor AUC-PR (all five): **1.0000**
- WC score mean stressor ROC-AUC (all five): **1.0000**
- Base score mean stressor AUC-PR (excluding BRANCH/TLB): **0.8528**
- Base score mean stressor ROC-AUC (excluding BRANCH/TLB): **0.8542**
- WC score mean stressor AUC-PR (excluding BRANCH/TLB): **1.0000**
- WC score mean stressor ROC-AUC (excluding BRANCH/TLB): **1.0000**

## Diagnosis
- Feature-level diagnosis uses normalized whole-run residual-attribution prototypes as the default paper-facing result, with diagnosis-only filtering that removes monotonic counters and downweights generic memory-state features.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.30      0.55          0.30  0.225758               0.026869                 0.023006           mixed
      tier0_tier1       20      0.35      0.65          0.35  0.309524               0.017794                 0.017452           mixed
tier0_tier1_tier2       20      0.40      0.75          0.40  0.378999               0.015343                 0.012814           mixed
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.20      0.55          0.20  0.166364               0.019715                 0.014081           mixed
      tier0_tier1       20      0.15      0.30          0.15  0.141538               0.062771                 0.020596           mixed
tier0_tier1_tier2       20      0.15      0.40          0.15  0.157143               0.057796                 0.027301           mixed
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.20      0.55          0.20  0.190649               0.018712                 0.016208           mixed
      tier0_tier1       20      0.35      0.60          0.35  0.353333               0.017907                 0.013428           mixed
tier0_tier1_tier2       20      0.35      0.65          0.35  0.324156               0.014915                 0.014547           mixed
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.60      0.90      0.500000  0.421818               0.035774                 0.038853           mixed
      tier0_tier1       20      0.45      0.75      0.416667  0.335664               0.025453                 0.030454           mixed
tier0_tier1_tier2       20      0.50      0.70      0.500000  0.449084               0.024829                 0.026092           mixed
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.40      0.55        0.50          0.40  0.312727      0.45          0.55            0.555556            0.555556                0.400000            0.310000              -0.010502                -0.001984            0.017201              0.015886           0.011313        0.028038           mixed
      tier0_tier1       20      0.25      0.60        0.35          0.25  0.206061      0.45          0.55            0.444444            0.555556                0.400000            0.346667              -0.001127                 0.003586            0.024254              0.023740           0.009276        0.048054           mixed
tier0_tier1_tier2       20      0.35      0.75        0.35          0.35  0.318095      0.55          0.45            0.454545            0.818182                0.433333            0.354286               0.002591                 0.002275            0.020387              0.019075           0.016771        0.057087           mixed
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.40       0.6        0.50          0.40  0.368759      0.55          0.45            0.363636            0.545455                0.266667            0.238095              -0.022902                 0.005134            0.017201              0.015886           0.011313       -0.061609           mixed
      tier0_tier1       20      0.30       0.4        0.35          0.30  0.200000      0.60          0.40            0.416667            0.500000                0.333333            0.271429              -0.041036                -0.018499            0.024254              0.023740           0.009276       -0.122082           mixed
tier0_tier1_tier2       20      0.15       0.4        0.35          0.15  0.120000      0.65          0.35            0.076923            0.307692                0.066667            0.057143              -0.001303                 0.010297            0.020387              0.019075           0.016771       -0.037293           mixed
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0  conf_0.00              0.000000      10      0.50          0.50            0.500000            0.600000                0.400000            0.293333           mixed
            tier0    trained              0.028038      10      0.50          0.50            0.500000            0.600000                0.400000            0.293333           mixed
            tier0  conf_0.05              0.050000       8      0.40          0.60            0.500000            0.500000                0.400000            0.293333           mixed
            tier0  conf_0.10              0.100000       5      0.25          0.75            0.600000            0.600000                0.500000            0.293333           mixed
            tier0  conf_0.15              0.150000       5      0.25          0.75            0.600000            0.600000                0.500000            0.293333           mixed
            tier0  conf_0.20              0.200000       3      0.15          0.85            0.666667            0.666667                0.500000            0.160000           mixed
            tier0  conf_0.25              0.250000       2      0.10          0.90            1.000000            1.000000                1.000000            0.200000           mixed
      tier0_tier1  conf_0.00              0.000000      13      0.65          0.35            0.307692            0.615385                0.266667            0.248889           mixed
      tier0_tier1    trained              0.048054       8      0.40          0.60            0.250000            0.625000                0.266667            0.166667           mixed
      tier0_tier1  conf_0.05              0.050000       7      0.35          0.65            0.142857            0.571429                0.200000            0.066667           mixed
      tier0_tier1  conf_0.10              0.100000       6      0.30          0.70            0.166667            0.666667                0.250000            0.066667           mixed
      tier0_tier1  conf_0.15              0.150000       3      0.15          0.85            0.333333            0.666667                0.333333            0.100000           mixed
      tier0_tier1  conf_0.20              0.200000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
      tier0_tier1  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
tier0_tier1_tier2  conf_0.00              0.000000      16      0.80          0.20            0.375000            0.750000                0.333333            0.320346           mixed
tier0_tier1_tier2  conf_0.05              0.050000       6      0.30          0.70            0.333333            0.666667                0.333333            0.100000           mixed
tier0_tier1_tier2    trained              0.057087       6      0.30          0.70            0.333333            0.666667                0.333333            0.100000           mixed
tier0_tier1_tier2  conf_0.10              0.100000       4      0.20          0.80            0.500000            0.500000                0.333333            0.133333           mixed
tier0_tier1_tier2  conf_0.15              0.150000       3      0.15          0.85            0.666667            0.666667                0.500000            0.160000           mixed
tier0_tier1_tier2  conf_0.20              0.200000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained             -0.061609      12      0.60          0.40            0.416667            0.583333                0.333333            0.304762           mixed
            tier0  conf_0.00              0.000000      11      0.55          0.45            0.363636            0.545455                0.266667            0.238095           mixed
            tier0  conf_0.05              0.050000       9      0.45          0.55            0.444444            0.666667                0.266667            0.251429           mixed
            tier0  conf_0.10              0.100000       5      0.25          0.75            0.400000            0.600000                0.444444            0.233333           mixed
            tier0  conf_0.15              0.150000       3      0.15          0.85            0.333333            0.666667                0.500000            0.200000           mixed
            tier0  conf_0.20              0.200000       3      0.15          0.85            0.333333            0.666667                0.500000            0.200000           mixed
            tier0  conf_0.25              0.250000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000           mixed
      tier0_tier1    trained             -0.122082      11      0.55          0.45            0.363636            0.454545                0.333333            0.266667           mixed
      tier0_tier1  conf_0.00              0.000000       9      0.45          0.55            0.222222            0.333333                0.300000            0.200000           mixed
      tier0_tier1  conf_0.05              0.050000       5      0.25          0.75            0.000000            0.200000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.10              0.100000       5      0.25          0.75            0.000000            0.200000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.15              0.150000       4      0.20          0.80            0.000000            0.250000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.20              0.200000       3      0.15          0.85            0.000000            0.333333                0.000000            0.000000           mixed
      tier0_tier1  conf_0.25              0.250000       3      0.15          0.85            0.000000            0.333333                0.000000            0.000000           mixed
tier0_tier1_tier2    trained             -0.037293      14      0.70          0.30            0.071429            0.357143                0.066667            0.066667           mixed
tier0_tier1_tier2  conf_0.00              0.000000      13      0.65          0.35            0.076923            0.307692                0.066667            0.080000           mixed
tier0_tier1_tier2  conf_0.05              0.050000      10      0.50          0.50            0.100000            0.300000                0.100000            0.100000           mixed
tier0_tier1_tier2  conf_0.10              0.100000       8      0.40          0.60            0.000000            0.250000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.15              0.150000       5      0.25          0.75            0.000000            0.200000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.20              0.200000       5      0.25          0.75            0.000000            0.200000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.25              0.250000       4      0.20          0.80            0.000000            0.250000                0.000000            0.000000           mixed
```

## Diagnosis Mode Comparison
- Whole-run and post-alert-window diagnosis are exported together so the diagnosis mode can be evaluated directly.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile diagnosis_target    diagnosis_mode  family_acc  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau                       status  min_class_count  min_group_count    group_key  include_workload
            tier0       20      0.30      0.55      0.300000  0.225758               0.026869                 0.023006           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.35      0.65      0.350000  0.309524               0.017794                 0.017452           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.40      0.75      0.400000  0.378999               0.015343                 0.012814           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.20      0.55      0.200000  0.166364               0.019715                 0.014081           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.15      0.30      0.150000  0.141538               0.062771                 0.020596           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.15      0.40      0.150000  0.157143               0.057796                 0.027301           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.40      0.55      0.400000  0.312727              -0.010502                -0.001984           mixed     hierarchical         whole_run        0.50      0.45          0.55            0.555556            0.555556                0.400000            0.310000            0.017201              0.015886           0.011313        0.028038                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.25      0.60      0.250000  0.206061              -0.001127                 0.003586           mixed     hierarchical         whole_run        0.35      0.45          0.55            0.444444            0.555556                0.400000            0.346667            0.024254              0.023740           0.009276        0.048054                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.35      0.75      0.350000  0.318095               0.002591                 0.002275           mixed     hierarchical         whole_run        0.35      0.55          0.45            0.454545            0.818182                0.433333            0.354286            0.020387              0.019075           0.016771        0.057087                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.40      0.60      0.400000  0.368759              -0.022902                 0.005134           mixed     hierarchical post_alert_window        0.50      0.55          0.45            0.363636            0.545455                0.266667            0.238095            0.017201              0.015886           0.011313       -0.061609                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.30      0.40      0.300000  0.200000              -0.041036                -0.018499           mixed     hierarchical post_alert_window        0.35      0.60          0.40            0.416667            0.500000                0.333333            0.271429            0.024254              0.023740           0.009276       -0.122082                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.15      0.40      0.150000  0.120000              -0.001303                 0.010297           mixed     hierarchical post_alert_window        0.35      0.65          0.35            0.076923            0.307692                0.066667            0.057143            0.020387              0.019075           0.016771       -0.037293                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.60      0.90      0.500000  0.421818               0.035774                 0.038853           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.45      0.75      0.416667  0.335664               0.025453                 0.030454           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.50      0.70      0.500000  0.449084               0.024829                 0.026092           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.693366         0.158174     0.148460              tier0           mixed
  BRANCH     0.763717         0.095084     0.141199              tier0           mixed
   CACHE     0.541041         0.356159     0.102800              tier0           mixed
   MEMBW     0.783715         0.100318     0.115967              tier0           mixed
     TLB     0.701979         0.148401     0.149620              tier0           mixed
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC               memory_io       0.265385         0.400721             0.097234                 0.200798                 0.035861           mixed
  BRANCH               memory_io       0.242481         0.469563             0.052366                 0.186297                 0.049293           mixed
   CACHE                 compute       0.468559         0.275213             0.068704                 0.133349                 0.054175           mixed
   MEMBW               memory_io       0.234684         0.486830             0.057413                 0.158427                 0.062646           mixed
     TLB               memory_io       0.299416         0.406495             0.079525                 0.183427                 0.031137           mixed
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
            tier0                    0.0                             0.0                           0.0                 0.30                     75.5                 726.5                 0.2                 0.2                 0.2           mixed
      tier0_tier1                    0.0                             0.0                           0.0                 0.45                     62.0                 639.2                 0.3                 0.3                 0.4           mixed
tier0_tier1_tier2                    0.0                             0.0                           0.0                 0.45                     62.0                 544.6                 0.3                 0.3                 0.4           mixed
```

## Files
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B60_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B60_a0.05_k3/config_runtime_summary.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B60_a0.05_k3/run_context.json`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B60_a0.05_k3/case_inventory.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B60_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B60_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B60_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B60_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B60_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B60_a0.05_k3/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B60_a0.05_k3/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B60_a0.05_k3/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B60_a0.05_k3/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B60_a0.05_k3/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B60_a0.05_k3/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B60_a0.05_k3/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B60_a0.05_k3/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B60_a0.05_k3/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B60_a0.05_k3/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B60_a0.05_k3/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B60_a0.05_k3/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B60_a0.05_k3/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B60_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B60_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B60_a0.05_k3/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B60_a0.05_k3/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B60_a0.05_k3/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B60_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B60_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B60_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B60_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B60_a0.05_k3/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B60_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B60_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B60_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B60_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B60_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B60_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B60_a0.05_k3/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B60_a0.05_k3/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B60_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B60_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B60_a0.05_k3/figures/fig_detection_latency.png`
