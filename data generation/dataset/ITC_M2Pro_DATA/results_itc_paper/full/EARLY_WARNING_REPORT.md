# DICE Early-Warning Analysis

## What This Export Contains

- `anomaly_detection_metrics.csv`: run-level ROC-AUC, PR-AUC, precision, recall, F1-score, and balanced accuracy for the selected DICE operating point.
- `early_warning_case_summary.csv`: first warning time for each case, derived from the first persistent abnormal window when available.
- `early_warning_crash_alignment.csv`: merged case-level warning and crash evidence table.
- `early_warning_metrics.csv`: early-warning precision, recall-before-crash, lead-time statistics, and false-alarm measures.
- `fig_early_warning_timeline.png`: warning and crash timing for each case.
- `fig_early_warning_lead_time_distribution.png`: lead-time distribution for cases where a warning preceded a crash.

## Metric Interpretation

- `ROC-AUC` and `PR-AUC` measure ranking quality before an alert threshold is fixed. Higher values mean the digital twin separates benign and anomalous runs more cleanly.
- `Precision`, `Recall`, and `F1-score` describe the chosen alert operating point. In a deployed system, high precision limits alarm fatigue, while high recall limits missed anomalies.
- `Warning recall before crash` measures how often the first anomaly arrives before the first observed crash. This is the core early-warning metric for predictive maintenance.
- `Median lead time` and `lead_time_ge_*` rates measure how much operator response time DICE provides after the first warning. Larger values are better.
- `False alarm rate per monitored hour` measures how often DICE would trigger on runs with an observed non-crash outcome. Lower values are better for long-lived monitoring deployments.

## Crash-Evidence Status

No crash manifest was supplied for this export, so crash-specific precision, recall, and lead-time claims remain unavailable.
The warning-time tables and plots are still useful because they define the anomaly timestamps that will be paired with crash evidence in future collections.

## Headline Monitoring Result

The selected Full Tier-0/1/2 operating point achieves ROC-AUC 0.9625, PR-AUC 0.9925, precision 1.0000, recall 0.9500, and F1-score 0.9744.

## Case Preview

| case_id | workload | stressor | first_warning_s | crash_time_s | lead_time_s | warning_source |
| --- | --- | --- | --- | --- | --- | --- |
| BROWSER__ATOMIC | BROWSER | ATOMIC |  |  |  | no_detected_warning |
| BROWSER__BRANCH | BROWSER | BRANCH | 60.0 |  |  | first_persistent_alert |
| BROWSER__CACHE | BROWSER | CACHE | 60.0 |  |  | first_persistent_alert |
| BROWSER__MEMBW | BROWSER | MEMBW | 60.0 |  |  | first_persistent_alert |
| BROWSER__TLB | BROWSER | TLB | 60.0 |  |  | first_persistent_alert |
| BROWSER__NOMINAL | BROWSER | NOMINAL |  |  |  | no_detected_warning |
| VIDEO_SW__ATOMIC | VIDEO_SW | ATOMIC | 60.0 |  |  | first_persistent_alert |
| VIDEO_SW__BRANCH | VIDEO_SW | BRANCH | 815.0 |  |  | first_persistent_alert |
