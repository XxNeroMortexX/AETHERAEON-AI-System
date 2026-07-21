"""Aetheraeon architecture: Phase 4 Shadow Reasoning Engine.

Reasoning Engine responsibility:
    Convert explicitly supplied, observable approved context into the Phase 0A
    ``ReasoningResult`` contract without generating language, hidden reasoning,
    actions, or decisions.

Architecture layer:
    Cognitive Intelligence Layer reasoning-coordination boundary, after approved
    retrieval and before future generation and response validation.

Responsibilities:
    - represent observable analytical, creative/contextual, planning, evidence,
      personality, and response-requirement signals;
    - preserve correlation, confidence, provenance, warnings, and bounded safe
      summaries in a non-authoritative shadow result;
    - reject private reasoning, prompt, and secret-shaped input.

Boundaries:
    - shadow-only and not imported by the live runtime during Phase 4;
    - does not replace core_cognition.py or ai_orchestrator.py;
    - does not make security or memory decisions, authorize tools, execute
      actions, generate responses, persist state, or call external services.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import math
import re
import time
from typing import Any, Callable, Mapping

from core.cognitive_contracts import (
    COGNITIVE_CONTRACT_SCHEMA_VERSION,
    ReasoningResult,
)


SHADOW_REASONING_MODE = "shadow"
SHADOW_REASONING_AUTHORITATIVE = False
SHADOW_REASONING_POLICY_VERSION = "shadow-reasoning-adapter-1.0"
_MAX_OBSERVABLE_TEXT_LENGTH = 512
_MAX_OBSERVABLE_PAYLOAD_BYTES = 8192
_PRIVATE_REASONING_PATTERN = re.compile(
    r"chain(?:-|\s+)of(?:-|\s+)thought|hidden\s+scratch|scratch\s*(?:work|pad)|"
    r"system\s+prompt",
    re.IGNORECASE,
)
_SECRET_ASSIGNMENT_PATTERN = re.compile(
    r"(?:api[_ -]?key|password|credential|secret|token)\s*(?:=|:)\s*\S+",
    re.IGNORECASE,
)


class ShadowReasoningError(ValueError):
    """Raised when a shadow reasoning input is invalid or unsafe to observe."""


def _nonempty_string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ShadowReasoningError(f"{name} must be a non-empty string")
    normalized = value.strip()
    if len(normalized) > _MAX_OBSERVABLE_TEXT_LENGTH:
        raise ShadowReasoningError(f"{name} exceeds the observable text limit")
    if _PRIVATE_REASONING_PATTERN.search(normalized) or _SECRET_ASSIGNMENT_PATTERN.search(normalized):
        raise ShadowReasoningError(f"{name} contains private reasoning or secret-shaped data")
    return normalized


def _optional_string(value: Any, name: str) -> str | None:
    return None if value is None else _nonempty_string(value, name)


def _string_tuple(value: Any, name: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, (str, bytes)) or not isinstance(value, (list, tuple)):
        raise ShadowReasoningError(f"{name} must be a sequence of strings")
    return tuple(_nonempty_string(item, name) for item in value)


def _confidence(value: Any) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ShadowReasoningError("confidence must be a number between 0 and 1")
    normalized = float(value)
    if not math.isfinite(normalized) or not 0.0 <= normalized <= 1.0:
        raise ShadowReasoningError("confidence must be a finite number between 0 and 1")
    return normalized


def _optional_confidence(value: Any) -> float | None:
    """Preserve unavailable confidence instead of fabricating a percentage."""

    return None if value is None else _confidence(value)


def _observable_mapping(value: Any, name: str) -> Mapping[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise ShadowReasoningError(f"{name} must be a mapping")

    def validate(item: Any, path: str) -> Any:
        if item is None or isinstance(item, (bool, int)):
            return item
        if isinstance(item, float):
            if not math.isfinite(item):
                raise ShadowReasoningError(f"{path} must not contain non-finite numbers")
            return item
        if isinstance(item, str):
            return _nonempty_string(item, path)
        if isinstance(item, Mapping):
            return {str(_nonempty_string(key, f"{path} key")): validate(val, f"{path}.{key}") for key, val in item.items()}
        if isinstance(item, (list, tuple)):
            return [validate(entry, f"{path} item") for entry in item]
        raise ShadowReasoningError(f"{path} contains a non-observable value")

    normalized = validate(value, name)
    try:
        encoded = json.dumps(normalized, sort_keys=True, allow_nan=False).encode("utf-8")
    except (TypeError, ValueError) as error:
        raise ShadowReasoningError(f"{name} must be JSON-serializable") from error
    if len(encoded) > _MAX_OBSERVABLE_PAYLOAD_BYTES:
        raise ShadowReasoningError(f"{name} exceeds the observable payload limit")
    return normalized


@dataclass(frozen=True, slots=True)
class ReasoningRequest:
    """Explicit approved context accepted by the non-authoritative adapter."""

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
    confidence: float | None = None
    provenance: Mapping[str, Any] = field(default_factory=dict)
    warnings: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "trace_id", _nonempty_string(self.trace_id, "trace_id"))
        object.__setattr__(self, "response_objective", _nonempty_string(self.response_objective, "response_objective"))
        for name in (
            "approved_facts_and_constraints",
            "selected_evidence_references",
            "required_tool_results",
            "output_format_requirements",
            "validator_checklist",
            "warnings",
        ):
            object.__setattr__(self, name, _string_tuple(getattr(self, name), name))
        for name in (
            "analytical_signal_summary",
            "creative_contextual_signal_summary",
            "applied_personality_modifiers",
            "provenance",
        ):
            object.__setattr__(self, name, _observable_mapping(getattr(self, name), name))
        object.__setattr__(self, "planning_summary", _optional_string(self.planning_summary, "planning_summary"))
        object.__setattr__(self, "confidence", _optional_confidence(self.confidence))


@dataclass(frozen=True, slots=True)
class ShadowReasoning:
    """Read-only envelope around a standardized observable reasoning result."""

    reasoning_result: ReasoningResult
    status: str
    confidence: float | None
    provenance: Mapping[str, Any]
    warnings: tuple[str, ...]
    latency_ms: float
    policy_version: str = SHADOW_REASONING_POLICY_VERSION

    MODE = SHADOW_REASONING_MODE
    AUTHORITATIVE = SHADOW_REASONING_AUTHORITATIVE

    def __post_init__(self) -> None:
        if not isinstance(self.reasoning_result, ReasoningResult):
            raise ShadowReasoningError("reasoning_result must use the Phase 0A ReasoningResult contract")
        object.__setattr__(self, "status", _nonempty_string(self.status, "status"))
        object.__setattr__(self, "confidence", _optional_confidence(self.confidence))
        object.__setattr__(self, "provenance", _observable_mapping(self.provenance, "provenance"))
        object.__setattr__(self, "warnings", _string_tuple(self.warnings, "warnings"))
        if isinstance(self.latency_ms, bool) or not isinstance(self.latency_ms, (int, float)) or self.latency_ms < 0:
            raise ShadowReasoningError("latency_ms must be a non-negative number")
        if self.policy_version != SHADOW_REASONING_POLICY_VERSION:
            raise ShadowReasoningError("unsupported reasoning policy_version")

    @property
    def trace_id(self) -> str:
        return self.reasoning_result.trace_id

    def to_metadata_dict(self) -> dict[str, Any]:
        """Serialize observable result metadata; no hidden reasoning is retained."""

        return {
            "mode": self.MODE,
            "authoritative": self.AUTHORITATIVE,
            "status": self.status,
            "confidence": self.confidence,
            "reasoning_result": self.reasoning_result.to_dict(),
            "provenance": dict(self.provenance),
            "warnings": list(self.warnings),
            "latency_ms": self.latency_ms,
            "policy_version": self.policy_version,
            "schema_version": COGNITIVE_CONTRACT_SCHEMA_VERSION,
        }


class ShadowReasoningEngine:
    """Deterministic contract adapter; it does not perform hidden reasoning."""

    def analyze(
        self,
        request: ReasoningRequest,
        *,
        monotonic_clock: Callable[[], float] = time.monotonic,
    ) -> ShadowReasoning:
        if not isinstance(request, ReasoningRequest):
            raise ShadowReasoningError("request must be a ReasoningRequest")
        if not callable(monotonic_clock):
            raise ShadowReasoningError("monotonic_clock must be callable")
        started = monotonic_clock()
        result = ReasoningResult(
            trace_id=request.trace_id,
            response_objective=request.response_objective,
            approved_facts_and_constraints=request.approved_facts_and_constraints,
            selected_evidence_references=request.selected_evidence_references,
            analytical_signal_summary=request.analytical_signal_summary,
            creative_contextual_signal_summary=request.creative_contextual_signal_summary,
            planning_summary=request.planning_summary,
            applied_personality_modifiers=request.applied_personality_modifiers,
            required_tool_results=request.required_tool_results,
            output_format_requirements=request.output_format_requirements,
            validator_checklist=request.validator_checklist,
        )
        latency_ms = round(max(0.0, (monotonic_clock() - started) * 1000), 6)
        return ShadowReasoning(
            reasoning_result=result,
            status="observed",
            confidence=request.confidence,
            provenance={
                "adapter": "explicit_observable_input",
                "engine": "shadow_reasoning",
                **request.provenance,
            },
            warnings=request.warnings,
            latency_ms=latency_ms,
        )


def analyze_shadow_reasoning(
    request: ReasoningRequest,
    *,
    monotonic_clock: Callable[[], float] = time.monotonic,
) -> ShadowReasoning:
    """Produce a Phase 4 non-authoritative reasoning observation."""

    return ShadowReasoningEngine().analyze(request, monotonic_clock=monotonic_clock)
