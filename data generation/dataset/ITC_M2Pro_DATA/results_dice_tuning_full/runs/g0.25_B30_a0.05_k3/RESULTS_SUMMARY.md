# DICE Full Retrain Results

## Setup
- Feature profile: full ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_full_5hz.csv', 'tier2': 'tier2_full_5hz.csv'})
- Protocol: global, benign-only fit/calibration, block_B=30, alpha=0.05, persist_k=3, gain=0.25
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
           full             tier0       24          46          2.280388   0.8000 0.931899         1.0        1.0           0.25           0.30              0.008101              0.016247                      0.0                 0.009068
           full       tier0_tier1       24          64          3.069705   0.8250 0.955040         1.0        1.0           0.25           0.65              0.012413              0.034377                      0.0                 0.015871
           full tier0_tier1_tier2       24          75          3.593290   0.9625 0.992487         1.0        1.0           0.00           0.95              0.002872              0.008008                      0.0                 0.004391
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc  pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
           full   ATOMIC   0.9375    0.95         1.0        1.0          0.002872          0.007108                  0.0             0.003721       2.474283      0.004236       3722.039075         0.003721
           full   BRANCH   1.0000    1.00         1.0        1.0          0.002872          0.010083                  0.0             0.007026       3.509954      0.007211       7026.764865         0.007026
           full    CACHE   0.9375    0.95         1.0        1.0          0.002872          0.009173                  0.0             0.005852       3.192882      0.006300       5853.019141         0.005852
           full    MEMBW   1.0000    1.00         1.0        1.0          0.002872          0.008503                  0.0             0.004830       2.959783      0.005631       4830.795414         0.004830
           full      TLB   0.9375    0.95         1.0        1.0          0.002872          0.007578                  0.0             0.004866       2.637911      0.004706       4866.694400         0.004866
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
            tier0       20       0.3      0.65           0.3  0.238961               0.026699                 0.019982            full
      tier0_tier1       20       0.2      0.35           0.2  0.173333               0.012692                 0.008332            full
tier0_tier1_tier2       20       0.3      0.45           0.3  0.206667               0.020199                 0.019673            full
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.25       0.5          0.25  0.243175               0.016909                 0.011354            full
      tier0_tier1       20      0.10       0.3          0.10  0.094444               0.101524                 0.046995            full
tier0_tier1_tier2       20      0.10       0.2          0.10  0.080000               0.021595                 0.017832            full
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.25      0.65          0.25  0.214444               0.012582                 0.007010            full
      tier0_tier1       20      0.20      0.55          0.20  0.152727               0.020814                 0.015397            full
tier0_tier1_tier2       20      0.40      0.60          0.40  0.357013               0.016842                 0.014714            full
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.55      0.80      0.472222  0.398551               0.034380                 0.037193            full
      tier0_tier1       20      0.45      0.75      0.361111  0.305463               0.021774                 0.023913            full
tier0_tier1_tier2       20      0.50      0.90      0.555556  0.495951               0.015846                 0.015699            full
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.35      0.65        0.55          0.35  0.303377      0.45          0.55            0.444444            0.666667                0.333333            0.260000              -0.000316                 0.011054            0.013405              0.013555           0.010002        0.124961            full
      tier0_tier1       20      0.20      0.40        0.45          0.20  0.187013      0.75          0.25            0.200000            0.333333                0.166667            0.146667               0.006410                 0.004740            0.020924              0.021653           0.007982       -0.052489            full
tier0_tier1_tier2       20      0.25      0.45        0.40          0.25  0.180000      0.60          0.40            0.250000            0.416667                0.333333            0.180000               0.014110                 0.017375            0.020721              0.018314           0.009515        0.070886            full
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.35      0.55        0.55          0.35  0.343333      0.45          0.55            0.222222            0.444444                0.133333            0.088889              -0.025085                 0.004003            0.013405              0.013555           0.010002        0.020563            full
      tier0_tier1       20      0.10      0.30        0.45          0.10  0.080769      0.25          0.75            0.000000            0.400000                0.000000            0.000000              -0.026897                 0.008080            0.020924              0.021653           0.007982        0.398624            full
