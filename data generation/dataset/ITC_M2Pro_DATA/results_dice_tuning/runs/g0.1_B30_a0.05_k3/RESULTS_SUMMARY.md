# DICE Full Retrain Results

## Setup
- Feature profile: mixed ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_core_5hz.csv', 'tier2': 'tier2_core_5hz.csv'})
- Protocol: global, benign-only fit/calibration, block_B=30, alpha=0.05, persist_k=3, gain=0.1
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
          mixed             tier0       24          46          2.448532   0.8125 0.940232         1.0        1.0           0.25           0.30              0.014529              0.030374                      0.0                 0.015789
          mixed       tier0_tier1       24          57          2.908973   0.8500 0.962016         1.0        1.0           0.00           0.55              0.000043              0.000111                      0.0                 0.000048
          mixed tier0_tier1_tier2       24          64          3.245041   0.8625 0.966561         1.0        1.0           0.00           0.55              0.000045              0.000118                      0.0                 0.000054
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
          mixed   ATOMIC   0.7500 0.770833         1.0        1.0          0.000045          0.000090                  0.0             0.000037       1.979139      0.000045         37.811777         0.000037
          mixed   BRANCH   1.0000 1.000000         1.0        1.0          0.000045          0.000184                  0.0             0.000135       4.014215      0.000139        136.047391         0.000135
          mixed    CACHE   0.8125 0.804167         1.0        1.0          0.000045          0.000098                  0.0             0.000055       2.155637      0.000053         55.725445         0.000055
          mixed    MEMBW   0.9375 0.950000         1.0        1.0          0.000045          0.000143                  0.0             0.000081       3.114568      0.000098         82.262708         0.000081
          mixed      TLB   0.8125 0.804167         1.0        1.0          0.000045          0.000105                  0.0             0.000048       2.299062      0.000060         48.907492         0.000048
