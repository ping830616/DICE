---
layout: default
title: End-to-End User Guide
---

# End-to-End User Guide (Tier-0 to Tier-2)

This guide is designed for users who want a practical, reproducible workflow from environment setup to final validation.

## 1. Environment Setup

```bash
cd DICE/"data generation"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Optional dependency for AI workload behavior:

```bash
pip install torch
```

## 2. Dataset Design

- Workloads: `BROWSER`, `VIDEO_SW`, `PY_AI`, `PY_STATS`
- Stressors: `NOMINAL`, `CACHE`, `TLB`, `BRANCH`, `MEMBW`, `ATOMIC`
- Cases: `24` total (`WORKLOAD__STRESSOR`)
- Sampling rate: `5 Hz`
- Standard run duration: `1000 s`
- Samples per run: `5000` (`5001` lines with header)

## 3. Run Recommended Profile (Tier-0 + Tier-1-alt)

```bash
python generate_dataset.py --phase tier0 --duration_s 1000 --out_dir ./data
python generate_dataset.py --phase tier1_alt --duration_s 1000 --out_dir ./data --tier1_alt_bin macmon
```

This profile uses:

1. Tier-0 host telemetry collection.
2. Tier-1-alt collection on Apple Silicon (`macmon` source with automatic fallback when needed).

Legacy baseline (optional):

```bash
python generate_dataset.py --phase both --duration_s 1000 --out_dir ./data
```

Expected wall-clock time at the default `duration_s=1000` and `24` cases:

- `Tier-0`: about `6 h 40 m` total, plus about `10 s` once for the initial global schema probe
- `Tier-1-alt`: about `6 h 40 m` total, plus parsing overhead; if `macmon` fails and a case falls back to `powermetrics`, that case can take roughly twice as long
- `Legacy both` (`tier0 + tier1`): about `13 h 20 m` plus parsing and startup overhead

The collector now prints per-case elapsed time, total tier elapsed time, and an estimated remaining time while the run is in progress.

## 4. Run Tier-2 (Optional)

Tier-2 requires Xcode tooling and an accepted license.

Preflight:

```bash
xcrun xctrace version
xcrun xctrace list templates | rg "Time Profiler"
```

Run Tier-2:

```bash
python generate_dataset.py --phase tier2 --duration_s 1000 --out_dir ./data --tier2_template "Time Profiler"
```

Expected wall-clock time at the default `duration_s=1000` and `24` cases:

- `Tier-2`: about `6 h 40 m` total, plus trace-export overhead after each case

Important public-release note:

- the Tier-2 Python parser is included, but the low-level shell collector helper used to record and export traces is not shipped in the public GitHub release
- on a local private setup where that helper exists, the command above is the intended entry point

## 5. Full Collection in One Command

```bash
python generate_dataset.py --phase all --duration_s 1000 --out_dir ./data --tier2_template "Time Profiler"
```

Important:

- in the current public code, `--phase all` means `tier0 + legacy tier1 + tier2`
- it does **not** include the recommended Apple Silicon `tier1_alt` path
- if you want the current paper-facing Apple dataset profile, run `tier0`, then `tier1_alt`, then `tier2` explicitly

## 6. Validate Outputs

Recommended Tier-0 + Tier-1-alt + Tier-2 profile:

```bash
python tools/validate_itc_dataset.py --root ./data --tier1_mode alt --check_tier2
```

Legacy Tier-0 + Tier-1 + Tier-2 profile:

```bash
python tools/validate_itc_dataset.py --root ./data --tier1_mode powermetrics --check_tier2
```

## 7. Repair and Rerun

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
  --scripts_dir ./scripts \
  --tier1_alt_bin macmon \
  --cases BROWSER__CACHE PY_AI__TLB
```

Rerun selected Tier-2 cases:

```bash
python tools/rerun_cases.py \
  --phase tier2 \
  --duration_s 1000 \
  --out_dir ./data \
  --scripts_dir ./scripts \
  --tier2_template "Time Profiler" \
  --cases BROWSER__CACHE PY_AI__TLB
```

## 8. Output Structure

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
  manifest_tier1_alt.csv
  manifest_tier1.csv
  manifest_tier2.csv
  tier0_schema_global.json
  tier1_alt_schema_global.json
  tier1_schema_global.json
  tier2_schema_global.json
```

## 9. Expected Counts for a Complete Run

- Tier folders per phase: `24`
- Manifest line count per phase: `25`
- CSV line count per case: `5001`

For detailed per-feature definitions, see [Feature Dictionary](feature-dictionary.md).
