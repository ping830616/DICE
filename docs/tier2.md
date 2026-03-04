---
layout: default
title: Tier-2 Data
---

# Tier-2 (xctrace Telemetry)

## Purpose

Tier-2 adds trace-based signals from Instruments (`xctrace`) for deeper runtime behavior.

## Source and Requirements

- Source: `xcrun xctrace`
- Collection script: `scripts/05_xctrace_record_export.sh`
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

- `cpu_usage_pct`
- `cpu_time_ms`
- `thread_count`
- `wakeups_per_s`
- `context_switches_per_s`
- `page_faults_per_s`
- `phys_mem_bytes`
- `virt_mem_bytes`
- `io_read_Bps`
- `io_write_Bps`
- `energy_impact`

## Command

```bash
python generate_dataset.py --phase tier2 --duration_s 1000 --out_dir ./data --tier2_template "Time Profiler"
```

## Notes

- Tier-2 quality depends on trace export content and template behavior on the local machine.
- If a case fails, rerun it using `tools/rerun_cases.py` and validate again.
