# DICE Full Retrain Results

## Setup
- Feature profile: mixed ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_core_5hz.csv', 'tier2': 'tier2_core_5hz.csv'})
- Protocol: global, benign-only fit/calibration, block_B=90, alpha=0.05, persist_k=3, gain=0.15
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
          mixed             tier0       24          46          2.201504   0.7875 0.921899         1.0        1.0            0.0           0.30              0.009117              0.020492                      0.0                 0.011347
          mixed       tier0_tier1       24          57          2.683591   0.8250 0.947375         1.0        1.0            0.0           0.45              0.000043              0.000107                      0.0                 0.000057
          mixed tier0_tier1_tier2       24          64          2.934076   0.8125 0.940232         1.0        1.0            0.0           0.45              0.000047              0.000117                      0.0                 0.000058
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
          mixed   ATOMIC   0.8125 0.804167         1.0        1.0          0.000047          0.000102                  0.0             0.000058       2.156760      0.000055         58.960967         0.000058
          mixed   BRANCH   0.8125 0.804167         1.0        1.0          0.000047          0.000157                  0.0             0.000112       3.321521      0.000111        113.177385         0.000112
          mixed    CACHE   0.8125 0.804167         1.0        1.0          0.000047          0.000100                  0.0             0.000056       2.119546      0.000053         57.289071         0.000056
          mixed    MEMBW   0.8750 0.887500         1.0        1.0          0.000047          0.000163                  0.0             0.000095       3.451340      0.000117         96.037647         0.000095
          mixed      TLB   0.7500 0.679167         1.0        1.0          0.000047          0.000105                  0.0             0.000055       2.218528      0.000058         55.520292         0.000055
