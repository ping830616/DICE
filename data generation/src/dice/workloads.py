import os, time, threading, random, zlib
import numpy as np
import urllib.request
from .cfg import SEED

def _seed_all():
    random.seed(SEED)
    np.random.seed(SEED)

def workload_browser(stop_evt: threading.Event):
    _seed_all()
    urls = ["https://example.com","https://www.iana.org/domains/reserved","https://www.wikipedia.org"]
    i = 0
    while not stop_evt.is_set():
        try:
            urllib.request.urlopen(urls[i % len(urls)], timeout=5).read(200_000)
        except Exception:
            pass
        i += 1
        time.sleep(0.05)

def workload_video_sw(stop_evt: threading.Event):
    _seed_all()
    H, W = 720, 1280
    frame = (np.random.rand(H, W, 3) * 255).astype(np.uint8)
    while not stop_evt.is_set():
        gray = (0.299 * frame[:,:,0] + 0.587 * frame[:,:,1] + 0.114 * frame[:,:,2]).astype(np.uint8)
        small = gray[::2, ::2]
        comp = zlib.compress(small.tobytes(), level=1)
        _ = zlib.decompress(comp)
        frame = (frame + 1) % 255
        time.sleep(0.005)

def workload_ai_numpy_torch(stop_evt: threading.Event, phase_s: float = 5.0):
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
        while time.time() < end_t and (not stop_evt.is_set()):
            c = a_t @ b_t
            s = c.sum()
            if device.type == "cpu":
                _ = float(s.item())

    def numpy_phase(end_t):
        while time.time() < end_t and (not stop_evt.is_set()):
            _ = a_np @ b_np

    while not stop_evt.is_set():
        t0 = time.time()
        torch_phase(t0 + phase_s)
        if stop_evt.is_set(): break
        t1 = time.time()
        numpy_phase(t1 + phase_s)

def workload_stats_streaming(stop_evt: threading.Event):
    _seed_all()
    x = np.random.rand(100_000_000).astype(np.float32)
    while not stop_evt.is_set():
        _ = float(x.sum()); _ = float(x.mean())
        x[::16] += 1.0

def run_workload(workload: str, stop_evt: threading.Event):
    if workload == "BROWSER": return workload_browser(stop_evt)
    if workload == "VIDEO_SW": return workload_video_sw(stop_evt)
    if workload == "PY_AI": return workload_ai_numpy_torch(stop_evt, phase_s=5.0)
    if workload == "PY_STATS": return workload_stats_streaming(stop_evt)
    raise ValueError(f"Unknown workload: {workload}")

def run_stressor(stressor: str, stop_evt: threading.Event):
    _seed_all()
    if stressor == "NOMINAL":
        while not stop_evt.is_set(): time.sleep(0.2)
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
            if r & 1: x += 3
            elif r & 2: x -= 2
            elif r & 4: x ^= r
            else: x += 1

    elif stressor == "ATOMIC":
        lock = threading.Lock()
        counter = 0
        def worker():
            nonlocal counter
            while not stop_evt.is_set():
                with lock:
                    counter += 1
        threads = [threading.Thread(target=worker, daemon=True) for _ in range(max(2, os.cpu_count() // 2))]
        for th in threads: th.start()
        while not stop_evt.is_set(): time.sleep(0.05)

    else:
        raise ValueError(f"Unknown stressor: {stressor}")
