---
layout: default
title: DICE Home
---

# DICE Workflows

This site is split into two top-level areas:

- `analysis and results/` for portable notebook-first regeneration of figures, tables, and model outputs
- `data generation/` for Tier-0 to Tier-2 collection and validation

## Open

- [Portable notebook]({{ site.baseurl }}/analysis%20and%20results/dice_results_analysis.ipynb)
- [Portable setup guide]({{ site.baseurl }}/analysis%20and%20results/portable-setup.html)
- [Documentation home]({{ site.baseurl }}/data%20generation/docs/index.html)
- [Analysis and results]({{ site.baseurl }}/analysis%20and%20results/index.html)
- [Hardware and compatibility]({{ site.baseurl }}/data%20generation/docs/hardware-compatibility.html)

## Reviewer Path

Start from:

```bash
cd DICE/"analysis and results"
conda env create -f environment.yml
conda run -n dice-results jupyter lab dice_results_analysis.ipynb
```

The `data generation/` folder remains in the repository for dataset methodology and context.

## Remote Server

```bash
cd DICE/"analysis and results"
conda env create -f environment.yml
conda run -n dice-results jupyter lab --no-browser --ip 0.0.0.0 --port 8888 dice_results_analysis.ipynb
```