```

## Paper-style Aggregates (Final Config)
- Base score mean stressor AUC-PR (all five): **0.8658**
- Base score mean stressor ROC-AUC (all five): **0.8625**
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
            tier0       20      0.35      0.55          0.35  0.313333               0.022311                 0.016958           mixed
      tier0_tier1       20      0.20      0.60          0.20  0.134266               0.015546                 0.018289           mixed
tier0_tier1_tier2       20      0.40      0.80          0.40  0.412698               0.013027                 0.010396           mixed
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.25       0.5          0.25  0.220000               0.018114                 0.017426           mixed
      tier0_tier1       20      0.10       0.3          0.10  0.103030               0.100989                 0.044921           mixed
tier0_tier1_tier2       20      0.15       0.4          0.15  0.166364               0.092714                 0.027056           mixed
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.20      0.55          0.20  0.190649               0.020115                 0.016832           mixed
      tier0_tier1       20      0.20      0.55          0.20  0.198730               0.019693                 0.014890           mixed
tier0_tier1_tier2       20      0.25      0.55          0.25  0.225397               0.016571                 0.014108           mixed
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.55       0.9      0.527778  0.434343               0.032192                 0.040380           mixed
      tier0_tier1       20      0.45       0.8      0.416667  0.335664               0.020810                 0.020097           mixed
tier0_tier1_tier2       20      0.50       0.7      0.500000  0.448622               0.020321                 0.019573           mixed
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20       0.4      0.55        0.45           0.4  0.373333      0.35          0.65            0.571429            0.571429                     0.4            0.293333              -0.001862                 0.002342            0.016131              0.014984           0.011970        0.106540           mixed
      tier0_tier1       20       0.3      0.55        0.45           0.3  0.225758      0.70          0.30            0.285714            0.500000                     0.3            0.226032              -0.003220                 0.000079            0.026305              0.027990           0.012765       -0.032197           mixed
tier0_tier1_tier2       20       0.3      0.75        0.40           0.3  0.296061      0.45          0.55            0.333333            0.888889                     0.4            0.313333               0.002499                 0.004558            0.023063              0.019749           0.015051        0.075314           mixed
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.35      0.60        0.45          0.35  0.355873      0.50          0.50            0.300000            0.500000                0.200000            0.217143              -0.010884                 0.010696            0.016131              0.014984           0.011970       -0.043254           mixed
      tier0_tier1       20      0.25      0.35        0.45          0.25  0.166667      0.65          0.35            0.307692            0.384615                0.266667            0.214286              -0.061983                -0.032395            0.026305              0.027990           0.012765       -0.177143           mixed
tier0_tier1_tier2       20      0.15      0.30        0.40          0.15  0.106667      0.65          0.35            0.076923            0.230769                0.066667            0.050000               0.025798                 0.004286            0.023063              0.019749           0.015051       -0.017673           mixed
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0  conf_0.00              0.000000      14      0.70          0.30            0.428571            0.500000                0.416667            0.366667           mixed
            tier0  conf_0.05              0.050000       9      0.45          0.55            0.555556            0.555556                0.437500            0.310000           mixed
            tier0  conf_0.10              0.100000       5      0.25          0.75            0.600000            0.600000                0.500000            0.293333           mixed
            tier0    trained              0.106540       5      0.25          0.75            0.600000            0.600000                0.500000            0.293333           mixed
            tier0  conf_0.15              0.150000       4      0.20          0.80            0.750000            0.750000                0.666667            0.360000           mixed
            tier0  conf_0.20              0.200000       2      0.10          0.90            1.000000            1.000000                1.000000            0.200000           mixed
            tier0  conf_0.25              0.250000       2      0.10          0.90            1.000000            1.000000                1.000000            0.200000           mixed
      tier0_tier1    trained             -0.032197      14      0.70          0.30            0.285714            0.500000                0.300000            0.226032           mixed
      tier0_tier1  conf_0.00              0.000000      12      0.60          0.40            0.250000            0.500000                0.266667            0.214286           mixed
      tier0_tier1  conf_0.05              0.050000       6      0.30          0.70            0.333333            0.666667                0.444444            0.166667           mixed
      tier0_tier1  conf_0.10              0.100000       5      0.25          0.75            0.200000            0.600000                0.333333            0.066667           mixed
      tier0_tier1  conf_0.15              0.150000       1      0.05          0.95            1.000000            1.000000                1.000000            0.200000           mixed
      tier0_tier1  conf_0.20              0.200000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
      tier0_tier1  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
tier0_tier1_tier2  conf_0.00              0.000000      16      0.80          0.20            0.312500            0.750000                0.300000            0.297619           mixed
tier0_tier1_tier2  conf_0.05              0.050000       8      0.40          0.60            0.250000            0.750000                0.200000            0.190476           mixed
tier0_tier1_tier2    trained              0.075314       5      0.25          0.75            0.200000            0.600000                0.250000            0.080000           mixed
tier0_tier1_tier2  conf_0.10              0.100000       4      0.20          0.80            0.250000            0.500000                0.333333            0.080000           mixed
tier0_tier1_tier2  conf_0.15              0.150000       1      0.05          0.95            1.000000            1.000000                1.000000            0.200000           mixed
tier0_tier1_tier2  conf_0.20              0.200000       1      0.05          0.95            1.000000            1.000000                1.000000            0.200000           mixed
tier0_tier1_tier2  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained             -0.043254      13      0.65          0.35            0.307692            0.538462                0.216667            0.221429           mixed
            tier0  conf_0.00              0.000000      13      0.65          0.35            0.307692            0.538462                0.216667            0.221429           mixed
            tier0  conf_0.05              0.050000      10      0.50          0.50            0.200000            0.500000                0.166667            0.190476           mixed
            tier0  conf_0.10              0.100000       6      0.30          0.70            0.333333            0.666667                0.277778            0.213333           mixed
            tier0  conf_0.15              0.150000       2      0.10          0.90            0.500000            1.000000                0.500000            0.200000           mixed
            tier0  conf_0.20              0.200000       2      0.10          0.90            0.500000            1.000000                0.500000            0.200000           mixed
            tier0  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
      tier0_tier1    trained             -0.177143      13      0.65          0.35            0.307692            0.461538                0.291667            0.203175           mixed
      tier0_tier1  conf_0.00              0.000000       9      0.45          0.55            0.111111            0.222222                0.125000            0.100000           mixed
      tier0_tier1  conf_0.05              0.050000       6      0.30          0.70            0.000000            0.000000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.10              0.100000       5      0.25          0.75            0.000000            0.000000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.15              0.150000       4      0.20          0.80            0.000000            0.000000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.20              0.200000       3      0.15          0.85            0.000000            0.000000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.25              0.250000       2      0.10          0.90            0.000000            0.000000                0.000000            0.000000           mixed
tier0_tier1_tier2    trained             -0.017673      12      0.60          0.40            0.083333            0.166667                0.066667            0.066667           mixed
tier0_tier1_tier2  conf_0.00              0.000000      12      0.60          0.40            0.083333            0.166667                0.066667            0.066667           mixed
tier0_tier1_tier2  conf_0.05              0.050000       8      0.40          0.60            0.000000            0.125000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.10              0.100000       7      0.35          0.65            0.000000            0.142857                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.15              0.150000       4      0.20          0.80            0.000000            0.250000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.20              0.200000       4      0.20          0.80            0.000000            0.250000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.25              0.250000       4      0.20          0.80            0.000000            0.250000                0.000000            0.000000           mixed
```

