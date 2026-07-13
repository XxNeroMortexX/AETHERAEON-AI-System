"""
========================================================
AETHERAEON — HELP SYSTEM (Knowledge & Documentation Layer)
========================================================

FILE PURPOSE:
This file is responsible for generating dynamic help,
documentation, and tool usage guidance for the AI system.

It converts registered tools, metadata, and system
capabilities into structured help output for both:
- the AI model
- the user interface
- developer debugging tools

========================================================
SYSTEM ROLE:
"Knowledge + Documentation Layer" of the architecture.

It does NOT execute tools.
It does NOT make AI decisions.

It ONLY explains system capabilities.

========================================================
RESPONSIBILITIES:
(help_system.py)

- Read tool registry metadata (tool_registry)
- Generate dynamic help text / structured help output
- Build usage examples for tools
- Summarize system capabilities for AI context
- Provide tool descriptions for model prompting
- Support debugging and developer introspection

========================================================
STRICT BOUNDARIES (DO NOT BREAK):
(help_system.py)

This file MUST NOT:
- Execute tools or commands (tool_executor.py handles this)
- Perform AI reasoning (ai_orchestrator.py handles this)
- Access or modify memory database
- Modify system state or configuration
- Perform external API calls

It ONLY formats and organizes help data.

========================================================
HELP SYSTEM FLOW:
(help_system.py functions)

Tool Registry Input
    ↓
load_tools_metadata()
    ↓
parse_tool_definitions()
    ↓
build_tool_descriptions()
    ↓
format_help_output()
    ↓
return structured help object

========================================================
SYSTEM WIDE FLOW:
(full architecture integration)

User / AI Request
    ↓
request_router.py
    ↓
ai_orchestrator.py
    ↓
tool_executor.py
    ↓
external_toolkit.py
    ↓
memory_database.py
    ↓
model_registry.py
    ↓
help_system.py (ONLY when help is requested)
    ↓
UI / Debug Output

========================================================
KEY FILE DEPENDENCIES:

help_system.py depends on:
- tool_registry (source of all tool metadata)
- tool_executor (for execution context reference only)
- json_helpers.py (formatting structured help output)

========================================================
CORE FUNCTIONS (THIS FILE):

- build_help()
- format_tool_help()
- get_tool_descriptions()
- generate_usage_examples()
- summarize_system_tools()

========================================================
OUTPUT CONTRACT:
(help_system.py returns)

- help_text (string OR structured JSON)
- tool_list (optional structured metadata)
- examples (optional usage examples)

========================================================
DESIGN PHILOSOPHY:

"Explain the system without controlling it"

- Help System DESCRIBES
- Orchestrator DECIDES
- tool_executor EXECUTES
- Registry DEFINES
- UI DISPLAYS

========================================================
"""


# ============================================================
# CORE STANDARD LIBRARY IMPORTS
# ============================================================
# These are built-in Python modules used for formatting,
# string manipulation, and structured output generation.
# ============================================================

import json          # Used for optional structured help output
import re            # Pattern matching for formatting / cleanup (future use)

from core.tool_registry import register_tool


# ============================================================
# EXTERNAL DEPENDENCIES (PIP INSTALLED PACKAGES)
# ============================================================
# NOTE:
# help_system.py is a PURE formatting + documentation layer.
# It does NOT require external dependencies.
# ============================================================

# (No external dependencies required for this module)


# ============================================================
# INTERNAL SYSTEM IMPORTS (ARCHITECTURE LAYERS)
# ============================================================
# This module is responsible for generating dynamic help
# output from the tool registry system.
#
# RULES:
# - ONLY reads tool metadata
# - NEVER executes tools
# - NEVER modifies system state
# ============================================================

# ------------------------------------------------------------
# TOOL SYSTEM DEPENDENCY
# ------------------------------------------------------------
# Required source of truth for all tool definitions.
# help_system builds output from this registry structure.
# ------------------------------------------------------------

# (Expected input comes from tool_registry.py)
# from core.tool_registry import TOOL_META  # or registry getter


# ============================================================
# TOOL METADATA
# ============================================================

## TOOL_META = [
##     {
##         "name": "memory add",
##         "category": "memory",
##         "system_layer": "memory",
##         "description": "Stores information into long-term memory.",
##         "usage": "memory add <text>",
##         "parameters": {
##             "type": "string",
##             "required": True
##         },
##         "return_type": "action",
##         "examples": [
##             "memory add my name is James",
##             "remember favorite color = blue"
##         ],
##         "aliases": [
##             "remember",
##             "save memory"
##         ]
##     }
## ]



# ============================================================
# HELP SYSTEM (DYNAMIC TOOL DOCUMENTATION BUILDER)
# ============================================================
# 2–4 Header Style:
# - Purpose
# - Flow
# - Output Contract
# ============================================================

