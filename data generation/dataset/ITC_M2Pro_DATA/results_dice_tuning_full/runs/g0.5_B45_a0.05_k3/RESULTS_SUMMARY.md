# DICE Full Retrain Results

## Setup
- Feature profile: full ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_full_5hz.csv', 'tier2': 'tier2_full_5hz.csv'})
- Protocol: global, benign-only fit/calibration, block_B=45, alpha=0.05, persist_k=3, gain=0.5
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
           full             tier0       24          46          2.374584   0.7875 0.921899         1.0        1.0            0.0           0.30              0.004442              0.009197                      0.0                 0.005188
           full       tier0_tier1       24          64          3.172825   0.8125 0.949484         1.0        1.0            0.0           0.55              0.006666              0.019771                      0.0                 0.008881
           full tier0_tier1_tier2       24          75          3.753153   0.9375 0.986769         1.0        1.0            0.0           0.95              0.002511              0.007052                      0.0                 0.003788
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc  pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
           full   ATOMIC   0.8750  0.8875         1.0        1.0          0.002511          0.006188                  0.0             0.002639       2.463364      0.003676       2639.720406         0.002639
           full   BRANCH   0.9375  0.9500         1.0        1.0          0.002511          0.008661                  0.0             0.005960       3.447704      0.006149       5961.180736         0.005960
           full    CACHE   0.9375  0.9500         1.0        1.0          0.002511          0.008246                  0.0             0.005139       3.282569      0.005734       5140.056644         0.005139
           full    MEMBW   1.0000  1.0000         1.0        1.0          0.002511          0.007348                  0.0             0.004322       2.925268      0.004837       4322.901768         0.004322
           full      TLB   0.9375  0.9500         1.0        1.0          0.002511          0.006520                  0.0             0.004083       2.595506      0.004008       4084.064395         0.004083
