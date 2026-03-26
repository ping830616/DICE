---
layout: default
title: End-to-End Methodology
---

# End-to-End Methodology

## Case Matrix

- workloads: `BROWSER`, `VIDEO_SW`, `PY_AI`, `PY_STATS`
- conditions: `NOMINAL`, `CACHE`, `TLB`, `BRANCH`, `MEMBW`, `ATOMIC`
- case ID: `WORKLOAD__CONDITION`
- total cases: `24`

## Recommended Apple Silicon Profile

The recommended collection profile is:

1. `Tier-0`
   - collect unprivileged operating-system telemetry at `5 Hz`
   - build a probe-based global schema
   - write `tier0_full_5hz.csv`
2. `Tier-1-alt`
   - collect `macmon` telemetry at `5 Hz`
   - fall back to `powermetrics` if a `macmon` run fails
   - write `tier1_alt_core_5hz.csv` and `tier1_alt_full_5hz.csv`
3. `Tier-2`
   - record `xctrace` Time Profiler traces
   - export raw trace data
   - parse trace buckets into `tier2_core_5hz.csv` and `tier2_full_5hz.csv`

The single-command entry point is:

```bash
python generate_dataset.py --phase recommended --duration_s 1000 --out_dir ./data
```

## Portable Profile

When release-parity tooling is not available, use:

```bash
python generate_dataset.py --phase portable --duration_s 1000 --out_dir ./data
```

Portable mode always runs `Tier-0` and then chooses the best supported higher-tier collectors on the current host.

## Validation Sequence

```bash
python tools/repair_itc_dataset.py --root ./data --tier1_mode alt
python tools/validate_itc_dataset.py --root ./data --tier1_mode alt --check_tier2
```

## Release Snapshot Export

The public `ITC_M2Pro_DATA` layout is a processed snapshot of the fuller collection tree. Export that layout with:

```bash
python tools/export_release_snapshot.py --root ./data --out_dir ./ITC_M2Pro_DATA_export --tier1_mode alt
```

Validate the stripped export with:

```bash
python tools/validate_itc_dataset.py --root ./ITC_M2Pro_DATA_export --tier1_mode alt --check_tier2 --processed_only
```
