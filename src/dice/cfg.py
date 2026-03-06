from dataclasses import dataclass
from typing import List

HZ = 5
DT = 1.0 / HZ
SEED = 1337

WORKLOADS = ["BROWSER", "VIDEO_SW", "PY_AI", "PY_STATS"]
STRESSORS = ["NOMINAL", "CACHE", "TLB", "BRANCH", "MEMBW", "ATOMIC"]

TIER1_CORE_FIELDS = [
    "cpu_power_w", "gpu_power_w", "ane_power_w",
    "package_power_w", "soc_power_w", "processor_power_w",
    "cpu_avg_freq_mhz", "cpu_avg_freq_ghz",
    "gpu_avg_freq_mhz", "gpu_avg_freq_ghz",
    "cpu_temp_c", "soc_temp_c",
    "interrupts_per_s", "wakeups_per_s", "timer_wakeups_per_s",
    "thermal_level", "thermal_pressure",
]

TIER1_ALT_CORE_FIELDS = [
    "cpu_power_w",
    "gpu_power_w",
    "ane_power_w",
    "cpu_temp_c",
    "gpu_temp_c",
    "soc_temp_c",
    "cpu_avg_freq_mhz",
    "gpu_avg_freq_mhz",
    "cpu_usage_pct",
    "gpu_usage_pct",
    "cpu_residency_active_pct",
    "gpu_residency_active_pct",
    "fan_rpm",
]

TIER2_DEFAULT_TEMPLATE = "Time Profiler"

TIER2_CORE_FIELDS = [
    "cpu_usage_pct",
    "cpu_time_ms",
    "thread_count",
    "wakeups_per_s",
    "context_switches_per_s",
    "page_faults_per_s",
    "phys_mem_bytes",
    "virt_mem_bytes",
    "io_read_Bps",
    "io_write_Bps",
    "energy_impact",
]

@dataclass(frozen=True)
class Case:
    workload: str
    stressor: str
    label: str

def all_cases() -> List[Case]:
    out = []
    for w in WORKLOADS:
        for s in STRESSORS:
            out.append(Case(w, s, "NOMINAL" if s == "NOMINAL" else "ANOMALY"))
    return out

def case_id(w: str, s: str) -> str:
    return f"{w}__{s}"
