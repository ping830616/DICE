# DICE Full Retrain Results

## Setup
- Feature profile: full ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_full_5hz.csv', 'tier2': 'tier2_full_5hz.csv'})
- Protocol: global, benign-only fit/calibration, block_B=20, alpha=0.05, persist_k=3, gain=0.5
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
           full             tier0       24          46          2.248524   0.7500 0.904972         1.0        1.0           0.25           0.35              0.005420              0.010185                      0.0                 0.005339
           full       tier0_tier1       24          64          2.932408   0.8125 0.949484         1.0        1.0           0.25           0.65              0.009895              0.023841                      0.0                 0.009997
           full tier0_tier1_tier2       24          75          3.576047   0.9250 0.983644         1.0        1.0           0.25           0.95              0.002772              0.006671                      0.0                 0.003386
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc  pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
           full   ATOMIC   0.8750  0.8875         1.0        1.0          0.002772          0.005753                  0.0             0.002138       2.074630      0.002980       2138.736114         0.002138
           full   BRANCH   0.9375  0.9500         1.0        1.0          0.002772          0.010725                  0.0             0.006741       3.867456      0.007952       6742.314041         0.006741
           full    CACHE   0.8750  0.8875         1.0        1.0          0.002772          0.007556                  0.0             0.004783       2.724767      0.004783       4784.390485         0.004783
           full    MEMBW   1.0000  1.0000         1.0        1.0          0.002772          0.007024                  0.0             0.003556       2.532919      0.004251       3557.207795         0.003556
           full      TLB   0.9375  0.9500         1.0        1.0          0.002772          0.007536                  0.0             0.004507       2.717498      0.004763       4508.042946         0.004507
