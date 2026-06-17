from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from apps.worker.app import main as worker_main


class WorkerRuntimeTests(unittest.TestCase):
    def test_worker_uses_openai_adapter_when_enable_openai_is_true_in_repo_env(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / ".env"
            env_path.write_text("ENABLE_OPENAI=true\nOPENAI_API_KEY=test-token\n", encoding="utf-8")
            original_enabled = os.environ.get("ENABLE_OPENAI")
            original_openai = os.environ.get("OPENAI_API_KEY")
            try:
                os.environ["ENABLE_OPENAI"] = "false"
                os.environ["OPENAI_API_KEY"] = "inherited-token"
                session_factory = Mock(name="session_factory")
                openai_worker = Mock(name="openai_worker")

                with (
                    patch.object(worker_main, "find_repo_env", return_value=env_path),
                    patch.object(worker_main, "get_session_factory", return_value=session_factory),
                    patch.object(
                        worker_main.VisibilityWorker,
                        "with_openai_enabled",
                        return_value=openai_worker,
                    ) as with_openai_enabled,
                ):
                    worker = worker_main._worker_from_env()

                self.assertIs(openai_worker, worker)
                with_openai_enabled.assert_called_once_with(session_factory)
            finally:
                _restore_env("ENABLE_OPENAI", original_enabled)
                _restore_env("OPENAI_API_KEY", original_openai)


def _restore_env(key: str, value: str | None) -> None:
    if value is None:
        os.environ.pop(key, None)
    else:
        os.environ[key] = value
