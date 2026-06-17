from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from apps.shared.ai.credentials import EnvironmentCredentialResolver
from apps.shared.runtime.env import bootstrap_repo_env, load_repo_env


class RuntimeEnvTests(unittest.TestCase):
    def test_load_repo_env_sets_values_without_overriding_existing_environment(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / ".env"
            env_path.write_text(
                "\n".join(
                    (
                        "AI_VISIBILITY_TEST_VALUE=from-file",
                        "AI_VISIBILITY_EXISTING_VALUE=from-file",
                        "AI_VISIBILITY_QUOTED_VALUE=\"quoted # value\"",
                        "AI_VISIBILITY_COMMENTED_VALUE=value # local comment",
                    )
                ),
                encoding="utf-8",
            )
            original_values = {
                key: os.environ.get(key)
                for key in (
                    "AI_VISIBILITY_TEST_VALUE",
                    "AI_VISIBILITY_EXISTING_VALUE",
                    "AI_VISIBILITY_QUOTED_VALUE",
                    "AI_VISIBILITY_COMMENTED_VALUE",
                )
            }
            os.environ["AI_VISIBILITY_EXISTING_VALUE"] = "from-process"
            try:
                loaded_path = load_repo_env(env_path, keys=set(original_values))

                self.assertEqual(env_path, loaded_path)
                self.assertEqual("from-file", os.environ["AI_VISIBILITY_TEST_VALUE"])
                self.assertEqual("from-process", os.environ["AI_VISIBILITY_EXISTING_VALUE"])
                self.assertEqual("quoted # value", os.environ["AI_VISIBILITY_QUOTED_VALUE"])
                self.assertEqual("value", os.environ["AI_VISIBILITY_COMMENTED_VALUE"])
            finally:
                for key, value in original_values.items():
                    if value is None:
                        os.environ.pop(key, None)
                    else:
                        os.environ[key] = value

    def test_load_repo_env_ignores_unlisted_keys_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / ".env"
            env_path.write_text(
                "\n".join(
                    (
                        "OPENAI_API_KEY=from-file",
                        "HTTPS_PROXY=http://proxy.invalid",
                    )
                ),
                encoding="utf-8",
            )
            original_openai = os.environ.get("OPENAI_API_KEY")
            original_proxy = os.environ.get("HTTPS_PROXY")
            try:
                os.environ.pop("OPENAI_API_KEY", None)
                os.environ.pop("HTTPS_PROXY", None)

                load_repo_env(env_path)

                self.assertEqual("from-file", os.environ["OPENAI_API_KEY"])
                self.assertNotIn("HTTPS_PROXY", os.environ)
            finally:
                _restore_env("OPENAI_API_KEY", original_openai)
                _restore_env("HTTPS_PROXY", original_proxy)

    def test_bootstrap_repo_env_prefers_repo_openai_keys_over_inherited_values(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / ".env"
            env_path.write_text(
                "\n".join(
                    (
                        "OPENAI_API_KEY=",
                        "ENABLE_OPENAI=false",
                    )
                ),
                encoding="utf-8",
            )
            original_openai = os.environ.get("OPENAI_API_KEY")
            original_enabled = os.environ.get("ENABLE_OPENAI")
            try:
                os.environ["OPENAI_API_KEY"] = "inherited-token"
                os.environ["ENABLE_OPENAI"] = "true"

                bootstrap_repo_env(env_path)

                self.assertEqual("", os.environ["OPENAI_API_KEY"])
                self.assertEqual("false", os.environ["ENABLE_OPENAI"])
            finally:
                _restore_env("OPENAI_API_KEY", original_openai)
                _restore_env("ENABLE_OPENAI", original_enabled)

    def test_find_repo_env_discovers_dotenv_from_repo_like_cwd(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            nested_path = repo_path / "apps" / "worker"
            nested_path.mkdir(parents=True)
            (repo_path / "pyproject.toml").write_text("[tool.poetry]\n", encoding="utf-8")
            (repo_path / ".env").write_text("ENABLE_OPENAI=true\n", encoding="utf-8")
            original_cwd = Path.cwd()
            original_enabled = os.environ.get("ENABLE_OPENAI")
            try:
                os.environ.pop("ENABLE_OPENAI", None)
                os.chdir(nested_path)

                loaded_path = bootstrap_repo_env()

                self.assertEqual(repo_path / ".env", loaded_path)
                self.assertEqual("true", os.environ["ENABLE_OPENAI"])
            finally:
                os.chdir(original_cwd)
                _restore_env("ENABLE_OPENAI", original_enabled)

    def test_environment_credential_resolver_reads_bootstrapped_openai_key(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / ".env"
            env_path.write_text("OPENAI_API_KEY=repo-token\n", encoding="utf-8")
            original_openai = os.environ.get("OPENAI_API_KEY")
            try:
                os.environ["OPENAI_API_KEY"] = "inherited-token"

                bootstrap_repo_env(env_path)

                self.assertEqual(
                    "repo-token",
                    EnvironmentCredentialResolver().resolve_token("openai"),
                )
            finally:
                _restore_env("OPENAI_API_KEY", original_openai)


def _restore_env(key: str, value: str | None) -> None:
    if value is None:
        os.environ.pop(key, None)
    else:
        os.environ[key] = value
