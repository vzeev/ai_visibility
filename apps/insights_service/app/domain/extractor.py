from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import urlsplit, urlunsplit

DEFAULT_EXTRACTION_VERSION = "deterministic-v1"

_URL_PATTERN = re.compile(r"https?://[^\s<>\]\)]+", re.IGNORECASE)
_TRAILING_URL_PUNCTUATION = ".,;:!?)]}"
_POSITIVE_TERMS = (
    "best",
    "excellent",
    "good",
    "leader",
    "positive",
    "prominent",
    "recommend",
    "recommended",
    "strong",
    "trusted",
    "visible",
)
_NEGATIVE_TERMS = (
    "avoid",
    "bad",
    "decline",
    "invisible",
    "missing",
    "negative",
    "not recommended",
    "poor",
    "problem",
    "weak",
    "worse",
)


@dataclass(frozen=True)
class EntityAliases:
    entity_type: str
    entity_name: str
    aliases: tuple[str, ...]


@dataclass(frozen=True)
class MentionMatch:
    entity_type: str
    entity_name: str
    mention_text: str
    sentiment_label: str
    confidence: float
    start_index: int
    end_index: int
    snippet: str


@dataclass(frozen=True)
class CitationMatch:
    url: str
    domain: str
    start_index: int
    end_index: int
    snippet: str


@dataclass(frozen=True)
class ExtractionResult:
    mentions: tuple[MentionMatch, ...]
    citations: tuple[CitationMatch, ...]


class DeterministicInsightExtractor:
    def extract(self, *, output_text: str, entities: tuple[EntityAliases, ...]) -> ExtractionResult:
        citations = self._extract_citations(output_text)
        mentions = self._extract_mentions(
            output_text=output_text,
            entities=entities,
            ignored_spans=tuple(
                (citation.start_index, citation.end_index) for citation in citations
            ),
        )
        return ExtractionResult(mentions=tuple(mentions), citations=tuple(citations))

    def _extract_mentions(
        self,
        *,
        output_text: str,
        entities: tuple[EntityAliases, ...],
        ignored_spans: tuple[tuple[int, int], ...],
    ) -> list[MentionMatch]:
        matches: list[MentionMatch] = []
        seen: set[tuple[str, str, int, int]] = set()
        for entity in entities:
            for alias in _stable_aliases(entity.aliases):
                pattern = _alias_pattern(alias)
                for match in pattern.finditer(output_text):
                    start_index = match.start()
                    end_index = match.end()
                    if _overlaps_any(start_index, end_index, ignored_spans):
                        continue
                    key = (
                        entity.entity_type,
                        entity.entity_name.casefold(),
                        start_index,
                        end_index,
                    )
                    if key in seen:
                        continue
                    seen.add(key)
                    snippet = _snippet(output_text, start_index, end_index)
                    matches.append(
                        MentionMatch(
                            entity_type=entity.entity_type,
                            entity_name=entity.entity_name,
                            mention_text=output_text[start_index:end_index],
                            sentiment_label=_sentiment(snippet),
                            confidence=1.0,
                            start_index=start_index,
                            end_index=end_index,
                            snippet=snippet,
                        )
                    )
        return sorted(
            matches, key=lambda item: (item.start_index, item.entity_type, item.entity_name)
        )

    def _extract_citations(self, output_text: str) -> list[CitationMatch]:
        citations: list[CitationMatch] = []
        seen_urls: set[str] = set()
        for match in _URL_PATTERN.finditer(output_text):
            raw_url = match.group(0).rstrip(_TRAILING_URL_PUNCTUATION)
            normalized = _normalize_url(raw_url)
            if normalized is None:
                continue
            url, domain = normalized
            if url in seen_urls:
                continue
            seen_urls.add(url)
            start_index = match.start()
            end_index = start_index + len(raw_url)
            citations.append(
                CitationMatch(
                    url=url,
                    domain=domain,
                    start_index=start_index,
                    end_index=end_index,
                    snippet=_snippet(output_text, start_index, end_index),
                )
            )
        return citations


def _stable_aliases(aliases: tuple[str, ...]) -> tuple[str, ...]:
    unique: dict[str, str] = {}
    for alias in aliases:
        stripped = alias.strip()
        if stripped:
            unique.setdefault(stripped.casefold(), stripped)
    return tuple(unique[key] for key in sorted(unique, key=lambda value: (-len(value), value)))


def _alias_pattern(alias: str) -> re.Pattern[str]:
    return re.compile(rf"(?<!\w){re.escape(alias)}(?!\w)", re.IGNORECASE)


def _sentiment(text: str) -> str:
    lowered = text.casefold()
    if any(term in lowered for term in _NEGATIVE_TERMS):
        return "negative"
    if any(term in lowered for term in _POSITIVE_TERMS):
        return "positive"
    return "neutral"


def _snippet(text: str, start_index: int, end_index: int, context_chars: int = 60) -> str:
    start = max(0, start_index - context_chars)
    end = min(len(text), end_index + context_chars)
    return text[start:end]


def _overlaps_any(
    start_index: int,
    end_index: int,
    spans: tuple[tuple[int, int], ...],
) -> bool:
    return any(start_index < span_end and end_index > span_start for span_start, span_end in spans)


def _normalize_url(value: str) -> tuple[str, str] | None:
    parsed = urlsplit(value)
    if parsed.scheme.lower() not in {"http", "https"} or not parsed.netloc:
        return None
    domain = (parsed.hostname or parsed.netloc).casefold()
    if domain.startswith("www."):
        domain = domain[4:]
    normalized = urlunsplit(
        (
            parsed.scheme.lower(),
            parsed.netloc.casefold(),
            parsed.path,
            parsed.query,
            parsed.fragment,
        )
    )
    return normalized, domain
