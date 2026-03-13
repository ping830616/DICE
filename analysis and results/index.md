---
layout: default
title: Analysis and Results
---

# Analysis and Results

This public GitHub release is notebook-first for reproducing the paper-ready results from the released dataset.

The notebook below calls the same pinned Python pipeline used by the CLI wrapper, so you can run the same workflow on Linux servers, Windows, or macOS without relying on machine-specific local paths.

This portability applies to result regeneration from the released dataset. Raw Tier-1 and Tier-2 collection still depends on macOS Apple Silicon tooling (`macmon`, `powermetrics`, `xctrace`).

## Cross-Platform Environment

- Python: `3.11.4`
- Recommended for Linux/macOS/Windows: `analysis and results/environment.yml`
- Headless alternative: `analysis and results/requirements.txt`
- Default dataset root: `data generation/dataset/ITC_M2Pro_DATA/`

## Notebook Procedure

Recommended cross-platform setup with Conda or Mamba:

```bash
git clone https://github.com/ping830616/DICE.git
cd DICE/"analysis and results"
conda env create -f environment.yml
conda run -n dice-results jupyter lab dice_results_analysis.ipynb
```

If the environment already exists, refresh it with:

```bash
cd DICE/"analysis and results"
conda env update -f environment.yml --prune
conda run -n dice-results jupyter lab dice_results_analysis.ipynb
```

Alternative with `venv` + `pip`:

```bash
git clone https://github.com/ping830616/DICE.git
cd DICE/"analysis and results"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
jupyter lab dice_results_analysis.ipynb
```

On Windows PowerShell, activate the `venv` with `.venv\\Scripts\\Activate.ps1`.

If you want to point at a different dataset snapshot, pass `--root ../"data generation"/dataset/<DATASET_NAME>`.

## Conda Troubleshooting

If `conda activate dice-results` returns `EnvironmentNameNotFound`, the environment has not been created on that machine yet. Run `conda env create -f environment.yml` from `DICE/"analysis and results"` first.

If you are already inside another environment such as `.venv`, you can either `deactivate` before using Conda or skip activation entirely and run commands with `conda run -n dice-results ...`.

Run the notebook from top to bottom. The first execution cell resolves the repository location dynamically, and the pipeline cell regenerates:

- `results_analysis/`
- `results_dice_full/`
- `results_portable/run_manifest.json`

Optional notebook cells can also generate:

- `results_dice_full_holdout/`
- `results_dice_tuning/`

The notebook resolves repository paths dynamically and uses the same wrapper as the terminal flow, so it does not depend on `/Users/...` paths or macOS-only temp directories.

## Remote Linux Server

If you want to run the notebook on a remote Linux server:

```bash
git clone https://github.com/ping830616/DICE.git
cd DICE/"analysis and results"
conda env create -f environment.yml
conda run -n dice-results jupyter lab --no-browser --ip 0.0.0.0 --port 8888 dice_results_analysis.ipynb
```

Then connect through SSH port forwarding from your local machine and open the forwarded Jupyter URL in your browser.

## Optional CLI

The notebook is the primary public entry point. If you need a non-interactive run in CI or on a server, the same pipeline is available through:

```bash
cd DICE/"analysis and results"
conda run -n dice-results python tools/run_results_pipeline.py
```

## Optional Modes

Run workload-holdout evaluation too:

```bash
conda run -n dice-results python tools/run_results_pipeline.py \
  --run_holdout
```

Run the compact tuning sweep too:

```bash
conda run -n dice-results python tools/run_results_pipeline.py \
  --run_tuning
```

Run everything:

```bash
conda run -n dice-results python tools/run_results_pipeline.py \
  --run_holdout \
  --run_tuning
```

## Outputs

- `results_analysis/`
- `results_dice_full/`
- `results_dice_full_holdout/` when `--run_holdout` is used
- `results_dice_tuning/` when `--run_tuning` is used
- `results_portable/run_manifest.json`

## Reproducibility Controls

The notebook-backed pipeline enforces:

- single-threaded BLAS / OpenMP execution
- fixed `PYTHONHASHSEED=0`
- non-interactive matplotlib backend
- a dataset tree hash recorded in `results_portable/run_manifest.json`
- exact package versions from `analysis and results/requirements.txt` or `analysis and results/environment.yml`

To keep results consistent across machines and servers:

1. Use the committed dataset under `data generation/dataset/ITC_M2Pro_DATA/`.
2. Create or update the environment from the same `environment.yml`.
3. Run the notebook from top to bottom without changing the parameters.
4. Check `results_portable/run_manifest.json` and confirm the dataset hash and environment-file hashes match across runs.

This is designed for stable reproduction of the released results. It should be very close across machines, but exact byte-for-byte identity is not something I can honestly promise across every OS and linear algebra backend.
