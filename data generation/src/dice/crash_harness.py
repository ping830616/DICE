#!/usr/bin/env python3
"""Controlled user-space crash harness for safe crash-evidence collection."""

from __future__ import annotations

import argparse
import math
import os
import sys
import threading
import time
from dataclasses import dataclass


DEFAULT_WARMUP_S = 45.0
DEFAULT_RAMP_S = 120.0
DEFAULT_HOLD_S = 45.0
DEFAULT_MEMORY_STEP_MB = 32
DEFAULT_MAX_MEMORY_MB = 768
DEFAULT_CPU_THREADS = 2
DEFAULT_CPU_DUTY_MIN = 0.20
DEFAULT_CPU_DUTY_MAX = 0.92

CONTROL_SCENARIOS = {"NOMINAL", "MEM_RAMP_CONTROL", "CPU_RAMP_CONTROL"}
ABORT_SCENARIOS = {"MEM_RAMP_ABORT", "CPU_RAMP_ABORT"}


@dataclass(frozen=True)
class HarnessConfig:
    scenario: str
    warmup_s: float
    ramp_s: float
    hold_s: float
    memory_step_mb: int
    max_memory_mb: int
    cpu_threads: int
    cpu_duty_min: float
    cpu_duty_max: float
    gui: bool
    dry_run: bool


def now_s() -> float:
    return time.perf_counter()


