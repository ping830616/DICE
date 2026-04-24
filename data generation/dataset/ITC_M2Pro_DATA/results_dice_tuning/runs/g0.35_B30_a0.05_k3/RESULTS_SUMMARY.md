# DICE Full Retrain Results

## Setup
- Feature profile: mixed ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_core_5hz.csv', 'tier2': 'tier2_core_5hz.csv'})
- Protocol: global, benign-only fit/calibration, block_B=30, alpha=0.05, persist_k=3, gain=0.35
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
          mixed             tier0       24          46          2.441152   0.7875 0.921899         1.0        1.0           0.25           0.30              0.006307              0.012545                      0.0                 0.006902
          mixed       tier0_tier1       24          57          3.022462   0.8250 0.955040         1.0        1.0           0.25           0.55              0.000050              0.000117                      0.0                 0.000058
          mixed tier0_tier1_tier2       24          64          3.494780   0.8375 0.957016         1.0        1.0           0.25           0.55              0.000053              0.000128                      0.0                 0.000064
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
          mixed   ATOMIC   0.7500 0.770833         1.0        1.0          0.000053          0.000092                  0.0             0.000046       1.732702      0.000039         46.726295         0.000046
          mixed   BRANCH   0.9375 0.950000         1.0        1.0          0.000053          0.000199                  0.0             0.000125       3.721437      0.000147        125.925654         0.000125
          mixed    CACHE   0.8125 0.804167         1.0        1.0          0.000053          0.000105                  0.0             0.000065       1.970586      0.000052         65.628128         0.000065
          mixed    MEMBW   0.8750 0.887500         1.0        1.0          0.000053          0.000149                  0.0             0.000080       2.786637      0.000096         80.983831         0.000080
          mixed      TLB   0.8125 0.804167         1.0        1.0          0.000053          0.000113                  0.0             0.000041       2.124789      0.000061         41.842042         0.000041
