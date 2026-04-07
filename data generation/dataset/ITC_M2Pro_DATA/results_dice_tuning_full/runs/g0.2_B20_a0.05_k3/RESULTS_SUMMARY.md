# DICE Full Retrain Results

## Setup
- Feature profile: full ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_full_5hz.csv', 'tier2': 'tier2_full_5hz.csv'})
- Protocol: global, benign-only fit/calibration, block_B=20, alpha=0.05, persist_k=3, gain=0.2
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
           full             tier0       24          46          2.406522   0.7625 0.917472         1.0        1.0           0.25           0.35              0.010371              0.020111                      0.0                 0.011191
           full       tier0_tier1       24          64          3.050938   0.8250 0.955040         1.0        1.0           0.25           0.65              0.017170              0.043720                      0.0                 0.019103
           full tier0_tier1_tier2       24          75          3.655491   0.9625 0.992487         1.0        1.0           0.25           0.95              0.002971              0.007571                      0.0                 0.004179
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc  pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
           full   ATOMIC   0.9375    0.95         1.0        1.0          0.002971          0.006826                  0.0             0.003678       2.296978      0.003855       3679.220323         0.003678
           full   BRANCH   1.0000    1.00         1.0        1.0          0.002971          0.010770                  0.0             0.007689       3.623831      0.007799       7690.012124         0.007689
           full    CACHE   0.9375    0.95         1.0        1.0          0.002971          0.008839                  0.0             0.005682       2.974028      0.005868       5683.334113         0.005682
           full    MEMBW   1.0000    1.00         1.0        1.0          0.002971          0.008282                  0.0             0.004428       2.786634      0.005311       4428.926917         0.004428
           full      TLB   0.9375    0.95         1.0        1.0          0.002971          0.007429                  0.0             0.004819       2.499663      0.004458       4820.124501         0.004819