```

## Paper-style Aggregates (Final Config)
- Base score mean stressor AUC-PR (all five): **0.9475**
- Base score mean stressor ROC-AUC (all five): **0.9375**
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
            tier0       20      0.40      0.55          0.40  0.317980               0.022186                 0.018011            full
      tier0_tier1       20      0.25      0.35          0.25  0.170629               0.017733                 0.016081            full
tier0_tier1_tier2       20      0.30      0.40          0.30  0.200000               0.023544                 0.023995            full
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.30      0.55          0.30  0.281457               0.014851                 0.012720            full
      tier0_tier1       20      0.15      0.35          0.15  0.137143               0.067778                 0.038835            full
tier0_tier1_tier2       20      0.20      0.25          0.20  0.186364               0.012332                 0.008655            full
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.35      0.65          0.35  0.358730               0.011821                 0.010590            full
      tier0_tier1       20      0.30      0.50          0.30  0.232727               0.018973                 0.017167            full
tier0_tier1_tier2       20      0.40      0.60          0.40  0.369091               0.015692                 0.012084            full
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.55      0.75      0.472222  0.398551               0.029049                 0.031710            full
      tier0_tier1       20      0.50      0.70      0.388889  0.342995               0.028634                 0.030481            full
tier0_tier1_tier2       20      0.45      0.95      0.583333  0.458333               0.016767                 0.014547            full
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.25      0.55        0.30          0.25  0.208889      0.25          0.75                 0.6                 0.8                0.500000            0.333333               0.012309                 0.010060            0.009308              0.006824           0.012766        0.181815            full
      tier0_tier1       20      0.20      0.45        0.60          0.20  0.182395      0.50          0.50                 0.3                 0.4                0.366667            0.346667              -0.008994                 0.002474            0.018623              0.017827           0.008730       -0.000172            full
tier0_tier1_tier2       20      0.25      0.40        0.45          0.25  0.175000      0.50          0.50                 0.2                 0.2                0.300000            0.166667               0.009226                 0.016724            0.020302              0.016369           0.008666        0.107224            full
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20       0.2      0.45        0.30           0.2  0.172222      0.80          0.20            0.187500            0.375000                0.166667            0.151587               0.003981                  0.00933            0.009308              0.006824           0.012766       -0.054026            full
      tier0_tier1       20       0.2      0.35        0.60           0.2  0.150427      0.50          0.50            0.100000            0.400000                0.100000            0.066667              -0.015803                  0.00888            0.018623              0.017827           0.008730        0.037754            full
tier0_tier1_tier2       20       0.3      0.45        0.45           0.3  0.283030      0.75          0.25            0.266667            0.466667                0.300000            0.274444              -0.003864                 -0.00497            0.020302              0.016369           0.008666       -0.182277            full
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0  conf_0.00              0.000000      15      0.75          0.25            0.333333            0.533333                0.312500            0.208889            full
            tier0  conf_0.05              0.050000      11      0.55          0.45            0.454545            0.636364                0.354167            0.234286            full
            tier0  conf_0.10              0.100000       8      0.40          0.60            0.500000            0.625000                0.312500            0.220000            full
            tier0  conf_0.15              0.150000       6      0.30          0.70            0.500000            0.666667                0.250000            0.133333            full
            tier0    trained              0.181815       6      0.30          0.70            0.500000            0.666667                0.250000            0.133333            full
            tier0  conf_0.20              0.200000       5      0.25          0.75            0.600000            0.600000                0.375000            0.150000            full
            tier0  conf_0.25              0.250000       4      0.20          0.80            0.750000            0.750000                0.500000            0.171429            full
      tier0_tier1    trained             -0.000172      11      0.55          0.45            0.181818            0.363636                0.166667            0.146667            full
      tier0_tier1  conf_0.00              0.000000      11      0.55          0.45            0.181818            0.363636                0.166667            0.146667            full
      tier0_tier1  conf_0.05              0.050000       7      0.35          0.65            0.285714            0.285714                0.277778            0.160000            full
      tier0_tier1  conf_0.10              0.100000       3      0.15          0.85            0.000000            0.000000                0.000000            0.000000            full
      tier0_tier1  conf_0.15              0.150000       3      0.15          0.85            0.000000            0.000000                0.000000            0.000000            full
      tier0_tier1  conf_0.20              0.200000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000            full
      tier0_tier1  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN            full
tier0_tier1_tier2  conf_0.00              0.000000      16      0.80          0.20            0.250000            0.375000                0.250000            0.172308            full
tier0_tier1_tier2  conf_0.05              0.050000      11      0.55          0.45            0.272727            0.454545                0.200000            0.109091            full
tier0_tier1_tier2  conf_0.10              0.100000      10      0.50          0.50            0.300000            0.500000                0.200000            0.109091            full
tier0_tier1_tier2    trained              0.107224      10      0.50          0.50            0.300000            0.500000                0.200000            0.109091            full
tier0_tier1_tier2  conf_0.15              0.150000       7      0.35          0.65            0.142857            0.285714                0.200000            0.066667            full
tier0_tier1_tier2  conf_0.20              0.200000       3      0.15          0.85            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.25              0.250000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000            full
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained             -0.054026      16      0.80          0.20            0.187500            0.375000                0.166667            0.151587            full
            tier0  conf_0.00              0.000000      16      0.80          0.20            0.187500            0.375000                0.166667            0.151587            full
            tier0  conf_0.05              0.050000      11      0.55          0.45            0.181818            0.363636                0.166667            0.146667            full
            tier0  conf_0.10              0.100000       7      0.35          0.65            0.285714            0.428571                0.375000            0.266667            full
            tier0  conf_0.15              0.150000       5      0.25          0.75            0.400000            0.600000                0.666667            0.333333            full
            tier0  conf_0.20              0.200000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000            full
            tier0  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN            full
      tier0_tier1  conf_0.00              0.000000      11      0.55          0.45            0.181818            0.363636                0.133333            0.100000            full
      tier0_tier1    trained              0.037754      10      0.50          0.50            0.200000            0.400000                0.166667            0.114286            full
      tier0_tier1  conf_0.05              0.050000      10      0.50          0.50            0.200000            0.400000                0.166667            0.114286            full
      tier0_tier1  conf_0.10              0.100000       8      0.40          0.60            0.250000            0.500000                0.250000            0.133333            full
      tier0_tier1  conf_0.15              0.150000       5      0.25          0.75            0.200000            0.400000                0.250000            0.100000            full
      tier0_tier1  conf_0.20              0.200000       4      0.20          0.80            0.000000            0.250000                0.000000            0.000000            full
      tier0_tier1  conf_0.25              0.250000       3      0.15          0.85            0.000000            0.333333                0.000000            0.000000            full
tier0_tier1_tier2    trained             -0.182277      20      1.00          0.00            0.300000            0.450000                0.300000            0.283030            full
tier0_tier1_tier2  conf_0.00              0.000000      10      0.50          0.50            0.300000            0.400000                0.400000            0.316667            full
tier0_tier1_tier2  conf_0.05              0.050000       6      0.30          0.70            0.333333            0.333333                0.375000            0.333333            full
tier0_tier1_tier2  conf_0.10              0.100000       3      0.15          0.85            0.333333            0.333333                0.333333            0.200000            full
tier0_tier1_tier2  conf_0.15              0.150000       3      0.15          0.85            0.333333            0.333333                0.333333            0.200000            full
tier0_tier1_tier2  conf_0.20              0.200000       3      0.15          0.85            0.333333            0.333333                0.333333            0.200000            full
tier0_tier1_tier2  conf_0.25              0.250000       3      0.15          0.85            0.333333            0.333333                0.333333            0.200000            full
```

