# DICE Full Retrain Results

## Setup
- Feature profile: full ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_full_5hz.csv', 'tier2': 'tier2_full_5hz.csv'})
- Protocol: global, benign-only fit/calibration, block_B=45, alpha=0.05, persist_k=3, gain=0.25
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
           full             tier0       24          46          2.223940   0.8125 0.940232         1.0        1.0            0.0           0.30              0.007649              0.015906                      0.0                 0.008537
           full       tier0_tier1       24          64          2.991236   0.8250 0.958228         1.0        1.0            0.0           0.60              0.010644              0.032930                      0.0                 0.015745
           full tier0_tier1_tier2       24          75          3.532754   0.9750 0.995119         1.0        1.0            0.0           0.95              0.002841              0.007966                      0.0                 0.004409
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc  pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
           full   ATOMIC   0.9375    0.95         1.0        1.0          0.002841          0.007311                  0.0             0.003882       2.572648      0.004470       3882.767568         0.003882
           full   BRANCH   1.0000    1.00         1.0        1.0          0.002841          0.009034                  0.0             0.006425       3.178928      0.006193       6426.101206         0.006425
           full    CACHE   0.9375    0.95         1.0        1.0          0.002841          0.009627                  0.0             0.006350       3.387579      0.006786       6351.306472         0.006350
           full    MEMBW   1.0000    1.00         1.0        1.0          0.002841          0.008770                  0.0             0.005138       3.086205      0.005929       5139.004872         0.005138
           full      TLB   1.0000    1.00         1.0        1.0          0.002841          0.006887                  0.0             0.004624       2.423720      0.004046       4625.079970         0.004624
