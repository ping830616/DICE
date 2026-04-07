# DICE Full Retrain Results

## Setup
- Feature profile: full ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_full_5hz.csv', 'tier2': 'tier2_full_5hz.csv'})
- Protocol: global, benign-only fit/calibration, block_B=20, alpha=0.05, persist_k=3, gain=0.25
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
           full             tier0       24          46          2.232123   0.7625 0.917472         1.0        1.0           0.25           0.35              0.008961              0.017210                      0.0                 0.009635
           full       tier0_tier1       24          64          2.925517   0.8250 0.955040         1.0        1.0           0.25           0.65              0.015026              0.038008                      0.0                 0.016041
           full tier0_tier1_tier2       24          75          3.503615   0.9500 0.989710         1.0        1.0           0.25           0.95              0.002972              0.007543                      0.0                 0.004102
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc  pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
           full   ATOMIC   0.9375    0.95         1.0        1.0          0.002972          0.006734                  0.0             0.003358       2.265311      0.003762       3359.128727         0.003358
           full   BRANCH   0.9375    0.95         1.0        1.0          0.002972          0.010954                  0.0             0.007746       3.684867      0.007982       7747.346450         0.007746
           full    CACHE   0.9375    0.95         1.0        1.0          0.002972          0.008733                  0.0             0.005587       2.937525      0.005760       5588.269529         0.005587
           full    MEMBW   1.0000    1.00         1.0        1.0          0.002972          0.008094                  0.0             0.004308       2.722676      0.005122       4308.914619         0.004308
           full      TLB   0.9375    0.95         1.0        1.0          0.002972          0.007584                  0.0             0.004838       2.551203      0.004612       4838.614414         0.004838
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
            tier0       20      0.30      0.65          0.30  0.248485               0.026242                 0.023077            full
      tier0_tier1       20      0.15      0.40          0.15  0.133333               0.012777                 0.009970            full
tier0_tier1_tier2       20      0.30      0.45          0.30  0.206667               0.019635                 0.018907            full
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.25      0.45          0.25  0.243175               0.016344                 0.016186            full
      tier0_tier1       20      0.10      0.40          0.10  0.100000               0.108142                 0.055094            full
tier0_tier1_tier2       20      0.10      0.25          0.10  0.086364               0.022279                 0.016639            full
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.25      0.55          0.25  0.217778               0.012318                 0.006776            full
      tier0_tier1       20      0.20      0.55          0.20  0.152727               0.019989                 0.014896            full
tier0_tier1_tier2       20      0.40      0.65          0.40  0.357013               0.017711                 0.013275            full
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.55       0.8      0.472222  0.398551               0.034342                 0.037228            full
      tier0_tier1       20      0.45       0.8      0.361111  0.307359               0.021839                 0.024659            full
tier0_tier1_tier2       20      0.50       0.9      0.555556  0.495951               0.015339                 0.014946            full
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.35      0.65        0.50          0.35  0.277980      0.35          0.65            0.428571            0.714286                0.333333            0.226667               0.002023                 0.009380            0.012265              0.010666           0.011619        0.138387            full
      tier0_tier1       20      0.10      0.45        0.45          0.10  0.114286      0.55          0.45            0.000000            0.363636                0.000000            0.000000               0.004956                 0.007309            0.020098              0.019075           0.009405        0.022921            full
tier0_tier1_tier2       20      0.25      0.45        0.40          0.25  0.180000      0.50          0.50            0.300000            0.500000                0.333333            0.188889               0.013906                 0.017702            0.020977              0.018023           0.011057        0.081966            full
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.35      0.50        0.50          0.35  0.352222      0.50          0.50            0.200000            0.300000                0.116667            0.107143              -0.022038                 0.002707            0.012265              0.010666           0.011619        0.044987            full
      tier0_tier1       20      0.10      0.40        0.45          0.10  0.080769      0.25          0.75            0.000000            0.600000                0.000000            0.000000              -0.026415                 0.017968            0.020098              0.019075           0.009405        0.491255            full
