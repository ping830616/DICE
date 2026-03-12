---
layout: default
title: Data Description
---

# Data Description

This dataset was built to evaluate anomaly detection on Apple Silicon systems under realistic mixed workloads. The collection protocol is case-aligned and repeatable, so every workload and anomaly condition can be compared under the same timing and sampling settings.

## Composition

The dataset contains four workloads: `BROWSER`, `PY_AI`, `PY_STATS`, and `VIDEO_SW`. For each workload, we run one benign condition (`NOMINAL`) and five anomaly subclasses (`ATOMIC`, `BRANCH`, `CACHE`, `MEMBW`, and `TLB`). This design produces twenty-four total runs.

Each run is collected for 1,000 seconds at 5 Hz, which yields 5,000 samples per run (5,001 CSV lines including the header). Case identifiers use the format `WORKLOAD__STRESSOR`, and the same identifiers are reused across Tier-0, Tier-1, and Tier-2 so that folders align exactly between tiers.

## Workload Narrative

`BROWSER` represents interactive and bursty mixed activity. `PY_AI` represents Python AI-style numerical kernels. `PY_STATS` represents Python statistical kernels. `VIDEO_SW` represents software video-processing kernels. Together, these workloads provide varied CPU, memory, and system-pressure profiles.

For workload-by-workload behavior, tier-level dominant signals, and expected anomaly sensitivity, see [Workloads and Anomalies](workloads-anomalies.md).

## Anomaly Narrative

Each anomaly subclass stresses a distinct mechanism. `ATOMIC` increases synchronization contention. `BRANCH` perturbs control-flow behavior. `CACHE` induces cache-pressure effects. `MEMBW` drives memory-bandwidth pressure. `TLB` increases address-translation pressure.

## Tier Definitions

Tier-0 is host-level operating-system telemetry collected through `psutil`. It captures counters such as CPU utilization breakdowns, memory and swap behavior, disk and network rates, load averages, and process-level system statistics. Tier-1 for this Apple dataset is primarily represented by `tier1_alt` (Apple Silicon telemetry path with fallback support), while legacy `tier1` refers to direct `powermetrics` parsing. Tier-2 is trace-based telemetry parsed from `xctrace` exports.

## Why Tier-0 Matters

Tier-0 is the most deployment-friendly signal source because it relies on standard host counters that are easy to collect with low overhead. It does not directly expose all microarchitectural detail, but it provides broad system observability that is practical for real systems.

When results are computed from Tier-0 alone, anomaly separability is strongest for `ATOMIC`, `CACHE`, and `MEMBW`, because these conditions produce effects that are more visible in host-level counters. `BRANCH` and `TLB` are harder because their signatures are more microarchitectural and overlap more with benign runtime variability in system-level telemetry.

