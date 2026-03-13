# DICE ITC Data Generation (macOS)

DICE provides an end-to-end pipeline to generate case-aligned telemetry data for the DICE paper across:

- `Tier-0`: OS telemetry (`psutil`) with probe-based low-NaN global schema.
- `Tier-1-alt` (recommended): Apple Silicon Tier-1 replacement using `macmon` with automatic `powermetrics` fallback.
- `Tier-1` (legacy): direct `powermetrics` telemetry with global full schema and dense core features.
- `Tier-2`: `xctrace` telemetry export and parsing into core/full CSV outputs.

This public GitHub release is focused on the released dataset plus portable notebook-based results reproduction. The low-level Tier-1/Tier-2 shell collectors are not shipped in this repo.

## Start Here

1. Read the dataset narrative and assumptions: [docs/data-description.md](docs/data-description.md)
2. Check the current release status and known platform limits: [docs/current-dataset-status.md](docs/current-dataset-status.md)
3. Review the machine-specific constraints and portability notes: [docs/hardware-compatibility.md](docs/hardware-compatibility.md)
4. For notebook-first analysis and results, switch to [../analysis and results/README.md](../analysis%20and%20results/README.md)
5. Follow the runbook for full collection and validation: [docs/end-to-end.md](docs/end-to-end.md)
6. Use the legacy clean feature-map reference if you need a harmonized column description: [docs/dataset-feature-map-clean-tier1-consistent.md](docs/dataset-feature-map-clean-tier1-consistent.md)

## GitHub Pages Documentation

For the full Tier-0 to Tier-2 methodology and publish guide:

- Local docs entry: [docs/index.md](docs/index.md)
- Target site URL: `https://ping830616.github.io/DICE/`

Core narrative pages:

- [docs/data-description.md](docs/data-description.md)
- [docs/current-dataset-status.md](docs/current-dataset-status.md)
- [docs/hardware-compatibility.md](docs/hardware-compatibility.md)
- [../analysis and results/index.md](../analysis%20and%20results/index.md)
- [docs/dataset-feature-map-clean-tier1-consistent.md](docs/dataset-feature-map-clean-tier1-consistent.md)
- [docs/end-to-end.md](docs/end-to-end.md)
- [docs/feature-dictionary.md](docs/feature-dictionary.md)
- [docs/methodology.md](docs/methodology.md)
- [docs/tier0.md](docs/tier0.md)
- [docs/tier1.md](docs/tier1.md)
- [docs/tier2.md](docs/tier2.md)

## Dataset Release

Current dataset snapshot stored in this repository:

- `dataset/ITC_M2Pro_DATA/`
- Coverage report: `dataset/ITC_M2Pro_DATA/no_nan_report.json`
- Legacy clean-schema reference doc: `docs/dataset-feature-map-clean-tier1-consistent.md`

## Quick Start

All commands below assume your current working directory is `DICE/"data generation"`.

```bash
cd DICE/"data generation"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

For reproducible notebook-first regeneration of the released results dataset, use the sibling [`analysis and results`](../analysis%20and%20results/README.md) folder.

The raw Tier-1/Tier-2 collection helpers used for local macOS capture are intentionally not published in this GitHub release.

## Validate and Inspect Existing Data

```bash
# Validate legacy Tier-0 + Tier-1 profile
python tools/validate_itc_dataset.py --root ./data --tier1_mode powermetrics

# Validate recommended Tier-0 + Tier-1-alt + Tier-2 profile
python tools/validate_itc_dataset.py --root ./data --tier1_mode alt --check_tier2

# Validate both Tier-1 sources + Tier-2
python tools/validate_itc_dataset.py --root ./data --tier1_mode both --check_tier2

# Rebuild manifests
python tools/repair_itc_dataset.py --root ./data --tier1_mode alt

# Build a model-ready NaN-free copy (keeps only globally supported features)
python tools/ensure_no_nan_dataset.py --root ./data --tier1_mode alt --out_dir ./data_clean_no_nan --min_coverage_ratio 0.95

# Probe Tier-1 temperature support before long captures
python tools/probe_tier1_temperature.py --samples 3 --interval_ms 1000 --out_raw ./data/tier1_temp_probe.txt

```

## Repository Layout

```text
DICE/
  _config.yml
  README.md
  index.md
  data generation/
    generate_dataset.py
    docs/
      index.md
      hardware-compatibility.md
      methodology.md
      workloads-anomalies.md
      tier0.md
      tier1.md
      tier2.md
      validation.md
      publish.md
    src/dice/
      cfg.py
      workloads.py
      tier0_collect_schema.py
      powermetrics_parse_full.py
      tier1_alt_macmon.py
      tier2_xctrace_parse.py
      run_itc_two_phase.py
    tools/
      validate_itc_dataset.py
      repair_itc_dataset.py
      rerun_cases.py
      clean_tier1_core.py
      ensure_no_nan_dataset.py
      probe_tier1_temperature.py
```
