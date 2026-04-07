# DICE Full Retrain Results

## Setup
- Feature profile: mixed ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_core_5hz.csv', 'tier2': 'tier2_core_5hz.csv'})
- Protocol: global, benign-only fit/calibration, block_B=120, alpha=0.05, persist_k=3, gain=0.25
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
          mixed             tier0       24          46          2.133458   0.7875 0.921899         1.0        1.0            0.0           0.30              0.005726              0.013224                      0.0                 0.007681
          mixed       tier0_tier1       24          57          2.591482   0.8125 0.940232         1.0        1.0            0.0           0.45              0.000046              0.000115                      0.0                 0.000063
          mixed tier0_tier1_tier2       24          64          2.971421   0.8250 0.947375         1.0        1.0            0.0           0.45              0.000050              0.000127                      0.0                 0.000066
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
          mixed   ATOMIC   0.8125 0.804167         1.0        1.0           0.00005          0.000108                  0.0             0.000065       2.119666      0.000057         66.189769         0.000065
          mixed   BRANCH   0.8750 0.887500         1.0        1.0           0.00005          0.000173                  0.0             0.000118       3.395941      0.000123        119.173190         0.000118
          mixed    CACHE   0.8125 0.804167         1.0        1.0           0.00005          0.000108                  0.0             0.000061       2.127517      0.000058         62.438069         0.000061
          mixed    MEMBW   0.8750 0.887500         1.0        1.0           0.00005          0.000170                  0.0             0.000098       3.340954      0.000120         99.058001         0.000098
          mixed      TLB   0.7500 0.679167         1.0        1.0           0.00005          0.000113                  0.0             0.000057       2.231566      0.000063         57.956635         0.000057
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
            tier0       20       0.3      0.55           0.3  0.238961               0.028662                 0.021739           mixed
      tier0_tier1       20       0.3      0.65           0.3  0.215035               0.023459                 0.018879           mixed
tier0_tier1_tier2       20       0.5      0.70           0.5  0.486593               0.022967                 0.017494           mixed
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.15      0.65          0.15  0.153333               0.017588                 0.016077           mixed
      tier0_tier1       20      0.20      0.40          0.20  0.200000               0.042451                 0.032239           mixed
tier0_tier1_tier2       20      0.10      0.40          0.10  0.088889               0.031827                 0.014954           mixed
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20       0.4      0.65           0.4  0.373810               0.015777                 0.013746           mixed
      tier0_tier1       20       0.3      0.65           0.3  0.280952               0.014116                 0.008251           mixed
tier0_tier1_tier2       20       0.4      0.65           0.4  0.402222               0.012759                 0.009756           mixed
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.60      0.80      0.500000  0.421818               0.038262                 0.035942           mixed
      tier0_tier1       20      0.45      0.80      0.416667  0.335664               0.029069                 0.030834           mixed
tier0_tier1_tier2       20      0.55      0.75      0.583333  0.531039               0.029194                 0.029852           mixed
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20       0.4      0.55        0.55           0.4  0.320000      0.25          0.75            0.400000            0.400000                0.333333            0.160000              -0.010341                 0.007364            0.016378              0.017851           0.012289        0.132349           mixed
      tier0_tier1       20       0.3      0.65        0.30           0.3  0.209091      0.65          0.35            0.384615            0.615385                0.350000            0.242424               0.003158                 0.001355            0.019335              0.016424           0.014147        0.024283           mixed
tier0_tier1_tier2       20       0.5      0.70        0.30           0.5  0.480000      0.75          0.25            0.533333            0.800000                0.533333            0.528571               0.009348                 0.013748            0.018755              0.012388           0.010936       -0.022338           mixed
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.40      0.65        0.55          0.40  0.353680       0.7           0.3            0.428571            0.714286                0.433333            0.380000              -0.010484                 0.005169            0.016378              0.017851           0.012289       -0.044984           mixed
      tier0_tier1       20      0.25      0.45        0.30          0.25  0.197980       0.7           0.3            0.285714            0.500000                0.233333            0.247619              -0.012687                 0.008603            0.019335              0.016424           0.014147       -0.044333           mixed
