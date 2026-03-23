# DICE

Tier-aware digital-twin anomaly detection, diagnosis, and grounded triage for portable silicon lifecycle monitoring.

This repository is notebook-first. The primary reproducibility path is:

`dice_results_analysis.ipynb`

Open that notebook and run it from the first cell to the last cell. No repo bash wrapper is required for the main public results workflow.

## What To Run

- Primary notebook: `dice_results_analysis.ipynb`
- Notebook guide: [notebook-guide.md](notebook-guide.md)
- Portable setup notes: [portable-setup.md](portable-setup.md)
- Linux server guide: [asu-server-setup.md](asu-server-setup.md)
- ITC notebook suite: [itc_notebooks/README.md](itc_notebooks/README.md)
- Paper-method notes: [itc-paper-methodology.md](itc-paper-methodology.md)
- Optional uncertainty experiment: `tools/evaluate_dice_uncertainty.py`
- Optional portable local LLM scorer: `tools/run_grounded_llm_local.py`

## Step-By-Step Setup On Any Machine

Clone the repo, or update an existing clone:

```bash
git clone https://github.com/ping830616/DICE.git
cd DICE
```

If the repo already exists:

```bash
cd ~/DICE
git pull origin main
```

Create the environment, or refresh an existing one:

```bash
conda env create -f environment.yml
conda activate dice-results
```

If `dice-results` already exists:

```bash
conda activate dice-results
conda env update -f environment.yml --prune
```

Export the required runtime variables and validate the environment:

```bash
export PYTHONHASHSEED=0
export DICE_REPO_ROOT="$PWD"
export MPLCONFIGDIR="$PWD/.cache/matplotlib"
mkdir -p "$MPLCONFIGDIR"
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export BLIS_NUM_THREADS=1
python scripts/validate_env.py
```

The released dataset is expected at:

```bash
data generation/dataset/ITC_M2Pro_DATA
```

Choose the run mode that matches your machine:

Local interactive run on the same machine:

```bash
jupyter lab --notebook-dir="$PWD"
```

Headless run on any machine:

```bash
jupyter nbconvert --to notebook --execute --inplace dice_results_analysis.ipynb
```

Remote Linux server run with browser access from another machine:

use [asu-server-setup.md](asu-server-setup.md)

In Jupyter, choose `Kernel -> Restart Kernel and Run All Cells`.

Wait for the notebook to finish from top to bottom without jumping between cells.

## Optional Portable Add-Ons

The notebook is still the main public path. These two scripts are the portable add-ons used for the new uncertainty-aware and scored-LLM results:

```bash
python tools/evaluate_dice_uncertainty.py --feature_profile mixed
python tools/evaluate_dice_uncertainty.py --feature_profile full
```

For the grounded LLM scorer, install the lightweight local runtime once on Apple Silicon:

```bash
python -m pip install mlx-lm sentencepiece
```

Then run the same fixed scored baseline for both profiles:

```bash
python tools/run_grounded_llm_local.py \
  --feature_profile mixed \
  --model_id mlx-community/Qwen2.5-0.5B-Instruct-4bit \
  --prompt_types reviewer_summary \
  --seed 7 \
  --max_tokens 120

python tools/run_grounded_llm_local.py \
  --feature_profile full \
  --model_id mlx-community/Qwen2.5-0.5B-Instruct-4bit \
  --prompt_types reviewer_summary \
  --seed 7 \
  --max_tokens 120
```

These commands write the paper-facing uncertainty summaries, scored LLM outputs, grounding summaries, and runtime metadata under the released dataset tree so the notebook can pick them up automatically.

## Across Different Machines

To compare notebook runs across machines, keep these aligned:

- the same commit
- the same notebook: `dice_results_analysis.ipynb`
- the same released dataset
- the same strict launch block before starting Jupyter: `PYTHONHASHSEED=0`, `MPLCONFIGDIR`, and the single-thread variables above
- CPU-only execution
- single-threaded execution

For the optional portable LLM scorer, also keep these aligned:

- the same `model_id`
- the same cached model revision recorded in `llm_runtime_*.json`
- the same `seed`
- the same `max_tokens`
- the same prompt type (`reviewer_summary` in the released scored baseline)

The first notebook cells print the resolved repository root, dataset root, profile selection, imports, and default result save locations used for that run.

## Path Overrides

If you do not set `DICE_REPO_ROOT`, the notebook tries to infer the repository root from the current working directory and its parent directories.

