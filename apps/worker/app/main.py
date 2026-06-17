from __future__ import annotations

import asyncio
import os

from apps.shared.runtime.env import bootstrap_repo_env, find_repo_env
from apps.visibility_service.app.db.session import get_session_factory
from apps.worker.app.visibility_worker import VisibilityWorker


async def run_worker() -> None:
    worker = _worker_from_env()
    results = await worker.process_batch(max_items=_max_items_from_env())
    processed = sum(1 for result in results if result.status == "processed")
    failed = sum(1 for result in results if result.status == "failed")
    idle = any(result.status == "idle" for result in results)
    print(f"visibility-worker processed={processed} failed={failed} idle={idle}")


def main() -> None:
    asyncio.run(run_worker())


def _max_items_from_env() -> int:
    return max(1, int(os.environ.get("WORKER_MAX_ITEMS", "10")))


def _worker_from_env() -> VisibilityWorker:
    bootstrap_repo_env(find_repo_env())
    if os.environ.get("ENABLE_OPENAI", "").lower() in {"1", "true", "yes"}:
        return VisibilityWorker.with_openai_enabled(get_session_factory())
    return VisibilityWorker(get_session_factory())


if __name__ == "__main__":
    main()
