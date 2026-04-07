# DICE Full Retrain Results

## Setup
- Feature profile: full ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_full_5hz.csv', 'tier2': 'tier2_full_5hz.csv'})
- Protocol: global, benign-only fit/calibration, block_B=30, alpha=0.05, persist_k=3, gain=0.2
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
           full             tier0       24          46          2.211174   0.8000 0.931899         1.0        1.0           0.25           0.30              0.009451              0.019163                      0.0                 0.010567
           full       tier0_tier1       24          64          2.914958   0.8375 0.960040         1.0        1.0           0.25           0.65              0.014295              0.040018                      0.0                 0.018757
           full tier0_tier1_tier2       24          75          3.485356   0.9750 0.995119         1.0        1.0           0.00           0.95              0.002887              0.007957                      0.0                 0.004458
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc  pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
           full   ATOMIC   0.9375    0.95         1.0        1.0          0.002887          0.007204                  0.0             0.004021       2.494478      0.004316       4021.867174         0.004021
           full   BRANCH   1.0000    1.00         1.0        1.0          0.002887          0.009904                  0.0             0.006984       3.429315      0.007017       6985.096198         0.006984
           full    CACHE   0.9375    0.95         1.0        1.0          0.002887          0.009279                  0.0             0.006003       3.212869      0.006391       6004.075453         0.006003
           full    MEMBW   1.0000    1.00         1.0        1.0          0.002887          0.008693                  0.0             0.004934       3.010174      0.005806       4934.724140         0.004934
           full      TLB   1.0000    1.00         1.0        1.0          0.002887          0.007470                  0.0             0.004871       2.586610      0.004583       4871.575480         0.004871
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
            tier0       20       0.3       0.6           0.3  0.238961               0.027231                 0.021158            full
      tier0_tier1       20       0.2       0.4           0.2  0.177143               0.013507                 0.009318            full
tier0_tier1_tier2       20       0.3       0.5           0.3  0.220952               0.018873                 0.017335            full
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20       0.3      0.50           0.3  0.268889               0.014782                 0.010177            full
      tier0_tier1       20       0.1      0.30           0.1  0.100000               0.101352                 0.045606            full
tier0_tier1_tier2       20       0.1      0.15           0.1  0.080000               0.025679                 0.020212            full
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.25      0.65          0.25  0.200000               0.014126                 0.011200            full
      tier0_tier1       20      0.20      0.55          0.20  0.152727               0.019191                 0.015656            full
tier0_tier1_tier2       20      0.40      0.60          0.40  0.357013               0.017104                 0.015528            full
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.60      0.85      0.500000  0.416667               0.034283                 0.038040            full
      tier0_tier1       20      0.40      0.85      0.333333  0.279365               0.019882                 0.019112            full
tier0_tier1_tier2       20      0.45      0.90      0.583333  0.480556               0.014590                 0.014362            full
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.40      0.65        0.50          0.40  0.342222      0.45          0.55            0.444444            0.555556                0.400000            0.274286              -0.000297                 0.009789            0.015129              0.017260           0.012620        0.092695            full
      tier0_tier1       20      0.25      0.40        0.45          0.25  0.257143      0.80          0.20            0.187500            0.375000                0.183333            0.177778               0.011491                 0.014945            0.020594              0.019522           0.009820       -0.036733            full
tier0_tier1_tier2       20      0.20      0.45        0.35          0.20  0.146032      0.50          0.50            0.300000            0.600000                0.333333            0.188889               0.011634                 0.016246            0.020955              0.018408           0.005874        0.053636            full
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20       0.4       0.6        0.50           0.4  0.396032      0.45          0.55            0.222222            0.444444                0.133333            0.114286              -0.016583                 0.006215            0.015129              0.017260           0.012620        0.024936            full
      tier0_tier1       20       0.1       0.3        0.45           0.1  0.080808      0.25          0.75            0.000000            0.400000                0.000000            0.000000              -0.021034                 0.016247            0.020594              0.019522           0.009820        0.380051            full
