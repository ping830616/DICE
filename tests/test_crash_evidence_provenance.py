"""Regression checks for pilot evidence provenance and causal time boundaries."""

import math
from pathlib import Path
import sys
import tempfile
import unittest

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import aggregate_itc_crash_bridge as bridge
import feature_crash_analysis as feature


class PilotProvenanceTests(unittest.TestCase):
    def test_original_reference_is_not_a_pilot_warning(self):
        remapped = pd.DataFrame([{
            "case_id": "PY_AI__CACHE", "pilot_case_id_original": "PY_AI__CACHE_ABORT",
            "first_warning_s": 45.0, "warning_top_feature_1": "original_feature",
        }])
        self.assertTrue(bridge.resolve_direct_pilot_warning(remapped, "PY_AI__CACHE_ABORT").empty)

    def test_exact_pilot_warning_is_retained(self):
        direct = pd.DataFrame([{"case_id": "PY_AI__CACHE_ABORT", "first_warning_s": 62.0}])
        self.assertEqual(bridge.resolve_direct_pilot_warning(direct, "PY_AI__CACHE_ABORT")["first_warning_s"], 62.0)

    def test_ambiguous_collection_does_not_choose_first_row(self):
        direct = pd.DataFrame([
            {"case_id": "PY_STATS__ATOMIC_ABORT", "phase": "tier0", "first_warning_s": 61.0},
            {"case_id": "PY_STATS__ATOMIC_ABORT", "phase": "tier2", "first_warning_s": 62.0},
        ])
        with self.assertRaisesRegex(ValueError, "Ambiguous pilot warning"):
            bridge.resolve_direct_pilot_warning(direct, "PY_STATS__ATOMIC_ABORT")

    def test_direct_display_export_supplies_pilot_evidence(self):
        with tempfile.TemporaryDirectory() as folder:
            expected = Path(folder) / "early_warning_case_summary.csv"
            alternate = expected.with_name("early_warning_crash_alignment_display.csv")
            pd.DataFrame([{
                "case_id": "PY_AI__CACHE_ABORT", "first_warning_s": 62.0,
                "warning_top_feature_1": "tier0:soft_interrupts",
            }]).to_csv(alternate, index=False)
            row, source = bridge.load_direct_pilot_warning(expected, "PY_AI__CACHE_ABORT")
            self.assertEqual(row["warning_top_feature_1"], "tier0:soft_interrupts")
            self.assertEqual(source, str(alternate))

    def test_lfs_pointer_is_not_treated_as_csv_evidence(self):
        with tempfile.TemporaryDirectory() as folder:
            expected = Path(folder) / "early_warning_case_summary.csv"
            expected.write_text("version https://git-lfs.github.com/spec/v1\noid sha256:abc\nsize 10\n")
            with self.assertWarnsRegex(RuntimeWarning, "Git LFS pointer"):
                row, source = bridge.load_direct_pilot_warning(expected, "PY_AI__CACHE_ABORT")
            self.assertTrue(row.empty)
            self.assertEqual(source, "")

    def test_saved_timing_survives_missing_direct_evidence_with_explicit_status(self):
        record = {"crash_pilot_anomaly_warning_s": 62.0, "crash_time_s": 214.0, "lead_time_s": 152.0}
        result = bridge.pilot_timing_provenance(record, pd.Series(dtype=object))
        self.assertEqual(result["pilot_warning_evidence_status"], "unavailable")
        self.assertEqual(result["pilot_warning_time_status"], "saved_value_unverified")
        self.assertEqual(record["crash_pilot_anomaly_warning_s"], 62.0)
        self.assertEqual(result["pilot_timing_conflicts"], "")

    def test_conflicting_crash_times_are_exposed_not_overwritten(self):
        record = {"crash_pilot_anomaly_warning_s": 62.0, "crash_time_s": 196.682946, "lead_time_s": 134.682946}
        result = bridge.pilot_timing_provenance(
            record, pd.Series({"first_warning_s": 62.0}), pd.Series({"crash_time_s": 194.496976}),
        )
        self.assertEqual(result["pilot_warning_time_status"], "agrees_with_direct_pilot")
        self.assertEqual(result["pilot_crash_time_status"], "conflict")
        self.assertIn("crash_time_conflict", result["pilot_timing_conflicts"])
        self.assertAlmostEqual(result["direct_minus_saved_crash_s"], -2.18597)
        self.assertEqual(record["crash_time_s"], 196.682946)

    def test_collect_retains_saved_timing_without_inventing_warning_features(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            feature_dir = root / "results_feature_crash_analysis" / "mixed"
            feature_dir.mkdir(parents=True)
            pd.DataFrame([{
                "workload": "PY_AI", "base_stressor": "CACHE", "original_case_id": "PY_AI__CACHE",
                "pilot_abort_case_id": "PY_AI__CACHE_ABORT", "pilot_control_case_id": "PY_AI__CACHE_CONTROL",
                "original_anomaly_warning_s": 45.0, "crash_pilot_anomaly_warning_s": 62.0,
                "crash_time_s": 214.0, "lead_time_s": 152.0, "anomaly_warning_shift_s": 17.0,
            }]).to_csv(feature_dir / "warning_bridge_summary.csv", index=False)
            pd.DataFrame(columns=["workload", "base_stressor"]).to_csv(feature_dir / "feature_onset_summary.csv", index=False)
            rows = bridge.collect_pilot_rows(root, "mixed")
            self.assertEqual(rows[0]["crash_pilot_anomaly_warning_s"], 62.0)
            self.assertEqual(rows[0]["crash_pilot_warning_top_feature_1"], "")
            self.assertEqual(rows[0]["pilot_warning_evidence_status"], "unavailable")


class PreCrashBoundaryTests(unittest.TestCase):
    def test_larger_post_crash_sample_is_excluded(self):
        samples = pd.DataFrame({"time_s": [1, 9, 11], "value": [1, -4, 100]})
        self.assertEqual(feature.peak_deviation(samples, 0.0, 1.0), (100.0, 11.0))
        self.assertEqual(feature.peak_deviation(samples, 0.0, 1.0, end_s=10.0), (4.0, 9.0))

    def test_no_known_crash_cannot_produce_pre_crash_peak(self):
        samples = pd.DataFrame({"time_s": [1], "value": [100]})
        peak, when = feature.peak_deviation(samples, 0.0, 1.0, end_s=float("nan"))
        self.assertTrue(math.isnan(peak) and math.isnan(when))

    def test_pre_crash_value_fallback_never_reads_future_sample(self):
        samples = pd.DataFrame({"time_s": [1, 101], "value": [3, 100]})
        self.assertEqual(feature.value_pre_crash(samples, 100.0), 3.0)
        self.assertTrue(math.isnan(feature.value_pre_crash(samples.iloc[1:], 100.0)))

    def test_legacy_peaks_keep_explicit_unrestricted_scope(self):
        data = pd.DataFrame([{
            "mode": "ABORT", "column_name": "swap", "feature_name": "tier0:swap",
            "peak_abs_z": 100.0, "feature_first_divergence_s": 1.0, "feature_value_pre_crash": 3.0,
        }])
        result = bridge.pick_peak_features(data)
        self.assertEqual(result["crash_peak_scope"], "recorded_series_unrestricted")
        data["pre_crash_peak_abs_z"] = [4.0]
        result = bridge.pick_peak_features(data)
        self.assertEqual(result["crash_peak_scope"], "pre_crash")
        self.assertEqual(result["crash_peak_feature_1_peak_abs_z"], 4.0)


if __name__ == "__main__":
    unittest.main()
