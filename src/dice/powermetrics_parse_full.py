import csv, json, math, re
from typing import Dict, List
from .cfg import TIER1_CORE_FIELDS

_NUM_RE = re.compile(r"([-+]?\d+(?:\.\d+)?)\s*([A-Za-z%/]+)?")

def to_float_with_unit(s: str) -> float:
    if s is None: return math.nan
    m = _NUM_RE.search(str(s))
    if not m: return math.nan
    val = float(m.group(1))
    unit = (m.group(2) or "").lower()
    if unit == "mw": return val / 1000.0
    return val

def split_samples(text: str) -> List[str]:
    parts = re.split(r"(?m)^\*{2,}\s*Sampled system activity.*$", text)
    return [p.strip() for p in parts if p.strip()]

def norm_key(k: str) -> str:
    k = k.strip().lower()
    k = re.sub(r"\(.*?\)", "", k)
    k = re.sub(r"[^a-z0-9]+", "_", k)
    return k.strip("_")

def extract_kv(block: str) -> Dict[str, float]:
    kv = {}
    for line in block.splitlines():
        line = line.strip()
        if ":" in line:
            k, v = line.split(":", 1)
            k = norm_key(k)
            f = to_float_with_unit(v.strip())
            if not math.isnan(f): kv[k] = f
        elif "=" in line:
            k, v = line.split("=", 1)
            k = norm_key(k)
            f = to_float_with_unit(v.strip())
            if not math.isnan(f): kv[k] = f
    return kv

def _get(kv: Dict[str, float], k: str) -> float:
    return kv.get(k, math.nan)

def _weighted_avg(pairs: List[tuple]) -> float:
    num = 0.0; den = 0.0
    for v, w in pairs:
        if math.isnan(v) or math.isnan(w): continue
        if w <= 0: continue
        num += v * w; den += w
    return (num/den) if den>0 else math.nan

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
        if math.isnan(f) and math.isnan(r): continue
        pairs.append((f, r))
    cpu_avg = _weighted_avg(pairs)

    if math.isnan(cpu_avg):
        cl_pairs = []
        for pref in ["p0_cluster","p1_cluster","e_cluster"]:
            cl_pairs.append((_get(kv,f"{pref}_hw_active_frequency"), _get(kv,f"{pref}_hw_active_residency")))
        cpu_avg = _weighted_avg(cl_pairs)

    if math.isnan(cpu_avg): cpu_avg = _get(kv,"p1_cluster_hw_active_frequency")
    if math.isnan(cpu_avg): cpu_avg = _get(kv,"e_cluster_hw_active_frequency")

    out["cpu_avg_freq_mhz"] = cpu_avg
    out["cpu_avg_freq_ghz"] = (cpu_avg/1000.0) if not math.isnan(cpu_avg) else math.nan

    gpu_avg = _get(kv,"gpu_hw_active_frequency")
    out["gpu_avg_freq_mhz"] = gpu_avg
    out["gpu_avg_freq_ghz"] = (gpu_avg/1000.0) if not math.isnan(gpu_avg) else math.nan

    out["interrupts_per_s"] = _get(kv,"interrupts_per_s")
    out["wakeups_per_s"] = _get(kv,"wakeups_per_s")
    out["timer_wakeups_per_s"] = _get(kv,"timer_wakeups_per_s")
    out["thermal_level"] = _get(kv,"thermal_level")
    out["thermal_pressure"] = _get(kv,"thermal_pressure")
    return out

def build_global_schema(raw_txt: str, out_schema_json: str, max_keys: int = 250) -> List[str]:
    text = open(raw_txt, "r", errors="ignore").read()
    blocks = split_samples(text)
    freq = {}
    for b in blocks[:200]:
        kv = extract_kv(b)
        for k,v in kv.items():
            if not math.isnan(v):
                freq[k] = freq.get(k,0)+1
    keys = sorted(freq.keys(), key=lambda x: (-freq[x], x))[:max_keys]
    json.dump({"full_keys": keys, "max_full_keys": max_keys}, open(out_schema_json,"w"), indent=2)
    return keys

def load_schema(schema_json: str) -> List[str]:
    return json.load(open(schema_json))["full_keys"]

def parse_with_schema(raw_txt: str, out_core_csv: str, out_full_csv: str, schema_json: str, samples_target: int):
    text = open(raw_txt, "r", errors="ignore").read()
    blocks = split_samples(text)
    blocks = blocks[:samples_target] + [""] * max(0, samples_target - len(blocks))

    keys = load_schema(schema_json)

    with open(out_core_csv,"w",newline="") as f:
        w = csv.DictWriter(f, fieldnames=["idx"] + TIER1_CORE_FIELDS)
        w.writeheader()
        for i,b in enumerate(blocks):
            kv = extract_kv(b)
            core = extract_core(kv)
            w.writerow({"idx": i, **core})

    with open(out_full_csv,"w",newline="") as f:
        w = csv.DictWriter(f, fieldnames=["idx"] + keys)
        w.writeheader()
        for i,b in enumerate(blocks):
            kv = extract_kv(b)
            w.writerow({"idx": i, **{k: kv.get(k, math.nan) for k in keys}})
