# DICE Full Retrain Results

## Setup
- Feature profile: full ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_full_5hz.csv', 'tier2': 'tier2_full_5hz.csv'})
- Protocol: global, benign-only fit/calibration, block_B=30, alpha=0.05, persist_k=3, gain=0.35
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
           full             tier0       24          46          2.440357   0.7875 0.921899         1.0        1.0           0.25           0.30              0.006307              0.012545                      0.0                 0.006902
           full       tier0_tier1       24          64          3.145664   0.8250 0.955040         1.0        1.0           0.25           0.65              0.009985              0.027018                      0.0                 0.011987
           full tier0_tier1_tier2       24          75          3.723509   0.9500 0.989710         1.0        1.0           0.25           0.95              0.002788              0.007712                      0.0                 0.004213
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc  pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
           full   ATOMIC   0.9375    0.95         1.0        1.0          0.002788          0.006806                  0.0             0.003173       2.440222      0.004017       3174.302957         0.003173
           full   BRANCH   0.9375    0.95         1.0        1.0          0.002788          0.010143                  0.0             0.006930       3.636508      0.007354       6931.101438         0.006930
           full    CACHE   0.9375    0.95         1.0        1.0          0.002788          0.008744                  0.0             0.005431       3.135136      0.005956       5431.990436         0.005431
           full    MEMBW   1.0000    1.00         1.0        1.0          0.002788          0.007998                  0.0             0.004547       2.867658      0.005210       4548.124296         0.004547
           full      TLB   0.9375    0.95         1.0        1.0          0.002788          0.007576                  0.0             0.004728       2.716331      0.004788       4728.887908         0.004728
