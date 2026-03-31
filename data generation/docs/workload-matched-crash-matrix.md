# Workload-Matched Crash Matrix

This path extends the safe crash-evidence workflow from the single `CRASH_APP` harness to the original four DICE workloads:

- `BROWSER`
- `VIDEO_SW`
- `PY_AI`
- `PY_STATS`

For each selected workload and anomaly family, DICE generates:

- `*_CONTROL`: workload plus anomaly, then a clean user-space exit
- `*_ABORT`: workload plus anomaly, then a real user-space crash via `os.abort()`

These pairs let you study:

- anomaly detection on the original workload families,
- crash-aware early warning on matched workload/stressor cases,
- warning behavior on anomalous runs that do not crash,
- and lead time from the first warning to the first crash.

## Case Layout

By default, the matrix includes:

- one `NOMINAL` run per workload
- `CACHE_CONTROL` and `CACHE_ABORT`
- `TLB_CONTROL` and `TLB_ABORT`
- `BRANCH_CONTROL` and `BRANCH_ABORT`
- `MEMBW_CONTROL` and `MEMBW_ABORT`
- `ATOMIC_CONTROL` and `ATOMIC_ABORT`

That is `4 x (1 + 5 x 2) = 44` cases.

## Recommended Command

Collection happens in the **terminal**, not in the notebook.

```bash
cd DICE/"data generation"

python generate_workload_matched_crash_dataset.py \
  --phase recommended \
  --duration_s 240 \
  --out_dir ./dataset/ITC_M2Pro_DATA/workload_crash_pilots/data_workload_crash_matrix \
  --tier1_alt_bin macmon \
  --tier2_template "Time Profiler" \
  --capture_crash_evidence \
  --capture_crash_screenshot \
  --wrapper_gui
```

The default wrapper schedule is:

- `warmup_s = 45`
- `ramp_s = 120`
- `hold_s = 45`

and `duration_s = 240` leaves `30s` of slack after the wrapper schedule so the abort can complete before the collector closes the case.

## Staggered Workload Schedules

If you want the anomaly onset and crash target to differ across workloads, use:

```bash
python generate_workload_matched_crash_dataset.py \
  --phase recommended \
  --duration_s 240 \
  --out_dir ./dataset/ITC_M2Pro_DATA/workload_crash_pilots/data_workload_crash_matrix \
  --schedule_profile staggered \
  --tier1_alt_bin macmon \
  --tier2_template "Time Profiler" \
  --capture_crash_evidence \
  --capture_crash_screenshot \
  --wrapper_gui
```

The built-in staggered profile is:

- `BROWSER`: warmup `25s`, ramp `105s`, hold `30s`, crash target about `160s`
- `VIDEO_SW`: warmup `50s`, ramp `95s`, hold `25s`, crash target about `170s`
- `PY_AI`: warmup `65s`, ramp `115s`, hold `30s`, crash target about `210s`
- `PY_STATS`: warmup `35s`, ramp `130s`, hold `25s`, crash target about `190s`

This profile is useful when you want the first warning time and the warning-to-crash lead time to differ more clearly across workload families.

## Run a Smaller Subset First

If you want a lighter smoke run, restrict the workloads and stressors:

```bash
python generate_workload_matched_crash_dataset.py \
  --phase tier0 \
  --duration_s 60 \
  --warmup_s 10 \
  --ramp_s 20 \
  --hold_s 20 \
  --out_dir ./dataset/ITC_M2Pro_DATA/workload_crash_pilots/data_workload_crash_smoke \
  --workloads BROWSER,PY_AI \
  --stressors CACHE,ATOMIC \
  --wrapper_dry_run
```

`--wrapper_dry_run` keeps the abort cases from actually crashing while still validating the staged control/abort workflow.

For one-workload pilots, it is often clearer to run one stressor at a time with the staggered profile:

