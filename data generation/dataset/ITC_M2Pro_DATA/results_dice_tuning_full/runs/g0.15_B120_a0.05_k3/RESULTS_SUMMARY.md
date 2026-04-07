# DICE Full Retrain Results

## Setup
- Feature profile: full ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_full_5hz.csv', 'tier2': 'tier2_full_5hz.csv'})
- Protocol: global, benign-only fit/calibration, block_B=120, alpha=0.05, persist_k=3, gain=0.15
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
           full             tier0       24          46          2.237420   0.7875 0.921899         1.0        1.0            0.0            0.3              0.008313              0.019020                      0.0                 0.011024
           full       tier0_tier1       24          64          2.762618   0.8000 0.947673         1.0        1.0            0.0            0.5              0.012724              0.035535                      0.0                 0.017454
           full tier0_tier1_tier2       24          75          3.369860   0.9500 0.989710         1.0        1.0            0.0            0.9              0.003257              0.008470                      0.0                 0.005250
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc  pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
           full   ATOMIC   0.9375  0.9500         1.0        1.0          0.003257          0.008720                  0.0             0.005049       2.676766      0.005463       5050.193144         0.005049
           full   BRANCH   1.0000  1.0000         1.0        1.0          0.003257          0.008017                  0.0             0.005780       2.460935      0.004760       5780.692918         0.005780
           full    CACHE   0.8750  0.8875         1.0        1.0          0.003257          0.011281                  0.0             0.007861       3.462712      0.008024       7861.961528         0.007861
           full    MEMBW   1.0000  1.0000         1.0        1.0          0.003257          0.009619                  0.0             0.005998       2.952746      0.006362       5999.112053         0.005998
           full      TLB   0.9375  0.9500         1.0        1.0          0.003257          0.007113                  0.0             0.004616       2.183409      0.003856       4617.108849         0.004616
