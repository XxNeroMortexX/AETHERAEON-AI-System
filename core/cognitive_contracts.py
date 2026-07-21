"""Versioned, runtime-neutral contracts for Aetheraeon's cognitive layer.

This module contains data definitions only.  It deliberately has no imports from
the live request, memory, tool, persistence, prompt, or UI paths.  Phase 0A does
not wire these contracts into application behavior.

Confidence values use the inclusive range 0.0 through 1.0.  ``None`` means that
no measured score is available; callers must not manufacture a replacement.
"""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from datetime import datetime
from enum import Enum
import json
import math
from typing import Any, ClassVar, Mapping, Self


COGNITIVE_CONTRACT_SCHEMA_VERSION = "1.0"
SUPPORTED_COGNITIVE_CONTRACT_SCHEMA_VERSIONS = frozenset(
    {COGNITIVE_CONTRACT_SCHEMA_VERSION}
)


class ContractValidationError(ValueError):
    """Raised when a cognitive contract is structurally invalid."""

    def __init__(self, errors: str | tuple[str, ...] | list[str]):
        if isinstance(errors, str):
            normalized = (errors,)
        else:
            normalized = tuple(str(error) for error in errors)
        self.errors = normalized
        super().__init__("; ".join(normalized))


class TemporalScope(str, Enum):
    PRESENT = "present"
    HISTORICAL = "historical"
    FUTURE = "future"
    PERSISTENT = "persistent"
    TEMPORARY = "temporary"
    UNKNOWN = "unknown"


class ContextScope(str, Enum):
    CONVERSATION = "conversation"
    PROJECT = "project"
    USER = "user"
    GLOBAL = "global"
    UNKNOWN = "unknown"


class ProvenanceSource(str, Enum):
    RULE = "rule"
    MODEL = "model"
    HYBRID = "hybrid"
    DIRECT_COMMAND = "direct_command"


class ValidationOutcome(str, Enum):
    PASS = "pass"
    RETRY = "retry"
    BLOCK = "block"
    FALLBACK = "fallback"


class ValidationCheckStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    NOT_APPLICABLE = "not_applicable"
    ERROR = "error"


class TraceStage(str, Enum):
    TRACE_CREATED = "trace_created"
    INPUT_ACCEPTED = "input_accepted"
    NLU_COMPLETED = "nlu_completed"
    COGNITIVE_DECISION_COMPLETED = "cognitive_decision_completed"
    RETRIEVAL_COMPLETED = "retrieval_completed"
    REASONING_COMPLETED = "reasoning_completed"
    GENERATION_COMPLETED = "generation_completed"
    VALIDATION_COMPLETED = "validation_completed"
    RESPONSE_PERSISTED = "response_persisted"


class TraceStatus(str, Enum):
    PENDING = "pending"
    STARTED = "started"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


_PROHIBITED_OBSERVABILITY_KEYS = frozenset(
    {
        "chain_of_thought",
        "private_chain_of_thought",
        "scratch_work",
        "hidden_scratch_work",
        "hidden_prompt",
        "private_system_prompt",
        "system_prompt",
        "password",
        "access_token",
        "refresh_token",
        "api_token",
        "api_key",
        "secret",
        "session_id",
        "session_identifier",
        "raw_embedding",
        "raw_embeddings",
        "embedding_vector",
        "embedding_vectors",
    }
)


def _raise_if_errors(errors: list[str]) -> None:
    if errors:
        raise ContractValidationError(errors)


