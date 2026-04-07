# DICE Full Retrain Results

## Setup
- Feature profile: full ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_full_5hz.csv', 'tier2': 'tier2_full_5hz.csv'})
- Protocol: global, benign-only fit/calibration, block_B=30, alpha=0.05, persist_k=3, gain=0.5
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
           full             tier0       24          46          2.292327   0.7750 0.919734         1.0        1.0           0.25           0.30              0.004801              0.009448                      0.0                 0.005130
           full       tier0_tier1       24          64          3.051614   0.8125 0.949484         1.0        1.0           0.25           0.65              0.008005              0.020517                      0.0                 0.009483
           full tier0_tier1_tier2       24          75          3.629930   0.9500 0.989710         1.0        1.0           0.25           0.95              0.002613              0.007015                      0.0                 0.003896
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc  pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
           full   ATOMIC   0.9375    0.95         1.0        1.0          0.002613          0.006055                  0.0             0.002501       2.316324      0.003441       2502.082079         0.002501
           full   BRANCH   0.9375    0.95         1.0        1.0          0.002613          0.009909                  0.0             0.006662       3.790594      0.007295       6662.736786         0.006662
           full    CACHE   0.9375    0.95         1.0        1.0          0.002613          0.007893                  0.0             0.004813       3.019452      0.005279       4814.254339         0.004813
           full    MEMBW   1.0000    1.00         1.0        1.0          0.002613          0.007191                  0.0             0.004055       2.750854      0.004577       4056.493493         0.004055
           full      TLB   0.9375    0.95         1.0        1.0          0.002613          0.007335                  0.0             0.004386       2.806032      0.004722       4386.506057         0.004386
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
            tier0       20       0.4      0.50           0.4  0.338889               0.022843                 0.017983            full
      tier0_tier1       20       0.3      0.35           0.3  0.225758               0.019554                 0.017492            full
tier0_tier1_tier2       20       0.3      0.40           0.3  0.200000               0.022092                 0.022639            full
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.15      0.50          0.15  0.154286               0.016017                 0.014935            full
      tier0_tier1       20      0.15      0.25          0.15  0.137143               0.103156                 0.033042            full
tier0_tier1_tier2       20      0.10      0.30          0.10  0.094444               0.014428                 0.008170            full
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.40      0.60          0.40  0.403175               0.010773                 0.006097            full
      tier0_tier1       20      0.35      0.50          0.35  0.306667               0.018095                 0.013539            full
tier0_tier1_tier2       20      0.40      0.55          0.40  0.376104               0.016172                 0.012974            full
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.50      0.75      0.444444  0.378788               0.028843                 0.031042            full
      tier0_tier1       20      0.50      0.75      0.388889  0.342995               0.029843                 0.033171            full
tier0_tier1_tier2       20      0.45      0.95      0.583333  0.458333               0.016207                 0.016074            full
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.25      0.50         0.4          0.25  0.197980      0.35          0.65            0.428571            0.571429                0.333333            0.260000               0.013267                 0.011441            0.008541              0.007048           0.009274        0.159320            full
      tier0_tier1       20      0.25      0.45         0.5          0.25  0.240476      0.50          0.50            0.200000            0.300000                0.266667            0.257143              -0.005373                 0.006283            0.016326              0.015484           0.006973        0.018156            full
tier0_tier1_tier2       20      0.20      0.35         0.4          0.20  0.153333      0.50          0.50            0.200000            0.200000                0.300000            0.166667               0.008884                 0.016352            0.020263              0.018695           0.007763        0.111953            full
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.15      0.40         0.4          0.15  0.144444      0.80          0.20            0.125000            0.312500                0.116667            0.111111              -0.000754                 0.012707            0.008541              0.007048           0.009274       -0.076248            full
      tier0_tier1       20      0.20      0.30         0.5          0.20  0.161538      0.30          0.70            0.000000            0.166667                0.000000            0.000000              -0.005575                 0.011986            0.016326              0.015484           0.006973        0.409819            full
