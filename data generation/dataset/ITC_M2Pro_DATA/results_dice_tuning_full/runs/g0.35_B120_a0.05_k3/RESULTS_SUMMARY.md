# DICE Full Retrain Results

## Setup
- Feature profile: full ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_full_5hz.csv', 'tier2': 'tier2_full_5hz.csv'})
- Protocol: global, benign-only fit/calibration, block_B=120, alpha=0.05, persist_k=3, gain=0.35
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
           full             tier0       24          46          2.372756   0.8000 0.931899         1.0        1.0            0.0            0.3              0.004397              0.010045                      0.0                 0.005804
           full       tier0_tier1       24          64          3.289650   0.7875 0.941423         1.0        1.0            0.0            0.5              0.006493              0.020818                      0.0                 0.010046
           full tier0_tier1_tier2       24          75          3.600683   0.9375 0.986769         1.0        1.0            0.0            0.9              0.002944              0.008386                      0.0                 0.004665
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc  pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
           full   ATOMIC   0.8750  0.8875         1.0        1.0          0.002944          0.008102                  0.0             0.003863       2.751185      0.005158       3864.221981         0.003863
           full   BRANCH   1.0000  1.0000         1.0        1.0          0.002944          0.008159                  0.0             0.005766       2.770532      0.005215       5766.558836         0.005766
           full    CACHE   0.9375  0.9500         1.0        1.0          0.002944          0.010544                  0.0             0.007031       3.580192      0.007600       7032.097992         0.007031
           full    MEMBW   1.0000  1.0000         1.0        1.0          0.002944          0.008967                  0.0             0.005744       3.044816      0.006023       5744.592666         0.005744
           full      TLB   0.8750  0.8875         1.0        1.0          0.002944          0.006815                  0.0             0.004300       2.313921      0.003870       4300.535571         0.004300
