# ITC Dataset Collection Methodology (Tier-0 to Tier-2, macOS)

This document describes the local macOS collection workflow used to build the released dataset. The public GitHub repo is notebook-first for results reproduction and does not ship the low-level Tier-1/Tier-2 shell collectors.

## 1) Case Design

- Workloads (`4`): `BROWSER`, `VIDEO_SW`, `PY_AI`, `PY_STATS`
- Stressors (`6`): `NOMINAL`, `CACHE`, `TLB`, `BRANCH`, `MEMBW`, `ATOMIC`
- Total cases: `4 x 6 = 24`
- Stable case ID format: `WORKLOAD__STRESSOR` (used identically across all tiers)

## 2) Tier Definitions

### Tier-0 (OS telemetry, low-NaN schema)
- Source: `psutil` counters at `5 Hz`.
- Raw artifact per case: `tier0_full_5hz.csv`.
- Schema strategy:
  - Short probe (default `10s`) collects candidate fields.
  - Keep only fields that are non-NaN at least once.
  - Persist global schema as `tier0_schema_global.json`.
  - Reuse same schema across all cases for stable headers and lower NaN density.

### Tier-1 (powermetrics telemetry)
- Source: `powermetrics` at `5 Hz` (`-i 200`) for `5000` samples (`1000s` default).
- Raw artifact per case: `powermetrics_raw.txt`.
- Parsed outputs per case:
  - `tier1_core_5hz.csv` (dense power/frequency core)
  - `tier1_full_5hz.csv` (global schema, consistent header across cases)
- Global schema persisted as `tier1_schema_global.json`.

### Tier-2 (optional xctrace telemetry)
- Source: `xcrun xctrace` with template-based recording (`Time Profiler` default).
- Raw artifacts per case:
  - `xctrace.trace`
  - `xctrace_export.xml`
- Parsed outputs per case:
  - `tier2_core_5hz.csv`
  - `tier2_full_5hz.csv`
- Global schema persisted as `tier2_schema_global.json`.
- Note: Tier-2 depends on Xcode tooling and accepted Xcode license.

## 3) Output Layout

Assuming `--out_dir ./data`:

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

## 4) Environment Setup

```bash
cd DICE/"data generation"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install torch  # optional, recommended for PY_AI workload
```

## 5) Collection Commands

### 5.1 Tier-0 pass

```bash
python generate_dataset.py --phase tier0 --duration_s 1000 --out_dir ./data
```

### 5.2 Tier-1 pass

```bash
python generate_dataset.py --phase tier1 --duration_s 1000 --out_dir ./data
```

### 5.3 Tier-0 + Tier-1 (two-pass baseline)

```bash
python generate_dataset.py --phase both --duration_s 1000 --out_dir ./data
```

### 5.4 Tier-2 pass (optional)

```bash
python generate_dataset.py --phase tier2 --duration_s 1000 --out_dir ./data --tier2_template "Time Profiler"
```

### 5.5 All three tiers

```bash
python generate_dataset.py --phase all --duration_s 1000 --out_dir ./data --tier2_template "Time Profiler"
```

## 6) Progress Monitoring

Run in a second terminal while a tier is collecting.

### Tier-0 monitor

```bash
while true; do
  latest=$(ls -td ./data/tier0/* 2>/dev/null | head -n 1)
  if [ -z "$latest" ]; then echo "No Tier-0 case folder yet"; sleep 2; continue; fi
  cid=$(basename "$latest")
  f="$latest/tier0_full_5hz.csv"
  if [ -f "$f" ]; then
    echo "Tier-0 case: $cid | lines: $(wc -l < "$f") (target 5001)"
  else
    echo "Tier-0 case: $cid | CSV not created yet"
  fi
  sleep 2
  clear
done
```

### Tier-1 monitor

```bash
while true; do
  latest=$(ls -td ./data/tier1/* 2>/dev/null | head -n 1)
  if [ -z "$latest" ]; then echo "No Tier-1 case folder yet"; sleep 2; continue; fi
  cid=$(basename "$latest")
  raw="$latest/powermetrics_raw.txt"
  core="$latest/tier1_core_5hz.csv"
  full="$latest/tier1_full_5hz.csv"
  echo "Tier-1 case: $cid"
  [ -f "$raw" ] && ls -lh "$raw" | awk '{print "raw size:",$5,"modified:",$6,$7,$8}' || echo "raw missing"
  [ -f "$core" ] && echo "core lines: $(wc -l < "$core") (target 5001)" || echo "core missing"
  [ -f "$full" ] && echo "full lines: $(wc -l < "$full") (target 5001)" || echo "full missing"
  sleep 2
  clear
done
```

### Tier-2 monitor

```bash
while true; do
  latest=$(ls -td ./data/tier2/* 2>/dev/null | head -n 1)
  if [ -z "$latest" ]; then echo "No Tier-2 case folder yet"; sleep 2; continue; fi
  cid=$(basename "$latest")
  trace="$latest/xctrace.trace"
  raw="$latest/xctrace_export.xml"
  core="$latest/tier2_core_5hz.csv"
  full="$latest/tier2_full_5hz.csv"
  echo "Tier-2 case: $cid"
  [ -e "$trace" ] && ls -ld "$trace" | awk '{print "trace modified:",$6,$7,$8}' || echo "trace missing"
  [ -f "$raw" ] && ls -lh "$raw" | awk '{print "raw size:",$5,"modified:",$6,$7,$8}' || echo "raw missing"
  [ -f "$core" ] && echo "core lines: $(wc -l < "$core") (target 5001)" || echo "core missing"
  [ -f "$full" ] && echo "full lines: $(wc -l < "$full") (target 5001)" || echo "full missing"
  sleep 2
  clear
done
```

## 7) Completion Validators

### Tier-0 + Tier-1

```bash
python tools/validate_itc_dataset.py --root ./data
```

### Include Tier-2

```bash
python tools/validate_itc_dataset.py --root ./data --check_tier2
```

Expected for full runs:
- `24` case folders per tier.
- Manifest lines: `25` (`header + 24`).
- Per-case CSV line count: `5001`.

## 8) Tier-0 NaN Sanity (quick)

```bash
python - <<'PY'
import glob
import pandas as pd

files = sorted(glob.glob("./data/tier0/*/tier0_full_5hz.csv"))
print("tier0 files:", len(files))
if not files:
    raise SystemExit(0)

df = pd.read_csv(files[0])
nan_frac = df.isna().mean().sort_values(ascending=False)
print("Top NaN columns (first file):")
print(nan_frac.head(20))
print("Overall NaN fraction:", df.isna().mean().mean())
PY
```

## 9) Troubleshooting

- Tier-1 permission issues:
  - Pre-authenticate sudo: `sudo -v`
- Tier-2 license/tooling issues:
  - Ensure Xcode is installed and license is accepted.
  - Verify command works: `xcrun xctrace version`
- Case reruns:
  - `python tools/rerun_cases.py --phase tier1 --cases BROWSER__CACHE --duration_s 1000 --out_dir ./data --scripts_dir ./scripts`
  - `python tools/rerun_cases.py --phase tier2 --cases BROWSER__CACHE --duration_s 1000 --out_dir ./data --scripts_dir ./scripts --tier2_template "Time Profiler"`
