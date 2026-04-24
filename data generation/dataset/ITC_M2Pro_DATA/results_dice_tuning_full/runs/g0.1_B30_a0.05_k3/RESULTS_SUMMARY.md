# DICE Full Retrain Results

## Setup
- Feature profile: full ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_full_5hz.csv', 'tier2': 'tier2_full_5hz.csv'})
- Protocol: global, benign-only fit/calibration, block_B=30, alpha=0.05, persist_k=3, gain=0.1
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
           full             tier0       24          46          2.965271   0.8125 0.940232         1.0        1.0           0.25            0.3              0.014529              0.030374                      0.0                 0.015789
           full       tier0_tier1       24          64          3.372400   0.8750 0.972598         1.0        1.0           0.00            0.7              0.022139              0.063320                      0.0                 0.029593
           full tier0_tier1_tier2       24          75          3.894256   0.9875 0.997619         1.0        1.0           0.00            1.0              0.002786              0.007633                      0.0                 0.004790
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc  pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
           full   ATOMIC   0.9375    0.95         1.0        1.0          0.002786          0.007135                  0.0             0.004637       2.560458      0.004349       4637.689794         0.004637
           full   BRANCH   1.0000    1.00         1.0        1.0          0.002786          0.008988                  0.0             0.006496       3.225269      0.006202       6497.194993         0.006496
           full    CACHE   1.0000    1.00         1.0        1.0          0.002786          0.009123                  0.0             0.006078       3.273666      0.006337       6078.977458         0.006078
           full    MEMBW   1.0000    1.00         1.0        1.0          0.002786          0.008821                  0.0             0.005247       3.165440      0.006035       5247.521684         0.005247
           full      TLB   1.0000    1.00         1.0        1.0          0.002786          0.006786                  0.0             0.004566       2.435227      0.004000       4566.549228         0.004566
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
            tier0       20      0.35      0.55          0.35  0.313333               0.022311                 0.016958            full
      tier0_tier1       20      0.20      0.45          0.20  0.230000               0.015878                 0.016233            full
tier0_tier1_tier2       20      0.30      0.50          0.30  0.251429               0.017650                 0.015797            full
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.25      0.50          0.25  0.220000               0.018114                 0.017426            full
      tier0_tier1       20      0.15      0.35          0.15  0.138889               0.096777                 0.039296            full
tier0_tier1_tier2       20      0.10      0.25          0.10  0.076364               0.030279                 0.024017            full
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.20      0.55          0.20  0.190649               0.020115                 0.016832            full
      tier0_tier1       20      0.35      0.70          0.35  0.307648               0.019876                 0.015739            full
tier0_tier1_tier2       20      0.35      0.55          0.35  0.337013               0.014911                 0.011075            full
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.55      0.90      0.527778  0.434343               0.032192                 0.040380            full
      tier0_tier1       20      0.50      0.90      0.388889  0.412536               0.018693                 0.012305            full
tier0_tier1_tier2       20      0.45      0.95      0.472222  0.503663               0.016276                 0.012699            full
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20       0.4      0.55        0.45           0.4  0.373333      0.35          0.65            0.571429            0.571429                0.400000            0.293333              -0.001862                 0.002342            0.016131              0.014984           0.011970        0.106540            full
      tier0_tier1       20       0.3      0.55        0.50           0.3  0.326190      0.75          0.25            0.266667            0.533333                0.283333            0.323810               0.010217                 0.015371            0.024492              0.023873           0.015249        0.021765            full
tier0_tier1_tier2       20       0.2      0.35        0.35           0.2  0.157143      0.65          0.35            0.307692            0.461538                0.300000            0.272727               0.012661                 0.018403            0.020099              0.019158           0.012730        0.035539            full
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.35      0.60        0.45          0.35  0.355873      0.50          0.50            0.300000            0.500000                0.200000            0.217143              -0.010884                 0.010696            0.016131              0.014984           0.011970       -0.043254            full
      tier0_tier1       20      0.20      0.40        0.50          0.20  0.170000      0.30          0.70            0.166667            0.333333                0.200000            0.133333               0.019750                 0.033542            0.024492              0.023873           0.015249        0.415830            full
