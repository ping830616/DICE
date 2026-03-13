---
layout: default
title: Portable Jupyter Setup
---

# Portable Jupyter Setup

Use the notebook as the public entry point.

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
