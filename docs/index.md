---
layout: default
title: DICE Dataset Home
---

# DICE Dataset Generation (Tier-0 to Tier-2)

This site documents the end-to-end data generation pipeline used in the DICE paper.

The documentation is organized so that readers can start with the dataset narrative, then move to the execution methodology, feature-level tier details, and operational validation steps.

## Scope

- Platform: macOS (Apple Silicon recommended)
- Cases: `4 workloads x 6 stressors = 24` (`WORKLOAD__STRESSOR`)
- Sampling: `5 Hz`
- Standard duration: `1000 s` (`5000 rows`, `5001 lines` including header)

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

## Documentation Map

- [Data Description](data-description.md)
- [End-to-End User Guide](end-to-end.md)
- [Feature Dictionary](feature-dictionary.md)
- [Methodology](methodology.md)
- [Workloads and Anomalies](workloads-anomalies.md)
- [Tier-0 Data](tier0.md)
- [Tier-1 Data](tier1.md)
- [Tier-2 Data](tier2.md)
- [Validation and Repair](validation.md)
- [Publish on GitHub Pages](publish.md)
