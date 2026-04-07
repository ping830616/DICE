# DICE Full Retrain Results

## Setup
- Feature profile: mixed ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_core_5hz.csv', 'tier2': 'tier2_core_5hz.csv'})
- Protocol: global, benign-only fit/calibration, block_B=60, alpha=0.05, persist_k=3, gain=0.5
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
          mixed             tier0       24          46          2.255627    0.800 0.931899         1.0        1.0            0.0            0.3              0.004166              0.008967                      0.0                 0.005044
          mixed       tier0_tier1       24          57          2.770101    0.825 0.951460         1.0        1.0            0.0            0.5              0.000046              0.000115                      0.0                 0.000057
          mixed tier0_tier1_tier2       24          64          3.197700    0.825 0.951460         1.0        1.0            0.0            0.5              0.000050              0.000125                      0.0                 0.000064
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
          mixed   ATOMIC   0.7500 0.770833         1.0        1.0           0.00005          0.000100                  0.0             0.000059       1.996369      0.000050         59.653087         0.000059
          mixed   BRANCH   0.9375 0.950000         1.0        1.0           0.00005          0.000196                  0.0             0.000129       3.884935      0.000146        129.829452         0.000129
          mixed    CACHE   0.8125 0.804167         1.0        1.0           0.00005          0.000102                  0.0             0.000063       2.028211      0.000052         63.960145         0.000063
          mixed    MEMBW   0.8750 0.887500         1.0        1.0           0.00005          0.000159                  0.0             0.000090       3.154938      0.000109         91.232902         0.000090
          mixed      TLB   0.7500 0.679167         1.0        1.0           0.00005          0.000115                  0.0             0.000051       2.282762      0.000065         52.095944         0.000051
