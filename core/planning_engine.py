"""Aetheraeon architecture: Phase 4 Shadow Planning Engine.

Planning Engine responsibility:
    Convert explicitly supplied high-level planning information into the Phase
    0A ``PlanningResult`` contract without selecting or executing actions.

Architecture layer:
    Cognitive Intelligence Layer planning boundary, contributing observable
    strategy metadata to future reasoning and generation coordination.

Responsibilities:
    - represent proposed high-level stages, capabilities, dependencies,
      constraints, validation requirements, and clarification needs;
    - preserve correlation, confidence, provenance, warnings, and bounded safe
      operational summaries in a non-authoritative shadow result;
    - reject private reasoning, prompt, and secret-shaped input.

Boundaries:
    - shadow-only and not imported by the live runtime during Phase 4;
    - does not replace orchestration, automation execution, or existing tools;
    - does not execute plans, call tools, authorize actions, bypass security,
      modify memory, generate responses, or persist state.
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
    PlanningResult,
)


SHADOW_PLANNING_MODE = "shadow"
SHADOW_PLANNING_AUTHORITATIVE = False
SHADOW_PLANNING_POLICY_VERSION = "shadow-planning-adapter-1.0"
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


class ShadowPlanningError(ValueError):
    """Raised when a shadow planning input is invalid or unsafe to observe."""


def _nonempty_string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ShadowPlanningError(f"{name} must be a non-empty string")
    normalized = value.strip()
    if len(normalized) > _MAX_OBSERVABLE_TEXT_LENGTH:
        raise ShadowPlanningError(f"{name} exceeds the observable text limit")
    if _PRIVATE_REASONING_PATTERN.search(normalized) or _SECRET_ASSIGNMENT_PATTERN.search(normalized):
        raise ShadowPlanningError(f"{name} contains private reasoning or secret-shaped data")
    return normalized


def _string_tuple(value: Any, name: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, (str, bytes)) or not isinstance(value, (list, tuple)):
        raise ShadowPlanningError(f"{name} must be a sequence of strings")
    return tuple(_nonempty_string(item, name) for item in value)


def _confidence(value: Any) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ShadowPlanningError("confidence must be a number between 0 and 1")
    normalized = float(value)
    if not math.isfinite(normalized) or not 0.0 <= normalized <= 1.0:
        raise ShadowPlanningError("confidence must be a finite number between 0 and 1")
    return normalized


def _optional_confidence(value: Any) -> float | None:
    """Preserve unavailable confidence instead of fabricating a percentage."""

    return None if value is None else _confidence(value)


def _observable_mapping(value: Any, name: str) -> Mapping[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise ShadowPlanningError(f"{name} must be a mapping")

    def validate(item: Any, path: str) -> Any:
        if item is None or isinstance(item, (bool, int)):
            return item
        if isinstance(item, float):
            if not math.isfinite(item):
                raise ShadowPlanningError(f"{path} must not contain non-finite numbers")
            return item
        if isinstance(item, str):
            return _nonempty_string(item, path)
        if isinstance(item, Mapping):
            return {str(_nonempty_string(key, f"{path} key")): validate(val, f"{path}.{key}") for key, val in item.items()}
        if isinstance(item, (list, tuple)):
            return [validate(entry, f"{path} item") for entry in item]
        raise ShadowPlanningError(f"{path} contains a non-observable value")

    normalized = validate(value, name)
    try:
        encoded = json.dumps(normalized, sort_keys=True, allow_nan=False).encode("utf-8")
    except (TypeError, ValueError) as error:
        raise ShadowPlanningError(f"{name} must be JSON-serializable") from error
    if len(encoded) > _MAX_OBSERVABLE_PAYLOAD_BYTES:
        raise ShadowPlanningError(f"{name} exceeds the observable payload limit")
    return normalized


@dataclass(frozen=True, slots=True)
class PlanningRequest:
    """Explicit operational planning metadata accepted by the shadow adapter."""

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
    confidence: float | None = None
    provenance: Mapping[str, Any] = field(default_factory=dict)
    warnings: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for name in ("trace_id", "objective", "expected_deliverable"):
            object.__setattr__(self, name, _nonempty_string(getattr(self, name), name))
        for name in (
            "required_information",
            "retrieval_sources",
            "tool_requirements",
            "ordered_high_level_stages",
            "constraints",
            "stopping_conditions",
            "validation_requirements",
            "clarification_questions",
            "warnings",
        ):
            object.__setattr__(self, name, _string_tuple(getattr(self, name), name))
        if not isinstance(self.user_clarification_required, bool):
            raise ShadowPlanningError("user_clarification_required must be a boolean")
        if self.clarification_questions and not self.user_clarification_required:
            raise ShadowPlanningError("clarification_questions require user_clarification_required")
        object.__setattr__(self, "confidence", _optional_confidence(self.confidence))
        object.__setattr__(self, "provenance", _observable_mapping(self.provenance, "provenance"))


@dataclass(frozen=True, slots=True)
class ShadowPlan:
    """Read-only envelope around a standardized operational planning result."""

    planning_result: PlanningResult
    status: str
    confidence: float | None
    provenance: Mapping[str, Any]
    warnings: tuple[str, ...]
    latency_ms: float
    policy_version: str = SHADOW_PLANNING_POLICY_VERSION

    MODE = SHADOW_PLANNING_MODE
    AUTHORITATIVE = SHADOW_PLANNING_AUTHORITATIVE

    def __post_init__(self) -> None:
        if not isinstance(self.planning_result, PlanningResult):
            raise ShadowPlanningError("planning_result must use the Phase 0A PlanningResult contract")
        object.__setattr__(self, "status", _nonempty_string(self.status, "status"))
        object.__setattr__(self, "confidence", _optional_confidence(self.confidence))
        object.__setattr__(self, "provenance", _observable_mapping(self.provenance, "provenance"))
        object.__setattr__(self, "warnings", _string_tuple(self.warnings, "warnings"))
        if isinstance(self.latency_ms, bool) or not isinstance(self.latency_ms, (int, float)) or self.latency_ms < 0:
            raise ShadowPlanningError("latency_ms must be a non-negative number")
        if self.policy_version != SHADOW_PLANNING_POLICY_VERSION:
            raise ShadowPlanningError("unsupported planning policy_version")

    @property
    def trace_id(self) -> str:
        return self.planning_result.trace_id

    def to_metadata_dict(self) -> dict[str, Any]:
        """Serialize observable planning metadata; no plan execution is implied."""

        return {
            "mode": self.MODE,
            "authoritative": self.AUTHORITATIVE,
            "status": self.status,
            "confidence": self.confidence,
            "planning_result": self.planning_result.to_dict(),
            "provenance": dict(self.provenance),
            "warnings": list(self.warnings),
            "latency_ms": self.latency_ms,
            "policy_version": self.policy_version,
            "schema_version": COGNITIVE_CONTRACT_SCHEMA_VERSION,
        }


class ShadowPlanningEngine:
    """Deterministic contract adapter; it does not authorize or execute plans."""

    def plan(
        self,
        request: PlanningRequest,
        *,
        monotonic_clock: Callable[[], float] = time.monotonic,
    ) -> ShadowPlan:
        if not isinstance(request, PlanningRequest):
            raise ShadowPlanningError("request must be a PlanningRequest")
        if not callable(monotonic_clock):
            raise ShadowPlanningError("monotonic_clock must be callable")
        started = monotonic_clock()
        result = PlanningResult(
            trace_id=request.trace_id,
            objective=request.objective,
            expected_deliverable=request.expected_deliverable,
            required_information=request.required_information,
            retrieval_sources=request.retrieval_sources,
            tool_requirements=request.tool_requirements,
            ordered_high_level_stages=request.ordered_high_level_stages,
            constraints=request.constraints,
            stopping_conditions=request.stopping_conditions,
            validation_requirements=request.validation_requirements,
            user_clarification_required=request.user_clarification_required,
            clarification_questions=request.clarification_questions,
        )
        latency_ms = round(max(0.0, (monotonic_clock() - started) * 1000), 6)
        return ShadowPlan(
            planning_result=result,
            status="proposed",
            confidence=request.confidence,
            provenance={
                "adapter": "explicit_operational_input",
                "engine": "shadow_planning",
                **request.provenance,
            },
            warnings=request.warnings,
            latency_ms=latency_ms,
        )


def plan_shadow(
    request: PlanningRequest,
    *,
    monotonic_clock: Callable[[], float] = time.monotonic,
) -> ShadowPlan:
    """Produce a Phase 4 non-authoritative planning observation."""

    return ShadowPlanningEngine().plan(request, monotonic_clock=monotonic_clock)