```

## Paper-style Aggregates (Final Config)
- Base score mean stressor AUC-PR (all five): **0.9350**
- Base score mean stressor ROC-AUC (all five): **0.9250**
- WC score mean stressor AUC-PR (all five): **1.0000**
- WC score mean stressor ROC-AUC (all five): **1.0000**
- Base score mean stressor AUC-PR (excluding BRANCH/TLB): **0.9250**
- Base score mean stressor ROC-AUC (excluding BRANCH/TLB): **0.9167**
- WC score mean stressor AUC-PR (excluding BRANCH/TLB): **1.0000**
- WC score mean stressor ROC-AUC (excluding BRANCH/TLB): **1.0000**

## Diagnosis
- Feature-level diagnosis uses normalized whole-run residual-attribution prototypes as the default paper-facing result, with diagnosis-only filtering that removes monotonic counters and downweights generic memory-state features.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20       0.4      0.50           0.4  0.330000               0.022591                 0.016832            full
      tier0_tier1       20       0.3      0.35           0.3  0.225758               0.020210                 0.017800            full
tier0_tier1_tier2       20       0.3      0.40           0.3  0.200000               0.021109                 0.023439            full
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.20      0.50          0.20  0.220000               0.020132                 0.015452            full
      tier0_tier1       20      0.15      0.35          0.15  0.146032               0.104145                 0.034070            full
tier0_tier1_tier2       20      0.10      0.40          0.10  0.111111               0.015559                 0.013582            full
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.40      0.60          0.40  0.397619               0.009762                 0.006702            full
      tier0_tier1       20      0.35      0.45          0.35  0.306667               0.015973                 0.012169            full
tier0_tier1_tier2       20      0.35      0.60          0.35  0.290043               0.016553                 0.012579            full
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20       0.5      0.75      0.444444  0.378788               0.027245                 0.029276            full
      tier0_tier1       20       0.5      0.75      0.388889  0.342995               0.029640                 0.033685            full
tier0_tier1_tier2       20       0.4      0.95      0.500000  0.379552               0.015830                 0.017776            full
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.30      0.55        0.40          0.30  0.257143      0.35          0.65            0.428571            0.571429                0.333333            0.240000               0.013389                 0.010936            0.007829              0.006043           0.006901        0.167812            full
      tier0_tier1       20      0.30      0.40        0.45          0.30  0.280952      0.55          0.45            0.181818            0.181818                0.100000            0.088889              -0.000112                 0.011324            0.014943              0.012961           0.010050        0.021718            full
tier0_tier1_tier2       20      0.25      0.40        0.50          0.25  0.180000      0.40          0.60            0.250000            0.250000                0.300000            0.180000               0.011721                 0.015438            0.019736              0.017328           0.011164        0.119936            full
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.20       0.5        0.40          0.20  0.208889      0.80          0.20            0.187500            0.500000                0.166667            0.177143               0.003955                 0.012553            0.007829              0.006043           0.006901       -0.091720            full
      tier0_tier1       20      0.25       0.4        0.45          0.25  0.216667      0.15          0.85            0.000000            0.666667                0.000000            0.000000              -0.002687                 0.016132            0.014943              0.012961           0.010050        0.462757            full
tier0_tier1_tier2       20      0.25       0.5        0.50          0.25  0.252727      0.70          0.30            0.142857            0.500000                0.116667            0.130000              -0.010146                -0.006348            0.019736              0.017328           0.011164       -0.178112            full
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0  conf_0.00              0.000000      17      0.85          0.15            0.352941            0.529412                0.450000            0.300000            full
            tier0  conf_0.05              0.050000      11      0.55          0.45            0.545455            0.636364                0.550000            0.400000            full
            tier0  conf_0.10              0.100000       7      0.35          0.65            0.714286            0.857143                0.687500            0.483333            full
            tier0  conf_0.15              0.150000       5      0.25          0.75            0.600000            0.800000                0.375000            0.150000            full
            tier0    trained              0.167812       5      0.25          0.75            0.600000            0.800000                0.375000            0.150000            full
            tier0  conf_0.20              0.200000       4      0.20          0.80            0.750000            0.750000                0.750000            0.171429            full
            tier0  conf_0.25              0.250000       4      0.20          0.80            0.750000            0.750000                0.750000            0.171429            full
      tier0_tier1  conf_0.00              0.000000      14      0.70          0.30            0.285714            0.285714                0.300000            0.222222            full
      tier0_tier1    trained              0.021718      13      0.65          0.35            0.307692            0.307692                0.400000            0.235556            full
      tier0_tier1  conf_0.05              0.050000      11      0.55          0.45            0.272727            0.272727                0.250000            0.155556            full
      tier0_tier1  conf_0.10              0.100000       4      0.20          0.80            0.000000            0.000000                0.000000            0.000000            full
      tier0_tier1  conf_0.15              0.150000       3      0.15          0.85            0.000000            0.000000                0.000000            0.000000            full
      tier0_tier1  conf_0.20              0.200000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000            full
      tier0_tier1  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN            full
tier0_tier1_tier2  conf_0.00              0.000000      17      0.85          0.15            0.235294            0.352941                0.250000            0.172308            full
tier0_tier1_tier2  conf_0.05              0.050000      12      0.60          0.40            0.250000            0.416667                0.200000            0.109091            full
tier0_tier1_tier2  conf_0.10              0.100000       9      0.45          0.55            0.222222            0.444444                0.200000            0.088889            full
tier0_tier1_tier2    trained              0.119936       9      0.45          0.55            0.222222            0.444444                0.200000            0.088889            full
tier0_tier1_tier2  conf_0.15              0.150000       5      0.25          0.75            0.200000            0.400000                0.250000            0.080000            full
tier0_tier1_tier2  conf_0.20              0.200000       4      0.20          0.80            0.250000            0.250000                0.333333            0.080000            full
tier0_tier1_tier2  conf_0.25              0.250000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000            full
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained             -0.091720      16      0.80          0.20            0.187500            0.500000                0.166667            0.177143            full
            tier0  conf_0.00              0.000000      16      0.80          0.20            0.187500            0.500000                0.166667            0.177143            full
            tier0  conf_0.05              0.050000      12      0.60          0.40            0.250000            0.583333                0.350000            0.257778            full
            tier0  conf_0.10              0.100000       8      0.40          0.60            0.375000            0.500000                0.458333            0.300000            full
            tier0  conf_0.15              0.150000       6      0.30          0.70            0.500000            0.666667                0.583333            0.413333            full
            tier0  conf_0.20              0.200000       1      0.05          0.95            0.000000            1.000000                0.000000            0.000000            full
            tier0  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN            full
      tier0_tier1  conf_0.00              0.000000      14      0.70          0.30            0.214286            0.428571                0.200000            0.222222            full
      tier0_tier1  conf_0.05              0.050000      11      0.55          0.45            0.181818            0.454545                0.125000            0.100000            full
      tier0_tier1  conf_0.10              0.100000       8      0.40          0.60            0.125000            0.500000                0.125000            0.080000            full
      tier0_tier1  conf_0.15              0.150000       6      0.30          0.70            0.000000            0.333333                0.000000            0.000000            full
      tier0_tier1  conf_0.20              0.200000       4      0.20          0.80            0.000000            0.500000                0.000000            0.000000            full
      tier0_tier1  conf_0.25              0.250000       3      0.15          0.85            0.000000            0.666667                0.000000            0.000000            full
      tier0_tier1    trained              0.462757       3      0.15          0.85            0.000000            0.666667                0.000000            0.000000            full
tier0_tier1_tier2    trained             -0.178112      19      0.95          0.05            0.263158            0.526316                0.250000            0.267013            full
tier0_tier1_tier2  conf_0.00              0.000000      10      0.50          0.50            0.100000            0.400000                0.066667            0.100000            full
tier0_tier1_tier2  conf_0.05              0.050000       5      0.25          0.75            0.200000            0.200000                0.125000            0.133333            full
tier0_tier1_tier2  conf_0.10              0.100000       2      0.10          0.90            0.500000            0.500000                0.500000            0.200000            full
tier0_tier1_tier2  conf_0.15              0.150000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.20              0.200000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.25              0.250000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000            full
```