```

## Paper-style Aggregates (Final Config)
- Base score mean stressor AUC-PR (all five): **0.9600**
- Base score mean stressor ROC-AUC (all five): **0.9500**
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
            tier0       20      0.40       0.6          0.40  0.339091               0.024473                 0.019596            full
      tier0_tier1       20      0.25       0.4          0.25  0.190476               0.013210                 0.009802            full
tier0_tier1_tier2       20      0.30       0.4          0.30  0.200000               0.022003                 0.023027            full
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.30      0.55          0.30  0.281457               0.020023                 0.013969            full
      tier0_tier1       20      0.15      0.35          0.15  0.137143               0.104352                 0.048285            full
tier0_tier1_tier2       20      0.10      0.30          0.10  0.076364               0.015621                 0.013180            full
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.30      0.55          0.30  0.310173               0.012906                 0.010954            full
      tier0_tier1       20      0.25      0.50          0.25  0.180000               0.020937                 0.017730            full
tier0_tier1_tier2       20      0.30      0.60          0.30  0.244444               0.016028                 0.012663            full
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.55      0.85      0.472222  0.398551               0.032858                 0.033861            full
      tier0_tier1       20      0.45      0.75      0.361111  0.305463               0.024710                 0.028113            full
tier0_tier1_tier2       20      0.50      0.90      0.611111  0.501307               0.016101                 0.015492            full
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.45      0.65        0.35          0.45  0.435556      0.35          0.65            0.571429            0.714286                0.533333                0.46               0.013746                 0.012012            0.009994              0.009015           0.011759        0.172589            full
      tier0_tier1       20      0.20      0.55        0.55          0.20  0.190476      0.40          0.60            0.250000            0.500000                0.266667                0.30              -0.003141                 0.003432            0.018969              0.018102           0.010476        0.030576            full
tier0_tier1_tier2       20      0.25      0.40        0.45          0.25  0.175000      0.60          0.40            0.250000            0.333333                0.333333                0.18               0.014734                 0.017613            0.020218              0.016832           0.010565        0.093666            full
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.40      0.55        0.35          0.40  0.382698      0.60          0.40            0.250000            0.416667                0.266667            0.223810              -0.002173                 0.009186            0.009994              0.009015           0.011759       -0.027587            full
      tier0_tier1       20      0.20      0.40        0.55          0.20  0.150427      0.35          0.65            0.000000            0.571429                0.000000            0.000000              -0.009637                 0.007052            0.018969              0.018102           0.010476        0.165449            full
tier0_tier1_tier2       20      0.25      0.40        0.45          0.25  0.185714      0.70          0.30            0.142857            0.357143                0.133333            0.072727              -0.005156                 0.003569            0.020218              0.016832           0.010565       -0.174003            full
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0  conf_0.00              0.000000      16      0.80          0.20            0.437500            0.625000                0.450000            0.413333            full
            tier0  conf_0.05              0.050000      13      0.65          0.35            0.461538            0.692308                0.483333            0.422222            full
            tier0  conf_0.10              0.100000       7      0.35          0.65            0.571429            0.714286                0.416667            0.233333            full
            tier0  conf_0.15              0.150000       5      0.25          0.75            0.600000            0.800000                0.375000            0.150000            full
            tier0    trained              0.172589       5      0.25          0.75            0.600000            0.800000                0.375000            0.150000            full
            tier0  conf_0.20              0.200000       5      0.25          0.75            0.600000            0.800000                0.375000            0.150000            full
            tier0  conf_0.25              0.250000       5      0.25          0.75            0.600000            0.800000                0.375000            0.150000            full
      tier0_tier1  conf_0.00              0.000000      13      0.65          0.35            0.153846            0.461538                0.166667            0.146667            full
      tier0_tier1    trained              0.030576       9      0.45          0.55            0.111111            0.444444                0.100000            0.080000            full
      tier0_tier1  conf_0.05              0.050000       7      0.35          0.65            0.000000            0.428571                0.000000            0.000000            full
      tier0_tier1  conf_0.10              0.100000       5      0.25          0.75            0.000000            0.200000                0.000000            0.000000            full
      tier0_tier1  conf_0.15              0.150000       2      0.10          0.90            0.000000            0.000000                0.000000            0.000000            full
      tier0_tier1  conf_0.20              0.200000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000            full
      tier0_tier1  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN            full
tier0_tier1_tier2  conf_0.00              0.000000      17      0.85          0.15            0.235294            0.352941                0.250000            0.165714            full
tier0_tier1_tier2  conf_0.05              0.050000      16      0.80          0.20            0.250000            0.375000                0.250000            0.172308            full
tier0_tier1_tier2    trained              0.093666      11      0.55          0.45            0.272727            0.454545                0.200000            0.100000            full
tier0_tier1_tier2  conf_0.10              0.100000      11      0.55          0.45            0.272727            0.454545                0.200000            0.100000            full
tier0_tier1_tier2  conf_0.15              0.150000       7      0.35          0.65            0.142857            0.428571                0.250000            0.057143            full
tier0_tier1_tier2  conf_0.20              0.200000       3      0.15          0.85            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.25              0.250000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000            full
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained             -0.027587      16      0.80          0.20            0.375000            0.500000                0.400000            0.387143            full
            tier0  conf_0.00              0.000000      15      0.75          0.25            0.333333            0.466667                0.333333            0.307143            full
            tier0  conf_0.05              0.050000      10      0.50          0.50            0.400000            0.600000                0.450000            0.426667            full
            tier0  conf_0.10              0.100000       7      0.35          0.65            0.428571            0.571429                0.500000            0.380000            full
            tier0  conf_0.15              0.150000       4      0.20          0.80            0.500000            0.500000                0.500000            0.266667            full
            tier0  conf_0.20              0.200000       3      0.15          0.85            0.666667            0.666667                0.666667            0.333333            full
            tier0  conf_0.25              0.250000       2      0.10          0.90            0.500000            0.500000                0.500000            0.133333            full
      tier0_tier1  conf_0.00              0.000000      11      0.55          0.45            0.181818            0.454545                0.133333            0.100000            full
      tier0_tier1  conf_0.05              0.050000       9      0.45          0.55            0.111111            0.444444                0.125000            0.080000            full
      tier0_tier1  conf_0.10              0.100000       7      0.35          0.65            0.000000            0.428571                0.000000            0.000000            full
      tier0_tier1  conf_0.15              0.150000       7      0.35          0.65            0.000000            0.428571                0.000000            0.000000            full
      tier0_tier1    trained              0.165449       7      0.35          0.65            0.000000            0.428571                0.000000            0.000000            full
      tier0_tier1  conf_0.20              0.200000       6      0.30          0.70            0.000000            0.333333                0.000000            0.000000            full
      tier0_tier1  conf_0.25              0.250000       5      0.25          0.75            0.000000            0.400000                0.000000            0.000000            full
tier0_tier1_tier2    trained             -0.174003      19      0.95          0.05            0.263158            0.421053                0.250000            0.200000            full
tier0_tier1_tier2  conf_0.00              0.000000      11      0.55          0.45            0.090909            0.272727                0.100000            0.057143            full
tier0_tier1_tier2  conf_0.05              0.050000       6      0.30          0.70            0.000000            0.166667                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.10              0.100000       2      0.10          0.90            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.15              0.150000       2      0.10          0.90            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.20              0.200000       2      0.10          0.90            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.25              0.250000       2      0.10          0.90            0.000000            0.000000                0.000000            0.000000            full
```

