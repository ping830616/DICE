---
layout: default
title: Portable Jupyter Setup
---

# Portable Jupyter Setup

Use the notebook as the public entry point.

The notebook is the end-to-end runner. It does not require separate shell scripts or external Python entrypoints during normal use.

## Reproducibility Scope

This setup is intended to regenerate the released DICE analysis results from the committed dataset across different machines.

Expected to be reproducible:

- notebook execution flow
- paper and appendix output folders
- dataset and environment hashes in `results_portable/run_manifest.json`

Not guaranteed to be identical on every machine:

- bit-for-bit identical floating-point outputs across all OS and math-library stacks
- raw Tier-1/Tier-2 data collection outside Apple/macOS collection hosts

## Local

```bash
cd ~/Documents
git lfs install
GIT_LFS_SKIP_SMUDGE=1 git clone https://github.com/ping830616/DICE.git
cd DICE
conda env create -f environment.yml
conda activate dice-results
python scripts/validate_env.py --repo-root "$PWD" --dataset-root "$PWD/data generation/dataset/ITC_M2Pro_DATA"
export DICE_REPO_ROOT="$PWD"
export PYTHONHASHSEED=0
export MPLCONFIGDIR="$PWD/.mplconfig"
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export BLIS_NUM_THREADS=1
mkdir -p "$MPLCONFIGDIR"
jupyter lab dice_results_analysis.ipynb
```

If you need the crash-pilot payload too, run:

```bash
git lfs pull --include="data generation/dataset/ITC_M2Pro_DATA/workload_crash_pilots/**"
```

Run the notebook from top to bottom.

## Existing Clone

```bash
cd DICE
git fetch origin
git pull --ff-only origin main
conda env update -f environment.yml --prune
conda run -n dice-results python scripts/validate_env.py --repo-root "$PWD" --dataset-root "$PWD/data generation/dataset/ITC_M2Pro_DATA"
conda run -n dice-results jupyter lab dice_results_analysis.ipynb
```

## Remote Server

On the server:

```bash
git lfs install
GIT_LFS_SKIP_SMUDGE=1 git clone https://github.com/ping830616/DICE.git
cd DICE
conda env create -f environment.yml
conda run -n dice-results python scripts/validate_env.py --repo-root "$PWD" --dataset-root "$PWD/data generation/dataset/ITC_M2Pro_DATA"
conda run -n dice-results jupyter lab --no-browser --ip 0.0.0.0 --port 8888 dice_results_analysis.ipynb
```

A complete GitHub-provided clone requires Git LFS to be installed locally, `git lfs pull --include="data generation/dataset/ITC_M2Pro_DATA/workload_crash_pilots/**"` to succeed, and the quick check below to show real CSV content instead of a Git LFS pointer. A normal `git clone` can finish while `workload_crash_pilots/` is still incomplete.

If GitHub returns an LFS quota or LFS budget error during `git clone` or `git lfs pull`, GitHub alone cannot currently provide a 100% complete clone of this repository.

For `6. Crash-Aware Early Warning and Real Crash Localization`, the crash-evidence gallery cells, and `8G. Workload-Matched Crash Matrix`, treat the repo as incomplete until `workload_crash_pilots/.../crash_events.csv` shows real CSV content. If that file is missing or only contains Git LFS pointer text, run:

- run `git lfs install`
- run `git lfs pull --include="data generation/dataset/ITC_M2Pro_DATA/workload_crash_pilots/**"`
- or point the notebook at a local materialized copy of `workload_crash_pilots/`

Quick check:

```bash
PILOT_CSV="data generation/dataset/ITC_M2Pro_DATA/workload_crash_pilots/data_workload_crash_pilot_real_browser_branch/crash_evidence/crash_events.csv"
sed -n '1,3p' "$PILOT_CSV"
```

If the file starts with `version https://git-lfs.github.com/spec/v1`, the crash-pilot payload is still only a pointer stub.

When that happens, crash-aware notebook cells that read pilot manifests, copied diagnostic reports, or per-case logs may fail, show no abort pilot cases, or only read pointer text rather than the real payload.

If that happens even after `git lfs pull`, materialize the pilot payload from a known-good local copy:

```bash
rsync -a "/absolute/path/to/materialized/workload_crash_pilots/" \
  "$PWD/data generation/dataset/ITC_M2Pro_DATA/workload_crash_pilots/"
```

If you only want a lightweight released-results clone, you can still start with:

```bash
GIT_LFS_SKIP_SMUDGE=1 git clone https://github.com/ping830616/DICE.git
```

Then verify `crash_events.csv` again. Real payloads start with `case_id,workload,stressor,...`.

From your local machine:

```bash
ssh -L 8888:localhost:8888 <user>@<server>
```

Then open the Jupyter URL shown by the server.

## Outputs

The notebook generates the analysis, main-paper, appendix, and reproducibility folders under:

- `data generation/dataset/ITC_M2Pro_DATA/`

## Verification

After running on different machines, compare:

1. `results_portable/run_manifest.json`
2. dataset SHA256
3. `environment.yml` SHA256
4. `requirements.txt` SHA256
5. `results_dice_full/overall_metrics.csv`
6. `results_dice_full/sequential_metrics.csv`
7. `results_dice_full/stressor_diagnosis_metrics.csv`

If the manifest hashes and these core result tables match, the same released workflow and declared environment were used.
