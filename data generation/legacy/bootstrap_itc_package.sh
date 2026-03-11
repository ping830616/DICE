#!/bin/bash
set -euo pipefail

CODE_DIR="/Users/hsiaopingni/ITC_2026_M2Pro_CODE"
mkdir -p "$CODE_DIR"

# -----------------------------
# 00_config.py
# -----------------------------
cat > "$CODE_DIR/00_config.py" <<'PY'
from dataclasses import dataclass
from typing import List

HZ = 5
DT = 1.0 / HZ
DURATION_S_DEFAULT = 1000
SAMPLES_DEFAULT = HZ * DURATION_S_DEFAULT  # 5000

WORKLOADS = ["BROWSER", "VIDEO_SW", "PY_AI", "PY_STATS"]
STRESSORS = ["NOMINAL", "CACHE", "TLB", "BRANCH", "MEMBW", "ATOMIC"]

SEED = 1337

TIER1_FIELDS = [
    "cpu_power_w", "gpu_power_w", "ane_power_w",
    "package_power_w", "soc_power_w", "processor_power_w",
    "cpu_avg_freq_mhz", "cpu_avg_freq_ghz",
    "gpu_avg_freq_mhz", "gpu_avg_freq_ghz",
    "interrupts_per_s", "wakeups_per_s", "timer_wakeups_per_s",
    "thermal_level", "thermal_pressure",
]

@dataclass(frozen=True)
class Case:
    workload: str
    stressor: str
    label: str  # NOMINAL or ANOMALY

def all_cases() -> List[Case]:
    out = []
    for w in WORKLOADS:
        for s in STRESSORS:
            out.append(Case(w, s, "NOMINAL" if s == "NOMINAL" else "ANOMALY"))
    return out
PY

# -----------------------------
# 01_workloads.py
# -----------------------------
cat > "$CODE_DIR/01_workloads.py" <<'PY'
import os, time, threading, random, zlib
import numpy as np
import urllib.request
from 00_config import SEED

def _seed_all():
    random.seed(SEED)
    np.random.seed(SEED)

# -------- Workloads --------

def workload_browser(stop_evt: threading.Event):
    """
    Controlled browsing: fixed URLs, fixed read size.
    """
    _seed_all()
    urls = [
        "https://example.com",
        "https://www.iana.org/domains/reserved",
        "https://www.wikipedia.org",
    ]
    i = 0
    while not stop_evt.is_set():
        url = urls[i % len(urls)]
        try:
            urllib.request.urlopen(url, timeout=5).read(200_000)
        except Exception:
            pass
        i += 1
        time.sleep(0.05)

def workload_video_sw(stop_evt: threading.Event):
    """
    Software-only "video-like" pipeline (no external files):
      frame -> grayscale -> downsample -> compress/decompress
    """
    _seed_all()
    H, W = 720, 1280
    frame = (np.random.rand(H, W, 3) * 255).astype(np.uint8)
    while not stop_evt.is_set():
        gray = (0.299 * frame[:, :, 0] + 0.587 * frame[:, :, 1] + 0.114 * frame[:, :, 2]).astype(np.uint8)
        small = gray[::2, ::2]
        comp = zlib.compress(small.tobytes(), level=1)
        _ = zlib.decompress(comp)
        frame = (frame + 1) % 255
        time.sleep(0.005)

def workload_ai_numpy_torch(stop_evt: threading.Event, phase_s: float = 5.0):
    """
    One AI workload: alternate Torch (MPS if available) GEMM and NumPy GEMM.
    Compute-bound; distinct from streaming stats.
    """
    _seed_all()
    import torch
    torch.manual_seed(SEED)

    mps_ok = hasattr(torch.backends, "mps") and torch.backends.mps.is_available()
    device = torch.device("mps" if mps_ok else "cpu")

    N_NUMPY = 1024
    N_TORCH = 2048

    a_np = np.random.randn(N_NUMPY, N_NUMPY).astype(np.float32)
    b_np = np.random.randn(N_NUMPY, N_NUMPY).astype(np.float32)

    a_t = torch.randn((N_TORCH, N_TORCH), device=device, dtype=torch.float32)
    b_t = torch.randn((N_TORCH, N_TORCH), device=device, dtype=torch.float32)

    def torch_phase(end_t):
        while (time.time() < end_t) and (not stop_evt.is_set()):
            c = a_t @ b_t
            s = c.sum()
            if device.type == "cpu":
                _ = float(s.item())

    def numpy_phase(end_t):
        while (time.time() < end_t) and (not stop_evt.is_set()):
            _ = a_np @ b_np

    while not stop_evt.is_set():
        t0 = time.time()
        torch_phase(t0 + phase_s)
        if stop_evt.is_set():
            break
        t1 = time.time()
        numpy_phase(t1 + phase_s)