def parse_bool_env(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def parse_float_env(name: str, default: float) -> float:
    value = os.environ.get(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def parse_int_env(name: str, default: int) -> int:
    value = os.environ.get(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def scenario_progress(start_s: float, warmup_s: float, ramp_s: float, hold_s: float) -> tuple[str, float]:
    elapsed = max(0.0, now_s() - start_s)
    if elapsed < warmup_s:
        frac = safe_div(elapsed, warmup_s)
        return "warmup", frac
    elapsed -= warmup_s
    if elapsed < ramp_s:
        frac = safe_div(elapsed, ramp_s)
        return "ramp", frac
    elapsed -= ramp_s
    if elapsed < hold_s:
        frac = safe_div(elapsed, hold_s)
        return "hold", frac
    return "complete", 1.0


def safe_div(num: float, den: float) -> float:
    if abs(float(den)) <= 1e-12:
        return 0.0
    return float(num) / float(den)


class StatusSink:
    def __init__(self, gui: bool) -> None:
        self.gui = bool(gui)
        self._label = None
        self._root = None

    def __enter__(self) -> "StatusSink":
        if not self.gui:
            return self
        try:
            import tkinter as tk
        except Exception:
            return self
        try:
            root = tk.Tk()
        except Exception:
            return self
        root.title("DICE Crash Harness")
        root.geometry("640x220")
        root.configure(bg="#F8FAFC")
        title = tk.Label(
            root,
            text="DICE Controlled Crash Harness",
            font=("Helvetica", 18, "bold"),
            bg="#F8FAFC",
            fg="#0F172A",
        )
        title.pack(pady=(20, 6))
        subtitle = tk.Label(
            root,
            text="Dedicated user-space crash test. Close other unsaved work before running crash scenarios.",
            font=("Helvetica", 11),
            bg="#F8FAFC",
            fg="#334155",
            wraplength=580,
            justify="center",
        )
        subtitle.pack(pady=(0, 10))
        label = tk.Label(
            root,
            text="Preparing scenario...",
            font=("Helvetica", 14),
            bg="#F8FAFC",
            fg="#1D4ED8",
            wraplength=580,
            justify="center",
        )
        label.pack(pady=10)
        self._root = root
        self._label = label
        self._pump()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self._root is not None:
            try:
                self._root.destroy()
            except Exception:
                pass
        self._root = None
        self._label = None

    def _pump(self) -> None:
        if self._root is None:
            return
        try:
            self._root.update_idletasks()
            self._root.update()
        except Exception:
            self._root = None
            self._label = None

    def update(self, text: str) -> None:
        print(text, flush=True)
        if self._label is not None:
            try:
                self._label.config(text=text)
            except Exception:
                self._label = None
        self._pump()


def run_mem_ramp(config: HarnessConfig, sink: StatusSink) -> None:
    chunks: list[bytearray] = []
    step_bytes = max(1, int(config.memory_step_mb)) * 1024 * 1024
    max_bytes = max(step_bytes, int(config.max_memory_mb) * 1024 * 1024)
    start_s = now_s()
    last_status = ""

    while True:
        phase, frac = scenario_progress(start_s, config.warmup_s, config.ramp_s, config.hold_s)
        target_frac = 0.0 if phase == "warmup" else (1.0 if phase in {"hold", "complete"} else clamp(frac, 0.0, 1.0))
        target_bytes = int(target_frac * max_bytes)
        while sum(len(chunk) for chunk in chunks) < target_bytes:
            block = bytearray(step_bytes)
            for idx in range(0, len(block), 4096):
                block[idx] = (idx // 4096) % 251
            chunks.append(block)
        current_mb = sum(len(chunk) for chunk in chunks) // (1024 * 1024)
        status = f"[DICE crash-harness] scenario={config.scenario} phase={phase} memory={current_mb}MB"
        if status != last_status:
            sink.update(status)
            last_status = status
        if phase == "complete":
            break
        time.sleep(0.25)


def busy_wait(duration_s: float) -> None:
    end = now_s() + max(0.0, duration_s)
    value = 0.0
    while now_s() < end:
        value += math.sin(value + 0.125)
    if value > 1e308:  # pragma: no cover
        print(value)


def run_cpu_ramp(config: HarnessConfig, sink: StatusSink) -> None:
    stop_evt = threading.Event()
    phase_lock = threading.Lock()
    phase_state = {"phase": "warmup", "frac": 0.0}

    def worker() -> None:
        cycle_s = 0.25
        while not stop_evt.is_set():
            with phase_lock:
                phase = phase_state["phase"]
                frac = phase_state["frac"]
            if phase == "warmup":
                duty = 0.10
            elif phase == "ramp":
                duty = config.cpu_duty_min + (config.cpu_duty_max - config.cpu_duty_min) * clamp(frac, 0.0, 1.0)
            else:
                duty = config.cpu_duty_max
            busy_wait(cycle_s * duty)
            remaining = cycle_s * (1.0 - duty)
            if remaining > 0.0:
                time.sleep(remaining)

    threads = [threading.Thread(target=worker, daemon=True) for _ in range(max(1, int(config.cpu_threads)))]
    for thread in threads:
        thread.start()

    start_s = now_s()
    last_status = ""
    try:
        while True:
            phase, frac = scenario_progress(start_s, config.warmup_s, config.ramp_s, config.hold_s)
            with phase_lock:
                phase_state["phase"] = phase
                phase_state["frac"] = frac
            if phase == "warmup":
                duty = 0.10
            elif phase == "ramp":
                duty = config.cpu_duty_min + (config.cpu_duty_max - config.cpu_duty_min) * clamp(frac, 0.0, 1.0)
            else:
                duty = config.cpu_duty_max
            status = (
                f"[DICE crash-harness] scenario={config.scenario} phase={phase} "
                f"threads={max(1, int(config.cpu_threads))} target_duty={100.0 * duty:.0f}%"
            )
            if status != last_status:
                sink.update(status)
                last_status = status
            if phase == "complete":
                break
            time.sleep(0.25)
    finally:
        stop_evt.set()
        for thread in threads:
            thread.join(timeout=1.0)


def run_nominal(config: HarnessConfig, sink: StatusSink) -> None:
    start_s = now_s()
    last_phase = ""
    while True:
        phase, _ = scenario_progress(start_s, config.warmup_s, config.ramp_s, config.hold_s)
        if phase != last_phase:
            sink.update(f"[DICE crash-harness] scenario={config.scenario} phase={phase} idle_control")
            last_phase = phase
        if phase == "complete":
            break
        time.sleep(0.25)


def should_abort(scenario: str) -> bool:
    return scenario in ABORT_SCENARIOS


def run_scenario(config: HarnessConfig) -> None:
    with StatusSink(config.gui) as sink:
        sink.update(
            f"[DICE crash-harness] starting scenario={config.scenario} "
            f"warmup={config.warmup_s:.0f}s ramp={config.ramp_s:.0f}s hold={config.hold_s:.0f}s"
        )
        if config.scenario in {"MEM_RAMP_CONTROL", "MEM_RAMP_ABORT"}:
            run_mem_ramp(config, sink)
        elif config.scenario in {"CPU_RAMP_CONTROL", "CPU_RAMP_ABORT"}:
            run_cpu_ramp(config, sink)
        elif config.scenario == "NOMINAL":
            run_nominal(config, sink)
        else:
            raise ValueError(f"Unknown crash-harness scenario: {config.scenario}")

        if should_abort(config.scenario):
            sink.update("[DICE crash-harness] triggering real user-space crash via os.abort()")
            time.sleep(0.8)
            if config.dry_run:
                sink.update("[DICE crash-harness] dry-run mode enabled, skipping abort and exiting cleanly.")
                return
            os.abort()

        sink.update("[DICE crash-harness] control scenario completed with clean exit.")


def build_config(args: argparse.Namespace) -> HarnessConfig:
    return HarnessConfig(
        scenario=args.scenario,
        warmup_s=float(args.warmup_s),
        ramp_s=float(args.ramp_s),
        hold_s=float(args.hold_s),
        memory_step_mb=int(args.memory_step_mb),
        max_memory_mb=int(args.max_memory_mb),
        cpu_threads=int(args.cpu_threads),
        cpu_duty_min=clamp(float(args.cpu_duty_min), 0.05, 0.95),
        cpu_duty_max=clamp(float(args.cpu_duty_max), 0.10, 0.98),
        gui=bool(args.gui),
        dry_run=bool(args.dry_run),
    )


def parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="Run a controlled user-space crash scenario for DICE crash-evidence collection.")
    ap.add_argument("--scenario", required=True, choices=["NOMINAL", "MEM_RAMP_CONTROL", "MEM_RAMP_ABORT", "CPU_RAMP_CONTROL", "CPU_RAMP_ABORT"])
    ap.add_argument("--warmup_s", "--warmup-s", dest="warmup_s", type=float, default=parse_float_env("DICE_CRASH_WARMUP_S", DEFAULT_WARMUP_S))
    ap.add_argument("--ramp_s", "--ramp-s", dest="ramp_s", type=float, default=parse_float_env("DICE_CRASH_RAMP_S", DEFAULT_RAMP_S))
    ap.add_argument("--hold_s", "--hold-s", dest="hold_s", type=float, default=parse_float_env("DICE_CRASH_HOLD_S", DEFAULT_HOLD_S))
    ap.add_argument("--memory_step_mb", "--memory-step-mb", dest="memory_step_mb", type=int, default=parse_int_env("DICE_CRASH_MEMORY_STEP_MB", DEFAULT_MEMORY_STEP_MB))
    ap.add_argument("--max_memory_mb", "--max-memory-mb", dest="max_memory_mb", type=int, default=parse_int_env("DICE_CRASH_MAX_MEMORY_MB", DEFAULT_MAX_MEMORY_MB))
    ap.add_argument("--cpu_threads", "--cpu-threads", dest="cpu_threads", type=int, default=parse_int_env("DICE_CRASH_CPU_THREADS", DEFAULT_CPU_THREADS))
    ap.add_argument("--cpu_duty_min", "--cpu-duty-min", dest="cpu_duty_min", type=float, default=parse_float_env("DICE_CRASH_CPU_DUTY_MIN", DEFAULT_CPU_DUTY_MIN))
    ap.add_argument("--cpu_duty_max", "--cpu-duty-max", dest="cpu_duty_max", type=float, default=parse_float_env("DICE_CRASH_CPU_DUTY_MAX", DEFAULT_CPU_DUTY_MAX))
    ap.add_argument("--gui", action="store_true", default=parse_bool_env("DICE_CRASH_HARNESS_GUI", False))
    ap.add_argument("--dry_run", "--dry-run", dest="dry_run", action="store_true")
    return ap


def main() -> None:
    args = parser().parse_args()
    run_scenario(build_config(args))


if __name__ == "__main__":
    main()
