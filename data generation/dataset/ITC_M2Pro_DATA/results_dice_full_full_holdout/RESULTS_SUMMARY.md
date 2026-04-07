# DICE Full Retrain Results

## Setup
- Feature profile: full ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_full_5hz.csv', 'tier2': 'tier2_full_5hz.csv'})
- Protocol: workload_holdout, benign-only fit/calibration, block_B=90, alpha=0.05, persist_k=2, gain=0.35
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
           full             tier0       24          46          2.153550   0.3500 0.767142         1.0        1.0            1.0            0.9              0.074984              0.048755                      0.0                 0.013778
           full       tier0_tier1       24          64          2.846208   0.2250 0.721826         1.0        1.0            1.0            0.9              0.176685              0.097315                      0.0                 0.037187
           full tier0_tier1_tier2       24          75          3.438281   0.2375 0.750397         1.0        1.0            1.0            1.0              0.084268              0.024285                      0.0                 0.046932
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
           full   ATOMIC   0.1250 0.394643         1.0        1.0          0.084268          0.013190                  0.0             0.071078       0.156537     -0.071078      71079.017417         0.071078
           full   BRANCH   0.1875 0.412500         1.0        1.0          0.084268          0.024285                  0.0             0.058922       0.288193     -0.059983      58922.952894         0.058922
           full    CACHE   0.5000 0.642857         1.0        1.0          0.084268          0.075554                  0.0             0.008715       0.896587     -0.008715       8715.541460         0.008715
           full    MEMBW   0.1875 0.415476         1.0        1.0          0.084268          0.020124                  0.0             0.030339       0.238813     -0.064145      30339.725099         0.030339
           full      TLB   0.1875 0.412500         1.0        1.0          0.084268          0.023858                  0.0             0.046130       0.283123     -0.060411      46130.738557         0.046130
