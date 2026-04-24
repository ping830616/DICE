---
layout: default
title: DICE
---

# DICE

DICE is a digital twin-driven in-field continuous-test engine for Silicon Lifecycle Management (SLM). On the released Apple Silicon ITC study dataset, it uses tiered telemetry to support anomaly detection, anomaly-category diagnosis, subsystem-path evidence, crash-aware early warning, and an LLM-based triage layer.

## Terminology

- `Mixed profile`: Tier-0 plus the core Tier-1 and Tier-2 features.
- `Full profile`: Tier-0 plus the full Tier-1 and Tier-2 feature sets.
- `Anomaly evidence`: observed telemetry minus the behavioral micro-twin prediction.
- `Subsystem path`: system-level path associated with recurring anomaly evidence.
- `LLM-based triage layer`: interpretation layer that summarizes structured DICE evidence without changing alerts.

## Start Here

The main entry point is [`dice_results_analysis.ipynb`](https://github.com/ping830616/DICE/blob/main/dice_results_analysis.ipynb). The notebook is organized to follow the draft narrative:

1. experimental setup and hardware context
2. abstract-ready headline metrics
3. mixed vs full profile summary
4. main monitoring performance
5. operational alerting reliability
6. diagnosis and anomaly localization
7. cross-workload robustness and tradeoffs
8. crash-aware early warning
9. LLM-based triage layer
10. draft bundle, appendix exports, and reproducibility manifest

After that core draft-facing path, the notebook also includes optional host-platform interpretation, crash-evidence galleries, supplemental crash studies, workload-matched crash pilots, feature-level crash trajectories, and an ITC-study crash bridge. The repo docs use the draft's canonical terms for public descriptions.

## Quick Run

```bash
git lfs install
GIT_LFS_SKIP_SMUDGE=1 git clone https://github.com/ping830616/DICE.git
cd DICE
conda env create -f environment.yml
conda activate dice-results
python scripts/validate_env.py --repo-root "$PWD" --dataset-root "$PWD/data generation/dataset/ITC_M2Pro_DATA"
jupyter lab dice_results_analysis.ipynb
```

If you need the crash-aware sections too, materialize `workload_crash_pilots/` afterward with Git LFS as described in the main README.

Run the notebook from top to bottom. It writes draft-aligned outputs automatically under:

- `data generation/dataset/ITC_M2Pro_DATA/results_itc_paper/`
- `data generation/dataset/ITC_M2Pro_DATA/results_itc_appendix/`
- `data generation/dataset/ITC_M2Pro_DATA/results_itc_crash_bridge/`
- `data generation/dataset/ITC_M2Pro_DATA/results_portable/run_manifest.json`

## What You Can Regenerate

- main monitoring scorecards and profile comparisons
- alert reliability and cross-workload robustness summaries
- anomaly-category, subsystem-path, onset, and hardware-context figures
- crash-aware early-warning tables and evidence-card galleries when crash pilot data is available
- LLM-based triage bundles and audit summaries
- appendix-ready exports and reproducibility manifests

## Documentation

- [Repository README](https://github.com/ping830616/DICE/blob/main/README.md)
- [Notebook guide]({{ site.baseurl }}/notebook-guide.html)
- [Portable setup]({{ site.baseurl }}/portable-setup.html)
- [ASU server setup]({{ site.baseurl }}/asu-server-setup.html)
- [ITC paper methodology]({{ site.baseurl }}/itc-paper-methodology.html)
- [Data generation guide]({{ site.baseurl }}/data%20generation/README.html)
