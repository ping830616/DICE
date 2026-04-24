# DICE Full Retrain Results

## Setup
- Feature profile: full ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_full_5hz.csv', 'tier2': 'tier2_full_5hz.csv'})
- Protocol: global, benign-only fit/calibration, block_B=60, alpha=0.05, persist_k=3, gain=0.1
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
           full             tier0       24          46          2.323928   0.8000 0.931899         1.0        1.0            0.0           0.30              0.013403              0.029459                      0.0                 0.015871
           full       tier0_tier1       24          64          3.059177   0.8500 0.962016         1.0        1.0            0.0           0.60              0.019761              0.056633                      0.0                 0.027089
           full tier0_tier1_tier2       24          75          3.656244   0.9875 0.997619         1.0        1.0            0.0           0.95              0.002907              0.008229                      0.0                 0.004931
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc  pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
           full   ATOMIC   0.9375    0.95         1.0        1.0          0.002907          0.007628                  0.0             0.004957       2.623673      0.004721       4957.847688         0.004957
           full   BRANCH   1.0000    1.00         1.0        1.0          0.002907          0.007651                  0.0             0.005577       2.631646      0.004745       5577.853590         0.005577
           full    CACHE   1.0000    1.00         1.0        1.0          0.002907          0.009789                  0.0             0.006771       3.366646      0.006882       6771.883621         0.006771
           full    MEMBW   1.0000    1.00         1.0        1.0          0.002907          0.008691                  0.0             0.005669       2.989203      0.005784       5670.210004         0.005669
           full      TLB   1.0000    1.00         1.0        1.0          0.002907          0.006102                  0.0             0.004261       2.098685      0.003195       4262.062062         0.004261
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
            tier0       20      0.35      0.60          0.35  0.327778               0.022331                 0.018978            full
      tier0_tier1       20      0.20      0.50          0.20  0.177143               0.016286                 0.015031            full
tier0_tier1_tier2       20      0.30      0.55          0.30  0.251429               0.017291                 0.015192            full
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.25      0.55          0.25  0.228889               0.019916                 0.016016            full
      tier0_tier1       20      0.15      0.40          0.15  0.146667               0.041158                 0.031755            full
tier0_tier1_tier2       20      0.10      0.40          0.10  0.076364               0.026051                 0.020562            full
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.25      0.55          0.25  0.252237               0.023188                 0.021227            full
      tier0_tier1       20      0.50      0.75          0.50  0.516508               0.018833                 0.012139            full
tier0_tier1_tier2       20      0.35      0.55          0.35  0.337013               0.013736                 0.009488            full
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.65      0.85      0.583333  0.472222               0.031892                 0.037866            full
      tier0_tier1       20      0.55      0.90      0.416667  0.438889               0.019628                 0.012652            full
tier0_tier1_tier2       20      0.45      0.95      0.472222  0.503663               0.015859                 0.012796            full
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.35      0.55        0.50          0.35  0.325455      0.65          0.35            0.384615            0.538462                0.400000            0.347619              -0.008631                 0.000810            0.016170              0.016470           0.010574       -0.036184            full
      tier0_tier1       20      0.35      0.60        0.50          0.35  0.378571      0.80          0.20            0.312500            0.562500                0.316667            0.326840               0.009956                 0.014868            0.025337              0.022885           0.013611        0.025121            full
tier0_tier1_tier2       20      0.20      0.40        0.35          0.20  0.157143      0.60          0.40            0.333333            0.583333                0.333333            0.280000               0.012465                 0.016875            0.020070              0.018331           0.010273        0.043741            full
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.30      0.55        0.50          0.30  0.280476      0.65          0.35            0.307692            0.538462                0.266667            0.216667              -0.015502                 0.014147            0.016170              0.016470           0.010574       -0.009037            full
      tier0_tier1       20      0.25      0.50        0.50          0.25  0.222222      0.25          0.75            0.200000            0.400000                0.250000            0.133333              -0.003707                 0.016339            0.025337              0.022885           0.013611        0.140507            full
