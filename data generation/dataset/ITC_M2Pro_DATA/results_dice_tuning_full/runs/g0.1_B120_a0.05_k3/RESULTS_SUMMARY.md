# DICE Full Retrain Results

## Setup
- Feature profile: full ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_full_5hz.csv', 'tier2': 'tier2_full_5hz.csv'})
- Protocol: global, benign-only fit/calibration, block_B=120, alpha=0.05, persist_k=3, gain=0.1
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
           full             tier0       24          46          2.142606   0.7875 0.921899         1.0        1.0            0.0            0.3              0.011026              0.024926                      0.0                 0.014395
           full       tier0_tier1       24          64          2.764141   0.8250 0.951460         1.0        1.0            0.0            0.5              0.017224              0.046201                      0.0                 0.021628
           full tier0_tier1_tier2       24          75          3.332496   0.9500 0.989710         1.0        1.0            0.0            0.9              0.003167              0.007904                      0.0                 0.005205
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc  pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
           full   ATOMIC   0.9375  0.9500         1.0        1.0          0.003167          0.008440                  0.0             0.005205       2.664986      0.005274       5205.543055         0.005205
           full   BRANCH   1.0000  1.0000         1.0        1.0          0.003167          0.007461                  0.0             0.005386       2.355722      0.004294       5386.958429         0.005386
           full    CACHE   0.8750  0.8875         1.0        1.0          0.003167          0.010855                  0.0             0.007684       3.427226      0.007688       7684.735189         0.007684
           full    MEMBW   1.0000  1.0000         1.0        1.0          0.003167          0.009373                  0.0             0.005698       2.959374      0.006206       5699.121500         0.005698
           full      TLB   0.9375  0.9500         1.0        1.0          0.003167          0.006772                  0.0             0.004414       2.138184      0.003605       4414.927310         0.004414
