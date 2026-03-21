#!/usr/bin/env python3
"""
Preflight check for the pinned DICE notebook environment.

This script is intended to run before executing `dice_results_analysis.ipynb`,
locally or in GitHub Actions. It verifies that:

- the repository-level Python pin from `environment.yml` is present
- the root `requirements.txt` packages are installed at the pinned versions
- overlapping pins in `data generation/requirements.txt` match the root pins
- the notebook and released dataset layout exist where expected
"""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import re
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET_ROOT = PROJECT_ROOT / "data generation" / "dataset" / "ITC_M2Pro_DATA"
DEFAULT_NOTEBOOK = PROJECT_ROOT / "dice_results_analysis.ipynb"
DEFAULT_ENV_YML = PROJECT_ROOT / "environment.yml"
DEFAULT_REQ_TXT = PROJECT_ROOT / "requirements.txt"
DEFAULT_DATA_REQ_TXT = PROJECT_ROOT / "data generation" / "requirements.txt"


def normalize_package_name(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name.strip().lower())


def parse_python_pin(environment_yml: Path) -> str | None:
    for raw_line in environment_yml.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        match = re.match(r"-\s*python=([^\s#]+)", line)
        if match:
            return match.group(1).strip()
    return None


def parse_requirements(path: Path, seen: set[Path] | None = None) -> dict[str, str]:
    seen = seen or set()
    path = path.resolve()
    if path in seen:
        return {}
    seen.add(path)

    pinned: dict[str, str] = {}
    for raw_line in path.read_text().splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue
        if line.startswith("-r "):
            include_path = (path.parent / line[3:].strip()).resolve()
            pinned.update(parse_requirements(include_path, seen=seen))
            continue
        if "==" not in line:
            raise ValueError(f"Unsupported requirement line in {path}: {raw_line}")
        package, version = [part.strip() for part in line.split("==", 1)]
        pinned[normalize_package_name(package)] = version
    return pinned


def installed_versions(expected: dict[str, str]) -> tuple[dict[str, str], list[dict[str, str]]]:
    versions: dict[str, str] = {}
    mismatches: list[dict[str, str]] = []
    for package, expected_version in sorted(expected.items()):
        try:
            actual = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            mismatches.append(
                {
                    "package": package,
                    "expected": expected_version,
                    "actual": "missing",
                    "ok": False,
                }
            )
            continue
        versions[package] = actual
        mismatches.append(
            {
                "package": package,
                "expected": expected_version,
                "actual": actual,
                "ok": actual == expected_version,
            }
        )
    return versions, mismatches


def dataset_status(dataset_root: Path) -> dict[str, object]:
    required = [
        dataset_root / "tier0",
        dataset_root / "tier1_alt",
        dataset_root / "tier2",
        dataset_root / "no_nan_report.json",
    ]
    missing = [str(path) for path in required if not path.exists()]
    return {
        "path": str(dataset_root),
        "missing": missing,
        "ok": not missing,
    }


