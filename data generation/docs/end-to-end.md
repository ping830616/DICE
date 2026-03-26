---
layout: default
title: End-to-End User Guide
---

# End-to-End User Guide

This guide describes the practical public workflow for collecting, validating, and exporting the DICE ITC dataset.

## 1. Environment Setup

```bash
cd DICE/"data generation"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Optional dependency for the `PY_AI` workload:

```bash
pip install torch
```

## 2. Dataset Design

- Workloads: `BROWSER`, `VIDEO_SW`, `PY_AI`, `PY_STATS`
- Conditions: `NOMINAL`, `CACHE`, `TLB`, `BRANCH`, `MEMBW`, `ATOMIC`
- Cases: `24` total
- Sampling rate before alignment: `5 Hz`
- Standard run duration: `1000 s`
- Samples per processed run: `5000` (`5001` CSV lines with header)

## 3. Choose a Collection Mode

### Recommended Apple Silicon Profile

```bash
python generate_dataset.py --phase recommended --duration_s 1000 --out_dir ./data --tier1_alt_bin macmon --tier2_template "Time Profiler"
```

This profile runs:

- `Tier-0`
- `Tier-1-alt`
- `Tier-2`

Use it when you want the closest public match to the Apple Silicon procedure behind the released `ITC_M2Pro_DATA` dataset.

### Portable Profile

```bash
python generate_dataset.py --phase portable --duration_s 1000 --out_dir ./data --tier1_alt_bin macmon --tier2_template "Time Profiler"
```

Portable mode:

- always runs `Tier-0`
- prefers `Tier-1-alt` if `macmon` is available
- falls back to legacy `Tier-1` if `powermetrics` is available but `macmon` is not
- runs `Tier-2` only when `xctrace` is available and licensed
- skips unsupported tiers with an explicit message

Use this mode when you want the workflow to adapt to the capabilities of the current machine.

### Legacy Compatibility Modes

```bash
python generate_dataset.py --phase both --duration_s 1000 --out_dir ./data
python generate_dataset.py --phase all --duration_s 1000 --out_dir ./data --tier2_template "Time Profiler"
```

- `both` = `tier0 + tier1`
- `all` = `tier0 + tier1 + tier2`

These modes remain available for compatibility, but they do not match the recommended Apple Silicon release profile because they use legacy `Tier-1`.

## 4. Tooling Checks

Before a full Apple Silicon collection, confirm the required tools are available:

```bash
macmon --help
powermetrics --help
xcrun xctrace version
```

Tier-2 also requires a working Xcode installation and an accepted Xcode license.

## 5. Expected Time

At the default `duration_s=1000` and `24` cases, the nominal collection window is:

- `Tier-0`: about `6 h 40 m`, plus about `10 s` once for the Tier-0 schema probe
- `Tier-1-alt`: about `6 h 40 m`, plus parsing overhead
- `Tier-1`: about `6 h 40 m`, plus parsing and `sudo` startup overhead
- `Tier-2`: about `6 h 40 m`, plus trace-export overhead

On the reference local collection tree used for the released dataset, the observed wall-clock times were approximately:

- `Tier-0`: `7 h 11 m`
- `Tier-1-alt`: `8 h 02 m`
- `Tier-2`: `9 h 31 m`

The collector prints the current case ID, per-case elapsed time, tier elapsed time, and estimated remaining time while the run is in progress.

## 6. Validate the Full Collection Tree

For the recommended Apple Silicon profile:

```bash
python tools/repair_itc_dataset.py --root ./data --tier1_mode alt
python tools/validate_itc_dataset.py --root ./data --tier1_mode alt --check_tier2
```

For a legacy Tier-1 tree:

```bash
python tools/validate_itc_dataset.py --root ./data --tier1_mode powermetrics --check_tier2
```

## 7. Export a Processed Public Snapshot

The released `ITC_M2Pro_DATA` layout is a processed snapshot, not a full raw collection tree. After a full collection, create a matching stripped export with:

```bash
python tools/export_release_snapshot.py --root ./data --out_dir ./ITC_M2Pro_DATA_export --tier1_mode alt
```

Validate the stripped snapshot with:

```bash
python tools/validate_itc_dataset.py --root ./ITC_M2Pro_DATA_export --tier1_mode alt --check_tier2 --processed_only
```

## 8. Repair and Rerun

Rebuild manifests from existing files:

```bash
python tools/repair_itc_dataset.py --root ./data --tier1_mode alt
```

Rerun selected Tier-1-alt cases:

```bash
python tools/rerun_cases.py \
  --phase tier1_alt \
  --duration_s 1000 \
  --out_dir ./data \
  --tier1_alt_bin macmon \
  --cases BROWSER__CACHE PY_AI__TLB
```

Rerun selected Tier-2 cases:

```bash
python tools/rerun_cases.py \
  --phase tier2 \
  --duration_s 1000 \
  --out_dir ./data \
  --tier2_template "Time Profiler" \
  --cases BROWSER__CACHE PY_AI__TLB
```

## 9. Output Structure

A full collection tree contains:

```text
data/
  tier0/<CASE_ID>/tier0_full_5hz.csv
  tier1_alt/<CASE_ID>/macmon_raw.jsonl
  tier1_alt/<CASE_ID>/tier1_alt_core_5hz.csv
  tier1_alt/<CASE_ID>/tier1_alt_full_5hz.csv
  tier1/<CASE_ID>/powermetrics_raw.txt
  tier1/<CASE_ID>/tier1_core_5hz.csv
  tier1/<CASE_ID>/tier1_full_5hz.csv
  tier2/<CASE_ID>/xctrace.trace
  tier2/<CASE_ID>/xctrace_export.xml
  tier2/<CASE_ID>/tier2_core_5hz.csv
  tier2/<CASE_ID>/tier2_full_5hz.csv
  meta/<CASE_ID>/meta_tier{0,1,1_alt,2}.json
  logs/<CASE_ID>/*.log
  manifest_tier0.csv
  manifest_tier1.csv
  manifest_tier1_alt.csv
  manifest_tier2.csv
  tier0_schema_global.json
  tier1_schema_global.json
  tier1_alt_schema_global.json
  tier2_schema_global.json
```

A processed release snapshot keeps only the processed tier CSV files plus `no_nan_report.json`.
