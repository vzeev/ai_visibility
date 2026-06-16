from __future__ import annotations

import hashlib


def redacted_fingerprint(secret: str) -> str:
    if not secret:
        raise ValueError("secret must not be empty")
    digest = hashlib.sha256(secret.encode("utf-8")).hexdigest()[:12]
    return f"sha256:{digest}"