tier0_tier1_tier2       20      0.25      0.35         0.4          0.25  0.246667      0.65          0.35            0.153846            0.307692                0.133333            0.150000              -0.007514                -0.015371            0.020263              0.018695           0.007763       -0.173993            full
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0  conf_0.00              0.000000      16      0.80          0.20            0.312500            0.437500                0.312500            0.197980            full
            tier0  conf_0.05              0.050000      11      0.55          0.45            0.454545            0.545455                0.354167            0.234286            full
            tier0  conf_0.10              0.100000       8      0.40          0.60            0.500000            0.625000                0.312500            0.220000            full
            tier0  conf_0.15              0.150000       6      0.30          0.70            0.500000            0.666667                0.250000            0.133333            full
            tier0    trained              0.159320       6      0.30          0.70            0.500000            0.666667                0.250000            0.133333            full
            tier0  conf_0.20              0.200000       5      0.25          0.75            0.600000            0.600000                0.375000            0.150000            full
            tier0  conf_0.25              0.250000       5      0.25          0.75            0.600000            0.600000                0.375000            0.150000            full
      tier0_tier1  conf_0.00              0.000000      12      0.60          0.40            0.250000            0.333333                0.266667            0.203810            full
      tier0_tier1    trained              0.018156      11      0.55          0.45            0.181818            0.272727                0.166667            0.137143            full
      tier0_tier1  conf_0.05              0.050000       9      0.45          0.55            0.222222            0.222222                0.277778            0.137143            full
      tier0_tier1  conf_0.10              0.100000       4      0.20          0.80            0.000000            0.000000                0.000000            0.000000            full
      tier0_tier1  conf_0.15              0.150000       2      0.10          0.90            0.000000            0.000000                0.000000            0.000000            full
      tier0_tier1  conf_0.20              0.200000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000            full
      tier0_tier1  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN            full
tier0_tier1_tier2  conf_0.00              0.000000      16      0.80          0.20            0.187500            0.312500                0.200000            0.146667            full
tier0_tier1_tier2  conf_0.05              0.050000      11      0.55          0.45            0.181818            0.363636                0.133333            0.080000            full
tier0_tier1_tier2  conf_0.10              0.100000      10      0.50          0.50            0.200000            0.400000                0.133333            0.080000            full
tier0_tier1_tier2    trained              0.111953       9      0.45          0.55            0.222222            0.444444                0.200000            0.088889            full
tier0_tier1_tier2  conf_0.15              0.150000       6      0.30          0.70            0.166667            0.333333                0.250000            0.080000            full
tier0_tier1_tier2  conf_0.20              0.200000       4      0.20          0.80            0.250000            0.250000                0.333333            0.080000            full
tier0_tier1_tier2  conf_0.25              0.250000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000            full
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained             -0.076248      15      0.75          0.25            0.133333            0.333333                0.145833            0.111111            full
            tier0  conf_0.00              0.000000      15      0.75          0.25            0.133333            0.333333                0.145833            0.111111            full
            tier0  conf_0.05              0.050000      12      0.60          0.40            0.166667            0.333333                0.208333            0.123810            full
            tier0  conf_0.10              0.100000       8      0.40          0.60            0.250000            0.500000                0.375000            0.180000            full
            tier0  conf_0.15              0.150000       5      0.25          0.75            0.400000            0.400000                0.500000            0.300000            full
            tier0  conf_0.20              0.200000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN            full
            tier0  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN            full
      tier0_tier1  conf_0.00              0.000000      12      0.60          0.40            0.166667            0.250000                0.133333            0.100000            full
      tier0_tier1  conf_0.05              0.050000      10      0.50          0.50            0.100000            0.200000                0.125000            0.080000            full
      tier0_tier1  conf_0.10              0.100000       6      0.30          0.70            0.000000            0.166667                0.000000            0.000000            full
      tier0_tier1  conf_0.15              0.150000       5      0.25          0.75            0.000000            0.200000                0.000000            0.000000            full
      tier0_tier1  conf_0.20              0.200000       4      0.20          0.80            0.000000            0.250000                0.000000            0.000000            full
      tier0_tier1  conf_0.25              0.250000       4      0.20          0.80            0.000000            0.250000                0.000000            0.000000            full
      tier0_tier1    trained              0.409819       4      0.20          0.80            0.000000            0.250000                0.000000            0.000000            full