## Diagnosis Mode Comparison
- Whole-run and post-alert-window diagnosis are exported together so the diagnosis mode can be evaluated directly.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile diagnosis_target    diagnosis_mode  family_acc  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau                       status  min_class_count  min_group_count    group_key  include_workload
            tier0       20      0.40      0.60      0.400000  0.339091               0.024473                 0.019596            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.25      0.40      0.250000  0.190476               0.013210                 0.009802            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.30      0.40      0.300000  0.200000               0.022003                 0.023027            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.30      0.55      0.300000  0.281457               0.020023                 0.013969            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.15      0.35      0.150000  0.137143               0.104352                 0.048285            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.10      0.30      0.100000  0.076364               0.015621                 0.013180            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.45      0.65      0.450000  0.435556               0.013746                 0.012012            full     hierarchical         whole_run        0.35      0.35          0.65            0.571429            0.714286                0.533333            0.460000            0.009994              0.009015           0.011759        0.172589                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.20      0.55      0.200000  0.190476              -0.003141                 0.003432            full     hierarchical         whole_run        0.55      0.40          0.60            0.250000            0.500000                0.266667            0.300000            0.018969              0.018102           0.010476        0.030576                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.25      0.40      0.250000  0.175000               0.014734                 0.017613            full     hierarchical         whole_run        0.45      0.60          0.40            0.250000            0.333333                0.333333            0.180000            0.020218              0.016832           0.010565        0.093666                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.40      0.55      0.400000  0.382698              -0.002173                 0.009186            full     hierarchical post_alert_window        0.35      0.60          0.40            0.250000            0.416667                0.266667            0.223810            0.009994              0.009015           0.011759       -0.027587                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.20      0.40      0.200000  0.150427              -0.009637                 0.007052            full     hierarchical post_alert_window        0.55      0.35          0.65            0.000000            0.571429                0.000000            0.000000            0.018969              0.018102           0.010476        0.165449                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.25      0.40      0.250000  0.185714              -0.005156                 0.003569            full     hierarchical post_alert_window        0.45      0.70          0.30            0.142857            0.357143                0.133333            0.072727            0.020218              0.016832           0.010565       -0.174003                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.55      0.85      0.472222  0.398551               0.032858                 0.033861            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.45      0.75      0.361111  0.305463               0.024710                 0.028113            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.50      0.90      0.611111  0.501307               0.016101                 0.015492            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.599562         0.268840     0.131598              tier0            full
  BRANCH     0.630815         0.216346     0.152839              tier0            full
   CACHE     0.504990         0.203951     0.291059              tier0            full
   MEMBW     0.640486         0.243001     0.116513              tier0            full
     TLB     0.576485         0.277451     0.146065              tier0            full
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC                 compute       0.345601         0.305929             0.112471                 0.131854                 0.104146            full
  BRANCH               memory_io       0.309614         0.365967             0.081641                 0.166973                 0.075806            full
   CACHE                 compute       0.470538         0.292489             0.072051                 0.098630                 0.066292            full
   MEMBW               memory_io       0.317852         0.348045             0.104916                 0.129172                 0.100015            full
     TLB                 compute       0.341840         0.321899             0.115892                 0.134565                 0.085805            full
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
            tier0                   0.25                        0.927835                      2.783505                 0.30                     52.5                 603.5                0.20                0.20                0.25            full
      tier0_tier1                   0.25                        0.927835                      2.783505                 0.65                     36.0                 753.4                0.45                0.45                0.55            full
tier0_tier1_tier2                   0.25                        0.927835                      2.783505                 0.95                     32.0                 770.0                0.65                0.65                0.75            full
```

## Files
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B30_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B30_a0.05_k3/config_runtime_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B30_a0.05_k3/run_context.json`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B30_a0.05_k3/case_inventory.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B30_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B30_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B30_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B30_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B30_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B30_a0.05_k3/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B30_a0.05_k3/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B30_a0.05_k3/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B30_a0.05_k3/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B30_a0.05_k3/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B30_a0.05_k3/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B30_a0.05_k3/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B30_a0.05_k3/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B30_a0.05_k3/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B30_a0.05_k3/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B30_a0.05_k3/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B30_a0.05_k3/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B30_a0.05_k3/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B30_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B30_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B30_a0.05_k3/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B30_a0.05_k3/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B30_a0.05_k3/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B30_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B30_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B30_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B30_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B30_a0.05_k3/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B30_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B30_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B30_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B30_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B30_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B30_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B30_a0.05_k3/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B30_a0.05_k3/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B30_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B30_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B30_a0.05_k3/figures/fig_detection_latency.png`
