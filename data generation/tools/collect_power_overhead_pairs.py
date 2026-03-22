#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import os
import sys
import tempfile
import threading
import time
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_GEN_ROOT = PROJECT_ROOT / "data generation"
os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "dice-mplconfig"))

sys.path.insert(0, str(DATA_GEN_ROOT / "src"))
sys.path.insert(0, str(DATA_GEN_ROOT / "legacy"))

from dice.cfg import HZ, WORKLOADS
from dice.tier1_alt_macmon import (  # type: ignore[attr-defined]
    _reader_thread,
    _start_macmon_process,
    build_global_schema as build_tier1_alt_schema,
    extract_core,
    parse_with_schema,
)
import dice.workloads as dw
from tier0_collect_full import Prev as Tier0Prev, sample_tier0_full


def load_pipeline_module():
    module_path = PROJECT_ROOT / "tools" / "train_eval_dice_pipeline.py"
    module_name = "dice_train_eval_runtime"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load DICE pipeline module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


PIPELINE = load_pipeline_module()


def workload_ai_numpy_torch_fallback(stop_evt: threading.Event, phase_s: float = 5.0):
    dw._seed_all()
    try:
        import torch

        torch.manual_seed(dw.SEED)
        mps_ok = hasattr(torch.backends, "mps") and torch.backends.mps.is_available()
        device = torch.device("mps" if mps_ok else "cpu")

        n_numpy = 1024
        n_torch = 2048
        a_np = np.random.randn(n_numpy, n_numpy).astype(np.float32)
        b_np = np.random.randn(n_numpy, n_numpy).astype(np.float32)
        a_t = torch.randn((n_torch, n_torch), device=device, dtype=torch.float32)
        b_t = torch.randn((n_torch, n_torch), device=device, dtype=torch.float32)

        def torch_phase(end_t: float):
            while time.time() < end_t and (not stop_evt.is_set()):
                c = a_t @ b_t
                s = c.sum()
                if device.type == "cpu":
                    _ = float(s.item())

        def numpy_phase(end_t: float):
            while time.time() < end_t and (not stop_evt.is_set()):
                _ = a_np @ b_np

        while not stop_evt.is_set():
            t0 = time.time()
            torch_phase(t0 + phase_s)
            if stop_evt.is_set():
                break
            numpy_phase(time.time() + phase_s)

    except ModuleNotFoundError:
        n = 1536
        a = np.random.randn(n, n).astype(np.float32)
        b = np.random.randn(n, n).astype(np.float32)
        while not stop_evt.is_set():
            _ = a @ b


def run_workload_safe(workload: str, stop_evt: threading.Event):
    if workload == "PY_AI":
        return workload_ai_numpy_torch_fallback(stop_evt, phase_s=5.0)
    return dw.run_workload(workload, stop_evt)


@dataclass
class RuntimeConfig:
    dataset_root: Path
    feature_profile: str
    config_name: str
    fit_ratio: float
    block_B: int
    alpha: float
    gain: float
    ridge_lambda: float
    runtime_hz: int


