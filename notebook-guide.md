# Notebook Guide

## What Runs the Digital Twin?

The digital twin is executed in the `Run End-to-End` section of `dice_results_analysis.ipynb`.

That execution cell calls `run_notebook_pipeline(...)`, which runs:
- tier-level analysis artifact generation
- the full benign-trained DICE digital-twin pipeline
- the optional workload-holdout robustness pass
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
- `RUN_HOLDOUT`: whether to run workload-holdout robustness
- `INCLUDE_TUNING`: whether to run the tuning sweep

## Practical Reading Order

1. `Execution Guard`
2. `Notebook-Local Pipeline Engine`
3. `Run End-to-End`
4. `What Runs vs What Reads`
5. result sections below that point
