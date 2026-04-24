# DICE Full Retrain Results

## Setup
- Feature profile: full ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_full_5hz.csv', 'tier2': 'tier2_full_5hz.csv'})
- Protocol: global, benign-only fit/calibration, block_B=20, alpha=0.05, persist_k=3, gain=0.35
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
           full             tier0       24          46          2.764948   0.7625 0.917472         1.0        1.0           0.25           0.35              0.007060              0.013378                      0.0                 0.007368
           full       tier0_tier1       24          64          3.220653   0.8250 0.955040         1.0        1.0           0.25           0.65              0.012226              0.030427                      0.0                 0.012183
           full tier0_tier1_tier2       24          75          3.694766   0.9500 0.989710         1.0        1.0           0.25           0.95              0.002916              0.007312                      0.0                 0.003925
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc  pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
           full   ATOMIC   0.9375    0.95         1.0        1.0          0.002916          0.006449                  0.0             0.002797       2.211155      0.003533       2798.187258         0.002797
           full   BRANCH   0.9375    0.95         1.0        1.0          0.002916          0.011123                  0.0             0.007772       3.813555      0.008207       7772.871674         0.007772
           full    CACHE   0.9375    0.95         1.0        1.0          0.002916          0.008335                  0.0             0.005299       2.857884      0.005419       5300.253176         0.005299
           full    MEMBW   1.0000    1.00         1.0        1.0          0.002916          0.007620                  0.0             0.004024       2.612591      0.004704       4024.861535         0.004024
           full      TLB   0.9375    0.95         1.0        1.0          0.002916          0.007676                  0.0             0.004766       2.631800      0.004760       4767.297936         0.004766
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
            tier0       20       0.4       0.6           0.4  0.351429               0.023892                 0.020545            full
      tier0_tier1       20       0.3       0.4           0.3  0.231538               0.014234                 0.011031            full
tier0_tier1_tier2       20       0.3       0.4           0.3  0.206667               0.020962                 0.021623            full
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.30      0.45          0.30  0.297143               0.016699                 0.013017            full
      tier0_tier1       20      0.15      0.40          0.15  0.146032               0.107608                 0.051799            full
tier0_tier1_tier2       20      0.10      0.35          0.10  0.080000               0.016702                 0.014992            full
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.25      0.50          0.25  0.253030               0.011428                 0.008250            full
      tier0_tier1       20      0.20      0.45          0.20  0.152727               0.019006                 0.018123            full
tier0_tier1_tier2       20      0.35      0.65          0.35  0.286667               0.016452                 0.011590            full
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.55      0.85      0.472222  0.398551               0.032455                 0.033880            full
      tier0_tier1       20      0.45      0.75      0.361111  0.305463               0.024820                 0.028619            full
tier0_tier1_tier2       20      0.50      0.90      0.611111  0.501307               0.015427                 0.015088            full
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.45      0.65        0.40          0.45  0.419091      0.35          0.65            0.571429            0.857143                0.400000            0.333333               0.010322                 0.011049            0.008769              0.006465           0.007508        0.175733            full
      tier0_tier1       20      0.25      0.40        0.55          0.25  0.225824      0.45          0.55            0.222222            0.222222                0.100000            0.088889              -0.000381                 0.007036            0.016601              0.014976           0.013272        0.029365            full
tier0_tier1_tier2       20      0.25      0.40        0.40          0.25  0.180000      0.50          0.50            0.300000            0.400000                0.333333            0.188889               0.014502                 0.014867            0.020043              0.017060           0.009225        0.100202            full
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.35      0.55        0.40          0.35  0.319394      0.60          0.40            0.333333            0.416667                0.283333            0.235556              -0.010081                 0.007995            0.008769              0.006465           0.007508       -0.016645            full
      tier0_tier1       20      0.15      0.40        0.55          0.15  0.118681      0.25          0.75            0.000000            0.600000                0.000000            0.000000              -0.002465                 0.019687            0.016601              0.014976           0.013272        0.454022            full
