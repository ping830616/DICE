# Controlled Crash Harness

This path is the safest way to collect **real crash artifacts** on a daily laptop without intentionally provoking a kernel panic or full-machine freeze.

The harness creates a dedicated user-space process, ramps pressure in a bounded way, and then either:

- exits cleanly for a matched control run, or
- calls `os.abort()` to trigger a real macOS crash report for that process

Because the crash is user-space only, the host remains usable and the normal DICE crash-evidence collector can still capture:

- `crash_evidence/crash_events.csv`
- copied macOS `DiagnosticReports`
- filtered `log show` output
- optional screenshots

## What Runs

The crash harness uses these cases:

- `CRASH_APP__NOMINAL`
- `CRASH_APP__MEM_RAMP_CONTROL`
- `CRASH_APP__MEM_RAMP_ABORT`
- `CRASH_APP__CPU_RAMP_CONTROL`
- `CRASH_APP__CPU_RAMP_ABORT`

The control cases are important because they let you measure false alarms and warning precision, not only recall on crash cases.

## Recommended Command

Collection happens in the **terminal**, not in the notebook.

```bash
cd DICE/"data generation"

python generate_crash_harness_dataset.py \
  --phase recommended \
  --duration_s 300 \
  --out_dir ./data_crash_harness \
  --tier1_alt_bin macmon \
  --tier2_template "Time Profiler" \
  --capture_crash_evidence \
  --capture_crash_screenshot
```

This runs:

- Tier-0
- Tier-1-alt
- Tier-2

for the small crash-harness case set.

## If You Want a Visible Window for Screenshots

Add:

```bash
  --harness_gui
```

This opens a small dedicated harness window so post-crash screenshots are easier to interpret in a paper figure.

## Schedule Controls

The harness is staged:

1. warm-up
2. anomaly ramp
3. hold
4. clean exit or real user-space crash

The default schedule is:

- `warmup_s = 45`
- `ramp_s = 120`
- `hold_s = 45`

You can change it from the terminal:

```bash
python generate_crash_harness_dataset.py \
  --phase recommended \
  --duration_s 360 \
  --out_dir ./data_crash_harness \
  --capture_crash_evidence \
  --warmup_s 60 \
  --ramp_s 150 \
  --hold_s 60
```

## Direct Harness Smoke Test

If you want to test the harness logic without collecting DICE telemetry first:

```bash
python src/dice/crash_harness.py --scenario MEM_RAMP_CONTROL --gui
```

If you want to test an abort scenario **without actually crashing the harness process**, use:

```bash
python src/dice/crash_harness.py --scenario MEM_RAMP_ABORT --dry_run --gui
```

To trigger the real user-space crash:

```bash
python src/dice/crash_harness.py --scenario MEM_RAMP_ABORT --gui
```

## Notebook or Terminal?

- **Terminal**: run crash-harness collection
- **Notebook**: analyze the resulting outputs later

The notebook is the right place to inspect early-warning tables, crash-evidence cards, and paper-facing figures after collection is complete.

## After Collection: Analysis

Once `data_crash_harness/` exists, you have two analysis options:

1. Run the detector directly from the terminal:

```bash
cd DICE

python tools/train_eval_dice_pipeline.py \
  --root "data generation/data_crash_harness" \
  --feature_profile mixed \
  --protocol global \
  --out_dir "data generation/data_crash_harness/results_dice_crash_harness_mixed"
```

2. Open `dice_results_analysis.ipynb` and run `8F. Controlled Crash-Harness Analysis`.

That notebook section:

- reads `data generation/data_crash_harness/` as a second dataset root,
- reuses the normal DICE detector and early-warning exporter,
- renders the warning-to-crash alignment table,
- and previews the generated crash-evidence cards inline.

The crash-harness collector now also writes:

- `data_crash_harness/case_inventory.csv`
- `data_crash_harness/crash_harness_collection_config.json`

so the later analysis can recover the intended benign/anomalous labels without relying only on case names.

## Safety Notes

- Run this only against the dedicated crash harness process, not your real daily applications.
- Save your work first if you enable the GUI mode and screenshots.
- Prefer user-space crash scenarios on your daily laptop; do not intentionally chase kernel panics or full-machine freezes here.
