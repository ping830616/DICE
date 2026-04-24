# DICE Full Retrain Results

## Setup
- Feature profile: mixed ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_core_5hz.csv', 'tier2': 'tier2_core_5hz.csv'})
- Protocol: global, benign-only fit/calibration, block_B=45, alpha=0.05, persist_k=3, gain=0.15
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
          mixed             tier0       24          46          2.349075   0.8125 0.940232         1.0        1.0            0.0            0.3              0.010929              0.022954                      0.0                 0.012282
          mixed       tier0_tier1       24          57          2.849838   0.8250 0.951460         1.0        1.0            0.0            0.5              0.000042              0.000104                      0.0                 0.000052
          mixed tier0_tier1_tier2       24          64          3.457698   0.8500 0.959180         1.0        1.0            0.0            0.5              0.000045              0.000111                      0.0                 0.000057
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
          mixed   ATOMIC   0.8125 0.804167         1.0        1.0          0.000045          0.000092                  0.0             0.000045       2.027414      0.000047         46.170008         0.000045
          mixed   BRANCH   0.9375 0.950000         1.0        1.0          0.000045          0.000172                  0.0             0.000122       3.748351      0.000127        123.036408         0.000122
          mixed    CACHE   0.8125 0.804167         1.0        1.0          0.000045          0.000095                  0.0             0.000054       2.087247      0.000050         54.558298         0.000054
          mixed    MEMBW   0.9375 0.950000         1.0        1.0          0.000045          0.000155                  0.0             0.000089       3.384169      0.000110         90.217479         0.000089
          mixed      TLB   0.7500 0.679167         1.0        1.0          0.000045          0.000106                  0.0             0.000053       2.330613      0.000061         54.004086         0.000053
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
            tier0       20      0.30      0.55          0.30  0.225758               0.026569                 0.022909           mixed
      tier0_tier1       20      0.30      0.70          0.30  0.274237               0.017143                 0.015706           mixed
tier0_tier1_tier2       20      0.45      0.75          0.45  0.475824               0.014505                 0.010929           mixed
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.20      0.55          0.20  0.175253               0.020091                 0.017835           mixed
      tier0_tier1       20      0.15      0.20          0.15  0.128205               0.083411                 0.071760           mixed
tier0_tier1_tier2       20      0.20      0.40          0.20  0.211429               0.066966                 0.029368           mixed
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.20      0.50          0.20  0.194286               0.018016                 0.013889           mixed
      tier0_tier1       20      0.35      0.65          0.35  0.353333               0.017744                 0.013378           mixed
tier0_tier1_tier2       20      0.30      0.65          0.30  0.288730               0.014287                 0.013966           mixed
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.60      0.90      0.500000  0.421818               0.035224                 0.037364           mixed
      tier0_tier1       20      0.45      0.75      0.416667  0.335664               0.024316                 0.029191           mixed
tier0_tier1_tier2       20      0.55      0.70      0.527778  0.487179               0.024171                 0.025280           mixed
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.40      0.55        0.50          0.40  0.312727      0.50          0.50            0.500000            0.600000                     0.4            0.293333              -0.009360                -0.001788            0.017103              0.016506           0.011352        0.021724           mixed
      tier0_tier1       20      0.25      0.65        0.35          0.25  0.206061      0.50          0.50            0.400000            0.600000                     0.4            0.327619              -0.000657                 0.004302            0.024465              0.025853           0.011733        0.049486           mixed
tier0_tier1_tier2       20      0.30      0.75        0.35          0.30  0.280519      0.45          0.55            0.444444            0.888889                     0.5            0.360000              -0.000567                 0.003262            0.020789              0.017725           0.014803        0.069079           mixed
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.40      0.60        0.50          0.40  0.368759      0.55          0.45            0.363636            0.545455                0.266667            0.238095              -0.019904                 0.003563            0.017103              0.016506           0.011352       -0.088413           mixed
      tier0_tier1       20      0.30      0.35        0.35          0.30  0.200000      0.65          0.35            0.384615            0.384615                0.333333            0.264286              -0.060214                -0.017029            0.024465              0.025853           0.011733       -0.116448           mixed
