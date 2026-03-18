# ITC Notebook Suite

This folder splits the large `dice_results_analysis.ipynb` workflow into smaller notebooks that match the ITC paper flow.

## Recommended Order

1. `dice_itc_00_notebook_map.ipynb`
   Use this first. It explains the notebook sequence and the role of each notebook.
2. `dice_itc_01_run_and_setup.ipynb`
   Use this to regenerate results, patch block-trace export, and inspect the dataset/setup snapshot.
3. `dice_itc_02_core_results.ipynb`
   Use this for the main DICE results: performance, reliability, variants, and workload holdout.
4. `dice_itc_03_dse_and_complexity.ipynb`
   Use this for design-space exploration and the projected DICE-score accelerator complexity estimate.
5. `dice_itc_04_case_study_and_llm.ipynb`
   Use this for the true time-series overlay, attribution views, grounded LLM triage, and evidence concentration.
6. `dice_itc_05_paper_bundle_and_repro.ipynb`
   Use this for uncertainty summaries, paper-ready figure export, research directions, claim boundaries, and the reproducibility manifest.

## Practical Notes

- The split notebooks are organized for paper writing, not for isolated reimplementation of every helper cell.
- `dice_itc_01_run_and_setup.ipynb` is the notebook that regenerates the results used by the others.
- The later notebooks assume the expected result CSV and PNG artifacts already exist under the dataset result directories.
- The master notebook `dice_results_analysis.ipynb` remains the all-in-one workflow if you prefer a single file.
