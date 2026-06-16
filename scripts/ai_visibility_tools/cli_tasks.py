from __future__ import annotations

import subprocess  # nosec B404
import sys
from collections.abc import Sequence
from pathlib import Path

from scripts import check_skeleton

REPO_ROOT = Path(__file__).resolve().parents[2]


def _run(command: Sequence[str], *, cwd: Path = REPO_ROOT) -> int:
    completed = subprocess.run(command, cwd=cwd, check=False)  # nosec B603
    return completed.returncode


def _run_many(commands: Sequence[tuple[Sequence[str], Path]]) -> int:
    for command, cwd in commands:
        returncode = _run(command, cwd=cwd)
        if returncode != 0:
            return returncode
    return 0


def main_check_skeleton() -> int:
    return check_skeleton.main()


def main_doctor() -> int:
    ruff_paths = ("apps", "tests", "scripts", "alembic")
    checks = _run_many(
        (
            ((sys.executable, "scripts/check_skeleton.py"), REPO_ROOT),
            (
                (sys.executable, "-m", "ruff", "check", *ruff_paths),
                REPO_ROOT,
            ),
            (
                (
                    sys.executable,
                    "-m",
                    "ruff",
                    "format",
                    "--check",
                    *ruff_paths,
                ),
                REPO_ROOT,
            ),
            (
                (
                    sys.executable,
                    "-m",
                    "bandit",
                    "-c",
                    "pyproject.toml",
                    "-r",
                    "apps",
                    "scripts",
                    "alembic",
                ),
                REPO_ROOT,
            ),
            ((sys.executable, "-m", "pyright", "--project", "pyproject.toml"), REPO_ROOT),
        )
    )
    if checks != 0:
        return checks
    return main_test_all()


def main_fix() -> int:
    ruff_paths = ("apps", "tests", "scripts", "alembic")
    return _run_many(
        (
            (
                (
                    sys.executable,
                    "-m",
                    "ruff",
                    "check",
                    "--fix",
                    *ruff_paths,
                ),
                REPO_ROOT,
            ),
            (
                (sys.executable, "-m", "ruff", "format", *ruff_paths),
                REPO_ROOT,
            ),
        )
    )


def main_precommit() -> int:
    args = tuple(sys.argv[1:]) or ("--all-files",)
    return _run(("pre-commit", "run", *args))


def main_test_all() -> int:
    unit = main_test_unit()
    if unit != 0:
        return unit
    service = main_test_service()
    if service != 0:
        return service
    integration = main_test_integration()
    if integration != 0:
        return integration
    return main_web_check()


def main_test_unit() -> int:
    return _run_unittest_discover("tests/unit")


def main_test_service() -> int:
    return _run_unittest_discover("tests/services")


def main_test_servcie() -> int:
    return main_test_service()


def main_test_integration() -> int:
    return _run_unittest_discover("tests/integration")


def _unittest_discover_command(start_dir: str) -> tuple[str, ...]:
    return (
        sys.executable,
        "-m",
        "unittest",
        "discover",
        "-s",
        start_dir,
        "-p",
        "test_*.py",
    )


def _run_unittest_discover(start_dir: str) -> int:
    test_root = REPO_ROOT / start_dir
    if not any(test_root.rglob("test_*.py")):
        print(f"No unittest tests found in {start_dir}; skipping")
        return 0
    return _run(_unittest_discover_command(start_dir))


def main_web_check() -> int:
    return _run((sys.executable, "scripts/run_web_check.py"))