tier0_tier1_tier2       20       0.2       0.3        0.35           0.2  0.150427      0.55          0.45            0.090909            0.272727                0.066667            0.044444              -0.014554                -0.013991            0.020955              0.018408           0.005874       -0.132662            full
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0  conf_0.00              0.000000      13      0.65          0.35            0.384615            0.615385                0.350000            0.280000            full
            tier0  conf_0.05              0.050000      11      0.55          0.45            0.454545            0.636364                0.350000            0.280000            full
            tier0    trained              0.092695       8      0.40          0.60            0.500000            0.500000                0.400000            0.293333            full
            tier0  conf_0.10              0.100000       7      0.35          0.65            0.571429            0.571429                0.400000            0.293333            full
            tier0  conf_0.15              0.150000       4      0.20          0.80            0.500000            0.500000                0.333333            0.160000            full
            tier0  conf_0.20              0.200000       3      0.15          0.85            0.666667            0.666667                0.500000            0.160000            full
            tier0  conf_0.25              0.250000       2      0.10          0.90            1.000000            1.000000                1.000000            0.200000            full
      tier0_tier1    trained             -0.036733      16      0.80          0.20            0.312500            0.437500                0.300000            0.317143            full
      tier0_tier1  conf_0.00              0.000000      14      0.70          0.30            0.214286            0.357143                0.200000            0.180000            full
      tier0_tier1  conf_0.05              0.050000      11      0.55          0.45            0.181818            0.363636                0.133333            0.114286            full
      tier0_tier1  conf_0.10              0.100000       7      0.35          0.65            0.142857            0.428571                0.100000            0.133333            full
      tier0_tier1  conf_0.15              0.150000       4      0.20          0.80            0.000000            0.250000                0.000000            0.000000            full
      tier0_tier1  conf_0.20              0.200000       1      0.05          0.95            0.000000            1.000000                0.000000            0.000000            full
      tier0_tier1  conf_0.25              0.250000       1      0.05          0.95            0.000000            1.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.00              0.000000      16      0.80          0.20            0.187500            0.437500                0.200000            0.146667            full
tier0_tier1_tier2  conf_0.05              0.050000      13      0.65          0.35            0.230769            0.538462                0.200000            0.166667            full
tier0_tier1_tier2    trained              0.053636      13      0.65          0.35            0.230769            0.538462                0.200000            0.166667            full
tier0_tier1_tier2  conf_0.10              0.100000      10      0.50          0.50            0.300000            0.700000                0.300000            0.213333            full
tier0_tier1_tier2  conf_0.15              0.150000       4      0.20          0.80            0.000000            0.500000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.20              0.200000       3      0.15          0.85            0.000000            0.333333                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.25              0.250000       2      0.10          0.90            0.000000            0.500000                0.000000            0.000000            full
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0  conf_0.00              0.000000      12      0.60          0.40            0.333333            0.416667                0.266667            0.237143            full
            tier0    trained              0.024936      11      0.55          0.45            0.272727            0.363636                0.166667            0.157143            full
            tier0  conf_0.05              0.050000       7      0.35          0.65            0.428571            0.428571                0.291667            0.213333            full
            tier0  conf_0.10              0.100000       2      0.10          0.90            0.500000            0.500000                0.500000            0.200000            full
            tier0  conf_0.15              0.150000       2      0.10          0.90            0.500000            0.500000                0.500000            0.200000            full
            tier0  conf_0.20              0.200000       1      0.05          0.95            1.000000            1.000000                1.000000            0.200000            full
            tier0  conf_0.25              0.250000       1      0.05          0.95            1.000000            1.000000                1.000000            0.200000            full
      tier0_tier1  conf_0.00              0.000000      13      0.65          0.35            0.076923            0.307692                0.050000            0.057143            full
      tier0_tier1  conf_0.05              0.050000      11      0.55          0.45            0.090909            0.272727                0.066667            0.066667            full
      tier0_tier1  conf_0.10              0.100000       8      0.40          0.60            0.000000            0.250000                0.000000            0.000000            full
      tier0_tier1  conf_0.15              0.150000       7      0.35          0.65            0.000000            0.285714                0.000000            0.000000            full
      tier0_tier1  conf_0.20              0.200000       7      0.35          0.65            0.000000            0.285714                0.000000            0.000000            full
      tier0_tier1  conf_0.25              0.250000       7      0.35          0.65            0.000000            0.285714                0.000000            0.000000            full
      tier0_tier1    trained              0.380051       4      0.20          0.80            0.000000            0.250000                0.000000            0.000000            full
