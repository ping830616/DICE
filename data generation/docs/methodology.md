---
layout: default
title: End-to-End Methodology
---

# End-to-End Methodology

## Case Matrix

- Workloads: `BROWSER`, `VIDEO_SW`, `PY_AI`, `PY_STATS`
- Stressors: `NOMINAL`, `CACHE`, `TLB`, `BRANCH`, `MEMBW`, `ATOMIC`
- Case ID: `WORKLOAD__STRESSOR`
- Total cases: `24`

## Recommended Three-Tier Profile

1. Tier-0 pass:
   - collect host OS telemetry (`psutil`) at 5 Hz,
   - build low-NaN probe schema,
   - write `tier0_full_5hz.csv` per case.
2. Tier-1-alt pass (recommended on Apple Silicon):
   - collect `macmon` telemetry,
   - auto-fallback to `powermetrics` when needed,
   - write `tier1_alt_core_5hz.csv` and `tier1_alt_full_5hz.csv`.
3. Tier-2 pass:
   - record `xctrace` traces,
   - export XML,
   - parse to `tier2_core_5hz.csv` and `tier2_full_5hz.csv`.

Legacy Tier-1 (`powermetrics`) remains available for compatibility, but the recommended publication profile is `tier0 + tier1_alt + tier2`.

## Standard Terminal Sequence

```bash
cd DICE/"data generation"
source .venv/bin/activate

# Tier-0
python generate_dataset.py --phase tier0 --duration_s 1000 --out_dir ./data

# Tier-1-alt (recommended)
python generate_dataset.py --phase tier1_alt --duration_s 1000 --out_dir ./data --tier1_alt_bin macmon

# Tier-2
python generate_dataset.py --phase tier2 --duration_s 1000 --out_dir ./data --tier2_template "Time Profiler"
```

## Validation Sequence

```bash
python tools/repair_itc_dataset.py --root ./data --tier1_mode alt
python tools/validate_itc_dataset.py --root ./data --tier1_mode alt --check_tier2
```

## Output Layout

```text
data/
  tier0/<CASE_ID>/tier0_full_5hz.csv
  tier1_alt/<CASE_ID>/macmon_raw.jsonl
  tier1_alt/<CASE_ID>/tier1_alt_core_5hz.csv
  tier1_alt/<CASE_ID>/tier1_alt_full_5hz.csv
  tier2/<CASE_ID>/xctrace.trace
  tier2/<CASE_ID>/xctrace_export.xml
  tier2/<CASE_ID>/tier2_core_5hz.csv
  tier2/<CASE_ID>/tier2_full_5hz.csv
  meta/<CASE_ID>/meta_tier{0,1_alt,2}.json
  logs/<CASE_ID>/*.log
  manifest_tier0.csv
  manifest_tier1_alt.csv
  manifest_tier2.csv
  tier0_schema_global.json
  tier1_alt_schema_global.json
  tier2_schema_global.json
```

Legacy optional output:

```text
  tier1/<CASE_ID>/powermetrics_raw.txt
  tier1/<CASE_ID>/tier1_core_5hz.csv
  tier1/<CASE_ID>/tier1_full_5hz.csv
  manifest_tier1.csv
  tier1_schema_global.json
```