## Diagnosis Mode Comparison
- Whole-run and post-alert-window diagnosis are exported together so the diagnosis mode can be evaluated directly.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile diagnosis_target    diagnosis_mode  family_acc  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau                       status  min_class_count  min_group_count    group_key  include_workload
            tier0       20      0.40      0.55      0.400000  0.317980               0.022186                 0.018011            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.25      0.35      0.250000  0.170629               0.017733                 0.016081            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.30      0.40      0.300000  0.200000               0.023544                 0.023995            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.30      0.55      0.300000  0.281457               0.014851                 0.012720            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.15      0.35      0.150000  0.137143               0.067778                 0.038835            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.20      0.25      0.200000  0.186364               0.012332                 0.008655            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.25      0.55      0.250000  0.208889               0.012309                 0.010060            full     hierarchical         whole_run        0.30      0.25          0.75            0.600000            0.800000                0.500000            0.333333            0.009308              0.006824           0.012766        0.181815                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.20      0.45      0.200000  0.182395              -0.008994                 0.002474            full     hierarchical         whole_run        0.60      0.50          0.50            0.300000            0.400000                0.366667            0.346667            0.018623              0.017827           0.008730       -0.000172                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.25      0.40      0.250000  0.175000               0.009226                 0.016724            full     hierarchical         whole_run        0.45      0.50          0.50            0.200000            0.200000                0.300000            0.166667            0.020302              0.016369           0.008666        0.107224                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.20      0.45      0.200000  0.172222               0.003981                 0.009330            full     hierarchical post_alert_window        0.30      0.80          0.20            0.187500            0.375000                0.166667            0.151587            0.009308              0.006824           0.012766       -0.054026                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.20      0.35      0.200000  0.150427              -0.015803                 0.008880            full     hierarchical post_alert_window        0.60      0.50          0.50            0.100000            0.400000                0.100000            0.066667            0.018623              0.017827           0.008730        0.037754                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.30      0.45      0.300000  0.283030              -0.003864                -0.004970            full     hierarchical post_alert_window        0.45      0.75          0.25            0.266667            0.466667                0.300000            0.274444            0.020302              0.016369           0.008666       -0.182277                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.55      0.75      0.472222  0.398551               0.029049                 0.031710            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.50      0.70      0.388889  0.342995               0.028634                 0.030481            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.45      0.95      0.583333  0.458333               0.016767                 0.014547            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.616133         0.266024     0.117843              tier0            full
  BRANCH     0.649339         0.212645     0.138016              tier0            full
   CACHE     0.531537         0.205467     0.262996              tier0            full
   MEMBW     0.655918         0.241048     0.103034              tier0            full
     TLB     0.597258         0.272582     0.130160              tier0            full
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC                 compute       0.334332         0.324894             0.101081                 0.131849                 0.107844            full
  BRANCH               memory_io       0.301281         0.380906             0.074074                 0.163127                 0.080611            full
   CACHE                 compute       0.446972         0.314525             0.067222                 0.101320                 0.069961            full
   MEMBW               memory_io       0.309175         0.364709             0.097816                 0.128160                 0.100141            full
     TLB                 compute       0.330552         0.341331             0.106427                 0.133148                 0.088542            full
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
            tier0                    0.0                             0.0                      1.884817                 0.30                     62.5                 662.5                0.20                0.20                0.25            full
      tier0_tier1                    0.0                             0.0                      0.000000                 0.55                     47.0                 821.0                0.40                0.40                0.40            full
tier0_tier1_tier2                    0.0                             0.0                      0.000000                 0.95                     47.0                 783.8                0.65                0.65                0.70            full
```

## Files
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B45_a0.05_k3/overall_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B45_a0.05_k3/config_runtime_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B45_a0.05_k3/run_context.json`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B45_a0.05_k3/case_inventory.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B45_a0.05_k3/case_block_traces.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B45_a0.05_k3/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B45_a0.05_k3/sequential_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B45_a0.05_k3/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B45_a0.05_k3/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B45_a0.05_k3/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B45_a0.05_k3/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B45_a0.05_k3/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B45_a0.05_k3/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B45_a0.05_k3/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B45_a0.05_k3/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B45_a0.05_k3/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B45_a0.05_k3/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B45_a0.05_k3/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B45_a0.05_k3/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B45_a0.05_k3/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B45_a0.05_k3/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B45_a0.05_k3/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B45_a0.05_k3/mechanism_group_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B45_a0.05_k3/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B45_a0.05_k3/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B45_a0.05_k3/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B45_a0.05_k3/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B45_a0.05_k3/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B45_a0.05_k3/overall_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B45_a0.05_k3/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B45_a0.05_k3/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B45_a0.05_k3/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B45_a0.05_k3/sequential_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B45_a0.05_k3/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B45_a0.05_k3/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B45_a0.05_k3/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B45_a0.05_k3/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B45_a0.05_k3/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B45_a0.05_k3/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B45_a0.05_k3/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B45_a0.05_k3/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B45_a0.05_k3/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_tuning_full/runs/g0.5_B45_a0.05_k3/figures/fig_detection_latency.png`
