# DICE Full Retrain Results

## Setup
- Feature profile: mixed ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_core_5hz.csv', 'tier2': 'tier2_core_5hz.csv'})
- Protocol: global, benign-only fit/calibration, block_B=45, alpha=0.05, persist_k=3, gain=0.5
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
          mixed             tier0       24          46          2.353615   0.7875 0.921899         1.0        1.0            0.0            0.3              0.004442              0.009197                      0.0                 0.005188
          mixed       tier0_tier1       24          57          2.829012   0.8250 0.951460         1.0        1.0            0.0            0.5              0.000049              0.000116                      0.0                 0.000056
          mixed tier0_tier1_tier2       24          64          3.194330   0.8250 0.951460         1.0        1.0            0.0            0.5              0.000052              0.000129                      0.0                 0.000063
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
          mixed   ATOMIC   0.7500 0.770833         1.0        1.0          0.000052          0.000099                  0.0             0.000055       1.887928      0.000047         55.741952         0.000055
          mixed   BRANCH   0.9375 0.950000         1.0        1.0          0.000052          0.000199                  0.0             0.000127       3.787332      0.000147        127.747794         0.000127
          mixed    CACHE   0.8125 0.804167         1.0        1.0          0.000052          0.000103                  0.0             0.000063       1.968024      0.000051         64.244331         0.000063
          mixed    MEMBW   0.8750 0.887500         1.0        1.0          0.000052          0.000155                  0.0             0.000086       2.959419      0.000104         87.196698         0.000086
          mixed      TLB   0.7500 0.679167         1.0        1.0          0.000052          0.000114                  0.0             0.000047       2.176360      0.000062         47.990972         0.000047
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
            tier0       20      0.40      0.55          0.40  0.317980               0.022186                 0.018011           mixed
      tier0_tier1       20      0.30      0.55          0.30  0.184615               0.024110                 0.024631           mixed
tier0_tier1_tier2       20      0.45      0.60          0.45  0.425641               0.021062                 0.018405           mixed
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20       0.3      0.55           0.3  0.281457               0.014851                 0.012720           mixed
      tier0_tier1       20       0.1      0.30           0.1  0.057143               0.076775                 0.043237           mixed
tier0_tier1_tier2       20       0.2      0.45           0.2  0.180952               0.054875                 0.013980           mixed
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.35      0.65          0.35  0.358730               0.011821                 0.010590           mixed
      tier0_tier1       20      0.20      0.50          0.20  0.203175               0.018502                 0.015568           mixed
tier0_tier1_tier2       20      0.25      0.50          0.25  0.255556               0.014258                 0.011027           mixed
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.55      0.75      0.472222  0.398551               0.029049                 0.031710           mixed
      tier0_tier1       20      0.45      0.65      0.416667  0.333333               0.024759                 0.028678           mixed
tier0_tier1_tier2       20      0.45      0.75      0.527778  0.444042               0.028227                 0.028192           mixed
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.25      0.55         0.3          0.25  0.208889      0.25          0.75            0.600000            0.800000                0.500000            0.333333               0.012309                 0.010060            0.009308              0.006824           0.012766        0.181815           mixed
      tier0_tier1       20      0.20      0.45         0.3          0.20  0.161616      0.45          0.55            0.222222            0.444444                0.300000            0.213333               0.010498                 0.022681            0.017298              0.014334           0.010800        0.116475           mixed
tier0_tier1_tier2       20      0.35      0.50         0.3          0.35  0.351111      0.65          0.35            0.384615            0.538462                0.433333            0.374286               0.011246                 0.012764            0.017878              0.011884           0.009639       -0.031234           mixed
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.20      0.45         0.3          0.20  0.172222       0.8           0.2              0.1875               0.375                0.166667            0.151587               0.003981                 0.009330            0.009308              0.006824           0.012766       -0.054026           mixed
      tier0_tier1       20      0.10      0.30         0.3          0.10  0.088889       0.5           0.5              0.1000               0.300                0.100000            0.133333               0.030604                 0.027953            0.017298              0.014334           0.010800        0.129550           mixed