```

## Paper-style Aggregates (Final Config)
- Base score mean stressor AUC-PR (all five): **0.9575**
- Base score mean stressor ROC-AUC (all five): **0.9500**
- WC score mean stressor AUC-PR (all five): **1.0000**
- WC score mean stressor ROC-AUC (all five): **1.0000**
- Base score mean stressor AUC-PR (excluding BRANCH/TLB): **0.9458**
- Base score mean stressor ROC-AUC (excluding BRANCH/TLB): **0.9375**
- WC score mean stressor AUC-PR (excluding BRANCH/TLB): **1.0000**
- WC score mean stressor ROC-AUC (excluding BRANCH/TLB): **1.0000**

## Diagnosis
- Feature-level diagnosis uses normalized whole-run residual-attribution prototypes as the default paper-facing result, with diagnosis-only filtering that removes monotonic counters and downweights generic memory-state features.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.35      0.60          0.35  0.321429               0.024604                 0.015035            full
      tier0_tier1       20      0.20      0.50          0.20  0.177143               0.016255                 0.014652            full
tier0_tier1_tier2       20      0.30      0.55          0.30  0.251429               0.017911                 0.016456            full
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.15      0.45          0.15  0.147475               0.024902                 0.020440            full
      tier0_tier1       20      0.15      0.40          0.15  0.147436               0.017445                 0.013672            full
tier0_tier1_tier2       20      0.15      0.35          0.15  0.128889               0.014450                 0.012611            full
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.25      0.50          0.25  0.208889               0.023231                 0.021749            full
      tier0_tier1       20      0.60      0.75          0.60  0.596508               0.018633                 0.013188            full
tier0_tier1_tier2       20      0.45      0.60          0.45  0.426551               0.012634                 0.012101            full
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.60      0.85      0.500000  0.421818               0.034753                 0.038507            full
      tier0_tier1       20      0.55      0.90      0.416667  0.438889               0.020031                 0.015005            full
tier0_tier1_tier2       20      0.50      0.95      0.555556  0.556391               0.016143                 0.015710            full
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.20       0.6        0.40          0.20  0.181538      0.50          0.50            0.200000            0.700000                0.133333            0.166667              -0.012055                -0.001969            0.017807              0.013199           0.009908       -0.014112            full
      tier0_tier1       20      0.25       0.6        0.45          0.25  0.277778      0.65          0.35            0.153846            0.461538                0.150000            0.183333               0.008147                 0.009203            0.025391              0.026494           0.016323        0.024451            full
tier0_tier1_tier2       20      0.20       0.4        0.35          0.20  0.157143      0.65          0.35            0.307692            0.538462                0.333333            0.280000               0.013524                 0.016456            0.018854              0.018840           0.008651        0.028811            full
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.15      0.45        0.40          0.15  0.123810      0.60          0.40            0.083333            0.416667                0.066667            0.080000              -0.010978                 0.007178            0.017807              0.013199           0.009908       -0.043635            full
      tier0_tier1       20      0.25      0.55        0.45          0.25  0.230808      0.65          0.35            0.076923            0.384615                0.066667            0.057143               0.001949                 0.005190            0.025391              0.026494           0.016323        0.000000            full
tier0_tier1_tier2       20      0.25      0.40        0.35          0.25  0.205983      0.65          0.35            0.230769            0.384615                0.216667            0.201587               0.006337                 0.001481            0.018854              0.018840           0.008651        0.009214            full
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained             -0.014112      11      0.55          0.45            0.181818            0.636364                0.166667            0.190476            full
            tier0  conf_0.00              0.000000      10      0.50          0.50            0.200000            0.600000                0.208333            0.190476            full
            tier0  conf_0.05              0.050000       8      0.40          0.60            0.250000            0.625000                0.208333            0.200000            full
            tier0  conf_0.10              0.100000       6      0.30          0.70            0.166667            0.500000                0.083333            0.066667            full
            tier0  conf_0.15              0.150000       3      0.15          0.85            0.333333            0.666667                0.250000            0.100000            full
            tier0  conf_0.20              0.200000       1      0.05          0.95            1.000000            1.000000                1.000000            0.200000            full
            tier0  conf_0.25              0.250000       1      0.05          0.95            1.000000            1.000000                1.000000            0.200000            full
      tier0_tier1  conf_0.00              0.000000      15      0.75          0.25            0.200000            0.533333                0.200000            0.216667            full
      tier0_tier1    trained              0.024451      13      0.65          0.35            0.153846            0.538462                0.150000            0.180000            full
      tier0_tier1  conf_0.05              0.050000      10      0.50          0.50            0.100000            0.500000                0.100000            0.133333            full
      tier0_tier1  conf_0.10              0.100000       5      0.25          0.75            0.200000            0.800000                0.125000            0.133333            full
      tier0_tier1  conf_0.15              0.150000       1      0.05          0.95            0.000000            1.000000                0.000000            0.000000            full
      tier0_tier1  conf_0.20              0.200000       1      0.05          0.95            0.000000            1.000000                0.000000            0.000000            full
      tier0_tier1  conf_0.25              0.250000       1      0.05          0.95            0.000000            1.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.00              0.000000      16      0.80          0.20            0.250000            0.437500                0.233333            0.226667            full
tier0_tier1_tier2    trained              0.028811      14      0.70          0.30            0.285714            0.500000                0.233333            0.226667            full
tier0_tier1_tier2  conf_0.05              0.050000      13      0.65          0.35            0.230769            0.461538                0.200000            0.200000            full
tier0_tier1_tier2  conf_0.10              0.100000      10      0.50          0.50            0.200000            0.400000                0.133333            0.080000            full
tier0_tier1_tier2  conf_0.15              0.150000       5      0.25          0.75            0.000000            0.400000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.20              0.200000       3      0.15          0.85            0.000000            0.666667                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.25              0.250000       2      0.10          0.90            0.000000            0.500000                0.000000            0.000000            full
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained             -0.043635      13      0.65          0.35            0.153846            0.461538                0.133333            0.130000            full
            tier0  conf_0.00              0.000000      12      0.60          0.40            0.083333            0.416667                0.066667            0.080000            full
            tier0  conf_0.05              0.050000      10      0.50          0.50            0.100000            0.500000                0.100000            0.100000            full
            tier0  conf_0.10              0.100000       8      0.40          0.60            0.125000            0.625000                0.125000            0.100000            full
            tier0  conf_0.15              0.150000       6      0.30          0.70            0.000000            0.500000                0.000000            0.000000            full
            tier0  conf_0.20              0.200000       3      0.15          0.85            0.000000            0.666667                0.000000            0.000000            full
            tier0  conf_0.25              0.250000       1      0.05          0.95            0.000000            1.000000                0.000000            0.000000            full
      tier0_tier1    trained              0.000000      15      0.75          0.25            0.133333            0.466667                0.116667            0.090000            full
      tier0_tier1  conf_0.00              0.000000      15      0.75          0.25            0.133333            0.466667                0.116667            0.090000            full
      tier0_tier1  conf_0.05              0.050000       9      0.45          0.55            0.111111            0.444444                0.050000            0.080000            full
      tier0_tier1  conf_0.10              0.100000       5      0.25          0.75            0.000000            0.200000                0.000000            0.000000            full
      tier0_tier1  conf_0.15              0.150000       2      0.10          0.90            0.000000            0.500000                0.000000            0.000000            full
      tier0_tier1  conf_0.20              0.200000       2      0.10          0.90            0.000000            0.500000                0.000000            0.000000            full
      tier0_tier1  conf_0.25              0.250000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.00              0.000000      11      0.55          0.45            0.181818            0.363636                0.116667            0.101587            full
tier0_tier1_tier2    trained              0.009214      10      0.50          0.50            0.200000            0.400000                0.145833            0.107143            full
tier0_tier1_tier2  conf_0.05              0.050000       7      0.35          0.65            0.000000            0.142857                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.10              0.100000       4      0.20          0.80            0.000000            0.250000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.15              0.150000       4      0.20          0.80            0.000000            0.250000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.20              0.200000       4      0.20          0.80            0.000000            0.250000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.25              0.250000       4      0.20          0.80            0.000000            0.250000                0.000000            0.000000            full
```

