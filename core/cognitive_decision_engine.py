"""Aetheraeon architecture: Phase 2 Shadow Cognitive Decision Engine.

Cognitive Decision Engine responsibility:
    Convert a validated structured NLU result into an observable proposed
    cognitive-flow decision without executing or authorizing that proposal.

Architecture layer:
    Cognitive Intelligence Layer, between Natural Language Understanding and
    future retrieval, reasoning, planning, generation, and validation services.

Responsibilities:
    - identify proposed retrieval and memory needs;
    - identify tool, reasoning, planning, and response-validation candidates;
    - preserve correlation, confidence provenance, reason codes, and warnings;
    - support read-only comparison with observed current behavior.

Boundaries:
    - shadow-only and non-authoritative;
    - does not route requests, execute tools, mutate memory, grant permissions,
      bypass security, generate responses, persist state, or access databases;
    - does not replace request_router.py or ai_orchestrator.py;
    - is not imported by the live runtime during Phase 2.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import math
import re
import time
from typing import Any, Callable, ClassVar, Mapping

from core.cognitive_contracts import (
    COGNITIVE_CONTRACT_SCHEMA_VERSION,
    CognitiveDecision,
    NLUResult,
)


SHADOW_CDE_MODE = "shadow"
SHADOW_CDE_AUTHORITATIVE = False
SHADOW_CDE_POLICY_VERSION = "shadow-cde-policy-1.0"

_MEMORY_ACTION_PRIORITY = (
    "delete",
    "update",
    "store",
    "recall",
    "scoped_context",
    "candidate",
)

_OBJECTIVES = {
    "Conversation": "Respond to the conversation request",
    "Creative Writing": "Produce the requested creative material",
    "Coding": "Address the requested coding task",
    "Code Analysis": "Analyze the supplied code or implementation",
    "Debugging": "Diagnose the reported failure",
    "Calculation": "Produce the requested calculation",
    "Memory Recall": "Address the memory recall request",
    "Memory Storage": "Evaluate the proposed memory operation",
    "System Command": "Evaluate the proposed system command",
    "Research": "Address the research request using eligible sources",
    "Planning / Architecture": "Develop the requested high-level plan",
    "Decision Support": "Support the requested decision",
    "Personalization": "Address the requested communication preference",
    "Teaching / Learning": "Explain the requested subject",
}

_ANALYTICAL_INTENTS = frozenset(
    {
        "Coding",
        "Code Analysis",
        "Debugging",
        "Calculation",
        "Memory Recall",
        "Memory Storage",
        "Research",
        "Planning / Architecture",
        "Decision Support",
        "System Command",
    }
)
_CREATIVE_CONTEXTUAL_INTENTS = frozenset(
    {
        "Conversation",
        "Creative Writing",
        "Planning / Architecture",
        "Decision Support",
        "Personalization",
        "Teaching / Learning",
    }
)
_PLANNING_INTENTS = frozenset(
    {
        "Planning / Architecture",
        "Research",
        "Decision Support",
    }
)


class ShadowCDEError(ValueError):
    """Raised when shadow CDE input or output metadata is invalid."""


def _string_tuple(value: Any, name: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, (str, bytes)) or not isinstance(value, (list, tuple)):
        raise ShadowCDEError(f"{name} must be a sequence of strings")
    normalized = tuple(value)
    if any(not isinstance(item, str) or not item.strip() for item in normalized):
        raise ShadowCDEError(f"{name} must contain non-empty strings")
    return tuple(item.strip() for item in normalized)


def _optional_string(value: Any, name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ShadowCDEError(f"{name} must be None or a non-empty string")
    return value.strip()


@dataclass(frozen=True, slots=True)
class CognitiveDecisionRequest:
    """Structured, side-effect-free input accepted by the shadow CDE."""

    nlu_result: NLUResult
    request_objective: str | None = None
    response_format_requirements: tuple[str, ...] = ()
    observed_router_intent: str | None = None
    observed_retrieval_sources: tuple[str, ...] | None = None
    observed_memory_action: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.nlu_result, NLUResult):
            raise ShadowCDEError("nlu_result must use the Phase 0A NLUResult contract")
        object.__setattr__(
            self,
            "request_objective",
            _optional_string(self.request_objective, "request_objective"),
        )
        object.__setattr__(
            self,
            "response_format_requirements",
            _string_tuple(
                self.response_format_requirements,
                "response_format_requirements",
            ),
        )
        object.__setattr__(
            self,
            "observed_router_intent",
            _optional_string(self.observed_router_intent, "observed_router_intent"),
        )
        if self.observed_retrieval_sources is not None:
            object.__setattr__(
                self,
                "observed_retrieval_sources",
                _string_tuple(
                    self.observed_retrieval_sources,
                    "observed_retrieval_sources",
                ),
            )
        object.__setattr__(
            self,
            "observed_memory_action",
            _optional_string(
                self.observed_memory_action,
                "observed_memory_action",
            ),
        )


@dataclass(frozen=True, slots=True)
class ShadowCognitiveDecision:
    """Non-authoritative envelope around the versioned decision contract."""

    MODE: ClassVar[str] = SHADOW_CDE_MODE
    AUTHORITATIVE: ClassVar[bool] = SHADOW_CDE_AUTHORITATIVE

    decision: CognitiveDecision
    provenance: Mapping[str, str]
    response_requirements: Mapping[str, Any]
    retrieval_needs: tuple[str, ...]
    memory_need: str
    tool_candidates: tuple[str, ...]
    reasoning_needs: tuple[str, ...]
    planning_needed: bool
    latency_ms: float
    comparisons: Mapping[str, Any] = field(default_factory=dict)
    policy_version: str = SHADOW_CDE_POLICY_VERSION

    def __post_init__(self) -> None:
        if not isinstance(self.decision, CognitiveDecision):
            raise ShadowCDEError(
                "decision must use the Phase 0A CognitiveDecision contract"
            )
        object.__setattr__(self, "provenance", dict(self.provenance))
        object.__setattr__(
            self,
            "response_requirements",
            json.loads(json.dumps(self.response_requirements, allow_nan=False)),
        )
        object.__setattr__(
            self,
            "retrieval_needs",
            _string_tuple(self.retrieval_needs, "retrieval_needs"),
        )
        object.__setattr__(
            self,
            "tool_candidates",
            _string_tuple(self.tool_candidates, "tool_candidates"),
        )
        object.__setattr__(
            self,
            "reasoning_needs",
            _string_tuple(self.reasoning_needs, "reasoning_needs"),
        )
        if not isinstance(self.memory_need, str) or not self.memory_need:
            raise ShadowCDEError("memory_need must be a non-empty string")
        if not isinstance(self.planning_needed, bool):
            raise ShadowCDEError("planning_needed must be a boolean")
        if (
            isinstance(self.latency_ms, bool)
            or not isinstance(self.latency_ms, (int, float))
            or not math.isfinite(float(self.latency_ms))
            or self.latency_ms < 0
        ):
            raise ShadowCDEError("latency_ms must be a finite non-negative number")
        object.__setattr__(
            self,
            "comparisons",
            json.loads(json.dumps(self.comparisons, allow_nan=False)),
        )
        if any(
            not isinstance(key, str)
            or not isinstance(value, str)
            or not key
            or not value
            for key, value in self.provenance.items()
        ):
            raise ShadowCDEError("provenance must map non-empty strings to strings")

    @property
    def trace_id(self) -> str:
        return self.decision.trace_id

    @property
    def confidence(self) -> float | None:
        return self.decision.decision_confidence

    @property
    def warnings(self) -> tuple[str, ...]:
        return self.decision.warnings

    @property
    def schema_version(self) -> str:
        return self.decision.schema_version

    def to_dict(self) -> dict[str, Any]:
        return {
            "mode": self.MODE,
            "authoritative": self.AUTHORITATIVE,
            "policy_version": self.policy_version,
            "schema_version": self.schema_version,
            "trace_id": self.trace_id,
            "confidence": self.confidence,
            "provenance": dict(self.provenance),
            "warnings": list(self.warnings),
            "retrieval_needs": list(self.retrieval_needs),
            "memory_need": self.memory_need,
            "tool_candidates": list(self.tool_candidates),
            "reasoning_needs": list(self.reasoning_needs),
            "planning_needed": self.planning_needed,
            "response_requirements": dict(self.response_requirements),
            "latency_ms": self.latency_ms,
            "comparisons": dict(self.comparisons),
            "authority_boundaries": {
                "can_choose_live_routing": False,
                "can_execute_tools": False,
                "can_modify_memory": False,
                "can_authorize_permissions": False,
                "can_bypass_security": False,
                "can_generate_final_response": False,
                "can_persist_state": False,
            },
            "decision": self.decision.to_dict(),
        }

    def to_json(self, *, indent: int | None = None) -> str:
        return json.dumps(
            self.to_dict(),
            ensure_ascii=False,
            allow_nan=False,
            indent=indent,
            sort_keys=True,
        )


def _memory_action(nlu_result: NLUResult) -> str:
    for action in _MEMORY_ACTION_PRIORITY:
        if action in nlu_result.memory_signals:
            return action
    return "none"


def _memory_decision(nlu_result: NLUResult, action: str) -> dict[str, Any]:
    durable = action in {"store", "update", "delete"}
    requires_user_boundary = action != "none"
    reason_codes = ["NO_MEMORY_ACTION_PROPOSED"]
    if action != "none":
        reason_codes = [f"MEMORY_{action.upper()}_SIGNAL_OBSERVED"]
    if nlu_result.explicit_memory_instruction:
        reason_codes.append("EXPLICIT_MEMORY_INSTRUCTION_OBSERVED")
    if action == "candidate":
        reason_codes.append("CANDIDATE_OBSERVATION_ONLY")

    return {
        "mode": SHADOW_CDE_MODE,
        "status": "proposed",
        "action": action,
        "execute": False,
        "durable_operation": durable,
        "requires_authenticated_effective_user": requires_user_boundary,
        "requires_existing_authorization": requires_user_boundary,
        "requires_confirmed_receipt": durable,
        "candidate_promotion_allowed": False,
        "reason_codes": reason_codes,
    }


def _retrieval_plan(
    nlu_result: NLUResult,
    memory_action: str,
) -> tuple[dict[str, Any], tuple[str, ...]]:
    intent = nlu_result.primary_intent
    conversation_needed = intent not in {"System Command", "Calculation"}
    scoped_needed = (
        memory_action == "scoped_context"
        or nlu_result.context_scope.value in {"project", "user"}
        and intent in {"Memory Recall", "Planning / Architecture", "Coding", "Research"}
    )
    long_term_needed = memory_action == "recall" or intent == "Memory Recall"
    web_needed = "web" in nlu_result.tool_signals or intent == "Research"

    source_states = (
        (
            "conversation",
            conversation_needed,
            "CONVERSATION_CONTEXT_PROPOSED",
            True,
        ),
        (
            "scoped_memory",
            scoped_needed,
            "SCOPED_CONTEXT_PROPOSED",
            True,
        ),
        (
            "long_term_memory",
            long_term_needed,
            "LONG_TERM_RECALL_PROPOSED",
            True,
        ),
        ("web", web_needed, "WEB_RETRIEVAL_PROPOSED", False),
    )
    proposed_sources = []
    needed_sources = []
    for source, needed, reason_code, user_scoped in source_states:
        proposed_sources.append(
            {
                "source": source,
                "needed": needed,
                "execute": False,
                "reason_codes": [reason_code] if needed else ["NOT_PROPOSED"],
                "requires_authenticated_effective_user": user_scoped,
                "requires_existing_authorization": True,
                "requires_existing_ownership_check": user_scoped,
                "treat_results_as_untrusted_reference": source
                in {"long_term_memory", "web"},
            }
        )
        if needed:
            needed_sources.append(source)

    plan = {
        "mode": SHADOW_CDE_MODE,
        "status": "proposed",
        "execute": False,
        "proposed_sources": proposed_sources,
        "proposed_source_count": len(needed_sources),
        "selection_performed": False,
        "injection_performed": False,
    }
    return plan, tuple(needed_sources)


def _reasoning_needs(
    nlu_result: NLUResult,
    retrieval_needs: tuple[str, ...],
    planning_needed: bool,
) -> tuple[str, ...]:
    intent = nlu_result.primary_intent
    needs: list[str] = []
    if intent in _ANALYTICAL_INTENTS or nlu_result.entities or nlu_result.facts:
        needs.append("analytical")
    if intent in _CREATIVE_CONTEXTUAL_INTENTS:
        needs.append("creative_contextual")
    if planning_needed:
        needs.append("planning")
    if retrieval_needs:
        needs.append("evidence_alignment")
    if not needs:
        needs.append("contextual")
    return tuple(needs)


def _planning_needed(nlu_result: NLUResult) -> bool:
    if nlu_result.primary_intent in _PLANNING_INTENTS:
        return True
    return any(
        signal in {"execution_candidate", "aider", "n8n"}
        for signal in nlu_result.tool_signals
    )


def _validation_requirements(
    memory_action: str,
    retrieval_needs: tuple[str, ...],
    tool_candidates: tuple[str, ...],
) -> tuple[str, ...]:
    checks = [
        "request_coverage",
        "output_constraints",
        "permission_boundary",
        "privacy",
        "non_empty_response",
        "honest_failure_representation",
    ]
    if memory_action != "none" or any(
        source in {"scoped_memory", "long_term_memory"}
        for source in retrieval_needs
    ):
        checks.append("memory_claim_grounding")
    if tool_candidates:
        checks.append("tool_result_grounding")
    if "web" in retrieval_needs:
        checks.append("source_use_grounding")
    if retrieval_needs:
        checks.append("untrusted_reference_handling")
    return tuple(checks)


def _response_requirements(
    request: CognitiveDecisionRequest,
    memory_action: str,
    retrieval_needs: tuple[str, ...],
    tool_candidates: tuple[str, ...],
) -> dict[str, Any]:
    return {
        "address_current_request": True,
        "honor_output_constraints": True,
        "format_requirements": list(request.response_format_requirements),
        "represent_failures_honestly": True,
        "prevent_sensitive_trace_disclosure": True,
        "memory_claims_require_receipts": memory_action
        in {"store", "update", "delete"},
        "memory_influence_requires_actual_use": any(
            source in {"scoped_memory", "long_term_memory"}
            for source in retrieval_needs
        ),
        "tool_claims_require_results": bool(tool_candidates),
        "source_claims_require_actual_use": "web" in retrieval_needs,
        "final_response_generation_performed": False,
    }


def _reason_codes(
    nlu_result: NLUResult,
    memory_action: str,
    retrieval_needs: tuple[str, ...],
    tool_candidates: tuple[str, ...],
    planning_needed: bool,
) -> tuple[str, ...]:
    codes = [
        "SHADOW_DECISION_ONLY",
        "STRUCTURED_NLU_ACCEPTED",
        "EXISTING_AUTHORITIES_REQUIRED",
    ]
    intent_token = re.sub(r"[^A-Z0-9]+", "_", nlu_result.primary_intent.upper()).strip("_")
    codes.append(f"INTENT_{intent_token}")
    if memory_action != "none":
        codes.append(f"MEMORY_{memory_action.upper()}_PROPOSED")
    if retrieval_needs:
        codes.append("RETRIEVAL_NEEDS_PROPOSED")
    if tool_candidates:
        codes.append("TOOL_CANDIDATES_PROPOSED")
    if planning_needed:
        codes.append("PLANNING_PROPOSED")
    return tuple(codes)


def _warnings(
    nlu_result: NLUResult,
    memory_action: str,
    tool_candidates: tuple[str, ...],
) -> tuple[str, ...]:
    warnings = list(nlu_result.warnings)
    warnings.append("shadow_non_authoritative")
    if nlu_result.intent_confidence is None:
        warnings.append("decision_confidence_unavailable")
    if memory_action != "none":
        warnings.append("memory_operation_requires_server_authorization")
    if tool_candidates:
        warnings.append("tool_candidates_require_execution_validation")
    return tuple(dict.fromkeys(warnings))


def _comparisons(
    request: CognitiveDecisionRequest,
    retrieval_needs: tuple[str, ...],
    memory_action: str,
) -> dict[str, Any]:
    retrieval_match = None
    if request.observed_retrieval_sources is not None:
        retrieval_match = set(request.observed_retrieval_sources) == set(
            retrieval_needs
        )
    memory_match = None
    if request.observed_memory_action is not None:
        memory_match = request.observed_memory_action == memory_action
    return {
        "observed_router_intent": request.observed_router_intent,
        "observed_retrieval_sources": (
            list(request.observed_retrieval_sources)
            if request.observed_retrieval_sources is not None
            else None
        ),
        "retrieval_matches_observed": retrieval_match,
        "observed_memory_action": request.observed_memory_action,
        "memory_matches_observed": memory_match,
        "comparison_affects_decision": False,
    }


def propose_shadow_decision(
    request: CognitiveDecisionRequest,
    *,
    monotonic_clock: Callable[[], float] | None = None,
) -> ShadowCognitiveDecision:
    """Produce a proposal-only decision from structured request information."""

    if not isinstance(request, CognitiveDecisionRequest):
        raise ShadowCDEError("request must be a CognitiveDecisionRequest")
    clock = monotonic_clock or time.perf_counter
    started = float(clock())
    if not math.isfinite(started):
        raise ShadowCDEError("monotonic clock must return finite numbers")

    nlu_result = request.nlu_result
    memory_action = _memory_action(nlu_result)
    memory_decision = _memory_decision(nlu_result, memory_action)
    retrieval_plan, retrieval_needs = _retrieval_plan(
        nlu_result,
        memory_action,
    )
    tool_candidates = tuple(dict.fromkeys(nlu_result.tool_signals))
    planning_needed = _planning_needed(nlu_result)
    reasoning_needs = _reasoning_needs(
        nlu_result,
        retrieval_needs,
        planning_needed,
    )
    validation_requirements = _validation_requirements(
        memory_action,
        retrieval_needs,
        tool_candidates,
    )
    response_requirements = _response_requirements(
        request,
        memory_action,
        retrieval_needs,
        tool_candidates,
    )
    objective = request.request_objective or _OBJECTIVES.get(
        nlu_result.primary_intent,
        "Address the structured request",
    )

    decision = CognitiveDecision(
        trace_id=nlu_result.trace_id,
        request_objective=objective,
        approved_intent=nlu_result.primary_intent,
        relevant_entities=nlu_result.entities,
        relevant_facts=nlu_result.facts,
        context_treatment=(
            f"context:{nlu_result.context_scope.value};"
            f"temporal:{nlu_result.temporal_scope.value};"
            "evidence:reference_only"
        ),
        memory_decision=memory_decision,
        retrieval_plan=retrieval_plan,
        reasoning_strategy=reasoning_needs,
        personality_applicable=nlu_result.primary_intent != "System Command",
        planning_required=planning_needed,
        tool_or_web_requirements=tool_candidates,
        validation_requirements=validation_requirements,
        decision_confidence=nlu_result.intent_confidence,
        reason_codes=_reason_codes(
            nlu_result,
            memory_action,
            retrieval_needs,
            tool_candidates,
            planning_needed,
        ),
        warnings=_warnings(nlu_result, memory_action, tool_candidates),
        schema_version=COGNITIVE_CONTRACT_SCHEMA_VERSION,
    )
    provenance = {
        "request_objective": (
            "structured_request_context"
            if request.request_objective is not None
            else "deterministic_policy"
        ),
        "approved_intent": "nlu_result.primary_intent",
        "relevant_entities": "nlu_result.entities",
        "relevant_facts": "nlu_result.facts",
        "context_treatment": "nlu_scope_signals_and_deterministic_policy",
        "memory_decision": "nlu_result.memory_signals_and_deterministic_policy",
        "retrieval_plan": "deterministic_shadow_policy",
        "reasoning_strategy": "intent_and_evidence_policy",
        "planning_requirement": "intent_and_tool_signal_policy",
        "tool_candidates": "nlu_result.tool_signals",
        "validation_requirements": "governing_validation_policy",
        "decision_confidence": "nlu_result.intent_confidence",
        "warnings": "nlu_result_and_shadow_boundary_policy",
    }

    finished = float(clock())
    if not math.isfinite(finished):
        raise ShadowCDEError("monotonic clock must return finite numbers")
    latency_ms = max(0.0, (finished - started) * 1000.0)

    return ShadowCognitiveDecision(
        decision=decision,
        provenance=provenance,
        response_requirements=response_requirements,
        retrieval_needs=retrieval_needs,
        memory_need=memory_action,
        tool_candidates=tool_candidates,
        reasoning_needs=reasoning_needs,
        planning_needed=planning_needed,
        latency_ms=latency_ms,
        comparisons=_comparisons(request, retrieval_needs, memory_action),
    )


class ShadowCognitiveDecisionEngine:
    """Stateless facade exposing proposal-only CDE evaluation."""

    mode = SHADOW_CDE_MODE
    authoritative = SHADOW_CDE_AUTHORITATIVE

    def propose(
        self,
        request: CognitiveDecisionRequest,
        *,
        monotonic_clock: Callable[[], float] | None = None,
    ) -> ShadowCognitiveDecision:
        return propose_shadow_decision(
            request,
            monotonic_clock=monotonic_clock,
        )


__all__ = [
    "SHADOW_CDE_MODE",
    "SHADOW_CDE_AUTHORITATIVE",
    "SHADOW_CDE_POLICY_VERSION",
    "ShadowCDEError",
    "CognitiveDecisionRequest",
    "ShadowCognitiveDecision",
    "ShadowCognitiveDecisionEngine",
    "propose_shadow_decision",
]