```

## Paper-style Aggregates (Final Config)
- Base score mean stressor AUC-PR (all five): **0.9800**
- Base score mean stressor ROC-AUC (all five): **0.9750**
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
            tier0       20       0.3      0.55           0.3  0.238961               0.026338                 0.020373            full
      tier0_tier1       20       0.2      0.35           0.2  0.190476               0.013185                 0.007183            full
tier0_tier1_tier2       20       0.3      0.45           0.3  0.206667               0.020929                 0.019106            full
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.15      0.55          0.15  0.113333               0.016387                 0.009409            full
      tier0_tier1       20      0.15      0.35          0.15  0.146032               0.068230                 0.043761            full
tier0_tier1_tier2       20      0.10      0.25          0.10  0.080808               0.016567                 0.011389            full
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.25      0.70          0.25  0.223333               0.013553                 0.008810            full
      tier0_tier1       20      0.20      0.55          0.20  0.152727               0.020369                 0.015854            full
tier0_tier1_tier2       20      0.35      0.60          0.35  0.281616               0.016061                 0.013344            full
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.55      0.80      0.472222  0.398551               0.033323                 0.034916            full
      tier0_tier1       20      0.45      0.75      0.361111  0.307359               0.021324                 0.024366            full
tier0_tier1_tier2       20      0.50      0.90      0.555556  0.495951               0.015926                 0.015216            full
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.40      0.65        0.45          0.40  0.318182      0.35          0.65            0.571429            0.857143                0.416667            0.274286              -0.010578                -0.008828            0.014524              0.015935           0.013378        0.106067            full
      tier0_tier1       20      0.20      0.40        0.45          0.20  0.215873      0.55          0.45            0.090909            0.272727                0.100000            0.080000               0.007983                 0.004445            0.021650              0.021609           0.009734       -0.006198            full
tier0_tier1_tier2       20      0.25      0.45        0.45          0.25  0.180000      0.65          0.35            0.230769            0.384615                0.333333            0.180000               0.014319                 0.017475            0.020169              0.016290           0.010002        0.058968            full
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.35      0.60        0.45          0.35  0.296537      0.45          0.55            0.222222            0.444444                0.133333            0.146667              -0.018654                -0.002906            0.014524              0.015935           0.013378       -0.081446            full
      tier0_tier1       20      0.15      0.40        0.45          0.15  0.123810      0.35          0.65            0.000000            0.428571                0.000000            0.000000              -0.000049                 0.025975            0.021650              0.021609           0.009734        0.136310            full
tier0_tier1_tier2       20      0.25      0.35        0.45          0.25  0.200000      0.75          0.25            0.133333            0.266667                0.133333            0.072727              -0.003001                 0.006715            0.020169              0.016290           0.010002       -0.150577            full
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0  conf_0.00              0.000000      10      0.50          0.50            0.400000            0.700000                0.333333            0.247619            full
            tier0  conf_0.05              0.050000       8      0.40          0.60            0.500000            0.750000                0.416667            0.247619            full
            tier0  conf_0.10              0.100000       6      0.30          0.70            0.500000            0.666667                0.375000            0.233333            full
            tier0    trained              0.106067       6      0.30          0.70            0.500000            0.666667                0.375000            0.233333            full
            tier0  conf_0.15              0.150000       4      0.20          0.80            0.500000            0.750000                0.333333            0.133333            full
            tier0  conf_0.20              0.200000       3      0.15          0.85            0.666667            1.000000                0.500000            0.160000            full
            tier0  conf_0.25              0.250000       2      0.10          0.90            1.000000            1.000000                1.000000            0.200000            full
      tier0_tier1    trained             -0.006198      14      0.70          0.30            0.142857            0.285714                0.166667            0.146667            full
      tier0_tier1  conf_0.00              0.000000      14      0.70          0.30            0.142857            0.285714                0.166667            0.146667            full
      tier0_tier1  conf_0.05              0.050000       9      0.45          0.55            0.111111            0.222222                0.100000            0.080000            full
      tier0_tier1  conf_0.10              0.100000       8      0.40          0.60            0.000000            0.125000                0.000000            0.000000            full
      tier0_tier1  conf_0.15              0.150000       4      0.20          0.80            0.000000            0.250000                0.000000            0.000000            full
      tier0_tier1  conf_0.20              0.200000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000            full
      tier0_tier1  conf_0.25              0.250000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.00              0.000000      17      0.85          0.15            0.235294            0.411765                0.250000            0.172308            full
tier0_tier1_tier2  conf_0.05              0.050000      14      0.70          0.30            0.285714            0.500000                0.250000            0.192308            full
tier0_tier1_tier2    trained              0.058968      14      0.70          0.30            0.285714            0.500000                0.250000            0.192308            full
tier0_tier1_tier2  conf_0.10              0.100000      11      0.55          0.45            0.272727            0.545455                0.300000            0.180000            full
tier0_tier1_tier2  conf_0.15              0.150000       4      0.20          0.80            0.000000            0.250000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.20              0.200000       3      0.15          0.85            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.25              0.250000       2      0.10          0.90            0.000000            0.000000                0.000000            0.000000            full
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained             -0.081446      12      0.60          0.40            0.333333            0.583333                0.333333            0.293333            full
            tier0  conf_0.00              0.000000      11      0.55          0.45            0.272727            0.545455                0.233333            0.226667            full
            tier0  conf_0.05              0.050000       5      0.25          0.75            0.200000            0.400000                0.166667            0.100000            full
            tier0  conf_0.10              0.100000       4      0.20          0.80            0.250000            0.250000                0.333333            0.133333            full
            tier0  conf_0.15              0.150000       4      0.20          0.80            0.250000            0.250000                0.333333            0.133333            full
            tier0  conf_0.20              0.200000       3      0.15          0.85            0.333333            0.333333                0.500000            0.200000            full
            tier0  conf_0.25              0.250000       2      0.10          0.90            0.000000            0.000000                0.000000            0.000000            full
      tier0_tier1  conf_0.00              0.000000      13      0.65          0.35            0.153846            0.461538                0.100000            0.100000            full
      tier0_tier1  conf_0.05              0.050000      12      0.60          0.40            0.166667            0.500000                0.100000            0.100000            full
      tier0_tier1  conf_0.10              0.100000      11      0.55          0.45            0.181818            0.545455                0.133333            0.114286            full
      tier0_tier1    trained              0.136310       9      0.45          0.55            0.000000            0.444444                0.000000            0.000000            full
      tier0_tier1  conf_0.15              0.150000       9      0.45          0.55            0.000000            0.444444                0.000000            0.000000            full
      tier0_tier1  conf_0.20              0.200000       7      0.35          0.65            0.000000            0.428571                0.000000            0.000000            full
      tier0_tier1  conf_0.25              0.250000       5      0.25          0.75            0.000000            0.400000                0.000000            0.000000            full
tier0_tier1_tier2    trained             -0.150577      18      0.90          0.10            0.222222            0.333333                0.233333            0.200000            full
tier0_tier1_tier2  conf_0.00              0.000000      12      0.60          0.40            0.083333            0.166667                0.100000            0.057143            full
tier0_tier1_tier2  conf_0.05              0.050000       7      0.35          0.65            0.142857            0.142857                0.166667            0.100000            full
tier0_tier1_tier2  conf_0.10              0.100000       3      0.15          0.85            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.15              0.150000       2      0.10          0.90            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.20              0.200000       2      0.10          0.90            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.25              0.250000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000            full
```

