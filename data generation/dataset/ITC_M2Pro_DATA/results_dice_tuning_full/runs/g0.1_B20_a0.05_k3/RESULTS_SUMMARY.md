# DICE Full Retrain Results

## Setup
- Feature profile: full ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_full_5hz.csv', 'tier2': 'tier2_full_5hz.csv'})
- Protocol: global, benign-only fit/calibration, block_B=20, alpha=0.05, persist_k=3, gain=0.1
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
           full             tier0       24          46          2.427904   0.7750 0.919734         1.0        1.0           0.25           0.35              0.015544              0.031791                      0.0                 0.016567
           full       tier0_tier1       24          64          3.106372   0.8625 0.970786         1.0        1.0           0.25           0.70              0.025701              0.067620                      0.0                 0.031129
           full tier0_tier1_tier2       24          75          4.349552   0.9875 0.997619         1.0        1.0           0.25           1.00              0.002855              0.007497                      0.0                 0.004604
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc  pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
           full   ATOMIC   0.9375    0.95         1.0        1.0          0.002855          0.006850                  0.0             0.004413       2.399143      0.003996       4413.850065         0.004413
           full   BRANCH   1.0000    1.00         1.0        1.0          0.002855          0.009856                  0.0             0.007193       3.451592      0.007001       7194.014575         0.007193
           full    CACHE   1.0000    1.00         1.0        1.0          0.002855          0.008798                  0.0             0.005766       3.081220      0.005944       5767.019552         0.005766
           full    MEMBW   1.0000    1.00         1.0        1.0          0.002855          0.008488                  0.0             0.004868       2.972682      0.005634       4868.510120         0.004868
           full      TLB   1.0000    1.00         1.0        1.0          0.002855          0.006711                  0.0             0.004530       2.350365      0.003856       4530.907689         0.004530
