"""Exercise notebook provenance/dispatch without executing experiments or cells."""

import ast
import json
from pathlib import Path
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = REPO_ROOT / "dice_results_analysis.ipynb"
DATASET = REPO_ROOT / "data generation" / "dataset" / "ITC_M2Pro_DATA"


def load_definitions(*names, namespace=None):
    """Load selected definitions only; never run notebook top-level workflows."""
    requested = set(names)
    nodes = []
    notebook = json.loads(NOTEBOOK.read_text())
    for cell in notebook["cells"]:
        if cell["cell_type"] != "code":
            continue
        tree = ast.parse("".join(cell["source"]))
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name in requested:
                    nodes.append(node)
            elif isinstance(node, ast.Assign):
                if any(isinstance(t, ast.Name) and t.id in requested for t in node.targets):
                    nodes.append(node)
    env = {"Path": Path, "json": json, "sys": sys}
    env.update(namespace or {})
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(NOTEBOOK), "exec"), env)
    missing = requested - env.keys()
    if missing:
        raise AssertionError(f"Missing notebook definitions: {sorted(missing)}")
    return env


class NotebookProvenanceTests(unittest.TestCase):
    def test_detector_context_wins_over_conflicting_historical_invocation(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            context = {"alpha": 0.05, "block_B": 90, "persist_k": 2}
            invocation = {"alpha": 0.02, "block_B": 60, "persist_k": 1}
            (folder / "run_context.json").write_text(json.dumps(context))
            history = folder / "notebook_invocation.json"
            history.write_text(json.dumps(invocation))
            original_history = history.read_bytes()
            env = load_definitions(
                "profile_operating_point",
                namespace={"profile_global_dir": lambda _: folder},
            )
            result = env["profile_operating_point"]("full")
            self.assertEqual(result["alpha"], 0.05)
            self.assertEqual(result["block_B"], 90)
            self.assertEqual(result["persist_k"], 2)
            self.assertEqual(result["operating_point_source"], "run_context.json")
            self.assertEqual(history.read_bytes(), original_history)

    def test_legacy_bundle_falls_back_to_invocation_and_missing_bundle_is_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            env = load_definitions(
                "profile_operating_point",
                namespace={"profile_global_dir": lambda _: folder},
            )
            self.assertEqual(env["profile_operating_point"]("mixed"), {})
            (folder / "notebook_invocation.json").write_text('{"alpha": 0.1}')
            result = env["profile_operating_point"]("mixed")
            self.assertEqual(result["alpha"], 0.1)
            self.assertEqual(result["operating_point_source"], "notebook_invocation.json")

    def test_invalid_authoritative_context_does_not_silently_use_stale_settings(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / "run_context.json").write_text("[]")
            (folder / "notebook_invocation.json").write_text('{"alpha": 0.02}')
            env = load_definitions(
                "profile_operating_point",
                namespace={"profile_global_dir": lambda _: folder},
            )
            with self.assertRaises(ValueError):
                env["profile_operating_point"]("full")

    def test_default_commands_reproduce_saved_settings_using_canonical_tool(self):
        calls = []
        env = load_definitions(
            "PAPER_OPERATING_POINTS", "PROFILE_OPERATING_POINT_OVERRIDES",
            "INCLUDE_TUNING", "USE_TUNED_ALERT_CONFIG", "paper_operating_point",
            "run_full_notebook", "default_full_out_dir",
            namespace={
                "REPO_ROOT": REPO_ROOT,
                "RUN_FULL_TOOL": REPO_ROOT / "tools" / "train_eval_dice_pipeline.py",
                "deterministic_env": lambda: {},
                "_run_checked": lambda cmd, **kwargs: calls.append((cmd, kwargs)),
            },
        )
        self.assertFalse(env["INCLUDE_TUNING"])
        self.assertFalse(env["USE_TUNED_ALERT_CONFIG"])
        for profile, folder in [("mixed", "results_dice_full"), ("full", "results_dice_full_full")]:
            with self.subTest(profile=profile):
                saved = json.loads((DATASET / folder / "run_context.json").read_text())
                settings = env["paper_operating_point"](profile)
                self.assertEqual(settings, {key: saved[key] for key in settings})
                result = env["run_full_notebook"](
                    DATASET, protocol="global", feature_profile=profile, **settings
                )
                command, options = calls[-1]
                self.assertEqual(command[1], str(REPO_ROOT / "tools" / "train_eval_dice_pipeline.py"))
                flags = dict(zip(command[2::2], command[3::2]))
                self.assertEqual(result, DATASET / folder)
                self.assertEqual(options["cwd"], REPO_ROOT)
                for key, value in settings.items():
                    self.assertEqual(float(flags[f"--{key}"]), value)

    def test_explicit_override_does_not_change_the_other_profile(self):
        env = load_definitions(
            "PAPER_OPERATING_POINTS", "PROFILE_OPERATING_POINT_OVERRIDES", "paper_operating_point"
        )
        env["PROFILE_OPERATING_POINT_OVERRIDES"]["mixed"] = {"alpha": 0.03}
        self.assertEqual(env["paper_operating_point"]("mixed")["alpha"], 0.03)
        self.assertEqual(env["paper_operating_point"]("full")["alpha"], 0.05)
        env["PROFILE_OPERATING_POINT_OVERRIDES"]["mixed"] = {"alhpa": 0.03}
        with self.assertRaises(ValueError):
            env["paper_operating_point"]("mixed")

    def test_default_workflow_dispatches_both_profiles_and_records_actual_settings(self):
        commands = []
        manifests = []

        def run_stage(_step, _total, _title, function, *args, **kwargs):
            kwargs.pop("detail", None)
            return function(*args, **kwargs)

        def save_manifest(*args):
            manifests.append(args[-1])
            return DATASET / "dry_run_manifest.json"

        env = load_definitions(
            "PAPER_OPERATING_POINTS", "PROFILE_OPERATING_POINT_OVERRIDES",
            "INCLUDE_TUNING", "USE_TUNED_ALERT_CONFIG", "paper_operating_point",
            "run_full_notebook", "default_full_out_dir", "RUN_END_TO_END", "RUN_HOLDOUT",
            "ALERT_TUNING_OBJECTIVE", "TUNED_ALERT_CONFIG_PATH",
            namespace={
                "REPO_ROOT": REPO_ROOT, "DATASET_ROOT": DATASET,
                "FEATURE_PROFILES_TO_SWEEP": ["mixed", "full"], "DISPLAY_FEATURE_PROFILE": "mixed",
                "RUN_FULL_TOOL": REPO_ROOT / "tools" / "train_eval_dice_pipeline.py",
                "deterministic_env": lambda: {}, "ensure_dataset_root": lambda _: None,
                "_run_checked": lambda cmd, **kwargs: commands.append(cmd),
                "run_analysis_notebook": lambda root, **kwargs: root / "analysis",
                "run_stage": run_stage, "update_progress": lambda *args: None,
                "write_run_manifest": save_manifest,
            },
        )
        notebook = json.loads(NOTEBOOK.read_text())
        blocks = [
            node
            for cell in notebook["cells"] if cell["cell_type"] == "code"
            for node in ast.parse("".join(cell["source"])).body
            if isinstance(node, ast.If) and isinstance(node.test, ast.Name)
            and node.test.id == "RUN_END_TO_END"
        ]
        self.assertEqual(len(blocks), 1)
        exec(compile(ast.Module(body=blocks, type_ignores=[]), str(NOTEBOOK), "exec"), env)
        self.assertEqual(len(commands), 4)  # Both global and holdout for each profile.
        self.assertEqual(len(manifests), 1)
        for profile in ("mixed", "full"):
            recorded = manifests[0]["profile_runs"][profile]["operating_point"]
            self.assertEqual(recorded, env["paper_operating_point"](profile))
        self.assertEqual(manifests[0]["block_B"], 45)
        self.assertEqual(manifests[0]["alpha"], 0.1)


if __name__ == "__main__":
    unittest.main()