tier0_tier1_tier2       20      0.15      0.35        0.40          0.15  0.136364      0.70          0.30            0.071429            0.357143                0.050000            0.040000              -0.000071                 0.006572            0.020977              0.018023           0.011057       -0.126948            full
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0  conf_0.00              0.000000      13      0.65          0.35            0.384615            0.692308                0.283333            0.242424            full
            tier0  conf_0.05              0.050000      11      0.55          0.45            0.454545            0.727273                0.283333            0.242424            full
            tier0  conf_0.10              0.100000       9      0.45          0.55            0.444444            0.666667                0.333333            0.233333            full
            tier0    trained              0.138387       5      0.25          0.75            0.600000            0.600000                0.555556            0.266667            full
            tier0  conf_0.15              0.150000       5      0.25          0.75            0.600000            0.600000                0.555556            0.266667            full
            tier0  conf_0.20              0.200000       3      0.15          0.85            0.666667            0.666667                0.666667            0.160000            full
            tier0  conf_0.25              0.250000       3      0.15          0.85            0.666667            0.666667                0.666667            0.160000            full
      tier0_tier1  conf_0.00              0.000000      14      0.70          0.30            0.071429            0.428571                0.100000            0.080000            full
      tier0_tier1    trained              0.022921      12      0.60          0.40            0.083333            0.333333                0.100000            0.080000            full
      tier0_tier1  conf_0.05              0.050000       8      0.40          0.60            0.000000            0.250000                0.000000            0.000000            full
      tier0_tier1  conf_0.10              0.100000       5      0.25          0.75            0.000000            0.400000                0.000000            0.000000            full
      tier0_tier1  conf_0.15              0.150000       1      0.05          0.95            0.000000            1.000000                0.000000            0.000000            full
      tier0_tier1  conf_0.20              0.200000       1      0.05          0.95            0.000000            1.000000                0.000000            0.000000            full
      tier0_tier1  conf_0.25              0.250000       1      0.05          0.95            0.000000            1.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.00              0.000000      17      0.85          0.15            0.235294            0.411765                0.250000            0.172308            full
tier0_tier1_tier2  conf_0.05              0.050000      14      0.70          0.30            0.285714            0.500000                0.250000            0.192308            full
tier0_tier1_tier2    trained              0.081966      12      0.60          0.40            0.250000            0.500000                0.233333            0.172727            full
tier0_tier1_tier2  conf_0.10              0.100000      11      0.55          0.45            0.272727            0.545455                0.300000            0.180000            full
tier0_tier1_tier2  conf_0.15              0.150000       4      0.20          0.80            0.000000            0.250000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.20              0.200000       3      0.15          0.85            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.25              0.250000       2      0.10          0.90            0.000000            0.000000                0.000000            0.000000            full
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0  conf_0.00              0.000000      12      0.60          0.40            0.333333            0.416667                0.266667            0.272222            full
            tier0    trained              0.044987       6      0.30          0.70            0.333333            0.500000                0.333333            0.146667            full
            tier0  conf_0.05              0.050000       6      0.30          0.70            0.333333            0.500000                0.333333            0.146667            full
            tier0  conf_0.10              0.100000       6      0.30          0.70            0.333333            0.500000                0.333333            0.146667            full
            tier0  conf_0.15              0.150000       2      0.10          0.90            0.500000            0.500000                0.500000            0.200000            full
            tier0  conf_0.20              0.200000       2      0.10          0.90            0.500000            0.500000                0.500000            0.200000            full
            tier0  conf_0.25              0.250000       1      0.05          0.95            1.000000            1.000000                1.000000            0.200000            full
      tier0_tier1  conf_0.00              0.000000      12      0.60          0.40            0.083333            0.500000                0.050000            0.050000            full
      tier0_tier1  conf_0.05              0.050000      11      0.55          0.45            0.090909            0.545455                0.066667            0.057143            full
      tier0_tier1  conf_0.10              0.100000       8      0.40          0.60            0.000000            0.500000                0.000000            0.000000            full
      tier0_tier1  conf_0.15              0.150000       8      0.40          0.60            0.000000            0.500000                0.000000            0.000000            full
      tier0_tier1  conf_0.20              0.200000       7      0.35          0.65            0.000000            0.571429                0.000000            0.000000            full
      tier0_tier1  conf_0.25              0.250000       7      0.35          0.65            0.000000            0.571429                0.000000            0.000000            full
      tier0_tier1    trained              0.491255       2      0.10          0.90            0.000000            1.000000                0.000000            0.000000            full