```

## Paper-style Aggregates (Final Config)
- Base score mean stressor AUC-PR (all five): **0.9575**
- Base score mean stressor ROC-AUC (all five): **0.9500**
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
            tier0       20      0.35      0.55          0.35  0.306234               0.028197                 0.023666            full
      tier0_tier1       20      0.25      0.60          0.25  0.257143               0.015708                 0.013080            full
tier0_tier1_tier2       20      0.30      0.55          0.30  0.220952               0.020780                 0.017267            full
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.10      0.60          0.10  0.076364               0.018010                 0.009924            full
      tier0_tier1       20      0.20      0.45          0.20  0.211722               0.021158                 0.008997            full
tier0_tier1_tier2       20      0.15      0.35          0.15  0.137951               0.016921                 0.015046            full
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.20      0.55          0.20  0.180808               0.020531                 0.020687            full
      tier0_tier1       20      0.35      0.65          0.35  0.330505               0.017530                 0.011824            full
tier0_tier1_tier2       20      0.45      0.65          0.45  0.416508               0.012725                 0.009966            full
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20       0.6      0.85      0.500000  0.421818               0.038620                 0.039412            full
      tier0_tier1       20       0.5      0.85      0.444444  0.447343               0.017563                 0.009417            full
tier0_tier1_tier2       20       0.6      0.90      0.722222  0.623856               0.016121                 0.013079            full
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.30      0.50        0.50          0.30  0.295556      0.40          0.60            0.250000            0.375000                0.300000            0.266667              -0.010040                 0.002182            0.017115              0.017564           0.011609        0.054628            full
      tier0_tier1       20      0.35      0.65        0.50          0.35  0.352698      0.80          0.20            0.312500            0.625000                0.316667            0.334921               0.009030                 0.011889            0.025746              0.025270           0.012315       -0.021043            full
tier0_tier1_tier2       20      0.25      0.55        0.35          0.25  0.180000      0.75          0.25            0.266667            0.533333                0.266667            0.206061               0.014642                 0.016379            0.020310              0.018852           0.007696        0.021770            full
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.25       0.6        0.50          0.25  0.231111      0.65          0.35            0.230769            0.692308                    0.20            0.168889              -0.015668                 0.004746            0.017115              0.017564           0.011609       -0.038478            full
      tier0_tier1       20      0.35       0.6        0.50          0.35  0.317094      0.70          0.30            0.285714            0.500000                    0.25            0.213333               0.008245                 0.006193            0.025746              0.025270           0.012315        0.017340            full
tier0_tier1_tier2       20      0.30       0.4        0.35          0.30  0.237143      0.60          0.40            0.250000            0.333333                    0.20            0.139394              -0.001367                 0.001666            0.020310              0.018852           0.007696        0.000724            full
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0  conf_0.00              0.000000      11      0.55          0.45            0.363636            0.454545                0.333333            0.314286            full
            tier0  conf_0.05              0.050000       6      0.30          0.70            0.333333            0.333333                0.375000            0.233333            full
            tier0    trained              0.054628       6      0.30          0.70            0.333333            0.333333                0.375000            0.233333            full
            tier0  conf_0.10              0.100000       6      0.30          0.70            0.333333            0.333333                0.375000            0.233333            full
            tier0  conf_0.15              0.150000       5      0.25          0.75            0.400000            0.400000                0.500000            0.266667            full
            tier0  conf_0.20              0.200000       2      0.10          0.90            0.500000            0.500000                0.500000            0.133333            full
            tier0  conf_0.25              0.250000       2      0.10          0.90            0.500000            0.500000                0.500000            0.133333            full
      tier0_tier1    trained             -0.021043      14      0.70          0.30            0.285714            0.571429                0.283333            0.291111            full
      tier0_tier1  conf_0.00              0.000000      14      0.70          0.30            0.285714            0.571429                0.283333            0.291111            full
      tier0_tier1  conf_0.05              0.050000      11      0.55          0.45            0.272727            0.636364                0.266667            0.237143            full
      tier0_tier1  conf_0.10              0.100000       5      0.25          0.75            0.200000            0.600000                0.125000            0.133333            full
      tier0_tier1  conf_0.15              0.150000       2      0.10          0.90            0.000000            0.500000                0.000000            0.000000            full
      tier0_tier1  conf_0.20              0.200000       1      0.05          0.95            0.000000            1.000000                0.000000            0.000000            full
      tier0_tier1  conf_0.25              0.250000       1      0.05          0.95            0.000000            1.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.00              0.000000      16      0.80          0.20            0.250000            0.562500                0.250000            0.192308            full
tier0_tier1_tier2    trained              0.021770      14      0.70          0.30            0.285714            0.642857                0.250000            0.192308            full
tier0_tier1_tier2  conf_0.05              0.050000      12      0.60          0.40            0.333333            0.750000                0.300000            0.233333            full
tier0_tier1_tier2  conf_0.10              0.100000      10      0.50          0.50            0.300000            0.700000                0.300000            0.213333            full
tier0_tier1_tier2  conf_0.15              0.150000       5      0.25          0.75            0.000000            0.400000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.20              0.200000       3      0.15          0.85            0.000000            0.333333                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.25              0.250000       2      0.10          0.90            0.000000            0.500000                0.000000            0.000000            full
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained             -0.038478      13      0.65          0.35            0.230769            0.692308                0.200000            0.168889            full
            tier0  conf_0.00              0.000000      13      0.65          0.35            0.230769            0.692308                0.200000            0.168889            full
            tier0  conf_0.05              0.050000       7      0.35          0.65            0.285714            0.857143                0.200000            0.133333            full
            tier0  conf_0.10              0.100000       4      0.20          0.80            0.250000            0.750000                0.333333            0.133333            full
            tier0  conf_0.15              0.150000       2      0.10          0.90            0.000000            0.500000                0.000000            0.000000            full
            tier0  conf_0.20              0.200000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000            full
            tier0  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN            full
      tier0_tier1  conf_0.00              0.000000      13      0.65          0.35            0.307692            0.538462                0.316667            0.239394            full
      tier0_tier1    trained              0.017340      12      0.60          0.40            0.250000            0.500000                0.250000            0.139394            full
      tier0_tier1  conf_0.05              0.050000       8      0.40          0.60            0.375000            0.625000                0.266667            0.188889            full
      tier0_tier1  conf_0.10              0.100000       6      0.30          0.70            0.333333            0.500000                0.200000            0.100000            full
      tier0_tier1  conf_0.15              0.150000       5      0.25          0.75            0.200000            0.400000                0.200000            0.066667            full
      tier0_tier1  conf_0.20              0.200000       4      0.20          0.80            0.000000            0.250000                0.000000            0.000000            full
      tier0_tier1  conf_0.25              0.250000       4      0.20          0.80            0.000000            0.250000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.00              0.000000      11      0.55          0.45            0.272727            0.363636                0.183333            0.146032            full
tier0_tier1_tier2    trained              0.000724      11      0.55          0.45            0.272727            0.363636                0.183333            0.146032            full
tier0_tier1_tier2  conf_0.05              0.050000       6      0.30          0.70            0.166667            0.166667                0.125000            0.080000            full
tier0_tier1_tier2  conf_0.10              0.100000       4      0.20          0.80            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.15              0.150000       3      0.15          0.85            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.20              0.200000       2      0.10          0.90            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.25              0.250000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000            full
```

