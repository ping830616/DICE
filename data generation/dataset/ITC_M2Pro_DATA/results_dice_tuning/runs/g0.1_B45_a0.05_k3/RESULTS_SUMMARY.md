# DICE Full Retrain Results

## Setup
- Feature profile: mixed ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_core_5hz.csv', 'tier2': 'tier2_core_5hz.csv'})
- Protocol: global, benign-only fit/calibration, block_B=45, alpha=0.05, persist_k=3, gain=0.1
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
          mixed             tier0       24          46          2.447548   0.8000 0.931899         1.0        1.0            0.0            0.3              0.014150              0.029909                      0.0                 0.016063
          mixed       tier0_tier1       24          57          2.909883   0.8250 0.951460         1.0        1.0            0.0            0.5              0.000041              0.000102                      0.0                 0.000050
          mixed tier0_tier1_tier2       24          64          3.255394   0.8625 0.964180         1.0        1.0            0.0            0.5              0.000044              0.000108                      0.0                 0.000058
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
          mixed   ATOMIC   0.8125 0.804167         1.0        1.0          0.000044          0.000091                  0.0             0.000041       2.072410      0.000048         42.167867         0.000041
          mixed   BRANCH   1.0000 1.000000         1.0        1.0          0.000044          0.000162                  0.0             0.000119       3.667086      0.000119        119.909045         0.000119
          mixed    CACHE   0.8125 0.804167         1.0        1.0          0.000044          0.000094                  0.0             0.000052       2.131463      0.000050         52.698346         0.000052
          mixed    MEMBW   0.9375 0.950000         1.0        1.0          0.000044          0.000153                  0.0             0.000089       3.443151      0.000109         89.812245         0.000089
          mixed      TLB   0.7500 0.679167         1.0        1.0          0.000044          0.000104                  0.0             0.000054       2.354438      0.000060         55.415313         0.000054