## Diagnosis Mode Comparison
- Whole-run and post-alert-window diagnosis are exported together so the diagnosis mode can be evaluated directly.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile diagnosis_target    diagnosis_mode  family_acc  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau                       status  min_class_count  min_group_count    group_key  include_workload
            tier0       20      0.40      0.50      0.400000  0.330000               0.022591                 0.016832            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.30      0.35      0.300000  0.225758               0.020210                 0.017800            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.30      0.40      0.300000  0.200000               0.021109                 0.023439            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.20      0.50      0.200000  0.220000               0.020132                 0.015452            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.15      0.35      0.150000  0.146032               0.104145                 0.034070            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.10      0.40      0.100000  0.111111               0.015559                 0.013582            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.30      0.55      0.300000  0.257143               0.013389                 0.010936            full     hierarchical         whole_run        0.40      0.35          0.65            0.428571            0.571429                0.333333            0.240000            0.007829              0.006043           0.006901        0.167812                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.30      0.40      0.300000  0.280952              -0.000112                 0.011324            full     hierarchical         whole_run        0.45      0.55          0.45            0.181818            0.181818                0.100000            0.088889            0.014943              0.012961           0.010050        0.021718                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.25      0.40      0.250000  0.180000               0.011721                 0.015438            full     hierarchical         whole_run        0.50      0.40          0.60            0.250000            0.250000                0.300000            0.180000            0.019736              0.017328           0.011164        0.119936                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.20      0.50      0.200000  0.208889               0.003955                 0.012553            full     hierarchical post_alert_window        0.40      0.80          0.20            0.187500            0.500000                0.166667            0.177143            0.007829              0.006043           0.006901       -0.091720                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.25      0.40      0.250000  0.216667              -0.002687                 0.016132            full     hierarchical post_alert_window        0.45      0.15          0.85            0.000000            0.666667                0.000000            0.000000            0.014943              0.012961           0.010050        0.462757                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.25      0.50      0.250000  0.252727              -0.010146                -0.006348            full     hierarchical post_alert_window        0.50      0.70          0.30            0.142857            0.500000                0.116667            0.130000            0.019736              0.017328           0.011164       -0.178112                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.50      0.75      0.444444  0.378788               0.027245                 0.029276            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.50      0.75      0.388889  0.342995               0.029640                 0.033685            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.40      0.95      0.500000  0.379552               0.015830                 0.017776            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.600798         0.270227     0.128976              tier0            full
  BRANCH     0.636310         0.213101     0.150589              tier0            full
   CACHE     0.517990         0.202284     0.279726              tier0            full
   MEMBW     0.639713         0.246730     0.113557              tier0            full
     TLB     0.582637         0.274755     0.142609              tier0            full
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC                 compute       0.345559         0.308499             0.112150                 0.136656                 0.097136            full
  BRANCH               memory_io       0.309565         0.364183             0.081301                 0.174473                 0.070478            full
   CACHE                 compute       0.462126         0.295828             0.073084                 0.106536                 0.062425            full
   MEMBW               memory_io       0.318135         0.349429             0.107156                 0.135255                 0.090025            full
     TLB                 compute       0.339518         0.323113             0.117422                 0.140997                 0.078949            full
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
            tier0                   0.25                        2.755102                      4.591837                 0.35                     70.0                 554.8                0.25                0.25                0.30            full
      tier0_tier1                   0.25                        1.836735                      3.673469                 0.65                     33.0                 752.2                0.45                0.45                0.55            full
tier0_tier1_tier2                   0.25                        1.836735                      3.673469                 0.95                     22.0                 795.8                0.65                0.65                0.75            full
```

## Files
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B20_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B20_a0.05_k3/config_runtime_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B20_a0.05_k3/run_context.json`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B20_a0.05_k3/case_inventory.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B20_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B20_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B20_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B20_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B20_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B20_a0.05_k3/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B20_a0.05_k3/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B20_a0.05_k3/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B20_a0.05_k3/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B20_a0.05_k3/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B20_a0.05_k3/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B20_a0.05_k3/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B20_a0.05_k3/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B20_a0.05_k3/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B20_a0.05_k3/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B20_a0.05_k3/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B20_a0.05_k3/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B20_a0.05_k3/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B20_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B20_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B20_a0.05_k3/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B20_a0.05_k3/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B20_a0.05_k3/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B20_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B20_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B20_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B20_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B20_a0.05_k3/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B20_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B20_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B20_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B20_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B20_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B20_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B20_a0.05_k3/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B20_a0.05_k3/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B20_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B20_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B20_a0.05_k3/figures/fig_detection_latency.png`