```

## Paper-style Aggregates (Final Config)
- Base score mean stressor AUC-PR (all five): **0.9900**
- Base score mean stressor ROC-AUC (all five): **0.9875**
- WC score mean stressor AUC-PR (all five): **1.0000**
- WC score mean stressor ROC-AUC (all five): **1.0000**
- Base score mean stressor AUC-PR (excluding BRANCH/TLB): **0.9833**
- Base score mean stressor ROC-AUC (excluding BRANCH/TLB): **0.9792**
- WC score mean stressor AUC-PR (excluding BRANCH/TLB): **1.0000**
- WC score mean stressor ROC-AUC (excluding BRANCH/TLB): **1.0000**

## Diagnosis
- Feature-level diagnosis uses normalized whole-run residual-attribution prototypes as the default paper-facing result, with diagnosis-only filtering that removes monotonic counters and downweights generic memory-state features.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.30       0.5          0.30  0.252727               0.023169                 0.013994            full
      tier0_tier1       20      0.25       0.5          0.25  0.280000               0.015685                 0.015708            full
tier0_tier1_tier2       20      0.30       0.5          0.30  0.251429               0.017909                 0.015799            full
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20       0.3      0.60           0.3  0.260678               0.013100                 0.008894            full
      tier0_tier1       20       0.1      0.25           0.1  0.101587               0.099612                 0.033782            full
tier0_tier1_tier2       20       0.1      0.25           0.1  0.076364               0.031976                 0.029217            full
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.35      0.55          0.35  0.350649               0.017861                 0.012884            full
      tier0_tier1       20      0.40      0.60          0.40  0.348283               0.020106                 0.013726            full
tier0_tier1_tier2       20      0.30      0.55          0.30  0.298730               0.015506                 0.012207            full
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.55      0.90      0.527778  0.434343               0.033342                 0.041977            full
      tier0_tier1       20      0.50      0.90      0.388889  0.412536               0.018342                 0.010809            full
tier0_tier1_tier2       20      0.45      0.95      0.472222  0.503663               0.016324                 0.013550            full
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.35      0.50        0.45          0.35  0.273535      0.40          0.60            0.500000            0.500000                0.400000            0.274286               0.005354                 0.006796            0.016357              0.014942           0.013009        0.124782            full
      tier0_tier1       20      0.30      0.60        0.50          0.30  0.345238      0.75          0.25            0.266667            0.600000                0.283333            0.323810               0.011305                 0.015708            0.024045              0.022411           0.015266        0.029536            full
tier0_tier1_tier2       20      0.20      0.35        0.35          0.20  0.171429      0.65          0.35            0.307692            0.384615                0.300000            0.280000               0.014551                 0.019092            0.019846              0.016837           0.013027        0.043562            full
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20       0.4      0.75        0.45           0.4  0.387143      0.55          0.45            0.363636            0.636364                0.466667            0.370476              -0.014445                 0.003167            0.016357              0.014942           0.013009       -0.060356            full
      tier0_tier1       20       0.2      0.35        0.50           0.2  0.177778      0.30          0.70            0.166667            0.500000                0.200000            0.133333               0.014946                 0.026524            0.024045              0.022411           0.015266        0.518284            full
tier0_tier1_tier2       20       0.2      0.35        0.35           0.2  0.150427      0.55          0.45            0.090909            0.272727                0.066667            0.050000              -0.010201                -0.003716            0.019846              0.016837           0.013027       -0.020963            full
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0  conf_0.00              0.000000      15      0.75          0.25            0.333333            0.400000                0.350000            0.242424            full
            tier0  conf_0.05              0.050000      10      0.50          0.50            0.500000            0.500000                0.350000            0.293333            full
            tier0  conf_0.10              0.100000       6      0.30          0.70            0.500000            0.500000                0.400000            0.260000            full
            tier0    trained              0.124782       5      0.25          0.75            0.600000            0.600000                0.500000            0.293333            full
            tier0  conf_0.15              0.150000       5      0.25          0.75            0.600000            0.600000                0.500000            0.293333            full
            tier0  conf_0.20              0.200000       3      0.15          0.85            0.666667            0.666667                0.500000            0.200000            full
            tier0  conf_0.25              0.250000       3      0.15          0.85            0.666667            0.666667                0.500000            0.200000            full
      tier0_tier1  conf_0.00              0.000000      18      0.90          0.10            0.277778            0.555556                0.300000            0.345714            full
      tier0_tier1    trained              0.029536      14      0.70          0.30            0.285714            0.642857                0.266667            0.296364            full
      tier0_tier1  conf_0.05              0.050000      12      0.60          0.40            0.250000            0.583333                0.200000            0.200000            full
      tier0_tier1  conf_0.10              0.100000       5      0.25          0.75            0.000000            0.600000                0.000000            0.000000            full
      tier0_tier1  conf_0.15              0.150000       2      0.10          0.90            0.000000            1.000000                0.000000            0.000000            full
      tier0_tier1  conf_0.20              0.200000       1      0.05          0.95            0.000000            1.000000                0.000000            0.000000            full
      tier0_tier1  conf_0.25              0.250000       1      0.05          0.95            0.000000            1.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.00              0.000000      17      0.85          0.15            0.235294            0.352941                0.233333            0.226667            full
tier0_tier1_tier2    trained              0.043562      13      0.65          0.35            0.230769            0.384615                0.200000            0.200000            full
tier0_tier1_tier2  conf_0.05              0.050000      13      0.65          0.35            0.230769            0.384615                0.200000            0.200000            full
tier0_tier1_tier2  conf_0.10              0.100000      11      0.55          0.45            0.181818            0.272727                0.100000            0.072727            full
tier0_tier1_tier2  conf_0.15              0.150000       8      0.40          0.60            0.125000            0.250000                0.125000            0.057143            full
tier0_tier1_tier2  conf_0.20              0.200000       3      0.15          0.85            0.000000            0.333333                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.25              0.250000       2      0.10          0.90            0.000000            0.500000                0.000000            0.000000            full
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained             -0.060356      13      0.65          0.35            0.307692            0.692308                0.312500            0.222222            full
            tier0  conf_0.00              0.000000      13      0.65          0.35            0.307692            0.692308                0.312500            0.222222            full
            tier0  conf_0.05              0.050000       6      0.30          0.70            0.333333            0.500000                0.375000            0.266667            full
            tier0  conf_0.10              0.100000       3      0.15          0.85            0.333333            0.333333                0.250000            0.133333            full
            tier0  conf_0.15              0.150000       1      0.05          0.95            1.000000            1.000000                1.000000            0.200000            full
            tier0  conf_0.20              0.200000       1      0.05          0.95            1.000000            1.000000                1.000000            0.200000            full
            tier0  conf_0.25              0.250000       1      0.05          0.95            1.000000            1.000000                1.000000            0.200000            full
      tier0_tier1  conf_0.00              0.000000      17      0.85          0.15            0.176471            0.352941                0.183333            0.171429            full
      tier0_tier1  conf_0.05              0.050000      14      0.70          0.30            0.142857            0.357143                0.166667            0.166667            full
      tier0_tier1  conf_0.10              0.100000      11      0.55          0.45            0.090909            0.363636                0.100000            0.100000            full
      tier0_tier1  conf_0.15              0.150000       7      0.35          0.65            0.000000            0.285714                0.000000            0.000000            full
      tier0_tier1  conf_0.20              0.200000       6      0.30          0.70            0.000000            0.333333                0.000000            0.000000            full
      tier0_tier1  conf_0.25              0.250000       4      0.20          0.80            0.000000            0.500000                0.000000            0.000000            full
      tier0_tier1    trained              0.518284       3      0.15          0.85            0.000000            0.666667                0.000000            0.000000            full
tier0_tier1_tier2    trained             -0.020963      11      0.55          0.45            0.090909            0.181818                0.066667            0.066667            full
tier0_tier1_tier2  conf_0.00              0.000000      10      0.50          0.50            0.000000            0.100000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.05              0.050000       6      0.30          0.70            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.10              0.100000       6      0.30          0.70            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.15              0.150000       5      0.25          0.75            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.20              0.200000       5      0.25          0.75            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.25              0.250000       2      0.10          0.90            0.000000            0.000000                0.000000            0.000000            full
```

