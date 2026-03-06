import csv
import json
import math
import re
from typing import Dict, List

from .cfg import TIER1_CORE_FIELDS

_NUM_RE = re.compile(r"([-+]?\d+(?:\.\d+)?)\s*([A-Za-z%/]+)?")
_THERMAL_PRESSURE_MAP = {
    "nominal": 0.0,
    "fair": 1.0,
    "serious": 2.0,
    "critical": 3.0,
}


def to_float_with_unit(s: str) -> float:
    if s is None:
        return math.nan
    m = _NUM_RE.search(str(s))
    if not m:
        return math.nan

    val = float(m.group(1))
    unit = (m.group(2) or "").lower()

    if unit == "mw":
        return val / 1000.0
    if unit == "ghz":
        return val * 1000.0
    if unit == "khz":
        return val / 1000.0
    if unit == "hz":
        return val / 1_000_000.0

    return val


def split_samples(text: str) -> List[str]:
    parts = re.split(r"(?m)^\*{2,}\s*Sampled system activity.*$", text)
    return [p.strip() for p in parts if p.strip()]


def norm_key(k: str) -> str:
    k = k.strip().lower()
    k = re.sub(r"\(.*?\)", "", k)
    k = re.sub(r"[^a-z0-9]+", "_", k)
    return k.strip("_")


def _parse_thermal_pressure_code(v: str) -> float:
    if v is None:
        return math.nan
    s = norm_key(str(v))
    if s in _THERMAL_PRESSURE_MAP:
        return _THERMAL_PRESSURE_MAP[s]
    for name, code in _THERMAL_PRESSURE_MAP.items():
        if name in s:
            return code
    return math.nan


def extract_kv(block: str) -> Dict[str, float]:
    kv: Dict[str, float] = {}

    for line in block.splitlines():
        line = line.strip()
        if not line:
            continue

        pair = None
        if ":" in line:
            pair = line.split(":", 1)
        elif "=" in line:
            pair = line.split("=", 1)
        if pair is None:
            continue

        k, v = pair[0], pair[1]
        k = norm_key(k)
        v = v.strip()

        f = to_float_with_unit(v)
        if not math.isnan(f):
            kv[k] = f
            continue

        # powermetrics thermal pressure is often textual: Nominal/Fair/Serious/Critical
        if k in ("current_pressure_level", "thermal_pressure_level", "pressure_level"):
            code = _parse_thermal_pressure_code(v)
            if not math.isnan(code):
                kv[k] = code
                kv["thermal_pressure"] = code
                kv["thermal_level"] = code

    return kv


def _get(kv: Dict[str, float], k: str) -> float:
    return kv.get(k, math.nan)


def _weighted_avg(pairs: List[tuple]) -> float:
    num = 0.0
    den = 0.0
    for v, w in pairs:
        if math.isnan(v) or math.isnan(w):
            continue
        if w <= 0:
            continue
        num += v * w
        den += w
    return (num / den) if den > 0 else math.nan


def _pick_from_candidates(kv: Dict[str, float], exact: List[str], token_sets: List[List[str]]) -> float:
    for k in exact:
        if k in kv:
            return kv[k]
    for k, v in kv.items():
        for tokset in token_sets:
            if all(tok in k for tok in tokset):
                return v
    return math.nan