```

## Paper-style Aggregates (Final Config)
- Base score mean stressor AUC-PR (all five): **0.4556**
- Base score mean stressor ROC-AUC (all five): **0.2375**
- WC score mean stressor AUC-PR (all five): **1.0000**
- WC score mean stressor ROC-AUC (all five): **1.0000**
- Base score mean stressor AUC-PR (excluding BRANCH/TLB): **0.4843**
- Base score mean stressor ROC-AUC (excluding BRANCH/TLB): **0.2708**
- WC score mean stressor AUC-PR (excluding BRANCH/TLB): **1.0000**
- WC score mean stressor ROC-AUC (excluding BRANCH/TLB): **1.0000**

## Diagnosis
- Feature-level diagnosis uses normalized whole-run residual-attribution prototypes as the default paper-facing result, with diagnosis-only filtering that removes monotonic counters and downweights generic memory-state features.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.20      0.55          0.20  0.185348               0.009221                 0.006140            full
      tier0_tier1       20      0.20      0.30          0.20  0.154921               0.014432                 0.015462            full
tier0_tier1_tier2       20      0.25      0.50          0.25  0.202597               0.030131                 0.031224            full
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.25      0.45          0.25  0.189394               0.033343                 0.035388            full
      tier0_tier1       20      0.15      0.35          0.15  0.120808               0.022659                 0.014244            full
tier0_tier1_tier2       20      0.25      0.40          0.25  0.195338               0.023761                 0.021746            full
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.25      0.55          0.25  0.189286               0.008666                 0.009900            full
      tier0_tier1       20      0.10      0.30          0.10  0.080000               0.017867                 0.016273            full
tier0_tier1_tier2       20      0.20      0.40          0.20  0.145455               0.029892                 0.019436            full
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.40      0.85      0.333333  0.337662               0.031455                 0.026011            full
      tier0_tier1       20      0.15      0.70      0.250000  0.152505               0.020868                 0.020206            full
tier0_tier1_tier2       20      0.40      0.85      0.555556  0.404762               0.027281                 0.021765            full
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20       0.2      0.55        0.35           0.2  0.157143       0.9           0.1            0.166667            0.555556                0.150000            0.123810               0.004026                 0.005968            0.007960              0.007664           0.009685        0.000000            full
      tier0_tier1       20       0.2      0.30        0.30           0.2  0.154921       1.0           0.0            0.200000            0.300000                0.200000            0.154921               0.014432                 0.015462            0.019859              0.014145           0.011992        0.000000            full
tier0_tier1_tier2       20       0.2      0.45        0.50           0.2  0.145455       0.9           0.1            0.222222            0.444444                0.216667            0.160000               0.037304                 0.028903            0.030109              0.021614           0.015585       -0.031554            full
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.25      0.50        0.35          0.25  0.196032      0.80          0.20            0.250000            0.500000                0.266667            0.201587               0.012590                 0.023006            0.007960              0.007664           0.009685        0.000000            full
      tier0_tier1       20      0.15      0.35        0.30          0.15  0.120808      0.95          0.05            0.157895            0.368421                0.150000            0.125253               0.021081                 0.014244            0.019859              0.014145           0.011992        0.000000            full
tier0_tier1_tier2       20      0.20      0.35        0.50          0.20  0.136364      1.00          0.00            0.200000            0.350000                0.200000            0.136364               0.028820                 0.017872            0.030109              0.021614           0.015585       -0.125198            full
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained              0.000000      18      0.90          0.10            0.166667            0.555556                0.150000            0.123810            full
            tier0  conf_0.00              0.000000      18      0.90          0.10            0.166667            0.555556                0.150000            0.123810            full
            tier0  conf_0.05              0.050000       5      0.25          0.75            0.200000            0.600000                0.166667            0.080000            full
            tier0  conf_0.10              0.100000       2      0.10          0.90            0.000000            0.500000                0.000000            0.000000            full
            tier0  conf_0.15              0.150000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN            full
            tier0  conf_0.20              0.200000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN            full
            tier0  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN            full
      tier0_tier1    trained              0.000000      20      1.00          0.00            0.200000            0.300000                0.200000            0.154921            full
      tier0_tier1  conf_0.00              0.000000      20      1.00          0.00            0.200000            0.300000                0.200000            0.154921            full
      tier0_tier1  conf_0.05              0.050000      11      0.55          0.45            0.181818            0.272727                0.150000            0.100000            full
      tier0_tier1  conf_0.10              0.100000       5      0.25          0.75            0.200000            0.400000                0.125000            0.066667            full
      tier0_tier1  conf_0.15              0.150000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN            full
      tier0_tier1  conf_0.20              0.200000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN            full
      tier0_tier1  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN            full
tier0_tier1_tier2    trained             -0.031554      18      0.90          0.10            0.222222            0.444444                0.216667            0.160000            full
tier0_tier1_tier2  conf_0.00              0.000000      18      0.90          0.10            0.222222            0.444444                0.216667            0.160000            full
tier0_tier1_tier2  conf_0.05              0.050000      14      0.70          0.30            0.285714            0.500000                0.250000            0.177143            full
tier0_tier1_tier2  conf_0.10              0.100000      12      0.60          0.40            0.250000            0.500000                0.233333            0.157143            full
tier0_tier1_tier2  conf_0.15              0.150000       8      0.40          0.60            0.250000            0.500000                0.300000            0.146667            full
tier0_tier1_tier2  conf_0.20              0.200000       8      0.40          0.60            0.250000            0.500000                0.300000            0.146667            full
tier0_tier1_tier2  conf_0.25              0.250000       6      0.30          0.70            0.166667            0.500000                0.200000            0.066667            full
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained              0.000000      16      0.80          0.20            0.250000            0.500000                0.266667            0.201587            full
            tier0  conf_0.00              0.000000      16      0.80          0.20            0.250000            0.500000                0.266667            0.201587            full
            tier0  conf_0.05              0.050000      12      0.60          0.40            0.250000            0.500000                0.300000            0.150000            full
            tier0  conf_0.10              0.100000      10      0.50          0.50            0.300000            0.600000                0.300000            0.166667            full
            tier0  conf_0.15              0.150000       8      0.40          0.60            0.250000            0.625000                0.266667            0.146667            full
            tier0  conf_0.20              0.200000       3      0.15          0.85            0.000000            0.333333                0.000000            0.000000            full
            tier0  conf_0.25              0.250000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000            full
      tier0_tier1    trained              0.000000      19      0.95          0.05            0.157895            0.368421                0.150000            0.125253            full
      tier0_tier1  conf_0.00              0.000000      19      0.95          0.05            0.157895            0.368421                0.150000            0.125253            full
      tier0_tier1  conf_0.05              0.050000      13      0.65          0.35            0.153846            0.384615                0.166667            0.101587            full
      tier0_tier1  conf_0.10              0.100000       6      0.30          0.70            0.166667            0.333333                0.100000            0.057143            full
      tier0_tier1  conf_0.15              0.150000       3      0.15          0.85            0.000000            0.333333                0.000000            0.000000            full
      tier0_tier1  conf_0.20              0.200000       3      0.15          0.85            0.000000            0.333333                0.000000            0.000000            full
      tier0_tier1  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN            full
tier0_tier1_tier2    trained             -0.125198      19      0.95          0.05            0.210526            0.368421                0.216667            0.140000            full
tier0_tier1_tier2  conf_0.00              0.000000      19      0.95          0.05            0.210526            0.368421                0.216667            0.140000            full
tier0_tier1_tier2  conf_0.05              0.050000      11      0.55          0.45            0.272727            0.454545                0.333333            0.166667            full
tier0_tier1_tier2  conf_0.10              0.100000       9      0.45          0.55            0.222222            0.444444                0.300000            0.133333            full
tier0_tier1_tier2  conf_0.15              0.150000       8      0.40          0.60            0.125000            0.375000                0.200000            0.066667            full
tier0_tier1_tier2  conf_0.20              0.200000       5      0.25          0.75            0.200000            0.400000                0.200000            0.066667            full
tier0_tier1_tier2  conf_0.25              0.250000       5      0.25          0.75            0.200000            0.400000                0.200000            0.066667            full
```