```

## Paper-style Aggregates (Final Config)
- Base score mean stressor AUC-PR (all five): **0.8183**
- Base score mean stressor ROC-AUC (all five): **0.8250**
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
            tier0       20      0.40      0.55          0.40  0.307071               0.022469                 0.018635           mixed
      tier0_tier1       20      0.30      0.55          0.30  0.184615               0.024517                 0.025273           mixed
tier0_tier1_tier2       20      0.45      0.60          0.45  0.425641               0.021514                 0.019583           mixed
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.30      0.65          0.30  0.282597               0.015781                 0.014537           mixed
      tier0_tier1       20      0.15      0.30          0.15  0.080000               0.071586                 0.045931           mixed
tier0_tier1_tier2       20      0.15      0.40          0.15  0.166667               0.047288                 0.013882           mixed
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.35      0.70          0.35  0.358730               0.012569                 0.011176           mixed
      tier0_tier1       20      0.25      0.40          0.25  0.243175               0.017069                 0.014600           mixed
tier0_tier1_tier2       20      0.30      0.45          0.30  0.301587               0.014931                 0.013372           mixed
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.55      0.75      0.472222  0.398551               0.029980                 0.032589           mixed
      tier0_tier1       20      0.45      0.65      0.416667  0.333333               0.025732                 0.029671           mixed
tier0_tier1_tier2       20      0.45      0.75      0.527778  0.450142               0.028168                 0.027725           mixed
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.30      0.55        0.30          0.30  0.258889      0.30          0.70            0.500000            0.666667                0.416667            0.260000               0.014373                 0.013596            0.010213              0.007842           0.013019        0.139412           mixed
      tier0_tier1       20      0.15      0.45        0.25          0.15  0.120000      0.45          0.55            0.111111            0.444444                0.100000            0.100000               0.007714                 0.013854            0.017205              0.013583           0.012789        0.104976           mixed
tier0_tier1_tier2       20      0.35      0.50        0.30          0.35  0.351111      0.65          0.35            0.384615            0.538462                0.433333            0.374286               0.010962                 0.015131            0.018509              0.016168           0.011331       -0.034027           mixed
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.30      0.45        0.30          0.30  0.286364      0.85          0.15            0.294118            0.470588                0.333333            0.327778               0.008261                 0.013194            0.010213              0.007842           0.013019       -0.066567           mixed
      tier0_tier1       20      0.10      0.30        0.25          0.10  0.080000      0.40          0.60            0.000000            0.250000                0.000000            0.000000               0.003591                 0.023768            0.017205              0.013583           0.012789        0.127902           mixed
tier0_tier1_tier2       20      0.15      0.40        0.30          0.15  0.166364      0.60          0.40            0.083333            0.333333                0.100000            0.133333               0.000912                 0.008311            0.018509              0.016168           0.011331       -0.083813           mixed
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0  conf_0.00              0.000000      16      0.80          0.20            0.375000            0.562500                0.450000            0.288889           mixed
            tier0  conf_0.05              0.050000      11      0.55          0.45            0.545455            0.727273                0.483333            0.434286           mixed
            tier0  conf_0.10              0.100000       8      0.40          0.60            0.500000            0.625000                0.312500            0.220000           mixed
            tier0    trained              0.139412       6      0.30          0.70            0.500000            0.666667                0.250000            0.133333           mixed
            tier0  conf_0.15              0.150000       6      0.30          0.70            0.500000            0.666667                0.250000            0.133333           mixed
            tier0  conf_0.20              0.200000       5      0.25          0.75            0.600000            0.600000                0.375000            0.150000           mixed
            tier0  conf_0.25              0.250000       4      0.20          0.80            0.750000            0.750000                0.500000            0.171429           mixed
      tier0_tier1  conf_0.00              0.000000      14      0.70          0.30            0.071429            0.285714                0.200000            0.057143           mixed
      tier0_tier1  conf_0.05              0.050000      10      0.50          0.50            0.100000            0.300000                0.200000            0.080000           mixed
      tier0_tier1  conf_0.10              0.100000      10      0.50          0.50            0.100000            0.300000                0.200000            0.080000           mixed
      tier0_tier1    trained              0.104976      10      0.50          0.50            0.100000            0.300000                0.200000            0.080000           mixed
      tier0_tier1  conf_0.15              0.150000       5      0.25          0.75            0.000000            0.200000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.20              0.200000       4      0.20          0.80            0.000000            0.250000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.25              0.250000       1      0.05          0.95            0.000000            1.000000                0.000000            0.000000           mixed
tier0_tier1_tier2    trained             -0.034027      16      0.80          0.20            0.375000            0.500000                0.433333            0.385397           mixed
tier0_tier1_tier2  conf_0.00              0.000000      15      0.75          0.25            0.400000            0.533333                0.450000            0.410952           mixed
tier0_tier1_tier2  conf_0.05              0.050000      11      0.55          0.45            0.363636            0.454545                0.400000            0.323810           mixed
tier0_tier1_tier2  conf_0.10              0.100000       8      0.40          0.60            0.250000            0.375000                0.300000            0.166667           mixed
tier0_tier1_tier2  conf_0.15              0.150000       6      0.30          0.70            0.333333            0.500000                0.500000            0.213333           mixed
tier0_tier1_tier2  conf_0.20              0.200000       3      0.15          0.85            0.333333            0.666667                0.333333            0.100000           mixed
tier0_tier1_tier2  conf_0.25              0.250000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000           mixed
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained             -0.066567      18      0.90          0.10            0.333333            0.500000                0.350000            0.347778           mixed
            tier0  conf_0.00              0.000000      17      0.85          0.15            0.294118            0.470588                0.333333            0.327778           mixed
            tier0  conf_0.05              0.050000      13      0.65          0.35            0.230769            0.384615                0.266667            0.266667           mixed
            tier0  conf_0.10              0.100000       9      0.45          0.55            0.222222            0.444444                0.300000            0.213333           mixed
            tier0  conf_0.15              0.150000       5      0.25          0.75            0.000000            0.200000                0.000000            0.000000           mixed
            tier0  conf_0.20              0.200000       2      0.10          0.90            0.000000            0.000000                0.000000            0.000000           mixed
            tier0  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
      tier0_tier1  conf_0.00              0.000000      13      0.65          0.35            0.000000            0.230769                0.000000            0.000000           mixed
      tier0_tier1  conf_0.05              0.050000      12      0.60          0.40            0.000000            0.250000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.10              0.100000      11      0.55          0.45            0.000000            0.181818                0.000000            0.000000           mixed
      tier0_tier1    trained              0.127902      10      0.50          0.50            0.000000            0.200000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.15              0.150000       9      0.45          0.55            0.000000            0.222222                0.000000            0.000000           mixed
      tier0_tier1  conf_0.20              0.200000       9      0.45          0.55            0.000000            0.222222                0.000000            0.000000           mixed
      tier0_tier1  conf_0.25              0.250000       6      0.30          0.70            0.000000            0.333333                0.000000            0.000000           mixed
tier0_tier1_tier2    trained             -0.083813      15      0.75          0.25            0.133333            0.400000                0.150000            0.177778           mixed
tier0_tier1_tier2  conf_0.00              0.000000      15      0.75          0.25            0.133333            0.400000                0.150000            0.177778           mixed
tier0_tier1_tier2  conf_0.05              0.050000       9      0.45          0.55            0.000000            0.222222                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.10              0.100000       6      0.30          0.70            0.000000            0.333333                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.15              0.150000       6      0.30          0.70            0.000000            0.333333                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.20              0.200000       3      0.15          0.85            0.000000            0.333333                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.25              0.250000       3      0.15          0.85            0.000000            0.333333                0.000000            0.000000           mixed
```

