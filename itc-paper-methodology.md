---
layout: default
title: ITC Paper and Appendix Methodology
---

# ITC Paper and Appendix Methodology

This page defines a submission-oriented split for DICE so the main ITC paper stays focused while the AI appendix carries the extra detail allowed for AI-focused papers.

The public workflow is notebook-first: reviewers should run `dice_results_analysis.ipynb`, not the internal helper scripts directly.

## Main Paper

The main paper should emphasize:

1. The tier-aware DICE methodology:
   - benign-only regime-conditioned micro-twin fitting
   - residual block signatures
   - sequential conformal decisioning
   - mechanism-level diagnosis
2. The core evidence:
   - run-level anomaly separability by tier
   - false alarms at a fixed decision budget
   - time-to-detect under persistent alerting
   - final-config mechanism diagnosis metrics
   - tier and mechanism contribution figures
   - optional crash-aware early-warning lead time when a crash manifest is available
3. The portability story:
   - released dataset
   - pinned environment
   - reproducibility manifest

Use the generated `results_itc_paper/` bundle for this material.

## AI Appendix

The AI appendix can carry supporting material that is useful but too detailed for the main paper:

1. Strict workload-holdout evaluation as the workload/software-drift proxy
2. Per-case diagnosis summaries and confusion matrices
3. Tier-contribution and mechanism-group tables by stressor
4. Reduced-observability robustness across Tier-0, Tier-0/1, and Tier-0/1/2
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

- regime-conditioned benign modeling heads through tier-aware observation configurations
- sequential decision metrics including false alarms and time-to-detect
- mechanism-group diagnosis summaries in addition to raw feature attribution
- workload-holdout robustness as a portable drift proxy
- optional crash-aware early-warning analysis that pairs the first persistent anomaly with a reproducible crash-evidence manifest
- packaged paper and appendix artifact folders

This keeps the code portable because all of these artifacts are generated from the released CSV dataset with pinned Python dependencies and without macOS-only collection tools.
