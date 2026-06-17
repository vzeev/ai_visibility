from __future__ import annotations

import subprocess  # nosec B404
import sys
from collections.abc import Sequence
from os import environ
from pathlib import Path
from shutil import which

from scripts import check_skeleton

REPO_ROOT = Path(__file__).resolve().parents[2]


def _run(
    command: Sequence[str],
    *,
    cwd: Path = REPO_ROOT,
    env: dict[str, str] | None = None,
) -> int:
    completed = subprocess.run(command, cwd=cwd, check=False, env=env)  # nosec B603
    return completed.returncode


def _run_many(
    commands: Sequence[tuple[Sequence[str], Path]],
    *,
    env: dict[str, str] | None = None,
) -> int:
    for command, cwd in commands:
        returncode = _run(command, cwd=cwd, env=env)
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


def main_demo_e2e() -> int:
    from scripts.ai_visibility_tools import demo_e2e

    return demo_e2e.main(tuple(sys.argv[1:]))


def main_dev() -> int:
    env_file = REPO_ROOT / ".env"
    if not env_file.is_file():
        print("Missing .env. Create it from .env.example before running `poetry run dev`.")
        return 1

    compose_env = _compose_env(env_file)
    compose = _compose_command()
    commands: tuple[tuple[Sequence[str], Path], ...] = (
        (
            (
                *compose,
                "build",
                "config-service",
                "visibility-service",
                "insights-service",
                "visibility-worker",
            ),
            REPO_ROOT,
        ),
        ((*compose, "up", "-d", "postgres"), REPO_ROOT),
        (
            (
                *compose,
                "run",
                "--rm",
                "config-service",
                "poetry",
                "run",
                "alembic",
                "-c",
                "alembic/alembic.ini",
                "upgrade",
                "head",
            ),
            REPO_ROOT,
        ),
        (
            (
                *compose,
                "up",
                "-d",
                "config-service",
                "visibility-service",
                "insights-service",
                "visibility-worker",
                "web",
            ),
            REPO_ROOT,
        ),
    )
    returncode = _run_many(commands, env=compose_env)
    if returncode != 0:
        return returncode

    print("Dev stack is running:")
    print(f"- UI: {_web_url(compose_env)}")
    print(f"- Config API: {compose_env['VITE_CONFIG_SERVICE_URL']}/docs")
    print(f"- Visibility API: {compose_env['VITE_VISIBILITY_SERVICE_URL']}/docs")
    print(f"- Insights API: {compose_env['VITE_INSIGHTS_SERVICE_URL']}/docs")
    print(f"Use `{' '.join(compose)} logs -f` to follow logs.")
    return 0


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


def _compose_env(env_file: Path) -> dict[str, str]:
    values = dict(environ)
    for key, value in _read_env_values(REPO_ROOT / ".env.example").items():
        values.setdefault(key, value)
    values.update(_read_env_values(env_file))
    values.setdefault("REPO_ENV_FILE", "./.env")
    values.setdefault("CONTAINER_ENV_FILE", "/app/.env")
    values.pop("OPENAI_API_KEY", None)
    values.pop("ENABLE_OPENAI", None)
    return values


def _compose_command() -> tuple[str, ...]:
    if which("docker-compose"):
        return ("docker-compose",)
    return ("docker", "compose")


def _read_env_values(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}

    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line.removeprefix("export ").lstrip()
        if "=" not in line:
            continue
        key, value = line.split("=", maxsplit=1)
        key = key.strip()
        if key:
            values[key] = _clean_env_value(value.strip())
    return values


def _clean_env_value(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    marker = " #"
    if marker in value:
        return value.split(marker, maxsplit=1)[0].rstrip()
    return value


def _web_url(compose_env: dict[str, str]) -> str:
    config_url = compose_env["VITE_CONFIG_SERVICE_URL"]
    config_port = compose_env["CONFIG_SERVICE_PORT"]
    web_port = compose_env["WEB_PORT"]
    return config_url.replace(f":{config_port}", f":{web_port}")
