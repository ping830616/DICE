# DICE Full Retrain Results

## Setup
- Feature profile: mixed ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_core_5hz.csv', 'tier2': 'tier2_core_5hz.csv'})
- Protocol: global, benign-only fit/calibration, block_B=120, alpha=0.05, persist_k=3, gain=0.35
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
          mixed             tier0       24          46          2.165267   0.8000 0.931899         1.0        1.0            0.0           0.30              0.004397              0.010045                      0.0                 0.005804
          mixed       tier0_tier1       24          57          2.554675   0.8125 0.940232         1.0        1.0            0.0           0.45              0.000047              0.000115                      0.0                 0.000064
          mixed tier0_tier1_tier2       24          64          2.869700   0.8250 0.947375         1.0        1.0            0.0           0.45              0.000051              0.000128                      0.0                 0.000068
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
          mixed   ATOMIC   0.8125 0.804167         1.0        1.0          0.000051          0.000109                  0.0             0.000067       2.125221      0.000058         68.175396         0.000067
          mixed   BRANCH   0.8750 0.887500         1.0        1.0          0.000051          0.000177                  0.0             0.000121       3.438264      0.000126        122.015699         0.000121
          mixed    CACHE   0.8125 0.804167         1.0        1.0          0.000051          0.000110                  0.0             0.000064       2.140315      0.000059         64.529644         0.000064
          mixed    MEMBW   0.8750 0.887500         1.0        1.0          0.000051          0.000176                  0.0             0.000103       3.416572      0.000125        104.430111         0.000103
          mixed      TLB   0.7500 0.679167         1.0        1.0          0.000051          0.000118                  0.0             0.000058       2.302141      0.000067         59.062792         0.000058
