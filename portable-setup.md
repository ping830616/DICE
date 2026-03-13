---
layout: default
title: Portable Jupyter Setup
---

# Portable Jupyter Setup

This page describes the recommended way to run the DICE analysis notebook across Linux, Windows, macOS, and remote servers.

## Primary Entry Point

Open:

- `dice_results_analysis.ipynb`

Use this environment:

- `environment.yml`

The notebook resolves repository paths dynamically and calls the same pinned Python pipeline used by the CLI wrapper, so it does not depend on machine-specific local paths.

`environment.yml` creates a lightweight Conda environment and then installs the exact pinned notebook stack from `requirements.txt` via `pip`. This is more reliable across platforms than pinning every package directly through Conda.

## Updating an Existing Clone

If you already cloned the repository and want the latest GitHub changes:

```bash
cd DICE
git fetch origin
git pull --ff-only origin main
conda env update -f environment.yml --prune
```

If `git status --short` shows local changes you want to keep, commit them or stash them before pulling.

## Conda Environment Fix

If this command fails:

```bash
conda run -n dice-results jupyter lab dice_results_analysis.ipynb
```

with:

```text
EnvironmentLocationNotFound: Not a conda environment
```

then `dice-results` has not been created yet on that machine.

If Conda instead fails while solving and mentions `tzdata=2025.2`, you are using an older copy of `environment.yml`. The current repo version no longer pins Conda packages that way. Update your clone first:

```bash
cd DICE
git fetch origin
git pull --ff-only origin main
```

Then confirm the file now looks like this:

```yaml
name: dice-results
channels:
  - conda-forge
dependencies:
  - python=3.11.4
  - pip
  - pip:
      - -r requirements.txt
```

Create it with:

```bash
cd DICE
conda env create -f environment.yml
conda run -n dice-results jupyter lab dice_results_analysis.ipynb
```

You can verify it exists with:

```bash
conda env list
```

If the environment exists but seems broken, rebuild it cleanly:

```bash
cd DICE
conda env remove -n dice-results
conda env create -f environment.yml
```

## Local Machine Procedure

```bash
git clone https://github.com/ping830616/DICE.git
cd DICE
conda env create -f environment.yml
conda run -n dice-results jupyter lab dice_results_analysis.ipynb
```

If the environment already exists:

```bash
cd DICE
conda env update -f environment.yml --prune
conda run -n dice-results jupyter lab dice_results_analysis.ipynb
```

Run the notebook from top to bottom.

## Remote Linux Server

On the server:

```bash
git clone https://github.com/ping830616/DICE.git
cd DICE
conda env create -f environment.yml
conda run -n dice-results jupyter lab --no-browser --ip 0.0.0.0 --port 8888 dice_results_analysis.ipynb
```

From your local machine, forward the port:

```bash
ssh -L 8888:localhost:8888 <user>@<server>
```

Then open the Jupyter URL shown by the server command in your local browser.

For an ASU-specific server workflow with placeholders instead of personal account details, see [asu-server-setup.md](asu-server-setup.md).

## Windows and `venv`

Conda is the recommended cross-platform path. If you prefer `venv`:

```bash
git clone https://github.com/ping830616/DICE.git
cd DICE
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