```

## Paper-style Aggregates (Final Config)
- Base score mean stressor AUC-PR (all five): **0.8475**
- Base score mean stressor ROC-AUC (all five): **0.8625**
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
            tier0       20      0.35      0.60          0.35  0.327778               0.022145                 0.017375           mixed
      tier0_tier1       20      0.20      0.60          0.20  0.134266               0.014510                 0.017462           mixed
tier0_tier1_tier2       20      0.35      0.75          0.35  0.352015               0.013033                 0.007904           mixed
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.25       0.5          0.25  0.217778               0.020990                 0.018667           mixed
      tier0_tier1       20      0.10       0.3          0.10  0.103030               0.084075                 0.063268           mixed
tier0_tier1_tier2       20      0.15       0.4          0.15  0.163810               0.063692                 0.029394           mixed
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.25      0.55          0.25  0.252237               0.022254                 0.019441           mixed
      tier0_tier1       20      0.30      0.55          0.30  0.304286               0.020341                 0.017031           mixed
tier0_tier1_tier2       20      0.30      0.55          0.30  0.272727               0.017141                 0.012452           mixed
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.65       0.9      0.583333  0.472222               0.031960                 0.038648           mixed
      tier0_tier1       20      0.45       0.8      0.416667  0.335664               0.021206                 0.020079           mixed
tier0_tier1_tier2       20      0.55       0.7      0.527778  0.487302               0.020654                 0.019404           mixed
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.40      0.55        0.50          0.40  0.362424      0.35          0.65            0.571429            0.571429                0.400000            0.293333              -0.008018                 0.001038            0.016543              0.016098           0.011657        0.089746           mixed
      tier0_tier1       20      0.25      0.55        0.45          0.25  0.191409      0.45          0.55            0.444444            0.666667                0.466667            0.313333              -0.005792                 0.000039            0.026178              0.027628           0.010012        0.032136           mixed
tier0_tier1_tier2       20      0.25      0.70        0.40          0.25  0.232900      0.45          0.55            0.333333            0.777778                0.400000            0.300000               0.001926                 0.004410            0.022908              0.017719           0.015561        0.104428           mixed
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.35      0.60        0.50          0.35  0.336032      0.45          0.55            0.444444            0.555556                0.266667            0.251429              -0.016987                 0.013662            0.016543              0.016098           0.011657       -0.026379           mixed
      tier0_tier1       20      0.25      0.35        0.45          0.25  0.158974      0.55          0.45            0.272727            0.363636                0.300000            0.194286              -0.082626                -0.055683            0.026178              0.027628           0.010012       -0.134331           mixed
tier0_tier1_tier2       20      0.15      0.35        0.40          0.15  0.112727      0.65          0.35            0.076923            0.307692                0.066667            0.057143               0.000605                 0.000755            0.022908              0.017719           0.015561       -0.050931           mixed
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0  conf_0.00              0.000000      12      0.60          0.40            0.500000            0.583333                0.500000            0.416667           mixed
            tier0  conf_0.05              0.050000       6      0.30          0.70            0.500000            0.500000                0.500000            0.293333           mixed
            tier0    trained              0.089746       6      0.30          0.70            0.500000            0.500000                0.500000            0.293333           mixed
            tier0  conf_0.10              0.100000       6      0.30          0.70            0.500000            0.500000                0.500000            0.293333           mixed
            tier0  conf_0.15              0.150000       3      0.15          0.85            1.000000            1.000000                1.000000            0.400000           mixed
            tier0  conf_0.20              0.200000       2      0.10          0.90            1.000000            1.000000                1.000000            0.200000           mixed
            tier0  conf_0.25              0.250000       1      0.05          0.95            1.000000            1.000000                1.000000            0.200000           mixed
      tier0_tier1  conf_0.00              0.000000      11      0.55          0.45            0.181818            0.545455                0.166667            0.123810           mixed
      tier0_tier1    trained              0.032136       7      0.35          0.65            0.285714            0.714286                0.333333            0.166667           mixed
      tier0_tier1  conf_0.05              0.050000       7      0.35          0.65            0.285714            0.714286                0.333333            0.166667           mixed
      tier0_tier1  conf_0.10              0.100000       5      0.25          0.75            0.200000            0.600000                0.333333            0.066667           mixed
      tier0_tier1  conf_0.15              0.150000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
      tier0_tier1  conf_0.20              0.200000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
      tier0_tier1  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
tier0_tier1_tier2  conf_0.00              0.000000      16      0.80          0.20            0.250000            0.687500                0.250000            0.234921           mixed
tier0_tier1_tier2  conf_0.05              0.050000       6      0.30          0.70            0.166667            0.500000                0.200000            0.066667           mixed
tier0_tier1_tier2  conf_0.10              0.100000       3      0.15          0.85            0.333333            0.333333                0.333333            0.100000           mixed
tier0_tier1_tier2    trained              0.104428       3      0.15          0.85            0.333333            0.333333                0.333333            0.100000           mixed
tier0_tier1_tier2  conf_0.15              0.150000       1      0.05          0.95            1.000000            1.000000                1.000000            0.200000           mixed
tier0_tier1_tier2  conf_0.20              0.200000       1      0.05          0.95            1.000000            1.000000                1.000000            0.200000           mixed
tier0_tier1_tier2  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained             -0.026379      12      0.60          0.40            0.333333            0.583333                0.266667            0.238095           mixed
            tier0  conf_0.00              0.000000      12      0.60          0.40            0.333333            0.583333                0.266667            0.238095           mixed
            tier0  conf_0.05              0.050000      10      0.50          0.50            0.400000            0.700000                0.266667            0.266667           mixed
            tier0  conf_0.10              0.100000       7      0.35          0.65            0.571429            0.714286                0.444444            0.280000           mixed
            tier0  conf_0.15              0.150000       5      0.25          0.75            0.600000            0.800000                0.666667            0.300000           mixed
            tier0  conf_0.20              0.200000       3      0.15          0.85            0.333333            0.666667                0.500000            0.200000           mixed
            tier0  conf_0.25              0.250000       2      0.10          0.90            0.500000            1.000000                0.500000            0.200000           mixed
      tier0_tier1    trained             -0.134331       9      0.45          0.55            0.222222            0.333333                0.250000            0.133333           mixed
      tier0_tier1  conf_0.00              0.000000       8      0.40          0.60            0.250000            0.375000                0.250000            0.160000           mixed
      tier0_tier1  conf_0.05              0.050000       5      0.25          0.75            0.200000            0.400000                0.333333            0.133333           mixed
      tier0_tier1  conf_0.10              0.100000       2      0.10          0.90            0.000000            0.000000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.15              0.150000       2      0.10          0.90            0.000000            0.000000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.20              0.200000       2      0.10          0.90            0.000000            0.000000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.25              0.250000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000           mixed
tier0_tier1_tier2    trained             -0.050931      14      0.70          0.30            0.142857            0.357143                0.133333            0.123810           mixed
tier0_tier1_tier2  conf_0.00              0.000000      12      0.60          0.40            0.083333            0.250000                0.066667            0.080000           mixed
tier0_tier1_tier2  conf_0.05              0.050000       7      0.35          0.65            0.142857            0.285714                0.100000            0.100000           mixed
tier0_tier1_tier2  conf_0.10              0.100000       6      0.30          0.70            0.000000            0.166667                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.15              0.150000       6      0.30          0.70            0.000000            0.166667                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.20              0.200000       5      0.25          0.75            0.000000            0.200000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.25              0.250000       4      0.20          0.80            0.000000            0.250000                0.000000            0.000000           mixed
```