tier0_tier1_tier2       20      0.15      0.40        0.35          0.15  0.109091      0.60          0.40            0.083333            0.333333                0.066667            0.057143               0.000948                 0.011229            0.020789              0.017725           0.014803       -0.079244           mixed
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0  conf_0.00              0.000000      10      0.50          0.50            0.500000            0.600000                0.400000            0.293333           mixed
            tier0    trained              0.021724      10      0.50          0.50            0.500000            0.600000                0.400000            0.293333           mixed
            tier0  conf_0.05              0.050000       9      0.45          0.55            0.555556            0.555556                0.400000            0.310000           mixed
            tier0  conf_0.10              0.100000       5      0.25          0.75            0.600000            0.600000                0.500000            0.293333           mixed
            tier0  conf_0.15              0.150000       5      0.25          0.75            0.600000            0.600000                0.500000            0.293333           mixed
            tier0  conf_0.20              0.200000       3      0.15          0.85            0.666667            0.666667                0.500000            0.160000           mixed
            tier0  conf_0.25              0.250000       2      0.10          0.90            1.000000            1.000000                1.000000            0.200000           mixed
      tier0_tier1  conf_0.00              0.000000      13      0.65          0.35            0.307692            0.692308                0.266667            0.248889           mixed
      tier0_tier1    trained              0.049486       8      0.40          0.60            0.250000            0.750000                0.266667            0.166667           mixed
      tier0_tier1  conf_0.05              0.050000       8      0.40          0.60            0.250000            0.750000                0.266667            0.166667           mixed
      tier0_tier1  conf_0.10              0.100000       5      0.25          0.75            0.200000            0.600000                0.333333            0.066667           mixed
      tier0_tier1  conf_0.15              0.150000       4      0.20          0.80            0.250000            0.500000                0.333333            0.080000           mixed
      tier0_tier1  conf_0.20              0.200000       1      0.05          0.95            1.000000            1.000000                1.000000            0.200000           mixed
      tier0_tier1  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
tier0_tier1_tier2  conf_0.00              0.000000      14      0.70          0.30            0.357143            0.714286                0.300000            0.305397           mixed
tier0_tier1_tier2  conf_0.05              0.050000       5      0.25          0.75            0.200000            0.600000                0.333333            0.066667           mixed
tier0_tier1_tier2    trained              0.069079       4      0.20          0.80            0.250000            0.500000                0.333333            0.080000           mixed
tier0_tier1_tier2  conf_0.10              0.100000       4      0.20          0.80            0.250000            0.500000                0.333333            0.080000           mixed
tier0_tier1_tier2  conf_0.15              0.150000       2      0.10          0.90            0.500000            0.500000                0.500000            0.133333           mixed
tier0_tier1_tier2  conf_0.20              0.200000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
tier0_tier1_tier2  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained             -0.088413      12      0.60          0.40            0.416667            0.583333                0.333333            0.304762           mixed
            tier0  conf_0.00              0.000000      11      0.55          0.45            0.363636            0.545455                0.266667            0.238095           mixed
            tier0  conf_0.05              0.050000       8      0.40          0.60            0.500000            0.750000                0.333333            0.271429           mixed
            tier0  conf_0.10              0.100000       7      0.35          0.65            0.428571            0.714286                0.333333            0.260000           mixed
            tier0  conf_0.15              0.150000       3      0.15          0.85            0.333333            0.666667                0.500000            0.200000           mixed
            tier0  conf_0.20              0.200000       2      0.10          0.90            0.000000            0.500000                0.000000            0.000000           mixed
            tier0  conf_0.25              0.250000       2      0.10          0.90            0.000000            0.500000                0.000000            0.000000           mixed
      tier0_tier1    trained             -0.116448      11      0.55          0.45            0.454545            0.454545                0.416667            0.310000           mixed
      tier0_tier1  conf_0.00              0.000000       8      0.40          0.60            0.250000            0.250000                0.375000            0.233333           mixed
      tier0_tier1  conf_0.05              0.050000       6      0.30          0.70            0.166667            0.166667                0.166667            0.133333           mixed
      tier0_tier1  conf_0.10              0.100000       3      0.15          0.85            0.000000            0.000000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.15              0.150000       3      0.15          0.85            0.000000            0.000000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.20              0.200000       2      0.10          0.90            0.000000            0.000000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.25              0.250000       2      0.10          0.90            0.000000            0.000000                0.000000            0.000000           mixed
