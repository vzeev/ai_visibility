from __future__ import annotations

import os
import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Protocol


class MissingProviderCredentialError(Exception):
    def __init__(self, provider_key: str) -> None:
        super().__init__(f"runtime credential is not configured for provider: {provider_key}")
        self.provider_key = provider_key


class ProviderCredentialResolver(Protocol):
    def resolve_token(self, provider_key: str) -> str: ...


def _default_env_names() -> dict[str, tuple[str, ...]]:
    return {"openai": ("OPENAI_API_KEY",)}


@dataclass(frozen=True)
class EnvironmentCredentialResolver:
    env_names_by_provider: Mapping[str, tuple[str, ...]] = field(default_factory=_default_env_names)

    def resolve_token(self, provider_key: str) -> str:
        env_names = self.env_names_by_provider.get(provider_key, _generated_env_names(provider_key))
        for env_name in env_names:
            token = os.environ.get(env_name)
            if token:
                return token
        raise MissingProviderCredentialError(provider_key)


@dataclass(frozen=True)
class StaticCredentialResolver:
    token: str

    def resolve_token(self, provider_key: str) -> str:
        if not self.token:
            raise MissingProviderCredentialError(provider_key)
        return self.token


def _generated_env_names(provider_key: str) -> tuple[str, ...]:
    normalized = re.sub(r"[^A-Za-z0-9]+", "_", provider_key).strip("_").upper()
    return (f"AI_VISIBILITY_{normalized}_API_KEY",)
