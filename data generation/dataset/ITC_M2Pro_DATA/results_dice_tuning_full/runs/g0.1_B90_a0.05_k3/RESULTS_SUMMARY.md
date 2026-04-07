# DICE Full Retrain Results

## Setup
- Feature profile: full ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_full_5hz.csv', 'tier2': 'tier2_full_5hz.csv'})
- Protocol: global, benign-only fit/calibration, block_B=90, alpha=0.05, persist_k=3, gain=0.1
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
           full             tier0       24          46          2.246792   0.7875 0.921899         1.0        1.0            0.0           0.30              0.011990              0.026694                      0.0                 0.014837
           full       tier0_tier1       24          64          2.894420   0.8250 0.951460         1.0        1.0            0.0           0.45              0.018406              0.049372                      0.0                 0.023803
           full tier0_tier1_tier2       24          75          3.450962   0.9625 0.992487         1.0        1.0            0.0           0.95              0.003077              0.008009                      0.0                 0.004996
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc  pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
           full   ATOMIC   0.9375    0.95         1.0        1.0          0.003077          0.008034                  0.0             0.005034       2.610654      0.004957       5035.381180         0.005034
           full   BRANCH   1.0000    1.00         1.0        1.0          0.003077          0.007406                  0.0             0.005344       2.406723      0.004330       5344.803767         0.005344
           full    CACHE   0.9375    0.95         1.0        1.0          0.003077          0.010346                  0.0             0.007240       3.361819      0.007269       7240.588104         0.007240
           full    MEMBW   1.0000    1.00         1.0        1.0          0.003077          0.008854                  0.0             0.005681       2.876989      0.005777       5682.312838         0.005681
           full      TLB   0.9375    0.95         1.0        1.0          0.003077          0.006438                  0.0             0.004260       2.092278      0.003362       4260.950115         0.004260
