---
layout: default
title: Publish on GitHub Pages
---

# Publish on GitHub Pages (`ping830616/DICE`)

Target URL:

`https://ping830616.github.io/DICE/`

## 1. Push This Repository to GitHub

If not already pushed:

```bash
cd DICE/"data generation"
cd ..
git init
git add .
git commit -m "Add DICE Tier-0 to Tier-2 docs site"
git branch -M main
git remote add origin git@github.com:ping830616/DICE.git
git push -u origin main
```

If the remote already exists, just commit and push:

```bash
git add .
git commit -m "Update DICE docs"
git push
```

## 2. Enable Pages in GitHub Settings

In `ping830616/DICE`:

1. Open `Settings` -> `Pages`.
2. Under `Build and deployment`, choose:
   - `Source`: `Deploy from a branch`
   - `Branch`: `main`
   - `Folder`: `/ (root)`
3. Save.

## 3. Wait for First Build

- GitHub Pages usually publishes in a few minutes.
- Refresh: `https://ping830616.github.io/DICE/`

## 4. Verify Site Navigation

Confirm these pages load:

- `/DICE/`
- `/DICE/data%20generation/docs/index.html`
- `/DICE/data%20generation/docs/hardware-compatibility.html`