The notebook uses these repo-local defaults:

- repository root inferred from the current working directory
- `data generation/dataset/ITC_M2Pro_DATA` as the dataset location
- `results_analysis/`, `results_dice_full*/`, `results_itc_paper/`, and `results_itc_appendix/` under the dataset root for outputs

If you want to launch Jupyter from somewhere else, use an absolute repo path:

```bash
export PYTHONHASHSEED=0
export DICE_REPO_ROOT=/absolute/path/to/DICE
export MPLCONFIGDIR=/absolute/path/to/matplotlib_cache
mkdir -p "$MPLCONFIGDIR"
```

For strict reviewer-to-reviewer matching, launch Jupyter from a shell where `PYTHONHASHSEED=0` is already exported.

## Method Sequence

The main notebook is meant to be executed in this order:

1. Validate the released repository and dataset layout.
2. Build the analysis/setup figures and released-data inventory.
3. Run the mixed and full DICE evaluations, including tuning, global evaluation, and holdout robustness when enabled.
4. Generate the detection, diagnosis, attribution, uncertainty-aware, two-stage, and feature-budget summaries.
5. Export the paper and appendix bundles.
6. Export the grounded LLM triage case cards, model catalog, prompt bundles, and any saved scored LLM outputs that match the released portable baseline.

If you prefer the split paper-oriented workflow, use the notebook order in [itc_notebooks/README.md](itc_notebooks/README.md).

## Main Outputs

After a successful notebook run, the main artifacts are written under:

- `data generation/dataset/ITC_M2Pro_DATA/results_analysis/`
- `data generation/dataset/ITC_M2Pro_DATA/results_dice_full/`
- `data generation/dataset/ITC_M2Pro_DATA/results_dice_full_holdout/`
- `data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full/`
- `data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full_holdout/`
- `data generation/dataset/ITC_M2Pro_DATA/results_itc_paper/`
- `data generation/dataset/ITC_M2Pro_DATA/results_itc_appendix/`
- `data generation/dataset/ITC_M2Pro_DATA/results_portable/run_manifest.json`

Key checkpoints:

- `results_dice_full/overall_metrics.csv`
- `results_dice_full/stressor_feature_diagnosis_metrics.csv`
- `results_dice_full_full/overall_metrics.csv`
- `results_dice_full_full/stressor_feature_diagnosis_metrics.csv`
- `results_itc_paper/comparison/digital_twin_variant_summary_profiles.csv`
- `results_itc_paper/comparison/diagnosis_summary_profiles.csv`
- `results_itc_paper/comparison/uncertainty_summary_profiles.csv`
- `results_itc_paper/comparison/llm_grounded_triage_assets_profiles.csv`
- `results_itc_paper/comparison/llm_runtime_profiles.csv`
- `results_itc_paper/comparison/llm_grounding_summary_profiles.csv`
- `results_itc_appendix/mixed/llm_case_cards.csv`
- `results_itc_appendix/full/llm_case_cards.csv`

## Reproducibility Notes

- The environment is pinned in [environment.yml](environment.yml) and [requirements.txt](requirements.txt).
- The notebook prints resolved paths and package/runtime settings in the first cells.
- Run the notebook only in top-to-bottom order.
- The released dataset is bundled under `data generation/dataset/ITC_M2Pro_DATA`, so the public results path is self-contained once the repo is present.
- The practical goal is reproducible regenerated results from the released dataset, not bit-identical floating-point outputs across every OS, CPU, or BLAS stack.
- Portable reproduction applies to the released results workflow, not to raw Tier-1/Tier-2 telemetry collection on arbitrary non-macOS hosts.
- The scored local LLM baseline is reproducible from the released case cards and prompt bundle, but the exact regenerated text depends on using the same model revision and runtime settings recorded in the emitted `llm_runtime_*.json` files.

## Optional Automated Path

The notebook is the main path. The shell wrappers are optional helpers for headless or CI-style runs:

```bash
python scripts/validate_env.py
bash scripts/reproduce_all.sh --ref <exact-commit-hash>
```

They are useful when you want a stricter scripted preflight or a headless notebook execution, but they are not required for the primary notebook-first workflow.

## Legacy/Internal Files

- `scripts/` is kept as optional automation support for validation and headless execution.
- `tools/` contains implementation helpers and pipeline code used by the notebook and automated runs.
- `itc_notebooks/` keeps the split paper workflow for smaller staged runs, but the main public reproduction path remains `dice_results_analysis.ipynb`.
