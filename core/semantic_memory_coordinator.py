"""Phase 5.1 semantic memory coordination.

This module is the authoritative boundary for the *new* semantic-context path,
Phase 5.1B adds an opt-in production consumer while keeping existing retrieval,
routing, CDE, access-control, and personality paths unchanged when disabled.

The coordinator always requires an owner, requests an owner-scoped candidate
pool, performs deterministic local ranking/compression, and emits content-free
telemetry.  It never queries or includes personality traits.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import math
import os
import re
import time
from typing import Any, Callable, Literal, Mapping, Protocol, Sequence


SemanticMemoryPurpose = Literal["chat", "greeting"]

SEMANTIC_MEMORY_COORDINATOR_MODE = "semantic_memory_coordinator"
SEMANTIC_MEMORY_COORDINATOR_AUTHORITATIVE = True
SEMANTIC_MEMORY_COORDINATOR_PRODUCTION_ACTIVE = False
SEMANTIC_MEMORY_COORDINATOR_SCHEMA_VERSION = "1.0"
SEMANTIC_MEMORY_RUNTIME_MODE_ENV = "AETHERAEON_SEMANTIC_MEMORY_MODE"
SEMANTIC_MEMORY_RUNTIME_MODES = {"off", "shadow", "production"}

MAX_SELECTED_PER_SOURCE = 3
DEFAULT_CANDIDATE_POOL_SIZE = 12
MIN_SEMANTIC_RELEVANCE = 0.16
MAX_MEMORY_CONTEXT_CHARS = 320
MAX_CONVERSATION_CONTEXT_CHARS = 360

_STOP_WORDS = {
    "a", "about", "an", "and", "are", "as", "at", "be", "by", "can",
    "do", "does", "explain", "for", "from", "give", "how", "i", "in",
    "is", "it", "me", "my", "of", "on", "or", "please", "tell", "that",
    "the", "this", "to", "was", "what", "when", "where", "which", "with",
    "work", "works", "would", "you",
}

_SEMANTIC_GROUPS = (
    {"rocket", "spacecraft", "spacex", "launch", "propulsion", "merlin"},
    {"engine", "motor", "propulsion", "thrust", "combustion", "turbopump"},
    {"memory", "recall", "remember", "context", "retrieval"},
    {"artificial", "ai", "assistant", "model", "llm"},
    {"funny", "humor", "humorous", "joke", "jokes", "playful"},
    {"technical", "detailed", "depth", "academic", "architecture"},
    {"build", "building", "develop", "developing", "create", "creating"},
)

_NOISE_LINE = re.compile(
    r"^\s*(?:\[?(?:debug|system|trace|processing)[^\]]*\]?|"
    r"system\s*:|processing details\s*:|intent classification\s*:|"
    r"sources?\s*/?\s*tools? used\s*:|analytical reasoning influence\s*:|"
    r"creative reasoning influence\s*:)",
    re.IGNORECASE,
)
_ROLE_PREFIX = re.compile(r"^\s*(?:user|assistant|ai)\s*:\s*", re.IGNORECASE)
_TOKEN = re.compile(r"[a-z0-9][a-z0-9_-]*", re.IGNORECASE)
_SENTENCE = re.compile(r"(?<=[.!?])\s+|[\r\n]+")


class SemanticMemoryCoordinatorError(ValueError):
    """Raised when a request cannot be made owner-scoped and safe."""


class SemanticMemoryUsageStore(Protocol):
    """Persistence contract for content-free selection usage records."""

    def get_usage(
        self, *, user_id: int, source: str, source_item_ids: Sequence[str]
    ) -> Mapping[str, Mapping[str, Any]]: ...

    def record_selections(
        self, *, user_id: int, selections: Sequence[Mapping[str, Any]]
    ) -> None: ...


class MariaDBSemanticMemoryUsageStore:
    """Lazy adapter to the existing MariaDB persistence boundary."""

    def get_usage(
        self, *, user_id: int, source: str, source_item_ids: Sequence[str]
    ) -> Mapping[str, Mapping[str, Any]]:
        from core.memory_database import get_semantic_memory_usage

        return get_semantic_memory_usage(user_id, source, source_item_ids)

    def record_selections(
        self, *, user_id: int, selections: Sequence[Mapping[str, Any]]
    ) -> None:
        from core.memory_database import record_semantic_memory_usage

        record_semantic_memory_usage(user_id, selections)


class InMemorySemanticMemoryUsageStore:
    """Deterministic non-production usage store for tests and shadow analysis."""

    def __init__(self) -> None:
        self._records: dict[tuple[int, str, str], dict[str, Any]] = {}

    def get_usage(
        self, *, user_id: int, source: str, source_item_ids: Sequence[str]
    ) -> Mapping[str, Mapping[str, Any]]:
        return {
            item_id: dict(self._records[(user_id, source, item_id)])
            for item_id in source_item_ids
            if (user_id, source, item_id) in self._records
        }

    def record_selections(
        self, *, user_id: int, selections: Sequence[Mapping[str, Any]]
    ) -> None:
        now = datetime.now(timezone.utc).isoformat()
        for item in selections:
            source = str(item["source"])
            source_item_id = str(item["source_item_id"])
            key = (user_id, source, source_item_id)
            previous = self._records.get(key, {})
            self._records[key] = {
                "source_item_id": source_item_id,
                "memory_type": str(item.get("memory_type") or "unknown"),
                "last_selected_at": now,
                "selection_count": int(previous.get("selection_count") or 0) + 1,
                "rotation_cycle": int(item.get("rotation_cycle") or 1),
            }


@dataclass(frozen=True, slots=True)
class SemanticMemoryContextItem:
    """One selected, compressed item safe for future prompt assembly."""

    source: Literal["chromadb", "conversation_history"]
    source_item_id: str
    memory_type: str
    context: str
    score: float
    semantic_relevance: float
    stable_importance: float
    historical_connection: float
    rotation_preference: float
    rotation_cycle: int

    @property
    def reference(self) -> str:
        prefix = "memory" if self.source == "chromadb" else "conversation"
        return f"{prefix}:{self.source_item_id}"

    def safe_score_metrics(self) -> dict[str, float | int]:
        return {
            "score": round(self.score, 4),
            "semantic_relevance": round(self.semantic_relevance, 4),
            "stable_importance": round(self.stable_importance, 4),
            "historical_connection": round(self.historical_connection, 4),
            "rotation_preference": round(self.rotation_preference, 4),
            "rotation_cycle": self.rotation_cycle,
        }


@dataclass(frozen=True, slots=True)
class SemanticMemoryContextPackage:
    """Selected semantic context plus content-free operational telemetry."""

    selected_memories: tuple[SemanticMemoryContextItem, ...]
    selected_conversations: tuple[SemanticMemoryContextItem, ...]
    compressed_context_block: str
    telemetry: Mapping[str, Any]
    schema_version: str = SEMANTIC_MEMORY_COORDINATOR_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if len(self.selected_memories) > MAX_SELECTED_PER_SOURCE:
            raise SemanticMemoryCoordinatorError("selected memory limit exceeded")
        if len(self.selected_conversations) > MAX_SELECTED_PER_SOURCE:
            raise SemanticMemoryCoordinatorError("selected conversation limit exceeded")


@dataclass(frozen=True, slots=True)
class SemanticMemoryShadowComparison:
    """Content-safe comparison of the legacy result and the new package."""

    current_result_count: int
    current_references: tuple[str, ...]
    semantic_context: SemanticMemoryContextPackage
    production_switched: bool = False


def semantic_memory_runtime_mode(environment: Mapping[str, str] | None = None) -> str:
    """Return the configured mode; production remains unconsumed in Phase 5.1."""

    source = os.environ if environment is None else environment
    mode = str(source.get(SEMANTIC_MEMORY_RUNTIME_MODE_ENV, "off")).strip().lower()
    return mode if mode in SEMANTIC_MEMORY_RUNTIME_MODES else "off"


def semantic_memory_shadow_enabled(environment: Mapping[str, str] | None = None) -> bool:
    return semantic_memory_runtime_mode(environment) == "shadow"


def semantic_memory_production_requested(
    environment: Mapping[str, str] | None = None,
) -> bool:
    """Return whether the explicitly opt-in production branch is requested."""

    return semantic_memory_runtime_mode(environment) == "production"


@dataclass(slots=True)
class _Candidate:
    source: Literal["chromadb", "conversation_history"]
    source_item_id: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)
    memory_type: str = "unknown"
    semantic_relevance: float = 0.0
    stable_importance: float = 0.0
    historical_connection: float = 0.0
    rotation_preference: float = 0.0
    rotation_cycle: int = 1
    score: float = 0.0

    @property
    def reference(self) -> str:
        prefix = "memory" if self.source == "chromadb" else "conversation"
        return f"{prefix}:{self.source_item_id}"


def _validate_user_id(user_id: Any) -> int:
    if isinstance(user_id, bool) or not isinstance(user_id, int) or user_id < 1:
        raise SemanticMemoryCoordinatorError("user_id must be a positive integer")
    return user_id


def _validate_request(
    *,
    user_id: Any,
    query: Any,
    conversation_id: Any,
    purpose: Any,
    allow_long_term_memory: Any,
    allow_conversation_history: Any,
    max_memories: Any,
    max_conversation_items: Any,
) -> tuple[int, str, str | None, SemanticMemoryPurpose, bool, bool, int, int]:
    owner_id = _validate_user_id(user_id)
    if not isinstance(query, str) or not query.strip():
        raise SemanticMemoryCoordinatorError("query must be a non-empty string")
    clean_query = query.strip()
    if len(clean_query) > 8000:
        raise SemanticMemoryCoordinatorError("query exceeds the semantic request limit")
    if conversation_id is not None and (
        not isinstance(conversation_id, str) or not conversation_id.strip()
    ):
        raise SemanticMemoryCoordinatorError("conversation_id must be a non-empty string or None")
    if purpose not in ("chat", "greeting"):
        raise SemanticMemoryCoordinatorError("purpose must be 'chat' or 'greeting'")
    if not isinstance(allow_long_term_memory, bool):
        raise SemanticMemoryCoordinatorError("allow_long_term_memory must be boolean")
    if not isinstance(allow_conversation_history, bool):
        raise SemanticMemoryCoordinatorError("allow_conversation_history must be boolean")

    def selected_limit(value: Any, name: str) -> int:
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise SemanticMemoryCoordinatorError(f"{name} must be a non-negative integer")
        return min(value, MAX_SELECTED_PER_SOURCE)

    return (
        owner_id,
        clean_query,
        conversation_id.strip() if conversation_id else None,
        purpose,
        allow_long_term_memory,
        allow_conversation_history,
        selected_limit(max_memories, "max_memories"),
        selected_limit(max_conversation_items, "max_conversation_items"),
    )


def _stem(token: str) -> str:
    token = token.lower()
    for suffix in ("ing", "ies", "ed", "es", "s"):
        if token.endswith(suffix) and len(token) > len(suffix) + 3:
            return token[:-len(suffix)] + ("y" if suffix == "ies" else "")
    return token


def _tokens(text: str) -> tuple[str, ...]:
    return tuple(
        token
        for raw in _TOKEN.findall(text.lower())
        if (token := _stem(raw)) not in _STOP_WORDS and len(token) > 1
    )


def _semantic_relevance(query: str, candidate: _Candidate) -> float:
    query_tokens = tuple(dict.fromkeys(_tokens(query)))
    searchable = " ".join(
        [candidate.text]
        + [
            str(candidate.metadata.get(name) or "")
            for name in ("tags", "category", "topic", "title", "memory_type", "type")
        ]
    )
    candidate_tokens = set(_tokens(searchable))
    if not query_tokens or not candidate_tokens:
        lexical = 0.0
    else:
        matched = 0
        for token in query_tokens:
            concepts = {token}
            for group in _SEMANTIC_GROUPS:
                if token in {_stem(value) for value in group}:
                    concepts.update(_stem(value) for value in group)
            if concepts.intersection(candidate_tokens):
                matched += 1
        lexical = matched / len(query_tokens)

    supplied: float | None = None
    for name in ("semantic_relevance", "relevance_score", "score"):
        value = candidate.metadata.get(name)
        if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value):
            supplied = float(value)
            supplied = supplied / 100.0 if supplied > 1 else supplied
            break
    if supplied is None:
        distance = candidate.metadata.get("distance")
        if isinstance(distance, (int, float)) and not isinstance(distance, bool):
            supplied = max(0.0, min(1.0, 1.0 - float(distance) / 2.0))
    return max(0.0, min(1.0, max(lexical, supplied or 0.0)))


def _normalize_fraction(value: Any, default: float) -> float:
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, (int, float)) and math.isfinite(float(value)):
        number = float(value)
        if number > 1:
            number /= 100.0
        return max(0.0, min(1.0, number))
    return default


def _is_preference(candidate: _Candidate) -> bool:
    memory_type = candidate.memory_type.lower().replace("-", "_")
    if "preference" in memory_type:
        return True
    lowered = candidate.text.lower()
    return any(marker in lowered for marker in ("user prefers", "i prefer", "user likes", "i like"))


def _is_contextual_communication_preference(candidate: _Candidate) -> bool:
    """Allow globally useful style preferences, not unrelated likes, off-topic."""

    if not _is_preference(candidate):
        return False
    classification = " ".join(
        str(candidate.metadata.get(name) or "").lower()
        for name in ("category", "topic", "preference_type")
    )
    text = candidate.text.lower()
    communication_markers = (
        "communication", "conversation", "teaching", "response", "answer",
        "explanation", "detailed", "concise", "technical", "academic",
        "example", "format", "tone", "humor", "greeting",
    )
    return any(marker in classification or marker in text for marker in communication_markers)


def _is_trait(candidate: _Candidate) -> bool:
    metadata = candidate.metadata
    classifications = " ".join(
        str(metadata.get(name) or "").lower()
        for name in ("type", "memory_type", "category", "source", "record_type")
    )
    return (
        "trait_id" in metadata
        or "personality_trait" in classifications
        or any(part == "trait" for part in re.split(r"[^a-z]+", classifications))
    )


def _stable_importance(candidate: _Candidate) -> float:
    metadata = candidate.metadata
    explicit = next(
        (metadata.get(name) for name in ("stable_importance", "importance", "importance_score") if name in metadata),
        None,
    )
    if explicit is not None:
        return _normalize_fraction(explicit, 0.4)
    if _is_preference(candidate):
        return 0.9
    if metadata.get("stable") is True or metadata.get("pinned") is True:
        return 0.8
    return 0.4 if candidate.source == "chromadb" else 0.3


def _parse_datetime(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str) and value.strip():
        try:
            parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
        except ValueError:
            return None
    else:
        return None
    return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed.astimezone(timezone.utc)


def _historical_connection(
    candidate: _Candidate, conversation_id: str | None, now: datetime
) -> float:
    same_conversation = bool(
        conversation_id
        and str(candidate.metadata.get("conversation_id") or "") == conversation_id
    )
    timestamp = next(
        (
            _parse_datetime(candidate.metadata.get(name))
            for name in ("created_at", "updated_at", "last_used_at")
            if candidate.metadata.get(name)
        ),
        None,
    )
    recency = 0.25
    if timestamp is not None:
        age_days = max(0.0, (now - timestamp).total_seconds() / 86400.0)
        recency = max(0.05, 1.0 - min(age_days, 365.0) / 365.0)
    return min(1.0, recency + (0.35 if same_conversation else 0.0))


def _clean_text(text: Any) -> str:
    raw = str(text or "")[:8000]
    cleaned_lines: list[str] = []
    for line in raw.replace("\x00", " ").splitlines():
        line = re.sub(r"<[^>]+>", " ", line).strip()
        if not line or _NOISE_LINE.match(line):
            continue
        line = _ROLE_PREFIX.sub("", line)
        line = re.sub(r"\s+", " ", line).strip(" -\t")
        if line:
            cleaned_lines.append(line)
    return " ".join(cleaned_lines)


def _compress_text(text: str, query: str, *, conversation: bool) -> str:
    cleaned = _clean_text(text)
    if not cleaned:
        return ""
    query_tokens = set(_tokens(query))
    sentences = [part.strip() for part in _SENTENCE.split(cleaned) if part.strip()]
    ranked = sorted(
        (
            (index, sentence, len(query_tokens.intersection(_tokens(sentence))))
            for index, sentence in enumerate(sentences)
        ),
        key=lambda item: (-item[2], item[0]),
    )
    relevant = [item for item in ranked if item[2] > 0]
    chosen = (relevant or ranked[:1])[:2]
    chosen_indexes = sorted(index for index, _sentence, _overlap in chosen)
    compressed = " ".join(sentences[index] for index in chosen_indexes)
    compressed = re.sub(
        r"^(?:full|raw) conversation transcript\s*[:.-]?\s*",
        "",
        compressed,
        flags=re.IGNORECASE,
    )
    compressed = _ROLE_PREFIX.sub("", compressed)
    if conversation:
        replacements = (
            (r"^I am\b", "User is"),
            (r"^I'm\b", "User is"),
            (r"^I prefer\b", "User prefers"),
            (r"^I like\b", "User likes"),
            (r"^My\b", "User's"),
        )
        transformed = compressed
        for pattern, replacement in replacements:
            transformed = re.sub(pattern, replacement, transformed, flags=re.IGNORECASE)
        if transformed == compressed and not transformed.lower().startswith("user "):
            transformed = f"Previous discussion: {transformed}"
        compressed = transformed
    limit = MAX_CONVERSATION_CONTEXT_CHARS if conversation else MAX_MEMORY_CONTEXT_CHARS
    if len(compressed) > limit:
        compressed = compressed[: limit - 1].rsplit(" ", 1)[0].rstrip(" ,;:") + "…"
    return compressed


def _candidate_id(source: str, text: str, index: int) -> str:
    digest = hashlib.sha256(f"{source}|{text}|{index}".encode("utf-8")).hexdigest()[:24]
    return f"derived-{digest}"


def _normalize_candidates(raw: Any, source: str, user_id: int) -> list[_Candidate]:
    if isinstance(raw, tuple) and len(raw) == 2 and isinstance(raw[1], Mapping):
        status = raw[1]
        if status.get("attempted") is False or status.get("completed") is False:
            return []
        raw = raw[0]
    if isinstance(raw, Mapping):
        raw = raw.get("results", raw.get("items", []))
    if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes, bytearray)):
        return []

    normalized: list[_Candidate] = []
    for index, item in enumerate(raw):
        metadata: dict[str, Any]
        if isinstance(item, Mapping):
            metadata = dict(item.get("metadata") or {})
            for key in (
                "user_id", "conversation_id", "created_at", "updated_at", "role",
                "memory_type", "type", "category", "importance", "stable_importance",
                "distance", "semantic_relevance", "relevance_score", "score", "trait_id",
            ):
                if key in item and key not in metadata:
                    metadata[key] = item[key]
            identifier = next(
                (item.get(name) for name in ("memory_id", "message_id", "id", "uuid") if item.get(name) not in (None, "")),
                None,
            )
            text = next(
                (item.get(name) for name in ("document", "content", "text", "message") if item.get(name) not in (None, "")),
                "",
            )
        elif isinstance(item, Sequence) and not isinstance(item, (str, bytes, bytearray)):
            identifier = item[0] if item else None
            text = item[1] if len(item) > 1 else ""
            metadata = dict(item[2]) if len(item) > 2 and isinstance(item[2], Mapping) else {}
        else:
            continue

        clean = _clean_text(text)
        if not clean:
            continue
        candidate_user = metadata.get("user_id")
        # A scoped retriever must return owner provenance.  Missing ownership is
        # treated as ineligible rather than trusted by implication.
        if candidate_user in (None, "") or str(candidate_user) != str(user_id):
            continue
        if str(metadata.get("role") or "").lower() == "system":
            continue
        source_item_id = str(identifier or _candidate_id(source, clean, index))
        memory_type = str(
            metadata.get("memory_type")
            or metadata.get("type")
            or ("conversation_message" if source == "conversation_history" else "memory")
        )
        candidate = _Candidate(
            source=source, source_item_id=source_item_id, text=clean,
            metadata=metadata, memory_type=memory_type,
        )
        if not _is_trait(candidate):
            normalized.append(candidate)
    return normalized


def _deduplicate(candidates: Sequence[_Candidate]) -> list[_Candidate]:
    unique: dict[str, _Candidate] = {}
    for candidate in candidates:
        fingerprint = " ".join(_tokens(candidate.text))[:600]
        if not fingerprint:
            continue
        previous = unique.get(fingerprint)
        if previous is None or candidate.semantic_relevance > previous.semantic_relevance:
            unique[fingerprint] = candidate
    return list(unique.values())


def _default_chroma_retriever(*, user_id: int, query: str, limit: int) -> Any:
    from core.memory_database import chroma_recall_with_meta

    return chroma_recall_with_meta(
        query, limit, user_id=user_id, return_status=True
    )


def _default_conversation_retriever(
    *,
    user_id: int,
    query: str,
    conversation_id: str | None,
    limit: int,
    purpose: SemanticMemoryPurpose = "chat",
) -> list[dict[str, Any]]:
    """Fetch a bounded owner-scoped lexical candidate pool, never a chat dump."""

    from core.memory_database import (
        get_recent_semantic_conversation_candidates,
        search_messages_page,
    )

    if purpose == "greeting":
        return get_recent_semantic_conversation_candidates(user_id, limit=limit)

    search_terms = list(dict.fromkeys(_tokens(query)))[:4]
    if not search_terms:
        return []
    collected: dict[str, dict[str, Any]] = {}
    per_term = max(3, math.ceil(limit / len(search_terms)))
    for term in search_terms:
        page = search_messages_page(user_id, term, page_size=min(per_term, limit))
        for item in page.get("results", []):
            owned_item = dict(item)
            owned_item["user_id"] = user_id
            identifier = str(owned_item.get("message_id") or "")
            if identifier:
                collected.setdefault(identifier, owned_item)
            if len(collected) >= limit:
                return list(collected.values())
    return list(collected.values())[:limit]


class SemanticMemoryCoordinator:
    """Owner-scoped semantic selection and deterministic context preparation."""

    def __init__(
        self,
        *,
        chroma_retriever: Callable[..., Any] | None = None,
        conversation_retriever: Callable[..., Any] | None = None,
        usage_store: SemanticMemoryUsageStore | None = None,
        wall_clock: Callable[[], datetime] | None = None,
        monotonic_clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._chroma_retriever = chroma_retriever or _default_chroma_retriever
        self._conversation_retriever = conversation_retriever or _default_conversation_retriever
        self._usage_store = usage_store or MariaDBSemanticMemoryUsageStore()
        self._wall_clock = wall_clock or (lambda: datetime.now(timezone.utc))
        self._monotonic_clock = monotonic_clock

    def _source_candidates(
        self,
        *,
        source: Literal["chromadb", "conversation_history"],
        user_id: int,
        query: str,
        conversation_id: str | None,
        purpose: SemanticMemoryPurpose,
        pool_limit: int,
        failures: list[dict[str, str]],
    ) -> list[_Candidate]:
        try:
            if source == "chromadb":
                raw = self._chroma_retriever(user_id=user_id, query=query, limit=pool_limit)
            else:
                raw = self._conversation_retriever(
                    user_id=user_id,
                    query=query,
                    conversation_id=conversation_id,
                    limit=pool_limit,
                    purpose=purpose,
                )
            return _normalize_candidates(raw, source, user_id)[:pool_limit]
        except Exception as error:
            failures.append({"source": source, "stage": "retrieval", "error_type": type(error).__name__})
            return []

    def _rank_and_select(
        self,
        *,
        candidates: Sequence[_Candidate],
        query: str,
        conversation_id: str | None,
        user_id: int,
        source: Literal["chromadb", "conversation_history"],
        limit: int,
        failures: list[dict[str, str]],
    ) -> tuple[list[SemanticMemoryContextItem], int]:
        now = self._wall_clock()
        now = now.replace(tzinfo=timezone.utc) if now.tzinfo is None else now.astimezone(timezone.utc)
        for candidate in candidates:
            candidate.semantic_relevance = _semantic_relevance(query, candidate)
            candidate.stable_importance = _stable_importance(candidate)
            candidate.historical_connection = _historical_connection(candidate, conversation_id, now)

        eligible = [
            candidate
            for candidate in _deduplicate(candidates)
            if not (
                source == "conversation_history"
                and _clean_text(candidate.text).casefold() == _clean_text(query).casefold()
            )
            and (
                candidate.semantic_relevance >= MIN_SEMANTIC_RELEVANCE
                or (
                    source == "chromadb"
                    and _is_contextual_communication_preference(candidate)
                )
            )
        ]
        item_ids = [candidate.source_item_id for candidate in eligible]
        try:
            usage = self._usage_store.get_usage(
                user_id=user_id, source=source, source_item_ids=item_ids
            ) if item_ids else {}
        except Exception as error:
            usage = {}
            failures.append({"source": source, "stage": "usage_read", "error_type": type(error).__name__})

        current_cycle = max(
            [int(record.get("rotation_cycle") or 1) for record in usage.values()] or [1]
        )
        if eligible and all(
            candidate.source_item_id in usage
            and int(usage[candidate.source_item_id].get("rotation_cycle") or 0) >= current_cycle
            for candidate in eligible
        ):
            current_cycle += 1

        for candidate in eligible:
            record = usage.get(candidate.source_item_id)
            unused = record is None or int(record.get("rotation_cycle") or 0) < current_cycle
            candidate.rotation_preference = 1.0 if unused else 0.1
            candidate.rotation_cycle = current_cycle
            candidate.score = (
                0.70 * candidate.semantic_relevance
                + 0.15 * candidate.stable_importance
                + 0.10 * candidate.historical_connection
                + 0.05 * candidate.rotation_preference
            )

        eligible.sort(
            key=lambda candidate: (
                -candidate.score,
                -candidate.semantic_relevance,
                -candidate.stable_importance,
                candidate.source_item_id,
            )
        )
        selected: list[SemanticMemoryContextItem] = []
        for candidate in eligible[:limit]:
            context = _compress_text(
                candidate.text, query, conversation=source == "conversation_history"
            )
            if not context:
                continue
            selected.append(
                SemanticMemoryContextItem(
                    source=source,
                    source_item_id=candidate.source_item_id,
                    memory_type=candidate.memory_type,
                    context=context,
                    score=candidate.score,
                    semantic_relevance=candidate.semantic_relevance,
                    stable_importance=candidate.stable_importance,
                    historical_connection=candidate.historical_connection,
                    rotation_preference=candidate.rotation_preference,
                    rotation_cycle=candidate.rotation_cycle,
                )
            )
        return selected, len(eligible)

    def retrieve_semantic_context(
        self,
        *,
        user_id: int,
        query: str,
        conversation_id: str | None,
        purpose: SemanticMemoryPurpose,
        allow_long_term_memory: bool,
        allow_conversation_history: bool,
        max_memories: int = 3,
        max_conversation_items: int = 3,
    ) -> SemanticMemoryContextPackage:
        (
            user_id, query, conversation_id, purpose,
            allow_long_term_memory, allow_conversation_history,
            max_memories, max_conversation_items,
        ) = _validate_request(
            user_id=user_id,
            query=query,
            conversation_id=conversation_id,
            purpose=purpose,
            allow_long_term_memory=allow_long_term_memory,
            allow_conversation_history=allow_conversation_history,
            max_memories=max_memories,
            max_conversation_items=max_conversation_items,
        )
        started = self._monotonic_clock()
        failures: list[dict[str, str]] = []
        pool_limit = DEFAULT_CANDIDATE_POOL_SIZE

        conversation_candidates = self._source_candidates(
            source="conversation_history", user_id=user_id, query=query,
            conversation_id=conversation_id, purpose=purpose,
            pool_limit=pool_limit, failures=failures,
        ) if allow_conversation_history and max_conversation_items else []

        # A greeting has no substantive user query. Recent owner-scoped
        # conversation candidates provide bounded topic terms so long-term
        # recall remains semantically grounded instead of becoming an
        # enumeration or a random-memory draw.
        ranking_query = query
        if purpose == "greeting" and conversation_candidates:
            recent_topics = " ".join(
                _compress_text(item.text, query, conversation=True)
                for item in conversation_candidates[:6]
            )
            ranking_query = f"{query} {recent_topics}"[:2400]

        memory_candidates = self._source_candidates(
            source="chromadb", user_id=user_id, query=ranking_query,
            conversation_id=conversation_id, purpose=purpose,
            pool_limit=pool_limit, failures=failures,
        ) if allow_long_term_memory and max_memories else []

        memories, eligible_memories = self._rank_and_select(
            candidates=memory_candidates, query=ranking_query, conversation_id=conversation_id,
            user_id=user_id, source="chromadb", limit=max_memories, failures=failures,
        ) if memory_candidates else ([], 0)
        conversations, eligible_conversations = self._rank_and_select(
            candidates=conversation_candidates, query=ranking_query, conversation_id=conversation_id,
            user_id=user_id, source="conversation_history", limit=max_conversation_items,
            failures=failures,
        ) if conversation_candidates else ([], 0)

        selections = [
            {
                "source": item.source,
                "source_item_id": item.source_item_id,
                "memory_type": item.memory_type,
                "rotation_cycle": item.rotation_cycle,
            }
            for item in (*memories, *conversations)
        ]
        if selections:
            try:
                self._usage_store.record_selections(user_id=user_id, selections=selections)
            except Exception as error:
                failures.append({"source": "usage", "stage": "usage_write", "error_type": type(error).__name__})

        context_lines = ["MEMORY CONTEXT:"]
        if memories:
            context_lines.append("\nRelevant memories:")
            context_lines.extend(f"- {item.context}" for item in memories)
        if conversations:
            context_lines.append("\nRelated conversation history:")
            context_lines.extend(f"- {item.context}" for item in conversations)
        compressed_context_block = "\n".join(context_lines) if memories or conversations else ""

        all_selected = (*memories, *conversations)
        telemetry = {
            "mode": SEMANTIC_MEMORY_COORDINATOR_MODE,
            "authoritative_for_new_path": SEMANTIC_MEMORY_COORDINATOR_AUTHORITATIVE,
            "production_active": SEMANTIC_MEMORY_COORDINATOR_PRODUCTION_ACTIVE,
            "retrieval_method": "semantic_memory_coordinator",
            "purpose": purpose,
            "candidate_pool_limit": pool_limit,
            "candidate_counts": {
                "chromadb": len(memory_candidates),
                "conversation_history": len(conversation_candidates),
            },
            "eligible_counts": {
                "chromadb": eligible_memories,
                "conversation_history": eligible_conversations,
            },
            "selected_counts": {
                "chromadb": len(memories),
                "conversation_history": len(conversations),
                "prepared_context": len(all_selected),
                # Consumers set this to the actual count after prompt assembly.
                "injected_context": 0,
            },
            "selected_references": [item.reference for item in all_selected],
            "scores": {item.reference: item.safe_score_metrics() for item in all_selected},
            "compression": {
                "performed": bool(all_selected),
                "compressed_item_count": len(all_selected),
                "context_char_count": len(compressed_context_block),
            },
            "latency_ms": round(max(0.0, (self._monotonic_clock() - started) * 1000), 4),
            "failures": failures,
            "schema_version": SEMANTIC_MEMORY_COORDINATOR_SCHEMA_VERSION,
        }
        return SemanticMemoryContextPackage(
            selected_memories=tuple(memories),
            selected_conversations=tuple(conversations),
            compressed_context_block=compressed_context_block,
            telemetry=telemetry,
        )


_DEFAULT_COORDINATOR = SemanticMemoryCoordinator()


def retrieve_semantic_context(
    *,
    user_id: int,
    query: str,
    conversation_id: str | None,
    purpose: SemanticMemoryPurpose,
    allow_long_term_memory: bool,
    allow_conversation_history: bool,
    max_memories: int = 3,
    max_conversation_items: int = 3,
) -> SemanticMemoryContextPackage:
    """Authoritative owner-scoped entry point for semantic context retrieval."""

    return _DEFAULT_COORDINATOR.retrieve_semantic_context(
        user_id=user_id,
        query=query,
        conversation_id=conversation_id,
        purpose=purpose,
        allow_long_term_memory=allow_long_term_memory,
        allow_conversation_history=allow_conversation_history,
        max_memories=max_memories,
        max_conversation_items=max_conversation_items,
    )


def compare_semantic_context_shadow(
    *,
    current_retrieval_result: Any,
    coordinator: SemanticMemoryCoordinator | None = None,
    user_id: int,
    query: str,
    conversation_id: str | None,
    purpose: SemanticMemoryPurpose,
    allow_long_term_memory: bool,
    allow_conversation_history: bool,
    max_memories: int = 3,
    max_conversation_items: int = 3,
) -> SemanticMemoryShadowComparison:
    """Run the new path beside a legacy result without switching or injecting it."""

    current_candidates = _normalize_candidates(current_retrieval_result, "chromadb", user_id)
    package = (coordinator or _DEFAULT_COORDINATOR).retrieve_semantic_context(
        user_id=user_id,
        query=query,
        conversation_id=conversation_id,
        purpose=purpose,
        allow_long_term_memory=allow_long_term_memory,
        allow_conversation_history=allow_conversation_history,
        max_memories=max_memories,
        max_conversation_items=max_conversation_items,
    )
    return SemanticMemoryShadowComparison(
        current_result_count=len(current_candidates),
        current_references=tuple(candidate.reference for candidate in current_candidates),
        semantic_context=package,
    )


def semantic_memory_shadow_telemetry(
    *,
    current_retrieval_result: Any,
    current_retrieval_method: str,
    current_selected_count: int | None = None,
    current_injected_count: int = 0,
    coordinator: SemanticMemoryCoordinator | None = None,
    user_id: int,
    query: str,
    conversation_id: str | None,
    purpose: SemanticMemoryPurpose,
    allow_long_term_memory: bool,
    allow_conversation_history: bool,
    max_memories: int = 3,
    max_conversation_items: int = 3,
) -> dict[str, Any]:
    """Return a content-free old/new comparison for a real shadow request."""

    comparison = compare_semantic_context_shadow(
        current_retrieval_result=current_retrieval_result,
        coordinator=coordinator,
        user_id=user_id,
        query=query,
        conversation_id=conversation_id,
        purpose=purpose,
        allow_long_term_memory=allow_long_term_memory,
        allow_conversation_history=allow_conversation_history,
        max_memories=max_memories,
        max_conversation_items=max_conversation_items,
    )
    old_count = comparison.current_result_count
    selected_count = old_count if current_selected_count is None else max(
        0, min(int(current_selected_count), old_count)
    )
    injected_count = max(0, min(int(current_injected_count), selected_count))
    semantic = comparison.semantic_context.telemetry
    new_references = tuple(semantic.get("selected_references") or ())
    overlap = set(comparison.current_references).intersection(new_references)
    return {
        "mode": "shadow",
        "production_active": False,
        "legacy": {
            "retrieval_method": str(current_retrieval_method or "unknown")[:120],
            "candidates_found": old_count,
            "selected_count": selected_count,
            "injected_count": injected_count,
            "references": list(comparison.current_references),
        },
        "semantic": dict(semantic),
        "comparison": {
            "legacy_reference_count": len(comparison.current_references),
            "semantic_reference_count": len(new_references),
            "overlap_count": len(overlap),
        },
    }


def semantic_memory_package_has_failure(
    package: SemanticMemoryContextPackage,
) -> bool:
    """Return true when any required coordinator operation failed.

    Production consumers use this to fall back as one unit. This includes
    selection-usage persistence because rotation is part of the production
    contract and the migration is a documented prerequisite.
    """

    failures = package.telemetry.get("failures")
    if not isinstance(failures, Sequence) or isinstance(
        failures, (str, bytes, bytearray)
    ):
        return False
    return any(isinstance(failure, Mapping) for failure in failures)


def semantic_memory_production_telemetry(
    package: SemanticMemoryContextPackage | None,
    *,
    injected_context_count: int = 0,
    fallback_used: bool = False,
    failure: BaseException | None = None,
) -> dict[str, Any]:
    """Build content-free metrics for one production attempt."""

    semantic = dict(package.telemetry) if package is not None else {}
    selected_counts = dict(semantic.get("selected_counts") or {})
    prepared = max(0, int(selected_counts.get("prepared_context") or 0))
    selected_counts["injected_context"] = min(
        max(0, int(injected_context_count)), prepared
    )
    semantic["selected_counts"] = selected_counts
    semantic["mode"] = "production"
    semantic["production_active"] = bool(package is not None and not fallback_used)
    semantic["retrieval_method"] = "Production Semantic Memory Coordinator"
    semantic["fallback_used"] = bool(fallback_used)
    if failure is not None:
        semantic["fallback_failure"] = {
            "source": "coordinator",
            "stage": "production_retrieval",
            "error_type": type(failure).__name__,
        }

    scores = semantic.get("scores") if isinstance(semantic.get("scores"), Mapping) else {}
    rotation_cycles: dict[str, int] = {"chromadb": 0, "conversation_history": 0}
    for reference, metrics in scores.items():
        if not isinstance(metrics, Mapping):
            continue
        source = "chromadb" if str(reference).startswith("memory:") else "conversation_history"
        try:
            cycle = max(0, int(metrics.get("rotation_cycle") or 0))
        except (TypeError, ValueError):
            cycle = 0
        rotation_cycles[source] = max(rotation_cycles[source], cycle)
    semantic["rotation_cycles"] = rotation_cycles
    return semantic


def sanitize_semantic_memory_production_telemetry(value: Any) -> dict[str, Any]:
    """Whitelist production metrics before API or persisted metadata exposure."""

    if not isinstance(value, Mapping) or value.get("mode") != "production":
        return {}

    def count(raw: Any) -> int:
        try:
            return max(0, int(raw))
        except (TypeError, ValueError):
            return 0

    def count_map(raw: Any) -> dict[str, int]:
        if not isinstance(raw, Mapping):
            return {}
        return {str(key)[:64]: count(item) for key, item in raw.items()}

    def references(raw: Any) -> list[str]:
        if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes, bytearray)):
            return []
        return [str(item)[:230] for item in raw[:12] if str(item).strip()]

    failures = []
    raw_failures = value.get("failures")
    if isinstance(raw_failures, Sequence) and not isinstance(
        raw_failures, (str, bytes, bytearray)
    ):
        for item in raw_failures[:8]:
            if isinstance(item, Mapping):
                failures.append({
                    key: str(item.get(key) or "")[:80]
                    for key in ("source", "stage", "error_type")
                })
    fallback_failure = value.get("fallback_failure")
    if isinstance(fallback_failure, Mapping):
        failures.append({
            key: str(fallback_failure.get(key) or "")[:80]
            for key in ("source", "stage", "error_type")
        })

    compression = value.get("compression") if isinstance(value.get("compression"), Mapping) else {}
    return {
        "mode": "production",
        "production_active": bool(value.get("production_active")),
        "retrieval_method": "Production Semantic Memory Coordinator",
        "purpose": str(value.get("purpose") or "")[:16],
        "candidate_counts": count_map(value.get("candidate_counts")),
        "eligible_counts": count_map(value.get("eligible_counts")),
        "selected_counts": count_map(value.get("selected_counts")),
        "selected_references": references(value.get("selected_references")),
        "rotation_cycles": count_map(value.get("rotation_cycles")),
        "compression": {
            "performed": bool(compression.get("performed")),
            "compressed_item_count": count(compression.get("compressed_item_count")),
            "context_char_count": count(compression.get("context_char_count")),
        },
        "fallback_used": bool(value.get("fallback_used")),
        "failures": failures,
        "schema_version": str(value.get("schema_version") or "")[:16],
    }


def sanitize_semantic_memory_shadow_telemetry(value: Any) -> dict[str, Any]:
    """Whitelist content-free metrics before API or message-metadata exposure."""

    if not isinstance(value, Mapping) or value.get("mode") != "shadow":
        return {}

    def count(raw: Any) -> int:
        try:
            return max(0, int(raw))
        except (TypeError, ValueError):
            return 0

    def nonnegative_float(raw: Any) -> float:
        try:
            number = float(raw)
        except (TypeError, ValueError):
            return 0.0
        return number if math.isfinite(number) and number >= 0 else 0.0

    def references(raw: Any) -> list[str]:
        if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes, bytearray)):
            return []
        return [str(item)[:230] for item in raw[:12] if str(item).strip()]

    legacy_raw = value.get("legacy") if isinstance(value.get("legacy"), Mapping) else {}
    semantic_raw = value.get("semantic") if isinstance(value.get("semantic"), Mapping) else {}
    comparison_raw = value.get("comparison") if isinstance(value.get("comparison"), Mapping) else {}
    failures_raw = semantic_raw.get("failures")
    safe_failures = []
    if isinstance(failures_raw, Sequence) and not isinstance(failures_raw, (str, bytes, bytearray)):
        for failure in failures_raw[:8]:
            if isinstance(failure, Mapping):
                safe_failures.append({
                    key: str(failure.get(key) or "")[:80]
                    for key in ("source", "stage", "error_type")
                })

    def count_map(name: str) -> dict[str, int]:
        raw = semantic_raw.get(name)
        if not isinstance(raw, Mapping):
            return {}
        return {str(key)[:64]: count(item) for key, item in raw.items()}

    compression_raw = (
        semantic_raw.get("compression")
        if isinstance(semantic_raw.get("compression"), Mapping)
        else {}
    )
    scores_raw = semantic_raw.get("scores")
    safe_scores: dict[str, dict[str, float | int]] = {}
    if isinstance(scores_raw, Mapping):
        for reference, metrics in list(scores_raw.items())[:6]:
            if not isinstance(metrics, Mapping):
                continue
            safe_scores[str(reference)[:230]] = {
                "score": nonnegative_float(metrics.get("score")),
                "semantic_relevance": nonnegative_float(metrics.get("semantic_relevance")),
                "stable_importance": nonnegative_float(metrics.get("stable_importance")),
                "historical_connection": nonnegative_float(metrics.get("historical_connection")),
                "rotation_preference": nonnegative_float(metrics.get("rotation_preference")),
                "rotation_cycle": count(metrics.get("rotation_cycle")),
            }
    return {
        "mode": "shadow",
        "production_active": False,
        "legacy": {
            "retrieval_method": str(legacy_raw.get("retrieval_method") or "")[:120],
            "candidates_found": count(legacy_raw.get("candidates_found")),
            "selected_count": count(legacy_raw.get("selected_count")),
            "injected_count": count(legacy_raw.get("injected_count")),
            "references": references(legacy_raw.get("references")),
        },
        "semantic": {
            "retrieval_method": str(semantic_raw.get("retrieval_method") or "")[:80],
            "purpose": str(semantic_raw.get("purpose") or "")[:16],
            "candidate_pool_limit": count(semantic_raw.get("candidate_pool_limit")),
            "candidate_counts": count_map("candidate_counts"),
            "eligible_counts": count_map("eligible_counts"),
            "selected_counts": count_map("selected_counts"),
            "selected_references": references(semantic_raw.get("selected_references")),
            "scores": safe_scores,
            "compression": {
                "performed": bool(compression_raw.get("performed")),
                "compressed_item_count": count(compression_raw.get("compressed_item_count")),
                "context_char_count": count(compression_raw.get("context_char_count")),
            },
            "latency_ms": nonnegative_float(semantic_raw.get("latency_ms")),
            "failures": safe_failures,
            "schema_version": str(semantic_raw.get("schema_version") or "")[:16],
            "production_active": False,
        },
        "comparison": {
            "legacy_reference_count": count(comparison_raw.get("legacy_reference_count")),
            "semantic_reference_count": count(comparison_raw.get("semantic_reference_count")),
            "overlap_count": count(comparison_raw.get("overlap_count")),
        },
    }
