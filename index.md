---
layout: default
title: DICE
---

# DICE

Portable analysis and ITC-paper result generation for the released DICE dataset.

## Run

```bash
git clone https://github.com/ping830616/DICE.git
cd DICE
conda env create -f environment.yml
conda run -n dice-results jupyter lab dice_results_analysis.ipynb
```

Run the notebook from top to bottom. It generates:

- `results_itc_paper/`
- `results_itc_appendix/`
- `results_portable/run_manifest.json`

## Docs

- [Portable setup]({{ site.baseurl }}/portable-setup.html)
- [ITC paper and appendix methodology]({{ site.baseurl }}/itc-paper-methodology.html)
- [ASU server setup]({{ site.baseurl }}/asu-server-setup.html)
- [Data generation docs]({{ site.baseurl }}/data%20generation/docs/index.html)