tier0_tier1_tier2    trained             -0.173993      19      0.95          0.05            0.263158            0.368421                0.250000            0.260952            full
tier0_tier1_tier2  conf_0.00              0.000000       9      0.45          0.55            0.111111            0.222222                0.100000            0.133333            full
tier0_tier1_tier2  conf_0.05              0.050000       5      0.25          0.75            0.200000            0.200000                0.333333            0.200000            full
tier0_tier1_tier2  conf_0.10              0.100000       4      0.20          0.80            0.250000            0.250000                0.333333            0.200000            full
tier0_tier1_tier2  conf_0.15              0.150000       4      0.20          0.80            0.250000            0.250000                0.333333            0.200000            full
tier0_tier1_tier2  conf_0.20              0.200000       3      0.15          0.85            0.333333            0.333333                0.333333            0.200000            full
tier0_tier1_tier2  conf_0.25              0.250000       2      0.10          0.90            0.000000            0.000000                0.000000            0.000000            full
```

## Diagnosis Mode Comparison
- Whole-run and post-alert-window diagnosis are exported together so the diagnosis mode can be evaluated directly.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile diagnosis_target    diagnosis_mode  family_acc  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau                       status  min_class_count  min_group_count    group_key  include_workload
            tier0       20      0.40      0.50      0.400000  0.338889               0.022843                 0.017983            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.30      0.35      0.300000  0.225758               0.019554                 0.017492            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.30      0.40      0.300000  0.200000               0.022092                 0.022639            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.15      0.50      0.150000  0.154286               0.016017                 0.014935            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.15      0.25      0.150000  0.137143               0.103156                 0.033042            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.10      0.30      0.100000  0.094444               0.014428                 0.008170            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.25      0.50      0.250000  0.197980               0.013267                 0.011441            full     hierarchical         whole_run         0.4      0.35          0.65            0.428571            0.571429                0.333333            0.260000            0.008541              0.007048           0.009274        0.159320                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.25      0.45      0.250000  0.240476              -0.005373                 0.006283            full     hierarchical         whole_run         0.5      0.50          0.50            0.200000            0.300000                0.266667            0.257143            0.016326              0.015484           0.006973        0.018156                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.20      0.35      0.200000  0.153333               0.008884                 0.016352            full     hierarchical         whole_run         0.4      0.50          0.50            0.200000            0.200000                0.300000            0.166667            0.020263              0.018695           0.007763        0.111953                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.15      0.40      0.150000  0.144444              -0.000754                 0.012707            full     hierarchical post_alert_window         0.4      0.80          0.20            0.125000            0.312500                0.116667            0.111111            0.008541              0.007048           0.009274       -0.076248                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.20      0.30      0.200000  0.161538              -0.005575                 0.011986            full     hierarchical post_alert_window         0.5      0.30          0.70            0.000000            0.166667                0.000000            0.000000            0.016326              0.015484           0.006973        0.409819                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.25      0.35      0.250000  0.246667              -0.007514                -0.015371            full     hierarchical post_alert_window         0.4      0.65          0.35            0.153846            0.307692                0.133333            0.150000            0.020263              0.018695           0.007763       -0.173993                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.50      0.75      0.444444  0.378788               0.028843                 0.031042            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.50      0.75      0.388889  0.342995               0.029843                 0.033171            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.45      0.95      0.583333  0.458333               0.016207                 0.016074            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.609017         0.266923     0.124060              tier0            full
  BRANCH     0.642810         0.212205     0.144986              tier0            full
   CACHE     0.525623         0.202468     0.271909              tier0            full
   MEMBW     0.648215         0.243140     0.108644              tier0            full
     TLB     0.590746         0.272349     0.136905              tier0            full
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC                 compute       0.340220         0.315902             0.106565                 0.134974                 0.102340            full
  BRANCH               memory_io       0.305857         0.371736             0.077963                 0.169414                 0.075030            full
   CACHE                 compute       0.454633         0.305069             0.069918                 0.104124                 0.066256            full
   MEMBW               memory_io       0.313707         0.356528             0.102498                 0.132145                 0.095122            full
     TLB                 compute       0.335234         0.331872             0.111858                 0.137402                 0.083634            full
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
            tier0                   0.25                        0.927835                      2.783505                 0.30                     51.5                 608.0                0.20                0.20                0.25            full
      tier0_tier1                   0.25                        0.927835                      2.783505                 0.65                     36.0                 791.2                0.45                0.45                0.50            full
tier0_tier1_tier2                   0.25                        0.927835                      2.783505                 0.95                     32.0                 773.8                0.65                0.65                0.75            full
```

## Files
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/config_runtime_summary.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/run_context.json`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/case_inventory.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B30_a0.05_k3/figures/fig_detection_latency.png`
