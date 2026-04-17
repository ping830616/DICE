---
layout: default
title: ITC Paper and Appendix Methodology
---

# ITC Paper and Appendix Methodology

This page defines a draft-oriented split for DICE so the main ITC paper stays focused while the AI appendix carries the extra detail allowed for AI-focused papers.

The public workflow is notebook-first: users should run `dice_results_analysis.ipynb`, not the internal helper scripts directly.

## Main Paper

The main paper should emphasize:

1. The digital twin-driven DICE methodology:
   - benign-trained behavioral micro-twin fitting
   - anomaly evidence and block signatures
   - sequential scoring on the decision grid with a persistence rule
   - anomaly-category diagnosis with subsystem-path evidence
2. The core evidence:
   - benign-run versus anomalous-run separability by tier
   - benign-run alerts at a fixed decision budget
   - time-to-detect under the selected persistence rule
   - final-config anomaly-category diagnosis metrics
   - dominant-tier and anomaly-category contribution figures
   - optional crash-aware early-warning lead time when a crash manifest is available
3. The portability story:
   - released dataset
   - pinned environment
   - reproducibility manifest

Use the generated `results_itc_paper/` bundle for this material.

## AI Appendix

The AI appendix can carry supporting material that is useful but too detailed for the main paper:

1. Strict workload-holdout evaluation as the workload/software-drift proxy
2. Per-case anomaly-category summaries and confusion matrices
3. Dominant-tier and anomaly-category tables by stressor
4. Reduced-telemetry robustness across Tier-0, Tier-0/1, and Tier-0/1/2
5. Optional tuning or sensitivity runs if included
6. Feature inventory, case quality, and reproducibility files

Use the generated `results_itc_appendix/` bundle for this material.

## Portable Command

Run this from a clean clone:

```bash
cd DICE
conda env create -f environment.yml
conda run -n dice-results jupyter lab dice_results_analysis.ipynb
```

Run the notebook from top to bottom. It produces:

- `results_analysis/`
- `results_dice_full/`
- `results_dice_full_holdout/`
- `results_dice_tuning/`
- `results_itc_paper/`
- `results_itc_appendix/`
- `results_portable/run_manifest.json`

## Methodology Update in This Repo

The updated portable analysis path now adds:

- benign-trained behavioral micro-twin heads through tiered-telemetry configurations
- sequential decision metrics including benign-run alerts and time-to-detect
- anomaly-category summaries in addition to raw feature attribution
- workload-holdout robustness as a portable drift proxy
- optional crash-aware early-warning analysis that pairs the first persistent anomaly with a reproducible crash-evidence manifest
- packaged draft and appendix artifact folders

This keeps the code portable because all of these artifacts are generated from the released CSV dataset with pinned Python dependencies and without macOS-only collection tools.
