# DICE ITC Data Generation (macOS)

DICE provides an end-to-end pipeline to generate case-aligned telemetry data for the DICE paper across:

- `Tier-0`: OS telemetry (`psutil`) with probe-based low-NaN global schema.
- `Tier-1-alt` (recommended): Apple Silicon Tier-1 replacement using `macmon` with automatic `powermetrics` fallback.
- `Tier-1` (legacy): direct `powermetrics` telemetry with global full schema and dense core features.
- `Tier-2`: `xctrace` telemetry export and parsing into core/full CSV outputs.

This public GitHub release is focused on the released dataset plus portable notebook-based results reproduction. The low-level Tier-1/Tier-2 shell collectors are not shipped in this repo.

In practice, that means:

- `Tier-0`: public collection path is included
- `Tier-1-alt` (`macmon`): public collection path is included
- legacy `Tier-1` (`powermetrics` shell helper): documented, but not fully collectable from GitHub alone
- `Tier-2` (`xctrace` shell helper): documented, but not fully collectable from GitHub alone

## Start Here

1. Read the dataset narrative and assumptions: [docs/data-description.md](docs/data-description.md)
2. Check the current release status and known platform limits: [docs/current-dataset-status.md](docs/current-dataset-status.md)
3. Review the machine-specific constraints and portability notes: [docs/hardware-compatibility.md](docs/hardware-compatibility.md)
4. For notebook-first analysis and results, switch to the root [README.md](../README.md), [dice_results_analysis.ipynb](../dice_results_analysis.ipynb), and [portable-setup.md](../portable-setup.md)
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
- [../portable-setup.md](../portable-setup.md)
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

For reproducible notebook-first regeneration of the released results dataset, use the root-level notebook and setup files in this repository.

The raw Tier-1/Tier-2 collection helpers used for local macOS capture are intentionally not published in this GitHub release.

At the default `duration_s=1000` and `24` cases, the nominal collection window is:

- `Tier-0`: about `6 h 40 m` total, plus about `10 s` once for the initial schema probe
- `Tier-1-alt`: about `6 h 40 m` total, plus parsing overhead
- legacy `Tier-1`: about `6 h 40 m` total, plus parsing and `sudo` startup overhead
- `Tier-2`: about `6 h 40 m` total, plus trace-export overhead

`generate_dataset.py` now prints per-case elapsed time, tier elapsed time, and estimated remaining time while a collection run is in progress.

## MacBook Pro Collection Instructions

If you want to collect fresh DICE telemetry on your own MacBook Pro, use this as the practical public-GitHub path.

### 1. Open a terminal in the data-generation folder

```bash
cd /absolute/path/to/DICE/data\ generation
```

### 2. Create and activate the data-generation environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Optional for the `PY_AI` workload behavior:

```bash
pip install torch
```

### 3. Install the recommended Tier-1 collector

The recommended Apple Silicon Tier-1 source is `macmon`.

Check that it is available:

```bash
macmon --help
```

If that command is not found, install `macmon` first and make sure it is on your shell `PATH`.

### 4. Choose an output folder for your collected dataset

Example:

```bash
OUT="$PWD/dataset/MY_MBP_DICE_DATA"
mkdir -p "$OUT"
```

### 5. Collect Tier-0

```bash
python generate_dataset.py --phase tier0 --duration_s 1000 --out_dir "$OUT"
```

This is the host-visible telemetry layer and is fully collectable from the public repo.

### 6. Collect the recommended Tier-1-alt on Apple Silicon

```bash
python generate_dataset.py --phase tier1_alt --duration_s 1000 --out_dir "$OUT" --tier1_alt_bin macmon
```

This is the recommended Apple Silicon power/usage/thermal proxy tier and is fully collectable from the public repo.

### 7. Tier-2 status

Tier-2 is documented, and the parser is included, but the low-level raw collection helper used to record/export `xctrace` traces is not shipped in the public GitHub release.

So:

- if you only have the public GitHub repo, stop after `tier0` and `tier1_alt`
- if you also have your private/local Tier-2 collector helper restored, then you can run:

```bash
xcrun xctrace version
xcrun xctrace list templates | rg "Time Profiler"
python generate_dataset.py --phase tier2 --duration_s 1000 --out_dir "$OUT" --tier2_template "Time Profiler"
```

### 8. Validate what you collected

For the recommended MacBook Pro profile:

```bash
python tools/repair_itc_dataset.py --root "$OUT" --tier1_mode alt
python tools/validate_itc_dataset.py --root "$OUT" --tier1_mode alt --check_tier2
```

If you did not collect Tier-2, validate without `--check_tier2`:

```bash
python tools/validate_itc_dataset.py --root "$OUT" --tier1_mode alt
```

### 9. Understand the time you will spend

At the default `duration_s=1000` and `24` cases:

- `Tier-0`: about `6 h 40 m`
- `Tier-1-alt`: about `6 h 40 m`
- `Tier-2`: about `6 h 40 m` plus trace export overhead

The collector now prints:

- which case is running
- how long that case took
- how much time the whole tier has taken so far
- the estimated remaining time

### 10. Important command note

Do not use `--phase all` if your goal is the current recommended Apple Silicon dataset profile.

In the current code:

- `--phase all` = `tier0 + legacy tier1 + tier2`
- it does **not** include the recommended `tier1_alt`

For your MacBook Pro, the practical public-repo sequence is:

```bash
python generate_dataset.py --phase tier0 --duration_s 1000 --out_dir "$OUT"
python generate_dataset.py --phase tier1_alt --duration_s 1000 --out_dir "$OUT" --tier1_alt_bin macmon
```

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
