---
layout: default
title: Portable Jupyter Setup
---

# Portable Jupyter Setup

Use the notebook as the public entry point.

The notebook is the end-to-end runner. It does not require separate shell scripts or external Python entrypoints during normal use.

## Reproducibility Scope

This setup is intended to regenerate the released DICE analysis results from the committed dataset across different machines.

Expected to be reproducible:

- notebook execution flow
- paper and appendix output folders
- dataset and environment hashes in `results_portable/run_manifest.json`

Not guaranteed to be identical on every machine:

- bit-for-bit identical floating-point outputs across all OS and math-library stacks
- raw Tier-1/Tier-2 data collection outside Apple/macOS collection hosts

## Local

```bash
git clone https://github.com/ping830616/DICE.git
cd DICE
conda env create -f environment.yml
conda run -n dice-results jupyter lab dice_results_analysis.ipynb
```

Run the notebook from top to bottom.

## Existing Clone

```bash
cd DICE
git fetch origin
git pull --ff-only origin main
conda env update -f environment.yml --prune
conda run -n dice-results jupyter lab dice_results_analysis.ipynb
```

## Remote Server

On the server:

```bash
git clone https://github.com/ping830616/DICE.git
cd DICE
conda env create -f environment.yml
conda run -n dice-results jupyter lab --no-browser --ip 0.0.0.0 --port 8888 dice_results_analysis.ipynb
```

From your local machine:

```bash
ssh -L 8888:localhost:8888 <user>@<server>
```

Then open the Jupyter URL shown by the server.

## Outputs

The notebook generates the analysis, main-paper, appendix, and reproducibility folders under:

- `data generation/dataset/ITC_M2Pro_DATA/`

## Verification

After running on different machines, compare:

1. `results_portable/run_manifest.json`
2. dataset SHA256
3. `environment.yml` SHA256
4. `requirements.txt` SHA256
5. `results_dice_full/overall_metrics.csv`
6. `results_dice_full/sequential_metrics.csv`
7. `results_dice_full/stressor_diagnosis_metrics.csv`

If the manifest hashes and these core result tables match, the same released workflow and declared environment were used.
