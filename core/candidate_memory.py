"""Aetheraeon architecture: explicit candidate-memory observation foundation.

Architecture layer:
    Memory Intelligence Layer service above the candidate-memory persistence
    seam.

Responsibilities:
    - model versioned candidate observations and structured truthful receipts;
    - validate explicit fact references, ownership, source evidence, confidence
      metadata, audit data, and effective-user context before persistence;
    - retain observations as candidates only, with no promotion, reinforcement,
      expiration, retrieval, truth decision, or runtime activation.

Boundaries:
    - this service is isolated and is not imported by active AI, routing,
      retrieval, memory-injection, API, UI, ChromaDB, or database paths;
    - it never learns from conversations, modifies existing memories, selects
      retrieval, promotes a candidate, or overrides user control;
    - durable storage is supplied through the repository seam only. Without a
      configured delegate, explicit observation fails safely with a receipt.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
import math
from typing import Any, Mapping, Sequence
from uuid import uuid4

from core.access_control import normalize_role
from database.candidate_memory_repository import CandidateMemoryRepositoryAdapter
from database.conversation_repository import RepositoryOperationUnavailable


CANDIDATE_MEMORY_SCHEMA_VERSION = "1.0"
CANDIDATE_MEMORY_STATUSES = frozenset({"candidate", "dismissed", "rejected"})


class CandidateMemoryValidationError(ValueError):
    """Raised when an explicit candidate-memory observation is invalid."""


def _required_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CandidateMemoryValidationError(f"{field_name} must be a non-empty string")
    return value.strip()


def _json_mapping(value: Any, field_name: str) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise CandidateMemoryValidationError(f"{field_name} must be a mapping")
    normalized = dict(value)
    try:
        json.dumps(normalized, ensure_ascii=False, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise CandidateMemoryValidationError(
            f"{field_name} must contain JSON-serializable values"
        ) from exc
    return normalized


def _string_tuple(value: Any, field_name: str) -> tuple[str, ...]:
    if isinstance(value, str) or not isinstance(value, Sequence):
        raise CandidateMemoryValidationError(f"{field_name} must be a sequence of strings")
    normalized = tuple(_required_string(item, f"{field_name} item") for item in value)
    return normalized


def _confidence(value: Any, field_name: str) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise CandidateMemoryValidationError(
            f"{field_name} must be None or a number from 0.0 through 1.0"
        )
    normalized = float(value)
    if not math.isfinite(normalized) or not 0.0 <= normalized <= 1.0:
        raise CandidateMemoryValidationError(
            f"{field_name} must be None or a number from 0.0 through 1.0"
        )
    return normalized


def _confidence_components(value: Any) -> dict[str, float | None]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise CandidateMemoryValidationError("confidence_components must be a mapping")
    return {
        _required_string(name, "confidence_components key"): _confidence(
            score, f"confidence_components.{name}"
        )
        for name, score in value.items()
    }


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _effective_user_snapshot(effective_user: Any) -> dict[str, str]:
    """Retain only non-secret identity fields established by an upstream path."""

    if not isinstance(effective_user, Mapping):
        raise CandidateMemoryValidationError("effective_user context is required")
    return {
        "user_id": _required_string(effective_user.get("user_id"), "effective_user.user_id"),
        "role": normalize_role(effective_user.get("role")),
        "source": _required_string(effective_user.get("source"), "effective_user.source"),
    }


@dataclass(frozen=True, slots=True)
class CandidateMemoryRecord:
    """Versioned candidate only; its promotion outcome is always unresolved."""

    candidate_id: str
    owner_identity: str
    scope_identifier: str
    proposed_content_reference: str
    normalized_fact: str
    fact_type: str
    source_message_reference: str
    provenance: dict[str, Any]
    observed_at: str
    confidence: float | None
    confidence_components: dict[str, float | None]
    status: str
    supporting_references: tuple[str, ...]
    reinforcement_references: tuple[str, ...]
    conflict_flag: bool
    sensitivity_flag: str
    authorization_context: dict[str, str]
    audit_information: dict[str, Any] = field(default_factory=dict)
    promotion_outcome: None = None
    schema_version: str = CANDIDATE_MEMORY_SCHEMA_VERSION

    def __post_init__(self) -> None:
        for field_name in (
            "candidate_id",
            "owner_identity",
            "scope_identifier",
            "proposed_content_reference",
            "normalized_fact",
            "fact_type",
            "source_message_reference",
            "observed_at",
            "sensitivity_flag",
        ):
            object.__setattr__(
                self, field_name, _required_string(getattr(self, field_name), field_name)
            )
        if self.schema_version != CANDIDATE_MEMORY_SCHEMA_VERSION:
            raise CandidateMemoryValidationError(
                f"schema_version must be {CANDIDATE_MEMORY_SCHEMA_VERSION!r}"
            )
        if self.status not in CANDIDATE_MEMORY_STATUSES:
            raise CandidateMemoryValidationError(
                "status must be one of: " + ", ".join(sorted(CANDIDATE_MEMORY_STATUSES))
            )
        if self.promotion_outcome is not None:
            raise CandidateMemoryValidationError(
                "promotion_outcome must be None while promotion is not implemented"
            )
        try:
            datetime.fromisoformat(self.observed_at.replace("Z", "+00:00"))
        except ValueError as exc:
            raise CandidateMemoryValidationError("observed_at must be ISO-8601") from exc
        if not isinstance(self.conflict_flag, bool):
            raise CandidateMemoryValidationError("conflict_flag must be a boolean")
        object.__setattr__(self, "confidence", _confidence(self.confidence, "confidence"))
        object.__setattr__(
            self, "confidence_components", _confidence_components(self.confidence_components)
        )
        object.__setattr__(self, "provenance", _json_mapping(self.provenance, "provenance"))
        object.__setattr__(
            self, "audit_information", _json_mapping(self.audit_information, "audit_information")
        )
        object.__setattr__(
            self,
            "supporting_references",
            _string_tuple(self.supporting_references, "supporting_references"),
        )
        object.__setattr__(
            self,
            "reinforcement_references",
            _string_tuple(self.reinforcement_references, "reinforcement_references"),
        )
        authorization = _effective_user_snapshot(self.authorization_context)
        if authorization["user_id"] != self.owner_identity:
            raise CandidateMemoryValidationError(
                "authorization_context.user_id must match owner_identity"
            )
        object.__setattr__(self, "authorization_context", authorization)

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "owner_identity": self.owner_identity,
            "scope_identifier": self.scope_identifier,
            "proposed_content_reference": self.proposed_content_reference,
            "normalized_fact": self.normalized_fact,
            "fact_type": self.fact_type,
            "source_message_reference": self.source_message_reference,
            "provenance": dict(self.provenance),
            "observed_at": self.observed_at,
            "confidence": self.confidence,
            "confidence_components": dict(self.confidence_components),
            "status": self.status,
            "supporting_references": list(self.supporting_references),
            "reinforcement_references": list(self.reinforcement_references),
            "conflict_flag": self.conflict_flag,
            "sensitivity_flag": self.sensitivity_flag,
            "authorization_context": dict(self.authorization_context),
            "audit_information": dict(self.audit_information),
            "promotion_outcome": None,
            "schema_version": self.schema_version,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "CandidateMemoryRecord":
        if not isinstance(payload, Mapping):
            raise CandidateMemoryValidationError("candidate-memory record must be a mapping")
        allowed = set(cls.__dataclass_fields__)
        unknown = set(payload) - allowed
        missing = {name for name in allowed if name not in payload}
        if unknown or missing:
            details = []
            if unknown:
                details.append("unknown fields: " + ", ".join(sorted(unknown)))
            if missing:
                details.append("missing fields: " + ", ".join(sorted(missing)))
            raise CandidateMemoryValidationError("; ".join(details))
        try:
            return cls(**dict(payload))
        except TypeError as exc:
            raise CandidateMemoryValidationError(f"invalid candidate-memory fields: {exc}") from exc

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, allow_nan=False, sort_keys=True)

    @classmethod
    def from_json(cls, value: str) -> "CandidateMemoryRecord":
        try:
            payload = json.loads(value)
        except (TypeError, json.JSONDecodeError) as exc:
            raise CandidateMemoryValidationError("candidate-memory JSON is invalid") from exc
        return cls.from_dict(payload)


@dataclass(frozen=True, slots=True)
class CandidateMemoryReceipt:
    """Truthful observation/read outcome without exposing candidate content."""

    operation: str
    success: bool
    status: str
    candidate_id: str | None
    owner_identity: str | None
    scope_identifier: str | None
    reason: str | None = None
    warnings: tuple[str, ...] = ()
    schema_version: str = CANDIDATE_MEMORY_SCHEMA_VERSION

    def to_dict(self) -> dict[str, Any]:
        return {
            "operation": self.operation,
            "success": self.success,
            "status": self.status,
            "candidate_id": self.candidate_id,
            "owner_identity": self.owner_identity,
            "scope_identifier": self.scope_identifier,
            "reason": self.reason,
            "warnings": list(self.warnings),
            "schema_version": self.schema_version,
        }


class CandidateMemoryService:
    """Explicit, isolated observer for future durable candidate memory."""

    def __init__(self, repository: CandidateMemoryRepositoryAdapter) -> None:
        if not isinstance(repository, CandidateMemoryRepositoryAdapter):
            raise TypeError("repository must be CandidateMemoryRepositoryAdapter")
        self._repository = repository

    @staticmethod
    def _failure(operation: str, reason: str) -> CandidateMemoryReceipt:
        return CandidateMemoryReceipt(
            operation=operation,
            success=False,
            status="failed",
            candidate_id=None,
            owner_identity=None,
            scope_identifier=None,
            reason=reason,
        )

    def observe(
        self,
        *,
        owner_identity: str,
        scope_identifier: str,
        proposed_content_reference: str,
        normalized_fact: str,
        fact_type: str,
        source_message_reference: str,
        provenance: Mapping[str, Any],
        effective_user: Mapping[str, Any],
        confidence: float | None = None,
        confidence_components: Mapping[str, float | None] | None = None,
        supporting_references: Sequence[str] = (),
        reinforcement_references: Sequence[str] = (),
        conflict_flag: bool = False,
        sensitivity_flag: str = "unknown",
        audit_information: Mapping[str, Any] | None = None,
        status: str = "candidate",
    ) -> CandidateMemoryReceipt:
        """Persist one explicitly supplied candidate observation through a delegate."""

        try:
            authorization = _effective_user_snapshot(effective_user)
            normalized_owner = _required_string(owner_identity, "owner_identity")
            if authorization["user_id"] != normalized_owner:
                return self._failure("observe", "Effective user is not authorized for this owner.")
            audit = _json_mapping(audit_information, "audit_information")
            audit.setdefault("observation_mode", "explicit")
            record = CandidateMemoryRecord(
                candidate_id=str(uuid4()),
                owner_identity=normalized_owner,
                scope_identifier=scope_identifier,
                proposed_content_reference=proposed_content_reference,
                normalized_fact=normalized_fact,
                fact_type=fact_type,
                source_message_reference=source_message_reference,
                provenance=_json_mapping(provenance, "provenance"),
                observed_at=_utc_timestamp(),
                confidence=_confidence(confidence, "confidence"),
                confidence_components=_confidence_components(confidence_components),
                status=status,
                supporting_references=_string_tuple(supporting_references, "supporting_references"),
                reinforcement_references=_string_tuple(
                    reinforcement_references, "reinforcement_references"
                ),
                conflict_flag=conflict_flag,
                sensitivity_flag=sensitivity_flag,
                authorization_context=authorization,
                audit_information=audit,
            )
        except CandidateMemoryValidationError as exc:
            return self._failure("observe", str(exc))

        try:
            persistence_receipt = self._repository.create(record.to_dict())
        except RepositoryOperationUnavailable:
            return self._failure("observe", "Candidate-memory persistence is not configured.")
        except Exception as exc:
            return self._failure(
                "observe", f"Candidate-memory persistence failed: {type(exc).__name__}"
            )

        confirmed = isinstance(persistence_receipt, Mapping) and (
            persistence_receipt.get("success") is True
            and persistence_receipt.get("candidate_id") == record.candidate_id
        )
        if not confirmed:
            reason = (
                persistence_receipt.get("reason")
                if isinstance(persistence_receipt, Mapping)
                else None
            )
            return CandidateMemoryReceipt(
                operation="observe",
                success=False,
                status="failed",
                candidate_id=record.candidate_id,
                owner_identity=record.owner_identity,
                scope_identifier=record.scope_identifier,
                reason=str(reason or "Candidate-memory persistence did not confirm the record."),
            )

        return CandidateMemoryReceipt(
            operation="observe",
            success=True,
            status="completed",
            candidate_id=record.candidate_id,
            owner_identity=record.owner_identity,
            scope_identifier=record.scope_identifier,
        )

    def get_by_id(
        self,
        candidate_id: str,
        *,
        effective_user: Mapping[str, Any],
    ) -> tuple[CandidateMemoryReceipt, CandidateMemoryRecord | None]:
        """Read explicitly by identifier only for its owning effective user."""

        try:
            authorization = _effective_user_snapshot(effective_user)
            normalized_candidate_id = _required_string(candidate_id, "candidate_id")
        except CandidateMemoryValidationError as exc:
            return self._failure("get_by_id", str(exc)), None

        try:
            payload = self._repository.get_by_id(normalized_candidate_id)
        except RepositoryOperationUnavailable:
            return self._failure("get_by_id", "Candidate-memory persistence is not configured."), None
        except Exception as exc:
            return self._failure("get_by_id", f"Candidate-memory read failed: {type(exc).__name__}"), None

        if payload is None:
            return self._failure("get_by_id", "Candidate-memory record was not found."), None
        try:
            record = CandidateMemoryRecord.from_dict(payload)
        except CandidateMemoryValidationError:
            return self._failure("get_by_id", "Candidate-memory record is invalid."), None
        if record.owner_identity != authorization["user_id"]:
            return self._failure("get_by_id", "Effective user is not authorized for this record."), None
        return CandidateMemoryReceipt(
            operation="get_by_id",
            success=True,
            status="completed",
            candidate_id=record.candidate_id,
            owner_identity=record.owner_identity,
            scope_identifier=record.scope_identifier,
        ), record
