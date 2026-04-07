# DICE Full Retrain Results

## Setup
- Feature profile: full ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_full_5hz.csv', 'tier2': 'tier2_full_5hz.csv'})
- Protocol: global, benign-only fit/calibration, block_B=45, alpha=0.05, persist_k=3, gain=0.15
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
           full             tier0       24          46          2.307192   0.8125 0.940232         1.0        1.0            0.0           0.30              0.010929              0.022954                      0.0                 0.012282
           full       tier0_tier1       24          64          3.048812   0.8250 0.958228         1.0        1.0            0.0           0.60              0.015002              0.046171                      0.0                 0.022421
           full tier0_tier1_tier2       24          75          3.605827   0.9750 0.995119         1.0        1.0            0.0           0.95              0.002903              0.008127                      0.0                 0.004618
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc  pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
           full   ATOMIC   0.9375    0.95         1.0        1.0          0.002903          0.007449                  0.0             0.004473       2.565820      0.004547       4474.017166         0.004473
           full   BRANCH   1.0000    1.00         1.0        1.0          0.002903          0.008602                  0.0             0.006236       2.962689      0.005699       6236.869654         0.006236
           full    CACHE   0.9375    0.95         1.0        1.0          0.002903          0.009722                  0.0             0.006585       3.348608      0.006820       6586.266566         0.006585
           full    MEMBW   1.0000    1.00         1.0        1.0          0.002903          0.009091                  0.0             0.005378       3.131023      0.006188       5379.306506         0.005378
           full      TLB   1.0000    1.00         1.0        1.0          0.002903          0.006604                  0.0             0.004585       2.274805      0.003702       4586.042356         0.004585
