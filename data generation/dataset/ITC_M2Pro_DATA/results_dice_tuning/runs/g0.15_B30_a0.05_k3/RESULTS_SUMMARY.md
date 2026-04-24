# DICE Full Retrain Results

## Setup
- Feature profile: mixed ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_core_5hz.csv', 'tier2': 'tier2_core_5hz.csv'})
- Protocol: global, benign-only fit/calibration, block_B=30, alpha=0.05, persist_k=3, gain=0.15
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
          mixed             tier0       24          46          3.031691   0.8000 0.931899         1.0        1.0           0.25           0.30              0.011353              0.023357                      0.0                 0.012710
          mixed       tier0_tier1       24          57          3.229253   0.8375 0.957016         1.0        1.0           0.25           0.55              0.000044              0.000113                      0.0                 0.000052
          mixed tier0_tier1_tier2       24          64          3.341892   0.8500 0.962016         1.0        1.0           0.00           0.55              0.000047              0.000120                      0.0                 0.000056
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
          mixed   ATOMIC   0.7500 0.770833         1.0        1.0          0.000047          0.000091                  0.0             0.000041       1.916407      0.000044         41.947972         0.000041
          mixed   BRANCH   0.9375 0.950000         1.0        1.0          0.000047          0.000189                  0.0             0.000135       3.977285      0.000142        135.948580         0.000135
          mixed    CACHE   0.8125 0.804167         1.0        1.0          0.000047          0.000100                  0.0             0.000056       2.100190      0.000053         57.030674         0.000056
          mixed    MEMBW   0.9375 0.950000         1.0        1.0          0.000047          0.000145                  0.0             0.000081       3.057149      0.000098         82.293975         0.000081
          mixed      TLB   0.8125 0.804167         1.0        1.0          0.000047          0.000107                  0.0             0.000046       2.259590      0.000060         47.374077         0.000046
