from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Protocol


def _empty_metadata() -> Mapping[str, object]:
    return {}


@dataclass(frozen=True)
class AIRequest:
    provider_key: str
    model_id: str
    prompt_text: str
    system_text: str | None = None
    temperature: float | None = None
    max_output_tokens: int | None = None
    response_format: Mapping[str, object] | None = None
    metadata: Mapping[str, object] = field(default_factory=_empty_metadata)


@dataclass(frozen=True)
class AIResponse:
    provider_key: str
    model_id: str
    output_text: str
    raw_request_json: Mapping[str, object]
    raw_response_json: Mapping[str, object]
    usage_json: Mapping[str, object]
    latency_ms: int
    provider_response_id: str | None = None


class AIProviderAdapter(Protocol):
    provider_key: str

    async def complete(self, request: AIRequest) -> AIResponse: ...


class AIProviderError(Exception):
    def __init__(self, *, provider_key: str, model_id: str, message: str, retryable: bool) -> None:
        super().__init__(message)
        self.provider_key = provider_key
        self.model_id = model_id
        self.retryable = retryable


class FakeAIProviderAdapter:
    provider_key = "fake"

    def __init__(self, responses: Mapping[str, str] | None = None) -> None:
        self._responses = dict(responses or {})

    async def complete(self, request: AIRequest) -> AIResponse:
        output_text = self._responses.get(
            request.model_id,
            f"Fake visibility answer for model {request.model_id}: {request.prompt_text}",
        )
        raw_request = {
            "provider": request.provider_key,
            "model": request.model_id,
            "prompt": request.prompt_text,
            "system": request.system_text,
            "response_format": request.response_format,
        }
        provider_response_id = f"fake-{request.model_id}"
        raw_response = {
            "id": provider_response_id,
            "output_text": output_text,
        }
        return AIResponse(
            provider_key=request.provider_key,
            model_id=request.model_id,
            output_text=output_text,
            raw_request_json=raw_request,
            raw_response_json=raw_response,
            usage_json={"input_tokens": 0, "output_tokens": 0},
            latency_ms=0,
            provider_response_id=provider_response_id,
        )