tier0_tier1_tier2       20      0.25      0.40        0.40          0.25  0.185714      0.70          0.30            0.142857            0.357143                0.133333            0.072727              -0.004456                 0.003979            0.020043              0.017060           0.009225       -0.148779            full
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0  conf_0.00              0.000000      15      0.75          0.25            0.466667            0.600000                0.500000            0.459091            full
            tier0  conf_0.05              0.050000      12      0.60          0.40            0.500000            0.666667                0.550000            0.450000            full
            tier0  conf_0.10              0.100000       6      0.30          0.70            0.666667            0.666667                0.583333            0.283333            full
            tier0  conf_0.15              0.150000       5      0.25          0.75            0.800000            0.800000                0.875000            0.304762            full
            tier0    trained              0.175733       4      0.20          0.80            0.750000            0.750000                0.750000            0.171429            full
            tier0  conf_0.20              0.200000       4      0.20          0.80            0.750000            0.750000                0.750000            0.171429            full
            tier0  conf_0.25              0.250000       4      0.20          0.80            0.750000            0.750000                0.750000            0.171429            full
      tier0_tier1  conf_0.00              0.000000      14      0.70          0.30            0.285714            0.357143                0.300000            0.226667            full
      tier0_tier1    trained              0.029365      10      0.50          0.50            0.200000            0.300000                0.166667            0.146667            full
      tier0_tier1  conf_0.05              0.050000       9      0.45          0.55            0.111111            0.222222                0.066667            0.066667            full
      tier0_tier1  conf_0.10              0.100000       3      0.15          0.85            0.000000            0.000000                0.000000            0.000000            full
      tier0_tier1  conf_0.15              0.150000       2      0.10          0.90            0.000000            0.000000                0.000000            0.000000            full
      tier0_tier1  conf_0.20              0.200000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000            full
      tier0_tier1  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN            full
tier0_tier1_tier2  conf_0.00              0.000000      17      0.85          0.15            0.235294            0.352941                0.250000            0.172308            full
tier0_tier1_tier2  conf_0.05              0.050000      15      0.75          0.25            0.266667            0.400000                0.250000            0.172308            full
tier0_tier1_tier2  conf_0.10              0.100000       9      0.45          0.55            0.222222            0.444444                0.200000            0.080000            full
tier0_tier1_tier2    trained              0.100202       9      0.45          0.55            0.222222            0.444444                0.200000            0.080000            full
tier0_tier1_tier2  conf_0.15              0.150000       7      0.35          0.65            0.142857            0.428571                0.250000            0.057143            full
tier0_tier1_tier2  conf_0.20              0.200000       3      0.15          0.85            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.25              0.250000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000            full
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained             -0.016645      14      0.70          0.30            0.285714            0.428571                0.216667            0.206061            full
            tier0  conf_0.00              0.000000      14      0.70          0.30            0.285714            0.428571                0.216667            0.206061            full
            tier0  conf_0.05              0.050000       9      0.45          0.55            0.222222            0.444444                0.312500            0.213333            full
            tier0  conf_0.10              0.100000       4      0.20          0.80            0.500000            0.500000                0.500000            0.266667            full
            tier0  conf_0.15              0.150000       2      0.10          0.90            0.500000            0.500000                0.500000            0.200000            full
            tier0  conf_0.20              0.200000       2      0.10          0.90            0.500000            0.500000                0.500000            0.200000            full
            tier0  conf_0.25              0.250000       2      0.10          0.90            0.500000            0.500000                0.500000            0.200000            full
      tier0_tier1  conf_0.00              0.000000      13      0.65          0.35            0.153846            0.461538                0.100000            0.088889            full
      tier0_tier1  conf_0.05              0.050000      10      0.50          0.50            0.100000            0.500000                0.100000            0.080000            full
      tier0_tier1  conf_0.10              0.100000      10      0.50          0.50            0.100000            0.500000                0.100000            0.080000            full
      tier0_tier1  conf_0.15              0.150000       7      0.35          0.65            0.000000            0.571429                0.000000            0.000000            full
      tier0_tier1  conf_0.20              0.200000       7      0.35          0.65            0.000000            0.571429                0.000000            0.000000            full
      tier0_tier1  conf_0.25              0.250000       4      0.20          0.80            0.000000            0.500000                0.000000            0.000000            full
      tier0_tier1    trained              0.454022       3      0.15          0.85            0.000000            0.666667                0.000000            0.000000            full