```

## Paper-style Aggregates (Final Config)
- Base score mean stressor AUC-PR (all five): **0.8558**
- Base score mean stressor ROC-AUC (all five): **0.8500**
- WC score mean stressor AUC-PR (all five): **1.0000**
- WC score mean stressor ROC-AUC (all five): **1.0000**
- Base score mean stressor AUC-PR (excluding BRANCH/TLB): **0.8417**
- Base score mean stressor ROC-AUC (excluding BRANCH/TLB): **0.8333**
- WC score mean stressor AUC-PR (excluding BRANCH/TLB): **1.0000**
- WC score mean stressor ROC-AUC (excluding BRANCH/TLB): **1.0000**

## Diagnosis
- Feature-level diagnosis uses normalized whole-run residual-attribution prototypes as the default paper-facing result, with diagnosis-only filtering that removes monotonic counters and downweights generic memory-state features.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20       0.3      0.55           0.3  0.232900               0.027017                 0.021021           mixed
      tier0_tier1       20       0.3      0.65           0.3  0.274237               0.017039                 0.013143           mixed
tier0_tier1_tier2       20       0.5      0.80           0.5  0.528571               0.014832                 0.010030           mixed
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.25      0.50          0.25  0.212727               0.017396                 0.014295           mixed
      tier0_tier1       20      0.15      0.35          0.15  0.146667               0.105113                 0.055503           mixed
tier0_tier1_tier2       20      0.15      0.35          0.15  0.164444               0.099542                 0.032555           mixed
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.25      0.55          0.25  0.226364               0.016676                 0.010039           mixed
      tier0_tier1       20      0.40      0.60          0.40  0.388889               0.016269                 0.012866           mixed
tier0_tier1_tier2       20      0.30      0.60          0.30  0.287013               0.014225                 0.012509           mixed
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.60      0.85      0.500000  0.421818               0.034120                 0.036788           mixed
      tier0_tier1       20      0.45      0.75      0.416667  0.335664               0.023366                 0.028363           mixed
tier0_tier1_tier2       20      0.55      0.75      0.527778  0.487179               0.023803                 0.024462           mixed
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.40      0.60        0.50          0.40  0.331313      0.50          0.50            0.400000            0.500000                0.400000            0.260000               0.001758                 0.011079            0.016657              0.017394           0.012575        0.113357           mixed
      tier0_tier1       20      0.25      0.65        0.35          0.25  0.208205      0.70          0.30            0.285714            0.642857                0.266667            0.246667              -0.000020                 0.004935            0.024470              0.026009           0.012137        0.009571           mixed
tier0_tier1_tier2       20      0.35      0.75        0.35          0.35  0.311429      0.45          0.55            0.555556            0.888889                0.600000            0.493333               0.000524                 0.004621            0.022934              0.021482           0.014003        0.078949           mixed
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.40      0.65        0.50          0.40  0.364444      0.55          0.45            0.272727            0.454545                0.150000            0.120000              -0.014215                 0.006782            0.016657              0.017394           0.012575        0.004508           mixed
      tier0_tier1       20      0.30      0.35        0.35          0.30  0.201399      0.55          0.45            0.363636            0.363636                0.333333            0.247619              -0.060568                -0.016324            0.024470              0.026009           0.012137       -0.159366           mixed
tier0_tier1_tier2       20      0.15      0.30        0.35          0.15  0.106667      0.60          0.40            0.083333            0.250000                0.066667            0.050000               0.023189                 0.000880            0.022934              0.021482           0.014003       -0.098292           mixed
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0  conf_0.00              0.000000      13      0.65          0.35            0.384615            0.538462                0.350000            0.269091           mixed
            tier0  conf_0.05              0.050000      11      0.55          0.45            0.454545            0.545455                0.400000            0.280000           mixed
            tier0  conf_0.10              0.100000       6      0.30          0.70            0.500000            0.500000                0.400000            0.260000           mixed
            tier0    trained              0.113357       6      0.30          0.70            0.500000            0.500000                0.400000            0.260000           mixed
            tier0  conf_0.15              0.150000       6      0.30          0.70            0.500000            0.500000                0.400000            0.260000           mixed
            tier0  conf_0.20              0.200000       4      0.20          0.80            0.500000            0.500000                0.333333            0.160000           mixed
            tier0  conf_0.25              0.250000       3      0.15          0.85            0.666667            0.666667                0.500000            0.200000           mixed
      tier0_tier1  conf_0.00              0.000000      14      0.70          0.30            0.214286            0.642857                0.233333            0.196667           mixed
      tier0_tier1    trained              0.009571      11      0.55          0.45            0.272727            0.545455                0.233333            0.237143           mixed
      tier0_tier1  conf_0.05              0.050000       7      0.35          0.65            0.285714            0.714286                0.333333            0.166667           mixed
      tier0_tier1  conf_0.10              0.100000       5      0.25          0.75            0.200000            0.600000                0.333333            0.066667           mixed
      tier0_tier1  conf_0.15              0.150000       5      0.25          0.75            0.200000            0.600000                0.333333            0.066667           mixed
      tier0_tier1  conf_0.20              0.200000       1      0.05          0.95            1.000000            1.000000                1.000000            0.200000           mixed
      tier0_tier1  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
tier0_tier1_tier2  conf_0.00              0.000000      14      0.70          0.30            0.428571            0.714286                0.366667            0.364286           mixed
tier0_tier1_tier2  conf_0.05              0.050000       7      0.35          0.65            0.285714            0.714286                0.375000            0.257143           mixed
tier0_tier1_tier2    trained              0.078949       4      0.20          0.80            0.250000            0.500000                0.333333            0.080000           mixed
tier0_tier1_tier2  conf_0.10              0.100000       4      0.20          0.80            0.250000            0.500000                0.333333            0.080000           mixed
tier0_tier1_tier2  conf_0.15              0.150000       2      0.10          0.90            0.500000            0.500000                0.500000            0.133333           mixed
tier0_tier1_tier2  conf_0.20              0.200000       1      0.05          0.95            1.000000            1.000000                1.000000            0.200000           mixed
tier0_tier1_tier2  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0  conf_0.00              0.000000      13      0.65          0.35            0.307692            0.538462                0.216667            0.200000           mixed
            tier0    trained              0.004508      13      0.65          0.35            0.307692            0.538462                0.216667            0.200000           mixed
            tier0  conf_0.05              0.050000       9      0.45          0.55            0.222222            0.444444                0.133333            0.114286           mixed
            tier0  conf_0.10              0.100000       5      0.25          0.75            0.400000            0.400000                0.250000            0.200000           mixed
            tier0  conf_0.15              0.150000       2      0.10          0.90            0.500000            0.500000                0.500000            0.200000           mixed
            tier0  conf_0.20              0.200000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
            tier0  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
      tier0_tier1    trained             -0.159366      12      0.60          0.40            0.416667            0.416667                0.416667            0.293333           mixed
      tier0_tier1  conf_0.00              0.000000      10      0.50          0.50            0.300000            0.300000                0.416667            0.240000           mixed
      tier0_tier1  conf_0.05              0.050000       6      0.30          0.70            0.000000            0.000000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.10              0.100000       6      0.30          0.70            0.000000            0.000000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.15              0.150000       5      0.25          0.75            0.000000            0.000000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.20              0.200000       3      0.15          0.85            0.000000            0.000000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.25              0.250000       3      0.15          0.85            0.000000            0.000000                0.000000            0.000000           mixed
tier0_tier1_tier2    trained             -0.098292      14      0.70          0.30            0.142857            0.285714                0.133333            0.114286           mixed
tier0_tier1_tier2  conf_0.00              0.000000      12      0.60          0.40            0.083333            0.166667                0.066667            0.066667           mixed
tier0_tier1_tier2  conf_0.05              0.050000       8      0.40          0.60            0.000000            0.125000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.10              0.100000       8      0.40          0.60            0.000000            0.125000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.15              0.150000       6      0.30          0.70            0.000000            0.166667                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.20              0.200000       5      0.25          0.75            0.000000            0.200000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.25              0.250000       4      0.20          0.80            0.000000            0.250000                0.000000            0.000000           mixed
```

