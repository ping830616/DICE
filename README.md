# DICE

Portable analysis and ITC-paper result generation for the released DICE dataset.

The public results workflow is notebook-only. Reviewers do not need to run shell scripts or external Python entrypoints; `dice_results_analysis.ipynb` contains the analysis and evaluation path directly.

For paper writing and review, the same workflow is also split into a smaller notebook suite under `itc_notebooks/`.

## Reproducibility

This repository is designed so the released `analysis/results` workflow can be rerun across Linux, macOS, and remote servers from the same committed dataset.

What should match across machines:

- the notebook workflow
- the input dataset
- the Conda environment specification
- the generated paper and appendix artifact structure
- the dataset and environment hashes recorded in `results_portable/run_manifest.json`

What is not claimed:

- bit-identical floating-point outputs on every OS, CPU, or BLAS stack
- portable raw Tier-1/Tier-2 collection on non-macOS machines

The practical goal is reproducible regenerated results from the released dataset, not hardware-independent telemetry collection.

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

If you want a single reproducible command for laptops, servers, or CI-style runs:

```bash
git clone https://github.com/ping830616/DICE.git
cd DICE
bash tools/run_reproducible_notebook.sh --ref 3d3ee6c51122bd0a2d8083c207e0a3efc8277542
```

That wrapper:

- checks out the exact git ref you specify
- creates or refreshes the pinned `dice-results` Conda environment
- exports deterministic runtime settings used for the notebook
- runs the notebook environment preflight
- executes `dice_results_analysis.ipynb` headlessly with `nbconvert`

For the strictest cross-machine/server reproducibility, use the exact same git commit, the pinned Conda environment, the committed dataset, and the headless notebook runner:

```bash
git clone https://github.com/ping830616/DICE.git
cd DICE
bash tools/run_reproducible_notebook.sh --ref 3d3ee6c51122bd0a2d8083c207e0a3efc8277542
```

This is the recommended path for laptops, remote Linux servers, and CI runners because it fixes the repository state first, refreshes the pinned software environment, applies the deterministic runtime settings, runs the environment preflight, and then executes the notebook in a non-interactive way.

Before running the notebook, you can verify that the pinned environment is actually the one in use:

```bash
conda run -n dice-results python tools/check_notebook_environment.py \
  --repo-root . \
  --dataset-root "data generation/dataset/ITC_M2Pro_DATA"
```

If you prefer a smaller paper-oriented workflow, open the split notebooks in `itc_notebooks/` and follow the order listed in `itc_notebooks/README.md`.

## GitHub Preflight

The repository now includes `.github/workflows/notebook-environment-preflight.yml`.

Use it when you want GitHub to set up the same pinned notebook environment before execution:

- the workflow creates the `dice-results` conda environment from `environment.yml`
- it verifies Python and every pinned package in `requirements.txt`
- it checks that the released dataset layout exists
- it uploads a JSON preflight report as an artifact
- on manual `workflow_dispatch`, you can set `run_notebook=true` to execute `dice_results_analysis.ipynb` only after the preflight succeeds

This gives you a repo-side guardrail so the notebook is not launched on GitHub under a drifted environment.

## Verify Across Machines

After the run finishes on each machine, compare:

1. `results_portable/run_manifest.json`
2. the dataset SHA256
3. the `environment.yml` and `requirements.txt` SHA256 values
4. these result tables:
   `results_dice_full/overall_metrics.csv`
   `results_dice_full/sequential_metrics.csv`
   `results_dice_full/stressor_diagnosis_metrics.csv`

If the manifest hashes and these core result tables match, you are rerunning the same released DICE workflow and dataset under the same declared software environment.

## Update

```bash
cd DICE
git fetch origin
git pull --ff-only origin main
conda env update -f environment.yml --prune
conda run -n dice-results jupyter lab dice_results_analysis.ipynb
```

## Docs

- [Portable setup](portable-setup.md)
- [Notebook guide](notebook-guide.md)
- [ITC notebook suite](itc_notebooks/README.md)
- [ITC paper and appendix methodology](itc-paper-methodology.md)
- [ASU server setup](asu-server-setup.md)
- [`data generation`](data%20generation/README.md)
