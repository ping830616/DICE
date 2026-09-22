#!/usr/bin/env python3
"""Refresh derived CSV metadata from saved evidence, without fitting a detector.

This intentionally does not refresh figures or execute the notebook. It keeps
raw measurements and recorded invocation history unchanged.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))
from early_warning_analysis import (
    compute_early_warning_metrics, merge_warning_and_crash,
    normalize_crash_manifest, write_markdown_report,
)


def refresh(dataset_root: Path) -> None:
    paper = dataset_root / "results_itc_paper"
    comparison = paper / "comparison"
    contexts = {}
    for profile, folder in (("mixed", "results_dice_full"), ("full", "results_dice_full_full")):
        contexts[profile] = json.loads((dataset_root / folder / "run_context.json").read_text())

    for filename in ("conformal_reliability_profiles.csv", "conformal_reliability_by_workload_profiles.csv"):
        path = comparison / filename
        with path.open(newline="") as stream:
            reader = csv.DictReader(stream)
            fields = reader.fieldnames
            records = list(reader)
        for record in records:
            record["target_alpha"] = str(contexts[record["feature_profile"]]["alpha"])
        with path.open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
            writer.writeheader()
            writer.writerows(records)

    manifest_path = comparison / "early_warning_merged_crash_events.csv"
    crash = normalize_crash_manifest(manifest_path)
    profile_rows = []
    for profile in ("mixed", "full"):
        folder = paper / profile
        warnings = pd.read_csv(folder / "early_warning_case_summary.csv")
        aligned = merge_warning_and_crash(warnings, crash)
        overall, by_workload = compute_early_warning_metrics(aligned)
        aligned.to_csv(folder / "early_warning_crash_alignment.csv", index=False)
        aligned[aligned["crash_detected"].eq(1)].to_csv(
            folder / "early_warning_crash_alignment_pilot_cases.csv", index=False)
        overall.to_csv(folder / "early_warning_metrics.csv", index=False)
        by_workload.to_csv(folder / "early_warning_by_workload.csv", index=False)
        detection = pd.read_csv(folder / "anomaly_detection_metrics.csv")
        report_path = folder / "EARLY_WARNING_REPORT.md"
        write_markdown_report(report_path, detection, overall, aligned, manifest_path)
        try:
            display_path = manifest_path.relative_to(REPO_ROOT)
        except ValueError:
            display_path = Path(manifest_path.name)
        report_path.write_text(report_path.read_text().replace(str(manifest_path), str(display_path)))
        status_path = folder / "early_warning_status.json"
        status = json.loads(status_path.read_text())
        status["n_observed_crashes"] = int(overall.iloc[0]["observed_crashes"])
        status["n_retrospective_crashes"] = int(overall.iloc[0]["retrospective_crashes"])
        status["metadata_refresh"] = "Saved evidence only; no detector or pilot rerun. Figures require notebook regeneration."
        status_path.write_text(json.dumps(status, indent=2) + "\n")
        metrics = overall.iloc[0]
        d = detection.iloc[0]
        row = {key: d[key] for key in (
            "feature_profile", "profile_label", "config_label", "roc_auc", "pr_auc", "precision", "recall", "f1_score")}
        row.update({key: metrics[key] for key in (
            "observed_crashes", "warning_recall_before_crash", "median_lead_time_s", "false_alarm_rate_runs",
            "retrospective_alignment_cases", "retrospective_crashes", "median_retrospective_offset_s",
            "min_retrospective_offset_s", "max_retrospective_offset_s")})
        profile_rows.append(row)
    pd.DataFrame(profile_rows).to_csv(comparison / "early_warning_profile_summary.csv", index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-root", type=Path, default=REPO_ROOT / "data generation/dataset/ITC_M2Pro_DATA")
    refresh(parser.parse_args().dataset_root)