```bash
python generate_workload_matched_crash_dataset.py \
  --phase recommended \
  --duration_s 240 \
  --out_dir ./dataset/ITC_M2Pro_DATA/workload_crash_pilots/data_workload_crash_pilot_real_py_ai_cache \
  --workloads PY_AI \
  --stressors CACHE \
  --schedule_profile staggered \
  --tier1_alt_bin macmon \
  --tier2_template "Time Profiler" \
  --capture_crash_evidence \
  --capture_crash_screenshot \
  --wrapper_gui
```

## Direct Wrapper Commands

You can also test one workload wrapper directly before running the full collection:

Dry run:

```bash
python src/dice/workload_crash_wrapper.py \
  --workload BROWSER \
  --stressor CACHE \
  --mode abort \
  --dry_run \
  --gui
```

Real user-space crash:

```bash
python src/dice/workload_crash_wrapper.py \
  --workload BROWSER \
  --stressor CACHE \
  --mode abort \
  --gui
```

## What Gets Written

The collector writes the normal DICE tier folders plus:

- `dataset/ITC_M2Pro_DATA/workload_crash_pilots/data_workload_crash_matrix/case_inventory.csv`
- `dataset/ITC_M2Pro_DATA/workload_crash_pilots/data_workload_crash_matrix/workload_crash_collection_config.json`

When crash capture is enabled, it also writes:

- `dataset/ITC_M2Pro_DATA/workload_crash_pilots/data_workload_crash_matrix/crash_evidence/crash_events.csv`
- per-case copied diagnostic reports
- filtered `log show` windows
- optional screenshots

## After Collection: Analysis

After collection, run the standard detector on the new dataset root:

```bash
cd DICE

python tools/train_eval_dice_pipeline.py \
  --root "data generation/dataset/ITC_M2Pro_DATA/workload_crash_pilots/data_workload_crash_matrix" \
  --feature_profile mixed \
  --protocol global \
  --out_dir "data generation/dataset/ITC_M2Pro_DATA/workload_crash_pilots/data_workload_crash_matrix/results_dice_workload_crash_mixed"
```

Then export the warning-to-crash bundle:

```bash
python tools/early_warning_analysis.py \
  --result_dir "data generation/dataset/ITC_M2Pro_DATA/workload_crash_pilots/data_workload_crash_matrix/results_dice_workload_crash_mixed" \
  --out_dir "data generation/dataset/ITC_M2Pro_DATA/workload_crash_pilots/data_workload_crash_matrix/results_itc_workload_crash/mixed" \
  --feature_profile mixed \
  --crash_manifest "data generation/dataset/ITC_M2Pro_DATA/workload_crash_pilots/data_workload_crash_matrix/crash_evidence/crash_events.csv"
```

You can then render crash-evidence cards in the same way as the main ITC path:

```bash
python tools/generate_crash_evidence_cards.py \
  --alignment_csv "data generation/dataset/ITC_M2Pro_DATA/workload_crash_pilots/data_workload_crash_matrix/results_itc_workload_crash/mixed/early_warning_crash_alignment.csv" \
  --out_dir "data generation/dataset/ITC_M2Pro_DATA/workload_crash_pilots/data_workload_crash_matrix/results_itc_workload_crash/mixed/crash_evidence_cards" \
  --title "DICE Workload-Matched Crash Gallery (Mixed Profile)"
```

If you prefer the notebook path after collection, open `dice_results_analysis.ipynb` and run `8G. Workload-Matched Crash Matrix`. The notebook now auto-detects the newest `ITC_M2Pro_DATA/workload_crash_pilots/data_workload_crash_*` folder and prints the crash output locations before it runs.

## Safety Notes

- Run this only against the dedicated DICE wrappers, not your daily applications.
- Save active work before real abort runs.
- Start with `--wrapper_dry_run` if you want to confirm the schedule and case list first.
- Prefer one or two workloads as a pilot before collecting the full 44-case matrix.
