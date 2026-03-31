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
- Optional crash-aware early-warning analysis: `tools/early_warning_analysis.py`
- Optional crash-evidence card export: `tools/generate_crash_evidence_cards.py`
- Optional feature-level crash analysis: `tools/feature_crash_analysis.py`
- Optional portable local LLM scorer: `tools/run_grounded_llm_local.py`
- Terminal crash collection runbooks: [data generation/docs/controlled-crash-harness.md](data%20generation/docs/controlled-crash-harness.md) and [data generation/docs/workload-matched-crash-matrix.md](data%20generation/docs/workload-matched-crash-matrix.md)

## Start Here On GitHub

If you want the same top-to-bottom story used for the ITC draft, open `dice_results_analysis.ipynb` and read the early sections in this order after running the notebook:

1. `Run End-to-End`
2. `Reader Guide and Main Claims`
3. `Quick Paper-Safe Metrics`
4. `Mixed vs Full Deployment Summary`
5. `Operating-Point Rationale and Industry Metrics`
6. `Diagnosis, Localization, and Hardware Scorecard`
7. `Scenario diagnosis and localization figures`
8. `Case-by-case onset and hotspot figures`
9. `Six-Cell Paper Storyboard`
10. `8D. Early-Warning Readiness and Crash Lead Time` when a crash manifest is available
11. `8E. Crash Evidence Cards and Artifact Gallery` to show paper-ready warning/crash evidence cards
12. `8F. Controlled Crash-Harness Analysis` when you want to analyze the safe user-space crash dataset collected from the terminal
13. `8G. Workload-Matched Crash Matrix` when you want crash-aware runs across the original four workloads after terminal collection
14. `8H. Feature-Level Warning and Crash Trajectories` when you want richer per-column figures that explicitly bridge the original ITC anomaly warning, the matched crash-pilot anomaly warning, and the real crash time

These sections are placed near the front of the notebook so the GitHub page reads like a paper storyboard instead of a raw analysis dump.

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

Crash-aware early warning is optional because the released processed dataset does not include a crash manifest. When you recollect data with crash evidence enabled, generate the case-level warning and lead-time bundle with:

```bash
python tools/early_warning_analysis.py \
  --result_dir "data generation/dataset/ITC_M2Pro_DATA/results_dice_full" \
  --out_dir "data generation/dataset/ITC_M2Pro_DATA/results_itc_paper/mixed" \
  --feature_profile mixed \
  --crash_manifest "data generation/dataset/ITC_M2Pro_DATA/crash_evidence/crash_events.csv"
```

Repeat with `results_dice_full_full` and `results_itc_paper/full` for the full profile.

To generate a paper-ready crash-evidence gallery after `early_warning_crash_alignment.csv` exists:

```bash
python tools/generate_crash_evidence_cards.py \
  --alignment_csv "data generation/dataset/ITC_M2Pro_DATA/results_itc_paper/mixed/early_warning_crash_alignment.csv" \
  --out_dir "data generation/dataset/ITC_M2Pro_DATA/results_itc_paper/mixed/crash_evidence_cards" \
  --title "DICE Crash Evidence Gallery (Mixed Profile)"
```

The same command works for the full profile by swapping the `mixed` paths for `full`.

For workload-matched crash pilots, you can also generate richer per-column feature plots that keep the original ITC warning time as a reference line:

```bash
python tools/feature_crash_analysis.py \
  --dataset_root "data generation/dataset/ITC_M2Pro_DATA/workload_crash_pilots/data_workload_crash_pilot_real_py_ai_cache" \
  --result_dir "data generation/dataset/ITC_M2Pro_DATA/workload_crash_pilots/data_workload_crash_pilot_real_py_ai_cache/results_dice_workload_crash_mixed" \
  --warning_dir "data generation/dataset/ITC_M2Pro_DATA/workload_crash_pilots/data_workload_crash_pilot_real_py_ai_cache/results_workload_crash_paper/mixed" \
  --out_dir "data generation/dataset/ITC_M2Pro_DATA/workload_crash_pilots/data_workload_crash_pilot_real_py_ai_cache/results_feature_crash_analysis/mixed"
```

