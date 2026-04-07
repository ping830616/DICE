# DICE Full Retrain Results

## Setup
- Feature profile: mixed ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_core_5hz.csv', 'tier2': 'tier2_core_5hz.csv'})
- Protocol: global, benign-only fit/calibration, block_B=90, alpha=0.05, persist_k=3, gain=0.35
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
          mixed             tier0       24          46          2.233097   0.8000 0.931899         1.0        1.0            0.0           0.30              0.004903              0.010882                      0.0                 0.006095
          mixed       tier0_tier1       24          57          2.653509   0.8375 0.953625         1.0        1.0            0.0           0.45              0.000045              0.000111                      0.0                 0.000064
          mixed tier0_tier1_tier2       24          64          3.037922   0.8375 0.953625         1.0        1.0            0.0           0.45              0.000048              0.000120                      0.0                 0.000066
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
          mixed   ATOMIC   0.8125 0.804167         1.0        1.0          0.000048          0.000104                  0.0             0.000061       2.138469      0.000056         62.005104         0.000061
          mixed   BRANCH   0.9375 0.950000         1.0        1.0          0.000048          0.000177                  0.0             0.000120       3.636408      0.000129        120.723237         0.000120
          mixed    CACHE   0.8125 0.804167         1.0        1.0          0.000048          0.000104                  0.0             0.000062       2.153475      0.000056         62.825966         0.000062
          mixed    MEMBW   0.8750 0.887500         1.0        1.0          0.000048          0.000171                  0.0             0.000103       3.522922      0.000123        103.868486         0.000103
          mixed      TLB   0.7500 0.679167         1.0        1.0          0.000048          0.000116                  0.0             0.000058       2.393880      0.000068         58.990254         0.000058
