---
layout: default
title: End-to-End User Guide
---

# End-to-End User Guide (Tier-0 to Tier-2)

This guide is designed for users who want a practical, reproducible workflow from environment setup to final validation.

## 1. Environment Setup

```bash
cd DICE
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

## 3. Run Tier-0 and Tier-1 (Baseline)

```bash
python generate_dataset.py --phase both --duration_s 1000 --out_dir ./data
```

This command performs a two-pass baseline collection:

1. Tier-0 host telemetry collection.
2. Tier-1 powermetrics collection and parsing.

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

## 5. Full Collection in One Command

```bash
python generate_dataset.py --phase all --duration_s 1000 --out_dir ./data --tier2_template "Time Profiler"
```

## 6. Validate Outputs

Tier-0 and Tier-1:

```bash
python tools/validate_itc_dataset.py --root ./data
```

Tier-0 through Tier-2:

```bash
python tools/validate_itc_dataset.py --root ./data --check_tier2
```

## 7. Repair and Rerun

Rebuild manifests from existing files:

```bash
python tools/repair_itc_dataset.py --root ./data
```

Rerun selected Tier-1 cases:

```bash
python tools/rerun_cases.py \
  --phase tier1 \
  --duration_s 1000 \
  --out_dir ./data \
  --scripts_dir ./scripts \
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
  tier1/<CASE_ID>/powermetrics_raw.txt
  tier1/<CASE_ID>/tier1_core_5hz.csv
  tier1/<CASE_ID>/tier1_full_5hz.csv
  tier2/<CASE_ID>/xctrace.trace
  tier2/<CASE_ID>/xctrace_export.xml
  tier2/<CASE_ID>/tier2_core_5hz.csv
  tier2/<CASE_ID>/tier2_full_5hz.csv
  meta/<CASE_ID>/meta_tier{0,1,2}.json
  logs/<CASE_ID>/*.log
  manifest_tier0.csv
  manifest_tier1.csv
  manifest_tier2.csv
  tier0_schema_global.json
  tier1_schema_global.json
  tier2_schema_global.json
```

## 9. Expected Counts for a Complete Run

- Tier folders per phase: `24`
- Manifest line count per phase: `25`
- CSV line count per case: `5001`

For detailed per-feature definitions, see [Feature Dictionary](feature-dictionary.md).