tier0_tier1_tier2    trained             -0.079244      14      0.70          0.30            0.142857            0.357143                0.133333            0.116667           mixed
tier0_tier1_tier2  conf_0.00              0.000000      12      0.60          0.40            0.083333            0.250000                0.066667            0.080000           mixed
tier0_tier1_tier2  conf_0.05              0.050000       9      0.45          0.55            0.000000            0.222222                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.10              0.100000       8      0.40          0.60            0.000000            0.250000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.15              0.150000       5      0.25          0.75            0.000000            0.200000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.20              0.200000       5      0.25          0.75            0.000000            0.200000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.25              0.250000       5      0.25          0.75            0.000000            0.200000                0.000000            0.000000           mixed
```

## Diagnosis Mode Comparison
- Whole-run and post-alert-window diagnosis are exported together so the diagnosis mode can be evaluated directly.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile diagnosis_target    diagnosis_mode  family_acc  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau                       status  min_class_count  min_group_count    group_key  include_workload
            tier0       20      0.30      0.55      0.300000  0.225758               0.026569                 0.022909           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.30      0.70      0.300000  0.274237               0.017143                 0.015706           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.45      0.75      0.450000  0.475824               0.014505                 0.010929           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.20      0.55      0.200000  0.175253               0.020091                 0.017835           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.15      0.20      0.150000  0.128205               0.083411                 0.071760           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.20      0.40      0.200000  0.211429               0.066966                 0.029368           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.40      0.55      0.400000  0.312727              -0.009360                -0.001788           mixed     hierarchical         whole_run        0.50      0.50          0.50            0.500000            0.600000                0.400000            0.293333            0.017103              0.016506           0.011352        0.021724                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.25      0.65      0.250000  0.206061              -0.000657                 0.004302           mixed     hierarchical         whole_run        0.35      0.50          0.50            0.400000            0.600000                0.400000            0.327619            0.024465              0.025853           0.011733        0.049486                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.30      0.75      0.300000  0.280519              -0.000567                 0.003262           mixed     hierarchical         whole_run        0.35      0.45          0.55            0.444444            0.888889                0.500000            0.360000            0.020789              0.017725           0.014803        0.069079                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.40      0.60      0.400000  0.368759              -0.019904                 0.003563           mixed     hierarchical post_alert_window        0.50      0.55          0.45            0.363636            0.545455                0.266667            0.238095            0.017103              0.016506           0.011352       -0.088413                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.30      0.35      0.300000  0.200000              -0.060214                -0.017029           mixed     hierarchical post_alert_window        0.35      0.65          0.35            0.384615            0.384615                0.333333            0.264286            0.024465              0.025853           0.011733       -0.116448                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.15      0.40      0.150000  0.109091               0.000948                 0.011229           mixed     hierarchical post_alert_window        0.35      0.60          0.40            0.083333            0.333333                0.066667            0.057143            0.020789              0.017725           0.014803       -0.079244                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.60      0.90      0.500000  0.421818               0.035224                 0.037364           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.45      0.75      0.416667  0.335664               0.024316                 0.029191           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.55      0.70      0.527778  0.487179               0.024171                 0.025280           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.689690         0.158264     0.152045              tier0           mixed
  BRANCH     0.759371         0.094077     0.146552              tier0           mixed
   CACHE     0.537208         0.356859     0.105932              tier0           mixed
   MEMBW     0.779376         0.099046     0.121578              tier0           mixed
     TLB     0.696238         0.148412     0.155350              tier0           mixed
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC               memory_io       0.266260         0.395308             0.099660                 0.205222                 0.033551           mixed
  BRANCH               memory_io       0.245510         0.461225             0.052999                 0.192737                 0.047530           mixed
   CACHE                 compute       0.471229         0.268649             0.070798                 0.137319                 0.052006           mixed
   MEMBW               memory_io       0.237365         0.478002             0.058435                 0.165499                 0.060700           mixed
     TLB               memory_io       0.301890         0.396403             0.081951                 0.189977                 0.029779           mixed
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
            tier0                    0.0                             0.0                           0.0                  0.3                     64.5                 625.5                 0.2                 0.2                0.25           mixed
      tier0_tier1                    0.0                             0.0                           0.0                  0.5                     65.0                 849.0                 0.3                 0.3                0.40           mixed
tier0_tier1_tier2                    0.0                             0.0                           0.0                  0.5                     64.0                 835.6                 0.3                 0.3                0.40           mixed
```

## Files
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B45_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B45_a0.05_k3/config_runtime_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B45_a0.05_k3/run_context.json`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B45_a0.05_k3/case_inventory.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B45_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B45_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B45_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B45_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B45_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B45_a0.05_k3/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B45_a0.05_k3/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B45_a0.05_k3/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B45_a0.05_k3/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B45_a0.05_k3/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B45_a0.05_k3/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B45_a0.05_k3/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B45_a0.05_k3/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B45_a0.05_k3/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B45_a0.05_k3/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B45_a0.05_k3/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B45_a0.05_k3/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B45_a0.05_k3/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B45_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B45_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B45_a0.05_k3/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B45_a0.05_k3/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B45_a0.05_k3/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B45_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B45_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B45_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B45_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B45_a0.05_k3/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B45_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B45_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B45_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B45_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B45_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B45_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B45_a0.05_k3/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B45_a0.05_k3/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B45_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B45_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B45_a0.05_k3/figures/fig_detection_latency.png`