```

## Paper-style Aggregates (Final Config)
- Base score mean stressor AUC-PR (all five): **0.9800**
- Base score mean stressor ROC-AUC (all five): **0.9750**
- WC score mean stressor AUC-PR (all five): **1.0000**
- WC score mean stressor ROC-AUC (all five): **1.0000**
- Base score mean stressor AUC-PR (excluding BRANCH/TLB): **0.9667**
- Base score mean stressor ROC-AUC (excluding BRANCH/TLB): **0.9583**
- WC score mean stressor AUC-PR (excluding BRANCH/TLB): **1.0000**
- WC score mean stressor ROC-AUC (excluding BRANCH/TLB): **1.0000**

## Diagnosis
- Feature-level diagnosis uses normalized whole-run residual-attribution prototypes as the default paper-facing result, with diagnosis-only filtering that removes monotonic counters and downweights generic memory-state features.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.30      0.55          0.30  0.225758               0.026569                 0.022909            full
      tier0_tier1       20      0.25      0.55          0.25  0.257143               0.015827                 0.011755            full
tier0_tier1_tier2       20      0.35      0.55          0.35  0.256667               0.018746                 0.016683            full
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.20      0.55          0.20  0.175253               0.020091                 0.017835            full
      tier0_tier1       20      0.15      0.35          0.15  0.155556               0.064773                 0.039245            full
tier0_tier1_tier2       20      0.10      0.15          0.10  0.076364               0.024969                 0.020148            full
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20       0.2      0.50           0.2  0.194286               0.018016                 0.013889            full
      tier0_tier1       20       0.3      0.65           0.3  0.272727               0.018553                 0.012946            full
tier0_tier1_tier2       20       0.4      0.60           0.4  0.370346               0.016031                 0.012434            full
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.60      0.90      0.500000  0.421818               0.035224                 0.037364            full
      tier0_tier1       20      0.45      0.85      0.416667  0.419048               0.016317                 0.011305            full
tier0_tier1_tier2       20      0.45      0.90      0.527778  0.493386               0.014762                 0.013408            full
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.40      0.55         0.5          0.40  0.312727      0.50          0.50            0.500000            0.600000                0.400000            0.293333              -0.009360                -0.001788            0.017103              0.016506           0.011352        0.021724            full
      tier0_tier1       20      0.35      0.60         0.5          0.35  0.374286      0.70          0.30            0.357143            0.571429                0.333333            0.404444               0.012214                 0.011294            0.022450              0.017471           0.005201        0.000000            full
tier0_tier1_tier2       20      0.20      0.45         0.4          0.20  0.146032      0.65          0.35            0.307692            0.615385                0.266667            0.206061               0.012161                 0.013942            0.020224              0.016845           0.005210        0.026713            full
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.40      0.60         0.5          0.40  0.368759      0.55          0.45            0.363636            0.545455                0.266667            0.238095              -0.019904                 0.003563            0.017103              0.016506           0.011352       -0.088413            full
      tier0_tier1       20      0.25      0.35         0.5          0.25  0.213333      0.35          0.65            0.142857            0.285714                0.250000            0.133333               0.001710                 0.025054            0.022450              0.017471           0.005201        0.199461            full
tier0_tier1_tier2       20      0.20      0.30         0.4          0.20  0.150427      0.55          0.45            0.090909            0.272727                0.066667            0.044444              -0.017265                -0.018968            0.020224              0.016845           0.005210       -0.113403            full
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0  conf_0.00              0.000000      10      0.50          0.50            0.500000            0.600000                0.400000            0.293333            full
            tier0    trained              0.021724      10      0.50          0.50            0.500000            0.600000                0.400000            0.293333            full
            tier0  conf_0.05              0.050000       9      0.45          0.55            0.555556            0.555556                0.400000            0.310000            full
            tier0  conf_0.10              0.100000       5      0.25          0.75            0.600000            0.600000                0.500000            0.293333            full
            tier0  conf_0.15              0.150000       5      0.25          0.75            0.600000            0.600000                0.500000            0.293333            full
            tier0  conf_0.20              0.200000       3      0.15          0.85            0.666667            0.666667                0.500000            0.160000            full
            tier0  conf_0.25              0.250000       2      0.10          0.90            1.000000            1.000000                1.000000            0.200000            full
      tier0_tier1    trained              0.000000      15      0.75          0.25            0.333333            0.600000                0.350000            0.344286            full
      tier0_tier1  conf_0.00              0.000000      15      0.75          0.25            0.333333            0.600000                0.350000            0.344286            full
      tier0_tier1  conf_0.05              0.050000      11      0.55          0.45            0.272727            0.636364                0.233333            0.183333            full
      tier0_tier1  conf_0.10              0.100000       8      0.40          0.60            0.125000            0.500000                0.100000            0.133333            full
      tier0_tier1  conf_0.15              0.150000       3      0.15          0.85            0.000000            0.666667                0.000000            0.000000            full
      tier0_tier1  conf_0.20              0.200000       2      0.10          0.90            0.000000            1.000000                0.000000            0.000000            full
      tier0_tier1  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN            full
tier0_tier1_tier2  conf_0.00              0.000000      16      0.80          0.20            0.250000            0.500000                0.233333            0.200000            full
tier0_tier1_tier2    trained              0.026713      12      0.60          0.40            0.250000            0.583333                0.200000            0.200000            full
tier0_tier1_tier2  conf_0.05              0.050000      12      0.60          0.40            0.250000            0.583333                0.200000            0.200000            full
tier0_tier1_tier2  conf_0.10              0.100000      10      0.50          0.50            0.300000            0.700000                0.300000            0.213333            full
tier0_tier1_tier2  conf_0.15              0.150000       5      0.25          0.75            0.000000            0.600000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.20              0.200000       3      0.15          0.85            0.000000            0.333333                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.25              0.250000       2      0.10          0.90            0.000000            0.500000                0.000000            0.000000            full
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained             -0.088413      12      0.60          0.40            0.416667            0.583333                0.333333            0.304762            full
            tier0  conf_0.00              0.000000      11      0.55          0.45            0.363636            0.545455                0.266667            0.238095            full
            tier0  conf_0.05              0.050000       8      0.40          0.60            0.500000            0.750000                0.333333            0.271429            full
            tier0  conf_0.10              0.100000       7      0.35          0.65            0.428571            0.714286                0.333333            0.260000            full
            tier0  conf_0.15              0.150000       3      0.15          0.85            0.333333            0.666667                0.500000            0.200000            full
            tier0  conf_0.20              0.200000       2      0.10          0.90            0.000000            0.500000                0.000000            0.000000            full
            tier0  conf_0.25              0.250000       2      0.10          0.90            0.000000            0.500000                0.000000            0.000000            full
      tier0_tier1  conf_0.00              0.000000      14      0.70          0.30            0.214286            0.357143                0.200000            0.214286            full
      tier0_tier1  conf_0.05              0.050000      14      0.70          0.30            0.214286            0.357143                0.200000            0.214286            full
      tier0_tier1  conf_0.10              0.100000       9      0.45          0.55            0.111111            0.333333                0.100000            0.100000            full
      tier0_tier1  conf_0.15              0.150000       7      0.35          0.65            0.000000            0.285714                0.000000            0.000000            full
      tier0_tier1    trained              0.199461       4      0.20          0.80            0.000000            0.250000                0.000000            0.000000            full
      tier0_tier1  conf_0.20              0.200000       4      0.20          0.80            0.000000            0.250000                0.000000            0.000000            full
      tier0_tier1  conf_0.25              0.250000       4      0.20          0.80            0.000000            0.250000                0.000000            0.000000            full
tier0_tier1_tier2    trained             -0.113403      16      0.80          0.20            0.187500            0.312500                0.166667            0.146667            full
tier0_tier1_tier2  conf_0.00              0.000000       8      0.40          0.60            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.05              0.050000       7      0.35          0.65            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.10              0.100000       4      0.20          0.80            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.15              0.150000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.20              0.200000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.25              0.250000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000            full
```

