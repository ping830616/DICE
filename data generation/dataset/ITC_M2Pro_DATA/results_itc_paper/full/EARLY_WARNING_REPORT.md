# DICE Early-Warning Analysis

## What This Export Contains

- `anomaly_detection_metrics.csv`: ROC-AUC, PR-AUC, precision, recall, F1-score, and balanced accuracy for benign-or-anomalous decisions over complete executions.
- `early_warning_case_summary.csv`: first warning time for each case, derived from the first persistent abnormal window when available.
- `early_warning_crash_alignment.csv`: merged case-level warning and crash evidence table.
- `early_warning_metrics.csv`: early-warning precision, recall-before-crash, lead-time statistics, and false-alarm measures.
- `fig_early_warning_timeline.png`: warning and crash timing for each case.
- `fig_early_warning_lead_time_distribution.png`: lead-time distribution for cases where a warning preceded a crash.

## Metric Interpretation

- `ROC-AUC` and `PR-AUC` measure ranking quality before an alert threshold is fixed. Higher values mean the digital twin separates benign and anomalous runs more cleanly.
- `Precision`, `Recall`, and `F1-score` describe the chosen alert operating point. In a deployed system, high precision limits alarm fatigue, while high recall limits missed anomalies.
- Crash-warning metrics include only warning and outcome records from the same execution. Scheduled process aborts do not validate prediction of spontaneous hardware failure.
- `retrospective_offset_s` subtracts an original study warning time from a separate pilot crash time. It is excluded from `lead_time_s` and crash-warning accuracy metrics.
- `Median lead time` and `lead_time_ge_*` rates summarize observed intervals after a warning within the same execution.
- `False alarm rate per monitored hour` measures how often DICE would trigger on runs with an observed non-crash outcome. Lower values are better for long-lived monitoring deployments.

## Crash-Evidence Status

Crash manifest used: `data generation/dataset/ITC_M2Pro_DATA/results_itc_paper/comparison/early_warning_merged_crash_events.csv`

## Headline Monitoring Result

The selected Full Tier-0/1/2 operating point achieves ROC-AUC 0.9500, PR-AUC 0.9897, precision 1.0000, recall 0.9500, and F1-score 0.9744.

## Retrospective Timing Alignment

4 separate pilot crashes have a median offset of 90.0s from original study warnings. These are comparisons across separate executions, not measured warning-to-crash intervals.

## Case Preview

| case_id | workload | stressor | first_warning_s | crash_time_s | lead_time_s | warning_source |
| --- | --- | --- | --- | --- | --- | --- |
| BROWSER__ATOMIC | BROWSER | ATOMIC |  |  |  | no_detected_warning |
| BROWSER__BRANCH | BROWSER | BRANCH | 91.0 | 167.478639 |  | first_persistent_alert |
| BROWSER__CACHE | BROWSER | CACHE | 91.0 |  |  | first_persistent_alert |
| BROWSER__MEMBW | BROWSER | MEMBW | 91.0 |  |  | first_persistent_alert |
| BROWSER__TLB | BROWSER | TLB | 91.0 |  |  | first_persistent_alert |
| BROWSER__NOMINAL | BROWSER | NOMINAL |  |  |  | no_detected_warning |
| VIDEO_SW__ATOMIC | VIDEO_SW | ATOMIC | 91.0 |  |  | first_persistent_alert |
| VIDEO_SW__BRANCH | VIDEO_SW | BRANCH | 815.0 |  |  | first_persistent_alert |