tier0_tier1_tier2       20      0.25      0.45        0.35          0.25  0.200427      0.60          0.40            0.166667            0.416667                0.133333            0.101587              -0.003536                -0.003488            0.020070              0.018331           0.010273       -0.099384            full
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained             -0.036184      13      0.65          0.35            0.384615            0.538462                0.400000            0.347619            full
            tier0  conf_0.00              0.000000      12      0.60          0.40            0.416667            0.583333                0.433333            0.380952            full
            tier0  conf_0.05              0.050000       6      0.30          0.70            0.500000            0.500000                0.500000            0.293333            full
            tier0  conf_0.10              0.100000       6      0.30          0.70            0.500000            0.500000                0.500000            0.293333            full
            tier0  conf_0.15              0.150000       4      0.20          0.80            0.750000            0.750000                0.666667            0.360000            full
            tier0  conf_0.20              0.200000       2      0.10          0.90            1.000000            1.000000                1.000000            0.200000            full
            tier0  conf_0.25              0.250000       1      0.05          0.95            1.000000            1.000000                1.000000            0.200000            full
      tier0_tier1  conf_0.00              0.000000      17      0.85          0.15            0.352941            0.588235                0.366667            0.393506            full
      tier0_tier1    trained              0.025121      13      0.65          0.35            0.230769            0.538462                0.200000            0.173333            full
      tier0_tier1  conf_0.05              0.050000      11      0.55          0.45            0.272727            0.545455                0.233333            0.204444            full
      tier0_tier1  conf_0.10              0.100000       6      0.30          0.70            0.166667            0.666667                0.125000            0.133333            full
      tier0_tier1  conf_0.15              0.150000       2      0.10          0.90            0.000000            1.000000                0.000000            0.000000            full
      tier0_tier1  conf_0.20              0.200000       1      0.05          0.95            0.000000            1.000000                0.000000            0.000000            full
      tier0_tier1  conf_0.25              0.250000       1      0.05          0.95            0.000000            1.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.00              0.000000      16      0.80          0.20            0.250000            0.437500                0.233333            0.226667            full
tier0_tier1_tier2    trained              0.043741      14      0.70          0.30            0.285714            0.500000                0.233333            0.226667            full
tier0_tier1_tier2  conf_0.05              0.050000      13      0.65          0.35            0.230769            0.461538                0.200000            0.200000            full
tier0_tier1_tier2  conf_0.10              0.100000      10      0.50          0.50            0.200000            0.400000                0.133333            0.080000            full
tier0_tier1_tier2  conf_0.15              0.150000       6      0.30          0.70            0.166667            0.500000                0.250000            0.066667            full
tier0_tier1_tier2  conf_0.20              0.200000       3      0.15          0.85            0.000000            0.666667                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.25              0.250000       2      0.10          0.90            0.000000            0.500000                0.000000            0.000000            full
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained             -0.009037      13      0.65          0.35            0.307692            0.538462                0.266667            0.216667            full
            tier0  conf_0.00              0.000000      13      0.65          0.35            0.307692            0.538462                0.266667            0.216667            full
            tier0  conf_0.05              0.050000      11      0.55          0.45            0.363636            0.636364                0.266667            0.238095            full
            tier0  conf_0.10              0.100000       8      0.40          0.60            0.500000            0.625000                0.444444            0.271429            full
            tier0  conf_0.15              0.150000       4      0.20          0.80            0.500000            0.750000                0.666667            0.300000            full
            tier0  conf_0.20              0.200000       1      0.05          0.95            0.000000            1.000000                0.000000            0.000000            full
            tier0  conf_0.25              0.250000       1      0.05          0.95            0.000000            1.000000                0.000000            0.000000            full
      tier0_tier1  conf_0.00              0.000000      15      0.75          0.25            0.200000            0.533333                0.200000            0.214286            full
      tier0_tier1  conf_0.05              0.050000      11      0.55          0.45            0.090909            0.454545                0.100000            0.100000            full
      tier0_tier1  conf_0.10              0.100000       8      0.40          0.60            0.000000            0.375000                0.000000            0.000000            full
      tier0_tier1    trained              0.140507       6      0.30          0.70            0.000000            0.333333                0.000000            0.000000            full
      tier0_tier1  conf_0.15              0.150000       6      0.30          0.70            0.000000            0.333333                0.000000            0.000000            full
      tier0_tier1  conf_0.20              0.200000       2      0.10          0.90            0.000000            0.000000                0.000000            0.000000            full
      tier0_tier1  conf_0.25              0.250000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2    trained             -0.099384      15      0.75          0.25            0.200000            0.400000                0.183333            0.161111            full
