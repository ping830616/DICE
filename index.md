---
layout: default
title: DICE Home
---

# DICE Workflows

This site is split into two top-level areas:

- root-level analysis files for portable notebook-first regeneration of figures, tables, and model outputs
- `data generation/` for Tier-0 to Tier-2 collection and validation

## Open

- [Portable notebook]({{ site.baseurl }}/dice_results_analysis.ipynb)
- [Portable setup guide]({{ site.baseurl }}/portable-setup.html)
- [ASU server setup]({{ site.baseurl }}/asu-server-setup.html)
- [Documentation home]({{ site.baseurl }}/data%20generation/docs/index.html)
- [Hardware and compatibility]({{ site.baseurl }}/data%20generation/docs/hardware-compatibility.html)

## Reviewer Path

Start from:

```bash
cd DICE
conda env create -f environment.yml
conda run -n dice-results jupyter lab dice_results_analysis.ipynb
```

If `conda run -n dice-results ...` fails with `EnvironmentLocationNotFound`, create the environment first with `conda env create -f environment.yml`.

The `data generation/` folder remains in the repository for dataset methodology and context.

## Remote Server

```bash
cd DICE
conda env create -f environment.yml
conda run -n dice-results jupyter lab --no-browser --ip 0.0.0.0 --port 8888 dice_results_analysis.ipynb
```

## Updating an Existing Clone

```bash
cd DICE
git fetch origin
git pull --ff-only origin main
conda env update -f environment.yml --prune
```