tier0_tier1_tier2       20      0.25      0.50        0.30          0.25  0.214444       0.6           0.4            0.250000            0.500000                0.200000            0.194286              -0.006497                 0.003132            0.018755              0.012388           0.010936       -0.048731           mixed
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0  conf_0.00              0.000000      11      0.55          0.45            0.454545            0.545455                0.400000            0.293333           mixed
            tier0  conf_0.05              0.050000       8      0.40          0.60            0.500000            0.500000                0.400000            0.293333           mixed
            tier0  conf_0.10              0.100000       6      0.30          0.70            0.500000            0.500000                0.500000            0.293333           mixed
            tier0    trained              0.132349       5      0.25          0.75            0.400000            0.400000                0.333333            0.160000           mixed
            tier0  conf_0.15              0.150000       3      0.15          0.85            0.666667            0.666667                0.500000            0.160000           mixed
            tier0  conf_0.20              0.200000       3      0.15          0.85            0.666667            0.666667                0.500000            0.160000           mixed
            tier0  conf_0.25              0.250000       2      0.10          0.90            1.000000            1.000000                1.000000            0.200000           mixed
      tier0_tier1  conf_0.00              0.000000      12      0.60          0.40            0.250000            0.583333                0.150000            0.109091           mixed
      tier0_tier1    trained              0.024283       9      0.45          0.55            0.333333            0.444444                0.187500            0.109091           mixed
      tier0_tier1  conf_0.05              0.050000       8      0.40          0.60            0.375000            0.500000                0.250000            0.120000           mixed
      tier0_tier1  conf_0.10              0.100000       7      0.35          0.65            0.428571            0.571429                0.333333            0.120000           mixed
      tier0_tier1  conf_0.15              0.150000       4      0.20          0.80            0.250000            0.250000                0.333333            0.080000           mixed
      tier0_tier1  conf_0.20              0.200000       4      0.20          0.80            0.250000            0.250000                0.333333            0.080000           mixed
      tier0_tier1  conf_0.25              0.250000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000           mixed
tier0_tier1_tier2    trained             -0.022338      16      0.80          0.20            0.562500            0.687500                0.600000            0.555758           mixed
tier0_tier1_tier2  conf_0.00              0.000000      14      0.70          0.30            0.571429            0.714286                0.616667            0.566667           mixed
tier0_tier1_tier2  conf_0.05              0.050000      13      0.65          0.35            0.538462            0.692308                0.566667            0.486667           mixed
tier0_tier1_tier2  conf_0.10              0.100000       7      0.35          0.65            0.428571            0.571429                0.500000            0.300000           mixed
tier0_tier1_tier2  conf_0.15              0.150000       6      0.30          0.70            0.333333            0.500000                0.333333            0.100000           mixed
tier0_tier1_tier2  conf_0.20              0.200000       4      0.20          0.80            0.500000            0.500000                0.333333            0.133333           mixed
tier0_tier1_tier2  conf_0.25              0.250000       2      0.10          0.90            0.500000            0.500000                0.500000            0.133333           mixed
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained             -0.044984      13      0.65          0.35            0.384615            0.692308                0.400000            0.346667           mixed
            tier0  conf_0.00              0.000000      11      0.55          0.45            0.363636            0.636364                0.300000            0.293333           mixed
            tier0  conf_0.05              0.050000       8      0.40          0.60            0.250000            0.500000                0.200000            0.160000           mixed
            tier0  conf_0.10              0.100000       6      0.30          0.70            0.166667            0.500000                0.250000            0.133333           mixed
            tier0  conf_0.15              0.150000       5      0.25          0.75            0.200000            0.600000                0.333333            0.200000           mixed
            tier0  conf_0.20              0.200000       3      0.15          0.85            0.333333            1.000000                0.333333            0.200000           mixed
            tier0  conf_0.25              0.250000       1      0.05          0.95            0.000000            1.000000                0.000000            0.000000           mixed
      tier0_tier1    trained             -0.044333      13      0.65          0.35            0.230769            0.461538                0.200000            0.214286           mixed
      tier0_tier1  conf_0.00              0.000000      12      0.60          0.40            0.250000            0.500000                0.200000            0.247619           mixed
      tier0_tier1  conf_0.05              0.050000      10      0.50          0.50            0.200000            0.500000                0.100000            0.114286           mixed
      tier0_tier1  conf_0.10              0.100000       6      0.30          0.70            0.333333            0.666667                0.166667            0.160000           mixed
      tier0_tier1  conf_0.15              0.150000       5      0.25          0.75            0.400000            0.600000                0.250000            0.200000           mixed
      tier0_tier1  conf_0.20              0.200000       4      0.20          0.80            0.250000            0.500000                0.250000            0.200000           mixed
      tier0_tier1  conf_0.25              0.250000       4      0.20          0.80            0.250000            0.500000                0.250000            0.200000           mixed
