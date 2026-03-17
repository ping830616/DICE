# DICE

Portable analysis and ITC-paper result generation for the released DICE dataset.

The public results workflow is notebook-only. Reviewers do not need to run shell scripts or external Python entrypoints; `dice_results_analysis.ipynb` contains the analysis and evaluation path directly.

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
- [ITC paper and appendix methodology](itc-paper-methodology.md)
- [ASU server setup](asu-server-setup.md)
- [`data generation`](data%20generation/README.md)
