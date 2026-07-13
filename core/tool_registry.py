# ============================================================
# TOOL REGISTRY (SOURCE OF TRUTH FOR ALL COMMANDS)
# ============================================================

REGISTERED_TOOLS = []


def register_tool(meta, handler):
    """
    Registers a tool into the system.
    meta = TOOL_META dictionary
    handler = actual python function
    """

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


def get_tools():
    """Returns all registered tools"""
    return REGISTERED_TOOLS


def find_tool(name):
    """Find tool by name"""
    for t in REGISTERED_TOOLS:
        if t["meta"]["name"] == name:
            return t
    return None
