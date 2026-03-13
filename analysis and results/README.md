# DICE Analysis and Results

This folder contains the terminal-first analysis workflow for regenerating figures, tables, and evaluation outputs from the released dataset.

Start here:

- [Portable analysis page](index.md)
- [Cross-platform Conda environment](environment.yml)
- [Locked Python environment](requirements.txt)
- [Terminal wrapper](tools/run_results_pipeline.py)

Use this folder when you want to clone the repository and regenerate results without Jupyter.

## Quick Start

```bash
cd DICE/"analysis and results"
conda env create -f environment.yml
conda run -n dice-results python tools/run_results_pipeline.py
```

The default dataset is `../data generation/dataset/ITC_M2Pro_DATA/`.

If the Conda environment already exists, refresh it with `conda env update -f environment.yml --prune`.

For a plain `venv` workflow, install [requirements.txt](requirements.txt) instead. A portable notebook copy also lives in `dice_results_analysis.ipynb`, and you can launch it with `conda run -n dice-results jupyter lab dice_results_analysis.ipynb`.
