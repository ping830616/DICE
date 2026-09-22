# Paper evidence and reproducibility notes

These notes describe the released study and the corrections to its analysis exports. They supersede conflicting numerical or methodological descriptions in the historical draft-writing packages. No new telemetry, crash experiments, or detector-training results were produced by this correction.

## Recorded detector settings

| Profile | Decision block (s) | Base significance level | Consecutive flagged blocks | Synchronization gain |
| --- | ---: | ---: | ---: | ---: |
| Mixed | 45 | 0.10 | 1 | 0.20 |
| Full | 90 | 0.05 | 2 | 0.35 |

The authoritative settings for saved detector outputs are in `results_dice_full/run_context.json` and `results_dice_full_full/run_context.json` under `data generation/dataset/ITC_M2Pro_DATA/`. Both use a fitting fraction of 0.6 and ridge penalty 0.001. Adjacent `notebook_invocation.json` files contain older invocation settings and have been retained as historical records. The settings reader now prefers the actual run context, and the Full significance level in the derived reliability CSV is corrected from 0.02 to 0.05.

The notebook invokes `tools/train_eval_dice_pipeline.py`. An obsolete embedded source snapshot was unused and has been removed. The default notebook workflow uses the recorded operating points. Enable tuning and selection explicitly to conduct a new parameter search; the resulting study must be reported as a new evaluation. Cleared notebook outputs must be regenerated before they can support updated figures or tables.

## Calibration and evaluation scope

The base detector is fitted on benign telemetry and uses the strict rule `p < alpha`. Global evaluation scores all 24 complete executions, including the four benign reference traces used for fitting and calibration. The global zero-alert observation therefore reuses reference data; it is not a measurement on independent benign executions. Overlapping decision blocks do not establish the exchangeability required for a conformal guarantee.

The global implementation also applies a phase guard to VIDEO_SW: a smoothed template and tolerance use its complete benign trace, and both the base and phase-excess p-values must pass. The guard is absent when VIDEO_SW is excluded from training. This behavior is part of the saved results, not an optional detail that can be removed while retaining the same claims.

Workload-holdout fitting and calibration use benign traces from the other workloads. Feature availability and constant-column filtering are computed across the released cases before those folds. Profile parameters and reported diagnosis variants were selected retrospectively on the evaluated dataset.

## Diagnosis metrics

The anomaly detector is fitted on benign telemetry. Stressor diagnosis separately uses labeled anomalous attribution prototypes, trained on other workloads for each held-out workload. The diagnosis summaries cover all 20 anomalous cases, including those without a persistent alert.

| Profile | Reported Top-2 variant | Top-2 | Confidence-gated variant | Accepted cases | Correct Top-2 among accepted |
| --- | --- | ---: | --- | ---: | ---: |
| Mixed | Whole-run feature prototypes | 15/20 | Hierarchical whole-run | 11/20 | 10/11 |
| Full | Hierarchical post-alert, with peak-window fallback | 9/20 | Hierarchical whole-run | 12/20 | 5/12 |

The confidence-gated results use a different variant from the headline Top-2 result. The values 0.888 and 0.828 are **mean evidence shares of the three highest-scoring mechanism categories**, not accuracy against known anomaly-category labels. The five categories are compute, memory/I/O, thermal/power, scheduler/runtime, and platform pressure. Historical CSV fields containing `top3_coverage` denote this evidence concentration; see the notebook's corrected display labels.

## Controlled crash pilots

The pilots terminate through scheduled user-space aborts. Precision, recall, and F1 from the original study describe benign-or-anomalous decisions; they do not measure crash prediction.

The historical timing medians 139.5 s (Mixed) and 90.0 s (Full) subtract an original study warning from a recorded crash in a separate, matched pilot. Corrected exports retain these values as `median_retrospective_offset_s` and exclude them from same-execution lead-time and crash-warning metrics. Remapped manifests retain their original pilot IDs and explicit timing provenance, including nominal cases with unchanged textual IDs.

The saved pilot feature bridge reports warnings at 62 s. The public PY_AI/CACHE `results_workload_crash_paper/mixed/early_warning_crash_alignment_display.csv` contains a direct `PY_AI__CACHE_ABORT` record with a 62 s persistent warning, `tier0:soft_interrupts` and `tier0:uptime_s` as its two leading features, and a 214.779384 s crash time. The old aggregate incorrectly substituted original-study frequency features when the primary warning-summary path was unavailable. The bridge now accepts exact abort-case records from direct pilot warning or alignment exports, records the chosen source, and never silently substitutes original-run evidence.

The two PY_STATS/ATOMIC crash times identify distinct recorded collection events. `results_itc_paper/comparison/early_warning_merged_crash_events.csv` records a `tier1_alt` run starting at 2026-04-01 02:36:35 UTC, with the crash at 02:39:49 UTC and relative time 194.496976 s. The pilot's `results_workload_crash_paper/mixed/early_warning_crash_alignment.csv` and `crash_events_repaired.csv` instead record a run starting at 04:55:08 UTC, with the crash at 04:58:24 UTC and relative time 196.682946 s. These UTC strings have lower precision than the relative timestamps. Keep each relative value tied to its collection event; do not replace one with the other to force agreement. The bridge reports source/timestamp conflicts explicitly.

The historical `peak_abs_z` statistic searches the entire recorded trace and can occur after the abort. The feature exporter now provides separate pre-crash peak fields. Neither set of feature associations establishes the cause of a scheduled termination.

## LLM checks and collection support

The LLM checker tests known tier/mechanism aliases and four selected cues. Zero unsupported-alias flags is not a general factuality assessment. Recorded batch time divided by output count is an amortized cost, not independently measured request latency.

The repository includes processed data and source for Tier-0, Tier-1, and Tier-2 collection/parsing. New Tier-2 collection requires a supported macOS/Xcode Instruments setup; analysis of released CSVs is portable. Crash-pilot payloads require Git LFS materialization as documented in the README.

## Validation scope

To refresh the corrected reliability and timing CSVs from already saved predictions and warning records, run `python scripts/refresh_saved_evidence_exports.py`. This does not fit a detector, collect data, or regenerate figures. Run the targeted checks with `python -m unittest discover -s tests -v` in the analysis environment.

Targeted tests cover operating-point provenance, crash-record matching, missing/conflicting evidence, separate-execution timing, and pre-crash feature bounds. They do not constitute a complete notebook reproduction. Re-execute the corrected notebook with the required payloads before replacing published figures or claiming new measured results.
