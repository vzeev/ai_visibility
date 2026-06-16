"""Small utility entrypoint for local service imports."""

from __future__ import annotations

import importlib
import os
from typing import Any


def load_app() -> Any:
    import_path = os.environ.get("SERVICE_APP", "apps.config_service.app.main:app")
    module_name, object_name = import_path.split(":", maxsplit=1)
    module = importlib.import_module(module_name)
    return getattr(module, object_name)