```

## Paper-style Aggregates (Final Config)
- Base score mean stressor AUC-PR (all five): **0.9700**
- Base score mean stressor ROC-AUC (all five): **0.9625**
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
            tier0       20      0.30      0.55          0.30  0.242424               0.027180                 0.022863            full
      tier0_tier1       20      0.15      0.40          0.15  0.133333               0.012979                 0.008910            full
tier0_tier1_tier2       20      0.30      0.45          0.30  0.220952               0.018462                 0.017234            full
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.25       0.5          0.25  0.233333               0.015828                 0.014921            full
      tier0_tier1       20      0.10       0.3          0.10  0.100000               0.106270                 0.052432            full
tier0_tier1_tier2       20      0.10       0.2          0.10  0.080808               0.024238                 0.017886            full
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.25      0.60          0.25  0.217778               0.013545                 0.010480            full
      tier0_tier1       20      0.20      0.55          0.20  0.152727               0.019194                 0.015946            full
tier0_tier1_tier2       20      0.40      0.60          0.40  0.357013               0.017916                 0.014095            full
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.55      0.85      0.472222  0.398551               0.034527                 0.038891            full
      tier0_tier1       20      0.40      0.80      0.333333  0.279365               0.019629                 0.018751            full
tier0_tier1_tier2       20      0.50      0.90      0.611111  0.540196               0.014559                 0.014238            full
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.40      0.55        0.45          0.40  0.368889      0.35          0.65            0.428571            0.428571                0.333333            0.213333               0.005885                 0.013386            0.013892              0.016292           0.014967        0.117755            full
      tier0_tier1       20      0.15      0.45        0.45          0.15  0.166667      0.65          0.35            0.076923            0.384615                0.100000            0.080000               0.011850                 0.013723            0.020789              0.017629           0.013578        0.022643            full
tier0_tier1_tier2       20      0.25      0.45        0.35          0.25  0.180000      0.50          0.50            0.300000            0.500000                0.333333            0.188889               0.013040                 0.016436            0.021024              0.017478           0.009744        0.053086            full
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.40      0.55        0.45          0.40  0.396032      0.65          0.35            0.384615            0.538462                0.300000            0.271429              -0.013257                 0.004914            0.013892              0.016292           0.014967       -0.019756            full
      tier0_tier1       20      0.15      0.30        0.45          0.15  0.128889      0.30          0.70            0.166667            0.333333                0.200000            0.133333               0.022910                 0.045399            0.020789              0.017629           0.013578        0.399851            full
tier0_tier1_tier2       20      0.20      0.30        0.35          0.20  0.166667      0.60          0.40            0.083333            0.250000                0.066667            0.044444              -0.005289                -0.002760            0.021024              0.017478           0.009744       -0.130506            full
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0  conf_0.00              0.000000      15      0.75          0.25            0.400000            0.533333                0.350000            0.333333            full
            tier0  conf_0.05              0.050000      12      0.60          0.40            0.416667            0.583333                0.366667            0.355556            full
            tier0  conf_0.10              0.100000       9      0.45          0.55            0.444444            0.555556                0.333333            0.233333            full
            tier0    trained              0.117755       8      0.40          0.60            0.500000            0.500000                0.333333            0.247619            full
            tier0  conf_0.15              0.150000       5      0.25          0.75            0.400000            0.400000                0.222222            0.133333            full
            tier0  conf_0.20              0.200000       4      0.20          0.80            0.500000            0.500000                0.333333            0.133333            full
            tier0  conf_0.25              0.250000       3      0.15          0.85            0.666667            0.666667                0.666667            0.160000            full
      tier0_tier1  conf_0.00              0.000000      17      0.85          0.15            0.117647            0.411765                0.133333            0.114286            full
      tier0_tier1    trained              0.022643      14      0.70          0.30            0.142857            0.357143                0.133333            0.114286            full
      tier0_tier1  conf_0.05              0.050000      12      0.60          0.40            0.166667            0.333333                0.133333            0.114286            full
      tier0_tier1  conf_0.10              0.100000       5      0.25          0.75            0.000000            0.400000                0.000000            0.000000            full
      tier0_tier1  conf_0.15              0.150000       2      0.10          0.90            0.000000            0.500000                0.000000            0.000000            full
      tier0_tier1  conf_0.20              0.200000       1      0.05          0.95            0.000000            1.000000                0.000000            0.000000            full
      tier0_tier1  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN            full
tier0_tier1_tier2  conf_0.00              0.000000      17      0.85          0.15            0.235294            0.411765                0.250000            0.172308            full
tier0_tier1_tier2  conf_0.05              0.050000      12      0.60          0.40            0.250000            0.500000                0.233333            0.172727            full
tier0_tier1_tier2    trained              0.053086      12      0.60          0.40            0.250000            0.500000                0.233333            0.172727            full
tier0_tier1_tier2  conf_0.10              0.100000       9      0.45          0.55            0.333333            0.666667                0.400000            0.288889            full
tier0_tier1_tier2  conf_0.15              0.150000       4      0.20          0.80            0.000000            0.250000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.20              0.200000       3      0.15          0.85            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.25              0.250000       2      0.10          0.90            0.000000            0.000000                0.000000            0.000000            full
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained             -0.019756      14      0.70          0.30            0.357143            0.500000                0.300000            0.260317            full
            tier0  conf_0.00              0.000000      14      0.70          0.30            0.357143            0.500000                0.300000            0.260317            full
            tier0  conf_0.05              0.050000       9      0.45          0.55            0.444444            0.666667                0.458333            0.314286            full
            tier0  conf_0.10              0.100000       5      0.25          0.75            0.600000            0.600000                0.666667            0.433333            full
            tier0  conf_0.15              0.150000       2      0.10          0.90            0.500000            0.500000                0.500000            0.200000            full
            tier0  conf_0.20              0.200000       2      0.10          0.90            0.500000            0.500000                0.500000            0.200000            full
            tier0  conf_0.25              0.250000       1      0.05          0.95            1.000000            1.000000                1.000000            0.200000            full
      tier0_tier1  conf_0.00              0.000000      16      0.80          0.20            0.125000            0.312500                0.116667            0.116667            full
      tier0_tier1  conf_0.05              0.050000      13      0.65          0.35            0.153846            0.384615                0.166667            0.166667            full
      tier0_tier1  conf_0.10              0.100000      10      0.50          0.50            0.000000            0.200000                0.000000            0.000000            full
      tier0_tier1  conf_0.15              0.150000      10      0.50          0.50            0.000000            0.200000                0.000000            0.000000            full
      tier0_tier1  conf_0.20              0.200000       9      0.45          0.55            0.000000            0.222222                0.000000            0.000000            full
      tier0_tier1  conf_0.25              0.250000       8      0.40          0.60            0.000000            0.250000                0.000000            0.000000            full
      tier0_tier1    trained              0.399851       7      0.35          0.65            0.000000            0.142857                0.000000            0.000000            full
tier0_tier1_tier2    trained             -0.130506      16      0.80          0.20            0.125000            0.250000                0.133333            0.140000            full
tier0_tier1_tier2  conf_0.00              0.000000      10      0.50          0.50            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.05              0.050000       7      0.35          0.65            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.10              0.100000       7      0.35          0.65            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.15              0.150000       4      0.20          0.80            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.20              0.200000       3      0.15          0.85            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.25              0.250000       2      0.10          0.90            0.000000            0.000000                0.000000            0.000000            full
```

