from __future__ import annotations

import asyncio
import os

from apps.visibility_service.app.db.session import get_session_factory
from apps.worker.app.visibility_worker import VisibilityWorker


async def run_worker() -> None:
    worker = VisibilityWorker(get_session_factory())
    results = await worker.process_batch(max_items=_max_items_from_env())
    processed = sum(1 for result in results if result.status == "processed")
    failed = sum(1 for result in results if result.status == "failed")
    idle = any(result.status == "idle" for result in results)
    print(f"visibility-worker processed={processed} failed={failed} idle={idle}")


def main() -> None:
    asyncio.run(run_worker())


def _max_items_from_env() -> int:
    return max(1, int(os.environ.get("WORKER_MAX_ITEMS", "10")))


if __name__ == "__main__":
    main()
