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

## Quick Start

Clone the repo and create the pinned environment:

```bash
git clone https://github.com/ping830616/DICE.git
cd DICE
conda env create -f environment.yml
conda activate dice-results
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

These folders can be very large and may contain local crash evidence, screenshots, logs, or pilot reruns. They are ignored by default so the repository stays reviewable and portable. The tracked paper-facing summaries derived from those pilots belong under `results_itc_paper/`, `results_itc_appendix/`, or `results_itc_crash_bridge/`.

To make the pilot set visible on GitHub without committing the full bundle, the repo now tracks:

- `data generation/dataset/ITC_M2Pro_DATA/workload_crash_pilots/README.md`
- `data generation/dataset/ITC_M2Pro_DATA/workload_crash_pilots/pilot_manifest.csv`

Those two files document the current four one-workload pilots and the exact commands used to generate them.

## Additional Docs

- [notebook-guide.md](notebook-guide.md)
- [portable-setup.md](portable-setup.md)
- [asu-server-setup.md](asu-server-setup.md)
- [data generation/README.md](data%20generation/README.md)
- [itc-paper-methodology.md](itc-paper-methodology.md)
- [itc_results_section_package.md](itc_results_section_package.md)
