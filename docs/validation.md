---
layout: default
title: Validation and Repair
---

# Validation and Repair

## Validate Tier-0 + Tier-1

```bash
python tools/validate_itc_dataset.py --root ./data
```

## Validate Including Tier-2

```bash
python tools/validate_itc_dataset.py --root ./data --check_tier2
```

## Rebuild Manifests

```bash
python tools/repair_itc_dataset.py --root ./data
```

## Rerun Specific Cases

Tier-1 example:

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