tier0_tier1_tier2    trained             -0.132662      15      0.75          0.25            0.133333            0.266667                0.133333            0.120000            full
tier0_tier1_tier2  conf_0.00              0.000000       8      0.40          0.60            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.05              0.050000       7      0.35          0.65            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.10              0.100000       4      0.20          0.80            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.15              0.150000       3      0.15          0.85            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.20              0.200000       2      0.10          0.90            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.25              0.250000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000            full
```

## Diagnosis Mode Comparison
- Whole-run and post-alert-window diagnosis are exported together so the diagnosis mode can be evaluated directly.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile diagnosis_target    diagnosis_mode  family_acc  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau                       status  min_class_count  min_group_count    group_key  include_workload
            tier0       20      0.30      0.60      0.300000  0.238961               0.027231                 0.021158            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.20      0.40      0.200000  0.177143               0.013507                 0.009318            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.30      0.50      0.300000  0.220952               0.018873                 0.017335            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.30      0.50      0.300000  0.268889               0.014782                 0.010177            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.10      0.30      0.100000  0.100000               0.101352                 0.045606            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.10      0.15      0.100000  0.080000               0.025679                 0.020212            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.40      0.65      0.400000  0.342222              -0.000297                 0.009789            full     hierarchical         whole_run        0.50      0.45          0.55            0.444444            0.555556                0.400000            0.274286            0.015129              0.017260           0.012620        0.092695                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.25      0.40      0.250000  0.257143               0.011491                 0.014945            full     hierarchical         whole_run        0.45      0.80          0.20            0.187500            0.375000                0.183333            0.177778            0.020594              0.019522           0.009820       -0.036733                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.20      0.45      0.200000  0.146032               0.011634                 0.016246            full     hierarchical         whole_run        0.35      0.50          0.50            0.300000            0.600000                0.333333            0.188889            0.020955              0.018408           0.005874        0.053636                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.40      0.60      0.400000  0.396032              -0.016583                 0.006215            full     hierarchical post_alert_window        0.50      0.45          0.55            0.222222            0.444444                0.133333            0.114286            0.015129              0.017260           0.012620        0.024936                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.10      0.30      0.100000  0.080808              -0.021034                 0.016247            full     hierarchical post_alert_window        0.45      0.25          0.75            0.000000            0.400000                0.000000            0.000000            0.020594              0.019522           0.009820        0.380051                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.20      0.30      0.200000  0.150427              -0.014554                -0.013991            full     hierarchical post_alert_window        0.35      0.55          0.45            0.090909            0.272727                0.066667            0.044444            0.020955              0.018408           0.005874       -0.132662                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.60      0.85      0.500000  0.416667               0.034283                 0.038040            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.40      0.85      0.333333  0.279365               0.019882                 0.019112            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.45      0.90      0.583333  0.480556               0.014590                 0.014362            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.578914         0.264962     0.156124              tier0            full
  BRANCH     0.607780         0.218943     0.173278              tier0            full
   CACHE     0.471142         0.201128     0.327729              tier0            full
   MEMBW     0.623312         0.235666     0.141022              tier0            full
     TLB     0.550079         0.276928     0.172993              tier0            full
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC                 compute       0.361303         0.291023             0.115585                 0.127177                 0.104912            full
  BRANCH                 compute       0.322702         0.353707             0.084158                 0.165002                 0.074430            full
   CACHE                 compute       0.498234         0.271959             0.072246                 0.091935                 0.065627            full
   MEMBW                 compute       0.335189         0.331908             0.102310                 0.127305                 0.103288            full
     TLB                 compute       0.362783         0.303347             0.115887                 0.130783                 0.087200            full
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
            tier0                   0.25                        0.927835                      2.783505                 0.30                     53.5                 605.5                0.20                0.20                0.25            full
      tier0_tier1                   0.25                        0.927835                      2.783505                 0.65                     40.0                 753.6                0.45                0.45                0.55            full
tier0_tier1_tier2                   0.00                        0.000000                      0.000000                 0.95                     32.0                 587.6                0.70                0.75                0.85            full
```

## Files
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B30_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B30_a0.05_k3/config_runtime_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B30_a0.05_k3/run_context.json`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B30_a0.05_k3/case_inventory.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B30_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B30_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B30_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B30_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B30_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B30_a0.05_k3/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B30_a0.05_k3/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B30_a0.05_k3/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B30_a0.05_k3/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B30_a0.05_k3/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B30_a0.05_k3/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B30_a0.05_k3/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B30_a0.05_k3/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B30_a0.05_k3/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B30_a0.05_k3/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B30_a0.05_k3/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B30_a0.05_k3/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B30_a0.05_k3/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B30_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B30_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B30_a0.05_k3/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B30_a0.05_k3/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B30_a0.05_k3/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B30_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B30_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B30_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B30_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B30_a0.05_k3/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B30_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B30_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B30_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B30_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B30_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B30_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B30_a0.05_k3/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B30_a0.05_k3/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B30_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B30_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B30_a0.05_k3/figures/fig_detection_latency.png`