def workload_stats_streaming(stop_evt: threading.Event):
    """
    Bandwidth-dominated stats: large array reductions + strided updates.
    """
    _seed_all()
    x = np.random.rand(100_000_000).astype(np.float32)  # ~400MB
    while not stop_evt.is_set():
        _ = float(x.sum())
        _ = float(x.mean())
        x[::16] += 1.0

def run_workload(workload: str, stop_evt: threading.Event):
    if workload == "BROWSER":
        return workload_browser(stop_evt)
    if workload == "VIDEO_SW":
        return workload_video_sw(stop_evt)
    if workload == "PY_AI":
        return workload_ai_numpy_torch(stop_evt, phase_s=5.0)
    if workload == "PY_STATS":
        return workload_stats_streaming(stop_evt)
    raise ValueError(f"Unknown workload: {workload}")

# -------- Stressors (run-level anomaly) --------

def run_stressor(stressor: str, stop_evt: threading.Event):
    _seed_all()

    if stressor == "NOMINAL":
        while not stop_evt.is_set():
            time.sleep(0.2)
        return

    if stressor == "MEMBW":
        arr = np.zeros((200_000_000,), dtype=np.uint8)
        i = 0
        while not stop_evt.is_set():
            arr[i:i+10_000_000] = (arr[i:i+10_000_000] + 1) % 255
            i = (i + 10_000_000) % (len(arr) - 10_000_000)

    elif stressor == "CACHE":
        arr = np.random.randn(20_000_000).astype(np.float32)
        while not stop_evt.is_set():
            _ = float(arr[::64].sum())

    elif stressor == "TLB":
        arr = np.zeros((200_000_000,), dtype=np.uint8)
        pages = [i for i in range(0, len(arr), 4096)]
        while not stop_evt.is_set():
            for _ in range(20000):
                idx = random.choice(pages)
                arr[idx] = (arr[idx] + 1) % 255

    elif stressor == "BRANCH":
        x = 0
        while not stop_evt.is_set():
            r = random.getrandbits(32)
            if r & 1:
                x += 3
            elif r & 2:
                x -= 2
            elif r & 4:
                x ^= r
            else:
                x += 1

    elif stressor == "ATOMIC":
        lock = threading.Lock()
        counter = 0

        def worker():
            nonlocal counter
            while not stop_evt.is_set():
                with lock:
                    counter += 1

        threads = [threading.Thread(target=worker, daemon=True) for _ in range(max(2, os.cpu_count() // 2))]
        for th in threads:
            th.start()
        while not stop_evt.is_set():
            time.sleep(0.05)

    else:
        raise ValueError(f"Unknown stressor: {stressor}")
PY

# -----------------------------
# 02_tier0_collect.py
# -----------------------------
cat > "$CODE_DIR/02_tier0_collect.py" <<'PY'
import csv, time, math
import psutil
from dataclasses import dataclass
from typing import Optional, Any, Dict

def _rate(curr, prev, dt):
    if prev is None or dt <= 0:
        return math.nan
    return (curr - prev) / dt

@dataclass
class Prev:
    disk: Optional[Any] = None
    net: Optional[Any] = None
    ts: Optional[float] = None

def sample_tier0(prev: Prev, dt_default: float) -> Dict[str, float]:
    t = time.time()
    dt = (t - prev.ts) if prev.ts else dt_default

    cpu_times = psutil.cpu_times_percent(interval=None)
    load1, load5, load15 = psutil.getloadavg()
    freq = psutil.cpu_freq()

    vm = psutil.virtual_memory()
    sm = psutil.swap_memory()

    disk = psutil.disk_io_counters()
    net = psutil.net_io_counters()

    out = {
        "cpu_pct": psutil.cpu_percent(interval=None),
        "cpu_user_pct": float(getattr(cpu_times, "user", math.nan)),
        "cpu_system_pct": float(getattr(cpu_times, "system", math.nan)),
        "cpu_idle_pct": float(getattr(cpu_times, "idle", math.nan)),
        "load1": float(load1), "load5": float(load5), "load15": float(load15),
        "cpu_freq_mhz": float(freq.current) if freq else math.nan,

        "mem_total": float(vm.total),
        "mem_used": float(vm.used),
        "mem_available": float(vm.available),
        "mem_percent": float(vm.percent),
        "mem_active": float(getattr(vm, "active", math.nan)),
        "mem_inactive": float(getattr(vm, "inactive", math.nan)),
        "mem_wired": float(getattr(vm, "wired", math.nan)),

        "swap_total": float(sm.total),
        "swap_used": float(sm.used),
        "swap_free": float(sm.free),

        "disk_read_Bps": _rate(disk.read_bytes, prev.disk.read_bytes if prev.disk else None, dt),
        "disk_write_Bps": _rate(disk.write_bytes, prev.disk.write_bytes if prev.disk else None, dt),
        "disk_read_IOPS": _rate(disk.read_count, prev.disk.read_count if prev.disk else None, dt),
        "disk_write_IOPS": _rate(disk.write_count, prev.disk.write_count if prev.disk else None, dt),

        "net_sent_Bps": _rate(net.bytes_sent, prev.net.bytes_sent if prev.net else None, dt),
        "net_recv_Bps": _rate(net.bytes_recv, prev.net.bytes_recv if prev.net else None, dt),
        "net_sent_Pps": _rate(net.packets_sent, prev.net.packets_sent if prev.net else None, dt),
        "net_recv_Pps": _rate(net.packets_recv, prev.net.packets_recv if prev.net else None, dt),
    }

    prev.disk, prev.net, prev.ts = disk, net, t
    return out

def collect_tier0_5hz(out_csv: str, hz: int, duration_s: int):
    dt = 1.0 / hz
    samples = hz * duration_s

    prev = Prev()
    t0 = time.time()

    probe = sample_tier0(prev, dt)
    fieldnames = ["idx", "ts_unix_s", "t_rel_s"] + list(probe.keys())

    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()

        prev = Prev()
        for i in range(samples):
            ts = time.time()
            row = sample_tier0(prev, dt)
            w.writerow({"idx": i, "ts_unix_s": ts, "t_rel_s": ts - t0, **row})
            elapsed = time.time() - ts
            time.sleep(max(0.0, dt - elapsed))
PY

# -----------------------------
# 03_powermetrics_collect_5hz.sh
# -----------------------------
cat > "$CODE_DIR/03_powermetrics_collect_5hz.sh" <<'SH2'
#!/bin/bash
set -euo pipefail
OUT_RAW="${1:?Need output raw file path}"
SAMPLES="${2:-5000}"
INTERVAL_MS="${3:-200}"
sudo powermetrics -i "${INTERVAL_MS}" -n "${SAMPLES}" -f plist -s cpu_power,gpu_power,thermal > "${OUT_RAW}"
SH2
chmod +x "$CODE_DIR/03_powermetrics_collect_5hz.sh"

# -----------------------------
# 04_powermetrics_parse.py
# -----------------------------
cat > "$CODE_DIR/04_powermetrics_parse.py" <<'PY'
import csv, math, plistlib
from typing import Any, Dict, List
from 00_config import TIER1_FIELDS

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
PY

# -----------------------------
# 99_run_all_end_to_end.py
# -----------------------------
cat > "$CODE_DIR/99_run_all_end_to_end.py" <<'PY'
import argparse, json, time, threading, subprocess, platform
from pathlib import Path

from 00_config import all_cases, WORKLOADS, STRESSORS, HZ, DT, SEED
from 01_workloads import run_workload, run_stressor
from 02_tier0_collect import collect_tier0_5hz
from 04_powermetrics_parse import parse_powermetrics_to_csv

OUT = Path("/Users/hsiaopingni/ITC_2026_M2Pro_DATA")
CODE = Path("/Users/hsiaopingni/ITC_2026_M2Pro_CODE")

def mkdirp(p: Path): p.mkdir(parents=True, exist_ok=True)

def make_run_id(workload: str, stressor: str) -> str:
    return f"{time.strftime('%Y%m%d_%H%M%S')}__{workload}__{stressor}"

def append_manifest(row: dict):
    import csv
    mf = OUT / "manifest.csv"
    exists = mf.exists()
    with mf.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(row.keys()))
        if not exists:
            w.writeheader()
        w.writerow(row)

def run_one(workload: str, stressor: str, duration_s: int):
    label = "NOMINAL" if stressor == "NOMINAL" else "ANOMALY"
    rid = make_run_id(workload, stressor)

    # directories
    t0 = OUT / "tier0" / rid
    t1 = OUT / "tier1" / rid
    meta_dir = OUT / "meta" / rid
    logs = OUT / "logs" / rid
    for d in [t0, t1, meta_dir, logs]:
        mkdirp(d)

    meta = {
        "run_id": rid,
        "workload": workload,
        "stressor": stressor,
        "label": label,
        "duration_s": duration_s,
        "hz": HZ,
        "seed": SEED,
        "platform": platform.platform(),
        "ai_mode": "numpy+torch(mps if available)",
        "video_mode": "software pipeline (no external files)",
    }

    # start workload + stressor threads
    stop_evt = threading.Event()
    th_w = threading.Thread(target=run_workload, args=(workload, stop_evt), daemon=True)
    th_s = threading.Thread(target=run_stressor, args=(stressor, stop_evt), daemon=True)
    th_w.start(); th_s.start()

    # Tier-1 raw capture (exact sample count)
    samples_target = HZ * duration_s
    raw_plistnul = t1 / "powermetrics_raw.plistnul"
    cmd_t1 = ["bash", str(CODE / "03_powermetrics_collect_5hz.sh"), str(raw_plistnul), str(samples_target), "200"]
    with (logs / "tier1_collect.log").open("w") as lf:
        p1 = subprocess.Popen(cmd_t1, stdout=lf, stderr=subprocess.STDOUT)

    # Tier-0 capture
    tier0_csv = t0 / "tier0_5hz.csv"
    collect_tier0_5hz(str(tier0_csv), hz=HZ, duration_s=duration_s)

    # stop workload/stressor
    stop_evt.set()
    th_w.join(timeout=3)
    th_s.join(timeout=3)

    # wait for tier1
    p1.wait(timeout=600)

    # parse tier1 to exact row count
    tier1_csv = t1 / "tier1_5hz.csv"
    parse_powermetrics_to_csv(str(raw_plistnul), str(tier1_csv), samples_target=samples_target)

    (meta_dir / "meta.json").write_text(json.dumps(meta, indent=2))

    append_manifest({
        "run_id": rid,
        "workload": workload,
        "stressor": stressor,
        "label": label,
        "duration_s": duration_s,
        "tier0_csv": str(tier0_csv),
        "tier1_csv": str(tier1_csv),
        "tier1_raw": str(raw_plistnul),
        "meta_json": str(meta_dir / "meta.json"),
    })

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["single", "all"], default="all")
    ap.add_argument("--workload", choices=WORKLOADS, default="PY_AI")
    ap.add_argument("--stressor", choices=STRESSORS, default="NOMINAL")
    ap.add_argument("--duration_s", type=int, default=1000)
    args = ap.parse_args()

    mkdirp(OUT / "tier0")
    mkdirp(OUT / "tier1")
    mkdirp(OUT / "meta")
    mkdirp(OUT / "logs")

    if args.mode == "single":
        run_one(args.workload, args.stressor, args.duration_s)
    else:
        for w in WORKLOADS:
            for s in STRESSORS:
                run_one(w, s, args.duration_s)

if __name__ == "__main__":
    main()
PY

echo "[OK] Wrote package to: $CODE_DIR"
echo "[OK] Files:"
ls -lah "$CODE_DIR" | sed -n '1,200p'