## Diagnosis Mode Comparison
- Whole-run and post-alert-window diagnosis are exported together so the diagnosis mode can be evaluated directly.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile diagnosis_target    diagnosis_mode  family_acc  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau                       status  min_class_count  min_group_count    group_key  include_workload
            tier0       20      0.30      0.55      0.300000  0.232900               0.027017                 0.021021           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.30      0.65      0.300000  0.274237               0.017039                 0.013143           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.50      0.80      0.500000  0.528571               0.014832                 0.010030           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.25      0.50      0.250000  0.212727               0.017396                 0.014295           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.15      0.35      0.150000  0.146667               0.105113                 0.055503           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.15      0.35      0.150000  0.164444               0.099542                 0.032555           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.40      0.60      0.400000  0.331313               0.001758                 0.011079           mixed     hierarchical         whole_run        0.50      0.50          0.50            0.400000            0.500000                0.400000            0.260000            0.016657              0.017394           0.012575        0.113357                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.25      0.65      0.250000  0.208205              -0.000020                 0.004935           mixed     hierarchical         whole_run        0.35      0.70          0.30            0.285714            0.642857                0.266667            0.246667            0.024470              0.026009           0.012137        0.009571                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.35      0.75      0.350000  0.311429               0.000524                 0.004621           mixed     hierarchical         whole_run        0.35      0.45          0.55            0.555556            0.888889                0.600000            0.493333            0.022934              0.021482           0.014003        0.078949                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.40      0.65      0.400000  0.364444              -0.014215                 0.006782           mixed     hierarchical post_alert_window        0.50      0.55          0.45            0.272727            0.454545                0.150000            0.120000            0.016657              0.017394           0.012575        0.004508                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.30      0.35      0.300000  0.201399              -0.060568                -0.016324           mixed     hierarchical post_alert_window        0.35      0.55          0.45            0.363636            0.363636                0.333333            0.247619            0.024470              0.026009           0.012137       -0.159366                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.15      0.30      0.150000  0.106667               0.023189                 0.000880           mixed     hierarchical post_alert_window        0.35      0.60          0.40            0.083333            0.250000                0.066667            0.050000            0.022934              0.021482           0.014003       -0.098292                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.60      0.85      0.500000  0.421818               0.034120                 0.036788           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.45      0.75      0.416667  0.335664               0.023366                 0.028363           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.55      0.75      0.527778  0.487179               0.023803                 0.024462           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.683510         0.160098     0.156392              tier0           mixed
  BRANCH     0.752727         0.094024     0.153249              tier0           mixed
   CACHE     0.531680         0.358405     0.109914              tier0           mixed
   MEMBW     0.771161         0.099806     0.129033              tier0           mixed
     TLB     0.686951         0.150491     0.162558              tier0           mixed
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC               memory_io       0.266891         0.388121             0.103460                 0.210507                 0.031020           mixed
  BRANCH               memory_io       0.249703         0.450115             0.054448                 0.201304                 0.044431           mixed
   CACHE                 compute       0.474165         0.261333             0.073695                 0.142128                 0.048679           mixed
   MEMBW               memory_io       0.240777         0.466822             0.060946                 0.174425                 0.057029           mixed
     TLB               memory_io       0.305185         0.382624             0.086025                 0.198340                 0.027826           mixed
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
            tier0                   0.25                        0.927835                      2.783505                 0.30                     54.0                 603.5                0.20                0.20                0.25           mixed
      tier0_tier1                   0.25                        0.927835                      2.783505                 0.55                     77.0                 819.0                0.30                0.30                0.45           mixed
tier0_tier1_tier2                   0.00                        0.000000                      0.000000                 0.55                     38.0                 818.0                0.35                0.35                0.45           mixed
```

## Files
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.05_k3/config_runtime_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.05_k3/run_context.json`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.05_k3/case_inventory.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.05_k3/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.05_k3/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.05_k3/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.05_k3/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.05_k3/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.05_k3/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.05_k3/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.05_k3/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.05_k3/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.05_k3/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.05_k3/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.05_k3/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.05_k3/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.05_k3/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.05_k3/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.05_k3/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.05_k3/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.05_k3/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.05_k3/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.15_B30_a0.05_k3/figures/fig_detection_latency.png`