tier0_tier1_tier2       20      0.20      0.35        0.35          0.20  0.161538      0.55          0.45            0.090909            0.181818                0.066667            0.050000              -0.006748                -0.001926            0.020099              0.019158           0.012730       -0.033033            full
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0  conf_0.00              0.000000      14      0.70          0.30            0.428571            0.500000                0.416667            0.366667            full
            tier0  conf_0.05              0.050000       9      0.45          0.55            0.555556            0.555556                0.437500            0.310000            full
            tier0  conf_0.10              0.100000       5      0.25          0.75            0.600000            0.600000                0.500000            0.293333            full
            tier0    trained              0.106540       5      0.25          0.75            0.600000            0.600000                0.500000            0.293333            full
            tier0  conf_0.15              0.150000       4      0.20          0.80            0.750000            0.750000                0.666667            0.360000            full
            tier0  conf_0.20              0.200000       2      0.10          0.90            1.000000            1.000000                1.000000            0.200000            full
            tier0  conf_0.25              0.250000       2      0.10          0.90            1.000000            1.000000                1.000000            0.200000            full
      tier0_tier1  conf_0.00              0.000000      17      0.85          0.15            0.294118            0.529412                0.316667            0.347912            full
      tier0_tier1    trained              0.021765      14      0.70          0.30            0.285714            0.571429                0.266667            0.296364            full
      tier0_tier1  conf_0.05              0.050000      11      0.55          0.45            0.272727            0.545455                0.233333            0.204444            full
      tier0_tier1  conf_0.10              0.100000       5      0.25          0.75            0.000000            0.600000                0.000000            0.000000            full
      tier0_tier1  conf_0.15              0.150000       2      0.10          0.90            0.000000            1.000000                0.000000            0.000000            full
      tier0_tier1  conf_0.20              0.200000       2      0.10          0.90            0.000000            1.000000                0.000000            0.000000            full
      tier0_tier1  conf_0.25              0.250000       1      0.05          0.95            0.000000            1.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.00              0.000000      16      0.80          0.20            0.250000            0.375000                0.233333            0.226667            full
tier0_tier1_tier2    trained              0.035539      13      0.65          0.35            0.230769            0.384615                0.200000            0.200000            full
tier0_tier1_tier2  conf_0.05              0.050000      13      0.65          0.35            0.230769            0.384615                0.200000            0.200000            full
tier0_tier1_tier2  conf_0.10              0.100000      10      0.50          0.50            0.200000            0.300000                0.133333            0.080000            full
tier0_tier1_tier2  conf_0.15              0.150000       7      0.35          0.65            0.142857            0.285714                0.250000            0.066667            full
tier0_tier1_tier2  conf_0.20              0.200000       3      0.15          0.85            0.000000            0.333333                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.25              0.250000       2      0.10          0.90            0.000000            0.500000                0.000000            0.000000            full
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained             -0.043254      13      0.65          0.35            0.307692            0.538462                0.216667            0.221429            full
            tier0  conf_0.00              0.000000      13      0.65          0.35            0.307692            0.538462                0.216667            0.221429            full
            tier0  conf_0.05              0.050000      10      0.50          0.50            0.200000            0.500000                0.166667            0.190476            full
            tier0  conf_0.10              0.100000       6      0.30          0.70            0.333333            0.666667                0.277778            0.213333            full
            tier0  conf_0.15              0.150000       2      0.10          0.90            0.500000            1.000000                0.500000            0.200000            full
            tier0  conf_0.20              0.200000       2      0.10          0.90            0.500000            1.000000                0.500000            0.200000            full
            tier0  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN            full
      tier0_tier1  conf_0.00              0.000000      16      0.80          0.20            0.187500            0.437500                0.183333            0.180952            full
      tier0_tier1  conf_0.05              0.050000      14      0.70          0.30            0.142857            0.428571                0.166667            0.160000            full
      tier0_tier1  conf_0.10              0.100000      11      0.55          0.45            0.090909            0.363636                0.100000            0.133333            full
      tier0_tier1  conf_0.15              0.150000       7      0.35          0.65            0.000000            0.285714                0.000000            0.000000            full
      tier0_tier1  conf_0.20              0.200000       6      0.30          0.70            0.000000            0.166667                0.000000            0.000000            full
      tier0_tier1  conf_0.25              0.250000       6      0.30          0.70            0.000000            0.166667                0.000000            0.000000            full
      tier0_tier1    trained              0.415830       3      0.15          0.85            0.000000            0.333333                0.000000            0.000000            full
