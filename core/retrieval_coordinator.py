"""Aetheraeon architecture: Phase 3 Retrieval Coordinator (shadow adapter).

Retrieval Coordinator responsibility:
    Observe explicitly requested conversation-history or ChromaDB retrieval
    through supplied callables and describe the observed result with the
    versioned Phase 0A ``RetrievalResult`` contract.

Architecture layer:
    Cognitive Intelligence Layer retrieval coordination boundary, between an
    approved retrieval plan and existing retrieval implementations.

Responsibilities:
    - provide one isolated interface for the current conversation and ChromaDB
      retrieval sources, while reserving source names for scoped and candidate
      memory;
    - preserve the supplied retriever's successful output object unchanged;
    - record safe, content-free retrieval metadata and correlation identifiers.

Boundaries:
    - adapter-only; in Phase 6 only the existing semantic-memory recall wrapper
      imports this module, while all other retrieval paths remain unchanged;
    - does not determine memory policy, promote or write memory, re-rank or
      inject retrieved content, authorize tools, or authorize permissions;
    - does not replace memory_interface.py, memory_context_builder.py,
      ai_orchestrator.py, request_router.py, or any persistence implementation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import math
import time
from typing import Any, Callable, Mapping, Sequence

from core.cognitive_contracts import (
    COGNITIVE_CONTRACT_SCHEMA_VERSION,
    RetrievalResult,
)


RETRIEVAL_COORDINATOR_MODE = "shadow_adapter"
RETRIEVAL_COORDINATOR_AUTHORITATIVE = False
RETRIEVAL_COORDINATOR_SCHEMA_VERSION = "1.0"


class RetrievalSource(str, Enum):
    """Named retrieval sources represented by the architecture boundary."""

    CONVERSATION_HISTORY = "conversation_history"
    CHROMADB = "chromadb"
    SCOPED_MEMORY = "scoped_memory"
    CANDIDATE_MEMORY = "candidate_memory"


class RetrievalCoordinatorError(ValueError):
    """Raised when isolated adapter inputs would produce invalid metadata."""


def _nonempty_string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RetrievalCoordinatorError(f"{name} must be a non-empty string")
    return value.strip()


def _nonnegative_int(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise RetrievalCoordinatorError(f"{name} must be a non-negative integer")
    return value


def _safe_count(value: Any) -> int:
    """Count a result container without consuming or copying its content."""

    if value is None:
        return 0
    try:
        return len(value)
    except TypeError:
        return 0


def _status_payload(value: Any) -> tuple[Any, Mapping[str, Any] | None]:
    """Separate an existing optional ``(results, status)`` return unchanged."""

    if (
        isinstance(value, tuple)
        and len(value) == 2
        and isinstance(value[1], Mapping)
        and {"attempted", "completed"}.issubset(value[1])
    ):
        return value[0], value[1]
    return value, None


def _reference_prefix(source: RetrievalSource) -> str:
    return "conversation" if source is RetrievalSource.CONVERSATION_HISTORY else "memory"


def _safe_references(source: RetrievalSource, content: Any) -> tuple[str, ...]:
    """Create opaque references only; never copy retrieved content into metadata."""

    if not isinstance(content, Sequence) or isinstance(content, (str, bytes, bytearray)):
        return ()

    references: list[str] = []
    prefix = _reference_prefix(source)
    for index, item in enumerate(content):
        identifier: Any = None
        if isinstance(item, Mapping):
            for field_name in ("id", "message_id", "memory_id", "uuid"):
                if item.get(field_name) not in (None, ""):
                    identifier = item[field_name]
                    break
        elif (
            source is RetrievalSource.CHROMADB
            and isinstance(item, Sequence)
            and not isinstance(item, (str, bytes, bytearray))
            and item
        ):
            identifier = item[0]

        suffix = str(identifier) if identifier is not None else f"index-{index}"
        references.append(f"{prefix}:{suffix}")
    return tuple(references)


def _actual_relevance_scores(
    content: Any, references: tuple[str, ...]
) -> Mapping[str, float]:
    """Return only scores present in an already structured source result."""

    if not isinstance(content, Sequence) or isinstance(content, (str, bytes, bytearray)):
        return {}
    scores: dict[str, float] = {}
    for item, reference in zip(content, references):
        if not isinstance(item, Mapping):
            continue
        score = next(
            (item[name] for name in ("relevance_score", "score") if name in item),
            None,
        )
        if isinstance(score, bool) or not isinstance(score, (int, float)):
            continue
        if math.isfinite(float(score)):
            scores[reference] = float(score)
    return scores


@dataclass(frozen=True, slots=True)
class CoordinatedRetrieval:
    """Read-only envelope around an unchanged retrieval return value."""

    retrieval_result: RetrievalResult
    retrieved_content: Any
    raw_output: Any
    source: RetrievalSource
    status: str
    provenance: Mapping[str, Any] = field(default_factory=dict)
    warnings: tuple[str, ...] = ()
    schema_version: str = RETRIEVAL_COORDINATOR_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if not isinstance(self.retrieval_result, RetrievalResult):
            raise RetrievalCoordinatorError("retrieval_result must be a RetrievalResult")
        if not isinstance(self.source, RetrievalSource):
            raise RetrievalCoordinatorError("source must be a RetrievalSource")
        _nonempty_string(self.status, "status")
        if not isinstance(self.provenance, Mapping):
            raise RetrievalCoordinatorError("provenance must be a mapping")
        if any(not isinstance(warning, str) or not warning.strip() for warning in self.warnings):
            raise RetrievalCoordinatorError("warnings must contain non-empty strings")
        if self.schema_version != RETRIEVAL_COORDINATOR_SCHEMA_VERSION:
            raise RetrievalCoordinatorError("unsupported coordinator schema_version")

    @property
    def trace_id(self) -> str:
        return self.retrieval_result.trace_id

    def to_metadata_dict(self) -> dict[str, Any]:
        """Serialize contract and metadata without serializing retrieved content."""

        return {
            "mode": RETRIEVAL_COORDINATOR_MODE,
            "authoritative": RETRIEVAL_COORDINATOR_AUTHORITATIVE,
            "source": self.source.value,
            "status": self.status,
            "retrieval_result": self.retrieval_result.to_dict(),
            "provenance": dict(self.provenance),
            "warnings": list(self.warnings),
            "schema_version": self.schema_version,
        }


class RetrievalAdapter:
    """Base adapter that forwards calls to one existing retrieval callable."""

    SOURCE: RetrievalSource

    def __init__(self, retriever: Callable[..., Any]) -> None:
        if not callable(retriever):
            raise RetrievalCoordinatorError("retriever must be callable")
        self._retriever = retriever

    def retrieve(
        self,
        *args: Any,
        trace_id: str,
        result_limit: int | None = None,
        selected_result_count: int | None = None,
        injected_result_count: int | None = None,
        truncated: bool = False,
        raise_on_error: bool = False,
        monotonic_clock: Callable[[], float] = time.monotonic,
        **kwargs: Any,
    ) -> CoordinatedRetrieval:
        """Forward arguments unchanged and return a separate observation envelope.

        This method is deliberately not an integration point: its callable is
        supplied by a direct caller, and Phase 3 adds no live-runtime imports.
        """

        trace_id = _nonempty_string(trace_id, "trace_id")
        if result_limit is not None:
            _nonnegative_int(result_limit, "result_limit")
        if selected_result_count is not None:
            _nonnegative_int(selected_result_count, "selected_result_count")
        if injected_result_count is not None:
            _nonnegative_int(injected_result_count, "injected_result_count")
        if not isinstance(truncated, bool):
            raise RetrievalCoordinatorError("truncated must be a boolean")
        if not isinstance(raise_on_error, bool):
            raise RetrievalCoordinatorError("raise_on_error must be a boolean")
        if not callable(monotonic_clock):
            raise RetrievalCoordinatorError("monotonic_clock must be callable")

        started = monotonic_clock()
        try:
            raw_output = self._retriever(*args, **kwargs)
        except Exception as error:
            if raise_on_error:
                raise
            latency_ms = round(max(0.0, (monotonic_clock() - started) * 1000), 6)
            result = RetrievalResult(
                trace_id=trace_id,
                source_name=self.SOURCE.value,
                attempted=True,
                completed=False,
                failure_reason=f"{type(error).__name__}: {error}",
                latency_ms=latency_ms,
                result_limit=result_limit,
            )
            return CoordinatedRetrieval(
                retrieval_result=result,
                retrieved_content=None,
                raw_output=None,
                source=self.SOURCE,
                status="failed",
                provenance={
                    "adapter": "existing_callable",
                    "source": self.SOURCE.value,
                    "content_preserved": True,
                },
                warnings=("Existing retriever raised; no content was transformed or retained.",),
            )

        latency_ms = round(max(0.0, (monotonic_clock() - started) * 1000), 6)
        content, source_status = _status_payload(raw_output)
        attempted = True if source_status is None else bool(source_status.get("attempted"))
        completed = True if source_status is None else bool(source_status.get("completed"))
        source_error = None if source_status is None else source_status.get("error")

        if not attempted:
            status = "not_attempted"
            warnings = (str(source_error),) if source_error else ()
            result = RetrievalResult(
                trace_id=trace_id,
                source_name=self.SOURCE.value,
                attempted=False,
                completed=False,
                result_limit=result_limit,
            )
        elif not completed:
            status = "failed"
            failure_reason = str(source_error) if source_error else "Existing retriever reported failure."
            warnings = ()
            result = RetrievalResult(
                trace_id=trace_id,
                source_name=self.SOURCE.value,
                attempted=True,
                completed=False,
                failure_reason=failure_reason,
                latency_ms=latency_ms,
                result_limit=result_limit,
            )
        else:
            raw_count = _safe_count(content)
            selected_count = raw_count if selected_result_count is None else selected_result_count
            injected_count = 0 if injected_result_count is None else injected_result_count
            if selected_count > raw_count or injected_count > selected_count:
                raise RetrievalCoordinatorError(
                    "selection and injection counts must not exceed observed result counts"
                )
            references = _safe_references(self.SOURCE, content)
            status = "completed"
            warnings = ()
            result = RetrievalResult(
                trace_id=trace_id,
                source_name=self.SOURCE.value,
                attempted=True,
                completed=True,
                raw_result_count=raw_count,
                eligible_result_count=raw_count,
                selected_result_count=selected_count,
                injected_result_count=injected_count,
                safe_references=references,
                relevance_scores=_actual_relevance_scores(content, references),
                latency_ms=latency_ms,
                truncated=truncated,
                result_limit=result_limit,
            )

        return CoordinatedRetrieval(
            retrieval_result=result,
            retrieved_content=content,
            raw_output=raw_output,
            source=self.SOURCE,
            status=status,
            provenance={
                "adapter": "existing_callable",
                "source": self.SOURCE.value,
                "content_preserved": True,
                "source_status_available": source_status is not None,
            },
            warnings=warnings,
        )


class ConversationRetrievalAdapter(RetrievalAdapter):
    """Adapter for the existing chronological conversation-history retriever."""

    SOURCE = RetrievalSource.CONVERSATION_HISTORY


class ChromaRetrievalAdapter(RetrievalAdapter):
    """Adapter for the existing ChromaDB semantic retrieval callable."""

    SOURCE = RetrievalSource.CHROMADB


class RetrievalCoordinator:
    """Explicit-source dispatcher for isolated existing-retrieval adapters."""

    def __init__(
        self,
        *,
        conversation: ConversationRetrievalAdapter | None = None,
        chromadb: ChromaRetrievalAdapter | None = None,
    ) -> None:
        self._adapters: dict[RetrievalSource, RetrievalAdapter] = {}
        if conversation is not None:
            self._adapters[RetrievalSource.CONVERSATION_HISTORY] = conversation
        if chromadb is not None:
            self._adapters[RetrievalSource.CHROMADB] = chromadb

    @property
    def available_sources(self) -> tuple[RetrievalSource, ...]:
        """Sources configured by the caller; future sources remain unavailable."""

        return tuple(self._adapters)

    def retrieve(self, source: RetrievalSource, *args: Any, **kwargs: Any) -> CoordinatedRetrieval:
        """Dispatch only the source explicitly selected by the caller."""

        if not isinstance(source, RetrievalSource):
            raise RetrievalCoordinatorError("source must be a RetrievalSource")
        try:
            adapter = self._adapters[source]
        except KeyError as error:
            raise RetrievalCoordinatorError(
                f"No adapter is configured for retrieval source {source.value!r}"
            ) from error
        return adapter.retrieve(*args, **kwargs)


def coordinate_conversation_retrieval(
    retriever: Callable[..., Any], *args: Any, **kwargs: Any
) -> CoordinatedRetrieval:
    """Direct isolated helper for an existing conversation retrieval callable."""

    return ConversationRetrievalAdapter(retriever).retrieve(*args, **kwargs)


def coordinate_chromadb_retrieval(
    retriever: Callable[..., Any], *args: Any, **kwargs: Any
) -> CoordinatedRetrieval:
    """Direct isolated helper for an existing ChromaDB retrieval callable."""

    return ChromaRetrievalAdapter(retriever).retrieve(*args, **kwargs)