```

## Paper-style Aggregates (Final Config)
- Base score mean stressor AUC-PR (all five): **0.8250**
- Base score mean stressor ROC-AUC (all five): **0.8375**
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
            tier0       20      0.40       0.6          0.40  0.322424               0.025262                 0.016051           mixed
      tier0_tier1       20      0.35       0.6          0.35  0.249451               0.024545                 0.021039           mixed
tier0_tier1_tier2       20      0.45       0.6          0.45  0.425641               0.022770                 0.020813           mixed
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.15      0.65          0.15  0.141538               0.016303                 0.015934           mixed
      tier0_tier1       20      0.25      0.50          0.25  0.180000               0.020171                 0.021922           mixed
tier0_tier1_tier2       20      0.15      0.40          0.15  0.136364               0.036639                 0.015560           mixed
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.30      0.75          0.30  0.297143               0.015336                 0.013444           mixed
      tier0_tier1       20      0.30      0.50          0.30  0.327619               0.013739                 0.007992           mixed
tier0_tier1_tier2       20      0.35      0.65          0.35  0.308889               0.013873                 0.012468           mixed
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.55      0.75      0.472222  0.398551               0.035112                 0.036276           mixed
      tier0_tier1       20      0.50      0.70      0.444444  0.356745               0.028527                 0.032412           mixed
tier0_tier1_tier2       20      0.45      0.75      0.527778  0.444042               0.028217                 0.026719           mixed
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.25      0.60         0.4          0.25  0.205253      0.40          0.60            0.375000            0.750000                0.333333            0.240000               0.002409                 0.011835            0.014217              0.010873           0.010475        0.101878           mixed
      tier0_tier1       20      0.25      0.60         0.4          0.25  0.206061      0.65          0.35            0.307692            0.461538                0.333333            0.257143               0.007223                 0.017610            0.017451              0.012655           0.012865        0.055456           mixed
tier0_tier1_tier2       20      0.35      0.55         0.4          0.35  0.339567      0.50          0.50            0.300000            0.600000                0.300000            0.280000               0.005945                 0.013614            0.017377              0.014790           0.008238        0.014917           mixed
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.20      0.60         0.4          0.20  0.163333       0.7           0.3            0.214286            0.642857                0.200000            0.157143              -0.006905                 0.005644            0.014217              0.010873           0.010475       -0.057977           mixed
      tier0_tier1       20      0.25      0.55         0.4          0.25  0.200427       0.8           0.2            0.250000            0.437500                0.266667            0.209870              -0.010978                 0.013694            0.017451              0.012655           0.012865       -0.077662           mixed
tier0_tier1_tier2       20      0.20      0.40         0.4          0.20  0.159091       0.4           0.6            0.125000            0.250000                0.125000            0.133333              -0.023024                 0.001637            0.017377              0.014790           0.008238       -0.034971           mixed
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0  conf_0.00              0.000000      12      0.60          0.40            0.333333            0.583333                0.333333            0.203175           mixed
            tier0  conf_0.05              0.050000      12      0.60          0.40            0.333333            0.583333                0.333333            0.203175           mixed
            tier0  conf_0.10              0.100000       6      0.30          0.70            0.333333            0.500000                0.166667            0.114286           mixed
            tier0    trained              0.101878       6      0.30          0.70            0.333333            0.500000                0.166667            0.114286           mixed
            tier0  conf_0.15              0.150000       4      0.20          0.80            0.500000            0.750000                0.333333            0.133333           mixed
            tier0  conf_0.20              0.200000       4      0.20          0.80            0.500000            0.750000                0.333333            0.133333           mixed
            tier0  conf_0.25              0.250000       3      0.15          0.85            0.666667            0.666667                0.666667            0.160000           mixed
      tier0_tier1  conf_0.00              0.000000      14      0.70          0.30            0.214286            0.500000                0.266667            0.146032           mixed
      tier0_tier1  conf_0.05              0.050000      12      0.60          0.40            0.250000            0.500000                0.300000            0.155556           mixed
      tier0_tier1    trained              0.055456      11      0.55          0.45            0.272727            0.454545                0.300000            0.166667           mixed
      tier0_tier1  conf_0.10              0.100000       9      0.45          0.55            0.333333            0.444444                0.300000            0.200000           mixed
      tier0_tier1  conf_0.15              0.150000       6      0.30          0.70            0.166667            0.333333                0.200000            0.133333           mixed
      tier0_tier1  conf_0.20              0.200000       2      0.10          0.90            0.000000            0.000000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.25              0.250000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.00              0.000000      13      0.65          0.35            0.384615            0.538462                0.483333            0.430000           mixed
tier0_tier1_tier2    trained              0.014917      12      0.60          0.40            0.333333            0.500000                0.433333            0.363333           mixed
tier0_tier1_tier2  conf_0.05              0.050000      11      0.55          0.45            0.272727            0.454545                0.366667            0.283333           mixed
tier0_tier1_tier2  conf_0.10              0.100000       8      0.40          0.60            0.125000            0.375000                0.125000            0.057143           mixed
tier0_tier1_tier2  conf_0.15              0.150000       5      0.25          0.75            0.200000            0.600000                0.333333            0.080000           mixed
tier0_tier1_tier2  conf_0.20              0.200000       2      0.10          0.90            0.500000            0.500000                0.500000            0.133333           mixed
tier0_tier1_tier2  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained             -0.057977      14      0.70          0.30            0.214286            0.642857                0.200000            0.157143           mixed
            tier0  conf_0.00              0.000000      13      0.65          0.35            0.153846            0.615385                0.166667            0.123810           mixed
            tier0  conf_0.05              0.050000       8      0.40          0.60            0.125000            0.375000                0.100000            0.100000           mixed
            tier0  conf_0.10              0.100000       8      0.40          0.60            0.125000            0.375000                0.100000            0.100000           mixed
            tier0  conf_0.15              0.150000       7      0.35          0.65            0.142857            0.285714                0.100000            0.100000           mixed
            tier0  conf_0.20              0.200000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000           mixed
            tier0  conf_0.25              0.250000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000           mixed
      tier0_tier1    trained             -0.077662      14      0.70          0.30            0.214286            0.428571                0.200000            0.129870           mixed
      tier0_tier1  conf_0.00              0.000000      14      0.70          0.30            0.214286            0.428571                0.200000            0.129870           mixed
      tier0_tier1  conf_0.05              0.050000      11      0.55          0.45            0.272727            0.363636                0.200000            0.146667           mixed
      tier0_tier1  conf_0.10              0.100000       6      0.30          0.70            0.166667            0.333333                0.125000            0.057143           mixed
      tier0_tier1  conf_0.15              0.150000       3      0.15          0.85            0.333333            0.666667                0.333333            0.100000           mixed
      tier0_tier1  conf_0.20              0.200000       2      0.10          0.90            0.000000            0.500000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.25              0.250000       1      0.05          0.95            0.000000            1.000000                0.000000            0.000000           mixed
tier0_tier1_tier2    trained             -0.034971      13      0.65          0.35            0.153846            0.384615                0.300000            0.180000           mixed
tier0_tier1_tier2  conf_0.00              0.000000      12      0.60          0.40            0.083333            0.333333                0.200000            0.080000           mixed
tier0_tier1_tier2  conf_0.05              0.050000       7      0.35          0.65            0.142857            0.285714                0.200000            0.133333           mixed
tier0_tier1_tier2  conf_0.10              0.100000       4      0.20          0.80            0.000000            0.250000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.15              0.150000       3      0.15          0.85            0.000000            0.333333                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.20              0.200000       2      0.10          0.90            0.000000            0.500000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.25              0.250000       2      0.10          0.90            0.000000            0.500000                0.000000            0.000000           mixed
```

