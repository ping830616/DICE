---
layout: default
title: Hardware and Compatibility
---

# Hardware and Compatibility

The released dataset was collected on one specific Apple Silicon machine, but the public workflow now supports both a release-matching Apple profile and a capability-aware portable profile.

## Reference Collection Machine

The released data in this repository was collected on:

- `MacBook Pro` (`Mac14,10`)
- `Apple M2 Pro`
- `12` CPU cores (`8` performance + `4` efficiency)
- `19` GPU cores
- `16 GB` unified memory
- `arm64`
- `macOS 26.3`

## What Portability Means Here

The workflow is portable in the sense that the code can adapt to the telemetry interfaces available on the current machine:

- `recommended` mode targets the Apple Silicon release profile
- `portable` mode always runs `Tier-0` and then chooses the best available higher-tier path

Portability does not mean that every machine will expose the same tiers, the same fields, or the same schemas.

## Tier Availability by Platform

| Machine | Tier-0 | Tier-1 | Tier-2 | Practical status |
| --- | --- | --- | --- | --- |
| This Apple Silicon Mac (`M2 Pro`) | Yes | Yes | Yes | Release-matching path |
| Another Apple Silicon Mac | Yes | Usually | Usually | Best public port, but not schema-identical |
| Intel Mac | Yes | Usually legacy only | Partial | Partial collection path |
| Linux | Partial | No | No | Tier-0 only, schema differs |
| Windows | Partial | No | No | Tier-0 only, schema differs |

## Why the Data Changes Across Machines

- Apple Silicon exposes CPU, GPU, and ANE telemetry that does not exist in the same form on many x86 systems.
- The `M2 Pro` mix of performance and efficiency cores affects utilization, scheduling, and thermal behavior.
- Unified memory changes memory-pressure behavior relative to systems with discrete CPU and GPU memory.
- Tier-1 and Tier-2 depend on platform-specific tooling and exposed counters.
- Even another Mac can expose a different subset of Tier-1 signals or a different pattern of missing values.

## Recommended Use

- Use `recommended` mode when you want the closest public reproduction of the released Apple Silicon procedure.
- Use `portable` mode when you want the repo to collect the best supported tier set on the current host.
- Regenerate schemas and revalidate feature coverage whenever you move to a different machine.
