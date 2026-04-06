---
layout: default
title: ASU Server Setup
---

# ASU Server Setup

This page shows how to run the DICE notebook on an ASU-hosted Linux server without publishing personal account details.

Use placeholders like:

- `<ASURITE_ID>` for your ASU username
- `<ASU_SERVER_HOST>` for the assigned server hostname or IP

Example SSH shape:

```bash
ssh <ASURITE_ID>@<ASU_SERVER_HOST>
```

Do not commit personal usernames, hostnames, tokens, or notebook URLs into the repository.

## First-Time Setup on the Server

SSH into the server:

```bash
ssh <ASURITE_ID>@<ASU_SERVER_HOST>
```

Clone and set up the environment:

```bash
GIT_LFS_SKIP_SMUDGE=1 git clone https://github.com/ping830616/DICE.git
cd DICE
git lfs install
conda env create -f environment.yml
```

This uses `GIT_LFS_SKIP_SMUDGE=1` because `workload_crash_pilots/` is stored through Git LFS and may fail a normal checkout when the repository LFS budget is exhausted. The released ITC dataset and tracked `results_*` folders still work without those optional pilot objects.

Launch Jupyter without opening a browser on the server:

```bash
conda run -n dice-results jupyter lab --no-browser --ip 0.0.0.0 --port 8888 dice_results_analysis.ipynb
```

## Updating an Existing Clone

If you already cloned the repository on the ASU server and want the latest GitHub changes:

```bash
cd DICE
git fetch origin
git pull --ff-only origin main
conda env update -f environment.yml --prune
```

If `git status --short` shows local changes that you want to keep, commit them or stash them before `git pull --ff-only`.

## Connect from Your Local Machine

From your laptop or desktop, open a second terminal and forward the Jupyter port:

```bash
ssh -L 8888:localhost:8888 <ASURITE_ID>@<ASU_SERVER_HOST>
```

Then open the Jupyter URL printed by the server command in your local browser.

## Run Procedure

After Jupyter opens:

1. Open `dice_results_analysis.ipynb`.
2. Run the notebook from top to bottom.
3. Check the newly generated `results_itc_paper/`, `results_itc_appendix/`, and `results_portable/run_manifest.json` outputs under the dataset root.

## Reproducibility Notes

To keep results as consistent as possible across your laptop, the ASU server, and other machines:

1. Pull the latest `main` branch before running.
2. Refresh the environment with `conda env update -f environment.yml --prune`.
3. Use the committed dataset under `data generation/dataset/ITC_M2Pro_DATA/`.
4. Compare `results_portable/run_manifest.json` across machines and confirm the dataset and environment hashes match.
