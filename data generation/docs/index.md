---
layout: default
title: DICE Dataset Home
---

# DICE Dataset Generation (Tier-0 to Tier-2)

This site documents the end-to-end data generation pipeline used in the DICE paper.

The documentation is organized so that readers can start with the dataset narrative, then move to the execution methodology, feature-level tier details, and operational validation steps.

## Start Here

1. Read [Data Description](data-description.md) for scope, workloads, anomalies, and evaluation framing.
2. Check [Current Dataset Status](current-dataset-status.md) for what is fully exposed by this Mac.
3. Read [Hardware and Compatibility](hardware-compatibility.md) for the machine profile behind this release and what ports cleanly to other systems.
4. Use [../../analysis and results/index.md](../../analysis%20and%20results/index.md) to regenerate figures and tables without Jupyter.
5. Open [Dataset Feature Map (Clean Tier1 Consistent)](dataset-feature-map-clean-tier1-consistent.md) for the legacy harmonized-column reference.
6. Run collection with [End-to-End User Guide](end-to-end.md).

## Scope

- Platform: macOS (Apple Silicon recommended)
- Cases: `4 workloads x 6 stressors = 24` (`WORKLOAD__STRESSOR`)
- Sampling: `5 Hz`
- Standard duration: `1000 s` (`5000 rows`, `5001 lines` including header)

## Quick Start

All commands below assume your current working directory is `DICE/"data generation"`.

```bash
cd DICE/"data generation"
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

Tier-1 alternative (`macmon`) only:

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

## Documentation Map

- [Data Description](data-description.md)
- [Current Dataset Status](current-dataset-status.md)
- [Hardware and Compatibility](hardware-compatibility.md)
- [Analysis and Results](../../analysis%20and%20results/index.md)
- [Dataset Feature Map (Clean Tier1 Consistent)](dataset-feature-map-clean-tier1-consistent.md)
- [End-to-End User Guide](end-to-end.md)
- [Feature Dictionary](feature-dictionary.md)
- [Methodology](methodology.md)
- [Workloads and Anomalies](workloads-anomalies.md)
- [Tier-0 Data](tier0.md)
- [Tier-1 Data](tier1.md)
- [Tier-2 Data](tier2.md)
- [Validation and Repair](validation.md)
- [Publish on GitHub Pages](publish.md)