class LiveDiceRuntime:
    def __init__(
        self,
        bundle,
        runtime_cfg: RuntimeConfig,
        out_csv: Path,
    ) -> None:
        self.bundle = bundle
        self.runtime_cfg = runtime_cfg
        self.out_csv = out_csv
        self.prev = Tier0Prev()
        self.dt = 1.0 / float(runtime_cfg.runtime_hz)
        self.tier0_names = [name.split(":", 1)[1] for name in bundle.feature_names if name.startswith("tier0:")]
        self.tier1_names = [name.split(":", 1)[1] for name in bundle.feature_names if name.startswith("tier1_alt:")]

    def _live_vector(self, tier1_snapshot: Dict[str, float]) -> np.ndarray:
        raw_tier0 = sample_tier0_full(self.prev, self.dt)
        raw_tier1 = extract_core(tier1_snapshot)
        vals: List[float] = []
        for name in self.tier0_names:
            vals.append(float(raw_tier0.get(name, math.nan)))
        for name in self.tier1_names:
            vals.append(float(raw_tier1.get(name, math.nan)))
        x = np.asarray(vals, dtype=float)
        bad = ~np.isfinite(x)
        if np.any(bad):
            x[bad] = self.bundle.median[bad]
        return x

    def run(self, stop_evt: threading.Event, tier1_state: dict, duration_s: int) -> None:
        self.out_csv.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = [
            "idx",
            "ts_unix_s",
            "t_rel_s",
            "score",
            "pvalue",
            "residual_l2",
            "runtime_ms",
        ]
        z = None
        residual_hist: deque[np.ndarray] = deque(maxlen=self.runtime_cfg.block_B)
        samples_target = self.runtime_cfg.runtime_hz * duration_s
        t0 = time.time()

        # Warm psutil counters once before the timed loop.
        _ = sample_tier0_full(self.prev, self.dt)

        with self.out_csv.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            for idx in range(samples_target):
                if stop_evt.is_set():
                    break
                step_start = time.time()
                with tier1_state["lock"]:
                    snap = dict(tier1_state["last_kv"]) if tier1_state["last_kv"] else {}
                x = self._live_vector(snap)
                x_norm = (x - self.bundle.median) / (self.bundle.scale + 1e-12)

                score = 0.0
                pvalue = 1.0
                resid_l2 = 0.0
                if z is None:
                    z = x_norm.copy()
                else:
                    z_pred = z @ self.bundle.A
                    residual = x_norm - z_pred
                    resid_l2 = float(np.linalg.norm(residual))
                    residual_hist.append(np.abs(residual))
                    signature = np.mean(np.vstack(residual_hist), axis=0)
                    score = float(signature @ self.bundle.weights)
                    pvalue = float((1.0 + np.sum(self.bundle.cal_scores >= score)) / (len(self.bundle.cal_scores) + 1.0))
                    z = z_pred + self.runtime_cfg.gain * residual

                runtime_ms = (time.time() - step_start) * 1000.0
                now = time.time()
                writer.writerow(
                    {
                        "idx": idx,
                        "ts_unix_s": now,
                        "t_rel_s": now - t0,
                        "score": score,
                        "pvalue": pvalue,
                        "residual_l2": resid_l2,
                        "runtime_ms": runtime_ms,
                    }
                )
                sleep_s = self.dt - (time.time() - step_start)
                if sleep_s > 0:
                    time.sleep(sleep_s)


def prepare_bundle(runtime_cfg: RuntimeConfig):
    if runtime_cfg.config_name not in PIPELINE.CONFIGS:
        raise ValueError(f"Unsupported runtime config: {runtime_cfg.config_name}")

    tiers = PIPELINE.CONFIGS[runtime_cfg.config_name]
    tier_files = PIPELINE.FEATURE_PROFILES[runtime_cfg.feature_profile]
    feature_map = {
        tier: PIPELINE.common_features_per_tier(runtime_cfg.dataset_root, tier, tier_files)
        for tier in tiers
    }

    benign_runs: Dict[str, np.ndarray] = {}
    feature_names: List[str] | None = None
    for workload in WORKLOADS:
        case = PIPELINE.CaseRef(workload, "NOMINAL")
        X, names = PIPELINE.build_case_matrix(
            runtime_cfg.dataset_root,
            case,
            tiers,
            feature_map,
            tier_files,
            source_hz=HZ,
        )
        benign_runs[case.case_id] = X
        feature_names = names

    if feature_names is None:
        raise RuntimeError("Failed to prepare a benign DICE runtime bundle.")

    return PIPELINE.train_bundle(
        benign_runs,
        feature_names,
        fit_ratio=runtime_cfg.fit_ratio,
        B=runtime_cfg.block_B,
        alpha=runtime_cfg.alpha,
        gain=runtime_cfg.gain,
        ridge_lambda=runtime_cfg.ridge_lambda,
    )


