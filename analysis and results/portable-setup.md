---
layout: default
title: Portable Jupyter Setup
---

# Portable Jupyter Setup

This page describes the recommended way to run the DICE analysis notebook across Linux, Windows, macOS, and remote servers.

## Primary Entry Point

Open:

- `analysis and results/dice_results_analysis.ipynb`

Use this environment:

- `analysis and results/environment.yml`

The notebook resolves repository paths dynamically and calls the same pinned Python pipeline used by the CLI wrapper, so it does not depend on machine-specific local paths.

## Local Machine Procedure

```bash
git clone https://github.com/ping830616/DICE.git
cd DICE/"analysis and results"
conda env create -f environment.yml
conda run -n dice-results jupyter lab dice_results_analysis.ipynb
```

If the environment already exists:

```bash
cd DICE/"analysis and results"
conda env update -f environment.yml --prune
conda run -n dice-results jupyter lab dice_results_analysis.ipynb
```

Run the notebook from top to bottom.

## Remote Linux Server

On the server:

```bash
git clone https://github.com/ping830616/DICE.git
cd DICE/"analysis and results"
conda env create -f environment.yml
conda run -n dice-results jupyter lab --no-browser --ip 0.0.0.0 --port 8888 dice_results_analysis.ipynb
```

From your local machine, forward the port:

```bash
ssh -L 8888:localhost:8888 <user>@<server>
```

Then open the Jupyter URL shown by the server command in your local browser.

## Windows and `venv`

Conda is the recommended cross-platform path. If you prefer `venv`:

```bash
git clone https://github.com/ping830616/DICE.git
cd DICE/"analysis and results"
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
jupyter lab dice_results_analysis.ipynb
```

## What the Notebook Generates

- `results_analysis/`
- `results_dice_full/`
- `results_portable/run_manifest.json`

Optional cells can also generate:

- `results_dice_full_holdout/`
- `results_dice_tuning/`

## Reproducibility Checklist

To keep results consistent across machines and servers:

1. Use the committed dataset under `data generation/dataset/ITC_M2Pro_DATA/`.
2. Use the same `environment.yml` or `requirements.txt`.
3. Run the notebook from top to bottom without changing parameters.
4. Compare `results_portable/run_manifest.json` across runs and confirm the dataset hash and environment-file hashes match.

This is designed for stable reproduction of the released results. It should be very close across machines, but exact byte-for-byte identity is not guaranteed across every OS and linear algebra backend.
