# DICE Full Retrain Results

## Setup
- Feature profile: mixed ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_core_5hz.csv', 'tier2': 'tier2_core_5hz.csv'})
- Protocol: global, benign-only fit/calibration, block_B=60, alpha=0.05, persist_k=3, gain=0.1
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
          mixed             tier0       24          46          2.167447     0.80 0.931899         1.0        1.0            0.0           0.30              0.013403              0.029459                      0.0                 0.015871
          mixed       tier0_tier1       24          57          2.671328     0.85 0.959180         1.0        1.0            0.0           0.45              0.000040              0.000101                      0.0                 0.000051
          mixed tier0_tier1_tier2       24          64          3.057514     0.85 0.959180         1.0        1.0            0.0           0.45              0.000043              0.000107                      0.0                 0.000058
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
          mixed   ATOMIC   0.8125 0.804167         1.0        1.0          0.000043          0.000094                  0.0             0.000048       2.182282      0.000052         48.677445         0.000048
          mixed   BRANCH   0.9375 0.950000         1.0        1.0          0.000043          0.000156                  0.0             0.000113       3.589120      0.000113        114.157074         0.000113
          mixed    CACHE   0.8125 0.804167         1.0        1.0          0.000043          0.000094                  0.0             0.000052       2.169738      0.000051         53.266941         0.000052
          mixed    MEMBW   0.9375 0.950000         1.0        1.0          0.000043          0.000157                  0.0             0.000094       3.632349      0.000115         94.668920         0.000094
          mixed      TLB   0.7500 0.679167         1.0        1.0          0.000043          0.000101                  0.0             0.000054       2.346447      0.000059         55.321881         0.000054