These feature-level figures supplement the original anomaly/localization results; they do not replace the main ITC tables and figures. Their bridge tables foreground `original_anomaly_warning_s`, `crash_pilot_anomaly_warning_s`, and `crash_time_s` so the crash pilot stays tied to the overall ITC study.

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
3. Run the mixed and full DICE evaluations, including tuning, global evaluation, and cross-workload transfer analysis when enabled.
4. Generate the detection, diagnosis, attribution, uncertainty-aware, two-stage, and feature-budget summaries.
5. If a crash manifest exists, export the crash-aware early-warning tables and lead-time figures.
6. Export the paper and appendix bundles.
7. Export the grounded LLM triage case cards, model catalog, prompt bundles, and any saved scored LLM outputs that match the released portable baseline.

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

The `*_holdout*` directories keep the legacy file naming used by earlier scripts. In the paper-facing notebook and documentation, the same evaluation is described as cross-workload transfer.

Key checkpoints:

- `results_dice_full/overall_metrics.csv`
- `results_dice_full/case_inventory.csv`
- `results_dice_full/stressor_feature_diagnosis_metrics.csv`
- `results_dice_full/stressor_family_diagnosis_metrics.csv`
- `results_dice_full/stressor_supervised_diagnosis_metrics.csv`
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

## Released Operating Points

The notebook keeps the full sweeps, but the released paper-facing operating points are:

- Mixed profile: `gain=0.15`, `block_B=30`, `alpha=0.10`, `persist_k=1`
- Full profile: `gain=0.35`, `block_B=60`, `alpha=0.02`, `persist_k=1`

These settings were selected from the two-stage sweep recorded in:

- `results_itc_paper/comparison/tuning_parameter_sweep_best_points.csv`
- `results_itc_paper/comparison/tuning_parameter_sweep_summary_profiles.csv`

The notebook section `Operating-Point Rationale and Industry Metrics` explains why these settings were chosen. In short:

- the mixed profile uses a lower synchronization gain and shorter block so sparse deployment-visible signals remain sensitive to early anomalies
- the full profile uses a moderate gain and longer block so the richer telemetry set is more stable before scoring
- the stage-two `alpha` and `persist_k` settings were selected to improve anomaly detection and diagnosis while keeping benign run alerts low

## Suggested Complete Sweep Plan

If you want to rerun the full design study, use this sweep structure:

- Profiles: `mixed`, `full`
- Configurations: `Tier-0`, `Tier-0/1`, `Tier-0/1/2`
- Stage 1: `gain in {0.15, 0.25, 0.35, 0.50}` and `block_B in {30, 60, 90, 120}` with `alpha=0.05`, `persist_k=3`
- Stage 2: fix the best Stage-1 pair, then sweep `alpha in {0.01, 0.02, 0.05, 0.10}` and `persist_k in {1, 2, 3, 5}`
- Feature budgets: `10, 20, 30, 40, 50, 60, 70, 80, 90, 100` percent
- Two-stage screening quantiles: `0.90, 0.95, 0.98`
- Diagnosis views: whole-run, post-alert, and hierarchical selective diagnosis

The notebook already uses this structure for the released paper and appendix bundles.

## How To Read The Results

The recommended paper-facing metrics are split into four groups.

Monitoring quality:

- `ROC-AUC`
- `AUC-PR`
- anomaly detection rate
- benign run-alert rate
- median time to detection

Diagnosis quality:

- exact `Top-1` accuracy
- exact `Top-2` accuracy
- selective `Top-2` accuracy at coverage
- mechanism `Top-3` coverage
- `Macro-F1` as a secondary diagnosis metric

Localization quality:

- first abnormal block time
- second through fifth abnormal block times
- dominant telemetry tier
- dominant mechanism

