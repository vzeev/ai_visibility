from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Protocol, cast

import httpx

from apps.shared.ai.credentials import (
    EnvironmentCredentialResolver,
    MissingProviderCredentialError,
    ProviderCredentialResolver,
)

OPENAI_MODELS_ENDPOINT = "https://api.openai.com/v1/models"


@dataclass(frozen=True)
class DiscoveredModel:
    model_id: str
    display_name: str
    owned_by: str | None
    capability_json: dict[str, Any]


class ModelDiscoveryError(Exception):
    def __init__(self, provider_key: str, message: str, *, retryable: bool) -> None:
        super().__init__(message)
        self.provider_key = provider_key
        self.retryable = retryable


class ModelDiscoveryClient(Protocol):
    async def list_models(self, provider_key: str) -> list[DiscoveredModel]: ...


class OpenAIModelDiscoveryClient:
    def __init__(
        self,
        *,
        credential_resolver: ProviderCredentialResolver | None = None,
        http_client: httpx.AsyncClient | None = None,
        endpoint_url: str = OPENAI_MODELS_ENDPOINT,
    ) -> None:
        self._credential_resolver = credential_resolver or EnvironmentCredentialResolver()
        self._http_client = http_client
        self._endpoint_url = endpoint_url

    async def list_models(self, provider_key: str) -> list[DiscoveredModel]:
        if provider_key != "openai":
            raise ModelDiscoveryError(
                provider_key,
                f"model discovery is not implemented for provider: {provider_key}",
                retryable=False,
            )

        try:
            token = self._credential_resolver.resolve_token(provider_key)
        except MissingProviderCredentialError as error:
            raise ModelDiscoveryError(provider_key, str(error), retryable=True) from error

        try:
            response = await self._get(token=token)
        except httpx.TimeoutException as error:
            raise ModelDiscoveryError(
                provider_key,
                "OpenAI model discovery timed out",
                retryable=True,
            ) from error
        except httpx.TransportError as error:
            raise ModelDiscoveryError(
                provider_key,
                "OpenAI model discovery transport error",
                retryable=True,
            ) from error

        raw_response = _response_json(response)
        if response.status_code >= 400:
            raise ModelDiscoveryError(
                provider_key,
                f"OpenAI model discovery HTTP {response.status_code}: "
                f"{_error_message(raw_response)}",
                retryable=response.status_code == 429
                or response.status_code >= 500
                or response.status_code in (408, 409),
            )
        return _parse_models(raw_response)

    async def _get(self, *, token: str) -> httpx.Response:
        headers = {"Authorization": f"Bearer {token}"}
        if self._http_client is not None:
            return await self._http_client.get(self._endpoint_url, headers=headers)
        async with httpx.AsyncClient(timeout=30.0) as client:
            return await client.get(self._endpoint_url, headers=headers)


def _parse_models(raw_response: Mapping[str, Any]) -> list[DiscoveredModel]:
    data = raw_response.get("data")
    if not isinstance(data, list):
        return []

    models: list[DiscoveredModel] = []
    for item in cast(list[Any], data):
        if not isinstance(item, dict):
            continue
        model = cast(dict[str, Any], item)
        model_id = model.get("id")
        if not isinstance(model_id, str) or not model_id:
            continue
        owned_by = model.get("owned_by")
        models.append(
            DiscoveredModel(
                model_id=model_id,
                display_name=model_id,
                owned_by=owned_by if isinstance(owned_by, str) else None,
                capability_json={
                    "source": "openai.models",
                    "object": model.get("object"),
                    "created": model.get("created"),
                    "owned_by": owned_by,
                },
            )
        )
    return models


def _response_json(response: httpx.Response) -> dict[str, Any]:
    try:
        parsed = response.json()
    except ValueError:
        return {"error": {"message": response.text}}
    if isinstance(parsed, dict):
        return cast(dict[str, Any], parsed)
    return {"response": parsed}


def _error_message(raw_response: Mapping[str, Any]) -> str:
    error = raw_response.get("error")
    if isinstance(error, dict):
        error_mapping = cast(dict[str, Any], error)
        message = error_mapping.get("message")
        if isinstance(message, str):
            return message
    return "provider request failed"
