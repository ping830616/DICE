# DICE Full Retrain Results

## Setup
- Feature profile: full ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_full_5hz.csv', 'tier2': 'tier2_full_5hz.csv'})
- Protocol: global, benign-only fit/calibration, block_B=20, alpha=0.05, persist_k=3, gain=0.15
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
           full             tier0       24          46          2.496155   0.7750 0.919734         1.0        1.0           0.25           0.35              0.012338              0.024416                      0.0                 0.013168
           full       tier0_tier1       24          64          3.256648   0.8625 0.968752         1.0        1.0           0.25           0.70              0.020336              0.052644                      0.0                 0.023571
           full tier0_tier1_tier2       24          75          3.847452   0.9875 0.997619         1.0        1.0           0.25           0.95              0.002937              0.007585                      0.0                 0.004239
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc  pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
           full   ATOMIC   0.9375    0.95         1.0        1.0          0.002937          0.006881                  0.0             0.004029       2.342346      0.003944       4030.431754         0.004029
           full   BRANCH   1.0000    1.00         1.0        1.0          0.002937          0.010424                  0.0             0.007527       3.548439      0.007487       7527.861075         0.007527
           full    CACHE   1.0000    1.00         1.0        1.0          0.002937          0.008866                  0.0             0.005743       3.018175      0.005929       5743.719088         0.005743
           full    MEMBW   1.0000    1.00         1.0        1.0          0.002937          0.008415                  0.0             0.004518       2.864603      0.005478       4519.099679         0.004518
           full      TLB   1.0000    1.00         1.0        1.0          0.002937          0.007144                  0.0             0.004720       2.431844      0.004207       4721.328934         0.004720
