# DICE ITC Data Generation (macOS)

DICE provides an end-to-end pipeline to generate case-aligned telemetry data for the DICE paper across:

- `Tier-0`: OS telemetry (`psutil`) with probe-based low-NaN global schema.
- `Tier-1-alt` (recommended): Apple Silicon Tier-1 replacement using `macmon` with automatic `powermetrics` fallback.
- `Tier-1` (legacy): direct `powermetrics` telemetry with global full schema and dense core features.
- `Tier-2`: `xctrace` telemetry export and parsing into core/full CSV outputs.

## GitHub Pages Documentation

For the full Tier-0 to Tier-2 methodology and publish guide:

- Local docs entry: [docs/index.md](docs/index.md)
- Target site URL: `https://ping830616.github.io/DICE/`

Core narrative pages:

- [docs/data-description.md](docs/data-description.md)
- [docs/current-dataset-status.md](docs/current-dataset-status.md)
- [docs/end-to-end.md](docs/end-to-end.md)
- [docs/feature-dictionary.md](docs/feature-dictionary.md)
- [docs/methodology.md](docs/methodology.md)
- [docs/tier0.md](docs/tier0.md)
- [docs/tier1.md](docs/tier1.md)
- [docs/tier2.md](docs/tier2.md)

## Quick Start

```bash
cd DICE
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Recommended publication profile (`tier0 + tier1_alt + tier2`):

```bash
python generate_dataset.py --phase tier0 --duration_s 1000 --out_dir ./data
python generate_dataset.py --phase tier1_alt --duration_s 1000 --out_dir ./data --tier1_alt_bin macmon
python generate_dataset.py --phase tier2 --duration_s 1000 --out_dir ./data --tier2_template "Time Profiler"
```

Legacy Tier-0 + Tier-1 baseline:

```bash
python generate_dataset.py --phase both --duration_s 1000 --out_dir ./data
```

Tier-1 alternative on Apple Silicon using `macmon`:

```bash
python generate_dataset.py --phase tier1_alt --duration_s 1000 --out_dir ./data --tier1_alt_bin macmon
```

Tier-2 only:

```bash
python generate_dataset.py --phase tier2 --duration_s 1000 --out_dir ./data --tier2_template "Time Profiler"
```

All tiers:

```bash
python generate_dataset.py --phase all --duration_s 1000 --out_dir ./data --tier2_template "Time Profiler"
```

## Validate, Repair, Rerun

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

# Rerun selected cases
python tools/rerun_cases.py --phase tier1 --duration_s 1000 --out_dir ./data --scripts_dir ./scripts --cases BROWSER__CACHE PY_AI__TLB
python tools/rerun_cases.py --phase tier1_alt --duration_s 1000 --out_dir ./data --cases BROWSER__CACHE PY_AI__TLB --tier1_alt_bin macmon
python tools/rerun_cases.py --phase tier2 --duration_s 1000 --out_dir ./data --scripts_dir ./scripts --tier2_template "Time Profiler" --cases BROWSER__CACHE PY_AI__TLB
```

## Repository Layout

```text
DICE/
  _config.yml
  generate_dataset.py
  docs/
    index.md
    methodology.md
    workloads-anomalies.md
    tier0.md
    tier1.md
    tier2.md
    validation.md
    publish.md
  scripts/
    03_powermetrics_collect_5hz.sh
    05_xctrace_record_export.sh
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