```

## Paper-style Aggregates (Final Config)
- Base score mean stressor AUC-PR (all five): **0.9450**
- Base score mean stressor ROC-AUC (all five): **0.9375**
- WC score mean stressor AUC-PR (all five): **1.0000**
- WC score mean stressor ROC-AUC (all five): **1.0000**
- Base score mean stressor AUC-PR (excluding BRANCH/TLB): **0.9458**
- Base score mean stressor ROC-AUC (excluding BRANCH/TLB): **0.9375**
- WC score mean stressor AUC-PR (excluding BRANCH/TLB): **1.0000**
- WC score mean stressor ROC-AUC (excluding BRANCH/TLB): **1.0000**

## Diagnosis
- Feature-level diagnosis uses normalized whole-run residual-attribution prototypes as the default paper-facing result, with diagnosis-only filtering that removes monotonic counters and downweights generic memory-state features.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20       0.4       0.6           0.4  0.322424               0.026294                 0.019490            full
      tier0_tier1       20       0.2       0.3           0.2  0.183333               0.014293                 0.010745            full
tier0_tier1_tier2       20       0.3       0.4           0.3  0.206667               0.027207                 0.020649            full
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.25      0.70          0.25  0.241587               0.017364                 0.015229            full
      tier0_tier1       20      0.25      0.45          0.25  0.236667               0.021779                 0.024618            full
tier0_tier1_tier2       20      0.15      0.35          0.15  0.140000               0.019489                 0.013852            full
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20       0.3      0.60           0.3  0.287619               0.015595                 0.013728            full
      tier0_tier1       20       0.2      0.55           0.2  0.152727               0.022022                 0.020947            full
tier0_tier1_tier2       20       0.3      0.55           0.3  0.241616               0.013486                 0.008504            full
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.60      0.80      0.500000  0.421818               0.037200                 0.037432            full
      tier0_tier1       20      0.45      0.70      0.361111  0.305463               0.024353                 0.028978            full
tier0_tier1_tier2       20      0.55      0.95      0.638889  0.542328               0.020415                 0.016356            full
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.30       0.6        0.40          0.30  0.286667      0.50          0.50            0.400000            0.600000                0.433333            0.360000               0.006017                 0.010779            0.014441              0.010418           0.010614        0.060118            full
      tier0_tier1       20      0.20       0.4        0.50          0.20  0.197143      0.80          0.20            0.187500            0.312500                0.200000            0.173810               0.003094                 0.006881            0.023719              0.026936           0.012932       -0.054045            full
tier0_tier1_tier2       20      0.25       0.4        0.35          0.25  0.180000      0.75          0.25            0.266667            0.333333                0.250000            0.172308               0.016066                 0.019380            0.019549              0.017539           0.005258        0.074341            full
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.25      0.70        0.40          0.25  0.220269      0.85          0.15            0.235294            0.705882                0.233333            0.208730               0.005787                 0.015229            0.014441              0.010418           0.010614       -0.016288            full
      tier0_tier1       20      0.25      0.45        0.50          0.25  0.258205      0.55          0.45            0.272727            0.363636                0.266667            0.290476              -0.009980                 0.003924            0.023719              0.026936           0.012932        0.019141            full
tier0_tier1_tier2       20      0.25      0.35        0.35          0.25  0.185714      0.80          0.20            0.187500            0.250000                0.200000            0.139394               0.003191                 0.009228            0.019549              0.017539           0.005258       -0.109613            full
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0  conf_0.00              0.000000      14      0.70          0.30            0.357143            0.571429                0.433333            0.327619            full
            tier0  conf_0.05              0.050000      11      0.55          0.45            0.363636            0.545455                0.333333            0.214286            full
            tier0    trained              0.060118      10      0.50          0.50            0.400000            0.600000                0.333333            0.228571            full
            tier0  conf_0.10              0.100000       8      0.40          0.60            0.250000            0.500000                0.166667            0.114286            full
            tier0  conf_0.15              0.150000       6      0.30          0.70            0.333333            0.500000                0.166667            0.114286            full
            tier0  conf_0.20              0.200000       4      0.20          0.80            0.500000            0.750000                0.333333            0.133333            full
            tier0  conf_0.25              0.250000       4      0.20          0.80            0.500000            0.750000                0.333333            0.133333            full
      tier0_tier1    trained             -0.054045      15      0.75          0.25            0.200000            0.333333                0.200000            0.173810            full
      tier0_tier1  conf_0.00              0.000000      14      0.70          0.30            0.142857            0.285714                0.133333            0.123810            full
      tier0_tier1  conf_0.05              0.050000       7      0.35          0.65            0.000000            0.285714                0.000000            0.000000            full
      tier0_tier1  conf_0.10              0.100000       6      0.30          0.70            0.000000            0.333333                0.000000            0.000000            full
      tier0_tier1  conf_0.15              0.150000       5      0.25          0.75            0.000000            0.200000                0.000000            0.000000            full
      tier0_tier1  conf_0.20              0.200000       2      0.10          0.90            0.000000            0.000000                0.000000            0.000000            full
      tier0_tier1  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN            full
tier0_tier1_tier2  conf_0.00              0.000000      17      0.85          0.15            0.235294            0.352941                0.250000            0.172308            full
tier0_tier1_tier2  conf_0.05              0.050000      14      0.70          0.30            0.285714            0.428571                0.300000            0.200000            full
tier0_tier1_tier2    trained              0.074341      13      0.65          0.35            0.307692            0.461538                0.300000            0.233333            full
tier0_tier1_tier2  conf_0.10              0.100000      11      0.55          0.45            0.272727            0.454545                0.200000            0.100000            full
tier0_tier1_tier2  conf_0.15              0.150000       5      0.25          0.75            0.200000            0.200000                0.250000            0.066667            full
tier0_tier1_tier2  conf_0.20              0.200000       5      0.25          0.75            0.200000            0.200000                0.250000            0.066667            full
tier0_tier1_tier2  conf_0.25              0.250000       2      0.10          0.90            0.000000            0.000000                0.000000            0.000000            full
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained             -0.016288      16      0.80          0.20            0.250000            0.687500                0.233333            0.214286            full
            tier0  conf_0.00              0.000000      16      0.80          0.20            0.250000            0.687500                0.233333            0.214286            full
            tier0  conf_0.05              0.050000      16      0.80          0.20            0.250000            0.687500                0.233333            0.214286            full
            tier0  conf_0.10              0.100000       9      0.45          0.55            0.111111            0.666667                0.100000            0.080000            full
            tier0  conf_0.15              0.150000       6      0.30          0.70            0.166667            0.666667                0.125000            0.100000            full
            tier0  conf_0.20              0.200000       4      0.20          0.80            0.250000            0.750000                0.250000            0.133333            full
            tier0  conf_0.25              0.250000       2      0.10          0.90            0.000000            1.000000                0.000000            0.000000            full
      tier0_tier1  conf_0.00              0.000000      12      0.60          0.40            0.250000            0.416667                0.266667            0.257143            full
      tier0_tier1    trained              0.019141      11      0.55          0.45            0.272727            0.454545                0.266667            0.266667            full
      tier0_tier1  conf_0.05              0.050000       6      0.30          0.70            0.166667            0.333333                0.200000            0.100000            full
      tier0_tier1  conf_0.10              0.100000       6      0.30          0.70            0.166667            0.333333                0.200000            0.100000            full
      tier0_tier1  conf_0.15              0.150000       5      0.25          0.75            0.000000            0.200000                0.000000            0.000000            full
      tier0_tier1  conf_0.20              0.200000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000            full
      tier0_tier1  conf_0.25              0.250000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2    trained             -0.109613      17      0.85          0.15            0.235294            0.294118                0.233333            0.180000            full
tier0_tier1_tier2  conf_0.00              0.000000      14      0.70          0.30            0.214286            0.285714                0.233333            0.180952            full
tier0_tier1_tier2  conf_0.05              0.050000       8      0.40          0.60            0.250000            0.250000                0.300000            0.233333            full
tier0_tier1_tier2  conf_0.10              0.100000       6      0.30          0.70            0.333333            0.333333                0.300000            0.233333            full
tier0_tier1_tier2  conf_0.15              0.150000       3      0.15          0.85            0.333333            0.333333                0.250000            0.133333            full
tier0_tier1_tier2  conf_0.20              0.200000       2      0.10          0.90            0.500000            0.500000                0.500000            0.200000            full
tier0_tier1_tier2  conf_0.25              0.250000       2      0.10          0.90            0.500000            0.500000                0.500000            0.200000            full
```