tier0_tier1_tier2    trained             -0.048731      13      0.65          0.35            0.153846            0.461538                0.200000            0.166667           mixed
tier0_tier1_tier2  conf_0.00              0.000000      13      0.65          0.35            0.153846            0.461538                0.200000            0.166667           mixed
tier0_tier1_tier2  conf_0.05              0.050000       6      0.30          0.70            0.000000            0.333333                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.10              0.100000       6      0.30          0.70            0.000000            0.333333                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.15              0.150000       5      0.25          0.75            0.000000            0.200000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.20              0.200000       3      0.15          0.85            0.000000            0.333333                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.25              0.250000       3      0.15          0.85            0.000000            0.333333                0.000000            0.000000           mixed
```

## Diagnosis Mode Comparison
- Whole-run and post-alert-window diagnosis are exported together so the diagnosis mode can be evaluated directly.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile diagnosis_target    diagnosis_mode  family_acc  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau                       status  min_class_count  min_group_count    group_key  include_workload
            tier0       20      0.30      0.55      0.300000  0.238961               0.028662                 0.021739           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.30      0.65      0.300000  0.215035               0.023459                 0.018879           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.50      0.70      0.500000  0.486593               0.022967                 0.017494           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.15      0.65      0.150000  0.153333               0.017588                 0.016077           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.20      0.40      0.200000  0.200000               0.042451                 0.032239           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.10      0.40      0.100000  0.088889               0.031827                 0.014954           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.40      0.55      0.400000  0.320000              -0.010341                 0.007364           mixed     hierarchical         whole_run        0.55      0.25          0.75            0.400000            0.400000                0.333333            0.160000            0.016378              0.017851           0.012289        0.132349                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.30      0.65      0.300000  0.209091               0.003158                 0.001355           mixed     hierarchical         whole_run        0.30      0.65          0.35            0.384615            0.615385                0.350000            0.242424            0.019335              0.016424           0.014147        0.024283                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.50      0.70      0.500000  0.480000               0.009348                 0.013748           mixed     hierarchical         whole_run        0.30      0.75          0.25            0.533333            0.800000                0.533333            0.528571            0.018755              0.012388           0.010936       -0.022338                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.40      0.65      0.400000  0.353680              -0.010484                 0.005169           mixed     hierarchical post_alert_window        0.55      0.70          0.30            0.428571            0.714286                0.433333            0.380000            0.016378              0.017851           0.012289       -0.044984                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.25      0.45      0.250000  0.197980              -0.012687                 0.008603           mixed     hierarchical post_alert_window        0.30      0.70          0.30            0.285714            0.500000                0.233333            0.247619            0.019335              0.016424           0.014147       -0.044333                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.25      0.50      0.250000  0.214444              -0.006497                 0.003132           mixed     hierarchical post_alert_window        0.30      0.60          0.40            0.250000            0.500000                0.200000            0.194286            0.018755              0.012388           0.010936       -0.048731                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.60      0.80      0.500000  0.421818               0.038262                 0.035942           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.45      0.80      0.416667  0.335664               0.029069                 0.030834           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.55      0.75      0.583333  0.531039               0.029194                 0.029852           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.720535         0.142183     0.137283              tier0           mixed
  BRANCH     0.785828         0.089002     0.125171              tier0           mixed
   CACHE     0.555868         0.351219     0.092914              tier0           mixed
   MEMBW     0.800862         0.098490     0.100649              tier0           mixed
     TLB     0.728825         0.138377     0.132798              tier0           mixed
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC               memory_io       0.255525         0.434236             0.081117                 0.191446                 0.037676           mixed
  BRANCH               memory_io       0.227704         0.508651             0.045753                 0.169149                 0.048743           mixed
   CACHE               memory_io       0.451516         0.309153             0.062352                 0.124469                 0.052510           mixed
   MEMBW               memory_io       0.214003         0.530969             0.053462                 0.140853                 0.060713           mixed
     TLB               memory_io       0.283821         0.448965             0.067602                 0.168197                 0.031415           mixed
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
            tier0                    0.0                             0.0                           0.0                 0.30                    122.0                 644.0                 0.0                 0.2                0.25           mixed
      tier0_tier1                    0.0                             0.0                           0.0                 0.45                    122.0                 562.6                 0.0                 0.3                0.40           mixed
tier0_tier1_tier2                    0.0                             0.0                           0.0                 0.45                    122.0                 544.6                 0.0                 0.3                0.40           mixed
```

## Files
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B120_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B120_a0.05_k3/config_runtime_summary.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B120_a0.05_k3/run_context.json`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B120_a0.05_k3/case_inventory.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B120_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B120_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B120_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B120_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B120_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B120_a0.05_k3/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B120_a0.05_k3/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B120_a0.05_k3/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B120_a0.05_k3/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B120_a0.05_k3/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B120_a0.05_k3/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B120_a0.05_k3/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B120_a0.05_k3/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B120_a0.05_k3/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B120_a0.05_k3/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B120_a0.05_k3/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B120_a0.05_k3/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B120_a0.05_k3/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B120_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B120_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B120_a0.05_k3/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B120_a0.05_k3/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B120_a0.05_k3/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B120_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B120_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B120_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B120_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B120_a0.05_k3/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B120_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B120_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B120_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B120_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B120_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B120_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B120_a0.05_k3/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B120_a0.05_k3/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B120_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B120_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.25_B120_a0.05_k3/figures/fig_detection_latency.png`