tier0_tier1_tier2       20      0.25      0.40        0.40          0.25  0.200000      0.65          0.35            0.153846            0.384615                0.133333            0.072727              -0.000603                 0.004923            0.020721              0.018314           0.009515       -0.121235            full
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0  conf_0.00              0.000000      13      0.65          0.35            0.384615            0.692308                0.283333            0.269091            full
            tier0  conf_0.05              0.050000      11      0.55          0.45            0.454545            0.727273                0.283333            0.269091            full
            tier0  conf_0.10              0.100000       8      0.40          0.60            0.500000            0.625000                0.416667            0.274286            full
            tier0    trained              0.124961       5      0.25          0.75            0.600000            0.600000                0.555556            0.260000            full
            tier0  conf_0.15              0.150000       3      0.15          0.85            0.666667            0.666667                0.666667            0.160000            full
            tier0  conf_0.20              0.200000       3      0.15          0.85            0.666667            0.666667                0.666667            0.160000            full
            tier0  conf_0.25              0.250000       3      0.15          0.85            0.666667            0.666667                0.666667            0.160000            full
      tier0_tier1    trained             -0.052489      16      0.80          0.20            0.187500            0.375000                0.166667            0.146667            full
      tier0_tier1  conf_0.00              0.000000      13      0.65          0.35            0.153846            0.307692                0.166667            0.146667            full
      tier0_tier1  conf_0.05              0.050000       9      0.45          0.55            0.111111            0.222222                0.100000            0.080000            full
      tier0_tier1  conf_0.10              0.100000       6      0.30          0.70            0.000000            0.166667                0.000000            0.000000            full
      tier0_tier1  conf_0.15              0.150000       4      0.20          0.80            0.000000            0.250000                0.000000            0.000000            full
      tier0_tier1  conf_0.20              0.200000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000            full
      tier0_tier1  conf_0.25              0.250000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.00              0.000000      17      0.85          0.15            0.235294            0.411765                0.250000            0.172308            full
tier0_tier1_tier2  conf_0.05              0.050000      14      0.70          0.30            0.285714            0.500000                0.250000            0.192308            full
tier0_tier1_tier2    trained              0.070886      14      0.70          0.30            0.285714            0.500000                0.250000            0.192308            full
tier0_tier1_tier2  conf_0.10              0.100000      11      0.55          0.45            0.272727            0.545455                0.300000            0.180000            full
tier0_tier1_tier2  conf_0.15              0.150000       4      0.20          0.80            0.000000            0.250000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.20              0.200000       3      0.15          0.85            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.25              0.250000       2      0.10          0.90            0.000000            0.000000                0.000000            0.000000            full
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0  conf_0.00              0.000000      12      0.60          0.40            0.333333            0.500000                0.300000            0.246667            full
            tier0    trained              0.020563      11      0.55          0.45            0.363636            0.545455                0.300000            0.280000            full
            tier0  conf_0.05              0.050000       6      0.30          0.70            0.166667            0.500000                0.125000            0.057143            full
            tier0  conf_0.10              0.100000       2      0.10          0.90            0.500000            1.000000                0.500000            0.133333            full
            tier0  conf_0.15              0.150000       1      0.05          0.95            1.000000            1.000000                1.000000            0.200000            full
            tier0  conf_0.20              0.200000       1      0.05          0.95            1.000000            1.000000                1.000000            0.200000            full
            tier0  conf_0.25              0.250000       1      0.05          0.95            1.000000            1.000000                1.000000            0.200000            full
      tier0_tier1  conf_0.00              0.000000      12      0.60          0.40            0.083333            0.333333                0.050000            0.050000            full
      tier0_tier1  conf_0.05              0.050000      10      0.50          0.50            0.100000            0.300000                0.066667            0.066667            full
      tier0_tier1  conf_0.10              0.100000       8      0.40          0.60            0.000000            0.250000                0.000000            0.000000            full
      tier0_tier1  conf_0.15              0.150000       8      0.40          0.60            0.000000            0.250000                0.000000            0.000000            full
      tier0_tier1  conf_0.20              0.200000       7      0.35          0.65            0.000000            0.285714                0.000000            0.000000            full
      tier0_tier1  conf_0.25              0.250000       6      0.30          0.70            0.000000            0.166667                0.000000            0.000000            full
      tier0_tier1    trained              0.398624       2      0.10          0.90            0.000000            0.500000                0.000000            0.000000            full
