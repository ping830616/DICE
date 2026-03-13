---
layout: default
title: Tier-2 Data
---

# Tier-2 (xctrace Telemetry)

## Purpose

Tier-2 adds trace-based evidence from Instruments (`xctrace`) for deeper runtime behavior.

## Source and Requirements

- Source: `xcrun xctrace`
- Collection helper: not shipped in the public notebook-first GitHub release
- Requires Xcode and accepted Xcode license.

Preflight check:

```bash
xcrun xctrace version
xcrun xctrace list templates | rg "Time Profiler"
```

## Outputs

Per case:
- `xctrace.trace`
- `xctrace_export.xml`
- `tier2_core_5hz.csv`
- `tier2_full_5hz.csv`

Global:
- `tier2_schema_global.json`
- `manifest_tier2.csv`

## Tier-2 Core Fields

Current release schema (example):

- `samples_per_bucket`
- `unique_process_count`
- `unique_thread_count`
- `avg_core_id`
- `max_core_id`
- `total_weight_ns`
- `avg_weight_ns`
- `running_fraction`
- `sentinel_count`

Legacy parser versions may emit a CPU/memory/IO-oriented core schema (`cpu_usage_pct`, `cpu_time_ms`, `thread_count`, etc.).

## Command

Raw Tier-2 collection is not the primary public workflow in this repository. To reproduce the published results, use `analysis and results/dice_results_analysis.ipynb` against the released dataset.

## Notes

- Tier-2 quality depends on trace export content and template behavior on the local machine.
- If a case fails, rerun it using `tools/rerun_cases.py` and validate again.
