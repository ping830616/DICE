# DICE Analysis and Results

This folder contains the notebook-first analysis workflow for regenerating figures, tables, and evaluation outputs from the released dataset.

Start here:

- [Portable analysis page](index.md)
- [Portable notebook](dice_results_analysis.ipynb)
- [Portable setup guide](portable-setup.md)
- [Cross-platform Conda environment](environment.yml)
- [Locked Python environment](requirements.txt)
- [Terminal wrapper](tools/run_results_pipeline.py)

Use this folder when you want to clone the repository and regenerate results on Linux, Windows, macOS, or a remote server.

## Quick Start

```bash
cd DICE/"analysis and results"
conda env create -f environment.yml
conda run -n dice-results jupyter lab dice_results_analysis.ipynb
```

The default dataset is `../data generation/dataset/ITC_M2Pro_DATA/`.

If the Conda environment already exists, refresh it with `conda env update -f environment.yml --prune`.

Run the notebook from top to bottom to regenerate the published outputs. For remote servers, launch Jupyter with `--no-browser --ip 0.0.0.0 --port 8888` and connect through SSH forwarding.

For a plain `venv` workflow, install [requirements.txt](requirements.txt) instead. The CLI wrapper remains available for non-interactive runs, but the notebook is the primary public entry point.
