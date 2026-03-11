---
layout: default
title: Hardware and Compatibility
---

# Hardware and Compatibility

This dataset release is tied to one specific collection machine and one specific telemetry toolchain.

## Collection Machine

The released data in this repository was collected on:

- `MacBook Pro` (`Mac14,10`)
- `Apple M2 Pro`
- `12` CPU cores (`8` performance + `4` efficiency)
- `19` GPU cores
- `16 GB` unified memory
- `arm64`
- `macOS 26.3`

## Why This Repository Is Mac-Specific

- `Tier-0` uses `psutil`, so the code itself is the most portable part, but the exported fields still depend on the host OS and hardware.
- `Tier-1` uses `powermetrics` plus `sudo`, which is macOS-specific and exposes Apple-specific power and thermal counters.
- `Tier-1-alt` uses `macmon` and falls back to `powermetrics`, so it is effectively an Apple Silicon macOS path.
- `Tier-2` uses `xcrun xctrace`, which requires Apple's Xcode tooling and therefore macOS.

## What Your Hardware Changes in the Data

- Apple Silicon exposes CPU, GPU, and ANE power behavior that does not exist on generic x86 laptops in the same form.
- The `M2 Pro` split between performance and efficiency cores changes utilization, scheduling, thermals, and frequency behavior.
- Unified memory means memory pressure and bandwidth behavior differ from discrete CPU/GPU systems.
- The `19`-core integrated GPU affects Tier-1-alt and Tier-2 signals for graphics-heavy or AI-heavy workloads.
- Some fields are tool-exposure dependent even on Mac, so another Mac can still produce a different schema or different missing-value pattern.

## Compatibility Table

| Machine | Tier-0 | Tier-1 | Tier-1-alt | Tier-2 | Practical status |
| --- | --- | --- | --- | --- | --- |
| This Apple Silicon Mac (`M2 Pro`) | Yes | Yes | Yes | Yes | Full release path |
| Another Apple Silicon Mac | Yes | Usually | Usually | Usually | Best port, but not schema-identical |
| Intel Mac | Yes | Partial | No | Partial | Can run some pieces, not release-parity |
| Linux | Partial | No | No | No | Tier-0 only, schema differs |
| Windows | Partial | No | No | No | Tier-0 only, schema differs |

## Recommended Interpretation

- Treat this repository as a reproducible workflow for Apple Silicon macOS collection.
- Treat the released dataset as an `M2 Pro` machine profile, not as a hardware-neutral benchmark.
- If you move to another machine, expect to regenerate schemas and revalidate feature coverage before comparing results.