## Diagnosis Mode Comparison
- Whole-run and post-alert-window diagnosis are exported together so the diagnosis mode can be evaluated directly.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile diagnosis_target    diagnosis_mode  family_acc  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau                       status  min_class_count  min_group_count    group_key  include_workload
            tier0       20      0.35      0.55      0.350000  0.306234               0.028197                 0.023666            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.25      0.60      0.250000  0.257143               0.015708                 0.013080            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.30      0.55      0.300000  0.220952               0.020780                 0.017267            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.10      0.60      0.100000  0.076364               0.018010                 0.009924            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.20      0.45      0.200000  0.211722               0.021158                 0.008997            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.15      0.35      0.150000  0.137951               0.016921                 0.015046            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.30      0.50      0.300000  0.295556              -0.010040                 0.002182            full     hierarchical         whole_run        0.50      0.40          0.60            0.250000            0.375000                0.300000            0.266667            0.017115              0.017564           0.011609        0.054628                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.35      0.65      0.350000  0.352698               0.009030                 0.011889            full     hierarchical         whole_run        0.50      0.80          0.20            0.312500            0.625000                0.316667            0.334921            0.025746              0.025270           0.012315       -0.021043                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.25      0.55      0.250000  0.180000               0.014642                 0.016379            full     hierarchical         whole_run        0.35      0.75          0.25            0.266667            0.533333                0.266667            0.206061            0.020310              0.018852           0.007696        0.021770                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.25      0.60      0.250000  0.231111              -0.015668                 0.004746            full     hierarchical post_alert_window        0.50      0.65          0.35            0.230769            0.692308                0.200000            0.168889            0.017115              0.017564           0.011609       -0.038478                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.35      0.60      0.350000  0.317094               0.008245                 0.006193            full     hierarchical post_alert_window        0.50      0.70          0.30            0.285714            0.500000                0.250000            0.213333            0.025746              0.025270           0.012315        0.017340                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.30      0.40      0.300000  0.237143              -0.001367                 0.001666            full     hierarchical post_alert_window        0.35      0.60          0.40            0.250000            0.333333                0.200000            0.139394            0.020310              0.018852           0.007696        0.000724                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.60      0.85      0.500000  0.421818               0.038620                 0.039412            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.50      0.85      0.444444  0.447343               0.017563                 0.009417            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.60      0.90      0.722222  0.623856               0.016121                 0.013079            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.600410         0.257740     0.141850              tier0            full
  BRANCH     0.626932         0.221454     0.151614              tier0            full
   CACHE     0.478548         0.203163     0.318289              tier0            full
   MEMBW     0.647660         0.225864     0.126475              tier0            full
     TLB     0.567522         0.276144     0.156334              tier0            full
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC                 compute       0.346594         0.319803             0.097144                 0.112879                 0.123579            full
  BRANCH               memory_io       0.312617         0.390557             0.071116                 0.139316                 0.086394            full
   CACHE                 compute       0.490142         0.295487             0.059412                 0.079637                 0.075322            full
   MEMBW                 compute       0.323177         0.358186             0.083122                 0.112595                 0.122920            full
     TLB               memory_io       0.352354         0.335558             0.096041                 0.113010                 0.103036            full
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
            tier0                    0.0                             0.0                           0.0                  0.3                    122.0                 660.0                 0.0                0.20                0.25            full
      tier0_tier1                    0.0                             0.0                           0.0                  0.5                    122.0                 494.5                 0.0                0.35                0.45            full
tier0_tier1_tier2                    0.0                             0.0                           0.0                  0.9                    122.0                 588.5                 0.0                0.65                0.80            full
```

## Files
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B120_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B120_a0.05_k3/config_runtime_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B120_a0.05_k3/run_context.json`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B120_a0.05_k3/case_inventory.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B120_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B120_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B120_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B120_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B120_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B120_a0.05_k3/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B120_a0.05_k3/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B120_a0.05_k3/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B120_a0.05_k3/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B120_a0.05_k3/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B120_a0.05_k3/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B120_a0.05_k3/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B120_a0.05_k3/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B120_a0.05_k3/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B120_a0.05_k3/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B120_a0.05_k3/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B120_a0.05_k3/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B120_a0.05_k3/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B120_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B120_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B120_a0.05_k3/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B120_a0.05_k3/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B120_a0.05_k3/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B120_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B120_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B120_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B120_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B120_a0.05_k3/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B120_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B120_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B120_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B120_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B120_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B120_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B120_a0.05_k3/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B120_a0.05_k3/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B120_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B120_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B120_a0.05_k3/figures/fig_detection_latency.png`
