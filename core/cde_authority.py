"""Aetheraeon architecture: staged Cognitive Decision Engine authority gates.

Architecture layer:
    Cognitive policy boundary between the existing request pipeline and future
    CDE-owned capability adapters.

Responsibilities:
    - Read explicit, disabled-by-default CDE capability flags.
    - Produce a bounded CDE proposal and a privacy-safe decision receipt.
    - Preserve the existing authoritative decision for every disabled, invalid,
      or failed CDE evaluation.

Boundaries:
    This module never executes tools, writes memory, grants permissions, changes
    routing, generates responses, or persists state.  Access Control, the
    request router, orchestrator, memory services, validators, and executors
    remain authoritative.  The Stage 13 integration deliberately exposes only
    validated suggestions to future adapters; it does not replace an existing
    decision in this phase.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import os
from typing import Any, Mapping
from uuid import uuid4

from core.cognitive_trace import generate_correlation_id


CDE_AUTHORITY_SCHEMA_VERSION = "cde-authority-1.0"
CDE_AUTHORITY_POLICY_VERSION = "phase13-staged-authority-1.0"

_CAPABILITY_ENVIRONMENT_KEYS = {
    "retrieval_selection": "AETHERA_CDE_RETRIEVAL_SELECTION_ENABLED",
    "memory_operation": "AETHERA_CDE_MEMORY_OPERATION_ENABLED",
    "planning": "AETHERA_CDE_PLANNING_ENABLED",
    "reasoning_workflow": "AETHERA_CDE_REASONING_WORKFLOW_ENABLED",
    "tool_selection": "AETHERA_CDE_TOOL_SELECTION_ENABLED",
}
_TRUE_ENVIRONMENT_VALUES = frozenset({"1", "true", "yes", "on"})


class CDEAuthorityError(ValueError):
    """Raised only for invalid direct use of the isolated authority adapter."""


@dataclass(frozen=True, slots=True)
class CDEAuthorityFlags:
    """Explicit feature gates for individually staged CDE capabilities.

    All capabilities default to ``False``.  Mapping inputs accept literal
    booleans only, preventing accidental activation from a truthy string.
    Environment inputs require one of the documented true values.
    """

    retrieval_selection: bool = False
    memory_operation: bool = False
    planning: bool = False
    reasoning_workflow: bool = False
    tool_selection: bool = False

    @classmethod
    def from_mapping(cls, values: Mapping[str, Any] | None) -> "CDEAuthorityFlags":
        source = values if isinstance(values, Mapping) else {}
        normalized: dict[str, bool] = {}
        for capability in _CAPABILITY_ENVIRONMENT_KEYS:
            value = source.get(capability, False)
            normalized[capability] = value if isinstance(value, bool) else False
        return cls(**normalized)

    @classmethod
    def from_environment(cls, environment: Mapping[str, str] | None = None) -> "CDEAuthorityFlags":
        source = environment if environment is not None else os.environ
        return cls(**{
            capability: str(source.get(variable, "")).strip().lower()
            in _TRUE_ENVIRONMENT_VALUES
            for capability, variable in _CAPABILITY_ENVIRONMENT_KEYS.items()
        })

    @property
    def enabled_capabilities(self) -> tuple[str, ...]:
        return tuple(
            capability
            for capability in _CAPABILITY_ENVIRONMENT_KEYS
            if getattr(self, capability)
        )

    @property
    def any_enabled(self) -> bool:
        return bool(self.enabled_capabilities)

    def to_dict(self) -> dict[str, bool]:
        return {
            capability: getattr(self, capability)
            for capability in _CAPABILITY_ENVIRONMENT_KEYS
        }


@dataclass(frozen=True, slots=True)
class CDEDecisionReceipt:
    """A non-persistent receipt for one gated CDE evaluation.

    The receipt intentionally excludes prompts, user input, private memory,
    model reasoning, credentials, and tool payloads.  It records only the
    correlation and policy information required to audit this boundary.
    """

    receipt_id: str
    correlation_id: str
    recorded_at: str
    status: str
    enabled_capabilities: tuple[str, ...]
    confidence: float | None
    provenance: Mapping[str, str]
    authorization_context: Mapping[str, str]
    warnings: tuple[str, ...] = ()
    fallback_reason: str | None = None
    schema_version: str = CDE_AUTHORITY_SCHEMA_VERSION
    policy_version: str = CDE_AUTHORITY_POLICY_VERSION

    def to_dict(self) -> dict[str, Any]:
        return {
            "receipt_id": self.receipt_id,
            "correlation_id": self.correlation_id,
            "recorded_at": self.recorded_at,
            "status": self.status,
            "enabled_capabilities": list(self.enabled_capabilities),
            "confidence": self.confidence,
            "provenance": dict(self.provenance),
            "authorization_context": dict(self.authorization_context),
            "warnings": list(self.warnings),
            "fallback_reason": self.fallback_reason,
            "schema_version": self.schema_version,
            "policy_version": self.policy_version,
        }


@dataclass(frozen=True, slots=True)
class CDEAuthorityEvaluation:
    """Result of one isolated CDE evaluation without decision replacement."""

    effective_decision: Mapping[str, Any]
    receipt: CDEDecisionReceipt
    suggestions: Mapping[str, Mapping[str, Any]]
    cde_decision: Any | None = None

    @property
    def fallback_used(self) -> bool:
        return self.receipt.status == "fallback"


def _safe_authorization_context(effective_user: Mapping[str, Any] | None) -> dict[str, str] | None:
    if not isinstance(effective_user, Mapping):
        return None
    user_id = str(effective_user.get("user_id") or "").strip()
    role = str(effective_user.get("role") or "").strip().lower()
    source = str(effective_user.get("source") or "").strip()
    if not user_id or not role or not source:
        return None
    return {
        "effective_user_id": user_id,
        "effective_role": role,
        "source": source,
        "authorization_boundary": "access_control_remains_authoritative",
    }


def _receipt(
    *,
    correlation_id: str,
    status: str,
    flags: CDEAuthorityFlags,
    authorization_context: Mapping[str, str],
    confidence: float | None = None,
    warnings: tuple[str, ...] = (),
    fallback_reason: str | None = None,
) -> CDEDecisionReceipt:
    return CDEDecisionReceipt(
        receipt_id=f"cde-receipt-{uuid4()}",
        correlation_id=correlation_id,
        recorded_at=datetime.now(timezone.utc).isoformat(),
        status=status,
        enabled_capabilities=flags.enabled_capabilities,
        confidence=confidence,
        provenance={
            "authority_adapter": "core.cde_authority",
            "cde_policy": "core.cognitive_decision_engine",
            "policy_version": CDE_AUTHORITY_POLICY_VERSION,
        },
        authorization_context=dict(authorization_context),
        warnings=warnings,
        fallback_reason=fallback_reason,
    )


def _suggestions(cde_decision: Any, flags: CDEAuthorityFlags) -> dict[str, Mapping[str, Any]]:
    suggestions: dict[str, Mapping[str, Any]] = {}
    if flags.retrieval_selection:
        suggestions["retrieval_selection"] = {
            "status": "proposed_only",
            "sources": tuple(cde_decision.retrieval_needs),
        }
    if flags.memory_operation:
        suggestions["memory_operation"] = {
            "status": "proposed_only",
            "operation": cde_decision.memory_need,
        }
    if flags.planning:
        suggestions["planning"] = {
            "status": "proposed_only",
            "required": cde_decision.planning_needed,
        }
    if flags.reasoning_workflow:
        suggestions["reasoning_workflow"] = {
            "status": "proposed_only",
            "needs": tuple(cde_decision.reasoning_needs),
        }
    if flags.tool_selection:
        suggestions["tool_selection"] = {
            "status": "proposed_only",
            "candidates": tuple(cde_decision.tool_candidates),
        }
    return suggestions


def evaluate_cde_authority(
    *,
    user_message: str,
    existing_decision: Mapping[str, Any],
    effective_user: Mapping[str, Any] | None,
    flags: CDEAuthorityFlags | None = None,
    observed_router_intent: str | None = None,
) -> CDEAuthorityEvaluation:
    """Evaluate enabled CDE capabilities while retaining ``existing_decision``.

    This is a deliberately narrow Stage 13 authority seam.  It validates the
    authenticated user context, creates an NLU/CDE proposal only when a flag is
    enabled, and returns that proposal as non-executable suggestions.  The
    original decision object is always returned unchanged: a later approved
    migration may consume one capability through its own access-control and
    receipt boundary.
    """

    if not isinstance(existing_decision, Mapping):
        raise CDEAuthorityError("existing_decision must be a mapping")

    active_flags = flags if isinstance(flags, CDEAuthorityFlags) else CDEAuthorityFlags()
    correlation_id = generate_correlation_id()
    missing_context = {"authorization_boundary": "access_control_remains_authoritative"}
    authorization_context = _safe_authorization_context(effective_user)

    if not active_flags.any_enabled:
        return CDEAuthorityEvaluation(
            effective_decision=existing_decision,
            receipt=_receipt(
                correlation_id=correlation_id,
                status="disabled",
                flags=active_flags,
                authorization_context=missing_context,
            ),
            suggestions={},
        )

    if authorization_context is None:
        return CDEAuthorityEvaluation(
            effective_decision=existing_decision,
            receipt=_receipt(
                correlation_id=correlation_id,
                status="fallback",
                flags=active_flags,
                authorization_context=missing_context,
                warnings=("missing_effective_user_context",),
                fallback_reason="missing_effective_user_context",
            ),
            suggestions={},
        )

    try:
        # Imports remain lazy so disabled application requests never activate
        # the Phase 1 NLU or Phase 2 CDE modules.
        from core.cognitive_decision_engine import (
            CognitiveDecisionRequest,
            propose_shadow_decision,
        )
        from core.natural_language_understanding import analyze_shadow

        nlu_observation = analyze_shadow(
            user_message,
            trace_id=correlation_id,
            current_router_intent=observed_router_intent,
        )
        cde_decision = propose_shadow_decision(
            CognitiveDecisionRequest(
                nlu_result=nlu_observation.nlu_result,
                observed_router_intent=observed_router_intent,
            )
        )
        if cde_decision.trace_id != correlation_id:
            raise CDEAuthorityError("CDE correlation identifier did not match")
        confidence = cde_decision.confidence
        if confidence is not None and not 0.0 <= confidence <= 1.0:
            raise CDEAuthorityError("CDE confidence was outside the contract range")
        suggestions = _suggestions(cde_decision, active_flags)
        return CDEAuthorityEvaluation(
            effective_decision=existing_decision,
            receipt=_receipt(
                correlation_id=correlation_id,
                status="evaluated",
                flags=active_flags,
                authorization_context=authorization_context,
                confidence=confidence,
                warnings=tuple(cde_decision.warnings),
            ),
            suggestions=suggestions,
            cde_decision=cde_decision,
        )
    except Exception:
        # A CDE failure is intentionally non-observable to the user and cannot
        # alter the existing decision, response, permission, or execution path.
        return CDEAuthorityEvaluation(
            effective_decision=existing_decision,
            receipt=_receipt(
                correlation_id=correlation_id,
                status="fallback",
                flags=active_flags,
                authorization_context=authorization_context,
                warnings=("cde_authority_evaluation_failed",),
                fallback_reason="cde_authority_evaluation_failed",
            ),
            suggestions={},
        )


__all__ = [
    "CDE_AUTHORITY_SCHEMA_VERSION",
    "CDE_AUTHORITY_POLICY_VERSION",
    "CDEAuthorityError",
    "CDEAuthorityFlags",
    "CDEDecisionReceipt",
    "CDEAuthorityEvaluation",
    "evaluate_cde_authority",
]