## Diagnosis Mode Comparison
- Whole-run and post-alert-window diagnosis are exported together so the diagnosis mode can be evaluated directly.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile diagnosis_target    diagnosis_mode  family_acc  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau                       status  min_class_count  min_group_count    group_key  include_workload
            tier0       20      0.20      0.55      0.200000  0.185348               0.009221                 0.006140            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.20      0.30      0.200000  0.154921               0.014432                 0.015462            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.25      0.50      0.250000  0.202597               0.030131                 0.031224            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.25      0.45      0.250000  0.189394               0.033343                 0.035388            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.15      0.35      0.150000  0.120808               0.022659                 0.014244            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.25      0.40      0.250000  0.195338               0.023761                 0.021746            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.20      0.55      0.200000  0.157143               0.004026                 0.005968            full     hierarchical         whole_run        0.35      0.90          0.10            0.166667            0.555556                0.150000            0.123810            0.007960              0.007664           0.009685        0.000000                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.20      0.30      0.200000  0.154921               0.014432                 0.015462            full     hierarchical         whole_run        0.30      1.00          0.00            0.200000            0.300000                0.200000            0.154921            0.019859              0.014145           0.011992        0.000000                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.20      0.45      0.200000  0.145455               0.037304                 0.028903            full     hierarchical         whole_run        0.50      0.90          0.10            0.222222            0.444444                0.216667            0.160000            0.030109              0.021614           0.015585       -0.031554                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.25      0.50      0.250000  0.196032               0.012590                 0.023006            full     hierarchical post_alert_window        0.35      0.80          0.20            0.250000            0.500000                0.266667            0.201587            0.007960              0.007664           0.009685        0.000000                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.15      0.35      0.150000  0.120808               0.021081                 0.014244            full     hierarchical post_alert_window        0.30      0.95          0.05            0.157895            0.368421                0.150000            0.125253            0.019859              0.014145           0.011992        0.000000                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.20      0.35      0.200000  0.136364               0.028820                 0.017872            full     hierarchical post_alert_window        0.50      1.00          0.00            0.200000            0.350000                0.200000            0.136364            0.030109              0.021614           0.015585       -0.125198                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.40      0.85      0.333333  0.337662               0.031455                 0.026011            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.15      0.70      0.250000  0.152505               0.020868                 0.020206            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.40      0.85      0.555556  0.404762               0.027281                 0.021765            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.589177         0.213162     0.197661              tier0            full
  BRANCH     0.583436         0.275581     0.140983              tier0            full
   CACHE     0.392037         0.275920     0.332043              tier0            full
   MEMBW     0.522671         0.351516     0.125813              tier0            full
     TLB     0.555423         0.331928     0.112649              tier0            full
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC               memory_io       0.338141         0.420065             0.067063                 0.094343                 0.080387            full
  BRANCH               memory_io       0.289320         0.471355             0.076313                 0.096297                 0.066715            full
   CACHE               memory_io       0.258717         0.306579             0.113934                 0.299736                 0.021035            full
   MEMBW               memory_io       0.324336         0.411060             0.132422                 0.074135                 0.058047            full
     TLB               memory_io       0.283959         0.523347             0.099083                 0.064378                 0.029232            full
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
            tier0                    1.0                     2851.318681                   2855.274725                  0.9                     91.0                 101.8                0.80                0.90                0.90            full
      tier0_tier1                    1.0                     3596.043956                   3600.000000                  0.9                     91.0                  91.0                0.90                0.90                0.90            full
tier0_tier1_tier2                    1.0                     3596.043956                   3600.000000                  1.0                     91.0                  91.0                0.95                0.95                0.95            full
```

## Holdout Robustness (Workload Drift Proxy)
```text
           config  mean_pr_auc  worst_pr_auc  mean_roc_auc  mean_pr_auc_wc  worst_pr_auc_wc  mean_roc_auc_wc  pooled_pr_auc  pooled_roc_auc  pooled_pr_auc_wc  pooled_roc_auc_wc  mean_fpr  mean_tpr feature_profile
            tier0       0.7825          0.71          0.25             1.0              1.0              1.0       0.767142          0.3500               1.0                1.0  0.166667  0.750000            full
      tier0_tier1       0.7825          0.71          0.25             1.0              1.0              1.0       0.721826          0.2250               1.0                1.0  0.166667  0.750000            full
tier0_tier1_tier2       0.8075          0.71          0.30             1.0              1.0              1.0       0.750397          0.2375               1.0                1.0  0.166667  0.833333            full
```

## Files
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/overall_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/config_runtime_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/run_context.json`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/case_inventory.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/case_block_traces.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/sequential_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/mechanism_group_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/overall_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/sequential_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/figures/fig_detection_latency.png`
