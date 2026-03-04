---
layout: default
title: Workloads and Anomalies
---

# Workloads and Anomalies

## Workloads

| Workload | Description |
|---|---|
| `BROWSER` | Network + parsing style behavior via repeated HTTP fetches. |
| `VIDEO_SW` | Software video-style frame operations (grayscale, downsample, compress/decompress). |
| `PY_AI` | Alternating tensor and matrix math (Torch/Numpy). |
| `PY_STATS` | Large-array streaming stats and memory update pattern. |

## Stressors

| Stressor | Class | Description |
|---|---|---|
| `NOMINAL` | Nominal | No extra stress thread; baseline behavior. |
| `CACHE` | Anomaly | Cache pressure using strided access patterns. |
| `TLB` | Anomaly | TLB pressure using random page-level touches. |
| `BRANCH` | Anomaly | High branch unpredictability loop. |
| `MEMBW` | Anomaly | Memory bandwidth pressure with large-buffer updates. |
| `ATOMIC` | Anomaly | Lock/atomic contention with multithread increments. |

## Labeling Rule

- `NOMINAL` stressor -> class label `NOMINAL`
- any other stressor -> class label `ANOMALY`

## Total Cases

`4 workloads x 6 stressors = 24` case folders per tier.