## Diagnosis Mode Comparison
- Whole-run and post-alert-window diagnosis are exported together so the diagnosis mode can be evaluated directly.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile diagnosis_target    diagnosis_mode  family_acc  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau                       status  min_class_count  min_group_count    group_key  include_workload
            tier0       20      0.30      0.55      0.300000  0.225758               0.026569                 0.022909            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.25      0.55      0.250000  0.257143               0.015827                 0.011755            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.35      0.55      0.350000  0.256667               0.018746                 0.016683            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.20      0.55      0.200000  0.175253               0.020091                 0.017835            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.15      0.35      0.150000  0.155556               0.064773                 0.039245            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.10      0.15      0.100000  0.076364               0.024969                 0.020148            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.40      0.55      0.400000  0.312727              -0.009360                -0.001788            full     hierarchical         whole_run         0.5      0.50          0.50            0.500000            0.600000                0.400000            0.293333            0.017103              0.016506           0.011352        0.021724                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.35      0.60      0.350000  0.374286               0.012214                 0.011294            full     hierarchical         whole_run         0.5      0.70          0.30            0.357143            0.571429                0.333333            0.404444            0.022450              0.017471           0.005201        0.000000                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.20      0.45      0.200000  0.146032               0.012161                 0.013942            full     hierarchical         whole_run         0.4      0.65          0.35            0.307692            0.615385                0.266667            0.206061            0.020224              0.016845           0.005210        0.026713                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.40      0.60      0.400000  0.368759              -0.019904                 0.003563            full     hierarchical post_alert_window         0.5      0.55          0.45            0.363636            0.545455                0.266667            0.238095            0.017103              0.016506           0.011352       -0.088413                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.25      0.35      0.250000  0.213333               0.001710                 0.025054            full     hierarchical post_alert_window         0.5      0.35          0.65            0.142857            0.285714                0.250000            0.133333            0.022450              0.017471           0.005201        0.199461                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.20      0.30      0.200000  0.150427              -0.017265                -0.018968            full     hierarchical post_alert_window         0.4      0.55          0.45            0.090909            0.272727                0.066667            0.044444            0.020224              0.016845           0.005210       -0.113403                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.60      0.90      0.500000  0.421818               0.035224                 0.037364            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.45      0.85      0.416667  0.419048               0.016317                 0.011305            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.45      0.90      0.527778  0.493386               0.014762                 0.013408            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.574330         0.257955     0.167715              tier0            full
  BRANCH     0.603791         0.217878     0.178331              tier0            full
   CACHE     0.458858         0.197704     0.343438              tier0            full
   MEMBW     0.621826         0.227256     0.150918              tier0            full
     TLB     0.543175         0.273009     0.183816              tier0            full
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC                 compute       0.365990         0.290460             0.110188                 0.122439                 0.110924            full
  BRANCH                 compute       0.328156         0.354286             0.081011                 0.158065                 0.078482            full
   CACHE                 compute       0.509000         0.266488             0.068634                 0.087573                 0.068305            full
   MEMBW                 compute       0.343512         0.327053             0.094675                 0.122921                 0.111839            full
     TLB                 compute       0.371803         0.300325             0.110033                 0.124837                 0.093001            full
```

## Supervised Diagnosis
- This path is intended for expanded anomaly sets with repeated runs per workload-stressor pair. It is skipped automatically until each stressor has enough samples.
```text
           config                       status  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  min_class_count  min_group_count    group_key  include_workload feature_profile
            tier0 skipped_insufficient_samples       20       NaN       NaN           NaN       NaN                4                4 base_case_id                 1            full
      tier0_tier1 skipped_insufficient_samples       20       NaN       NaN           NaN       NaN                4                4 base_case_id                 1            full
tier0_tier1_tier2 skipped_insufficient_samples       20       NaN       NaN           NaN       NaN                4                4 base_case_id                 1            full
```

## Sequential Decisioning
```text
           config  benign_run_alert_rate  benign_persist_alerts_per_hour  benign_block_alerts_per_hour  anomaly_detect_rate  median_time_to_detect_s  p90_time_to_detect_s  detect_within_120s  detect_within_300s  detect_within_600s feature_profile
            tier0                    0.0                             0.0                           0.0                 0.30                     64.5                 625.5                 0.2                0.20                0.25            full
      tier0_tier1                    0.0                             0.0                           0.0                 0.60                     66.0                 783.2                 0.4                0.45                0.50            full
tier0_tier1_tier2                    0.0                             0.0                           0.0                 0.95                     47.0                 632.8                 0.7                0.75                0.85            full
```

## Files
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B45_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B45_a0.05_k3/config_runtime_summary.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B45_a0.05_k3/run_context.json`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B45_a0.05_k3/case_inventory.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B45_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B45_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B45_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B45_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B45_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B45_a0.05_k3/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B45_a0.05_k3/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B45_a0.05_k3/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B45_a0.05_k3/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B45_a0.05_k3/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B45_a0.05_k3/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B45_a0.05_k3/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B45_a0.05_k3/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B45_a0.05_k3/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B45_a0.05_k3/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B45_a0.05_k3/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B45_a0.05_k3/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B45_a0.05_k3/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B45_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B45_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B45_a0.05_k3/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B45_a0.05_k3/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B45_a0.05_k3/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B45_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B45_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B45_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B45_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B45_a0.05_k3/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B45_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B45_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B45_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B45_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B45_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B45_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B45_a0.05_k3/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B45_a0.05_k3/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B45_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B45_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B45_a0.05_k3/figures/fig_detection_latency.png`