```

## Paper-style Aggregates (Final Config)
- Base score mean stressor AUC-PR (all five): **0.7958**
- Base score mean stressor ROC-AUC (all five): **0.8125**
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
            tier0       20       0.4      0.55           0.4  0.348485               0.027146                 0.025305           mixed
      tier0_tier1       20       0.3      0.60           0.3  0.237143               0.018104                 0.013126           mixed
tier0_tier1_tier2       20       0.4      0.75           0.4  0.352381               0.016199                 0.010500           mixed
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.20      0.55          0.20  0.169697               0.016044                 0.010919           mixed
      tier0_tier1       20      0.15      0.30          0.15  0.141538               0.045650                 0.023622           mixed
tier0_tier1_tier2       20      0.15      0.50          0.15  0.160173               0.040135                 0.023528           mixed
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.20      0.45          0.20  0.190649               0.021017                 0.019769           mixed
      tier0_tier1       20      0.25      0.55          0.25  0.243506               0.018760                 0.016653           mixed
tier0_tier1_tier2       20      0.35      0.60          0.35  0.326984               0.014370                 0.011532           mixed
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.60      0.90      0.500000  0.421818               0.036861                 0.039022           mixed
      tier0_tier1       20      0.45      0.75      0.416667  0.335664               0.026199                 0.031418           mixed
tier0_tier1_tier2       20      0.50      0.70      0.500000  0.449084               0.025506                 0.027722           mixed
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.35      0.50        0.45          0.35  0.315556      0.55          0.45            0.454545            0.454545                0.333333            0.266667              -0.005416                 0.003019            0.016424              0.018444           0.012757        0.037822           mixed
      tier0_tier1       20      0.25      0.65        0.30          0.25  0.206061      0.50          0.50            0.400000            0.700000                0.366667            0.313333              -0.001987                 0.002553            0.021708              0.021193           0.008192        0.039834           mixed
tier0_tier1_tier2       20      0.30      0.75        0.30          0.30  0.270085      0.45          0.55            0.444444            0.888889                0.500000            0.393333               0.003076                 0.002874            0.019434              0.018703           0.016579        0.112024           mixed
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.25       0.5        0.45          0.25  0.206234      0.70          0.30            0.285714            0.500000                0.266667            0.186667              -0.015539                 0.003534            0.016424              0.018444           0.012757       -0.074605           mixed
      tier0_tier1       20      0.30       0.4        0.30          0.30  0.200000      0.30          0.70            0.500000            0.666667                0.375000            0.333333              -0.038337                -0.014777            0.021708              0.021193           0.008192       -0.037247           mixed
tier0_tier1_tier2       20      0.20       0.4        0.30          0.20  0.146667      0.55          0.45            0.090909            0.363636                0.066667            0.057143              -0.003895                 0.004096            0.019434              0.018703           0.016579        0.079368           mixed
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0  conf_0.00              0.000000      12      0.60          0.40            0.500000            0.500000                0.433333            0.366667           mixed
            tier0    trained              0.037822       9      0.45          0.55            0.333333            0.333333                0.333333            0.213333           mixed
            tier0  conf_0.05              0.050000       9      0.45          0.55            0.333333            0.333333                0.333333            0.213333           mixed
            tier0  conf_0.10              0.100000       7      0.35          0.65            0.428571            0.428571                0.416667            0.233333           mixed
            tier0  conf_0.15              0.150000       6      0.30          0.70            0.500000            0.500000                0.416667            0.233333           mixed
            tier0  conf_0.20              0.200000       4      0.20          0.80            0.500000            0.500000                0.333333            0.133333           mixed
            tier0  conf_0.25              0.250000       1      0.05          0.95            1.000000            1.000000                1.000000            0.200000           mixed
      tier0_tier1  conf_0.00              0.000000      13      0.65          0.35            0.307692            0.692308                0.266667            0.248889           mixed
      tier0_tier1    trained              0.039834       9      0.45          0.55            0.333333            0.777778                0.266667            0.200000           mixed
      tier0_tier1  conf_0.05              0.050000       7      0.35          0.65            0.142857            0.714286                0.200000            0.066667           mixed
      tier0_tier1  conf_0.10              0.100000       5      0.25          0.75            0.200000            0.600000                0.250000            0.080000           mixed
      tier0_tier1  conf_0.15              0.150000       3      0.15          0.85            0.333333            0.666667                0.333333            0.100000           mixed
      tier0_tier1  conf_0.20              0.200000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
tier0_tier1_tier2  conf_0.00              0.000000      16      0.80          0.20            0.312500            0.750000                0.266667            0.246667           mixed
tier0_tier1_tier2  conf_0.05              0.050000       6      0.30          0.70            0.333333            0.666667                0.333333            0.100000           mixed
tier0_tier1_tier2  conf_0.10              0.100000       4      0.20          0.80            0.500000            0.500000                0.333333            0.133333           mixed
tier0_tier1_tier2    trained              0.112024       4      0.20          0.80            0.500000            0.500000                0.333333            0.133333           mixed
tier0_tier1_tier2  conf_0.15              0.150000       3      0.15          0.85            0.666667            0.666667                0.500000            0.160000           mixed
tier0_tier1_tier2  conf_0.20              0.200000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained             -0.074605      14      0.70          0.30            0.285714            0.500000                0.266667            0.186667           mixed
            tier0  conf_0.00              0.000000      14      0.70          0.30            0.285714            0.500000                0.266667            0.186667           mixed
            tier0  conf_0.05              0.050000       8      0.40          0.60            0.500000            0.750000                0.333333            0.251429           mixed
            tier0  conf_0.10              0.100000       6      0.30          0.70            0.666667            0.833333                0.666667            0.300000           mixed
            tier0  conf_0.15              0.150000       2      0.10          0.90            0.000000            0.500000                0.000000            0.000000           mixed
            tier0  conf_0.20              0.200000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
            tier0  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
      tier0_tier1    trained             -0.037247       9      0.45          0.55            0.222222            0.333333                0.300000            0.200000           mixed
      tier0_tier1  conf_0.00              0.000000       8      0.40          0.60            0.250000            0.375000                0.375000            0.233333           mixed
      tier0_tier1  conf_0.05              0.050000       5      0.25          0.75            0.000000            0.200000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.10              0.100000       4      0.20          0.80            0.000000            0.250000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.15              0.150000       2      0.10          0.90            0.000000            0.500000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.20              0.200000       2      0.10          0.90            0.000000            0.500000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.25              0.250000       2      0.10          0.90            0.000000            0.500000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.00              0.000000      13      0.65          0.35            0.153846            0.384615                0.133333            0.130000           mixed
tier0_tier1_tier2  conf_0.05              0.050000       9      0.45          0.55            0.000000            0.333333                0.000000            0.000000           mixed
tier0_tier1_tier2    trained              0.079368       9      0.45          0.55            0.000000            0.333333                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.10              0.100000       8      0.40          0.60            0.000000            0.250000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.15              0.150000       3      0.15          0.85            0.000000            0.000000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.20              0.200000       3      0.15          0.85            0.000000            0.000000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.25              0.250000       3      0.15          0.85            0.000000            0.000000                0.000000            0.000000           mixed
```