```

## Paper-style Aggregates (Final Config)
- Base score mean stressor AUC-PR (all five): **0.9900**
- Base score mean stressor ROC-AUC (all five): **0.9875**
- WC score mean stressor AUC-PR (all five): **1.0000**
- WC score mean stressor ROC-AUC (all five): **1.0000**
- Base score mean stressor AUC-PR (excluding BRANCH/TLB): **0.9833**
- Base score mean stressor ROC-AUC (excluding BRANCH/TLB): **0.9792**
- WC score mean stressor AUC-PR (excluding BRANCH/TLB): **1.0000**
- WC score mean stressor ROC-AUC (excluding BRANCH/TLB): **1.0000**

## Diagnosis
- Feature-level diagnosis uses normalized whole-run residual-attribution prototypes as the default paper-facing result, with diagnosis-only filtering that removes monotonic counters and downweights generic memory-state features.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.30      0.50          0.30  0.232900               0.027057                 0.021266            full
      tier0_tier1       20      0.25      0.45          0.25  0.270476               0.013630                 0.011233            full
tier0_tier1_tier2       20      0.30      0.60          0.30  0.230000               0.018242                 0.017122            full
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20       0.2      0.55           0.2  0.190476               0.018105                 0.015524            full
      tier0_tier1       20       0.1      0.25           0.1  0.094444               0.102342                 0.044767            full
tier0_tier1_tier2       20       0.1      0.20           0.1  0.080808               0.025131                 0.016750            full
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.25      0.50          0.25  0.234444               0.016625                 0.012293            full
      tier0_tier1       20      0.20      0.65          0.20  0.161616               0.018944                 0.016602            full
tier0_tier1_tier2       20      0.35      0.60          0.35  0.318730               0.017178                 0.016078            full
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20       0.6      0.85      0.500000  0.416667               0.033374                 0.036584            full
      tier0_tier1       20       0.4      0.85      0.388889  0.387302               0.016167                 0.013191            full
tier0_tier1_tier2       20       0.5      0.90      0.611111  0.540196               0.014938                 0.013397            full
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20       0.4      0.55        0.45           0.4  0.331313      0.55          0.45            0.454545            0.545455                0.400000            0.280000               0.002982                 0.011714            0.016072              0.018454           0.013413        0.097723            full
      tier0_tier1       20       0.3      0.55        0.50           0.3  0.344935      0.65          0.35            0.307692            0.615385                0.266667            0.360000               0.007938                 0.003862            0.020666              0.017128           0.008503        0.000000            full
tier0_tier1_tier2       20       0.2      0.55        0.40           0.2  0.153333      0.60          0.40            0.250000            0.666667                0.333333            0.213333               0.012937                 0.013881            0.020922              0.017304           0.009159        0.045326            full
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.40      0.65        0.45          0.40  0.396032      0.60          0.40            0.333333            0.583333                0.266667            0.237143              -0.013357                 0.006452            0.016072              0.018454           0.013413       -0.040325            full
      tier0_tier1       20      0.25      0.40        0.50          0.25  0.244444      0.25          0.75            0.200000            0.600000                0.250000            0.133333              -0.015961                 0.027299            0.020666              0.017128           0.008503        0.451170            full
tier0_tier1_tier2       20      0.15      0.30        0.40          0.15  0.122222      0.55          0.45            0.090909            0.363636                0.066667            0.044444              -0.008931                -0.001332            0.020922              0.017304           0.009159       -0.090320            full
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0  conf_0.00              0.000000      13      0.65          0.35            0.384615            0.461538                0.350000            0.269091            full
            tier0  conf_0.05              0.050000      11      0.55          0.45            0.454545            0.545455                0.400000            0.280000            full
            tier0    trained              0.097723       8      0.40          0.60            0.500000            0.500000                0.400000            0.274286            full
            tier0  conf_0.10              0.100000       8      0.40          0.60            0.500000            0.500000                0.400000            0.274286            full
            tier0  conf_0.15              0.150000       6      0.30          0.70            0.500000            0.500000                0.400000            0.260000            full
            tier0  conf_0.20              0.200000       4      0.20          0.80            0.500000            0.500000                0.333333            0.160000            full
            tier0  conf_0.25              0.250000       3      0.15          0.85            0.666667            0.666667                0.500000            0.200000            full
      tier0_tier1    trained              0.000000      15      0.75          0.25            0.266667            0.533333                0.250000            0.313333            full
      tier0_tier1  conf_0.00              0.000000      15      0.75          0.25            0.266667            0.533333                0.250000            0.313333            full
      tier0_tier1  conf_0.05              0.050000       9      0.45          0.55            0.222222            0.555556                0.133333            0.160000            full
      tier0_tier1  conf_0.10              0.100000       5      0.25          0.75            0.000000            0.400000                0.000000            0.000000            full
      tier0_tier1  conf_0.15              0.150000       2      0.10          0.90            0.000000            0.500000                0.000000            0.000000            full
      tier0_tier1  conf_0.20              0.200000       2      0.10          0.90            0.000000            0.500000                0.000000            0.000000            full
      tier0_tier1  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN            full
tier0_tier1_tier2  conf_0.00              0.000000      17      0.85          0.15            0.235294            0.588235                0.233333            0.194872            full
tier0_tier1_tier2    trained              0.045326      11      0.55          0.45            0.272727            0.727273                0.233333            0.206061            full
tier0_tier1_tier2  conf_0.05              0.050000      11      0.55          0.45            0.272727            0.727273                0.233333            0.206061            full
tier0_tier1_tier2  conf_0.10              0.100000       9      0.45          0.55            0.333333            0.888889                0.400000            0.288889            full
tier0_tier1_tier2  conf_0.15              0.150000       5      0.25          0.75            0.000000            0.800000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.20              0.200000       3      0.15          0.85            0.000000            0.666667                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.25              0.250000       2      0.10          0.90            0.000000            0.500000                0.000000            0.000000            full
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained             -0.040325      13      0.65          0.35            0.307692            0.615385                0.233333            0.223810            full
            tier0  conf_0.00              0.000000      13      0.65          0.35            0.307692            0.615385                0.233333            0.223810            full
            tier0  conf_0.05              0.050000       9      0.45          0.55            0.444444            0.555556                0.400000            0.313333            full
            tier0  conf_0.10              0.100000       5      0.25          0.75            0.400000            0.400000                0.222222            0.160000            full
            tier0  conf_0.15              0.150000       3      0.15          0.85            0.666667            0.666667                0.500000            0.200000            full
            tier0  conf_0.20              0.200000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN            full
            tier0  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN            full
      tier0_tier1  conf_0.00              0.000000      14      0.70          0.30            0.214286            0.428571                0.200000            0.226667            full
      tier0_tier1  conf_0.05              0.050000      13      0.65          0.35            0.230769            0.461538                0.216667            0.260000            full
      tier0_tier1  conf_0.10              0.100000       9      0.45          0.55            0.111111            0.444444                0.100000            0.100000            full
      tier0_tier1  conf_0.15              0.150000       6      0.30          0.70            0.000000            0.500000                0.000000            0.000000            full
      tier0_tier1  conf_0.20              0.200000       6      0.30          0.70            0.000000            0.500000                0.000000            0.000000            full
      tier0_tier1  conf_0.25              0.250000       6      0.30          0.70            0.000000            0.500000                0.000000            0.000000            full
      tier0_tier1    trained              0.451170       2      0.10          0.90            0.000000            1.000000                0.000000            0.000000            full
tier0_tier1_tier2    trained             -0.090320      15      0.75          0.25            0.133333            0.266667                0.116667            0.120000            full
tier0_tier1_tier2  conf_0.00              0.000000      11      0.55          0.45            0.090909            0.181818                0.100000            0.100000            full
tier0_tier1_tier2  conf_0.05              0.050000       7      0.35          0.65            0.000000            0.142857                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.10              0.100000       6      0.30          0.70            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.15              0.150000       4      0.20          0.80            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.20              0.200000       4      0.20          0.80            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.25              0.250000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000            full
```

