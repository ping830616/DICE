import csv, math, plistlib
from typing import Any, Dict, List
from cfg import TIER1_FIELDS

def flatten(obj: Any, prefix: str = "") -> Dict[str, Any]:
    out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            kk = f"{prefix}{k}"
            if isinstance(v, (dict, list)):
                out.update(flatten(v, kk + "."))
            else:
                out[kk] = v
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out.update(flatten(v, f"{prefix}{i}."))
    return out

def _to_float(v) -> float:
    try:
        return float(v)
    except Exception:
        return math.nan

def _find_first(flat_lower: Dict[str, Any], needles: List[str]) -> float:
    for n in needles:
        n = n.lower()
        for k, v in flat_lower.items():
            if n in k:
                f = _to_float(v)
                if not math.isnan(f):
                    return f
    return math.nan

def extract_tier1(sample: Dict[str, Any]) -> Dict[str, float]:
    flat_lower = {str(k).lower(): v for k, v in flatten(sample).items()}
    out = {f: math.nan for f in TIER1_FIELDS}

    out["cpu_power_w"] = _find_first(flat_lower, ["cpu power", "cpu_power"])
    out["gpu_power_w"] = _find_first(flat_lower, ["gpu power", "gpu_power"])
    out["ane_power_w"] = _find_first(flat_lower, ["ane power", "ane_power"])
    out["package_power_w"] = _find_first(flat_lower, ["package power", "package_power"])
    out["soc_power_w"] = _find_first(flat_lower, ["soc power", "soc_power"])
    out["processor_power_w"] = _find_first(flat_lower, ["processor power", "combined power", "processor_power"])

    out["cpu_avg_freq_mhz"] = _find_first(flat_lower, ["cpu average frequency", "cpu frequency mhz", "cpu_avg_freq_mhz"])
    out["gpu_avg_freq_mhz"] = _find_first(flat_lower, ["gpu average frequency", "gpu frequency mhz", "gpu_avg_freq_mhz"])

    out["cpu_avg_freq_ghz"] = _find_first(flat_lower, ["cpu average frequency ghz", "cpu_avg_freq_ghz"])
    if math.isnan(out["cpu_avg_freq_ghz"]) and not math.isnan(out["cpu_avg_freq_mhz"]):
        out["cpu_avg_freq_ghz"] = out["cpu_avg_freq_mhz"] / 1000.0

    out["gpu_avg_freq_ghz"] = _find_first(flat_lower, ["gpu average frequency ghz", "gpu_avg_freq_ghz"])
    if math.isnan(out["gpu_avg_freq_ghz"]) and not math.isnan(out["gpu_avg_freq_mhz"]):
        out["gpu_avg_freq_ghz"] = out["gpu_avg_freq_mhz"] / 1000.0

    out["interrupts_per_s"] = _find_first(flat_lower, ["interrupts per", "interrupts_per_s", "irq"])
    out["wakeups_per_s"] = _find_first(flat_lower, ["wakeups per", "wakeups_per_s", "wakeups"])
    out["timer_wakeups_per_s"] = _find_first(flat_lower, ["timer wakeups", "timer_wakeups_per_s"])

    out["thermal_level"] = _find_first(flat_lower, ["thermal level", "thermal_level"])
    out["thermal_pressure"] = _find_first(flat_lower, ["thermal pressure", "thermal_pressure"])
    return out

def read_plistnul(path: str) -> List[Dict[str, Any]]:
    data = open(path, "rb").read()
    out = []
    for blob in data.split(b"\x00"):
        blob = blob.strip()
        if not blob:
            continue
        try:
            out.append(plistlib.loads(blob))
        except Exception:
            continue
    return out

def parse_powermetrics_to_csv(raw_plistnul: str, out_csv: str, samples_target: int):
    samples = read_plistnul(raw_plistnul)

    rows = []
    for s in samples[:samples_target]:
        rows.append(extract_tier1(s))
    while len(rows) < samples_target:
        rows.append({f: math.nan for f in TIER1_FIELDS})

    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["idx"] + TIER1_FIELDS)
        w.writeheader()
        for i, r in enumerate(rows):
            w.writerow({"idx": i, **r})