def extract_core(kv: Dict[str, float]) -> Dict[str, float]:
    out = {f: math.nan for f in TIER1_CORE_FIELDS}

    out["cpu_power_w"] = _get(kv, "cpu_power")
    out["gpu_power_w"] = _get(kv, "gpu_power")
    out["ane_power_w"] = _get(kv, "ane_power")
    out["processor_power_w"] = _get(kv, "combined_power")

    out["package_power_w"] = _get(kv, "package_power")
    out["soc_power_w"] = _get(kv, "soc_power")

    pairs = []
    for i in range(0, 64):
        f = _get(kv, f"cpu_{i}_frequency")
        r = _get(kv, f"cpu_{i}_active_residency")
        if math.isnan(f) and math.isnan(r):
            continue
        pairs.append((f, r))
    cpu_avg = _weighted_avg(pairs)

    if math.isnan(cpu_avg):
        cl_pairs = []
        for pref in ["p0_cluster", "p1_cluster", "e_cluster"]:
            cl_pairs.append((_get(kv, f"{pref}_hw_active_frequency"), _get(kv, f"{pref}_hw_active_residency")))
        cpu_avg = _weighted_avg(cl_pairs)

    if math.isnan(cpu_avg):
        cpu_avg = _get(kv, "p1_cluster_hw_active_frequency")
    if math.isnan(cpu_avg):
        cpu_avg = _get(kv, "e_cluster_hw_active_frequency")

    out["cpu_avg_freq_mhz"] = cpu_avg
    out["cpu_avg_freq_ghz"] = (cpu_avg / 1000.0) if not math.isnan(cpu_avg) else math.nan

    gpu_avg = _get(kv, "gpu_hw_active_frequency")
    out["gpu_avg_freq_mhz"] = gpu_avg
    out["gpu_avg_freq_ghz"] = (gpu_avg / 1000.0) if not math.isnan(gpu_avg) else math.nan

    out["cpu_temp_c"] = _pick_from_candidates(
        kv,
        exact=["cpu_temp_c", "cpu_die_temperature", "cpu_temperature", "cpu_temp"],
        token_sets=[["cpu", "temperature"], ["cpu", "temp"], ["cluster", "temperature"]],
    )
    out["soc_temp_c"] = _pick_from_candidates(
        kv,
        exact=["soc_temp_c", "soc_temperature", "soc_temp", "system_temperature"],
        token_sets=[["soc", "temperature"], ["soc", "temp"], ["system", "temperature"]],
    )

    out["interrupts_per_s"] = _get(kv, "interrupts_per_s")
    out["wakeups_per_s"] = _get(kv, "wakeups_per_s")
    out["timer_wakeups_per_s"] = _get(kv, "timer_wakeups_per_s")

    out["thermal_level"] = _get(kv, "thermal_level")
    out["thermal_pressure"] = _get(kv, "thermal_pressure")
    if math.isnan(out["thermal_level"]):
        out["thermal_level"] = _get(kv, "current_pressure_level")
    if math.isnan(out["thermal_pressure"]):
        out["thermal_pressure"] = _get(kv, "current_pressure_level")

    return out


def build_global_schema(raw_txt: str, out_schema_json: str, max_keys: int = 250) -> List[str]:
    text = open(raw_txt, "r", errors="ignore").read()
    blocks = split_samples(text)
    freq = {}
    for b in blocks[:200]:
        kv = extract_kv(b)
        for k, v in kv.items():
            if not math.isnan(v):
                freq[k] = freq.get(k, 0) + 1
    keys = sorted(freq.keys(), key=lambda x: (-freq[x], x))[:max_keys]
    json.dump({"full_keys": keys, "max_full_keys": max_keys}, open(out_schema_json, "w"), indent=2)
    return keys


def load_schema(schema_json: str) -> List[str]:
    return json.load(open(schema_json))["full_keys"]


def parse_with_schema(raw_txt: str, out_core_csv: str, out_full_csv: str, schema_json: str, samples_target: int):
    text = open(raw_txt, "r", errors="ignore").read()
    blocks = split_samples(text)
    blocks = blocks[:samples_target] + [""] * max(0, samples_target - len(blocks))

    keys = load_schema(schema_json)
    for k in ["current_pressure_level", "thermal_level", "thermal_pressure", "cpu_temp_c", "soc_temp_c"]:
        if k not in keys:
            keys.append(k)

    with open(out_core_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["idx"] + TIER1_CORE_FIELDS)
        w.writeheader()
        for i, b in enumerate(blocks):
            kv = extract_kv(b)
            core = extract_core(kv)
            w.writerow({"idx": i, **core})

    with open(out_full_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["idx"] + keys)
        w.writeheader()
        for i, b in enumerate(blocks):
            kv = extract_kv(b)
            core = extract_core(kv)
            row = {k: kv.get(k, math.nan) for k in keys}
            row["thermal_level"] = core.get("thermal_level", math.nan)
            row["thermal_pressure"] = core.get("thermal_pressure", math.nan)
            row["cpu_temp_c"] = core.get("cpu_temp_c", math.nan)
            row["soc_temp_c"] = core.get("soc_temp_c", math.nan)
            if "current_pressure_level" in row and math.isnan(row["current_pressure_level"]):
                row["current_pressure_level"] = core.get("thermal_pressure", math.nan)
            w.writerow({"idx": i, **row})
