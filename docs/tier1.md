---
layout: default
title: Tier-1 Data
---

# Tier-1 (powermetrics Telemetry)

## Purpose

Tier-1 captures power/frequency-oriented telemetry from `powermetrics` and normalizes it into case-aligned CSV files.

## Source and Sampling

- Source: `powermetrics`
- Collection: `scripts/03_powermetrics_collect_5hz.sh`
- Rate: `5 Hz` (`-i 200`)
- Duration: typically `1000 s`

## Outputs

Per case:
- `powermetrics_raw.txt`
- `tier1_core_5hz.csv`
- `tier1_full_5hz.csv`

Global:
- `tier1_schema_global.json`
- `manifest_tier1.csv`

## Tier-1 Core Fields

- `cpu_power_w`
- `gpu_power_w`
- `ane_power_w`
- `package_power_w`
- `soc_power_w`
- `processor_power_w`
- `cpu_avg_freq_mhz`
- `cpu_avg_freq_ghz`
- `gpu_avg_freq_mhz`
- `gpu_avg_freq_ghz`
- `interrupts_per_s`
- `wakeups_per_s`
- `timer_wakeups_per_s`
- `thermal_level`
- `thermal_pressure`

## Command

```bash
python generate_dataset.py --phase tier1 --duration_s 1000 --out_dir ./data
```
