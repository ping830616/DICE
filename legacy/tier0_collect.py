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
