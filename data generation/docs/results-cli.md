---
layout: default
title: Terminal Results Pipeline
---

# Terminal Results Pipeline

This repository no longer requires Jupyter to regenerate the paper-ready results.

Use the terminal wrapper below to run the analysis, the full DICE retrain/evaluation pipeline, and the optional tuning sweep in a reproducible way.

This portability applies to result regeneration from the released dataset. Raw Tier-1 and Tier-2 collection still depends on macOS Apple Silicon tooling (`macmon`, `powermetrics`, `xctrace`).

## Tested Setup

- Python: `3.11.4`
- Install from: `requirements.txt`
- Dataset root: `dataset/ITC_M2Pro_DATA/`

## Clone and Run

```bash
git clone https://github.com/ping830616/DICE.git
cd DICE/"data generation"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-results.lock.txt
python tools/run_results_pipeline.py --root dataset/ITC_M2Pro_DATA
```

If you only need the minimal runtime dependencies for the broader data-generation repo, `requirements.txt` remains available. Use `requirements-results.lock.txt` when you want the closest match to the tested results environment.

## Optional Modes

Run workload-holdout evaluation too:

```bash
python tools/run_results_pipeline.py \
  --root dataset/ITC_M2Pro_DATA \
  --run_holdout
```

Run the compact tuning sweep too:

```bash
python tools/run_results_pipeline.py \
  --root dataset/ITC_M2Pro_DATA \
  --run_tuning
```

Run everything:

```bash
python tools/run_results_pipeline.py \
  --root dataset/ITC_M2Pro_DATA \
  --run_holdout \
  --run_tuning
```

## Outputs

The wrapper writes:

- `results_analysis/`
- `results_dice_full/`
- `results_dice_full_holdout/` when `--run_holdout` is used
- `results_dice_tuning/` when `--run_tuning` is used
- `results_portable/run_manifest.json`

## Reproducibility Controls

The wrapper enforces:

- single-threaded BLAS / OpenMP execution
- fixed `PYTHONHASHSEED=0`
- non-interactive matplotlib backend
- a dataset tree hash recorded in `results_portable/run_manifest.json`
- exact package versions from `requirements-results.lock.txt`

For cross-machine consistency, use the same Python version, the same pinned dependencies, and the same dataset tree hash.