tier0_tier1_tier2    trained             -0.033033      14      0.70          0.30            0.142857            0.214286                0.133333            0.130000            full
tier0_tier1_tier2  conf_0.00              0.000000      10      0.50          0.50            0.000000            0.100000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.05              0.050000       8      0.40          0.60            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.10              0.100000       6      0.30          0.70            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.15              0.150000       4      0.20          0.80            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.20              0.200000       4      0.20          0.80            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.25              0.250000       3      0.15          0.85            0.000000            0.000000                0.000000            0.000000            full
```

## Diagnosis Mode Comparison
- Whole-run and post-alert-window diagnosis are exported together so the diagnosis mode can be evaluated directly.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile diagnosis_target    diagnosis_mode  family_acc  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau                       status  min_class_count  min_group_count    group_key  include_workload
            tier0       20      0.35      0.55      0.350000  0.313333               0.022311                 0.016958            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.20      0.45      0.200000  0.230000               0.015878                 0.016233            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.30      0.50      0.300000  0.251429               0.017650                 0.015797            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.25      0.50      0.250000  0.220000               0.018114                 0.017426            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.15      0.35      0.150000  0.138889               0.096777                 0.039296            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.10      0.25      0.100000  0.076364               0.030279                 0.024017            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.40      0.55      0.400000  0.373333              -0.001862                 0.002342            full     hierarchical         whole_run        0.45      0.35          0.65            0.571429            0.571429                0.400000            0.293333            0.016131              0.014984           0.011970        0.106540                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.30      0.55      0.300000  0.326190               0.010217                 0.015371            full     hierarchical         whole_run        0.50      0.75          0.25            0.266667            0.533333                0.283333            0.323810            0.024492              0.023873           0.015249        0.021765                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.20      0.35      0.200000  0.157143               0.012661                 0.018403            full     hierarchical         whole_run        0.35      0.65          0.35            0.307692            0.461538                0.300000            0.272727            0.020099              0.019158           0.012730        0.035539                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.35      0.60      0.350000  0.355873              -0.010884                 0.010696            full     hierarchical post_alert_window        0.45      0.50          0.50            0.300000            0.500000                0.200000            0.217143            0.016131              0.014984           0.011970       -0.043254                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.20      0.40      0.200000  0.170000               0.019750                 0.033542            full     hierarchical post_alert_window        0.50      0.30          0.70            0.166667            0.333333                0.200000            0.133333            0.024492              0.023873           0.015249        0.415830                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.20      0.35      0.200000  0.161538              -0.006748                -0.001926            full     hierarchical post_alert_window        0.35      0.55          0.45            0.090909            0.181818                0.066667            0.050000            0.020099              0.019158           0.012730       -0.033033                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.55      0.90      0.527778  0.434343               0.032192                 0.040380            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.50      0.90      0.388889  0.412536               0.018693                 0.012305            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.45      0.95      0.472222  0.503663               0.016276                 0.012699            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.530997         0.250122     0.218882              tier0            full
  BRANCH     0.572157         0.216128     0.211716              tier0            full
   CACHE     0.420278         0.186352     0.393370              tier0            full
   MEMBW     0.582719         0.221562     0.195720              tier0            full
     TLB     0.503145         0.264060     0.232795              tier0            full
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC                 compute       0.397928         0.266949             0.114311                 0.118815                 0.101997            full
  BRANCH                 compute       0.353424         0.330328             0.085168                 0.160505                 0.070575            full
   CACHE                 compute       0.543851         0.237380             0.070126                 0.086251                 0.062392            full
   MEMBW                 compute       0.375997         0.299744             0.095194                 0.122145                 0.106920            full
     TLB                 compute       0.408521         0.271575             0.112535                 0.122319                 0.085049            full
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
            tier0                   0.25                         1.85567                       3.71134                  0.3                     54.0                 599.0                0.20                0.20                0.25            full
      tier0_tier1                   0.00                         0.00000                       0.00000                  0.7                     58.5                 897.4                0.50                0.50                0.55            full
tier0_tier1_tier2                   0.00                         0.00000                       0.00000                  1.0                     32.0                 778.7                0.75                0.75                0.85            full
```

## Files
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B30_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B30_a0.05_k3/config_runtime_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B30_a0.05_k3/run_context.json`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B30_a0.05_k3/case_inventory.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B30_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B30_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B30_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B30_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B30_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B30_a0.05_k3/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B30_a0.05_k3/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B30_a0.05_k3/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B30_a0.05_k3/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B30_a0.05_k3/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B30_a0.05_k3/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B30_a0.05_k3/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B30_a0.05_k3/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B30_a0.05_k3/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B30_a0.05_k3/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B30_a0.05_k3/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B30_a0.05_k3/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B30_a0.05_k3/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B30_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B30_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B30_a0.05_k3/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B30_a0.05_k3/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B30_a0.05_k3/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B30_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B30_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B30_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B30_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B30_a0.05_k3/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B30_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B30_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B30_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B30_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B30_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B30_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B30_a0.05_k3/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B30_a0.05_k3/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B30_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B30_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.1_B30_a0.05_k3/figures/fig_detection_latency.png`
