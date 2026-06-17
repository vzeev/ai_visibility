from __future__ import annotations

import os
import shutil
import subprocess  # nosec B404
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

REPO_ROOT = Path(__file__).resolve().parents[1]
WEB_ROOT = REPO_ROOT / "apps" / "web"
WEB_URL = "http://127.0.0.1:5173"


def main() -> int:
    if not (WEB_ROOT / "node_modules").exists():
        raise SystemExit("apps/web/node_modules is missing. Run 'npm install' from apps/web.")
    if not (WEB_ROOT / "node_modules" / "cypress").exists():
        raise SystemExit("Cypress is missing. Run 'npm install' from apps/web.")

    npm = _resolve_npm()
    env = _windows_browser_env()
    server = None
    try:
        if not _is_web_ready():
            server = subprocess.Popen(  # nosec B603
                [npm, "run", "dev", "--", "--host", "127.0.0.1"],
                cwd=WEB_ROOT,
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            _wait_for_web(server)

        completed = subprocess.run(  # nosec B603
            [npm, "run", "cy:run", "--", "--config", f"baseUrl={WEB_URL}"],
            cwd=WEB_ROOT,
            env=env,
            check=False,
        )
        return completed.returncode
    finally:
        if server is not None:
            server.terminate()
            try:
                server.wait(timeout=10)
            except subprocess.TimeoutExpired:
                server.kill()


def _resolve_npm() -> str:
    names = ("npm.cmd", "npm") if os.name == "nt" else ("npm",)
    for name in names:
        npm = shutil.which(name)
        if npm is not None:
            return npm

    if os.name == "nt":
        env = _windows_browser_env()
        for root in (env.get("ProgramFiles"), env.get("ProgramFiles(x86)")):
            if root is None:
                continue
            candidate = Path(root) / "nodejs" / "npm.cmd"
            if candidate.exists():
                return str(candidate)
    raise SystemExit("npm is required for Cypress checks but was not found on PATH.")


def _windows_browser_env() -> dict[str, str]:
    env = dict(os.environ)
    user_profile = env.get("USERPROFILE") or str(Path.home())
    env.setdefault("APPDATA", str(Path(user_profile) / "AppData" / "Roaming"))
    env.setdefault("LOCALAPPDATA", str(Path(user_profile) / "AppData" / "Local"))
    env.setdefault("ProgramFiles", r"C:\Program Files")
    env.setdefault("ProgramFiles(x86)", r"C:\Program Files (x86)")
    return env


def _is_web_ready() -> bool:
    try:
        with urlopen(WEB_URL, timeout=2) as response:  # nosec B310
            return response.status < 500
    except (OSError, TimeoutError, URLError):
        return False


def _wait_for_web(server: subprocess.Popen[bytes]) -> None:
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        if server.poll() is not None:
            raise SystemExit("Vite dev server exited before Cypress could run.")
        if _is_web_ready():
            return
        time.sleep(0.5)
    raise SystemExit(f"Vite dev server did not become ready at {WEB_URL}.")


if __name__ == "__main__":
    raise SystemExit(main())
