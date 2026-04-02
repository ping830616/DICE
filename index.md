---
layout: default
title: DICE
---

# DICE

DICE is a tier-aware digital-twin analysis pipeline for anomaly detection, diagnosis, subsystem localization, crash-aware early warning, and grounded triage on the released Apple Silicon ITC study dataset.

## Start Here

The main entry point is [`dice_results_analysis.ipynb`](https://github.com/ping830616/DICE/blob/main/dice_results_analysis.ipynb). The notebook is organized to follow the draft narrative:

1. experimental setup and hardware context
2. abstract-ready headline metrics
3. mixed vs full profile summary
4. main monitoring performance
5. alerting reliability
6. diagnosis and localization
7. cross-workload robustness and tradeoffs
8. crash-aware early warning
9. grounded LLM triage
10. appendix exports and reproducibility manifest

## Quick Run

```bash
git clone https://github.com/ping830616/DICE.git
cd DICE
conda env create -f environment.yml
conda activate dice-results
python scripts/validate_env.py --repo-root "$PWD" --dataset-root "$PWD/data generation/dataset/ITC_M2Pro_DATA"
jupyter lab dice_results_analysis.ipynb
```

Run the notebook from top to bottom. It writes paper-ready outputs automatically under:

- `data generation/dataset/ITC_M2Pro_DATA/results_itc_paper/`
- `data generation/dataset/ITC_M2Pro_DATA/results_itc_appendix/`
- `data generation/dataset/ITC_M2Pro_DATA/results_itc_crash_bridge/`
- `data generation/dataset/ITC_M2Pro_DATA/results_portable/run_manifest.json`

## What You Can Regenerate

- main monitoring scorecards and profile comparisons
- alert reliability and cross-workload robustness summaries
- diagnosis, localization, onset, and hardware-context figures
- crash-aware early-warning tables and evidence-card galleries when crash pilot data is available
- grounded LLM triage bundles and audit summaries
- appendix-ready exports and reproducibility manifests

## Documentation

- [Repository README](https://github.com/ping830616/DICE/blob/main/README.md)
- [Notebook guide]({{ site.baseurl }}/notebook-guide.html)
- [Portable setup]({{ site.baseurl }}/portable-setup.html)
- [ASU server setup]({{ site.baseurl }}/asu-server-setup.html)
- [ITC paper methodology]({{ site.baseurl }}/itc-paper-methodology.html)
- [Data generation guide]({{ site.baseurl }}/data%20generation/README.html)