## Diagnosis Mode Comparison
- Whole-run and post-alert-window diagnosis are exported together so the diagnosis mode can be evaluated directly.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile diagnosis_target    diagnosis_mode  family_acc  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau                       status  min_class_count  min_group_count    group_key  include_workload
            tier0       20      0.40      0.60      0.400000  0.322424               0.026294                 0.019490            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.20      0.30      0.200000  0.183333               0.014293                 0.010745            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.30      0.40      0.300000  0.206667               0.027207                 0.020649            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.25      0.70      0.250000  0.241587               0.017364                 0.015229            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.25      0.45      0.250000  0.236667               0.021779                 0.024618            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.15      0.35      0.150000  0.140000               0.019489                 0.013852            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.30      0.60      0.300000  0.286667               0.006017                 0.010779            full     hierarchical         whole_run        0.40      0.50          0.50            0.400000            0.600000                0.433333            0.360000            0.014441              0.010418           0.010614        0.060118                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.20      0.40      0.200000  0.197143               0.003094                 0.006881            full     hierarchical         whole_run        0.50      0.80          0.20            0.187500            0.312500                0.200000            0.173810            0.023719              0.026936           0.012932       -0.054045                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.25      0.40      0.250000  0.180000               0.016066                 0.019380            full     hierarchical         whole_run        0.35      0.75          0.25            0.266667            0.333333                0.250000            0.172308            0.019549              0.017539           0.005258        0.074341                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.25      0.70      0.250000  0.220269               0.005787                 0.015229            full     hierarchical post_alert_window        0.40      0.85          0.15            0.235294            0.705882                0.233333            0.208730            0.014441              0.010418           0.010614       -0.016288                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.25      0.45      0.250000  0.258205              -0.009980                 0.003924            full     hierarchical post_alert_window        0.50      0.55          0.45            0.272727            0.363636                0.266667            0.290476            0.023719              0.026936           0.012932        0.019141                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.25      0.35      0.250000  0.185714               0.003191                 0.009228            full     hierarchical post_alert_window        0.35      0.80          0.20            0.187500            0.250000                0.200000            0.139394            0.019549              0.017539           0.005258       -0.109613                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.60      0.80      0.500000  0.421818               0.037200                 0.037432            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.45      0.70      0.361111  0.305463               0.024353                 0.028978            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.55      0.95      0.638889  0.542328               0.020415                 0.016356            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.626467         0.267322     0.106211              tier0            full
  BRANCH     0.655867         0.219857     0.124275              tier0            full
   CACHE     0.529327         0.212243     0.258429              tier0            full
   MEMBW     0.668188         0.238326     0.093486              tier0            full
     TLB     0.602454         0.279432     0.118114              tier0            full
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC               memory_io       0.320203         0.346179             0.092640                 0.117710                 0.123268            full
  BRANCH               memory_io       0.289078         0.412375             0.067527                 0.142160                 0.088860            full
   CACHE               memory_io       0.440265         0.334770             0.059328                 0.087726                 0.077911            full
   MEMBW               memory_io       0.294245         0.387883             0.087487                 0.114760                 0.115624            full
     TLB               memory_io       0.317860         0.368700             0.095428                 0.117131                 0.100880            full
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
            tier0                    0.0                             0.0                           0.0                  0.3                    122.0                 642.5                 0.0                0.20                0.25            full
      tier0_tier1                    0.0                             0.0                           0.0                  0.5                    122.0                 691.3                 0.0                0.35                0.40            full
tier0_tier1_tier2                    0.0                             0.0                           0.0                  0.9                    122.0                 727.3                 0.0                0.60                0.70            full
```

## Files
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B120_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B120_a0.05_k3/config_runtime_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B120_a0.05_k3/run_context.json`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B120_a0.05_k3/case_inventory.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B120_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B120_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B120_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B120_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B120_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B120_a0.05_k3/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B120_a0.05_k3/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B120_a0.05_k3/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B120_a0.05_k3/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B120_a0.05_k3/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B120_a0.05_k3/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B120_a0.05_k3/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B120_a0.05_k3/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B120_a0.05_k3/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B120_a0.05_k3/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B120_a0.05_k3/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B120_a0.05_k3/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B120_a0.05_k3/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B120_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B120_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B120_a0.05_k3/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B120_a0.05_k3/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B120_a0.05_k3/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B120_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B120_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B120_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B120_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B120_a0.05_k3/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B120_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B120_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B120_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B120_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B120_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B120_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B120_a0.05_k3/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B120_a0.05_k3/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B120_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B120_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B120_a0.05_k3/figures/fig_detection_latency.png`