Resource-aware results:

- low-overhead profile comparisons
- feature-budget sweeps
- projected DICE-score accelerator complexity

## Where The Main Paper Claims Live

Use these files first when drafting:

- `results_itc_paper/comparison/industry_paper_scorecard_profiles.csv`
- `results_itc_paper/comparison/industry_diagnosis_strength_profiles.csv`
- `results_itc_paper/comparison/industry_timeline_profiles.csv`
- `results_itc_paper/comparison/main_monitoring_profile_summary.csv`
- `results_itc_paper/comparison/profile_config_comparison.csv`
- `results_itc_paper/comparison/two_stage_dice_profiles.csv`
- `results_itc_paper/comparison/projected_dice_score_accelerator_complexity_profiles.csv`

The most important front-of-notebook cells load these same files and reformat them into paper-ready tables and figures.

## Localization And Timing Outputs

If you want figures that show where and when anomalies emerge, start with:

- `results_itc_paper/comparison/industry_timeline_profiles.csv`
- `results_itc_paper/comparison/industry_hardware_hotspots_profiles.csv`
- `results_itc_paper/comparison/industry_hardware_feature_map_profiles.csv`
- `results_itc_paper/comparison/industry_top_features_profiles.csv`
- `results_itc_paper/comparison/figures/`

The notebook sections `Scenario diagnosis and localization figures` and `Case-by-case onset and hotspot figures` turn these files into the main localization dashboards. They show:

- when the first abnormal block appears
- how quickly later abnormal blocks follow
- which tier contributes most strongly
- which mechanism and feature groups dominate the anomaly evidence

## Cross-Workload Transfer Outputs

For generalization across workloads, use:

- `results_itc_paper/comparison/holdout_robustness_profiles.csv`
- `results_itc_paper/comparison/uncertainty_holdout_profiles.csv`
- `results_dice_full_holdout/`
- `results_dice_full_full_holdout/`

The filenames keep the historical `holdout` label, but the notebook and paper text refer to this evaluation as cross-workload transfer.

## Reproducibility Notes

- The environment is pinned in [environment.yml](environment.yml) and [requirements.txt](requirements.txt).
- The notebook prints resolved paths and package/runtime settings in the first cells.
- Run the notebook only in top-to-bottom order.
- The released dataset is bundled under `data generation/dataset/ITC_M2Pro_DATA`, so the public results path is self-contained once the repo is present.
- The practical goal is reproducible regenerated results from the released dataset, not bit-identical floating-point outputs across every OS, CPU, or BLAS stack.
- Portable reproduction applies to the released results workflow, not to raw Tier-1/Tier-2 telemetry collection on arbitrary non-macOS hosts.
- The scored local LLM baseline is reproducible from the released case cards and prompt bundle, but the exact regenerated text depends on using the same model revision and runtime settings recorded in the emitted `llm_runtime_*.json` files.

## Expanded Diagnosis Workflows

The main release still ships one run per workload-stressor pair, but the CLI pipeline now supports larger anomaly collections more directly:

- repeated runs can be added as extra case directories with suffixes such as `BROWSER__CACHE__r01` and `BROWSER__CACHE__r02`
- `results_dice_full/case_inventory.csv` records the discovered run inventory, base case id, and repeat tags
- `stressor_family_diagnosis_metrics.csv` reports the relaxed three-family diagnosis setting (`memory_pressure`, `control_flow`, `synchronization`)
- `stressor_supervised_diagnosis_metrics.csv` is reserved for expanded anomaly sets and stays in a skipped state until each stressor has enough samples to train a supervised model without leaking repeated runs across folds

For terminal-first runs, the full script accepts these optional controls:

```bash
python tools/train_eval_dice_pipeline.py \
  --feature_profile mixed \
  --supervised_diagnosis auto \
  --supervised_min_class_samples 8 \
  --supervised_group_key base_case_id \
  --supervised_include_workload
```

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
