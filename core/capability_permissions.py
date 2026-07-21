"""Phase 4A capability policy decisions without capability execution.

This module classifies future system capabilities by role and records every
decision. It is intentionally disconnected from routing, tools, automation,
and filesystem operations.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
import uuid

from core.security_roles import ADMIN, OWNER, USER, normalize_security_role
from database import workspace_security_repository as workspace_repository


ALLOWED = "allowed"
DENIED = "denied"
REQUIRES_APPROVAL = "requires_approval"
CAPABILITY_DECISIONS = frozenset({ALLOWED, DENIED, REQUIRES_APPROVAL})


@dataclass(frozen=True)
class CapabilityDefinition:
    """Immutable policy metadata for one future capability."""

    name: str
    description: str
    required_role: str
    approval_required: bool
    enabled: bool


def _capability(
    name: str,
    description: str,
    required_role: str,
    *,
    enabled: bool = False,
) -> CapabilityDefinition:
    return CapabilityDefinition(
        name=name,
        description=description,
        required_role=required_role,
        approval_required=True,
        enabled=enabled,
    )


CAPABILITY_DEFINITIONS = MappingProxyType({
    "filesystem.read": _capability(
        "filesystem.read",
        "Future read-only access within an approved workspace sandbox.",
        ADMIN,
        enabled=True,
    ),
    "filesystem.write": _capability(
        "filesystem.write",
        "Future creation or modification of files in an approved sandbox.",
        ADMIN,
    ),
    "filesystem.delete": _capability(
        "filesystem.delete",
        "Future deletion of files from an approved location.",
        OWNER,
    ),
    "filesystem.execute": _capability(
        "filesystem.execute",
        "Future execution of an approved file.",
        OWNER,
    ),
    "system.command": _capability(
        "system.command",
        "Future invocation of an approved system command.",
        OWNER,
    ),
    "automation.execute": _capability(
        "automation.execute",
        "Future execution of an approved automation workflow.",
        OWNER,
    ),
    "integration.manage": _capability(
        "integration.manage",
        "Future management of an approved external integration.",
        OWNER,
    ),
})

_ROLE_LEVEL = MappingProxyType({USER: 0, ADMIN: 1, OWNER: 2})


def _audit_decision(repository, user_uid, capability, decision, reason) -> str:
    """Persist a decision and fail closed if audit persistence is unavailable."""

    try:
        repository.record_capability_decision(
            user_uid=user_uid,
            capability=capability,
            decision=decision,
            reason=reason,
        )
    except Exception:
        return DENIED
    return decision


def check_capability(
    user_uid,
    capability,
    *,
    repository=workspace_repository,
) -> str:
    """Return a Phase 4A policy decision without performing any operation."""

    requested_capability = str(capability or "").strip().lower()
    definition = CAPABILITY_DEFINITIONS.get(requested_capability)
    if definition is None:
        return _audit_decision(
            repository,
            user_uid,
            requested_capability or "<empty>",
            DENIED,
            "Unknown capability.",
        )

    if not definition.enabled:
        return _audit_decision(
            repository,
            user_uid,
            definition.name,
            DENIED,
            "Capability is disabled in Phase 4A.",
        )

    try:
        normalized_uid = str(uuid.UUID(str(user_uid or "").strip()))
    except (AttributeError, TypeError, ValueError):
        return _audit_decision(
            repository,
            user_uid,
            definition.name,
            DENIED,
            "User identity is invalid.",
        )

    identity = repository.get_workspace_user(normalized_uid)
    if not identity or not identity.get("is_active"):
        return _audit_decision(
            repository,
            normalized_uid,
            definition.name,
            DENIED,
            "User identity is unknown or inactive.",
        )

    role = normalize_security_role(identity.get("role"))
    if _ROLE_LEVEL[role] < _ROLE_LEVEL[definition.required_role]:
        reason = (
            "USER accounts are conversation-only."
            if role == USER
            else f"Capability requires the {definition.required_role.upper()} role."
        )
        return _audit_decision(
            repository,
            normalized_uid,
            definition.name,
            DENIED,
            reason,
        )

    if definition.approval_required:
        return _audit_decision(
            repository,
            normalized_uid,
            definition.name,
            REQUIRES_APPROVAL,
            "Explicit approval is required; no execution access was granted.",
        )

    return _audit_decision(
        repository,
        normalized_uid,
        definition.name,
        ALLOWED,
        "Role and capability policy requirements were satisfied.",
    )


__all__ = [
    "ALLOWED",
    "DENIED",
    "REQUIRES_APPROVAL",
    "CAPABILITY_DECISIONS",
    "CAPABILITY_DEFINITIONS",
    "CapabilityDefinition",
    "check_capability",
]
