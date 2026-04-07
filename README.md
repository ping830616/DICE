# DICE

DICE is a tier-aware digital-twin analysis pipeline for anomaly detection, diagnosis, subsystem localization, crash-aware early warning, and grounded triage on the released Apple Silicon ITC study dataset.

The main public entry point is [dice_results_analysis.ipynb](dice_results_analysis.ipynb). A top-to-bottom notebook run regenerates the paper-facing tables, figures, CSV summaries, appendix bundles, and reproducibility manifests under `data generation/dataset/ITC_M2Pro_DATA/`.

## What Is In This Repository

- [dice_results_analysis.ipynb](dice_results_analysis.ipynb): the paper-aligned, end-to-end results notebook.
- [data generation/README.md](data%20generation/README.md): dataset collection, release, and crash-pilot guidance.
- `data generation/dataset/ITC_M2Pro_DATA/`: the released processed dataset plus the tracked result bundles used by the notebook.
- `tools/`: reusable analysis/export helpers used by the notebook and optional scripted runs.
- `scripts/`: lightweight validation and headless reproduction helpers.
- [notebook-guide.md](notebook-guide.md): a shorter map of notebook sections, outputs, and checkpoints.
- [portable-setup.md](portable-setup.md) and [asu-server-setup.md](asu-server-setup.md): machine setup guidance.
- [itc-paper-methodology.md](itc-paper-methodology.md), [itc_results_section_package.md](itc_results_section_package.md), and [itc_appendix_rewrite.tex](itc_appendix_rewrite.tex): paper-facing drafting references.

## Draft-Aligned Notebook Flow

The notebook now follows the same story as the draft:

1. `1. Experimental Setup, Released Data Inventory, and Hardware Context`
2. `2A. Abstract-Ready Headline Metrics`
3. `2B. Mixed vs Full Deployment Summary`
4. `2. Main DICE Performance`
5. `3. Operational Alerting Reliability`
6. `4. Diagnosis and Anomaly Localization`
7. `5. Cross-Workload Robustness and Design-Space Tradeoffs`
8. `6. Crash-Aware Early Warning and Real Crash Localization`
9. `7. Grounded LLM Triage Support`
10. `Appendix A` through `Appendix F`
11. `8. Paper Bundle and Appendix Exports`
12. `9. Reproducibility Manifest`

That mapping corresponds directly to the draft results sequence:

- draft result `A`: run-level monitoring -> notebook section `2. Main DICE Performance`
- draft result `B`: operational alerting reliability -> notebook section `3. Operational Alerting Reliability`
- draft result `C`: diagnosis and localization -> notebook section `4. Diagnosis and Anomaly Localization`
- draft result `D`: cross-workload robustness and tradeoffs -> notebook section `5. Cross-Workload Robustness and Design-Space Tradeoffs`
- draft result `E`: crash-aware early warning -> notebook section `6. Crash-Aware Early Warning and Real Crash Localization`
- draft result `F`: grounded LLM triage -> notebook section `7. Grounded LLM Triage Support`

## Reviewer Quick Start

For a standard reviewer run on a laptop or server, clone the repo into any working directory and use:

```bash
git lfs install
GIT_LFS_SKIP_SMUDGE=1 git clone https://github.com/ping830616/DICE.git 
cd DICE
conda env create -f environment.yml
conda activate dice-results
python scripts/validate_env.py \
  --repo-root "$PWD" \
  --dataset-root "$PWD/data generation/dataset/ITC_M2Pro_DATA"
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

This path is sufficient for the main released-results workflow. Notebook outputs are written under `data generation/dataset/ITC_M2Pro_DATA/` inside the chosen clone directory.

For crash-aware sections that depend on `workload_crash_pilots/`, run:

```bash
git lfs pull --include="data generation/dataset/ITC_M2Pro_DATA/workload_crash_pilots/**"
```

If GitHub returns an LFS budget or quota error, the reviewer will need either restored Git LFS access for `ping830616/DICE` or a provided local copy of `workload_crash_pilots/`. The sections that require this payload are `6. Crash-Aware Early Warning and Real Crash Localization`, the crash-evidence gallery cells, and `8G. Workload-Matched Crash Matrix`.

Expected outputs reviewers should compare after a successful run:

- `data generation/dataset/ITC_M2Pro_DATA/results_portable/run_manifest.json`
- `data generation/dataset/ITC_M2Pro_DATA/results_itc_paper/comparison/main_monitoring_profile_summary.csv`
- `data generation/dataset/ITC_M2Pro_DATA/results_itc_paper/comparison/industry_paper_scorecard_profiles.csv`
- `data generation/dataset/ITC_M2Pro_DATA/results_itc_paper/comparison/holdout_robustness_profiles.csv`
- `data generation/dataset/ITC_M2Pro_DATA/results_itc_paper/mixed/early_warning_case_summary.csv`
- `data generation/dataset/ITC_M2Pro_DATA/results_itc_appendix/mixed/llm_case_cards.csv`

## Quick Start

Clone DICE into any directory where you want to keep the repo and generated outputs:

```bash
git lfs install
git clone https://github.com/ping830616/DICE.git <repo-dir>
cd <repo-dir>
conda env create -f environment.yml
conda activate dice-results
```

Run the notebook:

```bash
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

