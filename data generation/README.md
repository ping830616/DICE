# DICE ITC Data Generation (macOS)

DICE provides an end-to-end pipeline for generating the telemetry dataset used in the DICE paper across three observability tiers:

- `Tier-0`: unprivileged operating-system telemetry collected through `psutil`
- `Tier-1-alt` (recommended on Apple Silicon): `macmon` telemetry with automatic `powermetrics` fallback when collection fails at runtime
- `Tier-1` (legacy): direct `powermetrics` telemetry
- `Tier-2`: profiler-derived runtime evidence collected through `xcrun xctrace` and parsed into case-aligned CSV files

The repository now supports the public Apple Silicon collection procedure directly from Python. A fresh full collection produces raw artifacts, processed CSVs, schemas, manifests, metadata, and logs. The released `dataset/ITC_M2Pro_DATA/` folder is a stripped processed snapshot of that fuller collection tree.

## Start Here

1. Read the dataset narrative and assumptions: [docs/data-description.md](docs/data-description.md)
2. Check the current release status and known platform limits: [docs/current-dataset-status.md](docs/current-dataset-status.md)
3. Review machine-specific constraints and portability notes: [docs/hardware-compatibility.md](docs/hardware-compatibility.md)
4. Follow the practical collection runbook: [docs/end-to-end.md](docs/end-to-end.md)
5. Review the collection methodology used for the ITC dataset: [docs/ITC_COLLECTION_METHODOLOGY.md](docs/ITC_COLLECTION_METHODOLOGY.md)
6. Use the feature references if you need harmonized column descriptions: [docs/feature-dictionary.md](docs/feature-dictionary.md) and [docs/dataset-feature-map-clean-tier1-consistent.md](docs/dataset-feature-map-clean-tier1-consistent.md)

## Dataset Release

This repository includes the released processed snapshot:

- `dataset/ITC_M2Pro_DATA/`
- coverage report: `dataset/ITC_M2Pro_DATA/no_nan_report.json`

That folder is not a full raw collection tree. It contains the processed tier outputs used by the released experiments. A fresh collection run writes additional raw artifacts, logs, manifests, schemas, and metadata under the output root.

## Quick Start

All commands below assume your working directory is `DICE/"data generation"`.