def wait_for_macmon(state: dict, proc, tried: Sequence[str], timeout_s: float = 10.0) -> None:
    t_wait = time.time()
    while time.time() - t_wait < timeout_s:
        if proc.poll() is not None:
            break
        with state["lock"]:
            if state["seen"]:
                return
        time.sleep(0.05)

    stderr = ""
    try:
        if proc.poll() is None:
            proc.terminate()
        _, err = proc.communicate(timeout=2)
        stderr = (err or "").strip()
    except Exception:
        pass
    raise RuntimeError(
        "macmon started but no parseable telemetry was observed. "
        f"Tried commands: {tried}. stderr={stderr[:500]}"
    )


def collect_tier1_alt_raw(raw_jsonl: Path, tier1_state: dict, duration_s: int) -> None:
    raw_jsonl.parent.mkdir(parents=True, exist_ok=True)
    samples_target = HZ * duration_s
    dt = 1.0 / float(HZ)
    t0 = time.time()
    non_empty = 0

    with raw_jsonl.open("w") as handle:
        for idx in range(samples_target):
            ts = time.time()
            with tier1_state["lock"]:
                snap = dict(tier1_state["last_kv"]) if tier1_state["last_kv"] else {}
            if snap:
                non_empty += 1
            handle.write(
                json.dumps(
                    {
                        "idx": idx,
                        "ts_unix_s": ts,
                        "t_rel_s": ts - t0,
                        "metrics": snap,
                    }
                )
                + "\n"
            )
            sleep_s = dt - (time.time() - ts)
            if sleep_s > 0:
                time.sleep(sleep_s)

    if non_empty == 0:
        raise RuntimeError("macmon stream produced no usable samples.")


def ensure_manifest(pairs_root: Path) -> Path:
    pairs_root.mkdir(parents=True, exist_ok=True)
    rows = []
    for workload in WORKLOADS:
        for mode in ["baseline", "dice_on"]:
            rows.append(
                {
                    "workload": workload,
                    "mode": mode,
                    "csv_path": f"{workload}/{mode}/tier1_alt_full_5hz.csv",
                    "power_col": "sys_power",
                    "sample_hz": HZ,
                }
            )
    manifest_path = pairs_root / "manifest.csv"
    with manifest_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["workload", "mode", "csv_path", "power_col", "sample_hz"])
        writer.writeheader()
        writer.writerows(rows)
    return manifest_path


