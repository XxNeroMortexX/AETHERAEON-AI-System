"""
Aetheraeon AI - Tool Registry

Purpose:
Maintains the current catalog of registered tools and their descriptive metadata.

Architecture Layer:
Tool Execution Layer - tool directory.

Responsibilities:
- Register tool definitions, handlers, parameters, and help metadata.
- Provide predictable lookup and discovery information to authorized callers.
- Support help, routing, orchestration, and execution components with tool metadata.

Boundaries:
- Registry metadata does not select, authorize, or execute a tool.
- Security and permission checks remain authoritative at their established boundaries.
- The planned Cognitive Decision Engine may consume registry information but is not implemented by this module.
"""

# ============================================================
# TOOL REGISTRY (SOURCE OF TRUTH FOR ALL COMMANDS)
# ============================================================

REGISTERED_TOOLS = []

from core.access_control import normalize_role, roles_for_tool


def _future_role_labels(current_roles):
    """Build descriptive future-role metadata without changing authorization."""

    labels = ["Owner"]
    if "admin" in current_roles:
        labels.append("Admin")
    if "user" in current_roles:
        labels.append("User")
    return labels


def register_tool(meta, handler):
    """
    Registers a tool into the system.
    meta = TOOL_META dictionary
    handler = actual python function
    """

    if isinstance(meta, dict):
        meta = dict(meta)
        meta["roles"] = roles_for_tool(meta)
        meta.setdefault("type", meta.get("category") or meta.get("name"))
        meta.setdefault(
            "requires_confirmation",
            meta.get("confirmation_required", False),
        )
        meta.setdefault("allowed_roles", _future_role_labels(meta["roles"]))
    tool_name = meta.get("name") if isinstance(meta, dict) else None

    for registered_tool in REGISTERED_TOOLS:
        if registered_tool.get("meta", {}).get("name") == tool_name:
            registered_tool["meta"] = meta
            registered_tool["handler"] = handler
            return

    REGISTERED_TOOLS.append({
        "meta": meta,
        "handler": handler
    })


def get_tools(role=None):
    """Return registered tools, optionally filtered for one user role."""
    if role is None:
        return REGISTERED_TOOLS
    normalized_role = normalize_role(role)
    return [
        tool for tool in REGISTERED_TOOLS
        if normalized_role in tool.get("meta", {}).get("roles", ["admin", "user"])
    ]


def find_tool(name):
    """Find tool by name"""
    for t in REGISTERED_TOOLS:
        if t["meta"]["name"] == name:
            return t
    return None
