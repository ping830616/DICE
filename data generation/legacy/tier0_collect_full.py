import csv, time, math
import psutil
from dataclasses import dataclass
from typing import Any, Dict, Optional

def _nan(): return float("nan")

def _rate(curr, prev, dt):
    if prev is None or dt <= 0:
        return _nan()
    return (curr - prev) / dt

def _safe_getattr(obj, name, default=_nan()):
    try:
        return float(getattr(obj, name))
    except Exception:
        return default

@dataclass
class Prev:
    disk_total: Optional[Any] = None
    net_total: Optional[Any] = None
    disk_per: Optional[Dict[str, Any]] = None
    net_per: Optional[Dict[str, Any]] = None
    ts: Optional[float] = None

def sample_tier0_full(prev: Prev, dt_default: float) -> Dict[str, float]:
    ts = time.time()
    dt = (ts - prev.ts) if prev.ts else dt_default
    out: Dict[str, float] = {}

    # CPU %
    out["cpu_pct"] = float(psutil.cpu_percent(interval=None))

    # CPU time breakdown (%)
    ct = psutil.cpu_times_percent(interval=None)
    for k in ["user","system","idle","nice","iowait","irq","softirq","steal","guest","guest_nice"]:
        out[f"cpu_times_{k}_pct"] = _safe_getattr(ct, k)

    # per-CPU utilization
    try:
        per = psutil.cpu_percent(interval=None, percpu=True)
        for i, v in enumerate(per):
            out[f"cpu{i}_pct"] = float(v)
    except Exception:
        pass

    # load averages
    try:
        l1, l5, l15 = psutil.getloadavg()
        out["load1"] = float(l1); out["load5"] = float(l5); out["load15"] = float(l15)
    except Exception:
        out["load1"] = _nan(); out["load5"] = _nan(); out["load15"] = _nan()

    # cpu_stats
    try:
        cs = psutil.cpu_stats()
        out["ctx_switches"] = float(cs.ctx_switches)
        out["interrupts"] = float(cs.interrupts)
        out["soft_interrupts"] = float(getattr(cs, "soft_interrupts", _nan()))
        out["syscalls"] = float(getattr(cs, "syscalls", _nan()))
    except Exception:
        pass

    # cpu freq
    try:
        cf = psutil.cpu_freq()
        out["cpu_freq_current_mhz"] = float(cf.current) if cf else _nan()
        out["cpu_freq_min_mhz"] = float(cf.min) if cf else _nan()
        out["cpu_freq_max_mhz"] = float(cf.max) if cf else _nan()
    except Exception:
        pass

    out["cpu_count_logical"] = float(psutil.cpu_count(logical=True) or _nan())
    out["cpu_count_physical"] = float(psutil.cpu_count(logical=False) or _nan())

    # memory
    vm = psutil.virtual_memory()
    for k in ["total","available","used","free","active","inactive","buffers","cached","shared","wired"]:
        out[f"mem_{k}_bytes"] = _safe_getattr(vm, k)
    out["mem_percent"] = float(vm.percent)

    sm = psutil.swap_memory()
    for k in ["total","used","free","sin","sout"]:
        out[f"swap_{k}_bytes"] = _safe_getattr(sm, k)
    out["swap_percent"] = float(sm.percent)

    # disk totals + per-disk
    disk_total = psutil.disk_io_counters(perdisk=False)
    out["disk_read_bytes_per_s"]  = _rate(disk_total.read_bytes,  prev.disk_total.read_bytes if prev.disk_total else None, dt)
    out["disk_write_bytes_per_s"] = _rate(disk_total.write_bytes, prev.disk_total.write_bytes if prev.disk_total else None, dt)
    out["disk_read_iops"]  = _rate(disk_total.read_count,  prev.disk_total.read_count if prev.disk_total else None, dt)
    out["disk_write_iops"] = _rate(disk_total.write_count, prev.disk_total.write_count if prev.disk_total else None, dt)
    prev.disk_total = disk_total

    try:
        disk_per = psutil.disk_io_counters(perdisk=True)
        prev_disk_per = prev.disk_per or {}
        for name, d in disk_per.items():
            pd = prev_disk_per.get(name)
            out[f"disk_{name}_read_Bps"]  = _rate(d.read_bytes,  pd.read_bytes if pd else None, dt)
            out[f"disk_{name}_write_Bps"] = _rate(d.write_bytes, pd.write_bytes if pd else None, dt)
            out[f"disk_{name}_read_IOPS"]  = _rate(d.read_count,  pd.read_count if pd else None, dt)
            out[f"disk_{name}_write_IOPS"] = _rate(d.write_count, pd.write_count if pd else None, dt)
        prev.disk_per = disk_per
    except Exception:
        pass

    # disk usage root
    try:
        du = psutil.disk_usage("/")
        out["disk_root_total_bytes"] = float(du.total)
        out["disk_root_used_bytes"] = float(du.used)
        out["disk_root_free_bytes"] = float(du.free)
        out["disk_root_used_percent"] = float(du.percent)
    except Exception:
        pass

    # net totals + per-nic
    net_total = psutil.net_io_counters(pernic=False)
    out["net_sent_Bps"] = _rate(net_total.bytes_sent, prev.net_total.bytes_sent if prev.net_total else None, dt)
    out["net_recv_Bps"] = _rate(net_total.bytes_recv, prev.net_total.bytes_recv if prev.net_total else None, dt)
    out["net_sent_Pps"] = _rate(net_total.packets_sent, prev.net_total.packets_sent if prev.net_total else None, dt)
    out["net_recv_Pps"] = _rate(net_total.packets_recv, prev.net_total.packets_recv if prev.net_total else None, dt)
    out["net_errin_per_s"]  = _rate(net_total.errin,  prev.net_total.errin if prev.net_total else None, dt)
    out["net_errout_per_s"] = _rate(net_total.errout, prev.net_total.errout if prev.net_total else None, dt)
    out["net_dropin_per_s"]  = _rate(net_total.dropin,  prev.net_total.dropin if prev.net_total else None, dt)
    out["net_dropout_per_s"] = _rate(net_total.dropout, prev.net_total.dropout if prev.net_total else None, dt)
    prev.net_total = net_total

    try:
        net_per = psutil.net_io_counters(pernic=True)
        prev_net_per = prev.net_per or {}
        for nic, n in net_per.items():
            pn = prev_net_per.get(nic)
            out[f"net_{nic}_sent_Bps"] = _rate(n.bytes_sent, pn.bytes_sent if pn else None, dt)
            out[f"net_{nic}_recv_Bps"] = _rate(n.bytes_recv, pn.bytes_recv if pn else None, dt)
            out[f"net_{nic}_sent_Pps"] = _rate(n.packets_sent, pn.packets_sent if pn else None, dt)
            out[f"net_{nic}_recv_Pps"] = _rate(n.packets_recv, pn.packets_recv if pn else None, dt)
        prev.net_per = net_per
    except Exception:
        pass

    # misc
    try:
        out["pids_count"] = float(len(psutil.pids()))
    except Exception:
        out["pids_count"] = _nan()

    try:
        out["users_count"] = float(len(psutil.users()))
    except Exception:
        out["users_count"] = _nan()

    out["uptime_s"] = float(ts - psutil.boot_time())

    prev.ts = ts
    return out

def collect_tier0_full(out_csv: str, hz: int, duration_s: int):
    dt = 1.0 / hz
    samples = hz * duration_s
    prev = Prev()
    t0 = time.time()

    probe = sample_tier0_full(prev, dt)
    fieldnames = ["idx", "ts_unix_s", "t_rel_s"] + list(probe.keys())

    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()

        prev = Prev()
        for i in range(samples):
            ts = time.time()
            row = sample_tier0_full(prev, dt)
            w.writerow({"idx": i, "ts_unix_s": ts, "t_rel_s": ts - t0, **row})
            elapsed = time.time() - ts
            time.sleep(max(0.0, dt - elapsed))