## Diagnosis Mode Comparison
- Whole-run and post-alert-window diagnosis are exported together so the diagnosis mode can be evaluated directly.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile diagnosis_target    diagnosis_mode  family_acc  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau                       status  min_class_count  min_group_count    group_key  include_workload
            tier0       20      0.35      0.55      0.350000  0.313333               0.022311                 0.016958           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.20      0.60      0.200000  0.134266               0.015546                 0.018289           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.40      0.80      0.400000  0.412698               0.013027                 0.010396           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.25      0.50      0.250000  0.220000               0.018114                 0.017426           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.10      0.30      0.100000  0.103030               0.100989                 0.044921           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.15      0.40      0.150000  0.166364               0.092714                 0.027056           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.40      0.55      0.400000  0.373333              -0.001862                 0.002342           mixed     hierarchical         whole_run        0.45      0.35          0.65            0.571429            0.571429                0.400000            0.293333            0.016131              0.014984           0.011970        0.106540                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.30      0.55      0.300000  0.225758              -0.003220                 0.000079           mixed     hierarchical         whole_run        0.45      0.70          0.30            0.285714            0.500000                0.300000            0.226032            0.026305              0.027990           0.012765       -0.032197                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.30      0.75      0.300000  0.296061               0.002499                 0.004558           mixed     hierarchical         whole_run        0.40      0.45          0.55            0.333333            0.888889                0.400000            0.313333            0.023063              0.019749           0.015051        0.075314                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.35      0.60      0.350000  0.355873              -0.010884                 0.010696           mixed     hierarchical post_alert_window        0.45      0.50          0.50            0.300000            0.500000                0.200000            0.217143            0.016131              0.014984           0.011970       -0.043254                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.25      0.35      0.250000  0.166667              -0.061983                -0.032395           mixed     hierarchical post_alert_window        0.45      0.65          0.35            0.307692            0.384615                0.266667            0.214286            0.026305              0.027990           0.012765       -0.177143                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.15      0.30      0.150000  0.106667               0.025798                 0.004286           mixed     hierarchical post_alert_window        0.40      0.65          0.35            0.076923            0.230769                0.066667            0.050000            0.023063              0.019749           0.015051       -0.017673                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.55      0.90      0.527778  0.434343               0.032192                 0.040380           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.45      0.80      0.416667  0.335664               0.020810                 0.020097           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.50      0.70      0.500000  0.448622               0.020321                 0.019573           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.672605         0.172432     0.154963              tier0           mixed
  BRANCH     0.746924         0.098452     0.154624              tier0           mixed
   CACHE     0.529449         0.361127     0.109423              tier0           mixed
   MEMBW     0.769114         0.101967     0.128919              tier0           mixed
     TLB     0.680593         0.156597     0.162809              tier0           mixed
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC               memory_io       0.271543         0.377627             0.111646                 0.206902                 0.032282           mixed
  BRANCH               memory_io       0.253342         0.440246             0.057105                 0.201393                 0.047915           mixed
   CACHE                 compute       0.478713         0.253773             0.075209                 0.139479                 0.052827           mixed
   MEMBW               memory_io       0.249148         0.452540             0.062299                 0.174047                 0.061966           mixed
     TLB               memory_io       0.305935         0.376789             0.090212                 0.196032                 0.031032           mixed
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
            tier0                   0.25                         1.85567                      3.711340                 0.30                     54.0                 599.0                0.20                0.20                0.25           mixed
      tier0_tier1                   0.00                         0.00000                      0.927835                 0.55                     43.0                 820.0                0.35                0.35                0.45           mixed
tier0_tier1_tier2                   0.00                         0.00000                      0.000000                 0.55                     37.0                 818.0                0.35                0.35                0.45           mixed
```

## Files
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B30_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B30_a0.05_k3/config_runtime_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B30_a0.05_k3/run_context.json`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B30_a0.05_k3/case_inventory.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B30_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B30_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B30_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B30_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B30_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B30_a0.05_k3/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B30_a0.05_k3/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B30_a0.05_k3/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B30_a0.05_k3/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B30_a0.05_k3/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B30_a0.05_k3/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B30_a0.05_k3/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B30_a0.05_k3/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B30_a0.05_k3/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B30_a0.05_k3/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B30_a0.05_k3/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B30_a0.05_k3/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B30_a0.05_k3/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B30_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B30_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B30_a0.05_k3/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B30_a0.05_k3/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B30_a0.05_k3/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B30_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B30_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B30_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B30_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B30_a0.05_k3/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B30_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B30_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B30_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B30_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B30_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B30_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B30_a0.05_k3/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B30_a0.05_k3/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B30_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B30_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B30_a0.05_k3/figures/fig_detection_latency.png`
