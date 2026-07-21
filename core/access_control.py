"""
Aetheraeon AI - Access Control

Purpose:
Provides centralized role and command-permission checks used by the current API gateway.

Architecture Layer:
Security and authorization support.

Responsibilities:
- Evaluate supplied user roles against command permission metadata.
- Return predictable authorization results for server-side callers.

Boundaries:
- Authorization remains server-side and cannot be bypassed by routing, cognition, model output, or modified client requests.
- This module does not infer intent, grant roles, execute commands, or make cognitive policy decisions.
"""

VALID_ROLES = frozenset({"admin", "user"})

ADMIN_ONLY_COMMAND_INTENTS = frozenset({
    "shell",
    "status",
    "model_cmd",
    "aider_project",
})

ADMIN_ONLY_TOOLS = frozenset({
    "aider",
    "model",
    "model_cmd",
    "navigation",
    "n8n",
    "shell",
    "status",
})


def normalize_role(role):
    value = str(role or "user").strip().lower()
    # OWNER is persisted distinctly by the Phase 3 identity foundation. Map
    # it to the legacy administrative capability tier so existing command and
    # tool behavior is preserved without changing command policy.
    if value == "owner":
        return "admin"
    return value if value in VALID_ROLES else "user"


def roles_for_tool(meta):
    """Return explicit metadata roles, adding a safe default when absent."""
    metadata = meta if isinstance(meta, dict) else {}
    supplied = metadata.get("roles")
    if supplied:
        roles = [normalize_role(role) for role in supplied]
        return list(dict.fromkeys(roles))

    name = str(metadata.get("name") or "").strip().lower()
    category = str(metadata.get("category") or "").strip().lower()
    if name in ADMIN_ONLY_TOOLS or category in {"diagnostics"}:
        return ["admin"]
    return ["admin", "user"]


def role_can_use_tool(role, tool_name):
    normalized_role = normalize_role(role)
    normalized_tool = str(tool_name or "chat").strip().lower()
    return normalized_role == "admin" or normalized_tool not in ADMIN_ONLY_TOOLS


def role_can_execute_intent(role, intent):
    normalized_role = normalize_role(role)
    normalized_intent = str(intent or "").strip().lower()
    return normalized_role == "admin" or normalized_intent not in ADMIN_ONLY_COMMAND_INTENTS


def build_effective_user_context(user_id, role, source):
    """Create the minimal identity context carried to an execution boundary.

    Callers are responsible for resolving the authenticated user before using
    this helper.  The context intentionally contains no credentials or session
    secrets; it records only the identity and role already established by the
    caller.
    """

    normalized_user_id = str(user_id or "").strip()
    if not normalized_user_id:
        return None

    return {
        "user_id": normalized_user_id,
        "role": normalize_role(role),
        "source": str(source or "unknown").strip() or "unknown",
    }


def authorize_tool_execution(effective_user, tool_name):
    """Return an Access Control receipt for one proposed tool execution.

    This is the sole role-policy decision used by the execution path.  Tool
    executors consume the resulting receipt; they do not infer roles or grant
    permission for themselves.
    """

    context = effective_user if isinstance(effective_user, dict) else {}
    user_id = str(context.get("user_id") or "").strip()
    normalized_tool = str(tool_name or "").strip().lower()
    role = normalize_role(context.get("role"))
    authorized = bool(
        user_id
        and normalized_tool
        and role_can_use_tool(role, normalized_tool)
    )

    return {
        "authorized": authorized,
        "tool": normalized_tool,
        "effective_user_id": user_id or None,
        "effective_role": role,
        "reason": None if authorized else "Administrator permission is required for that tool.",
    }
