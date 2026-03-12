# DICE Analysis and Results

This folder contains the terminal-first analysis workflow for regenerating figures, tables, and evaluation outputs from the released dataset.

Start here:

- [Portable analysis page](index.md)
- [Locked Python environment](requirements.txt)
- [Terminal wrapper](tools/run_results_pipeline.py)

Use this folder when you want to clone the repository and regenerate results without Jupyter.

## Quick Start

```bash
cd DICE/"analysis and results"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python tools/run_results_pipeline.py
```

The default dataset is `../data generation/dataset/ITC_M2Pro_DATA/`.