## Diagnosis Mode Comparison
- Whole-run and post-alert-window diagnosis are exported together so the diagnosis mode can be evaluated directly.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile diagnosis_target    diagnosis_mode  family_acc  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau                       status  min_class_count  min_group_count    group_key  include_workload
            tier0       20      0.30      0.50      0.300000  0.252727               0.023169                 0.013994            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.25      0.50      0.250000  0.280000               0.015685                 0.015708            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.30      0.50      0.300000  0.251429               0.017909                 0.015799            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.30      0.60      0.300000  0.260678               0.013100                 0.008894            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.10      0.25      0.100000  0.101587               0.099612                 0.033782            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.10      0.25      0.100000  0.076364               0.031976                 0.029217            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.35      0.50      0.350000  0.273535               0.005354                 0.006796            full     hierarchical         whole_run        0.45      0.40          0.60            0.500000            0.500000                0.400000            0.274286            0.016357              0.014942           0.013009        0.124782                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.30      0.60      0.300000  0.345238               0.011305                 0.015708            full     hierarchical         whole_run        0.50      0.75          0.25            0.266667            0.600000                0.283333            0.323810            0.024045              0.022411           0.015266        0.029536                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.20      0.35      0.200000  0.171429               0.014551                 0.019092            full     hierarchical         whole_run        0.35      0.65          0.35            0.307692            0.384615                0.300000            0.280000            0.019846              0.016837           0.013027        0.043562                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.40      0.75      0.400000  0.387143              -0.014445                 0.003167            full     hierarchical post_alert_window        0.45      0.55          0.45            0.363636            0.636364                0.466667            0.370476            0.016357              0.014942           0.013009       -0.060356                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.20      0.35      0.200000  0.177778               0.014946                 0.026524            full     hierarchical post_alert_window        0.50      0.30          0.70            0.166667            0.500000                0.200000            0.133333            0.024045              0.022411           0.015266        0.518284                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.20      0.35      0.200000  0.150427              -0.010201                -0.003716            full     hierarchical post_alert_window        0.35      0.55          0.45            0.090909            0.272727                0.066667            0.050000            0.019846              0.016837           0.013027       -0.020963                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.55      0.90      0.527778  0.434343               0.033342                 0.041977            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.50      0.90      0.388889  0.412536               0.018342                 0.010809            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.45      0.95      0.472222  0.503663               0.016324                 0.013550            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.518877         0.253381     0.227742              tier0            full
  BRANCH     0.562162         0.217181     0.220657              tier0            full
   CACHE     0.411373         0.187104     0.401523              tier0            full
   MEMBW     0.570141         0.224748     0.205112              tier0            full
     TLB     0.491734         0.265848     0.242418              tier0            full
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC                 compute       0.404092         0.259547             0.118740                 0.119088                 0.098533            full
  BRANCH                 compute       0.357703         0.322291             0.087534                 0.164600                 0.067872            full
   CACHE                 compute       0.548673         0.230659             0.073111                 0.087605                 0.059952            full
   MEMBW                 compute       0.381530         0.291987             0.098768                 0.124460                 0.103254            full
     TLB                 compute       0.414017         0.262887             0.116522                 0.124580                 0.081994            full
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
            tier0                   0.25                        2.755102                      4.591837                 0.35                     33.0                 377.8                0.30                0.30                0.30            full
      tier0_tier1                   0.25                        2.755102                      4.591837                 0.70                     30.5                 884.5                0.50                0.50                0.55            full
tier0_tier1_tier2                   0.25                        1.836735                      3.673469                 1.00                     22.0                 641.3                0.75                0.75                0.85            full
```

## Files
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B20_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B20_a0.05_k3/config_runtime_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B20_a0.05_k3/run_context.json`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B20_a0.05_k3/case_inventory.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B20_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B20_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B20_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B20_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B20_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B20_a0.05_k3/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B20_a0.05_k3/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B20_a0.05_k3/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B20_a0.05_k3/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B20_a0.05_k3/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B20_a0.05_k3/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B20_a0.05_k3/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B20_a0.05_k3/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B20_a0.05_k3/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B20_a0.05_k3/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B20_a0.05_k3/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B20_a0.05_k3/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B20_a0.05_k3/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B20_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B20_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B20_a0.05_k3/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B20_a0.05_k3/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B20_a0.05_k3/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B20_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B20_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B20_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B20_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B20_a0.05_k3/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B20_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B20_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B20_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B20_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B20_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B20_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B20_a0.05_k3/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B20_a0.05_k3/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B20_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B20_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B20_a0.05_k3/figures/fig_detection_latency.png`