```

## Paper-style Aggregates (Final Config)
- Base score mean stressor AUC-PR (all five): **0.8433**
- Base score mean stressor ROC-AUC (all five): **0.8375**
- WC score mean stressor AUC-PR (all five): **1.0000**
- WC score mean stressor ROC-AUC (all five): **1.0000**
- Base score mean stressor AUC-PR (excluding BRANCH/TLB): **0.8208**
- Base score mean stressor ROC-AUC (excluding BRANCH/TLB): **0.8125**
- WC score mean stressor AUC-PR (excluding BRANCH/TLB): **1.0000**
- WC score mean stressor ROC-AUC (excluding BRANCH/TLB): **1.0000**

## Diagnosis
- Feature-level diagnosis uses normalized whole-run residual-attribution prototypes as the default paper-facing result, with diagnosis-only filtering that removes monotonic counters and downweights generic memory-state features.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.40      0.60          0.40  0.339091               0.024473                 0.019596           mixed
      tier0_tier1       20      0.35      0.55          0.35  0.251282               0.023492                 0.022329           mixed
tier0_tier1_tier2       20      0.50      0.60          0.50  0.485641               0.020196                 0.017682           mixed
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20       0.3      0.55           0.3  0.281457               0.020023                 0.013969           mixed
      tier0_tier1       20       0.1      0.35           0.1  0.057143               0.100366                 0.063896           mixed
tier0_tier1_tier2       20       0.1      0.45           0.1  0.110769               0.097205                 0.022626           mixed
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20       0.3      0.55           0.3  0.310173               0.012906                 0.010954           mixed
      tier0_tier1       20       0.2      0.50           0.2  0.214286               0.015900                 0.014482           mixed
tier0_tier1_tier2       20       0.3      0.55           0.3  0.283810               0.014138                 0.007317           mixed
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.55      0.85      0.472222  0.398551               0.032858                 0.033861           mixed
      tier0_tier1       20      0.50      0.75      0.444444  0.354978               0.026777                 0.029911           mixed
tier0_tier1_tier2       20      0.45      0.75      0.527778  0.444042               0.026777                 0.029730           mixed
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.45      0.65        0.35          0.45  0.435556      0.35          0.65            0.571429            0.714286                0.533333            0.460000               0.013746                 0.012012            0.009994              0.009015           0.011759        0.172589           mixed
      tier0_tier1       20      0.30      0.55        0.40          0.30  0.234343      0.75          0.25            0.333333            0.466667                0.400000            0.277778               0.009786                 0.014108            0.017207              0.014235           0.013602        0.009283           mixed
tier0_tier1_tier2       20      0.45      0.60        0.20          0.45  0.439394      0.45          0.55            0.666667            0.777778                0.733333            0.660000               0.011260                 0.012628            0.019536              0.014283           0.014684        0.088920           mixed
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.40      0.55        0.35          0.40  0.382698       0.6           0.4            0.250000            0.416667                0.266667             0.22381              -0.002173                 0.009186            0.009994              0.009015           0.011759       -0.027587           mixed
      tier0_tier1       20      0.15      0.35        0.40          0.15  0.116364       0.7           0.3            0.142857            0.357143                0.133333             0.13000               0.000379                 0.006604            0.017207              0.014235           0.013602       -0.193783           mixed
tier0_tier1_tier2       20      0.20      0.40        0.20          0.20  0.195556       0.5           0.5            0.000000            0.300000                0.000000             0.00000               0.031129                 0.009868            0.019536              0.014283           0.014684        0.075290           mixed
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0  conf_0.00              0.000000      16      0.80          0.20            0.437500            0.625000                0.450000            0.413333           mixed
            tier0  conf_0.05              0.050000      13      0.65          0.35            0.461538            0.692308                0.483333            0.422222           mixed
            tier0  conf_0.10              0.100000       7      0.35          0.65            0.571429            0.714286                0.416667            0.233333           mixed
            tier0  conf_0.15              0.150000       5      0.25          0.75            0.600000            0.800000                0.375000            0.150000           mixed
            tier0    trained              0.172589       5      0.25          0.75            0.600000            0.800000                0.375000            0.150000           mixed
            tier0  conf_0.20              0.200000       5      0.25          0.75            0.600000            0.800000                0.375000            0.150000           mixed
            tier0  conf_0.25              0.250000       5      0.25          0.75            0.600000            0.800000                0.375000            0.150000           mixed
      tier0_tier1  conf_0.00              0.000000      14      0.70          0.30            0.285714            0.428571                0.333333            0.177778           mixed
      tier0_tier1    trained              0.009283      13      0.65          0.35            0.307692            0.384615                0.333333            0.177778           mixed
      tier0_tier1  conf_0.05              0.050000      13      0.65          0.35            0.307692            0.384615                0.333333            0.177778           mixed
      tier0_tier1  conf_0.10              0.100000       9      0.45          0.55            0.333333            0.333333                0.400000            0.200000           mixed
      tier0_tier1  conf_0.15              0.150000       5      0.25          0.75            0.400000            0.400000                0.500000            0.280000           mixed
      tier0_tier1  conf_0.20              0.200000       4      0.20          0.80            0.250000            0.250000                0.333333            0.080000           mixed
      tier0_tier1  conf_0.25              0.250000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.00              0.000000      16      0.80          0.20            0.500000            0.625000                0.550000            0.506667           mixed
tier0_tier1_tier2  conf_0.05              0.050000      12      0.60          0.40            0.416667            0.583333                0.433333            0.355556           mixed
tier0_tier1_tier2    trained              0.088920       8      0.40          0.60            0.375000            0.625000                0.416667            0.233333           mixed
tier0_tier1_tier2  conf_0.10              0.100000       8      0.40          0.60            0.375000            0.625000                0.416667            0.233333           mixed
tier0_tier1_tier2  conf_0.15              0.150000       6      0.30          0.70            0.333333            0.666667                0.222222            0.114286           mixed
tier0_tier1_tier2  conf_0.20              0.200000       4      0.20          0.80            0.500000            0.750000                0.333333            0.133333           mixed
tier0_tier1_tier2  conf_0.25              0.250000       1      0.05          0.95            1.000000            1.000000                1.000000            0.200000           mixed
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained             -0.027587      16      0.80          0.20            0.375000            0.500000                0.400000            0.387143           mixed
            tier0  conf_0.00              0.000000      15      0.75          0.25            0.333333            0.466667                0.333333            0.307143           mixed
            tier0  conf_0.05              0.050000      10      0.50          0.50            0.400000            0.600000                0.450000            0.426667           mixed
            tier0  conf_0.10              0.100000       7      0.35          0.65            0.428571            0.571429                0.500000            0.380000           mixed
            tier0  conf_0.15              0.150000       4      0.20          0.80            0.500000            0.500000                0.500000            0.266667           mixed
            tier0  conf_0.20              0.200000       3      0.15          0.85            0.666667            0.666667                0.666667            0.333333           mixed
            tier0  conf_0.25              0.250000       2      0.10          0.90            0.500000            0.500000                0.500000            0.133333           mixed
      tier0_tier1    trained             -0.193783      14      0.70          0.30            0.142857            0.357143                0.133333            0.130000           mixed
      tier0_tier1  conf_0.00              0.000000      13      0.65          0.35            0.076923            0.307692                0.066667            0.050000           mixed
      tier0_tier1  conf_0.05              0.050000       8      0.40          0.60            0.125000            0.250000                0.100000            0.066667           mixed
      tier0_tier1  conf_0.10              0.100000       7      0.35          0.65            0.142857            0.142857                0.200000            0.080000           mixed
      tier0_tier1  conf_0.15              0.150000       7      0.35          0.65            0.142857            0.142857                0.200000            0.080000           mixed
      tier0_tier1  conf_0.20              0.200000       7      0.35          0.65            0.142857            0.142857                0.200000            0.080000           mixed
      tier0_tier1  conf_0.25              0.250000       6      0.30          0.70            0.166667            0.166667                0.200000            0.100000           mixed
tier0_tier1_tier2  conf_0.00              0.000000      14      0.70          0.30            0.142857            0.428571                0.150000            0.150000           mixed
tier0_tier1_tier2  conf_0.05              0.050000       9      0.45          0.55            0.111111            0.444444                0.066667            0.066667           mixed
tier0_tier1_tier2    trained              0.075290       9      0.45          0.55            0.111111            0.444444                0.066667            0.066667           mixed
tier0_tier1_tier2  conf_0.10              0.100000       7      0.35          0.65            0.000000            0.285714                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.15              0.150000       5      0.25          0.75            0.000000            0.400000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.20              0.200000       5      0.25          0.75            0.000000            0.400000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.25              0.250000       4      0.20          0.80            0.000000            0.500000                0.000000            0.000000           mixed
```