def collect_one(
    dataset_root: Path,
    pairs_root: Path,
    workload: str,
    mode: str,
    tier1_alt_bin: str,
    duration_s: int,
    runtime_cfg: RuntimeConfig | None,
    bundle,
) -> Path:
    out_dir = pairs_root / workload / mode
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_jsonl = out_dir / "macmon_raw.jsonl"
    core_csv = out_dir / "tier1_alt_core_5hz.csv"
    full_csv = out_dir / "tier1_alt_full_5hz.csv"
    runtime_csv = out_dir / "dice_runtime_trace.csv"
    meta_json = out_dir / "meta_power_overhead.json"
    schema_path = pairs_root / "tier1_alt_schema_global.json"

    proc, tried = _start_macmon_process(tier1_alt_bin)
    tier1_state = {
        "last_kv": {},
        "seen": False,
        "reader_error": None,
        "lock": threading.Lock(),
    }
    reader = threading.Thread(target=_reader_thread, args=(proc, tier1_state), daemon=True)
    reader.start()
    wait_for_macmon(tier1_state, proc, tried)

    stop_evt = threading.Event()
    workload_thread = threading.Thread(target=run_workload_safe, args=(workload, stop_evt), daemon=True)
    runtime_thread = None
    t0 = time.time()
    try:
        workload_thread.start()
        if mode == "dice_on":
            runtime = LiveDiceRuntime(bundle=bundle, runtime_cfg=runtime_cfg, out_csv=runtime_csv)
            runtime_thread = threading.Thread(
                target=runtime.run,
                args=(stop_evt, tier1_state, duration_s),
                daemon=True,
            )
            runtime_thread.start()

        collect_tier1_alt_raw(raw_jsonl, tier1_state, duration_s)
    finally:
        stop_evt.set()
        workload_thread.join(timeout=5)
        if runtime_thread is not None:
            runtime_thread.join(timeout=5)
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass

    if not schema_path.exists():
        build_tier1_alt_schema(str(raw_jsonl), str(schema_path), max_keys=300)

    parse_with_schema(
        str(raw_jsonl),
        str(core_csv),
        str(full_csv),
        str(schema_path),
        samples_target=HZ * duration_s,
    )

    meta = {
        "workload": workload,
        "mode": mode,
        "duration_s": duration_s,
        "hz": HZ,
        "tier1_alt_bin": tier1_alt_bin,
        "collector": "macmon",
        "raw_jsonl": str(raw_jsonl),
        "tier1_alt_core_csv": str(core_csv),
        "tier1_alt_full_csv": str(full_csv),
        "tier1_alt_schema": str(schema_path),
        "runtime_trace_csv": str(runtime_csv) if runtime_csv.exists() else None,
        "runtime_profile": runtime_cfg.config_name if runtime_cfg else None,
        "feature_profile": runtime_cfg.feature_profile if runtime_cfg else None,
        "elapsed_s": time.time() - t0,
    }
    meta_json.write_text(json.dumps(meta, indent=2) + "\n")
    return full_csv


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Collect benign-only paired Tier-1 power traces for baseline and live DICE-on overhead measurement."
    )
    ap.add_argument("--dataset_root", type=Path, default=PROJECT_ROOT / "data generation" / "dataset" / "ITC_M2Pro_DATA")
    ap.add_argument("--pairs_root", type=Path, default=None)
    ap.add_argument("--mode", choices=["baseline", "dice_on"], required=True)
    ap.add_argument("--workloads", nargs="+", default=WORKLOADS)
    ap.add_argument("--duration_s", type=int, default=1000)
    ap.add_argument("--tier1_alt_bin", default="macmon")
    ap.add_argument("--runtime_config", choices=["tier0", "tier0_tier1"], default="tier0_tier1")
    ap.add_argument("--feature_profile", choices=sorted(PIPELINE.FEATURE_PROFILES.keys()), default="mixed")
    ap.add_argument("--fit_ratio", type=float, default=0.6)
    ap.add_argument("--block_B", type=int, default=60)
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--gain", type=float, default=0.35)
    ap.add_argument("--ridge_lambda", type=float, default=1e-3)
    ap.add_argument("--runtime_hz", type=int, default=1)
    return ap.parse_args()


def main() -> None:
    args = parse_args()
    dataset_root = args.dataset_root.expanduser().resolve()
    pairs_root = args.pairs_root.expanduser().resolve() if args.pairs_root else dataset_root / "power_overhead_pairs"
    pairs_root.mkdir(parents=True, exist_ok=True)

    workloads = list(dict.fromkeys(args.workloads))
    bad = [w for w in workloads if w not in WORKLOADS]
    if bad:
        raise SystemExit(f"Unknown workloads: {bad}. Expected subset of {WORKLOADS}.")

    runtime_cfg = None
    bundle = None
    if args.mode == "dice_on":
        runtime_cfg = RuntimeConfig(
            dataset_root=dataset_root,
            feature_profile=args.feature_profile,
            config_name=args.runtime_config,
            fit_ratio=args.fit_ratio,
            block_B=args.block_B,
            alpha=args.alpha,
            gain=args.gain,
            ridge_lambda=args.ridge_lambda,
            runtime_hz=args.runtime_hz,
        )
        print(f"[DICE] Preparing live runtime bundle for {runtime_cfg.config_name} ({runtime_cfg.feature_profile})...")
        bundle = prepare_bundle(runtime_cfg)
        print(f"[DICE] Live runtime bundle ready with {len(bundle.feature_names)} features.")

    manifest_path = ensure_manifest(pairs_root)
    print(f"[DICE] Paired-overhead manifest: {manifest_path}")

    for workload in workloads:
        print(f"[DICE] Collecting {workload} / {args.mode} ...")
        full_csv = collect_one(
            dataset_root=dataset_root,
            pairs_root=pairs_root,
            workload=workload,
            mode=args.mode,
            tier1_alt_bin=args.tier1_alt_bin,
            duration_s=args.duration_s,
            runtime_cfg=runtime_cfg,
            bundle=bundle,
        )
        print(f"[DICE] Wrote: {full_csv}")


if __name__ == "__main__":
    main()
