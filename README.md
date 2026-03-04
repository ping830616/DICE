# DICE ITC Data Generation (macOS)

DICE provides an end-to-end pipeline to generate case-aligned telemetry data for the DICE paper across:

- `Tier-0`: OS telemetry (`psutil`) with probe-based low-NaN global schema.
- `Tier-1`: `powermetrics` telemetry with global full schema and dense core features.
- `Tier-2`: `xctrace` telemetry export and parsing into core/full CSV outputs.

## GitHub Pages Documentation

For the full Tier-0 to Tier-2 methodology and publish guide:

- Local docs entry: [docs/index.md](docs/index.md)
- Target site URL: `https://ping830616.github.io/DICE/`

Core narrative pages:

- [docs/data-description.md](docs/data-description.md)
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

Tier-0 + Tier-1 baseline:

```bash
python generate_dataset.py --phase both --duration_s 1000 --out_dir ./data
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
# Validate Tier-0 + Tier-1
python tools/validate_itc_dataset.py --root ./data

# Validate including Tier-2
python tools/validate_itc_dataset.py --root ./data --check_tier2

# Rebuild manifests
python tools/repair_itc_dataset.py --root ./data

# Rerun selected cases
python tools/rerun_cases.py --phase tier1 --duration_s 1000 --out_dir ./data --scripts_dir ./scripts --cases BROWSER__CACHE PY_AI__TLB
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
    tier2_xctrace_parse.py
    run_itc_two_phase.py
  tools/
    validate_itc_dataset.py
    repair_itc_dataset.py
    rerun_cases.py
    clean_tier1_core.py
```
