# Notebook Guide

## What Runs the Digital Twin?

The digital twin is executed in the `Run End-to-End` section of `dice_results_analysis.ipynb`.

That execution cell calls `run_notebook_pipeline(...)`, which runs:
- tier-level analysis artifact generation
- the full benign-trained DICE digital-twin pipeline
- the optional cross-workload transfer pass
- the optional tuning sweep

## What Only Defines Code?

The `Notebook-Local Pipeline Engine` section defines the embedded backend inside the notebook. It does not run experiments by itself.

## What Only Reads Results?

Everything after `What Runs vs What Reads` mostly loads generated CSV/PNG outputs and turns them into paper-ready tables, figures, dashboards, and appendix artifacts.

## Main Parameters in the Run Cell

- `fit_ratio`: benign fit/calibration split
- `block_B`: decision-block length
- `alpha`: split-conformal false-alarm target
- `persist_k`: persistent-alert requirement
- `gain`: fixed-gain synchronization strength
- `ridge_lambda`: ridge regularization for the benign dynamics model
- `RUN_HOLDOUT`: whether to run the cross-workload transfer pass
- `INCLUDE_TUNING`: whether to run the tuning sweep

## Recommended Reading Order

After the notebook finishes, the clearest GitHub reading order is:

1. `Run End-to-End`
2. `Reader Guide and Main Claims`
3. `Quick Paper-Safe Metrics`
4. `Mixed vs Full Deployment Summary`
5. `Operating-Point Rationale and Industry Metrics`
6. `Diagnosis, Localization, and Hardware Scorecard`
7. `Scenario diagnosis and localization figures`
8. `Case-by-case onset and hotspot figures`
9. `Six-Cell Paper Storyboard`
10. `8D. Early-Warning Readiness and Crash Lead Time`
11. `8E. Crash Evidence Cards and Artifact Gallery`
12. `8F. Controlled Crash-Harness Analysis` when you want to analyze the safe user-space crash dataset collected from the terminal
13. `8G. Workload-Matched Crash Matrix` when you want crash-aware runs across the original four workloads after terminal collection

These sections pull the main paper-facing outputs to the front of the notebook.

## Released Operating Points

The released paper-facing operating points are:

- mixed: `gain=0.15`, `block_B=30`, `alpha=0.10`, `persist_k=1`
- full: `gain=0.35`, `block_B=60`, `alpha=0.02`, `persist_k=1`

These settings come from the two-stage sweep and are summarized in the notebook section `Operating-Point Rationale and Industry Metrics`.

## Main Result Files

If you want to inspect the results without reading the full notebook first, start here:

- `results_itc_paper/comparison/industry_paper_scorecard_profiles.csv`
- `results_itc_paper/comparison/industry_diagnosis_strength_profiles.csv`
- `results_itc_paper/comparison/industry_timeline_profiles.csv`
- `results_itc_paper/comparison/main_monitoring_profile_summary.csv`
- `results_itc_paper/comparison/profile_config_comparison.csv`

If a crash manifest has been collected, the notebook also exports:

- `results_itc_paper/<profile>/early_warning_case_summary.csv`
- `results_itc_paper/<profile>/early_warning_metrics.csv`
- `results_itc_paper/<profile>/fig_early_warning_timeline.png`
- `results_itc_paper/<profile>/early_warning_crash_alignment.csv`
- `results_itc_paper/<profile>/crash_evidence_cards/` after running `tools/generate_crash_evidence_cards.py`

For timing and localization figures, use the notebook sections `Scenario diagnosis and localization figures` and `Case-by-case onset and hotspot figures`.
For crash-aware lead-time analysis, use the notebook section `8D. Early-Warning Readiness and Crash Lead Time`.
For paper-ready evidence panels, use the notebook section `8E. Crash Evidence Cards and Artifact Gallery`.
For the safe user-space crash-harness dataset, use the notebook section `8F. Controlled Crash-Harness Analysis` after collecting `data generation/data_crash_harness/` in the terminal.
For the workload-matched crash dataset, use the notebook section `8G. Workload-Matched Crash Matrix` after collecting a `data generation/data_workload_crash_*` folder in the terminal. The notebook now auto-detects the newest matching crash dataset root and prints the crash output folders before analysis starts.

## Practical Reading Order

1. `Execution Guard`
2. `Notebook-Local Pipeline Engine`
3. `Run End-to-End`
4. `Reader Guide and Main Claims`
5. front result sections below that point

## Split ITC Notebooks

If you want a smaller paper-oriented workflow instead of the all-in-one notebook, use the suite in `itc_notebooks/`.

Recommended order:

1. `dice_itc_00_notebook_map.ipynb`
2. `dice_itc_01_run_and_setup.ipynb`
3. `dice_itc_02_core_results.ipynb`
4. `dice_itc_03_dse_and_complexity.ipynb`
5. `dice_itc_04_case_study_and_llm.ipynb`
6. `dice_itc_05_paper_bundle_and_repro.ipynb`
