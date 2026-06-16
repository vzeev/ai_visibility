from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str)


def digest_payload(kind: str, payload: Mapping[str, object]) -> str:
    digest = hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()
    return f"{kind}:sha256:{digest}"


def build_run_item_idempotency_key(
    *,
    prompt_version_id: str,
    provider_key: str,
    model_id: str,
    sample_index: int,
    config_snapshot_hash: str,
) -> str:
    return digest_payload(
        "run-item:v1",
        {
            "prompt_version_id": prompt_version_id,
            "provider_key": provider_key,
            "model_id": model_id,
            "sample_index": sample_index,
            "config_snapshot_hash": config_snapshot_hash,
        },
    )


def build_raw_response_idempotency_key(
    *,
    run_item_idempotency_key: str,
    provider_key: str,
    model_id: str,
    provider_response_id: str | None,
    raw_response_json: Mapping[str, object],
) -> str:
    return digest_payload(
        "raw-response:v1",
        {
            "run_item_idempotency_key": run_item_idempotency_key,
            "provider_key": provider_key,
            "model_id": model_id,
            "provider_response_id": provider_response_id,
            "raw_response_json": raw_response_json,
        },
    )
