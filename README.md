# DICE

This repository is organized into two top-level workflows:

- [`analysis and results`](analysis%20and%20results/): the reviewer-facing, notebook-first workflow for regenerating figures, tables, and model results from the released dataset.
- [`data generation`](data%20generation/): the retained Tier-0 to Tier-2 data-generation materials and validation references.

Start here:

- [Analysis and results overview](analysis%20and%20results/README.md)
- [Portable notebook](analysis%20and%20results/dice_results_analysis.ipynb)
- [Portable setup guide](analysis%20and%20results/portable-setup.md)
- [Cross-platform environment](analysis%20and%20results/environment.yml)
- [Data generation overview](data%20generation/README.md)
- [Documentation home](data%20generation/docs/index.md)
- [Portable analysis page](analysis%20and%20results/index.md)
- [Hardware and compatibility](data%20generation/docs/hardware-compatibility.md)

## Analysis and Results

Reviewers and users should start here:

- [analysis and results/dice_results_analysis.ipynb](analysis%20and%20results/dice_results_analysis.ipynb)
- [analysis and results/environment.yml](analysis%20and%20results/environment.yml)
- [analysis and results/portable-setup.md](analysis%20and%20results/portable-setup.md)

Portable local run:

```bash
git clone https://github.com/ping830616/DICE.git
cd DICE/"analysis and results"
conda env create -f environment.yml
conda run -n dice-results jupyter lab dice_results_analysis.ipynb
```

Portable remote-server run:

```bash
cd DICE/"analysis and results"
conda env create -f environment.yml
conda run -n dice-results jupyter lab --no-browser --ip 0.0.0.0 --port 8888 dice_results_analysis.ipynb
```

The notebook regenerates the published outputs from `data generation/dataset/ITC_M2Pro_DATA/` and writes a manifest at `results_portable/run_manifest.json` so you can compare dataset and environment hashes across machines.

## Analysis Folder Map

- `dice_results_analysis.ipynb`: primary public notebook entry point.
- `environment.yml`: recommended Conda environment for Linux, Windows, macOS, and servers.
- `requirements.txt`: `venv`/`pip` fallback.
- `portable-setup.md`: step-by-step setup guide for local and remote execution.
- `tools/run_results_pipeline.py`: non-interactive backend used by the notebook.
- `tools/generate_results_analysis.py`: results-table and figure generation backend.
- `tools/train_eval_dice_pipeline.py`: retraining and evaluation backend.

## Data Generation

The [`data generation`](data%20generation/) folder is still kept in the repo for methodology, schema, and dataset context. The public-facing reproducibility path for reviewers is the notebook under `analysis and results/`.