```

## Paper-style Aggregates (Final Config)
- Base score mean stressor AUC-PR (all five): **0.9700**
- Base score mean stressor ROC-AUC (all five): **0.9625**
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
            tier0       20      0.35      0.60          0.35  0.321429               0.022551                 0.016912            full
      tier0_tier1       20      0.20      0.50          0.20  0.177143               0.016737                 0.014818            full
tier0_tier1_tier2       20      0.30      0.55          0.30  0.251429               0.017370                 0.015833            full
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.15       0.5          0.15  0.151111               0.020194                 0.020269            full
      tier0_tier1       20      0.10       0.4          0.10  0.101587               0.014064                 0.012666            full
tier0_tier1_tier2       20      0.10       0.4          0.10  0.080000               0.018235                 0.012070            full
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.20      0.50          0.20  0.180808               0.024125                  0.02151            full
      tier0_tier1       20      0.55      0.75          0.55  0.560952               0.018853                  0.01415            full
tier0_tier1_tier2       20      0.40      0.50          0.40  0.383175               0.013329                  0.01052            full
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.60      0.85      0.500000  0.421818               0.032658                 0.035832            full
      tier0_tier1       20      0.55      0.90      0.416667  0.438889               0.019515                 0.012604            full
tier0_tier1_tier2       20      0.50      0.95      0.555556  0.556391               0.015748                 0.014906            full
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.20      0.55        0.45          0.20  0.210808      0.60          0.40            0.250000            0.583333                0.233333            0.246667              -0.006411                 0.002514            0.017141              0.015516           0.011790       -0.016482            full
      tier0_tier1       20      0.35      0.60        0.45          0.35  0.378571      0.75          0.25            0.266667            0.533333                0.266667            0.269697               0.010340                 0.013746            0.024738              0.024429           0.016859        0.011945            full
tier0_tier1_tier2       20      0.20      0.40        0.35          0.20  0.157143      0.60          0.40            0.333333            0.583333                0.333333            0.280000               0.013117                 0.015868            0.019437              0.017680           0.008317        0.033452            full
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.20      0.45        0.45          0.20  0.200649      0.70          0.30            0.214286            0.428571                0.200000            0.190476              -0.009702                 0.014315            0.017141              0.015516           0.011790       -0.087669            full
      tier0_tier1       20      0.30      0.55        0.45          0.30  0.283333      0.55          0.45            0.272727            0.454545                0.366667            0.257143               0.002936                 0.009731            0.024738              0.024429           0.016859        0.000000            full
tier0_tier1_tier2       20      0.25      0.35        0.35          0.25  0.207143      0.50          0.50            0.200000            0.300000                0.116667            0.107143              -0.001498                -0.006684            0.019437              0.017680           0.008317       -0.018252            full
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained             -0.016482      14      0.70          0.30            0.214286            0.571429                0.200000            0.223810            full
            tier0  conf_0.00              0.000000      13      0.65          0.35            0.230769            0.538462                0.233333            0.257143            full
            tier0  conf_0.05              0.050000       7      0.35          0.65            0.285714            0.428571                0.333333            0.180000            full
            tier0  conf_0.10              0.100000       6      0.30          0.70            0.333333            0.500000                0.375000            0.200000            full
            tier0  conf_0.15              0.150000       4      0.20          0.80            0.500000            0.750000                0.500000            0.233333            full
            tier0  conf_0.20              0.200000       1      0.05          0.95            1.000000            1.000000                1.000000            0.200000            full
            tier0  conf_0.25              0.250000       1      0.05          0.95            1.000000            1.000000                1.000000            0.200000            full
      tier0_tier1  conf_0.00              0.000000      16      0.80          0.20            0.312500            0.562500                0.316667            0.336364            full
      tier0_tier1    trained              0.011945      15      0.75          0.25            0.266667            0.533333                0.250000            0.236364            full
      tier0_tier1  conf_0.05              0.050000      11      0.55          0.45            0.272727            0.545455                0.233333            0.204444            full
      tier0_tier1  conf_0.10              0.100000       5      0.25          0.75            0.200000            0.800000                0.125000            0.133333            full
      tier0_tier1  conf_0.15              0.150000       2      0.10          0.90            0.000000            1.000000                0.000000            0.000000            full
      tier0_tier1  conf_0.20              0.200000       1      0.05          0.95            0.000000            1.000000                0.000000            0.000000            full
      tier0_tier1  conf_0.25              0.250000       1      0.05          0.95            0.000000            1.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.00              0.000000      16      0.80          0.20            0.250000            0.437500                0.233333            0.226667            full
tier0_tier1_tier2    trained              0.033452      14      0.70          0.30            0.285714            0.500000                0.233333            0.226667            full
tier0_tier1_tier2  conf_0.05              0.050000      13      0.65          0.35            0.230769            0.461538                0.200000            0.200000            full
tier0_tier1_tier2  conf_0.10              0.100000      10      0.50          0.50            0.200000            0.400000                0.133333            0.080000            full
tier0_tier1_tier2  conf_0.15              0.150000       5      0.25          0.75            0.000000            0.400000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.20              0.200000       3      0.15          0.85            0.000000            0.666667                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.25              0.250000       2      0.10          0.90            0.000000            0.500000                0.000000            0.000000            full
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained             -0.087669      14      0.70          0.30            0.214286            0.428571                0.200000            0.190476            full
            tier0  conf_0.00              0.000000      14      0.70          0.30            0.214286            0.428571                0.200000            0.190476            full
            tier0  conf_0.05              0.050000      12      0.60          0.40            0.250000            0.500000                0.266667            0.217143            full
            tier0  conf_0.10              0.100000       9      0.45          0.55            0.222222            0.444444                0.333333            0.200000            full
            tier0  conf_0.15              0.150000       3      0.15          0.85            0.666667            1.000000                0.750000            0.333333            full
            tier0  conf_0.20              0.200000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN            full
            tier0  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN            full
      tier0_tier1    trained              0.000000      15      0.75          0.25            0.200000            0.466667                0.216667            0.196364            full
      tier0_tier1  conf_0.00              0.000000      15      0.75          0.25            0.200000            0.466667                0.216667            0.196364            full
      tier0_tier1  conf_0.05              0.050000       8      0.40          0.60            0.125000            0.375000                0.100000            0.050000            full
      tier0_tier1  conf_0.10              0.100000       3      0.15          0.85            0.333333            0.333333                0.333333            0.133333            full
      tier0_tier1  conf_0.15              0.150000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000            full
      tier0_tier1  conf_0.20              0.200000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000            full
      tier0_tier1  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN            full
tier0_tier1_tier2    trained             -0.018252      10      0.50          0.50            0.300000            0.400000                0.233333            0.257143            full
tier0_tier1_tier2  conf_0.00              0.000000       9      0.45          0.55            0.222222            0.333333                0.133333            0.123810            full
tier0_tier1_tier2  conf_0.05              0.050000       6      0.30          0.70            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.10              0.100000       4      0.20          0.80            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.15              0.150000       3      0.15          0.85            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.20              0.200000       3      0.15          0.85            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.25              0.250000       3      0.15          0.85            0.000000            0.000000                0.000000            0.000000            full
```