tier0_tier1_tier2  conf_0.00              0.000000      10      0.50          0.50            0.100000            0.400000                0.050000            0.050000            full
tier0_tier1_tier2  conf_0.05              0.050000       7      0.35          0.65            0.142857            0.285714                0.100000            0.066667            full
tier0_tier1_tier2  conf_0.10              0.100000       4      0.20          0.80            0.000000            0.250000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.15              0.150000       4      0.20          0.80            0.000000            0.250000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.20              0.200000       4      0.20          0.80            0.000000            0.250000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.25              0.250000       4      0.20          0.80            0.000000            0.250000                0.000000            0.000000            full
```

## Diagnosis Mode Comparison
- Whole-run and post-alert-window diagnosis are exported together so the diagnosis mode can be evaluated directly.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile diagnosis_target    diagnosis_mode  family_acc  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau                       status  min_class_count  min_group_count    group_key  include_workload
            tier0       20      0.35      0.60      0.350000  0.327778               0.022331                 0.018978            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.20      0.50      0.200000  0.177143               0.016286                 0.015031            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.30      0.55      0.300000  0.251429               0.017291                 0.015192            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.25      0.55      0.250000  0.228889               0.019916                 0.016016            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.15      0.40      0.150000  0.146667               0.041158                 0.031755            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.10      0.40      0.100000  0.076364               0.026051                 0.020562            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.35      0.55      0.350000  0.325455              -0.008631                 0.000810            full     hierarchical         whole_run        0.50      0.65          0.35            0.384615            0.538462                0.400000            0.347619            0.016170              0.016470           0.010574       -0.036184                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.35      0.60      0.350000  0.378571               0.009956                 0.014868            full     hierarchical         whole_run        0.50      0.80          0.20            0.312500            0.562500                0.316667            0.326840            0.025337              0.022885           0.013611        0.025121                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.20      0.40      0.200000  0.157143               0.012465                 0.016875            full     hierarchical         whole_run        0.35      0.60          0.40            0.333333            0.583333                0.333333            0.280000            0.020070              0.018331           0.010273        0.043741                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.30      0.55      0.300000  0.280476              -0.015502                 0.014147            full     hierarchical post_alert_window        0.50      0.65          0.35            0.307692            0.538462                0.266667            0.216667            0.016170              0.016470           0.010574       -0.009037                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.25      0.50      0.250000  0.222222              -0.003707                 0.016339            full     hierarchical post_alert_window        0.50      0.25          0.75            0.200000            0.400000                0.250000            0.133333            0.025337              0.022885           0.013611        0.140507                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.25      0.45      0.250000  0.200427              -0.003536                -0.003488            full     hierarchical post_alert_window        0.35      0.60          0.40            0.166667            0.416667                0.133333            0.101587            0.020070              0.018331           0.010273       -0.099384                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.65      0.85      0.583333  0.472222               0.031892                 0.037866            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.55      0.90      0.416667  0.438889               0.019628                 0.012652            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.45      0.95      0.472222  0.503663               0.015859                 0.012796            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.551065         0.247849     0.201085              tier0            full
  BRANCH     0.588710         0.216688     0.194603              tier0            full
   CACHE     0.433387         0.188978     0.377635              tier0            full
   MEMBW     0.602214         0.219769     0.178017              tier0            full
     TLB     0.520992         0.264541     0.214467              tier0            full
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC                 compute       0.386123         0.280925             0.105913                 0.116153                 0.110886            full
  BRANCH                 compute       0.345111         0.347210             0.079237                 0.150514                 0.077927            full
   CACHE                 compute       0.535207         0.250195             0.064378                 0.082503                 0.067717            full
   MEMBW                 compute       0.364091         0.313748             0.087689                 0.117450                 0.117021            full
     TLB                 compute       0.398060         0.287378             0.104107                 0.117124                 0.093331            full
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
            tier0                    0.0                             0.0                           0.0                 0.30                     75.0                 724.0                0.20                 0.2                 0.2            full
      tier0_tier1                    0.0                             0.0                           0.0                 0.60                     75.5                 795.0                0.40                 0.4                 0.5            full
tier0_tier1_tier2                    0.0                             0.0                           0.0                 0.95                     62.0                 667.4                0.65                 0.7                 0.8            full
```

## Files
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B60_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B60_a0.05_k3/config_runtime_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B60_a0.05_k3/run_context.json`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B60_a0.05_k3/case_inventory.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B60_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B60_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B60_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B60_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B60_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B60_a0.05_k3/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B60_a0.05_k3/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B60_a0.05_k3/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B60_a0.05_k3/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B60_a0.05_k3/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B60_a0.05_k3/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B60_a0.05_k3/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B60_a0.05_k3/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B60_a0.05_k3/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B60_a0.05_k3/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B60_a0.05_k3/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B60_a0.05_k3/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B60_a0.05_k3/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B60_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B60_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B60_a0.05_k3/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B60_a0.05_k3/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B60_a0.05_k3/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B60_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B60_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B60_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B60_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B60_a0.05_k3/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B60_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B60_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B60_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B60_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B60_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B60_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B60_a0.05_k3/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B60_a0.05_k3/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B60_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B60_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B60_a0.05_k3/figures/fig_detection_latency.png`