## Diagnosis Mode Comparison
- Whole-run and post-alert-window diagnosis are exported together so the diagnosis mode can be evaluated directly.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile diagnosis_target    diagnosis_mode  family_acc  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau                       status  min_class_count  min_group_count    group_key  include_workload
            tier0       20      0.30      0.55      0.300000  0.242424               0.027180                 0.022863            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.15      0.40      0.150000  0.133333               0.012979                 0.008910            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.30      0.45      0.300000  0.220952               0.018462                 0.017234            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.25      0.50      0.250000  0.233333               0.015828                 0.014921            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.10      0.30      0.100000  0.100000               0.106270                 0.052432            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.10      0.20      0.100000  0.080808               0.024238                 0.017886            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.40      0.55      0.400000  0.368889               0.005885                 0.013386            full     hierarchical         whole_run        0.45      0.35          0.65            0.428571            0.428571                0.333333            0.213333            0.013892              0.016292           0.014967        0.117755                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.15      0.45      0.150000  0.166667               0.011850                 0.013723            full     hierarchical         whole_run        0.45      0.65          0.35            0.076923            0.384615                0.100000            0.080000            0.020789              0.017629           0.013578        0.022643                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.25      0.45      0.250000  0.180000               0.013040                 0.016436            full     hierarchical         whole_run        0.35      0.50          0.50            0.300000            0.500000                0.333333            0.188889            0.021024              0.017478           0.009744        0.053086                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.40      0.55      0.400000  0.396032              -0.013257                 0.004914            full     hierarchical post_alert_window        0.45      0.65          0.35            0.384615            0.538462                0.300000            0.271429            0.013892              0.016292           0.014967       -0.019756                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.15      0.30      0.150000  0.128889               0.022910                 0.045399            full     hierarchical post_alert_window        0.45      0.30          0.70            0.166667            0.333333                0.200000            0.133333            0.020789              0.017629           0.013578        0.399851                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.20      0.30      0.200000  0.166667              -0.005289                -0.002760            full     hierarchical post_alert_window        0.35      0.60          0.40            0.083333            0.250000                0.066667            0.044444            0.021024              0.017478           0.009744       -0.130506                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.55      0.85      0.472222  0.398551               0.034527                 0.038891            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.40      0.80      0.333333  0.279365               0.019629                 0.018751            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.50      0.90      0.611111  0.540196               0.014559                 0.014238            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.567898         0.268847     0.163255              tier0            full
  BRANCH     0.599391         0.219310     0.181300              tier0            full
   CACHE     0.463129         0.201385     0.335486              tier0            full
   MEMBW     0.612896         0.238678     0.148426              tier0            full
     TLB     0.539548         0.279143     0.181309              tier0            full
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC                 compute       0.367229         0.283429             0.121184                 0.127830                 0.100329            full
  BRANCH                 compute       0.326953         0.345764             0.087090                 0.169567                 0.070627            full
   CACHE                 compute       0.504127         0.264136             0.075887                 0.093661                 0.062189            full
   MEMBW                 compute       0.341038         0.323958             0.106586                 0.129886                 0.098532            full
     TLB                 compute       0.368582         0.294047             0.120909                 0.133637                 0.082826            full
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
            tier0                   0.25                        2.755102                      4.591837                 0.35                     72.0                 550.6                0.25                0.25                0.30            full
      tier0_tier1                   0.25                        2.755102                      4.591837                 0.65                     32.0                 752.0                0.50                0.50                0.55            full
tier0_tier1_tier2                   0.25                        2.755102                      4.591837                 0.95                     22.0                 515.2                0.75                0.75                0.85            full
```

## Files
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B20_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B20_a0.05_k3/config_runtime_summary.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B20_a0.05_k3/run_context.json`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B20_a0.05_k3/case_inventory.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B20_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B20_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B20_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B20_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B20_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B20_a0.05_k3/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B20_a0.05_k3/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B20_a0.05_k3/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B20_a0.05_k3/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B20_a0.05_k3/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B20_a0.05_k3/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B20_a0.05_k3/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B20_a0.05_k3/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B20_a0.05_k3/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B20_a0.05_k3/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B20_a0.05_k3/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B20_a0.05_k3/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B20_a0.05_k3/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B20_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B20_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B20_a0.05_k3/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B20_a0.05_k3/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B20_a0.05_k3/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B20_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B20_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B20_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B20_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B20_a0.05_k3/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B20_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B20_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B20_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B20_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B20_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B20_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B20_a0.05_k3/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B20_a0.05_k3/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B20_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B20_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.2_B20_a0.05_k3/figures/fig_detection_latency.png`
