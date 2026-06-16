from __future__ import annotations

import os
import shutil
import subprocess  # nosec B404
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WEB_ROOT = REPO_ROOT / "apps" / "web"


def _resolve_npm() -> str:
    names = ("npm.cmd", "npm") if os.name == "nt" else ("npm",)
    for name in names:
        npm = shutil.which(name)
        if npm is not None:
            return npm

    if os.name == "nt":
        for root in (os.environ.get("ProgramFiles"), os.environ.get("ProgramFiles(x86)")):
            if root is None:
                continue
            candidate = Path(root) / "nodejs" / "npm.cmd"
            if candidate.exists():
                return str(candidate)

    raise SystemExit("npm is required for web checks but was not found on PATH.")


def main() -> int:
    if not (WEB_ROOT / "node_modules").exists():
        raise SystemExit("apps/web/node_modules is missing. Run 'npm install' from apps/web.")
    completed = subprocess.run(  # nosec B603
        [_resolve_npm(), "run", "test"],
        cwd=WEB_ROOT,
        check=False,
    )
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