Then verify that the crash-pilot data is real and not a Git LFS pointer:

```bash
PILOT_CSV="data generation/dataset/ITC_M2Pro_DATA/workload_crash_pilots/data_workload_crash_pilot_real_browser_branch/crash_evidence/crash_events.csv"
sed -n '1,3p' "$PILOT_CSV"
```

A complete GitHub-provided clone requires all of the following:

- Git LFS is installed and initialized on the local machine
- `git lfs pull --include="data generation/dataset/ITC_M2Pro_DATA/workload_crash_pilots/**"` succeeds
- the quick check file below starts with real CSV content such as `case_id,workload,stressor,...` rather than the Git LFS pointer header

If GitHub returns an LFS quota or LFS budget error during `git clone` or `git lfs pull`, GitHub alone cannot currently provide a 100% complete clone of this repository.

Crash-aware notebook sections need more than the lightweight manifest files. If `workload_crash_pilots/` is incomplete, sections that read pilot `crash_events.csv`, copied diagnostic reports, or crash logs will still need that payload to be materialized. In practice, `6. Crash-Aware Early Warning and Real Crash Localization`, the crash-evidence gallery cells, and `8G. Workload-Matched Crash Matrix` require either:

- a successful `git lfs pull --include="data generation/dataset/ITC_M2Pro_DATA/workload_crash_pilots/**"`
- or a local materialized copy of `workload_crash_pilots/` with `DATASET_ROOT` or `CRASH_PILOTS_ROOT` pointed at that copy

Quick check for a complete clone:

```bash
PILOT_CSV="data generation/dataset/ITC_M2Pro_DATA/workload_crash_pilots/data_workload_crash_pilot_real_browser_branch/crash_evidence/crash_events.csv"
sed -n '1,3p' "$PILOT_CSV"
```

If the file starts with `version https://git-lfs.github.com/spec/v1`, the crash-pilot payload is not checked out yet. If `git lfs pull` fails with an LFS quota or budget error, GitHub is not currently serving the full payload for this repository:

```bash
rsync -a "/absolute/path/to/materialized/workload_crash_pilots/" \
  "$PWD/data generation/dataset/ITC_M2Pro_DATA/workload_crash_pilots/"
```

If you only want the main released-results clone and do not need the crash-pilot payload immediately, you can still use:

```bash
GIT_LFS_SKIP_SMUDGE=1 git clone https://github.com/ping830616/DICE.git
```

Then rerun the quick check above. A real crash-pilot payload starts with:

```text
case_id,workload,stressor,...
```

If the environment already exists:

```bash
conda activate dice-results
conda env update -f environment.yml --prune
```

Validate the repo and released dataset layout before running:

```bash
python scripts/validate_env.py \
  --repo-root "$PWD" \
  --dataset-root "$PWD/data generation/dataset/ITC_M2Pro_DATA"
```

Run the notebook interactively:

```bash
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

Or run it headlessly from top to bottom:

```bash
jupyter nbconvert --to notebook --execute --inplace dice_results_analysis.ipynb
```

For a stricter preflight without executing the notebook, use:

```bash
python tools/check_notebook_environment.py \
  --repo-root "$PWD" \
  --dataset-root "$PWD/data generation/dataset/ITC_M2Pro_DATA"
