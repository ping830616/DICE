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
