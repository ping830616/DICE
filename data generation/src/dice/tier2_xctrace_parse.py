import csv
import json
import math
import re
from typing import Dict, List

from .cfg import TIER2_CORE_FIELDS

_NUM_RE = re.compile(r"([-+]?\d+(?:\.\d+)?)\s*([A-Za-z%/_]+)?")
_TAG_PAIR_RE = re.compile(r"<([A-Za-z0-9_.:-]+)[^>]*>\s*([^<]+?)\s*</\1>")
_ATTR_PAIR_RE = re.compile(r'([A-Za-z0-9_.:-]+)\s*=\s*"([^"]+)"')
_DICT_PAIR_RE = re.compile(r"<key>([^<]+)</key>\s*<(?:real|integer|string)>([^<]+)</(?:real|integer|string)>")
_LINE_KV_RE = re.compile(r"^\s*([^:=]+?)\s*[:=]\s*(.+?)\s*$")


def to_float_with_unit(s: str) -> float:
    if s is None:
        return math.nan
    m = _NUM_RE.search(str(s))
    if not m:
        return math.nan

    val = float(m.group(1))
    unit = (m.group(2) or "").lower()

    # Power
    if unit == "mw":
        return val / 1000.0

    # Frequency -> MHz
    if unit == "hz":
        return val / 1_000_000.0
    if unit == "khz":
        return val / 1000.0
    if unit == "ghz":
        return val * 1000.0

    # Time -> ms
    if unit in ("s", "sec", "secs", "second", "seconds"):
        return val * 1000.0
    if unit in ("us", "usec"):
        return val / 1000.0
    if unit in ("ns",):
        return val / 1_000_000.0

    # Bytes
    if unit in ("kb", "kib"):
        return val * 1024.0
    if unit in ("mb", "mib"):
        return val * 1024.0 * 1024.0
    if unit in ("gb", "gib"):
        return val * 1024.0 * 1024.0 * 1024.0
    if unit in ("tb", "tib"):
        return val * 1024.0 * 1024.0 * 1024.0 * 1024.0

    return val


def norm_key(k: str) -> str:
    k = k.strip().lower()
    k = k.split(":")[-1]  # Drop XML namespace prefix
    k = re.sub(r"\(.*?\)", "", k)
    k = re.sub(r"[^a-z0-9]+", "_", k)
    return k.strip("_")


def split_samples(text: str) -> List[str]:
    for pat in (r"(?s)<row\b.*?</row>", r"(?s)<sample\b.*?</sample>", r"(?s)<event\b.*?</event>"):
        rows = re.findall(pat, text)
        if rows:
            return rows

    blocks = [b.strip() for b in re.split(r"\n\s*\n", text) if b.strip()]
    numeric_blocks = []
    for b in blocks:
        if _NUM_RE.search(b):
            numeric_blocks.append(b)
    return numeric_blocks


def extract_kv(block: str) -> Dict[str, float]:
    kv: Dict[str, float] = {}

    # XML plist-like key/value pairs
    for k, v in _DICT_PAIR_RE.findall(block):
        nk = norm_key(k)
        fv = to_float_with_unit(v)
        if nk and (not math.isnan(fv)):
            kv[nk] = fv

    # XML tag text pairs
    for tag, text_val in _TAG_PAIR_RE.findall(block):
        nk = norm_key(tag)
        fv = to_float_with_unit(text_val)
        if nk and (not math.isnan(fv)):
            kv[nk] = fv

    # XML attributes
    for k, v in _ATTR_PAIR_RE.findall(block):
        nk = norm_key(k)
        fv = to_float_with_unit(v)
        if nk and (not math.isnan(fv)):
            kv[nk] = fv

    # Generic line key/value fallback
    for line in block.splitlines():
        m = _LINE_KV_RE.match(line)
        if not m:
            continue
        nk = norm_key(m.group(1))
        fv = to_float_with_unit(m.group(2))
        if nk and (not math.isnan(fv)):
            kv[nk] = fv

    return kv


def _pick(kv: Dict[str, float], exact: List[str], token_sets: List[List[str]]) -> float:
    for k in exact:
        if k in kv:
            return kv[k]
    for k, v in kv.items():
        for tokset in token_sets:
            if all(t in k for t in tokset):
                return v
    return math.nan


def extract_core(kv: Dict[str, float]) -> Dict[str, float]:
    out = {k: math.nan for k in TIER2_CORE_FIELDS}

    out["cpu_usage_pct"] = _pick(
        kv,
        exact=["cpu_usage_pct", "cpu_usage", "cpu_percent", "cpu_pct"],
        token_sets=[["cpu", "usage"], ["cpu", "percent"], ["cpu", "pct"]],
    )
    out["cpu_time_ms"] = _pick(
        kv,
        exact=["cpu_time_ms", "cpu_time"],
        token_sets=[["cpu", "time"]],
    )
    out["thread_count"] = _pick(
        kv,
        exact=["thread_count", "threads", "num_threads"],
        token_sets=[["thread", "count"], ["threads"]],
    )
    out["wakeups_per_s"] = _pick(
        kv,
        exact=["wakeups_per_s", "thread_wakeups_per_s"],
        token_sets=[["wake", "per", "s"], ["wakeups"]],
    )
    out["context_switches_per_s"] = _pick(
        kv,
        exact=["context_switches_per_s"],
        token_sets=[["context", "switch", "per", "s"], ["context", "switch"]],
    )
    out["page_faults_per_s"] = _pick(
        kv,
        exact=["page_faults_per_s", "faults_per_s"],
        token_sets=[["page", "fault"], ["fault", "per", "s"], ["fault"]],
    )
    out["phys_mem_bytes"] = _pick(
        kv,
        exact=["phys_mem_bytes", "physical_memory", "resident_size_bytes"],
        token_sets=[["phys", "mem"], ["physical", "mem"], ["resident", "size"]],
    )
    out["virt_mem_bytes"] = _pick(
        kv,
        exact=["virt_mem_bytes", "virtual_memory", "virtual_size_bytes"],
        token_sets=[["virt", "mem"], ["virtual", "mem"], ["virtual", "size"]],
    )
    out["io_read_Bps"] = _pick(
        kv,
        exact=["io_read_bps", "disk_read_bps", "bytes_read_per_s"],
        token_sets=[["read", "bps"], ["io", "read"], ["disk", "read"], ["bytes", "read"]],
    )
    out["io_write_Bps"] = _pick(
        kv,
        exact=["io_write_bps", "disk_write_bps", "bytes_written_per_s"],
        token_sets=[["write", "bps"], ["io", "write"], ["disk", "write"], ["bytes", "written"]],
    )
    out["energy_impact"] = _pick(
        kv,
        exact=["energy_impact"],
        token_sets=[["energy", "impact"], ["energy"]],
    )
    return out


def build_global_schema(raw_txt: str, out_schema_json: str, max_keys: int = 300) -> List[str]:
    text = open(raw_txt, "r", errors="ignore").read()
    blocks = split_samples(text)
    freq: Dict[str, int] = {}
    for b in blocks[:500]:
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

    with open(out_core_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["idx"] + TIER2_CORE_FIELDS)
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
            w.writerow({"idx": i, **{k: kv.get(k, math.nan) for k in keys}})