## Diagnosis Mode Comparison
- Whole-run and post-alert-window diagnosis are exported together so the diagnosis mode can be evaluated directly.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile diagnosis_target    diagnosis_mode  family_acc  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau                       status  min_class_count  min_group_count    group_key  include_workload
            tier0       20      0.40      0.55      0.400000  0.307071               0.022469                 0.018635           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.30      0.55      0.300000  0.184615               0.024517                 0.025273           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.45      0.60      0.450000  0.425641               0.021514                 0.019583           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.30      0.65      0.300000  0.282597               0.015781                 0.014537           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.15      0.30      0.150000  0.080000               0.071586                 0.045931           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.15      0.40      0.150000  0.166667               0.047288                 0.013882           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.30      0.55      0.300000  0.258889               0.014373                 0.013596           mixed     hierarchical         whole_run        0.30      0.30          0.70            0.500000            0.666667                0.416667            0.260000            0.010213              0.007842           0.013019        0.139412                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.15      0.45      0.150000  0.120000               0.007714                 0.013854           mixed     hierarchical         whole_run        0.25      0.45          0.55            0.111111            0.444444                0.100000            0.100000            0.017205              0.013583           0.012789        0.104976                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.35      0.50      0.350000  0.351111               0.010962                 0.015131           mixed     hierarchical         whole_run        0.30      0.65          0.35            0.384615            0.538462                0.433333            0.374286            0.018509              0.016168           0.011331       -0.034027                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.30      0.45      0.300000  0.286364               0.008261                 0.013194           mixed     hierarchical post_alert_window        0.30      0.85          0.15            0.294118            0.470588                0.333333            0.327778            0.010213              0.007842           0.013019       -0.066567                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.10      0.30      0.100000  0.080000               0.003591                 0.023768           mixed     hierarchical post_alert_window        0.25      0.40          0.60            0.000000            0.250000                0.000000            0.000000            0.017205              0.013583           0.012789        0.127902                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.15      0.40      0.150000  0.166364               0.000912                 0.008311           mixed     hierarchical post_alert_window        0.30      0.60          0.40            0.083333            0.333333                0.100000            0.133333            0.018509              0.016168           0.011331       -0.083813                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.55      0.75      0.472222  0.398551               0.029980                 0.032589           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.45      0.65      0.416667  0.333333               0.025732                 0.029671           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.45      0.75      0.527778  0.450142               0.028168                 0.027725           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.735133         0.119353     0.145514              tier0           mixed
  BRANCH     0.779016         0.083311     0.137673              tier0           mixed
   CACHE     0.557169         0.341746     0.101085              tier0           mixed
   MEMBW     0.793418         0.089684     0.116898              tier0           mixed
     TLB     0.729004         0.122619     0.148377              tier0           mixed
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC               memory_io       0.267672         0.415793             0.069296                 0.213299                 0.033940           mixed
  BRANCH               memory_io       0.245092         0.470412             0.046467                 0.195159                 0.042870           mixed
   CACHE               memory_io       0.458475         0.295635             0.058550                 0.143809                 0.043531           mixed
   MEMBW               memory_io       0.226260         0.497556             0.052245                 0.169698                 0.054242           mixed
     TLB               memory_io       0.295545         0.413623             0.064355                 0.196801                 0.029676           mixed
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
            tier0                    0.0                             0.0                           0.0                  0.3                     73.5                 734.0                 0.2                 0.2                0.20           mixed
      tier0_tier1                    0.0                             0.0                           0.0                  0.5                     76.0                 835.6                 0.3                 0.3                0.35           mixed
tier0_tier1_tier2                    0.0                             0.0                           0.0                  0.5                     73.0                 834.7                 0.3                 0.3                0.35           mixed
```

## Files
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B60_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B60_a0.05_k3/config_runtime_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B60_a0.05_k3/run_context.json`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B60_a0.05_k3/case_inventory.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B60_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B60_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B60_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B60_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B60_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B60_a0.05_k3/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B60_a0.05_k3/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B60_a0.05_k3/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B60_a0.05_k3/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B60_a0.05_k3/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B60_a0.05_k3/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B60_a0.05_k3/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B60_a0.05_k3/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B60_a0.05_k3/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B60_a0.05_k3/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B60_a0.05_k3/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B60_a0.05_k3/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B60_a0.05_k3/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B60_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B60_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B60_a0.05_k3/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B60_a0.05_k3/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B60_a0.05_k3/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B60_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B60_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B60_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B60_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B60_a0.05_k3/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B60_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B60_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B60_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B60_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B60_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B60_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B60_a0.05_k3/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B60_a0.05_k3/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B60_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B60_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B60_a0.05_k3/figures/fig_detection_latency.png`
