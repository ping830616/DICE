"""Separate paired crash evidence from retrospective comparisons."""
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from early_warning_analysis import (
    compute_early_warning_metrics, merge_warning_and_crash, normalize_crash_manifest,
)


class TimingProvenanceTests(unittest.TestCase):
    def warning(self, case_id="W__S"):
        return pd.DataFrame([dict(
            case_id=case_id, workload="W", stressor="S", feature_profile="mixed",
            profile_label="Mixed", config="tier0", config_label="Tier-0",
            first_warning_s=45., warning_available=1, run_duration_s=999.,
        )])

    def manifest(self, **extra):
        row = dict(case_id="W__S", workload="W", stressor="S",
                   crash_outcome_observed=1, crash_detected=1,
                   crash_time_s=167., monitor_duration_s=245.)
        row.update(extra)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "crash.csv"
            pd.DataFrame([row]).to_csv(path, index=False)
            return normalize_crash_manifest(path)

    def test_separate_pilot_is_offset_not_crash_prediction(self):
        merged = merge_warning_and_crash(self.warning(), self.manifest(pilot_case_id_original="W__S_ABORT"))
        self.assertEqual(merged.iloc[0]["retrospective_offset_s"], 122.)
        self.assertTrue(np.isnan(merged.iloc[0]["lead_time_s"]))
        overall, _ = compute_early_warning_metrics(merged)
        row = overall.iloc[0]
        self.assertEqual(row["retrospective_crashes"], 1)
        self.assertEqual(row["observed_crashes"], 0)
        self.assertEqual(row["median_retrospective_offset_s"], 122.)
        self.assertTrue(np.isnan(row["warning_recall_before_crash"]))

    def test_unchanged_nominal_id_still_belongs_to_separate_pilot(self):
        merged = merge_warning_and_crash(self.warning(), self.manifest(
            pilot_case_id_original="W__S", crash_detected=0, crash_time_s=np.nan))
        overall, _ = compute_early_warning_metrics(merged)
        self.assertEqual(overall.iloc[0]["observed_noncrashes"], 0)
        self.assertEqual(merged.iloc[0]["warning_without_observed_crash"], 0)

    def test_direct_pilot_preserves_actual_interval(self):
        merged = merge_warning_and_crash(self.warning(), self.manifest())
        self.assertEqual(merged.iloc[0]["lead_time_s"], 122.)
        self.assertEqual(merged.iloc[0]["warning_before_crash"], 1)
        overall, _ = compute_early_warning_metrics(merged)
        self.assertEqual(overall.iloc[0]["warning_recall_before_crash"], 1.)
        self.assertEqual(overall.iloc[0]["retrospective_crashes"], 0)

    def test_missing_manifest_has_no_outcome(self):
        merged = merge_warning_and_crash(self.warning(), pd.DataFrame())
        self.assertEqual(merged.iloc[0]["timing_alignment"], "unobserved")
        overall, _ = compute_early_warning_metrics(merged)
        self.assertEqual(overall.iloc[0]["observed_outcomes"], 0)

    def test_mixed_sources_do_not_dilute_paired_metrics(self):
        direct = merge_warning_and_crash(self.warning(), self.manifest())
        retrospective = merge_warning_and_crash(self.warning(), self.manifest(
            pilot_case_id_original="W__S_ABORT", crash_time_s=20.))
        overall, _ = compute_early_warning_metrics(pd.concat([direct, retrospective], ignore_index=True))
        self.assertEqual(overall.iloc[0]["median_lead_time_s"], 122.)
        self.assertEqual(overall.iloc[0]["median_retrospective_offset_s"], -25.)
        self.assertEqual(overall.iloc[0]["warning_recall_before_crash"], 1.)

    def test_combined_manifest_preserves_direct_noncrash_with_same_id(self):
        records = pd.DataFrame([
            dict(case_id="W__S", crash_detected=0, crash_time_s=np.nan,
                 crash_outcome_observed=1, monitor_duration_s=245.),
            dict(case_id="W__S", pilot_case_id_original="W__S_ABORT",
                 crash_detected=1, crash_time_s=167., crash_outcome_observed=1,
                 monitor_duration_s=245.),
        ])
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "combined.csv"
            records.to_csv(path, index=False)
            crash = normalize_crash_manifest(path)
        self.assertEqual(len(crash), 2)
        aligned = merge_warning_and_crash(self.warning(), crash)
        overall, _ = compute_early_warning_metrics(aligned)
        row = overall.iloc[0]
        self.assertEqual(row["observed_noncrashes"], 1)
        self.assertEqual(row["retrospective_crashes"], 1)
        self.assertEqual(row["warning_precision"], 0.)


if __name__ == "__main__":
    unittest.main()
