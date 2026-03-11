---
layout: default
title: Validation and Repair
---

# Validation and Repair

## Validate Recommended Profile (Tier-0 + Tier-1-alt)

```bash
python tools/validate_itc_dataset.py --root ./data --tier1_mode alt
```

## Validate Recommended Profile Including Tier-2

```bash
python tools/validate_itc_dataset.py --root ./data --tier1_mode alt --check_tier2
```

## Validate Legacy Tier-1 + Tier-2

```bash
python tools/validate_itc_dataset.py --root ./data --tier1_mode powermetrics --check_tier2
```

## Validate Both Tier-1 Sources + Tier-2

```bash
python tools/validate_itc_dataset.py --root ./data --tier1_mode both --check_tier2
```

## Rebuild Manifests

```bash
python tools/repair_itc_dataset.py --root ./data --tier1_mode alt
```

## Build NaN-Free, Model-Ready Dataset

Use this when you want no NaNs in output CSVs and a clear report of unsupported/sparse features.

```bash
python tools/ensure_no_nan_dataset.py \
  --root ./data \
  --tier1_mode alt \
  --out_dir ./data_clean_no_nan \
  --min_coverage_ratio 0.95
```

Outputs:

- `./data_clean_no_nan/...` mirrored Tier-0/1/2 CSV structure
- `./data_clean_no_nan/no_nan_report.json` with:
  - dropped all-NaN columns (globally unsupported)
  - dropped low-coverage columns
  - before/after NaN fractions per dataset group

## Rerun Specific Cases

Tier-1-alt example:

```bash
python tools/rerun_cases.py \
  --phase tier1_alt \
  --duration_s 1000 \
  --out_dir ./data \
  --scripts_dir ./scripts \
  --tier1_alt_bin macmon \
  --cases BROWSER__CACHE PY_AI__TLB
```

Tier-1 legacy example:

```bash
python tools/rerun_cases.py \
  --phase tier1 \
  --duration_s 1000 \
  --out_dir ./data \
  --scripts_dir ./scripts \
  --cases BROWSER__CACHE PY_AI__TLB
```

Tier-2 example:

```bash
python tools/rerun_cases.py \
  --phase tier2 \
  --duration_s 1000 \
  --out_dir ./data \
  --scripts_dir ./scripts \
  --tier2_template "Time Profiler" \
  --cases BROWSER__CACHE PY_AI__TLB
```

## Expected Full-Run Counts

- `24` case folders per tier
- `25` lines per manifest (`header + 24`)
- `5001` lines per case CSV (`header + 5000` rows)
