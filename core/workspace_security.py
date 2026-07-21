"""Isolated workspace and permission-checking foundation.

This module creates directories and evaluates future ACLs. It does not open,
modify, delete, or execute user files and is not connected to agent tools.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import os
from pathlib import Path
import uuid

from core.security_roles import ADMIN, OWNER, USER, can_manage_workspace_permissions
from core.security_roles import normalize_security_role
from database import workspace_security_repository as workspace_repository


WORKSPACE_FOLDERS = ("workspace", "documents", "projects", "ai_files", "uploads")
PERMISSION_TYPES = frozenset({"read", "write", "delete", "execute"})


@dataclass(frozen=True)
class WorkspaceAuditEvent:
    """Unpersisted shape reserved for future workspace-action auditing."""

    user_uid: str
    action: str
    path: str
    time: datetime
    result: str

    @classmethod
    def create(cls, user_uid, action, path, result):
        return cls(
            user_uid=str(user_uid),
            action=str(action),
            path=str(path),
            time=datetime.now(timezone.utc),
            result=str(result),
        )


def _normalized_uid(user_uid) -> str:
    return str(uuid.UUID(str(user_uid or "").strip()))


def _is_within(path: Path, boundary: Path) -> bool:
    try:
        return os.path.commonpath((
            os.path.normcase(str(path)),
            os.path.normcase(str(boundary)),
        )) == os.path.normcase(str(boundary))
    except (ValueError, OSError):
        return False


def provision_user_workspace(user_uid, base_path=None) -> Path:
    """Create one UUID-scoped workspace tree without touching user files."""

    normalized_uid = _normalized_uid(user_uid)
    base = Path(base_path or workspace_repository.USER_WORKSPACES_PATH).resolve()
    base.mkdir(parents=True, exist_ok=True)
    user_root = (base / normalized_uid).resolve()
    if not _is_within(user_root, base) or user_root == base:
        raise ValueError("User workspace path escaped the configured base")
    user_root.mkdir(mode=0o700, exist_ok=True)
    for folder_name in WORKSPACE_FOLDERS:
        folder = (user_root / folder_name).resolve()
        if not _is_within(folder, user_root):
            raise ValueError("Workspace folder escaped the user boundary")
        folder.mkdir(mode=0o700, exist_ok=True)
    return user_root


def provision_user_foundation(user_uid, base_path=None) -> Path:
    """Provision a new account's directories and default dormant ACL."""

    user_root = provision_user_workspace(user_uid, base_path)
    workspace_repository.ensure_default_workspace_permission(
        user_uid,
        base_path=base_path,
    )
    return user_root


def ensure_workspace_foundation(base_path=None) -> list[dict]:
    """Run additive schema/role migration and backfill every workspace."""

    users = workspace_repository.ensure_workspace_security_schema(base_path)
    for user in users:
        provision_user_workspace(user["user_uid"], base_path)
    return users


def check_permission(
    user_uid,
    path,
    permission_type,
    *,
    repository=workspace_repository,
    base_path=None,
) -> bool:
    """Evaluate a dormant workspace ACL without performing an operation."""

    requested_permission = str(permission_type or "").strip().lower()
    if requested_permission not in PERMISSION_TYPES:
        return False
    try:
        normalized_uid = _normalized_uid(user_uid)
        requested_path = Path(path)
        if not requested_path.is_absolute():
            return False
        requested_path = requested_path.resolve()
    except (TypeError, ValueError, OSError):
        return False

    identity = repository.get_workspace_user(normalized_uid)
    if not identity or not identity.get("is_active"):
        return False
    role = normalize_security_role(identity.get("role"))
    users_base = Path(base_path or workspace_repository.USER_WORKSPACES_PATH).resolve()
    own_root = (users_base / normalized_uid).resolve()
    if role == USER and not _is_within(requested_path, own_root):
        return False
    if role == ADMIN and not _is_within(requested_path, users_base):
        return False
    if role not in {OWNER, ADMIN, USER}:
        return False

    matches = []
    for permission in repository.list_workspace_permissions(normalized_uid):
        try:
            permission_root = Path(permission.get("path") or "").resolve()
        except (TypeError, ValueError, OSError):
            continue
        if _is_within(requested_path, permission_root):
            matches.append((len(permission_root.parts), permission))
    if not matches:
        return False
    _specificity, selected = max(matches, key=lambda item: item[0])
    return selected.get(requested_permission) in (1, True, "1")


__all__ = [
    "WORKSPACE_FOLDERS",
    "PERMISSION_TYPES",
    "WorkspaceAuditEvent",
    "provision_user_workspace",
    "provision_user_foundation",
    "ensure_workspace_foundation",
    "check_permission",
    "can_manage_workspace_permissions",
]
