"""Aetheraeon architecture: candidate reinforcement and promotion-evaluation foundation.

Architecture layer:
    Memory Intelligence Layer service above the candidate-reinforcement audit
    persistence seam.

Responsibilities:
    - model versioned candidate evaluation, evidence, confidence-history, and
      audit records with structured truthful receipts;
    - validate explicit owner context and policy-versioned evaluation inputs;
    - record optional promotion proposals as non-executable, non-authoritative
      observations only.

Boundaries:
    - this service is isolated and is not imported by candidate storage,
      ChromaDB, active AI, routing, retrieval, memory injection, API, or UI;
    - it never detects evidence automatically, recomputes confidence, changes
      candidate state, promotes a candidate, writes permanent memory, or makes
      a truth decision;
    - durable audit storage is supplied through the repository seam only.
      Without a configured delegate, explicit evaluation fails safely.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
import math
from typing import Any, Mapping, Sequence
from uuid import uuid4

from core.access_control import normalize_role
from database.candidate_reinforcement_repository import (
    CandidateReinforcementRepositoryAdapter,
)
from database.conversation_repository import RepositoryOperationUnavailable


CANDIDATE_REINFORCEMENT_SCHEMA_VERSION = "1.0"
EVALUATION_STATUSES = frozenset({"recorded", "blocked", "insufficient_evidence"})


class CandidateReinforcementValidationError(ValueError):
    """Raised when an explicit candidate evaluation is structurally invalid."""


def _required_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CandidateReinforcementValidationError(
            f"{field_name} must be a non-empty string"
        )
    return value.strip()


def _json_mapping(value: Any, field_name: str) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise CandidateReinforcementValidationError(f"{field_name} must be a mapping")
    normalized = dict(value)
    try:
        json.dumps(normalized, ensure_ascii=False, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise CandidateReinforcementValidationError(
            f"{field_name} must contain JSON-serializable values"
        ) from exc
    return normalized


def _string_tuple(value: Any, field_name: str) -> tuple[str, ...]:
    if isinstance(value, str) or not isinstance(value, Sequence):
        raise CandidateReinforcementValidationError(
            f"{field_name} must be a sequence of strings"
        )
    return tuple(_required_string(item, f"{field_name} item") for item in value)


def _confidence(value: Any, field_name: str) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise CandidateReinforcementValidationError(
            f"{field_name} must be None or a number from 0.0 through 1.0"
        )
    normalized = float(value)
    if not math.isfinite(normalized) or not 0.0 <= normalized <= 1.0:
        raise CandidateReinforcementValidationError(
            f"{field_name} must be None or a number from 0.0 through 1.0"
        )
    return normalized


def _confidence_components(value: Any) -> dict[str, float | None]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise CandidateReinforcementValidationError("confidence_components must be a mapping")
    return {
        _required_string(name, "confidence_components key"): _confidence(
            score, f"confidence_components.{name}"
        )
        for name, score in value.items()
    }


def _confidence_effect(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise CandidateReinforcementValidationError(
            "confidence_effect must be None or a number from -1.0 through 1.0"
        )
    normalized = float(value)
    if not math.isfinite(normalized) or not -1.0 <= normalized <= 1.0:
        raise CandidateReinforcementValidationError(
            "confidence_effect must be None or a number from -1.0 through 1.0"
        )
    return normalized


def _iso_timestamp(value: Any, field_name: str) -> str:
    normalized = _required_string(value, field_name)
    try:
        datetime.fromisoformat(normalized.replace("Z", "+00:00"))
    except ValueError as exc:
        raise CandidateReinforcementValidationError(
            f"{field_name} must be ISO-8601"
        ) from exc
    return normalized


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _effective_user_snapshot(effective_user: Any) -> dict[str, str]:
    """Retain only non-secret identity fields established by an upstream path."""

    if not isinstance(effective_user, Mapping):
        raise CandidateReinforcementValidationError("effective_user context is required")
    return {
        "user_id": _required_string(effective_user.get("user_id"), "effective_user.user_id"),
        "role": normalize_role(effective_user.get("role")),
        "source": _required_string(effective_user.get("source"), "effective_user.source"),
    }


def _promotion_proposal(value: Any) -> dict[str, Any] | None:
    if value is None:
        return None
    proposal = _json_mapping(value, "promotion_proposal")
    if proposal.get("status") != "proposed":
        raise CandidateReinforcementValidationError(
            "promotion_proposal.status must be 'proposed'"
        )
    if proposal.get("executable") is not False:
        raise CandidateReinforcementValidationError(
            "promotion_proposal.executable must be false"
        )
    if proposal.get("authoritative") is not False:
        raise CandidateReinforcementValidationError(
            "promotion_proposal.authoritative must be false"
        )
    return proposal


@dataclass(frozen=True, slots=True)
class ReinforcementEvidence:
    """Observable reinforcement evidence; no scoring policy is applied here."""

    source_message_reference: str
    observed_at: str
    matched_fact_reference: str
    match_confidence: float | None
    contradiction_result: str
    confidence_effect: float | None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "source_message_reference",
            _required_string(self.source_message_reference, "source_message_reference"),
        )
        object.__setattr__(self, "observed_at", _iso_timestamp(self.observed_at, "observed_at"))
        object.__setattr__(
            self,
            "matched_fact_reference",
            _required_string(self.matched_fact_reference, "matched_fact_reference"),
        )
        object.__setattr__(
            self,
            "contradiction_result",
            _required_string(self.contradiction_result, "contradiction_result"),
        )
        object.__setattr__(
            self, "match_confidence", _confidence(self.match_confidence, "match_confidence")
        )
        object.__setattr__(self, "confidence_effect", _confidence_effect(self.confidence_effect))

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_message_reference": self.source_message_reference,
            "observed_at": self.observed_at,
            "matched_fact_reference": self.matched_fact_reference,
            "match_confidence": self.match_confidence,
            "contradiction_result": self.contradiction_result,
            "confidence_effect": self.confidence_effect,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "ReinforcementEvidence":
        if not isinstance(payload, Mapping):
            raise CandidateReinforcementValidationError("reinforcement evidence must be a mapping")
        return cls(**dict(payload))


@dataclass(frozen=True, slots=True)
class ConfidenceHistoryEntry:
    """One reported confidence state; this module does not calculate it."""

    observed_at: str
    confidence: float | None
    confidence_components: dict[str, float | None]
    basis_reference: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "observed_at", _iso_timestamp(self.observed_at, "observed_at"))
        object.__setattr__(self, "confidence", _confidence(self.confidence, "confidence"))
        object.__setattr__(
            self, "confidence_components", _confidence_components(self.confidence_components)
        )
        object.__setattr__(
            self, "basis_reference", _required_string(self.basis_reference, "basis_reference")
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "observed_at": self.observed_at,
            "confidence": self.confidence,
            "confidence_components": dict(self.confidence_components),
            "basis_reference": self.basis_reference,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "ConfidenceHistoryEntry":
        if not isinstance(payload, Mapping):
            raise CandidateReinforcementValidationError("confidence history entry must be a mapping")
        return cls(**dict(payload))


@dataclass(frozen=True, slots=True)
class CandidateEvaluationRecord:
    """Immutable evaluation record that cannot execute or authorize promotion."""

    evaluation_id: str
    candidate_id: str
    owner_identity: str
    scope_identifier: str
    evaluated_at: str
    policy_version: str
    evaluation_status: str
    evaluation_result: dict[str, Any]
    reinforcement_evidence: tuple[ReinforcementEvidence, ...]
    confidence_history: tuple[ConfidenceHistoryEntry, ...]
    supporting_references: tuple[str, ...]
    authorization_context: dict[str, str]
    audit_information: dict[str, Any] = field(default_factory=dict)
    promotion_proposal: dict[str, Any] | None = None
    schema_version: str = CANDIDATE_REINFORCEMENT_SCHEMA_VERSION

    def __post_init__(self) -> None:
        for field_name in (
            "evaluation_id",
            "candidate_id",
            "owner_identity",
            "scope_identifier",
            "policy_version",
        ):
            object.__setattr__(
                self, field_name, _required_string(getattr(self, field_name), field_name)
            )
        object.__setattr__(self, "evaluated_at", _iso_timestamp(self.evaluated_at, "evaluated_at"))
        if self.schema_version != CANDIDATE_REINFORCEMENT_SCHEMA_VERSION:
            raise CandidateReinforcementValidationError(
                f"schema_version must be {CANDIDATE_REINFORCEMENT_SCHEMA_VERSION!r}"
            )
        if self.evaluation_status not in EVALUATION_STATUSES:
            raise CandidateReinforcementValidationError(
                "evaluation_status must be one of: " + ", ".join(sorted(EVALUATION_STATUSES))
            )
        result = _json_mapping(self.evaluation_result, "evaluation_result")
        if not result:
            raise CandidateReinforcementValidationError("evaluation_result must not be empty")
        object.__setattr__(self, "evaluation_result", result)
        object.__setattr__(
            self,
            "reinforcement_evidence",
            tuple(
                item if isinstance(item, ReinforcementEvidence) else ReinforcementEvidence.from_dict(item)
                for item in self.reinforcement_evidence
            ),
        )
        object.__setattr__(
            self,
            "confidence_history",
            tuple(
                item if isinstance(item, ConfidenceHistoryEntry) else ConfidenceHistoryEntry.from_dict(item)
                for item in self.confidence_history
            ),
        )
        object.__setattr__(
            self, "supporting_references", _string_tuple(self.supporting_references, "supporting_references")
        )
        object.__setattr__(
            self, "audit_information", _json_mapping(self.audit_information, "audit_information")
        )
        object.__setattr__(self, "promotion_proposal", _promotion_proposal(self.promotion_proposal))
        authorization = _effective_user_snapshot(self.authorization_context)
        if authorization["user_id"] != self.owner_identity:
            raise CandidateReinforcementValidationError(
                "authorization_context.user_id must match owner_identity"
            )
        object.__setattr__(self, "authorization_context", authorization)

    def to_dict(self) -> dict[str, Any]:
        return {
            "evaluation_id": self.evaluation_id,
            "candidate_id": self.candidate_id,
            "owner_identity": self.owner_identity,
            "scope_identifier": self.scope_identifier,
            "evaluated_at": self.evaluated_at,
            "policy_version": self.policy_version,
            "evaluation_status": self.evaluation_status,
            "evaluation_result": dict(self.evaluation_result),
            "reinforcement_evidence": [item.to_dict() for item in self.reinforcement_evidence],
            "confidence_history": [item.to_dict() for item in self.confidence_history],
            "supporting_references": list(self.supporting_references),
            "authorization_context": dict(self.authorization_context),
            "audit_information": dict(self.audit_information),
            "promotion_proposal": (
                dict(self.promotion_proposal) if self.promotion_proposal is not None else None
            ),
            "schema_version": self.schema_version,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "CandidateEvaluationRecord":
        if not isinstance(payload, Mapping):
            raise CandidateReinforcementValidationError("evaluation record must be a mapping")
        allowed = set(cls.__dataclass_fields__)
        unknown = set(payload) - allowed
        missing = {name for name in allowed if name not in payload}
        if unknown or missing:
            details = []
            if unknown:
                details.append("unknown fields: " + ", ".join(sorted(unknown)))
            if missing:
                details.append("missing fields: " + ", ".join(sorted(missing)))
            raise CandidateReinforcementValidationError("; ".join(details))
        try:
            return cls(**dict(payload))
        except TypeError as exc:
            raise CandidateReinforcementValidationError(
                f"invalid evaluation fields: {exc}"
            ) from exc

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, allow_nan=False, sort_keys=True)

    @classmethod
    def from_json(cls, value: str) -> "CandidateEvaluationRecord":
        try:
            payload = json.loads(value)
        except (TypeError, json.JSONDecodeError) as exc:
            raise CandidateReinforcementValidationError("evaluation JSON is invalid") from exc
        return cls.from_dict(payload)


@dataclass(frozen=True, slots=True)
class CandidateReinforcementReceipt:
    """Truthful evaluation/read outcome without candidate or memory mutation."""

    operation: str
    success: bool
    status: str
    evaluation_id: str | None
    candidate_id: str | None
    owner_identity: str | None
    promotion_proposal_status: str | None
    reason: str | None = None
    schema_version: str = CANDIDATE_REINFORCEMENT_SCHEMA_VERSION

    def to_dict(self) -> dict[str, Any]:
        return {
            "operation": self.operation,
            "success": self.success,
            "status": self.status,
            "evaluation_id": self.evaluation_id,
            "candidate_id": self.candidate_id,
            "owner_identity": self.owner_identity,
            "promotion_proposal_status": self.promotion_proposal_status,
            "reason": self.reason,
            "schema_version": self.schema_version,
        }


class CandidateReinforcementService:
    """Explicit isolated evaluator with no promotion or permanent-memory path."""

    def __init__(self, repository: CandidateReinforcementRepositoryAdapter) -> None:
        if not isinstance(repository, CandidateReinforcementRepositoryAdapter):
            raise TypeError("repository must be CandidateReinforcementRepositoryAdapter")
        self._repository = repository

    @staticmethod
    def _failure(operation: str, reason: str) -> CandidateReinforcementReceipt:
        return CandidateReinforcementReceipt(
            operation=operation,
            success=False,
            status="failed",
            evaluation_id=None,
            candidate_id=None,
            owner_identity=None,
            promotion_proposal_status=None,
            reason=reason,
        )

    def record_evaluation(
        self,
        *,
        candidate_id: str,
        owner_identity: str,
        scope_identifier: str,
        policy_version: str,
        evaluation_status: str,
        evaluation_result: Mapping[str, Any],
        effective_user: Mapping[str, Any],
        reinforcement_evidence: Sequence[ReinforcementEvidence | Mapping[str, Any]] = (),
        confidence_history: Sequence[ConfidenceHistoryEntry | Mapping[str, Any]] = (),
        supporting_references: Sequence[str] = (),
        audit_information: Mapping[str, Any] | None = None,
        promotion_proposal: Mapping[str, Any] | None = None,
    ) -> CandidateReinforcementReceipt:
        """Persist one explicit evaluation record through the audit delegate."""

        try:
            authorization = _effective_user_snapshot(effective_user)
            normalized_owner = _required_string(owner_identity, "owner_identity")
            if authorization["user_id"] != normalized_owner:
                return self._failure(
                    "record_evaluation", "Effective user is not authorized for this owner."
                )
            audit = _json_mapping(audit_information, "audit_information")
            audit.setdefault("evaluation_mode", "explicit")
            record = CandidateEvaluationRecord(
                evaluation_id=str(uuid4()),
                candidate_id=candidate_id,
                owner_identity=normalized_owner,
                scope_identifier=scope_identifier,
                evaluated_at=_utc_timestamp(),
                policy_version=policy_version,
                evaluation_status=evaluation_status,
                evaluation_result=_json_mapping(evaluation_result, "evaluation_result"),
                reinforcement_evidence=tuple(reinforcement_evidence),
                confidence_history=tuple(confidence_history),
                supporting_references=_string_tuple(supporting_references, "supporting_references"),
                authorization_context=authorization,
                audit_information=audit,
                promotion_proposal=_promotion_proposal(promotion_proposal),
            )
        except CandidateReinforcementValidationError as exc:
            return self._failure("record_evaluation", str(exc))

        try:
            persistence_receipt = self._repository.create(record.to_dict())
        except RepositoryOperationUnavailable:
            return self._failure(
                "record_evaluation", "Candidate-reinforcement persistence is not configured."
            )
        except Exception as exc:
            return self._failure(
                "record_evaluation",
                f"Candidate-reinforcement persistence failed: {type(exc).__name__}",
            )

        confirmed = isinstance(persistence_receipt, Mapping) and (
            persistence_receipt.get("success") is True
            and persistence_receipt.get("evaluation_id") == record.evaluation_id
        )
        proposal_status = "proposed" if record.promotion_proposal is not None else None
        if not confirmed:
            reason = (
                persistence_receipt.get("reason")
                if isinstance(persistence_receipt, Mapping)
                else None
            )
            return CandidateReinforcementReceipt(
                operation="record_evaluation",
                success=False,
                status="failed",
                evaluation_id=record.evaluation_id,
                candidate_id=record.candidate_id,
                owner_identity=record.owner_identity,
                promotion_proposal_status=proposal_status,
                reason=str(
                    reason or "Candidate-reinforcement persistence did not confirm the record."
                ),
            )

        return CandidateReinforcementReceipt(
            operation="record_evaluation",
            success=True,
            status="completed",
            evaluation_id=record.evaluation_id,
            candidate_id=record.candidate_id,
            owner_identity=record.owner_identity,
            promotion_proposal_status=proposal_status,
        )

    def get_by_id(
        self,
        evaluation_id: str,
        *,
        effective_user: Mapping[str, Any],
    ) -> tuple[CandidateReinforcementReceipt, CandidateEvaluationRecord | None]:
        """Read one audit record only for its owning effective user."""

        try:
            authorization = _effective_user_snapshot(effective_user)
            normalized_evaluation_id = _required_string(evaluation_id, "evaluation_id")
        except CandidateReinforcementValidationError as exc:
            return self._failure("get_by_id", str(exc)), None

        try:
            payload = self._repository.get_by_id(normalized_evaluation_id)
        except RepositoryOperationUnavailable:
            return self._failure(
                "get_by_id", "Candidate-reinforcement persistence is not configured."
            ), None
        except Exception as exc:
            return self._failure(
                "get_by_id", f"Candidate-reinforcement read failed: {type(exc).__name__}"
            ), None

        if payload is None:
            return self._failure("get_by_id", "Candidate-reinforcement record was not found."), None
        try:
            record = CandidateEvaluationRecord.from_dict(payload)
        except CandidateReinforcementValidationError:
            return self._failure("get_by_id", "Candidate-reinforcement record is invalid."), None
        if record.owner_identity != authorization["user_id"]:
            return self._failure(
                "get_by_id", "Effective user is not authorized for this record."
            ), None
        return CandidateReinforcementReceipt(
            operation="get_by_id",
            success=True,
            status="completed",
            evaluation_id=record.evaluation_id,
            candidate_id=record.candidate_id,
            owner_identity=record.owner_identity,
            promotion_proposal_status=(
                "proposed" if record.promotion_proposal is not None else None
            ),
        ), record

    def list_by_candidate(
        self,
        candidate_id: str,
        *,
        effective_user: Mapping[str, Any],
    ) -> tuple[CandidateReinforcementReceipt, tuple[CandidateEvaluationRecord, ...]]:
        """Return explicit audit history only after every record passes owner validation."""

        try:
            authorization = _effective_user_snapshot(effective_user)
            normalized_candidate_id = _required_string(candidate_id, "candidate_id")
        except CandidateReinforcementValidationError as exc:
            return self._failure("list_by_candidate", str(exc)), ()

        try:
            payloads = self._repository.list_by_candidate(normalized_candidate_id)
        except RepositoryOperationUnavailable:
            return self._failure(
                "list_by_candidate", "Candidate-reinforcement persistence is not configured."
            ), ()
        except Exception as exc:
            return self._failure(
                "list_by_candidate", f"Candidate-reinforcement read failed: {type(exc).__name__}"
            ), ()

        if isinstance(payloads, str) or not isinstance(payloads, Sequence):
            return self._failure("list_by_candidate", "Candidate-reinforcement history is invalid."), ()
        try:
            records = tuple(CandidateEvaluationRecord.from_dict(item) for item in payloads)
        except CandidateReinforcementValidationError:
            return self._failure("list_by_candidate", "Candidate-reinforcement history is invalid."), ()
        if any(
            record.candidate_id != normalized_candidate_id
            or record.owner_identity != authorization["user_id"]
            for record in records
        ):
            return self._failure(
                "list_by_candidate", "Effective user is not authorized for this history."
            ), ()
        return CandidateReinforcementReceipt(
            operation="list_by_candidate",
            success=True,
            status="completed",
            evaluation_id=None,
            candidate_id=normalized_candidate_id,
            owner_identity=authorization["user_id"],
            promotion_proposal_status=None,
        ), records