def version_matches_prefix(actual: str, expected: str) -> bool:
    return actual == expected or actual.startswith(f"{expected}.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify the pinned DICE notebook environment before execution.")
    parser.add_argument("--repo-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--dataset-root", type=Path, default=DEFAULT_DATASET_ROOT)
    parser.add_argument("--notebook", type=Path, default=DEFAULT_NOTEBOOK)
    parser.add_argument("--environment-yml", type=Path, default=DEFAULT_ENV_YML)
    parser.add_argument("--requirements", type=Path, default=DEFAULT_REQ_TXT)
    parser.add_argument("--data-generation-requirements", type=Path, default=DEFAULT_DATA_REQ_TXT)
    parser.add_argument("--report-path", type=Path, default=None)
    parser.add_argument("--skip-installed-checks", action="store_true")
    parser.add_argument("--skip-dataset-check", action="store_true")
    args = parser.parse_args()

    repo_root = args.repo_root.expanduser().resolve()
    dataset_root = args.dataset_root.expanduser().resolve()
    notebook = args.notebook.expanduser().resolve()
    environment_yml = args.environment_yml.expanduser().resolve()
    requirements_txt = args.requirements.expanduser().resolve()
    data_requirements_txt = args.data_generation_requirements.expanduser().resolve()

    python_expected = parse_python_pin(environment_yml)
    python_actual = ".".join(str(part) for part in sys.version_info[:3])

    root_requirements = parse_requirements(requirements_txt)
    data_generation_requirements = parse_requirements(data_requirements_txt)

    overlap_mismatches = []
    for package, expected_version in sorted(data_generation_requirements.items()):
        root_version = root_requirements.get(package)
        if root_version is None:
            overlap_mismatches.append(
                {
                    "package": package,
                    "root": "missing",
                    "data_generation": expected_version,
                    "ok": False,
                }
            )
        else:
            overlap_mismatches.append(
                {
                    "package": package,
                    "root": root_version,
                    "data_generation": expected_version,
                    "ok": root_version == expected_version,
                }
            )

    installed = {}
    package_checks: list[dict[str, str]] = []
    if not args.skip_installed_checks:
        installed, package_checks = installed_versions(root_requirements)

    dataset = {"path": str(dataset_root), "missing": [], "ok": True}
    if not args.skip_dataset_check:
        dataset = dataset_status(dataset_root)

    python_ok = python_expected is not None and version_matches_prefix(python_actual, python_expected)
    package_ok = all(item["ok"] for item in package_checks) if package_checks else args.skip_installed_checks
    overlap_ok = all(item["ok"] for item in overlap_mismatches)
    notebook_ok = notebook.exists()
    env_ok = environment_yml.exists() and requirements_txt.exists() and data_requirements_txt.exists()
    dataset_ok = dataset["ok"]

    report = {
        "repo_root": str(repo_root),
        "notebook": {
            "path": str(notebook),
            "exists": notebook_ok,
        },
        "environment_files": {
            "environment_yml": str(environment_yml),
            "requirements_txt": str(requirements_txt),
            "data_generation_requirements_txt": str(data_requirements_txt),
            "exist": env_ok,
        },
        "python": {
            "expected": python_expected,
            "actual": python_actual,
            "ok": python_ok,
        },
        "requirements": {
            "root_count": len(root_requirements),
            "data_generation_count": len(data_generation_requirements),
            "installed_versions": installed,
            "package_checks": package_checks,
            "overlap_checks": overlap_mismatches,
            "installed_ok": package_ok,
            "overlap_ok": overlap_ok,
        },
        "dataset": dataset,
    }
    report["ok"] = all([env_ok, notebook_ok, python_ok, package_ok, overlap_ok, dataset_ok])

    if args.report_path is not None:
        report_path = args.report_path.expanduser().resolve()
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2) + "\n")

    print(f"Notebook path     : {notebook}")
    print(f"Python expected   : {python_expected}")
    print(f"Python actual     : {python_actual}")
    print(f"Root requirements : {len(root_requirements)} packages")
    print(f"Data-gen overlap  : {len(data_generation_requirements)} packages")
    if not args.skip_dataset_check:
        print(f"Dataset root      : {dataset_root}")
        if dataset["missing"]:
            print("Dataset missing   :", ", ".join(dataset["missing"]))
    if args.skip_installed_checks:
        print("Installed checks  : skipped")
    else:
        failed = [item for item in package_checks if not item["ok"]]
        print(f"Installed checks  : {len(package_checks) - len(failed)}/{len(package_checks)} pinned packages matched")

    overlap_failed = [item for item in overlap_mismatches if not item["ok"]]
    if overlap_failed:
        print("Overlap mismatches:")
        for item in overlap_failed:
            print(
                f"  - {item['package']}: root={item['root']} data_generation={item['data_generation']}"
            )

    if not report["ok"]:
        if not notebook_ok:
            print("Notebook check    : missing notebook file")
        if not env_ok:
            print("Environment check : missing environment file(s)")
        if not python_ok:
            print("Python check      : interpreter version does not match environment.yml")
        if not dataset_ok:
            print("Dataset check     : required dataset files/folders are missing")
        failed = [item for item in package_checks if not item["ok"]]
        if failed:
            print("Pinned package mismatches:")
            for item in failed:
                print(
                    f"  - {item['package']}: expected={item['expected']} actual={item['actual']}"
                )
        return 1

    print("Environment check : OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