```

## Paper-style Aggregates (Final Config)
- Base score mean stressor AUC-PR (all five): **0.8125**
- Base score mean stressor ROC-AUC (all five): **0.8250**
- WC score mean stressor AUC-PR (all five): **1.0000**
- WC score mean stressor ROC-AUC (all five): **1.0000**
- Base score mean stressor AUC-PR (excluding BRANCH/TLB): **0.8319**
- Base score mean stressor ROC-AUC (excluding BRANCH/TLB): **0.8333**
- WC score mean stressor AUC-PR (excluding BRANCH/TLB): **1.0000**
- WC score mean stressor ROC-AUC (excluding BRANCH/TLB): **1.0000**

## Diagnosis
- Feature-level diagnosis uses normalized whole-run residual-attribution prototypes as the default paper-facing result, with diagnosis-only filtering that removes monotonic counters and downweights generic memory-state features.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.40       0.6          0.40  0.322424               0.026294                 0.019490           mixed
      tier0_tier1       20      0.35       0.6          0.35  0.249451               0.025840                 0.023812           mixed
tier0_tier1_tier2       20      0.45       0.6          0.45  0.425641               0.023672                 0.021537           mixed
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.25      0.70          0.25  0.241587               0.017364                 0.015229           mixed
      tier0_tier1       20      0.15      0.35          0.15  0.111111               0.043005                 0.029078           mixed
tier0_tier1_tier2       20      0.10      0.40          0.10  0.088889               0.031502                 0.011789           mixed
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.30      0.60          0.30  0.287619               0.015595                 0.013728           mixed
      tier0_tier1       20      0.30      0.55          0.30  0.305397               0.013949                 0.010314           mixed
tier0_tier1_tier2       20      0.25      0.70          0.25  0.223333               0.013780                 0.012415           mixed
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.60      0.80      0.500000  0.421818               0.037200                 0.037432           mixed
      tier0_tier1       20      0.50      0.70      0.444444  0.356745               0.028872                 0.030792           mixed
tier0_tier1_tier2       20      0.45      0.75      0.527778  0.444042               0.028563                 0.024444           mixed
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.30      0.60        0.40          0.30  0.286667      0.50          0.50            0.400000            0.600000                0.433333            0.360000               0.006017                 0.010779            0.014441              0.010418           0.010614        0.060118           mixed
      tier0_tier1       20      0.30      0.55        0.35          0.30  0.270476      0.65          0.35            0.230769            0.384615                0.333333            0.216667               0.010179                 0.020324            0.017062              0.014772           0.014059        0.052098           mixed
tier0_tier1_tier2       20      0.35      0.60        0.35          0.35  0.355824      0.65          0.35            0.461538            0.692308                0.466667            0.460000               0.016877                 0.023300            0.017267              0.013864           0.010991       -0.062527           mixed
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.25      0.70        0.40          0.25  0.220269      0.85          0.15            0.235294            0.705882                0.233333            0.208730               0.005787                 0.015229            0.014441              0.010418           0.010614       -0.016288           mixed
      tier0_tier1       20      0.20      0.45        0.35          0.20  0.155556      0.65          0.35            0.230769            0.538462                0.200000            0.188889               0.000188                 0.018401            0.017062              0.014772           0.014059       -0.026990           mixed
tier0_tier1_tier2       20      0.15      0.30        0.35          0.15  0.124444      0.60          0.40            0.250000            0.416667                0.266667            0.226667              -0.003223                 0.007162            0.017267              0.013864           0.010991       -0.154195           mixed
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0  conf_0.00              0.000000      14      0.70          0.30            0.357143            0.571429                0.433333            0.327619           mixed
            tier0  conf_0.05              0.050000      11      0.55          0.45            0.363636            0.545455                0.333333            0.214286           mixed
            tier0    trained              0.060118      10      0.50          0.50            0.400000            0.600000                0.333333            0.228571           mixed
            tier0  conf_0.10              0.100000       8      0.40          0.60            0.250000            0.500000                0.166667            0.114286           mixed
            tier0  conf_0.15              0.150000       6      0.30          0.70            0.333333            0.500000                0.166667            0.114286           mixed
            tier0  conf_0.20              0.200000       4      0.20          0.80            0.500000            0.750000                0.333333            0.133333           mixed
            tier0  conf_0.25              0.250000       4      0.20          0.80            0.500000            0.750000                0.333333            0.133333           mixed
      tier0_tier1  conf_0.00              0.000000      15      0.75          0.25            0.266667            0.466667                0.316667            0.207143           mixed
      tier0_tier1  conf_0.05              0.050000      12      0.60          0.40            0.250000            0.416667                0.300000            0.157143           mixed
      tier0_tier1    trained              0.052098      12      0.60          0.40            0.250000            0.416667                0.300000            0.157143           mixed
      tier0_tier1  conf_0.10              0.100000      10      0.50          0.50            0.300000            0.400000                0.300000            0.190476           mixed
      tier0_tier1  conf_0.15              0.150000       7      0.35          0.65            0.142857            0.285714                0.200000            0.133333           mixed
      tier0_tier1  conf_0.20              0.200000       3      0.15          0.85            0.000000            0.000000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.25              0.250000       2      0.10          0.90            0.000000            0.000000                0.000000            0.000000           mixed
tier0_tier1_tier2    trained             -0.062527      17      0.85          0.15            0.411765            0.588235                0.416667            0.426667           mixed
tier0_tier1_tier2  conf_0.00              0.000000      16      0.80          0.20            0.375000            0.562500                0.383333            0.393333           mixed
tier0_tier1_tier2  conf_0.05              0.050000      13      0.65          0.35            0.307692            0.538462                0.300000            0.252727           mixed
tier0_tier1_tier2  conf_0.10              0.100000      11      0.55          0.45            0.181818            0.454545                0.133333            0.072727           mixed
tier0_tier1_tier2  conf_0.15              0.150000       7      0.35          0.65            0.285714            0.571429                0.250000            0.100000           mixed
tier0_tier1_tier2  conf_0.20              0.200000       5      0.25          0.75            0.400000            0.400000                0.250000            0.114286           mixed
tier0_tier1_tier2  conf_0.25              0.250000       1      0.05          0.95            1.000000            1.000000                1.000000            0.200000           mixed
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained             -0.016288      16      0.80          0.20            0.250000            0.687500                0.233333            0.214286           mixed
            tier0  conf_0.00              0.000000      16      0.80          0.20            0.250000            0.687500                0.233333            0.214286           mixed
            tier0  conf_0.05              0.050000      16      0.80          0.20            0.250000            0.687500                0.233333            0.214286           mixed
            tier0  conf_0.10              0.100000       9      0.45          0.55            0.111111            0.666667                0.100000            0.080000           mixed
            tier0  conf_0.15              0.150000       6      0.30          0.70            0.166667            0.666667                0.125000            0.100000           mixed
            tier0  conf_0.20              0.200000       4      0.20          0.80            0.250000            0.750000                0.250000            0.133333           mixed
            tier0  conf_0.25              0.250000       2      0.10          0.90            0.000000            1.000000                0.000000            0.000000           mixed
      tier0_tier1    trained             -0.026990      13      0.65          0.35            0.153846            0.461538                0.133333            0.088889           mixed
      tier0_tier1  conf_0.00              0.000000      13      0.65          0.35            0.153846            0.461538                0.133333            0.088889           mixed
      tier0_tier1  conf_0.05              0.050000      10      0.50          0.50            0.200000            0.500000                0.133333            0.100000           mixed
      tier0_tier1  conf_0.10              0.100000      10      0.50          0.50            0.200000            0.500000                0.133333            0.100000           mixed
      tier0_tier1  conf_0.15              0.150000       8      0.40          0.60            0.125000            0.500000                0.100000            0.080000           mixed
      tier0_tier1  conf_0.20              0.200000       6      0.30          0.70            0.000000            0.500000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.25              0.250000       4      0.20          0.80            0.000000            0.500000                0.000000            0.000000           mixed
tier0_tier1_tier2    trained             -0.154195      16      0.80          0.20            0.187500            0.375000                0.250000            0.157143           mixed
tier0_tier1_tier2  conf_0.00              0.000000      15      0.75          0.25            0.133333            0.333333                0.200000            0.100000           mixed
tier0_tier1_tier2  conf_0.05              0.050000       9      0.45          0.55            0.111111            0.333333                0.200000            0.133333           mixed
tier0_tier1_tier2  conf_0.10              0.100000       7      0.35          0.65            0.142857            0.285714                0.200000            0.133333           mixed
tier0_tier1_tier2  conf_0.15              0.150000       3      0.15          0.85            0.000000            0.333333                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.20              0.200000       2      0.10          0.90            0.000000            0.500000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.25              0.250000       2      0.10          0.90            0.000000            0.500000                0.000000            0.000000           mixed
```

