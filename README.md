# DICE

This repository is organized into two top-level workflows:

- root-level analysis files: the reviewer-facing, notebook-first workflow for regenerating figures, tables, and model results from the released dataset.
- [`data generation`](data%20generation/): the retained Tier-0 to Tier-2 data-generation materials and validation references.

Start here:

- [Portable notebook](dice_results_analysis.ipynb)
- [Portable setup guide](portable-setup.md)
- [ASU server setup](asu-server-setup.md)
- [Cross-platform environment](environment.yml)
- [Pinned `pip` environment](requirements.txt)
- [Data generation overview](data%20generation/README.md)
- [Documentation home](data%20generation/docs/index.md)
- [Hardware and compatibility](data%20generation/docs/hardware-compatibility.md)

## Analysis and Results

Reviewers and users should start here:

- [dice_results_analysis.ipynb](dice_results_analysis.ipynb)
- [environment.yml](environment.yml)
- [portable-setup.md](portable-setup.md)
- [asu-server-setup.md](asu-server-setup.md)

Portable local run:

```bash
git clone https://github.com/ping830616/DICE.git
cd DICE
conda env create -f environment.yml
conda run -n dice-results jupyter lab dice_results_analysis.ipynb
```

If you see `EnvironmentLocationNotFound`, the environment has not been created yet on that machine. Run:

```bash
cd DICE
conda env create -f environment.yml
conda run -n dice-results jupyter lab dice_results_analysis.ipynb
```

`environment.yml` now creates the Conda environment and then installs the exact pinned notebook stack from `requirements.txt` via `pip`. This avoids Conda-only package availability problems for exact versions like `tzdata`.

Portable remote-server run:

```bash
cd DICE
conda env create -f environment.yml
conda run -n dice-results jupyter lab --no-browser --ip 0.0.0.0 --port 8888 dice_results_analysis.ipynb
```

Updating an existing clone:

```bash
cd DICE
git fetch origin
git pull --ff-only origin main
conda env update -f environment.yml --prune
```

If the environment is broken and you want a clean rebuild:

```bash
cd DICE
conda env remove -n dice-results
conda env create -f environment.yml
```

The notebook regenerates the published outputs from `data generation/dataset/ITC_M2Pro_DATA/` and writes a manifest at `results_portable/run_manifest.json` so you can compare dataset and environment hashes across machines.

## Analysis File Map

- `dice_results_analysis.ipynb`: primary public notebook entry point.
- `environment.yml`: recommended Conda environment for Linux, Windows, macOS, and servers.
- `requirements.txt`: `venv`/`pip` fallback.
- `portable-setup.md`: step-by-step setup guide for local and remote execution.
- `asu-server-setup.md`: server instructions using placeholders instead of personal account info.
- `tools/run_results_pipeline.py`: non-interactive backend used by the notebook.
- `tools/generate_results_analysis.py`: results-table and figure generation backend.
- `tools/train_eval_dice_pipeline.py`: retraining and evaluation backend.

## Data Generation

The [`data generation`](data%20generation/) folder is still kept in the repo for methodology, schema, and dataset context. The public-facing reproducibility path for reviewers is the root-level notebook and setup files.