## Diagnosis Mode Comparison
- Whole-run and post-alert-window diagnosis are exported together so the diagnosis mode can be evaluated directly.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile diagnosis_target    diagnosis_mode  family_acc  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau                       status  min_class_count  min_group_count    group_key  include_workload
            tier0       20      0.35      0.60      0.350000  0.321429               0.024604                 0.015035            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.20      0.50      0.200000  0.177143               0.016255                 0.014652            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.30      0.55      0.300000  0.251429               0.017911                 0.016456            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.15      0.45      0.150000  0.147475               0.024902                 0.020440            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.15      0.40      0.150000  0.147436               0.017445                 0.013672            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.15      0.35      0.150000  0.128889               0.014450                 0.012611            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.20      0.60      0.200000  0.181538              -0.012055                -0.001969            full     hierarchical         whole_run        0.40      0.50          0.50            0.200000            0.700000                0.133333            0.166667            0.017807              0.013199           0.009908       -0.014112                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.25      0.60      0.250000  0.277778               0.008147                 0.009203            full     hierarchical         whole_run        0.45      0.65          0.35            0.153846            0.461538                0.150000            0.183333            0.025391              0.026494           0.016323        0.024451                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.20      0.40      0.200000  0.157143               0.013524                 0.016456            full     hierarchical         whole_run        0.35      0.65          0.35            0.307692            0.538462                0.333333            0.280000            0.018854              0.018840           0.008651        0.028811                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.15      0.45      0.150000  0.123810              -0.010978                 0.007178            full     hierarchical post_alert_window        0.40      0.60          0.40            0.083333            0.416667                0.066667            0.080000            0.017807              0.013199           0.009908       -0.043635                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.25      0.55      0.250000  0.230808               0.001949                 0.005190            full     hierarchical post_alert_window        0.45      0.65          0.35            0.076923            0.384615                0.066667            0.057143            0.025391              0.026494           0.016323        0.000000                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.25      0.40      0.250000  0.205983               0.006337                 0.001481            full     hierarchical post_alert_window        0.35      0.65          0.35            0.230769            0.384615                0.216667            0.201587            0.018854              0.018840           0.008651        0.009214                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.60      0.85      0.500000  0.421818               0.034753                 0.038507            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.55      0.90      0.416667  0.438889               0.020031                 0.015005            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.50      0.95      0.555556  0.556391               0.016143                 0.015710            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.574093         0.247992     0.177915              tier0            full
  BRANCH     0.608365         0.218432     0.173204              tier0            full
   CACHE     0.450199         0.192723     0.357078              tier0            full
   MEMBW     0.624005         0.218853     0.157142              tier0            full
     TLB     0.541866         0.266448     0.191686              tier0            full
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC                 compute       0.370147         0.305775             0.097024                 0.108828                 0.118226            full
  BRANCH                 compute       0.332183         0.375471             0.072219                 0.137789                 0.082338            full
   CACHE                 compute       0.520129         0.273203             0.058516                 0.076246                 0.071905            full
   MEMBW                 compute       0.347654         0.338866             0.080048                 0.110347                 0.123084            full
     TLB                 compute       0.382369         0.314650             0.094837                 0.109509                 0.098635            full
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
            tier0                    0.0                             0.0                           0.0                  0.3                    122.0                 689.0                 0.0                0.20                0.25            full
      tier0_tier1                    0.0                             0.0                           0.0                  0.5                    122.0                 506.4                 0.0                0.35                0.45            full
tier0_tier1_tier2                    0.0                             0.0                           0.0                  0.9                    122.0                 599.1                 0.0                0.65                0.80            full
```

## Files
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B120_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B120_a0.05_k3/config_runtime_summary.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B120_a0.05_k3/run_context.json`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B120_a0.05_k3/case_inventory.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B120_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B120_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B120_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B120_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B120_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B120_a0.05_k3/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B120_a0.05_k3/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B120_a0.05_k3/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B120_a0.05_k3/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B120_a0.05_k3/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B120_a0.05_k3/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B120_a0.05_k3/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B120_a0.05_k3/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B120_a0.05_k3/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B120_a0.05_k3/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B120_a0.05_k3/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B120_a0.05_k3/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B120_a0.05_k3/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B120_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B120_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B120_a0.05_k3/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B120_a0.05_k3/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B120_a0.05_k3/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B120_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B120_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B120_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B120_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B120_a0.05_k3/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B120_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B120_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B120_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B120_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B120_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B120_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B120_a0.05_k3/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B120_a0.05_k3/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B120_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B120_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B120_a0.05_k3/figures/fig_detection_latency.png`
