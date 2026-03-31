#!/usr/bin/env python3
"""Run a workload plus a matched anomaly, then exit cleanly or crash."""

from __future__ import annotations

import argparse
import os
import sys
import threading
import time
from dataclasses import dataclass
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from dice.cfg import ANOMALOUS_STRESSORS
    from dice.workloads import run_base_stressor, run_base_workload
else:
    from .cfg import ANOMALOUS_STRESSORS
    from .workloads import run_base_stressor, run_base_workload


DEFAULT_WARMUP_S = 45.0
DEFAULT_RAMP_S = 120.0
DEFAULT_HOLD_S = 45.0


@dataclass(frozen=True)
class WrapperConfig:
    workload: str
    stressor: str
    mode: str
    warmup_s: float
    ramp_s: float
    hold_s: float
    gui: bool
    dry_run: bool


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
        root.title("DICE Workload Crash Wrapper")
        root.geometry("720x220")
        root.configure(bg="#F8FAFC")
        title = tk.Label(
            root,
            text="DICE Workload-Matched Crash Wrapper",
            font=("Helvetica", 18, "bold"),
            bg="#F8FAFC",
            fg="#0F172A",
        )
        title.pack(pady=(20, 6))
        subtitle = tk.Label(
            root,
            text="Dedicated user-space wrapper for workload crash collection. Save other work before abort runs.",
            font=("Helvetica", 11),
            bg="#F8FAFC",
            fg="#334155",
            wraplength=640,
            justify="center",
        )
        subtitle.pack(pady=(0, 10))
        label = tk.Label(
            root,
            text="Preparing workload...",
            font=("Helvetica", 14),
            bg="#F8FAFC",
            fg="#1D4ED8",
            wraplength=640,
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


def _join_thread(thread: threading.Thread | None, timeout: float = 3.0) -> None:
    if thread is None:
        return
    thread.join(timeout=timeout)


def run_wrapper(config: WrapperConfig) -> None:
    stop_evt = threading.Event()
    workload_thread = threading.Thread(
        target=run_base_workload,
        args=(config.workload, stop_evt),
        daemon=True,
    )
    stressor_thread: threading.Thread | None = None

    with StatusSink(config.gui) as sink:
        sink.update(
            f"[DICE workload-crash-wrapper] starting workload={config.workload} "
            f"stressor={config.stressor} mode={config.mode.upper()} "
            f"warmup={config.warmup_s:.0f}s ramp={config.ramp_s:.0f}s hold={config.hold_s:.0f}s"
        )
        workload_thread.start()
        start_s = time.perf_counter()
        last_status = ""
        stressor_started = False
        total_duration_s = max(0.0, config.warmup_s + config.ramp_s + config.hold_s)

        try:
            while True:
                elapsed = max(0.0, time.perf_counter() - start_s)
                if elapsed < config.warmup_s:
                    phase = "warmup"
                elif elapsed < config.warmup_s + config.ramp_s:
                    phase = "anomaly_ramp"
                elif elapsed < total_duration_s:
                    phase = "anomaly_hold"
                else:
                    phase = "complete"

                if (not stressor_started) and phase in {"anomaly_ramp", "anomaly_hold", "complete"}:
                    stressor_thread = threading.Thread(
                        target=run_base_stressor,
                        args=(config.stressor, stop_evt),
                        daemon=True,
                    )
                    stressor_thread.start()
                    stressor_started = True

                status = (
                    f"[DICE workload-crash-wrapper] workload={config.workload} "
                    f"stressor={config.stressor} phase={phase} elapsed={elapsed:.1f}s"
                )
                if status != last_status:
                    sink.update(status)
                    last_status = status

                if phase == "complete":
                    break
                time.sleep(0.25)

            if config.mode.upper() == "ABORT":
                sink.update(
                    f"[DICE workload-crash-wrapper] triggering real user-space crash for "
                    f"{config.workload} under {config.stressor}."
                )
                time.sleep(0.8)
                if config.dry_run:
                    sink.update("[DICE workload-crash-wrapper] dry-run mode enabled, skipping abort and exiting cleanly.")
                    sink.update("[DICE workload-crash-wrapper] abort scenario completed in dry-run mode.")
                else:
                    os.abort()
            else:
                sink.update("[DICE workload-crash-wrapper] control scenario completed with clean exit.")
        finally:
            stop_evt.set()
            _join_thread(stressor_thread)
            _join_thread(workload_thread)


def parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="Run a workload-matched crash wrapper for DICE crash-evidence collection.")
    ap.add_argument("--workload", required=True, choices=["BROWSER", "VIDEO_SW", "PY_AI", "PY_STATS"])
    ap.add_argument("--stressor", required=True, choices=list(ANOMALOUS_STRESSORS))
    ap.add_argument("--mode", required=True, choices=["control", "abort"])
    ap.add_argument("--warmup_s", "--warmup-s", dest="warmup_s", type=float, default=parse_float_env("DICE_MATCHED_WORKLOAD_CRASH_WARMUP_S", DEFAULT_WARMUP_S))
    ap.add_argument("--ramp_s", "--ramp-s", dest="ramp_s", type=float, default=parse_float_env("DICE_MATCHED_WORKLOAD_CRASH_RAMP_S", DEFAULT_RAMP_S))
    ap.add_argument("--hold_s", "--hold-s", dest="hold_s", type=float, default=parse_float_env("DICE_MATCHED_WORKLOAD_CRASH_HOLD_S", DEFAULT_HOLD_S))
    ap.add_argument("--gui", action="store_true", default=parse_bool_env("DICE_MATCHED_WORKLOAD_CRASH_GUI", False))
    ap.add_argument("--dry_run", "--dry-run", dest="dry_run", action="store_true", default=parse_bool_env("DICE_MATCHED_WORKLOAD_CRASH_DRY_RUN", False))
    return ap


def main() -> None:
    args = parser().parse_args()
    run_wrapper(
        WrapperConfig(
            workload=str(args.workload).upper(),
            stressor=str(args.stressor).upper(),
            mode=str(args.mode).upper(),
            warmup_s=float(args.warmup_s),
            ramp_s=float(args.ramp_s),
            hold_s=float(args.hold_s),
            gui=bool(args.gui),
            dry_run=bool(args.dry_run),
        )
    )


if __name__ == "__main__":
    main()