tier0_tier1_tier2       20      0.15      0.40         0.3          0.15  0.166364       0.4           0.6              0.0000               0.125                0.000000            0.000000               0.003556                 0.009565            0.017878              0.011884           0.009639        0.070184           mixed
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0  conf_0.00              0.000000      15      0.75          0.25            0.333333            0.533333                0.312500            0.208889           mixed
            tier0  conf_0.05              0.050000      11      0.55          0.45            0.454545            0.636364                0.354167            0.234286           mixed
            tier0  conf_0.10              0.100000       8      0.40          0.60            0.500000            0.625000                0.312500            0.220000           mixed
            tier0  conf_0.15              0.150000       6      0.30          0.70            0.500000            0.666667                0.250000            0.133333           mixed
            tier0    trained              0.181815       6      0.30          0.70            0.500000            0.666667                0.250000            0.133333           mixed
            tier0  conf_0.20              0.200000       5      0.25          0.75            0.600000            0.600000                0.375000            0.150000           mixed
            tier0  conf_0.25              0.250000       4      0.20          0.80            0.750000            0.750000                0.500000            0.171429           mixed
      tier0_tier1  conf_0.00              0.000000      15      0.75          0.25            0.133333            0.333333                0.200000            0.088889           mixed
      tier0_tier1  conf_0.05              0.050000      11      0.55          0.45            0.181818            0.363636                0.200000            0.114286           mixed
      tier0_tier1  conf_0.10              0.100000      11      0.55          0.45            0.181818            0.363636                0.200000            0.114286           mixed
      tier0_tier1    trained              0.116475       9      0.45          0.55            0.111111            0.222222                0.200000            0.100000           mixed
      tier0_tier1  conf_0.15              0.150000       6      0.30          0.70            0.166667            0.333333                0.200000            0.133333           mixed
      tier0_tier1  conf_0.20              0.200000       3      0.15          0.85            0.000000            0.333333                0.000000            0.000000           mixed
      tier0_tier1  conf_0.25              0.250000       1      0.05          0.95            0.000000            1.000000                0.000000            0.000000           mixed
tier0_tier1_tier2    trained             -0.031234      16      0.80          0.20            0.375000            0.500000                0.433333            0.385397           mixed
tier0_tier1_tier2  conf_0.00              0.000000      15      0.75          0.25            0.400000            0.533333                0.450000            0.410952           mixed
tier0_tier1_tier2  conf_0.05              0.050000      11      0.55          0.45            0.363636            0.454545                0.366667            0.323810           mixed
tier0_tier1_tier2  conf_0.10              0.100000       9      0.45          0.55            0.333333            0.444444                0.400000            0.300000           mixed
tier0_tier1_tier2  conf_0.15              0.150000       5      0.25          0.75            0.400000            0.600000                0.500000            0.233333           mixed
tier0_tier1_tier2  conf_0.20              0.200000       3      0.15          0.85            0.333333            0.666667                0.333333            0.100000           mixed
tier0_tier1_tier2  conf_0.25              0.250000       2      0.10          0.90            0.000000            0.500000                0.000000            0.000000           mixed
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained             -0.054026      16      0.80          0.20            0.187500            0.375000                0.166667            0.151587           mixed
            tier0  conf_0.00              0.000000      16      0.80          0.20            0.187500            0.375000                0.166667            0.151587           mixed
            tier0  conf_0.05              0.050000      11      0.55          0.45            0.181818            0.363636                0.166667            0.146667           mixed
            tier0  conf_0.10              0.100000       7      0.35          0.65            0.285714            0.428571                0.375000            0.266667           mixed
            tier0  conf_0.15              0.150000       5      0.25          0.75            0.400000            0.600000                0.666667            0.333333           mixed
            tier0  conf_0.20              0.200000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000           mixed
            tier0  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
      tier0_tier1  conf_0.00              0.000000      14      0.70          0.30            0.000000            0.214286                0.000000            0.000000           mixed
      tier0_tier1  conf_0.05              0.050000      12      0.60          0.40            0.000000            0.166667                0.000000            0.000000           mixed
      tier0_tier1  conf_0.10              0.100000      11      0.55          0.45            0.000000            0.181818                0.000000            0.000000           mixed
      tier0_tier1    trained              0.129550      10      0.50          0.50            0.000000            0.200000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.15              0.150000      10      0.50          0.50            0.000000            0.200000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.20              0.200000       9      0.45          0.55            0.000000            0.222222                0.000000            0.000000           mixed
      tier0_tier1  conf_0.25              0.250000       7      0.35          0.65            0.000000            0.285714                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.00              0.000000      14      0.70          0.30            0.142857            0.357143                0.166667            0.183333           mixed