## Diagnosis Mode Comparison
- Whole-run and post-alert-window diagnosis are exported together so the diagnosis mode can be evaluated directly.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile diagnosis_target    diagnosis_mode  family_acc  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau                       status  min_class_count  min_group_count    group_key  include_workload
            tier0       20      0.40      0.55      0.400000  0.348485               0.027146                 0.025305           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.30      0.60      0.300000  0.237143               0.018104                 0.013126           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.40      0.75      0.400000  0.352381               0.016199                 0.010500           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.20      0.55      0.200000  0.169697               0.016044                 0.010919           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.15      0.30      0.150000  0.141538               0.045650                 0.023622           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.15      0.50      0.150000  0.160173               0.040135                 0.023528           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.35      0.50      0.350000  0.315556              -0.005416                 0.003019           mixed     hierarchical         whole_run        0.45      0.55          0.45            0.454545            0.454545                0.333333            0.266667            0.016424              0.018444           0.012757        0.037822                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.25      0.65      0.250000  0.206061              -0.001987                 0.002553           mixed     hierarchical         whole_run        0.30      0.50          0.50            0.400000            0.700000                0.366667            0.313333            0.021708              0.021193           0.008192        0.039834                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.30      0.75      0.300000  0.270085               0.003076                 0.002874           mixed     hierarchical         whole_run        0.30      0.45          0.55            0.444444            0.888889                0.500000            0.393333            0.019434              0.018703           0.016579        0.112024                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.25      0.50      0.250000  0.206234              -0.015539                 0.003534           mixed     hierarchical post_alert_window        0.45      0.70          0.30            0.285714            0.500000                0.266667            0.186667            0.016424              0.018444           0.012757       -0.074605                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.30      0.40      0.300000  0.200000              -0.038337                -0.014777           mixed     hierarchical post_alert_window        0.30      0.30          0.70            0.500000            0.666667                0.375000            0.333333            0.021708              0.021193           0.008192       -0.037247                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.20      0.40      0.200000  0.146667              -0.003895                 0.004096           mixed     hierarchical post_alert_window        0.30      0.55          0.45            0.090909            0.363636                0.066667            0.057143            0.019434              0.018703           0.016579        0.079368                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.60      0.90      0.500000  0.421818               0.036861                 0.039022           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.45      0.75      0.416667  0.335664               0.026199                 0.031418           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.50      0.70      0.500000  0.449084               0.025506                 0.027722           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.700823         0.159015     0.140162              tier0           mixed
  BRANCH     0.774192         0.093806     0.132001              tier0           mixed
   CACHE     0.548317         0.355061     0.096622              tier0           mixed
   MEMBW     0.792435         0.100577     0.106988              tier0           mixed
     TLB     0.713290         0.147445     0.139265              tier0           mixed
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC               memory_io       0.262515         0.414746             0.094082                 0.191352                 0.037305           mixed
  BRANCH               memory_io       0.236559         0.489147             0.049718                 0.174542                 0.050034           mixed
   CACHE               memory_io       0.463533         0.289281             0.066042                 0.125570                 0.055575           mixed
   MEMBW               memory_io       0.226625         0.506262             0.056017                 0.147220                 0.063876           mixed
     TLB               memory_io       0.292739         0.427923             0.075817                 0.171435                 0.032086           mixed
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
            tier0                    0.0                             0.0                           0.0                 0.30                     95.0                 729.0                 0.2                 0.2                0.20           mixed
      tier0_tier1                    0.0                             0.0                           0.0                 0.45                     92.0                 654.0                 0.3                 0.3                0.35           mixed
tier0_tier1_tier2                    0.0                             0.0                           0.0                 0.45                     92.0                 545.0                 0.3                 0.3                0.40           mixed
```

## Files
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B90_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B90_a0.05_k3/config_runtime_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B90_a0.05_k3/run_context.json`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B90_a0.05_k3/case_inventory.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B90_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B90_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B90_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B90_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B90_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B90_a0.05_k3/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B90_a0.05_k3/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B90_a0.05_k3/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B90_a0.05_k3/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B90_a0.05_k3/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B90_a0.05_k3/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B90_a0.05_k3/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B90_a0.05_k3/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B90_a0.05_k3/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B90_a0.05_k3/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B90_a0.05_k3/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B90_a0.05_k3/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B90_a0.05_k3/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B90_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B90_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B90_a0.05_k3/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B90_a0.05_k3/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B90_a0.05_k3/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B90_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B90_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B90_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B90_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B90_a0.05_k3/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B90_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B90_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B90_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B90_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B90_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B90_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B90_a0.05_k3/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B90_a0.05_k3/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B90_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B90_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B90_a0.05_k3/figures/fig_detection_latency.png`
