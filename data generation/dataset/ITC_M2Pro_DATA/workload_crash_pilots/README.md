# Workload Crash Pilots

This folder is intentionally represented in GitHub by a lightweight manifest instead of the full raw pilot collections.

The complete local pilot bundle under `workload_crash_pilots/` is large and machine-generated. On the collection machine it is about `21 GB` and may include:

- copied macOS crash reports
- filtered `log show` windows
- screenshots
- per-case tier outputs
- rerun artifacts and local analysis folders

To keep the GitHub repository reviewable, DICE tracks the paper-facing summaries derived from these pilots under:

- `results_itc_paper/`
- `results_itc_appendix/`
- `results_itc_crash_bridge/`

This folder now keeps two small tracked files:

- `README.md`: how the pilots were generated
- `pilot_manifest.csv`: exact pilot-level metadata and case lists

## What The Four Pilots Are

The local pilot set consists of four one-workload crash studies:

1. `data_workload_crash_pilot_real_browser_branch`
2. `data_workload_crash_pilot_real_py_ai_cache`
3. `data_workload_crash_pilot_real_py_stats_atomic`
4. `data_workload_crash_pilot_real_video_membw`

Each pilot contains exactly three cases:

- one `NOMINAL` run
- one `*_CONTROL` anomaly run that exits cleanly
- one `*_ABORT` anomaly run that ends with a real user-space crash via the DICE wrapper

## Shared Generation Method

All four pilots were generated with the same collection mode:

- script: `data generation/generate_workload_matched_crash_dataset.py`
- `--phase recommended`
- `--duration_s 240`
- `--schedule_profile staggered`
- `--wrapper_gui`
- `--capture_crash_evidence`
- `--capture_crash_screenshot`
- `--tier1_alt_bin macmon`
- `--tier2_template "Time Profiler"`

The staggered profile gives each workload a different anomaly-onset and crash-target time so the warning-to-crash story is less synchronized across workloads.

## Exact Commands

Run these from `DICE/"data generation"`:

### 1. BROWSER / BRANCH

```bash
python generate_workload_matched_crash_dataset.py \
  --phase recommended \
  --duration_s 240 \
  --out_dir ./dataset/ITC_M2Pro_DATA/workload_crash_pilots/data_workload_crash_pilot_real_browser_branch \
  --workloads BROWSER \
  --stressors BRANCH \
  --schedule_profile staggered \
  --tier1_alt_bin macmon \
  --tier2_template "Time Profiler" \
  --capture_crash_evidence \
  --capture_crash_screenshot \
  --wrapper_gui
```

Generated cases:

- `BROWSER__NOMINAL`
- `BROWSER__BRANCH_CONTROL`
- `BROWSER__BRANCH_ABORT`

Workload schedule:

- warmup `25s`
- ramp `105s`
- hold `30s`
- crash target about `160s`

### 2. PY_AI / CACHE

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

Generated cases:

- `PY_AI__NOMINAL`
- `PY_AI__CACHE_CONTROL`
- `PY_AI__CACHE_ABORT`

Workload schedule:

- warmup `65s`
- ramp `115s`
- hold `30s`
- crash target about `210s`

### 3. PY_STATS / ATOMIC

```bash
python generate_workload_matched_crash_dataset.py \
  --phase recommended \
  --duration_s 240 \
  --out_dir ./dataset/ITC_M2Pro_DATA/workload_crash_pilots/data_workload_crash_pilot_real_py_stats_atomic \
  --workloads PY_STATS \
  --stressors ATOMIC \
  --schedule_profile staggered \
  --tier1_alt_bin macmon \
  --tier2_template "Time Profiler" \
  --capture_crash_evidence \
  --capture_crash_screenshot \
  --wrapper_gui
```

Generated cases:

- `PY_STATS__NOMINAL`
- `PY_STATS__ATOMIC_CONTROL`
- `PY_STATS__ATOMIC_ABORT`

Workload schedule:

- warmup `35s`
- ramp `130s`
- hold `25s`
- crash target about `190s`

### 4. VIDEO_SW / MEMBW

```bash
python generate_workload_matched_crash_dataset.py \
  --phase recommended \
  --duration_s 240 \
  --out_dir ./dataset/ITC_M2Pro_DATA/workload_crash_pilots/data_workload_crash_pilot_real_video_membw \
  --workloads VIDEO_SW \
  --stressors MEMBW \
  --schedule_profile staggered \
  --tier1_alt_bin macmon \
  --tier2_template "Time Profiler" \
  --capture_crash_evidence \
  --capture_crash_screenshot \
  --wrapper_gui
```

Generated cases:

- `VIDEO_SW__NOMINAL`
- `VIDEO_SW__MEMBW_CONTROL`
- `VIDEO_SW__MEMBW_ABORT`

Workload schedule:

- warmup `50s`
- ramp `95s`
- hold `25s`
- crash target about `170s`

## What Gets Written In Each Pilot Root

Each pilot root is expected to contain:

- `case_inventory.csv`
- `workload_crash_collection_config.json`
- `crash_evidence/`
- tier folders such as `tier0/`, `tier1_alt/`, and `tier2/` when available
- `meta/`
- optional downstream analysis folders if you later run detector, early-warning, or feature-level analysis

When crash capture is enabled, `crash_evidence/` may include:

- `crash_events.csv`
- copied diagnostic reports
- filtered system-log windows
- screenshots

## How These Pilots Connect Back To The Paper

These pilots support the crash-aware extension in the notebook and the whole-study bridge back to the main ITC dataset:

- notebook section `6. Crash-Aware Early Warning and Real Crash Localization`
- `results_itc_crash_bridge/`
- crash evidence cards and feature-level crash overlays

The tracked repo artifacts are the derived summaries, not the full raw pilot trees.

## If You Need To Share The Full Pilot Bundle

Package it outside normal git history. For example:

```bash
cd "data generation/dataset/ITC_M2Pro_DATA"
tar -czf workload_crash_pilots_bundle.tar.gz workload_crash_pilots
```

Then publish that archive as a release asset, on institutional storage, or through another dataset host. That keeps the code repository small while still making the full pilot data available when needed.
