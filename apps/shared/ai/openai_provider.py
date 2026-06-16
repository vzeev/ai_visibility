from __future__ import annotations

import time
from collections.abc import Mapping
from typing import cast

import httpx

from apps.shared.ai.credentials import (
    EnvironmentCredentialResolver,
    MissingProviderCredentialError,
    ProviderCredentialResolver,
)
from apps.shared.ai.provider import AIProviderError, AIRequest, AIResponse

OPENAI_RESPONSES_ENDPOINT = "https://api.openai.com/v1/responses"


class OpenAIResponsesAdapter:
    provider_key = "openai"

    def __init__(
        self,
        *,
        credential_resolver: ProviderCredentialResolver | None = None,
        http_client: httpx.AsyncClient | None = None,
        endpoint_url: str = OPENAI_RESPONSES_ENDPOINT,
    ) -> None:
        self._credential_resolver = credential_resolver or EnvironmentCredentialResolver()
        self._http_client = http_client
        self._endpoint_url = endpoint_url

    async def complete(self, request: AIRequest) -> AIResponse:
        try:
            token = self._credential_resolver.resolve_token(request.provider_key)
        except MissingProviderCredentialError as error:
            raise AIProviderError(
                provider_key=request.provider_key,
                model_id=request.model_id,
                message=str(error),
                retryable=True,
            ) from error

        payload = _build_response_payload(request)
        start = time.perf_counter()
        try:
            response = await self._post(payload=payload, token=token)
        except httpx.TimeoutException as error:
            raise _provider_error(request, "OpenAI request timed out", retryable=True) from error
        except httpx.TransportError as error:
            raise _provider_error(request, "OpenAI transport error", retryable=True) from error

        latency_ms = int((time.perf_counter() - start) * 1000)
        raw_response = _response_json(response)
        if response.status_code >= 400:
            raise _http_provider_error(request, response.status_code, raw_response)

        output_text = _extract_output_text(raw_response)
        return AIResponse(
            provider_key=request.provider_key,
            model_id=str(raw_response.get("model") or request.model_id),
            output_text=output_text,
            raw_request_json={
                "method": "POST",
                "url": self._endpoint_url,
                "body": payload,
            },
            raw_response_json=raw_response,
            usage_json=_mapping_or_empty(raw_response.get("usage")),
            latency_ms=latency_ms,
            provider_response_id=_optional_string(raw_response.get("id")),
        )

    async def _post(self, *, payload: dict[str, object], token: str) -> httpx.Response:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        if self._http_client is not None:
            return await self._http_client.post(self._endpoint_url, json=payload, headers=headers)
        async with httpx.AsyncClient(timeout=60.0) as client:
            return await client.post(self._endpoint_url, json=payload, headers=headers)


def _build_response_payload(request: AIRequest) -> dict[str, object]:
    payload: dict[str, object] = {
        "model": request.model_id,
        "input": request.prompt_text,
        "store": False,
        "metadata": _string_metadata(request.metadata),
    }
    if request.system_text:
        payload["instructions"] = request.system_text
    if request.max_output_tokens is not None:
        payload["max_output_tokens"] = request.max_output_tokens
    if request.temperature is not None:
        payload["temperature"] = request.temperature
    if request.response_format is not None:
        payload["text"] = {"format": dict(request.response_format)}
    return payload


def _string_metadata(metadata: Mapping[str, object]) -> dict[str, str]:
    stringified: dict[str, str] = {}
    for key, value in metadata.items():
        if isinstance(value, (str, int, float, bool)):
            stringified[str(key)] = str(value)
    return stringified


def _response_json(response: httpx.Response) -> dict[str, object]:
    try:
        parsed = response.json()
    except ValueError:
        return {"error": {"message": response.text}}
    if isinstance(parsed, dict):
        return cast(dict[str, object], parsed)
    return {"response": parsed}


def _extract_output_text(raw_response: Mapping[str, object]) -> str:
    output_text = raw_response.get("output_text")
    if isinstance(output_text, str):
        return output_text

    parts: list[str] = []
    output = raw_response.get("output")
    if not isinstance(output, list):
        return ""
    for output_item in cast(list[object], output):
        if not isinstance(output_item, dict):
            continue
        output_mapping = cast(dict[str, object], output_item)
        content = output_mapping.get("content")
        if not isinstance(content, list):
            continue
        for content_item in cast(list[object], content):
            if not isinstance(content_item, dict):
                continue
            content_mapping = cast(dict[str, object], content_item)
            text = content_mapping.get("text")
            if content_mapping.get("type") == "output_text" and isinstance(text, str):
                parts.append(text)
    return "\n".join(parts)


def _mapping_or_empty(value: object) -> dict[str, object]:
    if isinstance(value, dict):
        return cast(dict[str, object], value)
    return {}


def _optional_string(value: object) -> str | None:
    if isinstance(value, str):
        return value
    return None


def _http_provider_error(
    request: AIRequest,
    status_code: int,
    raw_response: Mapping[str, object],
) -> AIProviderError:
    retryable = status_code == 429 or status_code >= 500 or status_code in (408, 409)
    return _provider_error(
        request,
        f"OpenAI HTTP {status_code}: {_error_message(raw_response)}",
        retryable=retryable,
    )


def _provider_error(request: AIRequest, message: str, *, retryable: bool) -> AIProviderError:
    return AIProviderError(
        provider_key=request.provider_key,
        model_id=request.model_id,
        message=message,
        retryable=retryable,
    )


def _error_message(raw_response: Mapping[str, object]) -> str:
    error = raw_response.get("error")
    if isinstance(error, dict):
        error_mapping = cast(dict[str, object], error)
        message = error_mapping.get("message")
        if isinstance(message, str):
            return message
    return "provider request failed"