```

## Paper-style Aggregates (Final Config)
- Base score mean stressor AUC-PR (all five): **0.8375**
- Base score mean stressor ROC-AUC (all five): **0.8500**
- WC score mean stressor AUC-PR (all five): **1.0000**
- WC score mean stressor ROC-AUC (all five): **1.0000**
- Base score mean stressor AUC-PR (excluding BRANCH/TLB): **0.8528**
- Base score mean stressor ROC-AUC (excluding BRANCH/TLB): **0.8542**
- WC score mean stressor AUC-PR (excluding BRANCH/TLB): **1.0000**
- WC score mean stressor ROC-AUC (excluding BRANCH/TLB): **1.0000**

## Diagnosis
- Feature-level diagnosis uses normalized whole-run residual-attribution prototypes as the default paper-facing result, with diagnosis-only filtering that removes monotonic counters and downweights generic memory-state features.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.35      0.60          0.35  0.327778               0.022331                 0.018978           mixed
      tier0_tier1       20      0.25      0.55          0.25  0.165714               0.015018                 0.017877           mixed
tier0_tier1_tier2       20      0.30      0.70          0.30  0.274237               0.013200                 0.009117           mixed
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.25      0.55          0.25  0.228889               0.019916                 0.016016           mixed
      tier0_tier1       20      0.15      0.30          0.15  0.161111               0.064193                 0.032323           mixed
tier0_tier1_tier2       20      0.10      0.35          0.10  0.101587               0.055882                 0.024045           mixed
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.25      0.55          0.25  0.252237               0.023188                 0.021227           mixed
      tier0_tier1       20      0.30      0.55          0.30  0.304286               0.018930                 0.016507           mixed
tier0_tier1_tier2       20      0.30      0.55          0.30  0.272727               0.015468                 0.009998           mixed
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.65      0.85      0.583333  0.472222               0.031892                 0.037866           mixed
      tier0_tier1       20      0.45      0.75      0.416667  0.335664               0.021768                 0.023093           mixed
tier0_tier1_tier2       20      0.55      0.70      0.527778  0.487302               0.020867                 0.020760           mixed
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.35      0.55        0.50          0.35  0.325455      0.65          0.35            0.384615            0.538462                0.400000            0.347619              -0.008631                 0.000810            0.016170              0.016470           0.010574       -0.036184           mixed
      tier0_tier1       20      0.25      0.55        0.45          0.25  0.194872      0.45          0.55            0.444444            0.666667                0.466667            0.313333              -0.006517                -0.000233            0.024821              0.026023           0.009983        0.032828           mixed
tier0_tier1_tier2       20      0.10      0.65        0.40          0.10  0.087912      0.60          0.40            0.166667            0.583333                0.200000            0.130000               0.004158                 0.004881            0.021405              0.015799           0.015908        0.036542           mixed
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.30      0.55        0.50          0.30  0.280476      0.65          0.35            0.307692            0.538462                0.266667            0.216667              -0.015502                 0.014147            0.016170              0.016470           0.010574       -0.009037           mixed
      tier0_tier1       20      0.25      0.45        0.45          0.25  0.158974      0.30          0.70            0.333333            0.500000                0.400000            0.300000              -0.060261                -0.032764            0.024821              0.026023           0.009983        0.075592           mixed
tier0_tier1_tier2       20      0.10      0.20        0.40          0.10  0.080000      0.70          0.30            0.071429            0.214286                0.050000            0.050000               0.000712                 0.003980            0.021405              0.015799           0.015908       -0.058377           mixed
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained             -0.036184      13      0.65          0.35            0.384615            0.538462                0.400000            0.347619           mixed
            tier0  conf_0.00              0.000000      12      0.60          0.40            0.416667            0.583333                0.433333            0.380952           mixed
            tier0  conf_0.05              0.050000       6      0.30          0.70            0.500000            0.500000                0.500000            0.293333           mixed
            tier0  conf_0.10              0.100000       6      0.30          0.70            0.500000            0.500000                0.500000            0.293333           mixed
            tier0  conf_0.15              0.150000       4      0.20          0.80            0.750000            0.750000                0.666667            0.360000           mixed
            tier0  conf_0.20              0.200000       2      0.10          0.90            1.000000            1.000000                1.000000            0.200000           mixed
            tier0  conf_0.25              0.250000       1      0.05          0.95            1.000000            1.000000                1.000000            0.200000           mixed
      tier0_tier1  conf_0.00              0.000000      11      0.55          0.45            0.272727            0.636364                0.266667            0.180000           mixed
      tier0_tier1    trained              0.032828       8      0.40          0.60            0.250000            0.625000                0.266667            0.166667           mixed
      tier0_tier1  conf_0.05              0.050000       7      0.35          0.65            0.285714            0.714286                0.333333            0.166667           mixed
      tier0_tier1  conf_0.10              0.100000       5      0.25          0.75            0.200000            0.600000                0.333333            0.066667           mixed
      tier0_tier1  conf_0.15              0.150000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.20              0.200000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
      tier0_tier1  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
tier0_tier1_tier2  conf_0.00              0.000000      17      0.85          0.15            0.117647            0.647059                0.133333            0.103030           mixed
tier0_tier1_tier2    trained              0.036542       9      0.45          0.55            0.111111            0.555556                0.200000            0.050000           mixed
tier0_tier1_tier2  conf_0.05              0.050000       8      0.40          0.60            0.125000            0.500000                0.200000            0.057143           mixed
tier0_tier1_tier2  conf_0.10              0.100000       4      0.20          0.80            0.250000            0.500000                0.250000            0.080000           mixed
tier0_tier1_tier2  conf_0.15              0.150000       1      0.05          0.95            1.000000            1.000000                1.000000            0.200000           mixed
tier0_tier1_tier2  conf_0.20              0.200000       1      0.05          0.95            1.000000            1.000000                1.000000            0.200000           mixed
tier0_tier1_tier2  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained             -0.009037      13      0.65          0.35            0.307692            0.538462                0.266667            0.216667           mixed
            tier0  conf_0.00              0.000000      13      0.65          0.35            0.307692            0.538462                0.266667            0.216667           mixed
            tier0  conf_0.05              0.050000      11      0.55          0.45            0.363636            0.636364                0.266667            0.238095           mixed
            tier0  conf_0.10              0.100000       8      0.40          0.60            0.500000            0.625000                0.444444            0.271429           mixed
            tier0  conf_0.15              0.150000       4      0.20          0.80            0.500000            0.750000                0.666667            0.300000           mixed
            tier0  conf_0.20              0.200000       1      0.05          0.95            0.000000            1.000000                0.000000            0.000000           mixed
            tier0  conf_0.25              0.250000       1      0.05          0.95            0.000000            1.000000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.00              0.000000       8      0.40          0.60            0.125000            0.375000                0.200000            0.100000           mixed
      tier0_tier1  conf_0.05              0.050000       6      0.30          0.70            0.166667            0.500000                0.250000            0.133333           mixed
      tier0_tier1    trained              0.075592       4      0.20          0.80            0.000000            0.250000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.10              0.100000       4      0.20          0.80            0.000000            0.250000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.15              0.150000       3      0.15          0.85            0.000000            0.333333                0.000000            0.000000           mixed
      tier0_tier1  conf_0.20              0.200000       3      0.15          0.85            0.000000            0.333333                0.000000            0.000000           mixed
      tier0_tier1  conf_0.25              0.250000       1      0.05          0.95            0.000000            1.000000                0.000000            0.000000           mixed
tier0_tier1_tier2    trained             -0.058377      14      0.70          0.30            0.071429            0.214286                0.050000            0.057143           mixed
tier0_tier1_tier2  conf_0.00              0.000000      14      0.70          0.30            0.071429            0.214286                0.050000            0.057143           mixed
tier0_tier1_tier2  conf_0.05              0.050000       8      0.40          0.60            0.125000            0.125000                0.100000            0.100000           mixed
tier0_tier1_tier2  conf_0.10              0.100000       6      0.30          0.70            0.000000            0.000000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.15              0.150000       5      0.25          0.75            0.000000            0.000000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.20              0.200000       4      0.20          0.80            0.000000            0.000000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.25              0.250000       4      0.20          0.80            0.000000            0.000000                0.000000            0.000000           mixed
```

