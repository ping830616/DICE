# Notebook Guide

## Purpose

[`dice_results_analysis.ipynb`](dice_results_analysis.ipynb) is the main reproducible Results & Analysis notebook for DICE. It is organized to read like the draft first and like a deeper appendix second, while the surrounding repo docs use the draft's canonical terminology.

## Execution Model

- The first code cell owns the shared imports and notebook bootstrap.
- Early cells resolve `REPO_ROOT`, `DATASET_ROOT`, seeds, output folders, and runtime limits.
- `Run End-to-End` is the cell that triggers the main DICE pipeline.
- Most later cells load saved outputs and turn them into draft-ready tables, figures, markdown snippets, and manifests.
- Crash-pilot sections only work when `workload_crash_pilots/` is materialized locally. A skip-smudge clone can still run the main released ITC analysis, but crash-evidence cells will see Git LFS pointer stubs until you pull the pilot payload or point the notebook at a materialized local copy.

## Recommended Reading Order

1. `1. Experimental Setup, Released Data Inventory, and Hardware Context`
2. `2A. Abstract-Ready Headline Metrics`
3. `2B. Mixed vs Full Deployment Summary`
4. `2. Main DICE Performance`
5. `3. Operational Alerting Reliability`
6. `4. Diagnosis and Localization`
7. `5. Cross-Workload Robustness and Design-Space Tradeoffs`
8. `6. Crash-Aware Early Warning and Real Crash Localization`
9. `7. Grounded LLM Support` (`LLM-based triage layer`)
10. `Appendix A` through `Appendix F`
11. `8. Draft Bundle and Appendix Exports`
12. `9. Reproducibility Manifest`

## Draft Mapping

- draft result `A`: `2. Main DICE Performance`
- draft result `B`: `3. Operational Alerting Reliability`
- draft result `C`: anomaly-category diagnosis and subsystem-path evidence -> `4. Diagnosis and Localization`
- draft result `D`: `5. Cross-Workload Robustness and Design-Space Tradeoffs`
- draft result `E`: `6. Crash-Aware Early Warning and Real Crash Localization`
- draft result `F`: LLM-based triage layer -> `7. Grounded LLM Support`

The notebook section labels remain unchanged where they match the saved notebook, but repo-facing descriptions use `anomaly category`, `subsystem path`, and `LLM-based triage layer`.

## Main Output Roots

The notebook saves results automatically under `data generation/dataset/ITC_M2Pro_DATA/`.
These output folders are generated locally and are ignored by Git, so they will appear after you run the notebook rather than in a fresh clone.

- `results_itc_paper/comparison/`: cross-profile tables and figures
- `results_itc_paper/mixed/`: mixed-profile outputs
- `results_itc_paper/full/`: full-profile outputs
- `results_itc_appendix/`: appendix tables, figures, LLM-based triage bundles, and supporting diagnostics
- `results_itc_crash_bridge/mixed/`: whole-study crash-bridge summaries when crash pilot data is available
- `results_portable/run_manifest.json`: portable runtime manifest

## Key Files To Inspect First

- `results_itc_paper/comparison/main_monitoring_profile_summary.csv`
- `results_itc_paper/comparison/industry_paper_scorecard_profiles.csv`
- `results_itc_paper/comparison/holdout_robustness_profiles.csv`
- `results_itc_paper/comparison/figures/fig_main_monitoring_profile_comparison.png`
- `results_itc_paper/comparison/figures/fig_conformal_reliability_profiles.png`
- `results_itc_paper/comparison/figures/fig_scenario_diagnosis_localization_profiles.png`
- `results_itc_paper/comparison/figures/fig_case_onset_and_hotspots_profiles.png`
- `results_itc_paper/comparison/figures/fig_design_space_profile_comparison.png`

## Reproducibility Checks

- Use [`scripts/validate_env.py`](scripts/validate_env.py) for repo and dataset validation.
- Use [`tools/check_notebook_environment.py`](tools/check_notebook_environment.py) for notebook-specific dependency and layout checks.
- Export `DICE_REPO_ROOT`, `PYTHONHASHSEED=0`, and the single-thread environment variables before execution when you want the strictest reproducible run.
- Run the notebook from top to bottom without skipping cells.

## Optional Extensions

- crash-aware lead-time export: `tools/early_warning_analysis.py`
- crash evidence galleries: `tools/generate_crash_evidence_cards.py`
- feature-level crash traces: `tools/feature_crash_analysis.py`
- crash-bridge aggregation: `tools/aggregate_itc_crash_bridge.py`
- LLM-based triage local scoring: `tools/run_grounded_llm_local.py`