## Diagnosis Mode Comparison
- Whole-run and post-alert-window diagnosis are exported together so the diagnosis mode can be evaluated directly.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile diagnosis_target    diagnosis_mode  family_acc  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau                       status  min_class_count  min_group_count    group_key  include_workload
            tier0       20      0.30      0.50      0.300000  0.232900               0.027057                 0.021266            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.25      0.45      0.250000  0.270476               0.013630                 0.011233            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.30      0.60      0.300000  0.230000               0.018242                 0.017122            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.20      0.55      0.200000  0.190476               0.018105                 0.015524            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.10      0.25      0.100000  0.094444               0.102342                 0.044767            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.10      0.20      0.100000  0.080808               0.025131                 0.016750            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.40      0.55      0.400000  0.331313               0.002982                 0.011714            full     hierarchical         whole_run        0.45      0.55          0.45            0.454545            0.545455                0.400000            0.280000            0.016072              0.018454           0.013413        0.097723                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.30      0.55      0.300000  0.344935               0.007938                 0.003862            full     hierarchical         whole_run        0.50      0.65          0.35            0.307692            0.615385                0.266667            0.360000            0.020666              0.017128           0.008503        0.000000                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.20      0.55      0.200000  0.153333               0.012937                 0.013881            full     hierarchical         whole_run        0.40      0.60          0.40            0.250000            0.666667                0.333333            0.213333            0.020922              0.017304           0.009159        0.045326                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.40      0.65      0.400000  0.396032              -0.013357                 0.006452            full     hierarchical post_alert_window        0.45      0.60          0.40            0.333333            0.583333                0.266667            0.237143            0.016072              0.018454           0.013413       -0.040325                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.25      0.40      0.250000  0.244444              -0.015961                 0.027299            full     hierarchical post_alert_window        0.50      0.25          0.75            0.200000            0.600000                0.250000            0.133333            0.020666              0.017128           0.008503        0.451170                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.15      0.30      0.150000  0.122222              -0.008931                -0.001332            full     hierarchical post_alert_window        0.40      0.55          0.45            0.090909            0.363636                0.066667            0.044444            0.020922              0.017304           0.009159       -0.090320                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.60      0.85      0.500000  0.416667               0.033374                 0.036584            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.40      0.85      0.388889  0.387302               0.016167                 0.013191            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.50      0.90      0.611111  0.540196               0.014938                 0.013397            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.551152         0.263986     0.184862              tier0            full
  BRANCH     0.585338         0.218487     0.196175              tier0            full
   CACHE     0.442934         0.196807     0.360259              tier0            full
   MEMBW     0.599031         0.232613     0.168356              tier0            full
     TLB     0.522101         0.275257     0.202642              tier0            full
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC                 compute       0.379265         0.274826             0.121026                 0.124750                 0.100134            full
  BRANCH                 compute       0.337813         0.336777             0.087466                 0.168104                 0.069840            full
   CACHE                 compute       0.520914         0.251138             0.075130                 0.091409                 0.061409            full
   MEMBW                 compute       0.355388         0.312017             0.103721                 0.128297                 0.100578            full
     TLB                 compute       0.384414         0.282046             0.119748                 0.130521                 0.083270            full
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
            tier0                   0.25                        2.755102                      4.591837                 0.35                     42.0                 378.4                0.30                0.30                0.30            full
      tier0_tier1                   0.25                        2.755102                      4.591837                 0.70                     29.0                 886.6                0.50                0.50                0.55            full
tier0_tier1_tier2                   0.25                        2.755102                      4.591837                 0.95                     22.0                 498.8                0.75                0.75                0.85            full
```

## Files
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B20_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B20_a0.05_k3/config_runtime_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B20_a0.05_k3/run_context.json`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B20_a0.05_k3/case_inventory.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B20_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B20_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B20_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B20_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B20_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B20_a0.05_k3/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B20_a0.05_k3/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B20_a0.05_k3/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B20_a0.05_k3/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B20_a0.05_k3/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B20_a0.05_k3/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B20_a0.05_k3/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B20_a0.05_k3/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B20_a0.05_k3/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B20_a0.05_k3/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B20_a0.05_k3/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B20_a0.05_k3/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B20_a0.05_k3/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B20_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B20_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B20_a0.05_k3/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B20_a0.05_k3/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B20_a0.05_k3/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B20_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B20_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B20_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B20_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B20_a0.05_k3/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B20_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B20_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B20_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B20_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B20_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B20_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B20_a0.05_k3/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B20_a0.05_k3/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B20_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B20_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.15_B20_a0.05_k3/figures/fig_detection_latency.png`