## Diagnosis Mode Comparison
- Whole-run and post-alert-window diagnosis are exported together so the diagnosis mode can be evaluated directly.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile diagnosis_target    diagnosis_mode  family_acc  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau                       status  min_class_count  min_group_count    group_key  include_workload
            tier0       20      0.35      0.60      0.350000  0.327778               0.022331                 0.018978           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.25      0.55      0.250000  0.165714               0.015018                 0.017877           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.30      0.70      0.300000  0.274237               0.013200                 0.009117           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.25      0.55      0.250000  0.228889               0.019916                 0.016016           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.15      0.30      0.150000  0.161111               0.064193                 0.032323           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.10      0.35      0.100000  0.101587               0.055882                 0.024045           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.35      0.55      0.350000  0.325455              -0.008631                 0.000810           mixed     hierarchical         whole_run        0.50      0.65          0.35            0.384615            0.538462                0.400000            0.347619            0.016170              0.016470           0.010574       -0.036184                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.25      0.55      0.250000  0.194872              -0.006517                -0.000233           mixed     hierarchical         whole_run        0.45      0.45          0.55            0.444444            0.666667                0.466667            0.313333            0.024821              0.026023           0.009983        0.032828                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.10      0.65      0.100000  0.087912               0.004158                 0.004881           mixed     hierarchical         whole_run        0.40      0.60          0.40            0.166667            0.583333                0.200000            0.130000            0.021405              0.015799           0.015908        0.036542                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.30      0.55      0.300000  0.280476              -0.015502                 0.014147           mixed     hierarchical post_alert_window        0.50      0.65          0.35            0.307692            0.538462                0.266667            0.216667            0.016170              0.016470           0.010574       -0.009037                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.25      0.45      0.250000  0.158974              -0.060261                -0.032764           mixed     hierarchical post_alert_window        0.45      0.30          0.70            0.333333            0.500000                0.400000            0.300000            0.024821              0.026023           0.009983        0.075592                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.10      0.20      0.100000  0.080000               0.000712                 0.003980           mixed     hierarchical post_alert_window        0.40      0.70          0.30            0.071429            0.214286                0.050000            0.050000            0.021405              0.015799           0.015908       -0.058377                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.65      0.85      0.583333  0.472222               0.031892                 0.037866           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.45      0.75      0.416667  0.335664               0.021768                 0.023093           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.55      0.70      0.527778  0.487302               0.020867                 0.020760           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.683707         0.169840     0.146453              tier0           mixed
  BRANCH     0.758361         0.099595     0.142044              tier0           mixed
   CACHE     0.539050         0.358913     0.102037              tier0           mixed
   MEMBW     0.783015         0.101510     0.115474              tier0           mixed
     TLB     0.696228         0.154108     0.149663              tier0           mixed
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC               memory_io       0.269862         0.391260             0.104625                 0.196688                 0.037565           mixed
  BRANCH               memory_io       0.246190         0.461238             0.055126                 0.186148                 0.051298           mixed
   CACHE                 compute       0.473300         0.267919             0.070193                 0.130531                 0.058057           mixed
   MEMBW               memory_io       0.242217         0.475112             0.058160                 0.157809                 0.066703           mixed
     TLB               memory_io       0.300793         0.400825             0.083295                 0.181032                 0.034055           mixed
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
            tier0                    0.0                             0.0                           0.0                 0.30                     75.0                 724.0                 0.2                 0.2                 0.2           mixed
      tier0_tier1                    0.0                             0.0                           0.0                 0.45                     62.0                 587.4                 0.3                 0.3                 0.4           mixed
tier0_tier1_tier2                    0.0                             0.0                           0.0                 0.45                     62.0                 544.8                 0.3                 0.3                 0.4           mixed
```

## Files
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B60_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B60_a0.05_k3/config_runtime_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B60_a0.05_k3/run_context.json`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B60_a0.05_k3/case_inventory.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B60_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B60_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B60_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B60_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B60_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B60_a0.05_k3/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B60_a0.05_k3/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B60_a0.05_k3/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B60_a0.05_k3/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B60_a0.05_k3/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B60_a0.05_k3/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B60_a0.05_k3/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B60_a0.05_k3/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B60_a0.05_k3/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B60_a0.05_k3/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B60_a0.05_k3/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B60_a0.05_k3/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B60_a0.05_k3/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B60_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B60_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B60_a0.05_k3/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B60_a0.05_k3/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B60_a0.05_k3/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B60_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B60_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B60_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B60_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B60_a0.05_k3/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B60_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B60_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B60_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B60_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B60_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B60_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B60_a0.05_k3/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B60_a0.05_k3/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B60_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B60_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B60_a0.05_k3/figures/fig_detection_latency.png`
