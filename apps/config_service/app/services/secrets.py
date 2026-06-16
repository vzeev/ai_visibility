from __future__ import annotations

import hashlib


def build_local_secret_ref(secret: str) -> str:
    if not secret:
        raise ValueError("secret must not be empty")
    digest = hashlib.sha256(secret.encode("utf-8")).hexdigest()
    return f"local-sha256:{digest}"
