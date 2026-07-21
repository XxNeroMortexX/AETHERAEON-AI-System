"""Ownership policy for personality traits.

Traits are personality configuration, not memories.  This policy is separate
from CDE and tool Access Control and does not grant tool or memory authority.
"""

USER = "user"
AETHERAEON = "aetheraeon"


def trait_operation_allowed(actor: str, owner: str, operation: str) -> bool:
    actor = str(actor or "").lower()
    owner = str(owner or "").lower()
    operation = str(operation or "").lower()

    if actor == USER:
        if operation == "create":
            return owner == USER
        if operation == "edit":
            return owner == USER
        if operation == "delete":
            return owner in {USER, AETHERAEON}
        if operation == "correct":
            return owner == AETHERAEON
        return operation == "view" and owner in {USER, AETHERAEON}

    if actor == AETHERAEON:
        if operation in {"create", "edit", "delete"}:
            return owner == AETHERAEON
        return operation == "view" and owner == AETHERAEON

    return False


def require_trait_operation(actor: str, owner: str, operation: str) -> None:
    if not trait_operation_allowed(actor, owner, operation):
        raise PermissionError(
            f"{actor or 'unknown'} cannot {operation} a {owner or 'unknown'} trait"
        )
