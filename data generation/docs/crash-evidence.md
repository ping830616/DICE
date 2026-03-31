# Crash Evidence and Early-Warning Recollection

The released `ITC_M2Pro_DATA` snapshot does not include a crash manifest. As a result, the published DICE baseline can report first-warning times, but it cannot yet make a rigorous claim about warning-to-crash lead time.

This repo now supports a reproducible crash-evidence path for future recollection.

If you need a safe way to generate **real user-space crash artifacts** on a daily laptop, use the dedicated harness described in [controlled-crash-harness.md](controlled-crash-harness.md). That path is terminal-first and avoids intentionally provoking a kernel panic or full-machine freeze.

If you want the same crash-aware workflow extended across the original four workloads and five anomaly families, use [workload-matched-crash-matrix.md](workload-matched-crash-matrix.md).

The crash-harness collector also writes `case_inventory.csv` and `crash_harness_collection_config.json` so later analysis can recover the intended benign/anomalous labels and collection schedule directly from the dataset root.

## What Gets Captured

When `generate_dataset.py` or `run_itc_two_phase.py` is launched with `--capture_crash_evidence`, DICE writes:

- `crash_evidence/crash_events.csv`: one row per case with the observed crash outcome
- `crash_evidence/<case_id>/diagnostic_reports/`: copied new or modified macOS diagnostic reports
- `crash_evidence/<case_id>/system_logs/crash_window.jsonl`: filtered `log show` output for the run window
- `crash_evidence/<case_id>/screenshots/`: optional post-run screenshots when `--capture_crash_screenshot` is enabled
- `crash_evidence/<case_id>/crash_capture_summary.json`: per-case summary of the capture session

The manifest is designed so the early-warning analysis can evaluate both:

- crash runs, where `crash_detected = 1`
- observed non-crash runs, where `crash_detected = 0`

That second category is important because it lets DICE estimate warning precision and false alarms, not only recall.

## Recommended Collection Command

```bash
cd DICE/"data generation"
python generate_dataset.py \
  --phase recommended \
  --duration_s 1000 \
  --out_dir ./data \
  --tier1_alt_bin macmon \
  --tier2_template "Time Profiler" \
  --capture_crash_evidence \
  --crash_log_grace_s 60
```

If you want a screenshot after any detected crash evidence:

```bash
python generate_dataset.py \
  --phase recommended \
  --duration_s 1000 \
  --out_dir ./data \
  --capture_crash_evidence \
  --capture_crash_screenshot
```

## Manifest Columns

The collector writes these paper-facing fields:

- `case_id`
- `workload`
- `stressor`
- `phase`
- `crash_outcome_observed`
- `crash_detected`
- `run_start_utc`
- `run_end_utc`
- `monitor_duration_s`
- `crash_time_utc`
- `crash_time_s`
- `crash_source`
- `crash_kind`
- `diagnostic_report_path`
- `system_log_path`
- `screenshot_path`
- `evidence_note`

`crash_time_s` is measured from the start of the case and is the preferred field for the early-warning analysis.

## Running the Early-Warning Analysis

After DICE has produced `case_predictions.csv`, `case_block_traces.csv`, and `crash_events.csv`, run:

```bash
cd DICE
python tools/early_warning_analysis.py \
  --result_dir "data generation/dataset/ITC_M2Pro_DATA/results_dice_full" \
  --out_dir "data generation/dataset/ITC_M2Pro_DATA/results_itc_paper/mixed" \
  --feature_profile mixed \
  --crash_manifest "data generation/dataset/ITC_M2Pro_DATA/crash_evidence/crash_events.csv"
```

The same command works for the full profile by swapping `results_dice_full_full` and `results_itc_paper/full`.

## Generating Crash Evidence Cards

After `early_warning_crash_alignment.csv` is available, you can generate paper-ready PNG and Markdown cards:

```bash
cd DICE
python tools/generate_crash_evidence_cards.py \
  --alignment_csv "data generation/dataset/ITC_M2Pro_DATA/results_itc_paper/mixed/early_warning_crash_alignment.csv" \
  --out_dir "data generation/dataset/ITC_M2Pro_DATA/results_itc_paper/mixed/crash_evidence_cards" \
  --title "DICE Crash Evidence Gallery (Mixed Profile)"
```

This writes:

- `crash_evidence_cards.csv`: index of generated cards and key timing fields
- `CRASH_EVIDENCE_GALLERY.md`: gallery page for the selected cases
- `figures/<case_id>.png`: paper-ready visual card
- `cards/<case_id>.md`: per-case Markdown card with log and report excerpts

If the alignment table was produced without a crash manifest, the generator still renders warning-only template cards so you can validate the layout before recollection.

If you prefer the notebook path after collection, open `dice_results_analysis.ipynb` and run `8F. Controlled Crash-Harness Analysis` for the safe `CRASH_APP` dataset or `8G. Workload-Matched Crash Matrix` for the four-workload crash matrix.

## Interpretation

The early-warning analysis uses the first persistent abnormal window as the warning timestamp when available, and otherwise falls back to the first abnormal block alert. It then joins that warning to the first observed crash event in the manifest.

The key paper-facing metrics are:

- warning recall before crash
- warning precision
- warning F1-score
- median and percentile lead time
- lead-time coverage at practical thresholds such as `30 s`, `60 s`, and `120 s`
- false alarms per monitored hour on observed non-crash runs

These metrics are only publication-ready when the manifest includes both crash and non-crash outcomes for the evaluated cases.
