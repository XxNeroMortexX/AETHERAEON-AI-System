"""Canonical persisted roles for the Phase 3 security foundation."""

OWNER = "owner"
ADMIN = "admin"
USER = "user"

VALID_ROLES = frozenset({OWNER, ADMIN, USER})
ADMINISTRATIVE_ROLES = frozenset({OWNER, ADMIN})


def normalize_security_role(role) -> str:
    """Normalize stored role data and fail closed to USER."""

    normalized = str(role or USER).strip().lower()
    return normalized if normalized in VALID_ROLES else USER


def is_administrative_role(role) -> bool:
    return normalize_security_role(role) in ADMINISTRATIVE_ROLES


def can_manage_workspace_permissions(role) -> bool:
    """Only OWNER may manage future workspace ACL records."""

    return normalize_security_role(role) == OWNER


def can_assign_role(actor_role, requested_role) -> bool:
    """Describe role-assignment policy without exposing a mutation surface."""

    actor = normalize_security_role(actor_role)
    requested_value = str(requested_role or "").strip().lower()
    if requested_value not in VALID_ROLES:
        return False
    requested = normalize_security_role(requested_value)
    if requested == OWNER:
        return False
    return actor == OWNER and requested in {ADMIN, USER}