tier0_tier1_tier2    trained             -0.126948      17      0.85          0.15            0.117647            0.352941                0.116667            0.136364            full
tier0_tier1_tier2  conf_0.00              0.000000      11      0.55          0.45            0.000000            0.181818                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.05              0.050000       9      0.45          0.55            0.000000            0.222222                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.10              0.100000       6      0.30          0.70            0.000000            0.166667                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.15              0.150000       4      0.20          0.80            0.000000            0.250000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.20              0.200000       4      0.20          0.80            0.000000            0.250000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.25              0.250000       3      0.15          0.85            0.000000            0.000000                0.000000            0.000000            full
```

## Diagnosis Mode Comparison
- Whole-run and post-alert-window diagnosis are exported together so the diagnosis mode can be evaluated directly.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile diagnosis_target    diagnosis_mode  family_acc  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau                       status  min_class_count  min_group_count    group_key  include_workload
            tier0       20      0.30      0.65      0.300000  0.248485               0.026242                 0.023077            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.15      0.40      0.150000  0.133333               0.012777                 0.009970            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.30      0.45      0.300000  0.206667               0.019635                 0.018907            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.25      0.45      0.250000  0.243175               0.016344                 0.016186            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.10      0.40      0.100000  0.100000               0.108142                 0.055094            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.10      0.25      0.100000  0.086364               0.022279                 0.016639            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.35      0.65      0.350000  0.277980               0.002023                 0.009380            full     hierarchical         whole_run        0.50      0.35          0.65            0.428571            0.714286                0.333333            0.226667            0.012265              0.010666           0.011619        0.138387                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.10      0.45      0.100000  0.114286               0.004956                 0.007309            full     hierarchical         whole_run        0.45      0.55          0.45            0.000000            0.363636                0.000000            0.000000            0.020098              0.019075           0.009405        0.022921                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.25      0.45      0.250000  0.180000               0.013906                 0.017702            full     hierarchical         whole_run        0.40      0.50          0.50            0.300000            0.500000                0.333333            0.188889            0.020977              0.018023           0.011057        0.081966                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.35      0.50      0.350000  0.352222              -0.022038                 0.002707            full     hierarchical post_alert_window        0.50      0.50          0.50            0.200000            0.300000                0.116667            0.107143            0.012265              0.010666           0.011619        0.044987                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.10      0.40      0.100000  0.080769              -0.026415                 0.017968            full     hierarchical post_alert_window        0.45      0.25          0.75            0.000000            0.600000                0.000000            0.000000            0.020098              0.019075           0.009405        0.491255                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.15      0.35      0.150000  0.136364              -0.000071                 0.006572            full     hierarchical post_alert_window        0.40      0.70          0.30            0.071429            0.357143                0.050000            0.040000            0.020977              0.018023           0.011057       -0.126948                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.55      0.80      0.472222  0.398551               0.034342                 0.037228            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.45      0.80      0.361111  0.307359               0.021839                 0.024659            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.50      0.90      0.555556  0.495951               0.015339                 0.014946            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.577880         0.271578     0.150543              tier0            full
  BRANCH     0.609611         0.218997     0.171392              tier0            full
   CACHE     0.477122         0.203281     0.319597              tier0            full
   MEMBW     0.621402         0.242520     0.136078              tier0            full
     TLB     0.551460         0.280488     0.168052              tier0            full
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC                 compute       0.359768         0.289501             0.120795                 0.129861                 0.100076            full
  BRANCH                 compute       0.320639         0.351291             0.086443                 0.170466                 0.071161            full
   CACHE                 compute       0.492918         0.272531             0.076071                 0.095934                 0.062545            full
   MEMBW                 compute       0.332353         0.331635             0.108417                 0.130752                 0.096843            full
     TLB                 compute       0.358581         0.302189             0.121387                 0.135464                 0.082379            full
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
            tier0                   0.25                        2.755102                      4.591837                 0.35                     71.0                 551.2                0.25                0.25                0.30            full
      tier0_tier1                   0.25                        2.755102                      4.591837                 0.65                     33.0                 752.0                0.50                0.50                0.55            full
tier0_tier1_tier2                   0.25                        2.755102                      4.591837                 0.95                     22.0                 542.2                0.75                0.75                0.85            full
```

## Files
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B20_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B20_a0.05_k3/config_runtime_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B20_a0.05_k3/run_context.json`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B20_a0.05_k3/case_inventory.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B20_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B20_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B20_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B20_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B20_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B20_a0.05_k3/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B20_a0.05_k3/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B20_a0.05_k3/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B20_a0.05_k3/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B20_a0.05_k3/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B20_a0.05_k3/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B20_a0.05_k3/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B20_a0.05_k3/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B20_a0.05_k3/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B20_a0.05_k3/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B20_a0.05_k3/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B20_a0.05_k3/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B20_a0.05_k3/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B20_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B20_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B20_a0.05_k3/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B20_a0.05_k3/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B20_a0.05_k3/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B20_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B20_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B20_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B20_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B20_a0.05_k3/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B20_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B20_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B20_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B20_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B20_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B20_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B20_a0.05_k3/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B20_a0.05_k3/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B20_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B20_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B20_a0.05_k3/figures/fig_detection_latency.png`