```bash
cd DICE/"data generation"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Optional dependency for the `PY_AI` workload:

```bash
pip install torch
```

## Collection Profiles

### Recommended Apple Silicon Profile

`generate_dataset.py` now defaults to:

```bash
python generate_dataset.py --phase recommended --duration_s 1000 --out_dir ./data
```

This profile runs:

- `Tier-0`
- `Tier-1-alt`
- `Tier-2`

It is the closest public match to the procedure behind the released `ITC_M2Pro_DATA` snapshot. It requires:

- macOS
- `powermetrics`
- `macmon`
- Xcode tooling with a working `xcrun xctrace`

### Portable Profile

If you want the repo to collect the best supported data on the current machine, use:

```bash
python generate_dataset.py --phase portable --duration_s 1000 --out_dir ./data
```

Portable mode behaves as follows:

- always runs `Tier-0`
- prefers `Tier-1-alt` when `macmon` is available
- falls back to legacy `Tier-1` when `powermetrics` is available but `macmon` is not
- runs `Tier-2` only when `xctrace` is available and licensed
- skips unsupported tiers cleanly with an explicit message

This makes the workflow portable across different hosts, but it does not guarantee identical schemas or identical tier availability on every machine.

### Legacy Compatibility Profiles

- `--phase both` = `tier0 + tier1`
- `--phase all` = `tier0 + tier1 + tier2`

These legacy modes are still available for compatibility, but they do not match the current Apple Silicon release profile because they use legacy `Tier-1` instead of `Tier-1-alt`.

## Practical Apple Silicon Workflow

### 1. Check the required tools

```bash
macmon --help
powermetrics --help
xcrun xctrace version
```

### 2. Choose an output folder

```bash
OUT="$PWD/data"
mkdir -p "$OUT"
```

### 3. Run the recommended public collection path

```bash
python generate_dataset.py --phase recommended --duration_s 1000 --out_dir "$OUT" --tier1_alt_bin macmon --tier2_template "Time Profiler"
```

If you prefer to run the tiers separately:

```bash
python generate_dataset.py --phase tier0 --duration_s 1000 --out_dir "$OUT"
python generate_dataset.py --phase tier1_alt --duration_s 1000 --out_dir "$OUT" --tier1_alt_bin macmon
python generate_dataset.py --phase tier2 --duration_s 1000 --out_dir "$OUT" --tier2_template "Time Profiler"
```

### 4. Validate the full collection tree

```bash
python tools/repair_itc_dataset.py --root "$OUT" --tier1_mode alt
python tools/validate_itc_dataset.py --root "$OUT" --tier1_mode alt --check_tier2
```

## Matching the Released `ITC_M2Pro_DATA` Snapshot

The released snapshot is a processed export of the fuller collection tree. After collecting data into a full output directory, create a matching stripped snapshot with:

```bash
python tools/export_release_snapshot.py --root "$OUT" --out_dir ./ITC_M2Pro_DATA_export --tier1_mode alt
```

This export keeps the processed tier CSV files and regenerates `no_nan_report.json` for the exported snapshot.

To validate a processed snapshot that does not include raw artifacts, manifests, or schema files, use:

```bash
python tools/validate_itc_dataset.py --root ./ITC_M2Pro_DATA_export --tier1_mode alt --check_tier2 --processed_only
```

## Timing

At the default `duration_s=1000` and `24` cases, the nominal collection window is:

- `Tier-0`: about `6 h 40 m`, plus about `10 s` once for the initial schema probe
- `Tier-1-alt`: about `6 h 40 m`, plus parsing overhead
- `Tier-1`: about `6 h 40 m`, plus parsing and `sudo` startup overhead
- `Tier-2`: about `6 h 40 m`, plus trace-export overhead

On the reference Apple Silicon collection tree used for the released dataset, the observed wall-clock times were approximately:

- `Tier-0`: `7 h 11 m`
- `Tier-1-alt`: `8 h 02 m`
- `Tier-2`: `9 h 31 m`

During collection, `generate_dataset.py` prints:

- the current case ID
- the elapsed time for that case
- the elapsed time for the current tier
- the estimated remaining time

## Validate and Inspect Existing Data

```bash
# Validate a full legacy Tier-0 + Tier-1 tree
python tools/validate_itc_dataset.py --root ./data --tier1_mode powermetrics

# Validate a full recommended Tier-0 + Tier-1-alt + Tier-2 tree
python tools/validate_itc_dataset.py --root ./data --tier1_mode alt --check_tier2

# Validate a processed public snapshot
python tools/validate_itc_dataset.py --root ./dataset/ITC_M2Pro_DATA --tier1_mode alt --check_tier2 --processed_only

# Rebuild manifests after reruns
python tools/repair_itc_dataset.py --root ./data --tier1_mode alt

# Build a model-ready NaN-free copy
python tools/ensure_no_nan_dataset.py --root ./data --tier1_mode alt --out_dir ./data_clean_no_nan --min_coverage_ratio 0.95

# Probe Tier-1 temperature support before long captures
python tools/probe_tier1_temperature.py --samples 3 --interval_ms 1000 --out_raw ./data/tier1_temp_probe.txt
```

## Repository Layout

```text
DICE/
  README.md
  data generation/
    generate_dataset.py
    docs/
      end-to-end.md
      hardware-compatibility.md
      methodology.md
      tier0.md
      tier1.md
      tier2.md
      ITC_COLLECTION_METHODOLOGY.md
    src/dice/
      cfg.py
      macos_collectors.py
      workloads.py
      tier0_collect_schema.py
      powermetrics_parse_full.py
      tier1_alt_macmon.py
      tier2_xctrace_parse.py
      run_itc_two_phase.py
    tools/
      export_release_snapshot.py
      validate_itc_dataset.py
      repair_itc_dataset.py
      rerun_cases.py
      ensure_no_nan_dataset.py
      probe_tier1_temperature.py
```