## Diagnosis Mode Comparison
- Whole-run and post-alert-window diagnosis are exported together so the diagnosis mode can be evaluated directly.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile diagnosis_target    diagnosis_mode  family_acc  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau                       status  min_class_count  min_group_count    group_key  include_workload
            tier0       20      0.40      0.60      0.400000  0.322424               0.025262                 0.016051           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.35      0.60      0.350000  0.249451               0.024545                 0.021039           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.45      0.60      0.450000  0.425641               0.022770                 0.020813           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.15      0.65      0.150000  0.141538               0.016303                 0.015934           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.25      0.50      0.250000  0.180000               0.020171                 0.021922           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.15      0.40      0.150000  0.136364               0.036639                 0.015560           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.25      0.60      0.250000  0.205253               0.002409                 0.011835           mixed     hierarchical         whole_run         0.4      0.40          0.60            0.375000            0.750000                0.333333            0.240000            0.014217              0.010873           0.010475        0.101878                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.25      0.60      0.250000  0.206061               0.007223                 0.017610           mixed     hierarchical         whole_run         0.4      0.65          0.35            0.307692            0.461538                0.333333            0.257143            0.017451              0.012655           0.012865        0.055456                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.35      0.55      0.350000  0.339567               0.005945                 0.013614           mixed     hierarchical         whole_run         0.4      0.50          0.50            0.300000            0.600000                0.300000            0.280000            0.017377              0.014790           0.008238        0.014917                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.20      0.60      0.200000  0.163333              -0.006905                 0.005644           mixed     hierarchical post_alert_window         0.4      0.70          0.30            0.214286            0.642857                0.200000            0.157143            0.014217              0.010873           0.010475       -0.057977                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.25      0.55      0.250000  0.200427              -0.010978                 0.013694           mixed     hierarchical post_alert_window         0.4      0.80          0.20            0.250000            0.437500                0.266667            0.209870            0.017451              0.012655           0.012865       -0.077662                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.20      0.40      0.200000  0.159091              -0.023024                 0.001637           mixed     hierarchical post_alert_window         0.4      0.40          0.60            0.125000            0.250000                0.125000            0.133333            0.017377              0.014790           0.008238       -0.034971                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.55      0.75      0.472222  0.398551               0.035112                 0.036276           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.50      0.70      0.444444  0.356745               0.028527                 0.032412           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.45      0.75      0.527778  0.444042               0.028217                 0.026719           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.727893         0.130253     0.141854              tier0           mixed
  BRANCH     0.783457         0.085713     0.130830              tier0           mixed
   CACHE     0.556100         0.347215     0.096686              tier0           mixed
   MEMBW     0.797530         0.094426     0.108045              tier0           mixed
     TLB     0.729341         0.130721     0.139938              tier0           mixed
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC               memory_io       0.260404         0.425511             0.075136                 0.202765                 0.036184           mixed
  BRANCH               memory_io       0.236397         0.492674             0.045296                 0.180281                 0.045352           mixed
   CACHE               memory_io       0.453760         0.304066             0.060410                 0.133393                 0.048371           mixed
   MEMBW               memory_io       0.218525         0.518508             0.052853                 0.153102                 0.057013           mixed
     TLB               memory_io       0.288228         0.433985             0.065950                 0.181265                 0.030573           mixed
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
            tier0                    0.0                             0.0                           0.0                 0.30                     92.5                 689.5                 0.2                 0.2                0.25           mixed
      tier0_tier1                    0.0                             0.0                           0.0                 0.45                     92.0                 706.2                 0.3                 0.3                0.35           mixed
tier0_tier1_tier2                    0.0                             0.0                           0.0                 0.45                     92.0                 598.6                 0.3                 0.3                0.40           mixed
```

## Files
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B90_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B90_a0.05_k3/config_runtime_summary.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B90_a0.05_k3/run_context.json`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B90_a0.05_k3/case_inventory.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B90_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B90_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B90_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B90_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B90_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B90_a0.05_k3/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B90_a0.05_k3/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B90_a0.05_k3/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B90_a0.05_k3/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B90_a0.05_k3/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B90_a0.05_k3/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B90_a0.05_k3/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B90_a0.05_k3/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B90_a0.05_k3/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B90_a0.05_k3/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B90_a0.05_k3/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B90_a0.05_k3/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B90_a0.05_k3/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B90_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B90_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B90_a0.05_k3/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B90_a0.05_k3/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B90_a0.05_k3/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B90_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B90_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B90_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B90_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B90_a0.05_k3/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B90_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B90_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B90_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B90_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B90_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B90_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B90_a0.05_k3/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B90_a0.05_k3/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B90_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B90_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.35_B90_a0.05_k3/figures/fig_detection_latency.png`