tier0_tier1_tier2    trained             -0.121235      17      0.85          0.15            0.176471            0.352941                0.200000            0.166667            full
tier0_tier1_tier2  conf_0.00              0.000000      12      0.60          0.40            0.083333            0.250000                0.100000            0.057143            full
tier0_tier1_tier2  conf_0.05              0.050000       8      0.40          0.60            0.000000            0.250000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.10              0.100000       5      0.25          0.75            0.000000            0.200000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.15              0.150000       5      0.25          0.75            0.000000            0.200000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.20              0.200000       3      0.15          0.85            0.000000            0.333333                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.25              0.250000       3      0.15          0.85            0.000000            0.333333                0.000000            0.000000            full
```

## Diagnosis Mode Comparison
- Whole-run and post-alert-window diagnosis are exported together so the diagnosis mode can be evaluated directly.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile diagnosis_target    diagnosis_mode  family_acc  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau                       status  min_class_count  min_group_count    group_key  include_workload
            tier0       20      0.30      0.65      0.300000  0.238961               0.026699                 0.019982            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.20      0.35      0.200000  0.173333               0.012692                 0.008332            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.30      0.45      0.300000  0.206667               0.020199                 0.019673            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.25      0.50      0.250000  0.243175               0.016909                 0.011354            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.10      0.30      0.100000  0.094444               0.101524                 0.046995            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.10      0.20      0.100000  0.080000               0.021595                 0.017832            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.35      0.65      0.350000  0.303377              -0.000316                 0.011054            full     hierarchical         whole_run        0.55      0.45          0.55            0.444444            0.666667                0.333333            0.260000            0.013405              0.013555           0.010002        0.124961                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.20      0.40      0.200000  0.187013               0.006410                 0.004740            full     hierarchical         whole_run        0.45      0.75          0.25            0.200000            0.333333                0.166667            0.146667            0.020924              0.021653           0.007982       -0.052489                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.25      0.45      0.250000  0.180000               0.014110                 0.017375            full     hierarchical         whole_run        0.40      0.60          0.40            0.250000            0.416667                0.333333            0.180000            0.020721              0.018314           0.009515        0.070886                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.35      0.55      0.350000  0.343333              -0.025085                 0.004003            full     hierarchical post_alert_window        0.55      0.45          0.55            0.222222            0.444444                0.133333            0.088889            0.013405              0.013555           0.010002        0.020563                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.10      0.30      0.100000  0.080769              -0.026897                 0.008080            full     hierarchical post_alert_window        0.45      0.25          0.75            0.000000            0.400000                0.000000            0.000000            0.020924              0.021653           0.007982        0.398624                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.25      0.40      0.250000  0.200000              -0.000603                 0.004923            full     hierarchical post_alert_window        0.40      0.65          0.35            0.153846            0.384615                0.133333            0.072727            0.020721              0.018314           0.009515       -0.121235                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.55      0.80      0.472222  0.398551               0.034380                 0.037193            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.45      0.75      0.361111  0.305463               0.021774                 0.023913            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.50      0.90      0.555556  0.495951               0.015846                 0.015699            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.588370         0.267477     0.144154              tier0            full
  BRANCH     0.617642         0.218517     0.163841              tier0            full
   CACHE     0.485081         0.203104     0.311815              tier0            full
   MEMBW     0.631012         0.239548     0.129440              tier0            full
     TLB     0.561514         0.278202     0.160283              tier0            full
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC                 compute       0.353850         0.297125             0.114923                 0.129101                 0.105001            full
  BRANCH               memory_io       0.316468         0.359116             0.083355                 0.165658                 0.075403            full
   CACHE                 compute       0.486649         0.280784             0.072375                 0.093968                 0.066223            full
   MEMBW                 compute       0.326903         0.339226             0.103912                 0.128121                 0.101838            full
     TLB                 compute       0.353090         0.311423             0.116101                 0.132381                 0.087006            full
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
            tier0                   0.25                        0.927835                      2.783505                 0.30                     53.0                 605.5                0.20                0.20                0.25            full
      tier0_tier1                   0.25                        0.927835                      2.783505                 0.65                     39.0                 754.4                0.45                0.45                0.55            full
tier0_tier1_tier2                   0.00                        0.000000                      0.000000                 0.95                     32.0                 588.2                0.70                0.70                0.85            full
```

## Files
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B30_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B30_a0.05_k3/config_runtime_summary.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B30_a0.05_k3/run_context.json`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B30_a0.05_k3/case_inventory.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B30_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B30_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B30_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B30_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B30_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B30_a0.05_k3/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B30_a0.05_k3/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B30_a0.05_k3/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B30_a0.05_k3/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B30_a0.05_k3/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B30_a0.05_k3/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B30_a0.05_k3/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B30_a0.05_k3/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B30_a0.05_k3/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B30_a0.05_k3/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B30_a0.05_k3/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B30_a0.05_k3/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B30_a0.05_k3/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B30_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B30_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B30_a0.05_k3/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B30_a0.05_k3/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B30_a0.05_k3/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B30_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B30_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B30_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B30_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B30_a0.05_k3/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B30_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B30_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B30_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B30_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B30_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B30_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B30_a0.05_k3/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B30_a0.05_k3/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B30_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B30_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.25_B30_a0.05_k3/figures/fig_detection_latency.png`