tier0_tier1_tier2    trained             -0.148779      18      0.90          0.10            0.222222            0.388889                0.233333            0.180952            full
tier0_tier1_tier2  conf_0.00              0.000000      12      0.60          0.40            0.083333            0.250000                0.100000            0.050000            full
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
            tier0       20      0.40      0.60      0.400000  0.351429               0.023892                 0.020545            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.30      0.40      0.300000  0.231538               0.014234                 0.011031            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.30      0.40      0.300000  0.206667               0.020962                 0.021623            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.30      0.45      0.300000  0.297143               0.016699                 0.013017            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.15      0.40      0.150000  0.146032               0.107608                 0.051799            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.10      0.35      0.100000  0.080000               0.016702                 0.014992            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.45      0.65      0.450000  0.419091               0.010322                 0.011049            full     hierarchical         whole_run        0.40      0.35          0.65            0.571429            0.857143                0.400000            0.333333            0.008769              0.006465           0.007508        0.175733                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.25      0.40      0.250000  0.225824              -0.000381                 0.007036            full     hierarchical         whole_run        0.55      0.45          0.55            0.222222            0.222222                0.100000            0.088889            0.016601              0.014976           0.013272        0.029365                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.25      0.40      0.250000  0.180000               0.014502                 0.014867            full     hierarchical         whole_run        0.40      0.50          0.50            0.300000            0.400000                0.333333            0.188889            0.020043              0.017060           0.009225        0.100202                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.35      0.55      0.350000  0.319394              -0.010081                 0.007995            full     hierarchical post_alert_window        0.40      0.60          0.40            0.333333            0.416667                0.283333            0.235556            0.008769              0.006465           0.007508       -0.016645                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.15      0.40      0.150000  0.118681              -0.002465                 0.019687            full     hierarchical post_alert_window        0.55      0.25          0.75            0.000000            0.600000                0.000000            0.000000            0.016601              0.014976           0.013272        0.454022                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.25      0.40      0.250000  0.185714              -0.004456                 0.003979            full     hierarchical post_alert_window        0.40      0.70          0.30            0.142857            0.357143                0.133333            0.072727            0.020043              0.017060           0.009225       -0.148779                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.55      0.85      0.472222  0.398551               0.032455                 0.033880            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.45      0.75      0.361111  0.305463               0.024820                 0.028619            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.50      0.90      0.611111  0.501307               0.015427                 0.015088            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.589887         0.272918     0.137195              tier0            full
  BRANCH     0.623516         0.217059     0.159425              tier0            full
   CACHE     0.497289         0.203877     0.298834              tier0            full
   MEMBW     0.631244         0.246665     0.122091              tier0            full
     TLB     0.567208         0.280069     0.152723              tier0            full
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC                 compute       0.351136         0.298523             0.118351                 0.133047                 0.098943            full
  BRANCH               memory_io       0.313535         0.358560             0.084930                 0.171939                 0.071036            full
   CACHE                 compute       0.477130         0.283735             0.075422                 0.100722                 0.062991            full
   MEMBW               memory_io       0.322948         0.340881             0.109648                 0.132026                 0.094497            full
     TLB                 compute       0.346663         0.312891             0.121496                 0.137989                 0.080961            full
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
            tier0                   0.25                        2.755102                      4.591837                 0.35                     70.0                 550.6                0.25                0.25                0.30            full
      tier0_tier1                   0.25                        2.755102                      4.591837                 0.65                     33.0                 752.2                0.45                0.45                0.55            full
tier0_tier1_tier2                   0.25                        2.755102                      4.591837                 0.95                     22.0                 786.4                0.65                0.65                0.75            full
```

## Files
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B20_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B20_a0.05_k3/config_runtime_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B20_a0.05_k3/run_context.json`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B20_a0.05_k3/case_inventory.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B20_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B20_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B20_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B20_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B20_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B20_a0.05_k3/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B20_a0.05_k3/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B20_a0.05_k3/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B20_a0.05_k3/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B20_a0.05_k3/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B20_a0.05_k3/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B20_a0.05_k3/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B20_a0.05_k3/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B20_a0.05_k3/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B20_a0.05_k3/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B20_a0.05_k3/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B20_a0.05_k3/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B20_a0.05_k3/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B20_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B20_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B20_a0.05_k3/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B20_a0.05_k3/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B20_a0.05_k3/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B20_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B20_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B20_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B20_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B20_a0.05_k3/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B20_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B20_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B20_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B20_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B20_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B20_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B20_a0.05_k3/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B20_a0.05_k3/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B20_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B20_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.35_B20_a0.05_k3/figures/fig_detection_latency.png`