## Diagnosis Mode Comparison
- Whole-run and post-alert-window diagnosis are exported together so the diagnosis mode can be evaluated directly.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile diagnosis_target    diagnosis_mode  family_acc  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau                       status  min_class_count  min_group_count    group_key  include_workload
            tier0       20      0.35      0.60      0.350000  0.327778               0.022145                 0.017375           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.20      0.60      0.200000  0.134266               0.014510                 0.017462           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.35      0.75      0.350000  0.352015               0.013033                 0.007904           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.25      0.50      0.250000  0.217778               0.020990                 0.018667           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.10      0.30      0.100000  0.103030               0.084075                 0.063268           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.15      0.40      0.150000  0.163810               0.063692                 0.029394           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.40      0.55      0.400000  0.362424              -0.008018                 0.001038           mixed     hierarchical         whole_run        0.50      0.35          0.65            0.571429            0.571429                0.400000            0.293333            0.016543              0.016098           0.011657        0.089746                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.25      0.55      0.250000  0.191409              -0.005792                 0.000039           mixed     hierarchical         whole_run        0.45      0.45          0.55            0.444444            0.666667                0.466667            0.313333            0.026178              0.027628           0.010012        0.032136                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.25      0.70      0.250000  0.232900               0.001926                 0.004410           mixed     hierarchical         whole_run        0.40      0.45          0.55            0.333333            0.777778                0.400000            0.300000            0.022908              0.017719           0.015561        0.104428                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.35      0.60      0.350000  0.336032              -0.016987                 0.013662           mixed     hierarchical post_alert_window        0.50      0.45          0.55            0.444444            0.555556                0.266667            0.251429            0.016543              0.016098           0.011657       -0.026379                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.25      0.35      0.250000  0.158974              -0.082626                -0.055683           mixed     hierarchical post_alert_window        0.45      0.55          0.45            0.272727            0.363636                0.300000            0.194286            0.026178              0.027628           0.010012       -0.134331                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.15      0.35      0.150000  0.112727               0.000605                 0.000755           mixed     hierarchical post_alert_window        0.40      0.65          0.35            0.076923            0.307692                0.066667            0.057143            0.022908              0.017719           0.015561       -0.050931                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.65      0.90      0.583333  0.472222               0.031960                 0.038648           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.45      0.80      0.416667  0.335664               0.021206                 0.020079           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.55      0.70      0.527778  0.487302               0.020654                 0.019404           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.679201         0.170477     0.150322              tier0           mixed
  BRANCH     0.753956         0.098454     0.147591              tier0           mixed
   CACHE     0.535027         0.359644     0.105329              tier0           mixed
   MEMBW     0.777969         0.100750     0.121281              tier0           mixed
     TLB     0.690221         0.154440     0.155339              tier0           mixed
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC               memory_io       0.270889         0.385315             0.107479                 0.201302                 0.035016           mixed
  BRANCH               memory_io       0.249311         0.452251             0.055550                 0.192765                 0.050124           mixed
   CACHE                 compute       0.475884         0.261443             0.072335                 0.134589                 0.055750           mixed
   MEMBW               memory_io       0.245061         0.465713             0.059453                 0.164901                 0.064871           mixed
     TLB               memory_io       0.303179         0.390367             0.085973                 0.187662                 0.032820           mixed
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
            tier0                    0.0                             0.0                           0.0                  0.3                     64.5                 622.5                0.20                0.20                0.25           mixed
      tier0_tier1                    0.0                             0.0                           0.0                  0.5                     65.0                 850.0                0.30                0.30                0.40           mixed
tier0_tier1_tier2                    0.0                             0.0                           0.0                  0.5                     51.5                 849.3                0.35                0.35                0.40           mixed
```

## Files
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B45_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B45_a0.05_k3/config_runtime_summary.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B45_a0.05_k3/run_context.json`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B45_a0.05_k3/case_inventory.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B45_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B45_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B45_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B45_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B45_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B45_a0.05_k3/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B45_a0.05_k3/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B45_a0.05_k3/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B45_a0.05_k3/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B45_a0.05_k3/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B45_a0.05_k3/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B45_a0.05_k3/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B45_a0.05_k3/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B45_a0.05_k3/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B45_a0.05_k3/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B45_a0.05_k3/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B45_a0.05_k3/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B45_a0.05_k3/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B45_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B45_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B45_a0.05_k3/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B45_a0.05_k3/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B45_a0.05_k3/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B45_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B45_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B45_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B45_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B45_a0.05_k3/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B45_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B45_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B45_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B45_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B45_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B45_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B45_a0.05_k3/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B45_a0.05_k3/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B45_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B45_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/Documents/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning/runs/g0.1_B45_a0.05_k3/figures/fig_detection_latency.png`