```

## What The Notebook Saves

All major outputs are written automatically under `data generation/dataset/ITC_M2Pro_DATA/`.
For `ITC_M2Pro_DATA`, the main paper-facing `results_*` folders are now tracked in Git so GitHub exposes a reproducible baseline. Re-running the notebook refreshes those folders locally.

Main destinations:

- `results_itc_paper/comparison/`: cross-profile summary tables and figures used across the paper.
- `results_itc_paper/mixed/`: mixed-profile paper outputs.
- `results_itc_paper/full/`: full-profile paper outputs.
- `results_itc_appendix/`: appendix tables, figures, LLM export bundles, and supporting diagnostics.
- `results_itc_crash_bridge/mixed/`: whole-study crash-bridge summaries when crash pilot data is available.
- `results_portable/run_manifest.json` and `results_itc_paper/reproducibility/run_manifest.json`: reproducibility manifests and runtime context.

Representative generated outputs include:

- `results_itc_paper/comparison/main_monitoring_profile_summary.csv`
- `results_itc_paper/comparison/industry_paper_scorecard_profiles.csv`
- `results_itc_paper/comparison/holdout_robustness_profiles.csv`
- `results_itc_paper/comparison/figures/fig_main_monitoring_profile_comparison.png`
- `results_itc_paper/comparison/figures/fig_conformal_reliability_profiles.png`
- `results_itc_paper/comparison/figures/fig_scenario_diagnosis_localization_profiles.png`
- `results_itc_paper/comparison/figures/fig_case_onset_and_hotspots_profiles.png`
- `results_itc_paper/comparison/figures/fig_design_space_profile_comparison.png`
- `results_itc_paper/mixed/early_warning_case_summary.csv`
- `results_itc_paper/full/early_warning_case_summary.csv`
- `results_itc_appendix/mixed/llm_case_cards.csv`
- `results_itc_appendix/full/llm_case_cards.csv`

## Reproducibility And Portability

The repo is organized so the notebook behaves like a reproducible research pipeline rather than a loose collection of ad hoc cells:

- the first code cell owns the notebook imports and shared runtime bootstrap
- path resolution is centralized near the top of the notebook and supports `DICE_REPO_ROOT`
- seeds, thread caps, and output roots are defined early and reused across the run
- hard-coded local Python interpreter paths were removed from the notebook flow
- dependencies are pinned in [environment.yml](environment.yml), [requirements.txt](requirements.txt), and [data generation/requirements.txt](data%20generation/requirements.txt)
- figures, tables, markdown bundles, CSV summaries, and manifests are written automatically during execution
- the notebook can be rerun from top to bottom without manual file moving or post-run cleanup

The practical goal is consistent regenerated results from the released dataset. Exact bit-for-bit matching across every BLAS stack or operating system is not promised.

## Paper-Facing Utilities

Useful supporting scripts include:

- `tools/run_reproducible_notebook.sh`: wrapper for a pinned notebook execution flow
- `tools/evaluate_dice_uncertainty.py`: uncertainty summaries used by the appendix and comparison outputs
- `tools/early_warning_analysis.py`: crash-aware lead-time export
- `tools/feature_crash_analysis.py`: feature-level crash-warning traces
- `tools/aggregate_itc_crash_bridge.py`: whole-study bridge between the ITC dataset and crash pilots
- `tools/generate_crash_evidence_cards.py`: paper-ready crash evidence galleries
- `tools/generate_macbook_hardware_context_figure.py`: standalone hardware-context figure generator with a repo-local output path
- `tools/run_grounded_llm_local.py`: optional local scoring for the grounded LLM extension

## Local-Only Collections

Some crash-pilot roots are intentionally treated as local machine-generated artifacts rather than default GitHub content:

- `data generation/data_workload_crash_*`
- `data generation/dataset/ITC_M2Pro_DATA/workload_crash_pilots/`

These folders can be very large and may contain crash evidence, screenshots, logs, or pilot reruns. The repository currently tracks the four one-workload pilot roots through Git LFS, which means a normal checkout may fail if the repository LFS budget is exhausted. Use `GIT_LFS_SKIP_SMUDGE=1` for the initial clone when you only need the released ITC dataset and the tracked paper-facing result folders.

That clone mode is enough for the main released ITC dataset and tracked paper outputs, but it is not enough for notebook cells that parse crash-pilot `crash_events.csv`, copied diagnostic reports, or per-case crash logs. Those cells require the real pilot payload rather than the Git LFS pointer stubs left behind by a skip-smudge clone.

The lightweight entry points remain:

- `data generation/dataset/ITC_M2Pro_DATA/workload_crash_pilots/README.md`
- `data generation/dataset/ITC_M2Pro_DATA/workload_crash_pilots/pilot_manifest.csv`

Those files document the current four one-workload pilots and the exact commands used to generate them, even when the full LFS payload is not available locally.

## Additional Docs

- [notebook-guide.md](notebook-guide.md)
- [portable-setup.md](portable-setup.md)
- [asu-server-setup.md](asu-server-setup.md)
- [data generation/README.md](data%20generation/README.md)
- [itc-paper-methodology.md](itc-paper-methodology.md)
- [itc_results_section_package.md](itc_results_section_package.md)
