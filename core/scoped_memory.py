"""Aetheraeon architecture: explicit persistent scoped-memory foundation.

Architecture layer:
    Memory Intelligence Layer service above the scoped-memory persistence seam.

Responsibilities:
    - model versioned scoped-memory records and structured mutation receipts;
    - validate explicit scope, ownership, source evidence, and effective-user
      context before a persistence delegate is invoked;
    - preserve expiration metadata as informational data without automatic
      expiration, deletion, promotion, retrieval, or runtime activation.

Boundaries:
    - this service is isolated and is not imported by the active AI, routing,
      retrieval, memory-injection, API, UI, ChromaDB, or database paths;
    - it never learns from conversations, stores raw user messages, changes
      existing memory, selects retrieval, or makes cognitive policy decisions;
    - durable storage is supplied through the repository seam only.  Without
      a configured delegate, explicit creation fails safely with a receipt.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
from typing import Any, Mapping
from uuid import uuid4

from core.access_control import normalize_role
from database.conversation_repository import RepositoryOperationUnavailable
from database.scoped_memory_repository import ScopedMemoryRepositoryAdapter


SCOPED_MEMORY_SCHEMA_VERSION = "1.0"
SCOPED_MEMORY_STATUSES = frozenset({"active", "inactive", "superseded"})


class ScopedMemoryValidationError(ValueError):
    """Raised when an explicit scoped-memory request is structurally invalid."""


def _required_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ScopedMemoryValidationError(f"{field_name} must be a non-empty string")
    return value.strip()


def _json_mapping(value: Any, field_name: str) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise ScopedMemoryValidationError(f"{field_name} must be a mapping")
    normalized = dict(value)
    try:
        json.dumps(normalized, ensure_ascii=False, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise ScopedMemoryValidationError(
            f"{field_name} must contain JSON-serializable values"
        ) from exc
    return normalized


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _effective_user_snapshot(effective_user: Any) -> dict[str, str]:
    """Retain only the non-secret identity fields established upstream."""

    if not isinstance(effective_user, Mapping):
        raise ScopedMemoryValidationError("effective_user context is required")
    user_id = _required_string(effective_user.get("user_id"), "effective_user.user_id")
    source = _required_string(effective_user.get("source"), "effective_user.source")
    return {
        "user_id": user_id,
        "role": normalize_role(effective_user.get("role")),
        "source": source,
    }


@dataclass(frozen=True, slots=True)
class ScopedMemoryRecord:
    """Versioned, reference-only scoped-memory record for a durable delegate."""

    record_id: str
    scope_identifier: str
    owner_identity: str
    content_reference: str
    created_at: str
    source_message_reference: str
    scope_evidence_reference: str
    provenance: dict[str, Any]
    status: str
    creation_metadata: dict[str, Any] = field(default_factory=dict)
    expiration_metadata: dict[str, Any] = field(default_factory=dict)
    authorization_context: dict[str, str] = field(default_factory=dict)
    schema_version: str = SCOPED_MEMORY_SCHEMA_VERSION

    def __post_init__(self) -> None:
        for field_name in (
            "record_id",
            "scope_identifier",
            "owner_identity",
            "content_reference",
            "created_at",
            "source_message_reference",
            "scope_evidence_reference",
        ):
            object.__setattr__(
                self, field_name, _required_string(getattr(self, field_name), field_name)
            )
        if self.schema_version != SCOPED_MEMORY_SCHEMA_VERSION:
            raise ScopedMemoryValidationError(
                f"schema_version must be {SCOPED_MEMORY_SCHEMA_VERSION!r}"
            )
        if self.status not in SCOPED_MEMORY_STATUSES:
            raise ScopedMemoryValidationError(
                "status must be one of: " + ", ".join(sorted(SCOPED_MEMORY_STATUSES))
            )
        try:
            datetime.fromisoformat(self.created_at.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ScopedMemoryValidationError("created_at must be ISO-8601") from exc
        object.__setattr__(self, "provenance", _json_mapping(self.provenance, "provenance"))
        object.__setattr__(
            self, "creation_metadata", _json_mapping(self.creation_metadata, "creation_metadata")
        )
        object.__setattr__(
            self, "expiration_metadata", _json_mapping(self.expiration_metadata, "expiration_metadata")
        )
        authorization = _effective_user_snapshot(self.authorization_context)
        if authorization["user_id"] != self.owner_identity:
            raise ScopedMemoryValidationError(
                "authorization_context.user_id must match owner_identity"
            )
        object.__setattr__(self, "authorization_context", authorization)

    def to_dict(self) -> dict[str, Any]:
        return {
            "record_id": self.record_id,
            "scope_identifier": self.scope_identifier,
            "owner_identity": self.owner_identity,
            "content_reference": self.content_reference,
            "created_at": self.created_at,
            "source_message_reference": self.source_message_reference,
            "scope_evidence_reference": self.scope_evidence_reference,
            "provenance": dict(self.provenance),
            "status": self.status,
            "creation_metadata": dict(self.creation_metadata),
            "expiration_metadata": dict(self.expiration_metadata),
            "authorization_context": dict(self.authorization_context),
            "schema_version": self.schema_version,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "ScopedMemoryRecord":
        if not isinstance(payload, Mapping):
            raise ScopedMemoryValidationError("scoped-memory record must be a mapping")
        allowed = set(cls.__dataclass_fields__)
        unknown = set(payload) - allowed
        missing = {name for name in allowed if name not in payload}
        if unknown or missing:
            details = []
            if unknown:
                details.append("unknown fields: " + ", ".join(sorted(unknown)))
            if missing:
                details.append("missing fields: " + ", ".join(sorted(missing)))
            raise ScopedMemoryValidationError("; ".join(details))
        try:
            return cls(**dict(payload))
        except TypeError as exc:
            raise ScopedMemoryValidationError(f"invalid scoped-memory fields: {exc}") from exc

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, allow_nan=False, sort_keys=True)

    @classmethod
    def from_json(cls, value: str) -> "ScopedMemoryRecord":
        try:
            payload = json.loads(value)
        except (TypeError, json.JSONDecodeError) as exc:
            raise ScopedMemoryValidationError("scoped-memory JSON is invalid") from exc
        return cls.from_dict(payload)


@dataclass(frozen=True, slots=True)
class ScopedMemoryReceipt:
    """Truthful create/read outcome without exposing scoped content."""

    operation: str
    success: bool
    status: str
    record_id: str | None
    scope_identifier: str | None
    owner_identity: str | None
    reason: str | None = None
    warnings: tuple[str, ...] = ()
    schema_version: str = SCOPED_MEMORY_SCHEMA_VERSION

    def to_dict(self) -> dict[str, Any]:
        return {
            "operation": self.operation,
            "success": self.success,
            "status": self.status,
            "record_id": self.record_id,
            "scope_identifier": self.scope_identifier,
            "owner_identity": self.owner_identity,
            "reason": self.reason,
            "warnings": list(self.warnings),
            "schema_version": self.schema_version,
        }


class ScopedMemoryService:
    """Explicit, isolated service for a future durable scoped-memory store."""

    def __init__(self, repository: ScopedMemoryRepositoryAdapter) -> None:
        if not isinstance(repository, ScopedMemoryRepositoryAdapter):
            raise TypeError("repository must be ScopedMemoryRepositoryAdapter")
        self._repository = repository

    @staticmethod
    def _failure(operation: str, reason: str) -> ScopedMemoryReceipt:
        return ScopedMemoryReceipt(
            operation=operation,
            success=False,
            status="failed",
            record_id=None,
            scope_identifier=None,
            owner_identity=None,
            reason=reason,
        )

    def create(
        self,
        *,
        scope_identifier: str,
        owner_identity: str,
        content_reference: str,
        source_message_reference: str,
        scope_evidence_reference: str,
        provenance: Mapping[str, Any],
        effective_user: Mapping[str, Any],
        creation_metadata: Mapping[str, Any] | None = None,
        expiration_metadata: Mapping[str, Any] | None = None,
        status: str = "active",
    ) -> ScopedMemoryReceipt:
        """Persist one explicitly supplied scoped record through the delegate."""

        try:
            authorization = _effective_user_snapshot(effective_user)
            normalized_owner = _required_string(owner_identity, "owner_identity")
            if authorization["user_id"] != normalized_owner:
                return self._failure("create", "Effective user is not authorized for this owner.")
            record = ScopedMemoryRecord(
                record_id=str(uuid4()),
                scope_identifier=scope_identifier,
                owner_identity=normalized_owner,
                content_reference=content_reference,
                created_at=_utc_timestamp(),
                source_message_reference=source_message_reference,
                scope_evidence_reference=scope_evidence_reference,
                provenance=_json_mapping(provenance, "provenance"),
                status=status,
                creation_metadata=_json_mapping(creation_metadata, "creation_metadata"),
                expiration_metadata=_json_mapping(expiration_metadata, "expiration_metadata"),
                authorization_context=authorization,
            )
        except ScopedMemoryValidationError as exc:
            return self._failure("create", str(exc))

        try:
            persistence_receipt = self._repository.create(record.to_dict())
        except RepositoryOperationUnavailable:
            return self._failure("create", "Scoped-memory persistence is not configured.")
        except Exception as exc:
            return self._failure("create", f"Scoped-memory persistence failed: {type(exc).__name__}")

        confirmed = isinstance(persistence_receipt, Mapping) and (
            persistence_receipt.get("success") is True
            and persistence_receipt.get("record_id") == record.record_id
        )
        if not confirmed:
            reason = (
                persistence_receipt.get("reason")
                if isinstance(persistence_receipt, Mapping)
                else None
            )
            return ScopedMemoryReceipt(
                operation="create",
                success=False,
                status="failed",
                record_id=record.record_id,
                scope_identifier=record.scope_identifier,
                owner_identity=record.owner_identity,
                reason=str(reason or "Scoped-memory persistence did not confirm the record."),
            )

        warnings = ()
        if record.expiration_metadata:
            warnings = ("expiration_metadata_is_informational_only",)
        return ScopedMemoryReceipt(
            operation="create",
            success=True,
            status="completed",
            record_id=record.record_id,
            scope_identifier=record.scope_identifier,
            owner_identity=record.owner_identity,
            warnings=warnings,
        )

    def get_by_id(
        self,
        record_id: str,
        *,
        effective_user: Mapping[str, Any],
    ) -> tuple[ScopedMemoryReceipt, ScopedMemoryRecord | None]:
        """Read a record only for its owning effective user; never auto-retrieve."""

        try:
            authorization = _effective_user_snapshot(effective_user)
            normalized_record_id = _required_string(record_id, "record_id")
        except ScopedMemoryValidationError as exc:
            return self._failure("get_by_id", str(exc)), None

        try:
            payload = self._repository.get_by_id(normalized_record_id)
        except RepositoryOperationUnavailable:
            return self._failure("get_by_id", "Scoped-memory persistence is not configured."), None
        except Exception as exc:
            return self._failure("get_by_id", f"Scoped-memory read failed: {type(exc).__name__}"), None

        if payload is None:
            return self._failure("get_by_id", "Scoped-memory record was not found."), None
        try:
            record = ScopedMemoryRecord.from_dict(payload)
        except ScopedMemoryValidationError:
            return self._failure("get_by_id", "Scoped-memory record is invalid."), None
        if record.owner_identity != authorization["user_id"]:
            return self._failure("get_by_id", "Effective user is not authorized for this record."), None
        return ScopedMemoryReceipt(
            operation="get_by_id",
            success=True,
            status="completed",
            record_id=record.record_id,
            scope_identifier=record.scope_identifier,
            owner_identity=record.owner_identity,
        ), record