def _require_nonempty_string(value: Any, name: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{name} must be a non-empty string")


def _require_optional_string(value: Any, name: str, errors: list[str]) -> None:
    if value is not None and (not isinstance(value, str) or not value.strip()):
        errors.append(f"{name} must be None or a non-empty string")


def _require_confidence(value: Any, name: str, errors: list[str]) -> None:
    if value is None:
        return
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        errors.append(f"{name} must be None or a number from 0.0 through 1.0")
        return
    if not math.isfinite(float(value)) or not 0.0 <= float(value) <= 1.0:
        errors.append(f"{name} must be None or a number from 0.0 through 1.0")


def _require_nonnegative_number(value: Any, name: str, errors: list[str]) -> None:
    if value is None:
        return
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        errors.append(f"{name} must be None or a non-negative number")
        return
    if not math.isfinite(float(value)) or value < 0:
        errors.append(f"{name} must be None or a non-negative number")


def _require_nonnegative_int(value: Any, name: str, errors: list[str]) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        errors.append(f"{name} must be a non-negative integer")


def _string_tuple(value: Any, name: str) -> tuple[str, ...]:
    if isinstance(value, str) or not isinstance(value, (list, tuple)):
        raise ContractValidationError(f"{name} must be a sequence of strings")
    normalized = tuple(value)
    errors: list[str] = []
    for index, item in enumerate(normalized):
        _require_nonempty_string(item, f"{name}[{index}]", errors)
    _raise_if_errors(errors)
    return normalized


def _mapping(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ContractValidationError(f"{name} must be a mapping")
    normalized = dict(value)
    errors: list[str] = []
    _validate_json_value(normalized, name, errors)
    _raise_if_errors(errors)
    return normalized


def _validate_json_value(value: Any, path: str, errors: list[str]) -> None:
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            errors.append(f"{path} contains a non-finite number")
        return
    if isinstance(value, Enum):
        return
    if isinstance(value, Mapping):
        for key, item in value.items():
            if not isinstance(key, str):
                errors.append(f"{path} contains a non-string mapping key")
                continue
            _validate_json_value(item, f"{path}.{key}", errors)
        return
    if isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            _validate_json_value(item, f"{path}[{index}]", errors)
        return
    errors.append(f"{path} contains a non-JSON value of type {type(value).__name__}")


def _validate_observable_value(value: Any, path: str, errors: list[str]) -> None:
    _validate_json_value(value, path, errors)
    if isinstance(value, Mapping):
        for key, item in value.items():
            if isinstance(key, str) and key.strip().lower() in _PROHIBITED_OBSERVABILITY_KEYS:
                errors.append(f"{path}.{key} is prohibited observability content")
            _validate_observable_value(item, f"{path}.{key}", errors)
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            _validate_observable_value(item, f"{path}[{index}]", errors)


def _enum_value(value: Any, enum_type: type[Enum], name: str) -> Enum:
    if isinstance(value, enum_type):
        return value
    try:
        return enum_type(value)
    except (TypeError, ValueError) as exc:
        allowed = ", ".join(repr(member.value) for member in enum_type)
        raise ContractValidationError(f"{name} must be one of: {allowed}") from exc


def _to_json_value(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, (Entity, Fact, ValidationCheck)):
        return value.to_dict()
    if isinstance(value, Mapping):
        return {str(key): _to_json_value(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_to_json_value(item) for item in value]
    return value


def _contract_payload(
    payload: Mapping[str, Any],
    contract_type: str,
    field_names: set[str],
) -> dict[str, Any]:
    if not isinstance(payload, Mapping):
        raise ContractValidationError("contract payload must be a mapping")
    normalized = dict(payload)
    errors: list[str] = []
    if normalized.get("contract_type") != contract_type:
        errors.append(f"contract_type must be {contract_type!r}")
    version = normalized.get("schema_version")
    if version not in SUPPORTED_COGNITIVE_CONTRACT_SCHEMA_VERSIONS:
        errors.append(
            "schema_version must be one of: "
            + ", ".join(sorted(SUPPORTED_COGNITIVE_CONTRACT_SCHEMA_VERSIONS))
        )
    unknown = set(normalized) - field_names - {"contract_type"}
    if unknown:
        errors.append("unknown contract fields: " + ", ".join(sorted(unknown)))
    missing = field_names - set(normalized)
    if missing:
        errors.append("missing contract fields: " + ", ".join(sorted(missing)))
    _raise_if_errors(errors)
    normalized.pop("contract_type", None)
    return normalized


class CognitiveContract:
    """Serialization and validation behavior shared by all top-level contracts."""

    CONTRACT_TYPE: ClassVar[str]

    def validate(self) -> None:
        raise NotImplementedError

    def validation_errors(self) -> tuple[str, ...]:
        try:
            self.validate()
        except ContractValidationError as exc:
            return exc.errors
        return ()

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        result = {
            field.name: _to_json_value(getattr(self, field.name))
            for field in fields(self)
        }
        return {"contract_type": self.CONTRACT_TYPE, **result}

    def to_json(self, *, indent: int | None = None) -> str:
        return json.dumps(
            self.to_dict(),
            ensure_ascii=False,
            allow_nan=False,
            indent=indent,
            sort_keys=True,
        )

    @classmethod
    def from_json(cls, value: str) -> Self:
        try:
            payload = json.loads(value)
        except (TypeError, json.JSONDecodeError) as exc:
            raise ContractValidationError("contract JSON is invalid") from exc
        return cls.from_dict(payload)


@dataclass(frozen=True, slots=True)
class Entity:
    normalized_value: str
    original_text: str
    entity_type: str
    confidence: float | None = None
    source_location: str | None = None
    fact_references: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "fact_references", _string_tuple(self.fact_references, "fact_references")
        )
        errors: list[str] = []
        _require_nonempty_string(self.normalized_value, "normalized_value", errors)
        _require_nonempty_string(self.original_text, "original_text", errors)
        _require_nonempty_string(self.entity_type, "entity_type", errors)
        _require_confidence(self.confidence, "confidence", errors)
        _require_optional_string(self.source_location, "source_location", errors)
        _raise_if_errors(errors)

    def to_dict(self) -> dict[str, Any]:
        return {field.name: _to_json_value(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> Entity:
        if not isinstance(payload, Mapping):
            raise ContractValidationError("entity must be a mapping")
        allowed = {field.name for field in fields(cls)}
        unknown = set(payload) - allowed
        if unknown:
            raise ContractValidationError("unknown entity fields: " + ", ".join(sorted(unknown)))
        try:
            return cls(**dict(payload))
        except TypeError as exc:
            raise ContractValidationError(f"invalid entity fields: {exc}") from exc


@dataclass(frozen=True, slots=True)
class Fact:
    subject: str
    predicate: str
    object_or_value: Any
    normalized_text: str
    fact_type: str
    confidence: float | None = None
    stability_estimate: float | None = None
    temporal_scope: TemporalScope = TemporalScope.UNKNOWN
    context_scope: ContextScope = ContextScope.UNKNOWN
    sensitivity_classification: str = "unknown"
    quoted: bool = False
    hypothetical: bool = False
    negated: bool = False
    uncertain: bool = False
    source_message_reference: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "temporal_scope",
            _enum_value(self.temporal_scope, TemporalScope, "temporal_scope"),
        )
        object.__setattr__(
            self,
            "context_scope",
            _enum_value(self.context_scope, ContextScope, "context_scope"),
        )
        errors: list[str] = []
        _require_nonempty_string(self.subject, "subject", errors)
        _require_nonempty_string(self.predicate, "predicate", errors)
        _require_nonempty_string(self.normalized_text, "normalized_text", errors)
        _require_nonempty_string(self.fact_type, "fact_type", errors)
        _require_confidence(self.confidence, "confidence", errors)
        _require_confidence(self.stability_estimate, "stability_estimate", errors)
        _require_nonempty_string(
            self.sensitivity_classification, "sensitivity_classification", errors
        )
        _require_optional_string(
            self.source_message_reference, "source_message_reference", errors
        )
        _validate_json_value(self.object_or_value, "object_or_value", errors)
        for name in ("quoted", "hypothetical", "negated", "uncertain"):
            if not isinstance(getattr(self, name), bool):
                errors.append(f"{name} must be a boolean")
        _raise_if_errors(errors)

    def to_dict(self) -> dict[str, Any]:
        return {field.name: _to_json_value(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> Fact:
        if not isinstance(payload, Mapping):
            raise ContractValidationError("fact must be a mapping")
        allowed = {field.name for field in fields(cls)}
        unknown = set(payload) - allowed
        if unknown:
            raise ContractValidationError("unknown fact fields: " + ", ".join(sorted(unknown)))
        try:
            return cls(**dict(payload))
        except TypeError as exc:
            raise ContractValidationError(f"invalid fact fields: {exc}") from exc


@dataclass(frozen=True, slots=True)
class ValidationCheck:
    name: str
    status: ValidationCheckStatus
    reason_code: str | None = None
    summary: str | None = None
    evidence_references: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "status", _enum_value(self.status, ValidationCheckStatus, "status")
        )
        object.__setattr__(
            self,
            "evidence_references",
            _string_tuple(self.evidence_references, "evidence_references"),
        )
        errors: list[str] = []
        _require_nonempty_string(self.name, "name", errors)
        _require_optional_string(self.reason_code, "reason_code", errors)
        _require_optional_string(self.summary, "summary", errors)
        _raise_if_errors(errors)

    def to_dict(self) -> dict[str, Any]:
        return {field.name: _to_json_value(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> ValidationCheck:
        if not isinstance(payload, Mapping):
            raise ContractValidationError("validation check must be a mapping")
        allowed = {field.name for field in fields(cls)}
        unknown = set(payload) - allowed
        if unknown:
            raise ContractValidationError(
                "unknown validation check fields: " + ", ".join(sorted(unknown))
            )
        try:
            return cls(**dict(payload))
        except TypeError as exc:
            raise ContractValidationError(f"invalid validation check fields: {exc}") from exc


def _entities(value: Any, name: str) -> tuple[Entity, ...]:
    if isinstance(value, (str, bytes)) or not isinstance(value, (list, tuple)):
        raise ContractValidationError(f"{name} must be a sequence of entities")
    return tuple(item if isinstance(item, Entity) else Entity.from_dict(item) for item in value)


def _facts(value: Any, name: str) -> tuple[Fact, ...]:
    if isinstance(value, (str, bytes)) or not isinstance(value, (list, tuple)):
        raise ContractValidationError(f"{name} must be a sequence of facts")
    return tuple(item if isinstance(item, Fact) else Fact.from_dict(item) for item in value)


def _checks(value: Any) -> tuple[ValidationCheck, ...]:
    if isinstance(value, (str, bytes)) or not isinstance(value, (list, tuple)):
        raise ContractValidationError("checks must be a sequence of validation checks")
    return tuple(
        item if isinstance(item, ValidationCheck) else ValidationCheck.from_dict(item)
        for item in value
    )


@dataclass(frozen=True, slots=True)
class NLUResult(CognitiveContract):
    CONTRACT_TYPE: ClassVar[str] = "nlu_result"

    trace_id: str
    primary_intent: str
    secondary_intents: tuple[str, ...] = ()
    intent_confidence: float | None = None
    entities: tuple[Entity, ...] = ()
    facts: tuple[Fact, ...] = ()
    emotion: Mapping[str, Any] = field(default_factory=dict)
    temporal_scope: TemporalScope = TemporalScope.UNKNOWN
    context_scope: ContextScope = ContextScope.UNKNOWN
    explicit_memory_instruction: bool = False
    memory_signals: tuple[str, ...] = ()
    tool_signals: tuple[str, ...] = ()
    provenance: Mapping[str, str] = field(default_factory=dict)
    warnings: tuple[str, ...] = ()
    schema_version: str = COGNITIVE_CONTRACT_SCHEMA_VERSION

    def __post_init__(self) -> None:
        object.__setattr__(self, "secondary_intents", _string_tuple(self.secondary_intents, "secondary_intents"))
        object.__setattr__(self, "entities", _entities(self.entities, "entities"))
        object.__setattr__(self, "facts", _facts(self.facts, "facts"))
        object.__setattr__(self, "emotion", _mapping(self.emotion or {}, "emotion"))
        object.__setattr__(self, "temporal_scope", _enum_value(self.temporal_scope, TemporalScope, "temporal_scope"))
        object.__setattr__(self, "context_scope", _enum_value(self.context_scope, ContextScope, "context_scope"))
        object.__setattr__(self, "memory_signals", _string_tuple(self.memory_signals, "memory_signals"))
        object.__setattr__(self, "tool_signals", _string_tuple(self.tool_signals, "tool_signals"))
        object.__setattr__(self, "provenance", dict(self.provenance or {}))
        object.__setattr__(self, "warnings", _string_tuple(self.warnings, "warnings"))
        self.validate()

    def validate(self) -> None:
        errors: list[str] = []
        _require_nonempty_string(self.trace_id, "trace_id", errors)
        _require_nonempty_string(self.primary_intent, "primary_intent", errors)
        _require_confidence(self.intent_confidence, "intent_confidence", errors)
        if not isinstance(self.explicit_memory_instruction, bool):
            errors.append("explicit_memory_instruction must be a boolean")
        if not isinstance(self.provenance, Mapping):
            errors.append("provenance must be a mapping")
        else:
            for key, source in self.provenance.items():
                _require_nonempty_string(key, "provenance key", errors)
                try:
                    _enum_value(source, ProvenanceSource, f"provenance[{key!r}]")
                except ContractValidationError as exc:
                    errors.extend(exc.errors)
        _validate_json_value(self.emotion, "emotion", errors)
        if self.schema_version not in SUPPORTED_COGNITIVE_CONTRACT_SCHEMA_VERSIONS:
            errors.append("unsupported schema_version")
        _raise_if_errors(errors)

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> NLUResult:
        data = _contract_payload(payload, cls.CONTRACT_TYPE, {field.name for field in fields(cls)})
        try:
            return cls(**data)
        except TypeError as exc:
            raise ContractValidationError(f"invalid NLU result fields: {exc}") from exc


@dataclass(frozen=True, slots=True)
class CognitiveDecision(CognitiveContract):
    CONTRACT_TYPE: ClassVar[str] = "cognitive_decision"

    trace_id: str
    request_objective: str
    approved_intent: str
    relevant_entities: tuple[Entity, ...] = ()
    relevant_facts: tuple[Fact, ...] = ()
    context_treatment: str = "conversation"
    memory_decision: Mapping[str, Any] = field(default_factory=dict)
    retrieval_plan: Mapping[str, Any] = field(default_factory=dict)
    reasoning_strategy: tuple[str, ...] = ()
    personality_applicable: bool = True
    planning_required: bool = False
    tool_or_web_requirements: tuple[str, ...] = ()
    validation_requirements: tuple[str, ...] = ()
    decision_confidence: float | None = None
    reason_codes: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    schema_version: str = COGNITIVE_CONTRACT_SCHEMA_VERSION

    def __post_init__(self) -> None:
        object.__setattr__(self, "relevant_entities", _entities(self.relevant_entities, "relevant_entities"))
        object.__setattr__(self, "relevant_facts", _facts(self.relevant_facts, "relevant_facts"))
        object.__setattr__(self, "memory_decision", _mapping(self.memory_decision or {}, "memory_decision"))
        object.__setattr__(self, "retrieval_plan", _mapping(self.retrieval_plan or {}, "retrieval_plan"))
        object.__setattr__(self, "reasoning_strategy", _string_tuple(self.reasoning_strategy, "reasoning_strategy"))
        object.__setattr__(self, "tool_or_web_requirements", _string_tuple(self.tool_or_web_requirements, "tool_or_web_requirements"))
        object.__setattr__(self, "validation_requirements", _string_tuple(self.validation_requirements, "validation_requirements"))
        object.__setattr__(self, "reason_codes", _string_tuple(self.reason_codes, "reason_codes"))
        object.__setattr__(self, "warnings", _string_tuple(self.warnings, "warnings"))
        self.validate()

    def validate(self) -> None:
        errors: list[str] = []
        _require_nonempty_string(self.trace_id, "trace_id", errors)
        _require_nonempty_string(self.request_objective, "request_objective", errors)
        _require_nonempty_string(self.approved_intent, "approved_intent", errors)
        _require_nonempty_string(self.context_treatment, "context_treatment", errors)
        _require_confidence(self.decision_confidence, "decision_confidence", errors)
        for name in ("personality_applicable", "planning_required"):
            if not isinstance(getattr(self, name), bool):
                errors.append(f"{name} must be a boolean")
        _validate_json_value(self.memory_decision, "memory_decision", errors)
        _validate_json_value(self.retrieval_plan, "retrieval_plan", errors)
        if self.schema_version not in SUPPORTED_COGNITIVE_CONTRACT_SCHEMA_VERSIONS:
            errors.append("unsupported schema_version")
        _raise_if_errors(errors)

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> CognitiveDecision:
        data = _contract_payload(payload, cls.CONTRACT_TYPE, {field.name for field in fields(cls)})
        try:
            return cls(**data)
        except TypeError as exc:
            raise ContractValidationError(f"invalid cognitive decision fields: {exc}") from exc


@dataclass(frozen=True, slots=True)
class RetrievalResult(CognitiveContract):
    CONTRACT_TYPE: ClassVar[str] = "retrieval_result"

    trace_id: str
    source_name: str
    attempted: bool
    completed: bool
    failure_reason: str | None = None
    raw_result_count: int = 0
    eligible_result_count: int = 0
    selected_result_count: int = 0
    injected_result_count: int = 0
    safe_references: tuple[str, ...] = ()
    relevance_scores: Mapping[str, float] = field(default_factory=dict)
    latency_ms: float | None = None
    truncated: bool = False
    result_limit: int | None = None
    schema_version: str = COGNITIVE_CONTRACT_SCHEMA_VERSION

    def __post_init__(self) -> None:
        object.__setattr__(self, "safe_references", _string_tuple(self.safe_references, "safe_references"))
        object.__setattr__(self, "relevance_scores", dict(self.relevance_scores or {}))
        self.validate()

    @property
    def failed(self) -> bool:
        return self.attempted and not self.completed

    @property
    def found(self) -> bool:
        return self.raw_result_count > 0

    @property
    def not_used(self) -> bool:
        return not self.attempted or self.injected_result_count == 0

    def validate(self) -> None:
        errors: list[str] = []
        _require_nonempty_string(self.trace_id, "trace_id", errors)
        _require_nonempty_string(self.source_name, "source_name", errors)
        for name in ("attempted", "completed", "truncated"):
            if not isinstance(getattr(self, name), bool):
                errors.append(f"{name} must be a boolean")
        for name in (
            "raw_result_count",
            "eligible_result_count",
            "selected_result_count",
            "injected_result_count",
        ):
            _require_nonnegative_int(getattr(self, name), name, errors)
        _require_optional_string(self.failure_reason, "failure_reason", errors)
        _require_nonnegative_number(self.latency_ms, "latency_ms", errors)
        if self.result_limit is not None:
            _require_nonnegative_int(self.result_limit, "result_limit", errors)
        if self.completed and not self.attempted:
            errors.append("completed retrieval must have been attempted")
        if self.attempted and self.latency_ms is None:
            errors.append("attempted retrieval must report latency_ms")
        if self.attempted and not self.completed and not self.failure_reason:
            errors.append("failed retrieval must report failure_reason")
        if (not self.attempted or self.completed) and self.failure_reason is not None:
            errors.append("failure_reason is only valid for a failed retrieval")
        counts = (
            self.raw_result_count,
            self.eligible_result_count,
            self.selected_result_count,
            self.injected_result_count,
        )
        if all(isinstance(value, int) and not isinstance(value, bool) for value in counts):
            if not (
                self.injected_result_count
                <= self.selected_result_count
                <= self.eligible_result_count
                <= self.raw_result_count
            ):
                errors.append(
                    "retrieval counts must satisfy injected <= selected <= eligible <= raw"
                )
            if not self.completed and any(counts):
                errors.append("incomplete retrieval cannot report result counts")
        if self.raw_result_count and not self.safe_references:
            errors.append("found results must include identifiers or safe references")
        if not isinstance(self.relevance_scores, Mapping):
            errors.append("relevance_scores must be a mapping")
        else:
            for reference, score in self.relevance_scores.items():
                _require_nonempty_string(reference, "relevance score reference", errors)
                if reference not in self.safe_references:
                    errors.append(
                        f"relevance score reference {reference!r} is not in safe_references"
                    )
                if isinstance(score, bool) or not isinstance(score, (int, float)) or not math.isfinite(float(score)):
                    errors.append(f"relevance score for {reference!r} must be a finite number")
        if self.schema_version not in SUPPORTED_COGNITIVE_CONTRACT_SCHEMA_VERSIONS:
            errors.append("unsupported schema_version")
        _raise_if_errors(errors)

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> RetrievalResult:
        data = _contract_payload(payload, cls.CONTRACT_TYPE, {field.name for field in fields(cls)})
        try:
            return cls(**data)
        except TypeError as exc:
            raise ContractValidationError(f"invalid retrieval result fields: {exc}") from exc


@dataclass(frozen=True, slots=True)
class ReasoningResult(CognitiveContract):
    CONTRACT_TYPE: ClassVar[str] = "reasoning_result"

    trace_id: str
    response_objective: str
    approved_facts_and_constraints: tuple[str, ...] = ()
    selected_evidence_references: tuple[str, ...] = ()
    analytical_signal_summary: Mapping[str, Any] = field(default_factory=dict)
    creative_contextual_signal_summary: Mapping[str, Any] = field(default_factory=dict)
    planning_summary: str | None = None
    applied_personality_modifiers: Mapping[str, Any] = field(default_factory=dict)
    required_tool_results: tuple[str, ...] = ()
    output_format_requirements: tuple[str, ...] = ()
    validator_checklist: tuple[str, ...] = ()
    schema_version: str = COGNITIVE_CONTRACT_SCHEMA_VERSION

    def __post_init__(self) -> None:
        for name in (
            "approved_facts_and_constraints",
            "selected_evidence_references",
            "required_tool_results",
            "output_format_requirements",
            "validator_checklist",
        ):
            object.__setattr__(self, name, _string_tuple(getattr(self, name), name))
        for name in (
            "analytical_signal_summary",
            "creative_contextual_signal_summary",
            "applied_personality_modifiers",
        ):
            object.__setattr__(self, name, _mapping(getattr(self, name) or {}, name))
        self.validate()

    def validate(self) -> None:
        errors: list[str] = []
        _require_nonempty_string(self.trace_id, "trace_id", errors)
        _require_nonempty_string(self.response_objective, "response_objective", errors)
        _require_optional_string(self.planning_summary, "planning_summary", errors)
        for name in (
            "analytical_signal_summary",
            "creative_contextual_signal_summary",
            "applied_personality_modifiers",
        ):
            _validate_observable_value(getattr(self, name), name, errors)
        if self.schema_version not in SUPPORTED_COGNITIVE_CONTRACT_SCHEMA_VERSIONS:
            errors.append("unsupported schema_version")
        _raise_if_errors(errors)

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> ReasoningResult:
        data = _contract_payload(payload, cls.CONTRACT_TYPE, {field.name for field in fields(cls)})
        try:
            return cls(**data)
        except TypeError as exc:
            raise ContractValidationError(f"invalid reasoning result fields: {exc}") from exc


@dataclass(frozen=True, slots=True)
class PlanningResult(CognitiveContract):
    CONTRACT_TYPE: ClassVar[str] = "planning_result"

    trace_id: str
    objective: str
    expected_deliverable: str
    required_information: tuple[str, ...] = ()
    retrieval_sources: tuple[str, ...] = ()
    tool_requirements: tuple[str, ...] = ()
    ordered_high_level_stages: tuple[str, ...] = ()
    constraints: tuple[str, ...] = ()
    stopping_conditions: tuple[str, ...] = ()
    validation_requirements: tuple[str, ...] = ()
    user_clarification_required: bool = False
    clarification_questions: tuple[str, ...] = ()
    schema_version: str = COGNITIVE_CONTRACT_SCHEMA_VERSION

    def __post_init__(self) -> None:
        for name in (
            "required_information",
            "retrieval_sources",
            "tool_requirements",
            "ordered_high_level_stages",
            "constraints",
            "stopping_conditions",
            "validation_requirements",
            "clarification_questions",
        ):
            object.__setattr__(self, name, _string_tuple(getattr(self, name), name))
        self.validate()

    def validate(self) -> None:
        errors: list[str] = []
        _require_nonempty_string(self.trace_id, "trace_id", errors)
        _require_nonempty_string(self.objective, "objective", errors)
        _require_nonempty_string(self.expected_deliverable, "expected_deliverable", errors)
        if not isinstance(self.user_clarification_required, bool):
            errors.append("user_clarification_required must be a boolean")
        if self.clarification_questions and not self.user_clarification_required:
            errors.append(
                "clarification_questions require user_clarification_required to be true"
            )
        if self.schema_version not in SUPPORTED_COGNITIVE_CONTRACT_SCHEMA_VERSIONS:
            errors.append("unsupported schema_version")
        _raise_if_errors(errors)

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> PlanningResult:
        data = _contract_payload(payload, cls.CONTRACT_TYPE, {field.name for field in fields(cls)})
        try:
            return cls(**data)
        except TypeError as exc:
            raise ContractValidationError(f"invalid planning result fields: {exc}") from exc


@dataclass(frozen=True, slots=True)
class ResponseValidationResult(CognitiveContract):
    CONTRACT_TYPE: ClassVar[str] = "response_validation_result"

    trace_id: str
    outcome: ValidationOutcome
    checks: tuple[ValidationCheck, ...] = ()
    report_only: bool = True
    retry_count: int = 0
    maximum_retries: int = 0
    reason_codes: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    deterministic_response_reference: str | None = None
    schema_version: str = COGNITIVE_CONTRACT_SCHEMA_VERSION

    def __post_init__(self) -> None:
        object.__setattr__(self, "outcome", _enum_value(self.outcome, ValidationOutcome, "outcome"))
        object.__setattr__(self, "checks", _checks(self.checks))
        object.__setattr__(self, "reason_codes", _string_tuple(self.reason_codes, "reason_codes"))
        object.__setattr__(self, "warnings", _string_tuple(self.warnings, "warnings"))
        self.validate()

    def validate(self) -> None:
        errors: list[str] = []
        _require_nonempty_string(self.trace_id, "trace_id", errors)
        if not isinstance(self.report_only, bool):
            errors.append("report_only must be a boolean")
        _require_nonnegative_int(self.retry_count, "retry_count", errors)
        _require_nonnegative_int(self.maximum_retries, "maximum_retries", errors)
        _require_optional_string(
            self.deterministic_response_reference,
            "deterministic_response_reference",
            errors,
        )
        if self.outcome is ValidationOutcome.RETRY:
            if self.maximum_retries <= 0:
                errors.append("retry outcome requires a positive maximum_retries")
            if self.retry_count >= self.maximum_retries:
                errors.append("retry outcome exceeds the bounded retry allowance")
        if self.outcome is ValidationOutcome.PASS and any(
            check.status in {ValidationCheckStatus.FAIL, ValidationCheckStatus.ERROR}
            for check in self.checks
        ):
            errors.append("pass outcome cannot contain failed or errored checks")
        if self.schema_version not in SUPPORTED_COGNITIVE_CONTRACT_SCHEMA_VERSIONS:
            errors.append("unsupported schema_version")
        _raise_if_errors(errors)

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> ResponseValidationResult:
        data = _contract_payload(payload, cls.CONTRACT_TYPE, {field.name for field in fields(cls)})
        try:
            return cls(**data)
        except TypeError as exc:
            raise ContractValidationError(f"invalid response validation fields: {exc}") from exc


@dataclass(frozen=True, slots=True)
class CognitiveTraceEvent(CognitiveContract):
    CONTRACT_TYPE: ClassVar[str] = "cognitive_trace_event"

    trace_id: str
    stage: TraceStage
    status: TraceStatus
    occurred_at: str
    latency_ms: float | None = None
    user_reference: str | None = None
    conversation_reference: str | None = None
    source_message_reference: str | None = None
    response_message_reference: str | None = None
    intent: str | None = None
    intent_confidence: float | None = None
    reason_codes: tuple[str, ...] = ()
    safe_references: tuple[str, ...] = ()
    details: Mapping[str, Any] = field(default_factory=dict)
    schema_version: str = COGNITIVE_CONTRACT_SCHEMA_VERSION

    def __post_init__(self) -> None:
        object.__setattr__(self, "stage", _enum_value(self.stage, TraceStage, "stage"))
        object.__setattr__(self, "status", _enum_value(self.status, TraceStatus, "status"))
        object.__setattr__(self, "reason_codes", _string_tuple(self.reason_codes, "reason_codes"))
        object.__setattr__(self, "safe_references", _string_tuple(self.safe_references, "safe_references"))
        object.__setattr__(self, "details", _mapping(self.details or {}, "details"))
        self.validate()

    def validate(self) -> None:
        errors: list[str] = []
        _require_nonempty_string(self.trace_id, "trace_id", errors)
        _require_nonempty_string(self.occurred_at, "occurred_at", errors)
        if isinstance(self.occurred_at, str) and self.occurred_at.strip():
            try:
                datetime.fromisoformat(self.occurred_at.replace("Z", "+00:00"))
            except ValueError:
                errors.append("occurred_at must be an ISO 8601 timestamp")
        _require_nonnegative_number(self.latency_ms, "latency_ms", errors)
        for name in (
            "user_reference",
            "conversation_reference",
            "source_message_reference",
            "response_message_reference",
            "intent",
        ):
            _require_optional_string(getattr(self, name), name, errors)
        _require_confidence(self.intent_confidence, "intent_confidence", errors)
        _validate_observable_value(self.details, "details", errors)
        if self.schema_version not in SUPPORTED_COGNITIVE_CONTRACT_SCHEMA_VERSIONS:
            errors.append("unsupported schema_version")
        _raise_if_errors(errors)

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> CognitiveTraceEvent:
        data = _contract_payload(payload, cls.CONTRACT_TYPE, {field.name for field in fields(cls)})
        try:
            return cls(**data)
        except TypeError as exc:
            raise ContractValidationError(f"invalid cognitive trace event fields: {exc}") from exc


COGNITIVE_CONTRACT_TYPES: Mapping[str, type[CognitiveContract]] = {
    contract.CONTRACT_TYPE: contract
    for contract in (
        NLUResult,
        CognitiveDecision,
        RetrievalResult,
        ReasoningResult,
        PlanningResult,
        ResponseValidationResult,
        CognitiveTraceEvent,
    )
}


def deserialize_contract(payload: Mapping[str, Any] | str) -> CognitiveContract:
    """Deserialize a payload by its explicit ``contract_type`` discriminator."""

    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise ContractValidationError("contract JSON is invalid") from exc
    if not isinstance(payload, Mapping):
        raise ContractValidationError("contract payload must be a mapping")
    contract_type = payload.get("contract_type")
    contract_class = COGNITIVE_CONTRACT_TYPES.get(contract_type)
    if contract_class is None:
        raise ContractValidationError(f"unsupported contract_type: {contract_type!r}")
    return contract_class.from_dict(payload)


def validate_contract(contract: CognitiveContract) -> tuple[str, ...]:
    """Return validation errors without raising; an empty tuple means valid."""

    if not isinstance(contract, CognitiveContract):
        return ("value is not a cognitive contract",)
    return contract.validation_errors()


def validate_contract_payload(payload: Mapping[str, Any] | str) -> tuple[str, ...]:
    """Validate serialized contract data without propagating validation errors."""

    try:
        deserialize_contract(payload)
    except (ContractValidationError, TypeError) as exc:
        if isinstance(exc, ContractValidationError):
            return exc.errors
        return (str(exc),)
    return ()


__all__ = [
    "COGNITIVE_CONTRACT_SCHEMA_VERSION",
    "SUPPORTED_COGNITIVE_CONTRACT_SCHEMA_VERSIONS",
    "COGNITIVE_CONTRACT_TYPES",
    "CognitiveContract",
    "ContractValidationError",
    "TemporalScope",
    "ContextScope",
    "ProvenanceSource",
    "ValidationOutcome",
    "ValidationCheckStatus",
    "TraceStage",
    "TraceStatus",
    "Entity",
    "Fact",
    "ValidationCheck",
    "NLUResult",
    "CognitiveDecision",
    "RetrievalResult",
    "ReasoningResult",
    "PlanningResult",
    "ResponseValidationResult",
    "CognitiveTraceEvent",
    "deserialize_contract",
    "validate_contract",
    "validate_contract_payload",
]
