"""Privacy-safe, disabled-by-default Cognitive Trace infrastructure.

Phase 0B intentionally leaves this module disconnected from Aetheraeon's live
request path.  It has no side effects at import time and does not persist data.
Existing runtime modules do not import it.

The trace stores observable outcomes and measurements only.  Restricted content
is removed before an event is created, and event data is filtered again during
serialization as a defense against later mutation.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import math
import re
import threading
import time
from typing import Any, Callable, Mapping
from uuid import uuid4

from core.cognitive_contracts import (
    COGNITIVE_CONTRACT_SCHEMA_VERSION,
    CognitiveTraceEvent,
    ContractValidationError,
    TraceStage,
    TraceStatus,
)


COGNITIVE_TRACE_ENABLED_BY_DEFAULT = False
COGNITIVE_TRACE_SCHEMA_VERSION = COGNITIVE_CONTRACT_SCHEMA_VERSION
TRACE_REDACTION_MARKER = "[REDACTED]"

_MAX_TRACE_STRING_LENGTH = 2048
_MAX_TRACE_COLLECTION_ITEMS = 200
_MAX_TRACE_DEPTH = 12
_TRACE_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")

_SECRET_ASSIGNMENT_PATTERN = re.compile(
    r"(?i)\b(api[ _-]?key|password|passwd|secret|access[ _-]?token|"
    r"refresh[ _-]?token|authorization|credential(?:s)?)\b\s*[:=]\s*"
    r"([^\s,;]+)"
)
_BEARER_PATTERN = re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/-]{6,}=*")
_COMMON_API_KEY_PATTERN = re.compile(
    r"\b(?:sk|pk|rk|ghp|github_pat|xox[baprs])[-_][A-Za-z0-9_-]{8,}\b"
)
_AWS_ACCESS_KEY_PATTERN = re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")
_PRIVATE_KEY_PATTERN = re.compile(
    r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----.*?"
    r"-----END [A-Z0-9 ]*PRIVATE KEY-----",
    re.DOTALL,
)

_DIRECT_CONTENT_KEYS = frozenset(
    {
        "chain_of_thought",
        "private_chain_of_thought",
        "reasoning_text",
        "reasoning_content",
        "reasoning_transcript",
        "reasoning_steps",
        "reasoning",
        "private_reasoning",
        "model_reasoning",
        "thoughts",
        "thinking",
        "rationale",
        "scratch_work",
        "hidden_scratch_work",
        "analysis",
        "analysis_text",
        "analysis_transcript",
        "instructions",
        "system_instructions",
        "developer_instructions",
        "generation_context",
        "model_input",
        "llm_input",
        "tool_input",
        "tool_output",
        "message",
        "messages",
        "user_message",
        "assistant_message",
        "response_text",
        "generated_response",
        "model_response",
        "raw_input",
        "raw_output",
        "content",
        "contents",
        "document",
        "documents",
        "payload",
        "raw_result",
        "raw_results",
        "transcript",
        "memory",
        "memories",
        "memory_content",
        "memory_contents",
        "memory_text",
        "retrieved_memory",
        "retrieved_memories",
        "password",
        "passwd",
        "secret",
        "secrets",
        "credential",
        "credentials",
        "authorization",
        "api_key",
        "apikey",
        "access_token",
        "refresh_token",
        "session_id",
        "session_identifier",
        "raw_embedding",
        "raw_embeddings",
        "embedding_vector",
        "embedding_vectors",
    }
)

_REASONING_TEXT_PARTS = frozenset(
    {"text", "content", "summary", "transcript", "steps", "scratch", "analysis"}
)
_MEMORY_CONTENT_PARTS = frozenset(
    {"content", "contents", "text", "value", "values", "document", "documents", "payload", "raw"}
)
_SAFE_TOKEN_METADATA_KEYS = frozenset(
    {"token_count", "token_counts", "input_token_count", "output_token_count"}
)


class CognitiveTraceError(ValueError):
    """Base error for invalid trace data or state transitions."""


class CognitiveTraceStateError(CognitiveTraceError):
    """Raised when a finalized trace is modified."""


@dataclass(frozen=True, slots=True)
class PrivacyFilterResult:
    """A filtered copy and the number of removed or redacted values."""

    data: Mapping[str, Any]
    redaction_count: int


def generate_correlation_id() -> str:
    """Return an opaque correlation identifier containing no user information."""

    return f"ctrace_{uuid4().hex}"


def _normalize_key(key: str) -> str:
    normalized = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", key)
    normalized = re.sub(r"[^A-Za-z0-9]+", "_", normalized)
    return normalized.strip("_").lower()


def _key_parts(normalized_key: str) -> frozenset[str]:
    return frozenset(part for part in normalized_key.split("_") if part)


def _is_sensitive_key(key: str) -> bool:
    normalized = _normalize_key(key)
    parts = _key_parts(normalized)

    if normalized == "privacy_redaction_count":
        return True
    if normalized in _DIRECT_CONTENT_KEYS:
        return True
    if "prompt" in parts or "prompts" in parts:
        return True
    if "password" in parts or "passwd" in parts or "secret" in parts or "secrets" in parts:
        return True
    if "credential" in parts or "credentials" in parts:
        return True
    if "api" in parts and ("key" in parts or "keys" in parts):
        return True
    if "token" in parts or "tokens" in parts:
        return normalized not in _SAFE_TOKEN_METADATA_KEYS
    if "reasoning" in parts and parts.intersection(_REASONING_TEXT_PARTS):
        return True
    if "memory" in parts or "memories" in parts:
        if parts.intersection(_MEMORY_CONTENT_PARTS):
            return True
    return False


def _is_restricted_context(path: tuple[str, ...], category: str) -> bool:
    for key in path:
        parts = _key_parts(_normalize_key(key))
        if category == "reasoning":
            if "reasoning" in parts or "cognition" in parts or "analytical" in parts:
                return True
            if "creative" in parts and "contextual" in parts:
                return True
        if category == "memory" and ({"memory", "memories"} & parts):
            return True
    return False


def _redact_sensitive_text(value: str) -> tuple[str, int]:
    redaction_count = 0
    filtered = value

    def replace_assignment(match: re.Match[str]) -> str:
        nonlocal redaction_count
        redaction_count += 1
        return f"{match.group(1)}={TRACE_REDACTION_MARKER}"

    filtered = _SECRET_ASSIGNMENT_PATTERN.sub(replace_assignment, filtered)
    for pattern in (
        _BEARER_PATTERN,
        _COMMON_API_KEY_PATTERN,
        _AWS_ACCESS_KEY_PATTERN,
        _PRIVATE_KEY_PATTERN,
    ):
        filtered, replacements = pattern.subn(TRACE_REDACTION_MARKER, filtered)
        redaction_count += replacements

    if len(filtered) > _MAX_TRACE_STRING_LENGTH:
        filtered = filtered[:_MAX_TRACE_STRING_LENGTH] + "…"
        redaction_count += 1
    return filtered, redaction_count


def redact_sensitive_text(value: str) -> str:
    """Redact common credential and API-key forms from otherwise safe text."""

    if not isinstance(value, str):
        raise TypeError("value must be a string")
    return _redact_sensitive_text(value)[0]


_OMIT = object()


def _filter_value(
    value: Any,
    path: tuple[str, ...],
    depth: int,
) -> tuple[Any, int]:
    if depth > _MAX_TRACE_DEPTH:
        return _OMIT, 1
    if value is None or isinstance(value, (bool, int)):
        return value, 0
    if isinstance(value, float):
        if not math.isfinite(value):
            return _OMIT, 1
        return value, 0
    if isinstance(value, str):
        filtered, count = _redact_sensitive_text(value)
        return filtered, count
    if isinstance(value, Mapping):
        result: dict[str, Any] = {}
        redaction_count = 0
        for index, (raw_key, item) in enumerate(value.items()):
            if index >= _MAX_TRACE_COLLECTION_ITEMS:
                redaction_count += len(value) - index
                break
            if not isinstance(raw_key, str) or not raw_key.strip():
                redaction_count += 1
                continue
            key = raw_key.strip()
            normalized = _normalize_key(key)
            if _is_sensitive_key(key):
                redaction_count += 1
                continue

            parts = _key_parts(normalized)
            if _is_restricted_context(path, "reasoning"):
                if parts.intersection(_REASONING_TEXT_PARTS):
                    redaction_count += 1
                    continue
            if _is_restricted_context(path, "memory"):
                if parts.intersection(_MEMORY_CONTENT_PARTS):
                    redaction_count += 1
                    continue

            filtered, count = _filter_value(item, path + (key,), depth + 1)
            redaction_count += count
            if filtered is not _OMIT:
                result[key] = filtered
        return result, redaction_count
    if isinstance(value, (list, tuple)):
        result_list: list[Any] = []
        redaction_count = 0
        for index, item in enumerate(value):
            if index >= _MAX_TRACE_COLLECTION_ITEMS:
                redaction_count += len(value) - index
                break
            filtered, count = _filter_value(item, path, depth + 1)
            redaction_count += count
            if filtered is not _OMIT:
                result_list.append(filtered)
        return result_list, redaction_count
    return _OMIT, 1


def filter_trace_data(details: Mapping[str, Any] | None) -> PrivacyFilterResult:
    """Return a privacy-filtered copy suitable for a Cognitive Trace event.

    Restricted fields are omitted rather than retained under their original key.
    The input mapping is never mutated and no reference to it is stored.
    """

    if details is None:
        return PrivacyFilterResult(data={}, redaction_count=0)
    if not isinstance(details, Mapping):
        raise TypeError("trace details must be a mapping or None")
    filtered, redaction_count = _filter_value(details, (), 0)
    if filtered is _OMIT or not isinstance(filtered, Mapping):
        return PrivacyFilterResult(data={}, redaction_count=max(1, redaction_count))
    return PrivacyFilterResult(data=dict(filtered), redaction_count=redaction_count)


def _validate_trace_id(trace_id: str) -> str:
    if not isinstance(trace_id, str) or not _TRACE_ID_PATTERN.fullmatch(trace_id):
        raise CognitiveTraceError(
            "trace_id must be an opaque 1-128 character correlation identifier"
        )
    filtered, redaction_count = _redact_sensitive_text(trace_id)
    if redaction_count or TRACE_REDACTION_MARKER in filtered:
        raise CognitiveTraceError("trace_id must not contain credential or API-key data")
    return trace_id


def _safe_reference(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    if not normalized or len(normalized) > 512 or any(char.isspace() for char in normalized):
        return None
    filtered, redaction_count = _redact_sensitive_text(normalized)
    if redaction_count or TRACE_REDACTION_MARKER in filtered:
        return None
    return filtered


def _safe_short_label(value: Any) -> str | None:
    if value is None or not isinstance(value, str):
        return None
    normalized = value.strip()
    if not normalized or len(normalized) > 128 or "\n" in normalized or "\r" in normalized:
        return None
    filtered, redaction_count = _redact_sensitive_text(normalized)
    if redaction_count:
        return None
    return filtered


def _safe_string_tuple(values: Any) -> tuple[str, ...]:
    if values is None:
        return ()
    if isinstance(values, (str, bytes)) or not isinstance(values, (list, tuple)):
        raise CognitiveTraceError("trace references and reason codes must be sequences")
    safe: list[str] = []
    for value in values[:_MAX_TRACE_COLLECTION_ITEMS]:
        filtered = _safe_reference(value)
        if filtered is not None:
            safe.append(filtered)
    return tuple(safe)


def _coerce_stage(value: TraceStage | str) -> TraceStage:
    try:
        return value if isinstance(value, TraceStage) else TraceStage(value)
    except (TypeError, ValueError) as exc:
        raise CognitiveTraceError(f"invalid trace stage: {value!r}") from exc


def _coerce_status(value: TraceStatus | str) -> TraceStatus:
    try:
        return value if isinstance(value, TraceStatus) else TraceStatus(value)
    except (TypeError, ValueError) as exc:
        raise CognitiveTraceError(f"invalid trace status: {value!r}") from exc


def _utc_timestamp(clock: Callable[[], datetime]) -> str:
    value = clock()
    if not isinstance(value, datetime):
        raise CognitiveTraceError("trace clock must return datetime values")
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    value = value.astimezone(timezone.utc)
    return value.isoformat(timespec="milliseconds").replace("+00:00", "Z")


class CognitiveTrace:
    """In-memory record of one cognitive run.

    Tracing is disabled unless ``enabled=True`` is supplied explicitly.  Disabled
    traces generate an opaque correlation ID but capture no events or user data.
    """

    def __init__(
        self,
        *,
        enabled: bool = COGNITIVE_TRACE_ENABLED_BY_DEFAULT,
        trace_id: str | None = None,
        user_reference: str | None = None,
        conversation_reference: str | None = None,
        clock: Callable[[], datetime] | None = None,
        monotonic_clock: Callable[[], float] | None = None,
    ) -> None:
        if not isinstance(enabled, bool):
            raise CognitiveTraceError("enabled must be a boolean")

        self.enabled = enabled
        self.trace_id = _validate_trace_id(trace_id or generate_correlation_id())
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._monotonic_clock = monotonic_clock or time.perf_counter
        self.created_at = _utc_timestamp(self._clock)
        self._created_monotonic = float(self._monotonic_clock())
        if not math.isfinite(self._created_monotonic):
            raise CognitiveTraceError("monotonic clock must return a finite number")

        # Disabled traces intentionally retain no supplied user or conversation data.
        self.user_reference = _safe_reference(user_reference) if enabled else None
        self.conversation_reference = (
            _safe_reference(conversation_reference) if enabled else None
        )
        self._events: list[CognitiveTraceEvent] = []
        self._stage_starts: dict[TraceStage, float] = {}
        self._ended_at: str | None = None
        self._duration_ms: float | None = None
        self._final_status: TraceStatus | None = None
        self._lock = threading.RLock()

        if self.enabled:
            self._append_event(
                stage=TraceStage.TRACE_CREATED,
                status=TraceStatus.COMPLETED,
                occurred_at=self.created_at,
                latency_ms=0.0,
            )

    @property
    def correlation_id(self) -> str:
        return self.trace_id

    @property
    def events(self) -> tuple[CognitiveTraceEvent, ...]:
        with self._lock:
            return tuple(self._events)

    @property
    def finalized(self) -> bool:
        return self._final_status is not None

    @property
    def final_status(self) -> TraceStatus | None:
        return self._final_status

    @property
    def duration_ms(self) -> float | None:
        return self._duration_ms

    def _ensure_open(self) -> None:
        if self.finalized:
            raise CognitiveTraceStateError("a finalized cognitive trace cannot be modified")

    def _append_event(
        self,
        *,
        stage: TraceStage,
        status: TraceStatus,
        occurred_at: str | None = None,
        latency_ms: float | None = None,
        source_message_reference: str | None = None,
        response_message_reference: str | None = None,
        intent: str | None = None,
        intent_confidence: float | None = None,
        reason_codes: tuple[str, ...] | list[str] = (),
        safe_references: tuple[str, ...] | list[str] = (),
        details: Mapping[str, Any] | None = None,
    ) -> CognitiveTraceEvent:
        privacy = filter_trace_data(details)
        safe_details = dict(privacy.data)
        if privacy.redaction_count:
            safe_details["privacy_redaction_count"] = privacy.redaction_count

        try:
            event = CognitiveTraceEvent(
                trace_id=self.trace_id,
                stage=stage,
                status=status,
                occurred_at=occurred_at or _utc_timestamp(self._clock),
                latency_ms=latency_ms,
                user_reference=self.user_reference,
                conversation_reference=self.conversation_reference,
                source_message_reference=_safe_reference(source_message_reference),
                response_message_reference=_safe_reference(response_message_reference),
                intent=_safe_short_label(intent),
                intent_confidence=intent_confidence,
                reason_codes=_safe_string_tuple(reason_codes),
                safe_references=_safe_string_tuple(safe_references),
                details=safe_details,
            )
        except ContractValidationError as exc:
            raise CognitiveTraceError(str(exc)) from exc
        self._events.append(event)
        return event

    def record_event(
        self,
        stage: TraceStage | str,
        status: TraceStatus | str,
        *,
        latency_ms: float | None = None,
        source_message_reference: str | None = None,
        response_message_reference: str | None = None,
        intent: str | None = None,
        intent_confidence: float | None = None,
        reason_codes: tuple[str, ...] | list[str] = (),
        safe_references: tuple[str, ...] | list[str] = (),
        details: Mapping[str, Any] | None = None,
    ) -> CognitiveTraceEvent | None:
        """Record one independently timed, privacy-filtered stage event."""

        if not self.enabled:
            return None
        with self._lock:
            self._ensure_open()
            return self._append_event(
                stage=_coerce_stage(stage),
                status=_coerce_status(status),
                latency_ms=latency_ms,
                source_message_reference=source_message_reference,
                response_message_reference=response_message_reference,
                intent=intent,
                intent_confidence=intent_confidence,
                reason_codes=reason_codes,
                safe_references=safe_references,
                details=details,
            )

    def start_stage(
        self,
        stage: TraceStage | str,
        *,
        details: Mapping[str, Any] | None = None,
    ) -> CognitiveTraceEvent | None:
        """Start independent duration measurement for a trace stage."""

        if not self.enabled:
            return None
        normalized_stage = _coerce_stage(stage)
        with self._lock:
            self._ensure_open()
            started = float(self._monotonic_clock())
            if not math.isfinite(started):
                raise CognitiveTraceError("monotonic clock must return a finite number")
            self._stage_starts[normalized_stage] = started
            return self._append_event(
                stage=normalized_stage,
                status=TraceStatus.STARTED,
                details=details,
            )

    def finish_stage(
        self,
        stage: TraceStage | str,
        *,
        status: TraceStatus | str = TraceStatus.COMPLETED,
        details: Mapping[str, Any] | None = None,
        source_message_reference: str | None = None,
        response_message_reference: str | None = None,
        intent: str | None = None,
        intent_confidence: float | None = None,
        reason_codes: tuple[str, ...] | list[str] = (),
        safe_references: tuple[str, ...] | list[str] = (),
    ) -> CognitiveTraceEvent | None:
        """Finish a stage and attach its monotonic duration when available."""

        if not self.enabled:
            return None
        normalized_stage = _coerce_stage(stage)
        normalized_status = _coerce_status(status)
        with self._lock:
            self._ensure_open()
            finished = float(self._monotonic_clock())
            if not math.isfinite(finished):
                raise CognitiveTraceError("monotonic clock must return a finite number")
            started = self._stage_starts.pop(normalized_stage, None)
            latency_ms = None if started is None else max(0.0, (finished - started) * 1000.0)
            return self._append_event(
                stage=normalized_stage,
                status=normalized_status,
                latency_ms=latency_ms,
                source_message_reference=source_message_reference,
                response_message_reference=response_message_reference,
                intent=intent,
                intent_confidence=intent_confidence,
                reason_codes=reason_codes,
                safe_references=safe_references,
                details=details,
            )

    def finalize(
        self,
        status: TraceStatus | str = TraceStatus.COMPLETED,
    ) -> None:
        """Close the trace and freeze its measured total duration."""

        if not self.enabled:
            return
        normalized_status = _coerce_status(status)
        if normalized_status in {TraceStatus.PENDING, TraceStatus.STARTED}:
            raise CognitiveTraceError("final trace status must be completed, failed, or skipped")
        with self._lock:
            self._ensure_open()
            ended_monotonic = float(self._monotonic_clock())
            if not math.isfinite(ended_monotonic):
                raise CognitiveTraceError("monotonic clock must return a finite number")
            self._ended_at = _utc_timestamp(self._clock)
            self._duration_ms = max(
                0.0, (ended_monotonic - self._created_monotonic) * 1000.0
            )
            self._final_status = normalized_status
            self._stage_starts.clear()

    @staticmethod
    def _safe_event_dict(event: CognitiveTraceEvent) -> dict[str, Any]:
        original_count = event.details.get("privacy_redaction_count", 0)
        if isinstance(original_count, bool) or not isinstance(original_count, int):
            original_count = 0
        details_without_count = dict(event.details)
        details_without_count.pop("privacy_redaction_count", None)
        privacy = filter_trace_data(details_without_count)
        details = dict(privacy.data)
        total_redactions = max(0, original_count) + privacy.redaction_count
        if total_redactions:
            details["privacy_redaction_count"] = total_redactions

        safe_event = CognitiveTraceEvent(
            trace_id=event.trace_id,
            stage=event.stage,
            status=event.status,
            occurred_at=event.occurred_at,
            latency_ms=event.latency_ms,
            user_reference=_safe_reference(event.user_reference),
            conversation_reference=_safe_reference(event.conversation_reference),
            source_message_reference=_safe_reference(event.source_message_reference),
            response_message_reference=_safe_reference(event.response_message_reference),
            intent=_safe_short_label(event.intent),
            intent_confidence=event.intent_confidence,
            reason_codes=_safe_string_tuple(event.reason_codes),
            safe_references=_safe_string_tuple(event.safe_references),
            details=details,
        )
        return safe_event.to_dict()

    def to_dict(self) -> dict[str, Any]:
        """Serialize the trace to a fresh privacy-filtered dictionary."""

        with self._lock:
            return {
                "contract_type": "cognitive_trace",
                "schema_version": COGNITIVE_TRACE_SCHEMA_VERSION,
                "trace_id": self.trace_id,
                "enabled": self.enabled,
                "created_at": self.created_at,
                "ended_at": self._ended_at,
                "duration_ms": self._duration_ms,
                "final_status": (
                    self._final_status.value if self._final_status is not None else None
                ),
                "event_count": len(self._events),
                "events": [self._safe_event_dict(event) for event in self._events],
            }

    def to_json(self, *, indent: int | None = None) -> str:
        """Serialize the trace as deterministic, standards-compliant JSON."""

        return json.dumps(
            self.to_dict(),
            ensure_ascii=False,
            allow_nan=False,
            indent=indent,
            sort_keys=True,
        )


__all__ = [
    "COGNITIVE_TRACE_ENABLED_BY_DEFAULT",
    "COGNITIVE_TRACE_SCHEMA_VERSION",
    "TRACE_REDACTION_MARKER",
    "CognitiveTraceError",
    "CognitiveTraceStateError",
    "PrivacyFilterResult",
    "CognitiveTrace",
    "generate_correlation_id",
    "redact_sensitive_text",
    "filter_trace_data",
]