## Diagnosis Mode Comparison
- Whole-run and post-alert-window diagnosis are exported together so the diagnosis mode can be evaluated directly.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile diagnosis_target    diagnosis_mode  family_acc  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau                       status  min_class_count  min_group_count    group_key  include_workload
            tier0       20      0.30      0.55      0.300000  0.238961               0.026338                 0.020373            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.20      0.35      0.200000  0.190476               0.013185                 0.007183            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.30      0.45      0.300000  0.206667               0.020929                 0.019106            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.15      0.55      0.150000  0.113333               0.016387                 0.009409            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.15      0.35      0.150000  0.146032               0.068230                 0.043761            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.10      0.25      0.100000  0.080808               0.016567                 0.011389            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.40      0.65      0.400000  0.318182              -0.010578                -0.008828            full     hierarchical         whole_run        0.45      0.35          0.65            0.571429            0.857143                0.416667            0.274286            0.014524              0.015935           0.013378        0.106067                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.20      0.40      0.200000  0.215873               0.007983                 0.004445            full     hierarchical         whole_run        0.45      0.55          0.45            0.090909            0.272727                0.100000            0.080000            0.021650              0.021609           0.009734       -0.006198                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.25      0.45      0.250000  0.180000               0.014319                 0.017475            full     hierarchical         whole_run        0.45      0.65          0.35            0.230769            0.384615                0.333333            0.180000            0.020169              0.016290           0.010002        0.058968                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.35      0.60      0.350000  0.296537              -0.018654                -0.002906            full     hierarchical post_alert_window        0.45      0.45          0.55            0.222222            0.444444                0.133333            0.146667            0.014524              0.015935           0.013378       -0.081446                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.15      0.40      0.150000  0.123810              -0.000049                 0.025975            full     hierarchical post_alert_window        0.45      0.35          0.65            0.000000            0.428571                0.000000            0.000000            0.021650              0.021609           0.009734        0.136310                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.25      0.35      0.250000  0.200000              -0.003001                 0.006715            full     hierarchical post_alert_window        0.45      0.75          0.25            0.133333            0.266667                0.133333            0.072727            0.020169              0.016290           0.010002       -0.150577                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.55      0.80      0.472222  0.398551               0.033323                 0.034916            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.45      0.75      0.361111  0.307359               0.021324                 0.024366            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.50      0.90      0.555556  0.495951               0.015926                 0.015216            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.597825         0.265746     0.136429              tier0            full
  BRANCH     0.625310         0.219118     0.155572              tier0            full
   CACHE     0.491516         0.205143     0.303341              tier0            full
   MEMBW     0.641269         0.236762     0.121969              tier0            full
     TLB     0.569856         0.278239     0.151905              tier0            full
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC                 compute       0.347134         0.305361             0.109173                 0.126747                 0.111585            full
  BRANCH               memory_io       0.311467         0.368235             0.079531                 0.159845                 0.080922            full
   CACHE                 compute       0.479921         0.289297             0.068956                 0.091932                 0.069895            full
   MEMBW                 compute       0.321808         0.346555             0.098687                 0.124945                 0.108005            full
     TLB                 compute       0.347034         0.320765             0.110756                 0.128734                 0.092710            full
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
            tier0                    0.0                             0.0                           0.0                 0.30                     64.0                 619.0                0.20                0.20                0.25            full
      tier0_tier1                    0.0                             0.0                           0.0                 0.60                     67.0                 782.3                0.45                0.45                0.50            full
tier0_tier1_tier2                    0.0                             0.0                           0.0                 0.95                     47.0                 785.4                0.65                0.65                0.80            full
```

## Files
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B45_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B45_a0.05_k3/config_runtime_summary.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B45_a0.05_k3/run_context.json`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B45_a0.05_k3/case_inventory.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B45_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B45_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B45_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B45_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B45_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B45_a0.05_k3/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B45_a0.05_k3/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B45_a0.05_k3/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B45_a0.05_k3/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B45_a0.05_k3/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B45_a0.05_k3/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B45_a0.05_k3/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B45_a0.05_k3/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B45_a0.05_k3/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B45_a0.05_k3/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B45_a0.05_k3/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B45_a0.05_k3/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B45_a0.05_k3/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B45_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B45_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B45_a0.05_k3/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B45_a0.05_k3/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B45_a0.05_k3/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B45_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B45_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B45_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B45_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B45_a0.05_k3/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B45_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B45_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B45_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B45_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B45_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B45_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B45_a0.05_k3/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B45_a0.05_k3/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B45_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B45_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B45_a0.05_k3/figures/fig_detection_latency.png`
