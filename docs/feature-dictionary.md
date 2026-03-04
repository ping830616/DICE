---
layout: default
title: Feature Dictionary
---

# Feature Dictionary (Tier-0, Tier-1, Tier-2)

This page documents dataset features at the field level. It distinguishes between fixed core fields and dynamic full-schema fields.

## Global Metadata and Alignment

Case-level alignment is shared across tiers.

- Case ID format: `WORKLOAD__STRESSOR`
- Workload domain: `BROWSER`, `VIDEO_SW`, `PY_AI`, `PY_STATS`
- Stressor domain: `NOMINAL`, `CACHE`, `TLB`, `BRANCH`, `MEMBW`, `ATOMIC`
- Label rule: `NOMINAL -> NOMINAL`, otherwise `ANOMALY`
- Sampling rate: `5 Hz`
- Standard rows per run: `5000`

---

## Tier-0 Features (Host-Level, psutil)

Tier-0 is stored in `tier0_full_5hz.csv` and uses a probe-selected global schema (`tier0_schema_global.json`) to reduce persistent NaNs.

### Tier-0 Time Columns

| Feature | Type | Meaning |
|---|---|---|
| `idx` | integer | Sample index in run order. |
| `ts_unix_s` | float | Absolute UNIX timestamp (seconds). |
| `t_rel_s` | float | Relative time from run start (seconds). |

### Tier-0 CPU Features

| Feature | Type | Meaning |
|---|---|---|
| `cpu_pct` | percent | Aggregate CPU utilization. |
| `cpu_times_user_pct` | percent | User-space CPU time percentage. |
| `cpu_times_system_pct` | percent | Kernel/system CPU time percentage. |
| `cpu_times_idle_pct` | percent | Idle CPU time percentage. |
| `cpu_times_nice_pct` | percent | Nice-priority CPU time percentage. |
| `cpu_times_iowait_pct` | percent | CPU waiting for I/O percentage (if available). |
| `cpu_times_irq_pct` | percent | Hardware interrupt CPU time percentage (if available). |
| `cpu_times_softirq_pct` | percent | Software interrupt CPU time percentage (if available). |
| `cpu_times_steal_pct` | percent | Stolen CPU time percentage (if available). |
| `cpu{i}_pct` | percent | Per-core CPU utilization for core index `i`. |

### Tier-0 Load and Scheduling Features

| Feature | Type | Meaning |
|---|---|---|
| `load1` | float | 1-minute load average. |
| `load5` | float | 5-minute load average. |
| `load15` | float | 15-minute load average. |
| `ctx_switches` | count | Cumulative context switches (system-wide). |
| `interrupts` | count | Cumulative interrupts (system-wide). |
| `soft_interrupts` | count | Cumulative soft interrupts (if available). |
| `syscalls` | count | Cumulative system calls (if available). |

### Tier-0 CPU Frequency Features

| Feature | Type | Meaning |
|---|---|---|
| `cpu_freq_current_mhz` | MHz | Current average CPU frequency estimate. |
| `cpu_freq_min_mhz` | MHz | Reported minimum CPU frequency. |
| `cpu_freq_max_mhz` | MHz | Reported maximum CPU frequency. |

### Tier-0 Memory and Swap Features

| Feature | Type | Meaning |
|---|---|---|
| `mem_total_bytes` | bytes | Total physical memory. |
| `mem_available_bytes` | bytes | Available memory. |
| `mem_used_bytes` | bytes | Used memory. |
| `mem_free_bytes` | bytes | Free memory. |
| `mem_active_bytes` | bytes | Active memory pages. |
| `mem_inactive_bytes` | bytes | Inactive memory pages. |
| `mem_wired_bytes` | bytes | Wired memory (if available). |
| `mem_cached_bytes` | bytes | Cached memory (if available). |
| `mem_percent` | percent | Memory utilization percentage. |
| `swap_total_bytes` | bytes | Total swap space. |
| `swap_used_bytes` | bytes | Used swap space. |
| `swap_free_bytes` | bytes | Free swap space. |
| `swap_sin_bytes` | bytes | Bytes swapped in. |
| `swap_sout_bytes` | bytes | Bytes swapped out. |
| `swap_percent` | percent | Swap utilization percentage. |

### Tier-0 Disk and Network Rate Features

