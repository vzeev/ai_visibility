from __future__ import annotations

import os
import re
from collections.abc import Collection, Iterable
from pathlib import Path

_ENV_KEY_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
DEFAULT_REPO_ENV_KEYS = frozenset(
    {
        "AI_VISIBILITY_ALLOW_DB_RESET",
        "AI_VISIBILITY_CORS_ORIGINS",
        "AI_VISIBILITY_DEMO_DATABASE_URL",
        "AI_VISIBILITY_DEMO_FAKE_TOKEN",
        "AI_VISIBILITY_TEST_DATABASE_URL",
        "CONFIG_SERVICE_PORT",
        "DATABASE_URL",
        "ENABLE_OPENAI",
        "INSIGHTS_SERVICE_PORT",
        "OPENAI_API_KEY",
        "POSTGRES_DB",
        "POSTGRES_HOST",
        "POSTGRES_PASSWORD",
        "POSTGRES_PORT",
        "POSTGRES_USER",
        "VITE_CONFIG_SERVICE_URL",
        "VITE_INSIGHTS_SERVICE_URL",
        "VITE_VISIBILITY_SERVICE_URL",
        "VISIBILITY_SERVICE_PORT",
        "WEB_PORT",
        "WORKER_MAX_ITEMS",
    }
)
REPO_AUTHORITATIVE_ENV_KEYS = frozenset({"ENABLE_OPENAI", "OPENAI_API_KEY"})


def bootstrap_repo_env(env_path: str | Path | None = None) -> Path | None:
    dotenv_path = load_repo_env(env_path)
    if dotenv_path is not None:
        load_repo_env(dotenv_path, override=True, keys=REPO_AUTHORITATIVE_ENV_KEYS)
    return dotenv_path


def load_repo_env(
    env_path: str | Path | None = None,
    *,
    override: bool = False,
    keys: Collection[str] | None = DEFAULT_REPO_ENV_KEYS,
) -> Path | None:
    dotenv_path = Path(env_path) if env_path is not None else find_repo_env()
    if dotenv_path is None or not dotenv_path.is_file():
        return None

    values = _parse_dotenv_lines(dotenv_path.read_text(encoding="utf-8").splitlines())
    for key, value in values.items():
        if keys is not None and key not in keys:
            continue
        if override or key not in os.environ:
            os.environ[key] = value
    return dotenv_path


def find_repo_env(start: str | Path | None = None) -> Path | None:
    current = Path.cwd() if start is None else Path(start)
    current = current.resolve(strict=False)
    if current.is_file():
        current = current.parent

    for directory in (current, *current.parents):
        if (directory / "pyproject.toml").is_file() and (directory / "apps").is_dir():
            return directory / ".env"
    return None


def _parse_dotenv_lines(lines: Iterable[str]) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in lines:
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line.removeprefix("export ").lstrip()
        if "=" not in line:
            continue

        key, raw_value = line.split("=", maxsplit=1)
        key = key.strip()
        if not _ENV_KEY_PATTERN.fullmatch(key):
            continue
        values[key] = _decode_value(_strip_inline_comment(raw_value.strip()))
    return values


def _strip_inline_comment(value: str) -> str:
    in_single_quote = False
    in_double_quote = False
    escaped = False

    for index, character in enumerate(value):
        if escaped:
            escaped = False
            continue
        if character == "\\" and in_double_quote:
            escaped = True
            continue
        if character == "'" and not in_double_quote:
            in_single_quote = not in_single_quote
            continue
        if character == '"' and not in_single_quote:
            in_double_quote = not in_double_quote
            continue
        if character == "#" and not in_single_quote and not in_double_quote:
            if index == 0 or value[index - 1].isspace():
                return value[:index].rstrip()
    return value


def _decode_value(value: str) -> str:
    if len(value) < 2:
        return value
    if value[0] == value[-1] == "'":
        return value[1:-1]
    if value[0] == value[-1] == '"':
        return (
            value[1:-1]
            .replace(r"\n", "\n")
            .replace(r"\r", "\r")
            .replace(r"\t", "\t")
            .replace(r"\\", "\\")
            .replace(r"\"", '"')
        )
    return value