## Diagnosis Mode Comparison
- Whole-run and post-alert-window diagnosis are exported together so the diagnosis mode can be evaluated directly.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile diagnosis_target    diagnosis_mode  family_acc  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau                       status  min_class_count  min_group_count    group_key  include_workload
            tier0       20      0.40      0.60      0.400000  0.322424               0.026294                 0.019490           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.35      0.60      0.350000  0.249451               0.025840                 0.023812           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.45      0.60      0.450000  0.425641               0.023672                 0.021537           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.25      0.70      0.250000  0.241587               0.017364                 0.015229           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.15      0.35      0.150000  0.111111               0.043005                 0.029078           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.10      0.40      0.100000  0.088889               0.031502                 0.011789           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.30      0.60      0.300000  0.286667               0.006017                 0.010779           mixed     hierarchical         whole_run        0.40      0.50          0.50            0.400000            0.600000                0.433333            0.360000            0.014441              0.010418           0.010614        0.060118                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.30      0.55      0.300000  0.270476               0.010179                 0.020324           mixed     hierarchical         whole_run        0.35      0.65          0.35            0.230769            0.384615                0.333333            0.216667            0.017062              0.014772           0.014059        0.052098                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.35      0.60      0.350000  0.355824               0.016877                 0.023300           mixed     hierarchical         whole_run        0.35      0.65          0.35            0.461538            0.692308                0.466667            0.460000            0.017267              0.013864           0.010991       -0.062527                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.25      0.70      0.250000  0.220269               0.005787                 0.015229           mixed     hierarchical post_alert_window        0.40      0.85          0.15            0.235294            0.705882                0.233333            0.208730            0.014441              0.010418           0.010614       -0.016288                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.20      0.45      0.200000  0.155556               0.000188                 0.018401           mixed     hierarchical post_alert_window        0.35      0.65          0.35            0.230769            0.538462                0.200000            0.188889            0.017062              0.014772           0.014059       -0.026990                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.15      0.30      0.150000  0.124444              -0.003223                 0.007162           mixed     hierarchical post_alert_window        0.35      0.60          0.40            0.250000            0.416667                0.266667            0.226667            0.017267              0.013864           0.010991       -0.154195                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.60      0.80      0.500000  0.421818               0.037200                 0.037432           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.50      0.70      0.444444  0.356745               0.028872                 0.030792           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.45      0.75      0.527778  0.444042               0.028563                 0.024444           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.731184         0.131010     0.137806              tier0           mixed
  BRANCH     0.788838         0.086192     0.124970              tier0           mixed
   CACHE     0.558863         0.347991     0.093146              tier0           mixed
   MEMBW     0.803014         0.095351     0.101635              tier0           mixed
     TLB     0.735580         0.131120     0.133300              tier0           mixed
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC               memory_io       0.256127         0.436055             0.074011                 0.196430                 0.037378           mixed
  BRANCH               memory_io       0.229106         0.507494             0.044419                 0.172456                 0.046526           mixed
   CACHE               memory_io       0.448225         0.313866             0.060130                 0.128135                 0.049645           mixed
   MEMBW               memory_io       0.211656         0.534086             0.052254                 0.144641                 0.057364           mixed
     TLB               memory_io       0.281960         0.450074             0.063937                 0.172792                 0.031237           mixed
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
            tier0                    0.0                             0.0                           0.0                 0.30                    122.0                 642.5                 0.0                 0.2                0.25           mixed
      tier0_tier1                    0.0                             0.0                           0.0                 0.45                    122.0                 630.4                 0.0                 0.3                0.40           mixed
tier0_tier1_tier2                    0.0                             0.0                           0.0                 0.45                    122.0                 543.4                 0.0                 0.3                0.40           mixed
```

## Files
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B120_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B120_a0.05_k3/config_runtime_summary.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B120_a0.05_k3/run_context.json`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B120_a0.05_k3/case_inventory.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B120_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B120_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B120_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B120_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B120_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B120_a0.05_k3/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B120_a0.05_k3/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B120_a0.05_k3/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B120_a0.05_k3/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B120_a0.05_k3/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B120_a0.05_k3/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B120_a0.05_k3/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B120_a0.05_k3/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B120_a0.05_k3/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B120_a0.05_k3/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B120_a0.05_k3/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B120_a0.05_k3/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B120_a0.05_k3/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B120_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B120_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B120_a0.05_k3/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B120_a0.05_k3/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B120_a0.05_k3/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B120_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B120_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B120_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B120_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B120_a0.05_k3/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B120_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B120_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B120_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B120_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B120_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B120_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B120_a0.05_k3/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B120_a0.05_k3/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B120_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B120_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B120_a0.05_k3/figures/fig_detection_latency.png`