| Feature | Type | Meaning |
|---|---|---|
| `disk_read_Bps` | bytes/s | Disk read throughput rate. |
| `disk_write_Bps` | bytes/s | Disk write throughput rate. |
| `disk_read_IOPS` | ops/s | Disk read operation rate. |
| `disk_write_IOPS` | ops/s | Disk write operation rate. |
| `net_sent_Bps` | bytes/s | Network sent throughput rate. |
| `net_recv_Bps` | bytes/s | Network received throughput rate. |
| `net_sent_Pps` | packets/s | Network packets sent rate. |
| `net_recv_Pps` | packets/s | Network packets received rate. |

### Tier-0 System State Features

| Feature | Type | Meaning |
|---|---|---|
| `pids_count` | count | Number of process IDs visible at sample time. |
| `uptime_s` | seconds | Host uptime at sample time. |

---

## Tier-1 Features (powermetrics)

Tier-1 outputs are `tier1_core_5hz.csv` and `tier1_full_5hz.csv`. Full-schema keys are learned from observed numeric `powermetrics` fields and saved in `tier1_schema_global.json`.

### Tier-1 Core Features

| Feature | Type | Meaning |
|---|---|---|
| `cpu_power_w` | watts | CPU power estimate. |
| `gpu_power_w` | watts | GPU power estimate. |
| `ane_power_w` | watts | Apple Neural Engine power estimate. |
| `package_power_w` | watts | Package-level power estimate (if exported). |
| `soc_power_w` | watts | SoC power estimate (if exported). |
| `processor_power_w` | watts | Combined processor power estimate. |
| `cpu_avg_freq_mhz` | MHz | Weighted average CPU frequency. |
| `cpu_avg_freq_ghz` | GHz | CPU average frequency in GHz. |
| `gpu_avg_freq_mhz` | MHz | GPU active frequency. |
| `gpu_avg_freq_ghz` | GHz | GPU active frequency in GHz. |
| `interrupts_per_s` | 1/s | Interrupt rate (if exported). |
| `wakeups_per_s` | 1/s | Wakeup rate (if exported). |
| `timer_wakeups_per_s` | 1/s | Timer wakeup rate (if exported). |
| `thermal_level` | numeric | Thermal severity indicator (if exported). |
| `thermal_pressure` | numeric | Thermal pressure indicator (if exported). |

### Tier-1 Full Features

Tier-1 full features depend on the host and `powermetrics` export content. Common feature groups include:

- Per-core frequency and residency (for example, `cpu_0_frequency`, `cpu_0_active_residency`).
- Cluster-level frequency and residency (for example, `p0_cluster_hw_active_frequency`).
- GPU active frequency and residency.
- Power rails and combined power summaries.
- Thermal and scheduler-related counters when available.

---

## Tier-2 Features (xctrace)

Tier-2 outputs are `tier2_core_5hz.csv` and `tier2_full_5hz.csv`. Full-schema keys are discovered from exported trace key-value fields and saved in `tier2_schema_global.json`.

### Tier-2 Core Features

| Feature | Type | Meaning |
|---|---|---|
| `cpu_usage_pct` | percent | CPU usage estimate extracted from trace content. |
| `cpu_time_ms` | ms | CPU time estimate mapped to milliseconds. |
| `thread_count` | count | Thread-count estimate for current sample block. |
| `wakeups_per_s` | 1/s | Wakeup rate signal when present in export. |
| `context_switches_per_s` | 1/s | Context-switch rate signal when present. |
| `page_faults_per_s` | 1/s | Page-fault rate signal when present. |
| `phys_mem_bytes` | bytes | Physical/resident memory estimate. |
| `virt_mem_bytes` | bytes | Virtual memory estimate. |
| `io_read_Bps` | bytes/s | Read throughput estimate. |
| `io_write_Bps` | bytes/s | Write throughput estimate. |
| `energy_impact` | numeric | Exported energy-impact score if present. |

### Tier-2 Full Features

Tier-2 full features are parser-discovered numeric keys extracted from XML tags, attributes, and key-value structures in `xctrace_export.xml`. The exact key list is host- and template-dependent.

---

## Missingness Notes

- Tier-0 schema filtering removes fields that are never observed in a probe window.
- Tier-1 and Tier-2 full schemas are built from observed keys in initial successful captures.
- Some fields can remain NaN in specific runs if the source tool does not emit those counters under that workload or platform state.
