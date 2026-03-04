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

## Two-Pass Baseline + Optional Tier-2

1. Tier-0 pass:
   - collect OS telemetry with `psutil` at 5 Hz,
   - generate low-NaN global schema from a probe,
   - write `tier0_full_5hz.csv` per case.
2. Tier-1 pass:
   - collect `powermetrics` text,
   - parse to dense core + global full schema,
   - write `tier1_core_5hz.csv` and `tier1_full_5hz.csv`.
3. Tier-2 pass (optional):
   - record `xctrace` traces,
   - export XML,
   - parse to `tier2_core_5hz.csv` and `tier2_full_5hz.csv`.

## Standard Terminal Sequence

```bash
cd DICE
source .venv/bin/activate

# Tier-0
python generate_dataset.py --phase tier0 --duration_s 1000 --out_dir ./data

# Tier-1
python generate_dataset.py --phase tier1 --duration_s 1000 --out_dir ./data

# Tier-2
python generate_dataset.py --phase tier2 --duration_s 1000 --out_dir ./data --tier2_template "Time Profiler"
```

## Output Layout

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