tier0_tier1_tier2  conf_0.05              0.050000       9      0.45          0.55            0.000000            0.222222                0.000000            0.000000           mixed
tier0_tier1_tier2    trained              0.070184       6      0.30          0.70            0.000000            0.333333                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.10              0.100000       6      0.30          0.70            0.000000            0.333333                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.15              0.150000       6      0.30          0.70            0.000000            0.333333                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.20              0.200000       4      0.20          0.80            0.000000            0.250000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.25              0.250000       3      0.15          0.85            0.000000            0.333333                0.000000            0.000000           mixed
```

## Diagnosis Mode Comparison
- Whole-run and post-alert-window diagnosis are exported together so the diagnosis mode can be evaluated directly.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile diagnosis_target    diagnosis_mode  family_acc  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau                       status  min_class_count  min_group_count    group_key  include_workload
            tier0       20      0.40      0.55      0.400000  0.317980               0.022186                 0.018011           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.30      0.55      0.300000  0.184615               0.024110                 0.024631           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.45      0.60      0.450000  0.425641               0.021062                 0.018405           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.30      0.55      0.300000  0.281457               0.014851                 0.012720           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.10      0.30      0.100000  0.057143               0.076775                 0.043237           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.20      0.45      0.200000  0.180952               0.054875                 0.013980           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.25      0.55      0.250000  0.208889               0.012309                 0.010060           mixed     hierarchical         whole_run         0.3      0.25          0.75            0.600000            0.800000                0.500000            0.333333            0.009308              0.006824           0.012766        0.181815                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.20      0.45      0.200000  0.161616               0.010498                 0.022681           mixed     hierarchical         whole_run         0.3      0.45          0.55            0.222222            0.444444                0.300000            0.213333            0.017298              0.014334           0.010800        0.116475                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.35      0.50      0.350000  0.351111               0.011246                 0.012764           mixed     hierarchical         whole_run         0.3      0.65          0.35            0.384615            0.538462                0.433333            0.374286            0.017878              0.011884           0.009639       -0.031234                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.20      0.45      0.200000  0.172222               0.003981                 0.009330           mixed     hierarchical post_alert_window         0.3      0.80          0.20            0.187500            0.375000                0.166667            0.151587            0.009308              0.006824           0.012766       -0.054026                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.10      0.30      0.100000  0.088889               0.030604                 0.027953           mixed     hierarchical post_alert_window         0.3      0.50          0.50            0.100000            0.300000                0.100000            0.133333            0.017298              0.014334           0.010800        0.129550                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.15      0.40      0.150000  0.166364               0.003556                 0.009565           mixed     hierarchical post_alert_window         0.3      0.40          0.60            0.000000            0.125000                0.000000            0.000000            0.017878              0.011884           0.009639        0.070184                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.55      0.75      0.472222  0.398551               0.029049                 0.031710           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.45      0.65      0.416667  0.333333               0.024759                 0.028678           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.45      0.75      0.527778  0.444042               0.028227                 0.028192           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.732897         0.118862     0.148240              tier0           mixed
  BRANCH     0.776272         0.081968     0.141761              tier0           mixed
   CACHE     0.554439         0.341898     0.103663              tier0           mixed
   MEMBW     0.789847         0.088639     0.121515              tier0           mixed
     TLB     0.724512         0.122173     0.153315              tier0           mixed
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC               memory_io       0.269003         0.410395             0.070860                 0.217231                 0.032512           mixed
  BRANCH               memory_io       0.247520         0.463350             0.046852                 0.201195                 0.041084           mixed
   CACHE               memory_io       0.460982         0.289660             0.060149                 0.147278                 0.041931           mixed
   MEMBW               memory_io       0.229378         0.488514             0.053156                 0.175833                 0.053119           mixed
     TLB               memory_io       0.297847         0.404563             0.066062                 0.202980                 0.028548           mixed
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
            tier0                    0.0                             0.0                      1.884817                  0.3                     62.5                 662.5                 0.2                 0.2                0.25           mixed
      tier0_tier1                    0.0                             0.0                      0.000000                  0.5                     63.5                 834.6                 0.3                 0.3                0.35           mixed
tier0_tier1_tier2                    0.0                             0.0                      0.000000                  0.5                     62.5                 833.7                 0.3                 0.3                0.40           mixed
```

## Files
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B45_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B45_a0.05_k3/config_runtime_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B45_a0.05_k3/run_context.json`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B45_a0.05_k3/case_inventory.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B45_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B45_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B45_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B45_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B45_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B45_a0.05_k3/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B45_a0.05_k3/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B45_a0.05_k3/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B45_a0.05_k3/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B45_a0.05_k3/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B45_a0.05_k3/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B45_a0.05_k3/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B45_a0.05_k3/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B45_a0.05_k3/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B45_a0.05_k3/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B45_a0.05_k3/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B45_a0.05_k3/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B45_a0.05_k3/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B45_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B45_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B45_a0.05_k3/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B45_a0.05_k3/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B45_a0.05_k3/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B45_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B45_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B45_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B45_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B45_a0.05_k3/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B45_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B45_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B45_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B45_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B45_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B45_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B45_a0.05_k3/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B45_a0.05_k3/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B45_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B45_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.5_B45_a0.05_k3/figures/fig_detection_latency.png`