## Diagnosis Mode Comparison
- Whole-run and post-alert-window diagnosis are exported together so the diagnosis mode can be evaluated directly.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile diagnosis_target    diagnosis_mode  family_acc  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau                       status  min_class_count  min_group_count    group_key  include_workload
            tier0       20      0.40      0.60      0.400000  0.339091               0.024473                 0.019596           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.35      0.55      0.350000  0.251282               0.023492                 0.022329           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.50      0.60      0.500000  0.485641               0.020196                 0.017682           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.30      0.55      0.300000  0.281457               0.020023                 0.013969           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.10      0.35      0.100000  0.057143               0.100366                 0.063896           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.10      0.45      0.100000  0.110769               0.097205                 0.022626           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.45      0.65      0.450000  0.435556               0.013746                 0.012012           mixed     hierarchical         whole_run        0.35      0.35          0.65            0.571429            0.714286                0.533333            0.460000            0.009994              0.009015           0.011759        0.172589                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.30      0.55      0.300000  0.234343               0.009786                 0.014108           mixed     hierarchical         whole_run        0.40      0.75          0.25            0.333333            0.466667                0.400000            0.277778            0.017207              0.014235           0.013602        0.009283                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.45      0.60      0.450000  0.439394               0.011260                 0.012628           mixed     hierarchical         whole_run        0.20      0.45          0.55            0.666667            0.777778                0.733333            0.660000            0.019536              0.014283           0.014684        0.088920                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.40      0.55      0.400000  0.382698              -0.002173                 0.009186           mixed     hierarchical post_alert_window        0.35      0.60          0.40            0.250000            0.416667                0.266667            0.223810            0.009994              0.009015           0.011759       -0.027587                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.15      0.35      0.150000  0.116364               0.000379                 0.006604           mixed     hierarchical post_alert_window        0.40      0.70          0.30            0.142857            0.357143                0.133333            0.130000            0.017207              0.014235           0.013602       -0.193783                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.20      0.40      0.200000  0.195556               0.031129                 0.009868           mixed     hierarchical post_alert_window        0.20      0.50          0.50            0.000000            0.300000                0.000000            0.000000            0.019536              0.014283           0.014684        0.075290                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.55      0.85      0.472222  0.398551               0.032858                 0.033861           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.50      0.75      0.444444  0.354978               0.026777                 0.029911           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.45      0.75      0.527778  0.444042               0.026777                 0.029730           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.715705         0.129608     0.154687              tier0           mixed
  BRANCH     0.766790         0.084393     0.148817              tier0           mixed
   CACHE     0.544496         0.347593     0.107912              tier0           mixed
   MEMBW     0.780528         0.091859     0.127613              tier0           mixed
     TLB     0.707689         0.131120     0.161191              tier0           mixed
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC               memory_io       0.264668         0.404075             0.081297                 0.218419                 0.031541           mixed
  BRANCH               memory_io       0.247600         0.458036             0.049279                 0.205407                 0.039677           mixed
   CACHE               memory_io       0.463982         0.279576             0.066005                 0.148137                 0.042299           mixed
   MEMBW               memory_io       0.231194         0.481214             0.056555                 0.179070                 0.051967           mixed
     TLB               memory_io       0.300149         0.393188             0.073986                 0.206440                 0.026237           mixed
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
            tier0                   0.25                        0.927835                      2.783505                 0.30                     52.5                 603.5                 0.2                 0.2                0.25           mixed
      tier0_tier1                   0.25                        0.927835                      2.783505                 0.55                     75.0                 818.0                 0.3                 0.3                0.45           mixed
tier0_tier1_tier2                   0.25                        0.927835                      2.783505                 0.55                     73.0                 817.0                 0.3                 0.3                0.45           mixed
```

## Files
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B30_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B30_a0.05_k3/config_runtime_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B30_a0.05_k3/run_context.json`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B30_a0.05_k3/case_inventory.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B30_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B30_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B30_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B30_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B30_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B30_a0.05_k3/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B30_a0.05_k3/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B30_a0.05_k3/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B30_a0.05_k3/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B30_a0.05_k3/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B30_a0.05_k3/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B30_a0.05_k3/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B30_a0.05_k3/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B30_a0.05_k3/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B30_a0.05_k3/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B30_a0.05_k3/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B30_a0.05_k3/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B30_a0.05_k3/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B30_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B30_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B30_a0.05_k3/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B30_a0.05_k3/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B30_a0.05_k3/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B30_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B30_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B30_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B30_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B30_a0.05_k3/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B30_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B30_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B30_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B30_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B30_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B30_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B30_a0.05_k3/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B30_a0.05_k3/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B30_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B30_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B30_a0.05_k3/figures/fig_detection_latency.png`