def build_help(tool_registry: list) -> dict:
    """
    PURPOSE:
    Builds structured help documentation from the tool registry.

    FLOW:
    Tool Registry → Extract Metadata → Group by Category → Format Output

    OUTPUT:
    {
        "category_name": [tool_meta, tool_meta, ...]
    }
    """

    # ============================================================
    # STEP 1: INITIALIZE CATEGORY GROUPING CONTAINER
    # ============================================================
    # This dictionary will hold tools organized by category.
    # Example:
    # {
    #   "memory": [...],
    #   "system": [...]
    # }
    # ============================================================

    grouped_tools = {}

    # ============================================================
    # STEP 2: ITERATE THROUGH REGISTERED TOOLS
    # ============================================================
    # Extract metadata safely and assign each tool into its category.
    # ============================================================

    for tool_entry in tool_registry:

        # Safely extract metadata (prevents crash if structure changes)
        meta = tool_entry.get("meta", {})

        # Normalize category (fallback to "general")
        category = meta.get("category") or "general"

        # Initialize category bucket if it doesn't exist
        if category not in grouped_tools:
            grouped_tools[category] = []

        # Append tool metadata into correct category
        grouped_tools[category].append(meta)

    # ============================================================
    # STEP 3: FORMAT FINAL HELP OUTPUT
    # ============================================================
    # Delegates rendering to a formatting layer
    # (keeps logic separated from presentation)
    # ============================================================

    return format_help_output(grouped_tools)


# ============================================================
# HELP SYSTEM (UI FORMATTER)
# ============================================================
# Purpose:
# Converts grouped tool metadata into a readable help document.
#
# Input:
# {
#   "category": [tool_meta, tool_meta]
# }
#
# Output:
# formatted string for UI / console display
# ============================================================

def format_help_output(grouped_tools: dict) -> str:

    # ============================================================
    # STEP 1: INITIALIZE OUTPUT BUFFER
    # ============================================================
    # We build a list for performance (faster than string concat)
    # ============================================================

    output_lines = []

    # System header
    output_lines.append("AETHERAEON COMMAND REFERENCE")
    output_lines.append("")  # spacing

    # ============================================================
    # STEP 2: ITERATE THROUGH CATEGORIES
    # ============================================================

    for category_name in sorted(grouped_tools):

        tool_list = grouped_tools[category_name]

        # --------------------------------------------------------
        # CATEGORY HEADER
        # --------------------------------------------------------

        output_lines.append(f"[{category_name.upper()}]")
        output_lines.append("")  # spacing under category

        # ========================================================
        # STEP 3: FORMAT EACH TOOL ENTRY
        # ========================================================

        for tool_meta in sorted(
            tool_list,
            key=lambda item: str(item.get("name", "")),
        ):

            tool_name = tool_meta.get("name", "unknown")
            description = tool_meta.get("description", "")
            usage = tool_meta.get("usage", "")
            examples = tool_meta.get("examples", [])
            options = tool_meta.get("options")
            confirmation_required = tool_meta.get(
                "confirmation_required"
            )

            # ----------------------------------------------------
            # TOOL NAME
            # ----------------------------------------------------

            output_lines.append(f"- {tool_name}")

            # ----------------------------------------------------
            # TOOL DESCRIPTION
            # ----------------------------------------------------

            if description:
                output_lines.append(f"  {description}")

            # ----------------------------------------------------
            # TOOL USAGE
            # ----------------------------------------------------

            if usage:
                output_lines.append(f"  usage: {usage}")

            if examples:
                if isinstance(examples, str):
                    examples = [examples]
                output_lines.append("  examples:")
                output_lines.extend(
                    f"    - {example}"
                    for example in examples
                )

            if options:
                output_lines.append("  options:")
                if isinstance(options, dict):
                    output_lines.extend(
                        f"    - {option}: {details}"
                        for option, details in options.items()
                    )
                elif isinstance(options, (list, tuple, set)):
                    output_lines.extend(
                        f"    - {option}"
                        for option in options
                    )
                else:
                    output_lines.append(f"    - {options}")

            if confirmation_required is not None:
                if isinstance(confirmation_required, bool):
                    confirmation_text = (
                        "yes" if confirmation_required else "no"
                    )
                else:
                    confirmation_text = str(confirmation_required)
                output_lines.append(
                    f"  confirmation required: {confirmation_text}"
                )

            # Spacer between tools
            output_lines.append("")

    # ============================================================
    # STEP 4: RETURN FINAL HELP STRING
    # ============================================================

    return "\n".join(output_lines)


TOOL_META = {
    "name": "help",
    "category": "system",
    "description": "Shows the dynamically registered command reference.",
    "usage": "help",
    "examples": ["help", "commands", "what can you do"],
    "confirmation_required": False,
}

register_tool(TOOL_META, build_help)
