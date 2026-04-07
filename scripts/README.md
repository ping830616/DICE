# `scripts/`

This folder contains lightweight entry points for the reproducibility workflow.
The actual implementation lives in [`../tools/`](../tools), while the files here
provide short, stable commands for common local and CI usage.

## Files

### `reproduce_all.sh`

Shell wrapper for [`../tools/run_reproducible_notebook.sh`](../tools/run_reproducible_notebook.sh).

What it does:

- resolves the repository root from the current script location
- forwards all command-line arguments to the main reproducible notebook runner
- provides a short entry point for full end-to-end notebook execution

Use it when you want to:

- create or refresh the pinned Conda environment
- run the environment preflight checks
- execute `dice_results_analysis.ipynb` headlessly

Typical usage:

```bash
bash scripts/reproduce_all.sh
```

You can also pass the same options supported by `tools/run_reproducible_notebook.sh`,
such as `--dataset-root`, `--output-notebook`, `--skip-env-update`, or `--ref`.

### `validate_env.py`

Python wrapper for [`../tools/check_notebook_environment.py`](../tools/check_notebook_environment.py).

What it does:

- resolves the repo root from `DICE_REPO_ROOT` or from the script location
- checks the pinned notebook environment and dataset layout
- forwards `--repo-root`, `--dataset-root`, and `--report-path` to the main checker
- returns a nonzero exit code if the environment is not ready

Use it when you want to:

- verify that the local environment matches `environment.yml`
- confirm that the expected dataset folders are present
- generate the JSON preflight report before running the notebook

Typical usage:

```bash
python scripts/validate_env.py \
  --repo-root "$PWD" \
  --dataset-root "$PWD/data generation/dataset/ITC_M2Pro_DATA"
```

By default, the report is written to:

```text
ci_artifacts/notebook_environment_report.json
```

## Relationship To `tools/`

If you need the full implementation details, look in [`../tools/`](../tools):

- `scripts/reproduce_all.sh` delegates to `tools/run_reproducible_notebook.sh`
- `scripts/validate_env.py` delegates to `tools/check_notebook_environment.py`

In short:

- use `scripts/` for simple top-level entry points
- use `tools/` when you want the full underlying workflow logic