## Diagnosis Mode Comparison
- Whole-run and post-alert-window diagnosis are exported together so the diagnosis mode can be evaluated directly.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile diagnosis_target    diagnosis_mode  family_acc  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau                       status  min_class_count  min_group_count    group_key  include_workload
            tier0       20      0.35      0.60      0.350000  0.321429               0.022551                 0.016912            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.20      0.50      0.200000  0.177143               0.016737                 0.014818            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.30      0.55      0.300000  0.251429               0.017370                 0.015833            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.15      0.50      0.150000  0.151111               0.020194                 0.020269            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.10      0.40      0.100000  0.101587               0.014064                 0.012666            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.10      0.40      0.100000  0.080000               0.018235                 0.012070            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.20      0.55      0.200000  0.210808              -0.006411                 0.002514            full     hierarchical         whole_run        0.45      0.60          0.40            0.250000            0.583333                0.233333            0.246667            0.017141              0.015516           0.011790       -0.016482                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.35      0.60      0.350000  0.378571               0.010340                 0.013746            full     hierarchical         whole_run        0.45      0.75          0.25            0.266667            0.533333                0.266667            0.269697            0.024738              0.024429           0.016859        0.011945                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.20      0.40      0.200000  0.157143               0.013117                 0.015868            full     hierarchical         whole_run        0.35      0.60          0.40            0.333333            0.583333                0.333333            0.280000            0.019437              0.017680           0.008317        0.033452                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.20      0.45      0.200000  0.200649              -0.009702                 0.014315            full     hierarchical post_alert_window        0.45      0.70          0.30            0.214286            0.428571                0.200000            0.190476            0.017141              0.015516           0.011790       -0.087669                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.30      0.55      0.300000  0.283333               0.002936                 0.009731            full     hierarchical post_alert_window        0.45      0.55          0.45            0.272727            0.454545                0.366667            0.257143            0.024738              0.024429           0.016859        0.000000                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.25      0.35      0.250000  0.207143              -0.001498                -0.006684            full     hierarchical post_alert_window        0.35      0.50          0.50            0.200000            0.300000                0.116667            0.107143            0.019437              0.017680           0.008317       -0.018252                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.60      0.85      0.500000  0.421818               0.032658                 0.035832            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.55      0.90      0.416667  0.438889               0.019515                 0.012604            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.50      0.95      0.555556  0.556391               0.015748                 0.014906            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.564738         0.246976     0.188285              tier0            full
  BRANCH     0.601597         0.215991     0.182411              tier0            full
   CACHE     0.443760         0.189705     0.366535              tier0            full
   MEMBW     0.615576         0.217813     0.166611              tier0            full
     TLB     0.533757         0.264378     0.201866              tier0            full
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC                 compute       0.378206         0.293963             0.101033                 0.112827                 0.113972            full
  BRANCH                 compute       0.338165         0.362859             0.075059                 0.143192                 0.080725            full
   CACHE                 compute       0.528016         0.262190             0.060741                 0.079183                 0.069870            full
   MEMBW                 compute       0.355597         0.327509             0.083430                 0.113618                 0.119846            full
     TLB                 compute       0.390180         0.301890             0.098984                 0.112992                 0.095955            full
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
            tier0                    0.0                             0.0                           0.0                 0.30                     95.5                 768.5                0.20                0.20                0.20            full
      tier0_tier1                    0.0                             0.0                           0.0                 0.45                     92.0                 700.0                0.30                0.35                0.35            full
tier0_tier1_tier2                    0.0                             0.0                           0.0                 0.95                     92.0                 673.0                0.65                0.65                0.80            full
```

## Files
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B90_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B90_a0.05_k3/config_runtime_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B90_a0.05_k3/run_context.json`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B90_a0.05_k3/case_inventory.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B90_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B90_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B90_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B90_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B90_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B90_a0.05_k3/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B90_a0.05_k3/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B90_a0.05_k3/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B90_a0.05_k3/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B90_a0.05_k3/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B90_a0.05_k3/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B90_a0.05_k3/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B90_a0.05_k3/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B90_a0.05_k3/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B90_a0.05_k3/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B90_a0.05_k3/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B90_a0.05_k3/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B90_a0.05_k3/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B90_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B90_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B90_a0.05_k3/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B90_a0.05_k3/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B90_a0.05_k3/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B90_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B90_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B90_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B90_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B90_a0.05_k3/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B90_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B90_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B90_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B90_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B90_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B90_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B90_a0.05_k3/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B90_a0.05_k3/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B90_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B90_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B90_a0.05_k3/figures/fig_detection_latency.png`
