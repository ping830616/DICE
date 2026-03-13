---
layout: default
title: Tier-1 Data
---

# Tier-1 Sources (Tier-1-alt Recommended)

## Purpose

Tier-1 captures power/frequency-oriented telemetry and normalizes it into case-aligned CSV files.
For this Apple Silicon dataset release, `tier1_alt` is the recommended Tier-1 source.

## Source and Sampling

- Source: `powermetrics`
- Collection helper: not shipped in the public notebook-first GitHub release
- Rate: `5 Hz` (`-i 200`)
- Duration: typically `1000 s`
- Temperature extension: collector first tries `--show-extra-power-info` to expose additional sensor keys when available

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
- `cpu_temp_c` (optional, appears when `powermetrics` exports CPU temperature)
- `soc_temp_c` (optional, appears when `powermetrics` exports SoC temperature)
- `interrupts_per_s`
- `wakeups_per_s`
- `timer_wakeups_per_s`
- `thermal_level`
- `thermal_pressure`

Thermal pressure is encoded numerically:

- `Nominal=0`
- `Fair=1`
- `Serious=2`
- `Critical=3`

## Probe Temperature Support

Before long runs, you can check whether numeric temperatures are exposed on your host:

```bash
python tools/probe_tier1_temperature.py --samples 3 --interval_ms 1000 --out_raw ./data/tier1_temp_probe.txt
```

If no numeric temperature keys are reported, Tier-1 still captures thermal pressure state.

## Command

Raw Tier-1 collection is not the primary public workflow in this repository. To reproduce the published results, use `analysis and results/dice_results_analysis.ipynb` against the released dataset.

## Recommended Tier-1 for This Apple Dataset (`tier1_alt`)

For this Apple Silicon workflow, run:

```bash
python generate_dataset.py --phase tier1_alt --duration_s 1000 --out_dir ./data --tier1_alt_bin macmon
```

Prerequisite:

- `macmon` must be installed and available in your shell `PATH`.

Outputs per case:

- `tier1_alt/<CASE_ID>/macmon_raw.jsonl`
- `tier1_alt/<CASE_ID>/tier1_alt_core_5hz.csv`
- `tier1_alt/<CASE_ID>/tier1_alt_full_5hz.csv`

Global outputs:

- `tier1_alt_schema_global.json`
- `manifest_tier1_alt.csv`

Practical note for macOS laptop collection:

- `soc_temp_c` and `fan_rpm` may remain unavailable depending on the machine and exposed sensors.
- Frequency and residency fields can be sparse when fallback telemetry is used.
- Power and usage fields are typically the most reliable Tier-1-alt signals.

## Recovery Pipeline (If Tier-1 Raw Files Are Empty)

Those raw-collection recovery steps depended on local shell collectors that are no longer published in this repository.

## Verify Tier-1-alt Signal Coverage (Power/Usage/Temperature)

```bash
python3 - <<'PY'
import pandas as pd
from pathlib import Path

root = Path('/Users/hsiaopingni/ITC_2026_M2Pro_DATA/tier1_alt')
sample_case = sorted([p for p in root.iterdir() if p.is_dir()])[0].name
core = pd.read_csv(root / sample_case / 'tier1_alt_core_5hz.csv')
full = pd.read_csv(root / sample_case / 'tier1_alt_full_5hz.csv')

print('sample_case:', sample_case)

power_cols = [c for c in core.columns if 'power' in c]
usage_cols = [c for c in core.columns if 'usage' in c]
temp_cols = [c for c in core.columns if 'temp' in c]
res_cols_full = [c for c in full.columns if 'residency' in c]
freq_cols_full = [c for c in full.columns if 'frequency' in c]

print('core power cols:', power_cols)
print('core usage cols:', usage_cols)
print('core temp cols:', temp_cols)
print('full residency cols (count):', len(res_cols_full))
print('full frequency cols (count):', len(freq_cols_full))
PY
```
