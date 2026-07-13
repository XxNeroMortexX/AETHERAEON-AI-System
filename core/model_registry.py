"""
========================================================
AETHERAEON — MODEL REGISTRY (MODEL ROUTING LAYER)
========================================================

FILE PURPOSE:
This file is the centralized model management and routing
system for the entire AI architecture.

It controls:
- Which AI model should be used
- When models should switch
- Model capability definitions
- Routing policies
- Fallback handling
- Performance-aware model selection

========================================================
SYSTEM ROLE:
"Model Intelligence Routing Layer"

This file does NOT perform reasoning itself.

It ONLY:
- Defines available models
- Selects the correct model for a task
- Returns model configuration data
- Handles model fallback policies
- Maintains routing consistency

========================================================
RESPONSIBILITIES:
(model_registry.py)

- Register all available AI models
- Define model metadata + capabilities
- Route tasks to correct model
- Handle fallback model selection
- Define local vs cloud model policies
- Store model context window limits
- Store model temperature defaults
- Define reasoning vs utility model roles
- Validate model availability
- Support future multi-model orchestration

========================================================
STRICT BOUNDARIES (DO NOT BREAK):
(model_registry.py)

This file MUST NOT:

- Call models directly (llm_interface.py handles this)
- Execute tools (tool_executor.py handles this)
- Access databases (memory_database.py handles this)
- Perform AI reasoning
- Build prompts
- Modify frontend/UI state
- Execute HTTP/API routes

This file ONLY manages model configuration + routing.

========================================================
MODEL REGISTRY INTERNAL FLOW:
(model_registry.py functions)

AI Request
    ↓
get_model_for_task()
    ↓
check_model_availability()
    ↓
apply_routing_rules()
    ↓
fallback_if_needed()
    ↓
return structured model configuration
    ↓
llm_interface.py executes model

========================================================
SYSTEM WIDE FLOW:
(full architecture flow)

User Input
    ↓
api_gateway.py
    ↓
request_router.py
    ↓
ai_orchestrator.py
    ↓
model_registry.py   ← THIS FILE
    ↓
llm_interface.py
    ↓
selected AI model executes
    ↓
tool_executor.py (if needed)
    ↓
response returned upward
    ↓
Web UI

========================================================
KEY FILE DEPENDENCIES:

model_registry.py is used by:
- ai_orchestrator.py
- llm_interface.py
- request_router.py
- tool_executor.py (optional future routing)

========================================================
CORE FUNCTIONS (THIS FILE):

- register_model()
- get_model()
- get_default_model()
- get_reasoning_model()
- get_fast_model()
- get_fallback_model()
- get_model_for_task()
- list_available_models()
- check_model_availability()

========================================================
OUTPUT CONTRACT:
(model_registry.py returns)

Structured model configuration objects:

{
    "model": str,
    "provider": str,
    "context_window": int,
    "temperature": float,
    "supports_tools": bool,
    "supports_reasoning": bool
}

========================================================
DESIGN PHILOSOPHY:

"Centralized Model Control"

- Registry defines models
- Orchestrator decides intent
- LLM Interface performs execution
- tool_executor performs actions

The registry remains:
predictable, centralized, and stateless.

========================================================
"""


# ============================================================
# CORE STANDARD LIBRARY IMPORTS
# ============================================================
# These are built-in Python modules used for:
# - String processing
# - Pattern matching
# - Timing / diagnostics
# - Lightweight utility operations
#
# This file should remain lightweight and focused on:
# - Model selection
# - Model routing
# - Model configuration management
# ============================================================

import re            # Command parsing / model command matching
import time          # Timing / debug metrics / latency tracking


# ============================================================
# EXTERNAL DEPENDENCIES (PIP INSTALLED PACKAGES)
# ============================================================
# Third-party libraries used for:
# - Ollama API communication
# - Local model discovery
# ============================================================

import requests      # HTTP requests to Ollama API endpoint

from core.tool_registry import register_tool


# ============================================================
# INTERNAL SYSTEM IMPORTS (ARCHITECTURE LAYERS)
# ============================================================
# Internal architecture dependencies required by the
# model registry / model routing layer.
#
# RULES:
# - No database imports here
# - No frontend imports
# - No orchestration imports
# - No tool execution imports
#
# This file should ONLY manage:
# - Model discovery
# - Model selection
# - Model configuration
# - Routing preferences
# ============================================================

# ------------------------------------------------------------
# CONFIGURATION MANAGEMENT LAYER
# ------------------------------------------------------------
# Handles persistent AI configuration storage.
# ------------------------------------------------------------

from core.config_manager import (
    load_settings,
    save_settings,
)

# ------------------------------------------------------------
# SYSTEM LOGGER
# ------------------------------------------------------------
# Centralized logging / debug output layer.
# ------------------------------------------------------------

from core import system_logger


# ============================================================
# OLLAMA MODEL DISCOVERY
# ============================================================
# Retrieves all locally installed Ollama models directly from
# the Ollama API server.
#
# PURPOSE:
# - Detect available local AI models
# - Populate model registry dynamically
# - Support automatic model routing
# - Prevent hardcoded model assumptions
#
# RETURNS:
# - list[str]
#   Example:
#   [
#       "llama3:8b",
#       "qwen2.5-coder:14b",
#       "mistral:7b"
#   ]
#
# FAILURE POLICY:
# - NEVER crash system startup
# - Return empty list if Ollama is offline
# - Registry layer must remain fault tolerant
# ============================================================

def ollama_models() -> list[str]:
    """
    Query the local Ollama server and return all installed models.
    """

    # ------------------------------------------------------------
    # OLLAMA API ENDPOINT
    # ------------------------------------------------------------
    # Ollama exposes installed model metadata through:
    #   GET /api/tags
    # ------------------------------------------------------------

    ollama_api_url = "http://localhost:11434/api/tags"

    try:

        # --------------------------------------------------------
        # REQUEST INSTALLED MODEL LIST
        # --------------------------------------------------------
        # Timeout kept short so startup/model checks never hang.
        # --------------------------------------------------------

        response = requests.get(
            ollama_api_url,
            timeout=5
        )

        # --------------------------------------------------------
        # VALIDATE RESPONSE STATUS
        # --------------------------------------------------------
        # Non-200 responses are treated as unavailable.
        # --------------------------------------------------------

        if response.status_code != 200:
            return []

        # --------------------------------------------------------
        # PARSE RESPONSE PAYLOAD
        # --------------------------------------------------------
        # Expected format:
        #
        # {
        #   "models": [
        #       {"name": "llama3:8b"},
        #       {"name": "qwen2.5-coder:14b"}
        #   ]
        # }
        # --------------------------------------------------------

        response_payload = response.json()

        model_entries = response_payload.get(
            "models",
            []
        ) or []

        # --------------------------------------------------------
        # EXTRACT VALID MODEL NAMES
        # --------------------------------------------------------
        # Ignore malformed entries safely.
        # --------------------------------------------------------

        installed_models = [
            model_entry.get("name")
            for model_entry in model_entries
            if model_entry.get("name")
        ]

        return installed_models

    # ------------------------------------------------------------
    # FAILURE SAFETY
    # ------------------------------------------------------------
    # Registry layer must NEVER hard crash if Ollama is offline.
    #
    # Common failure causes:
    # - Ollama not running
    # - API unavailable
    # - Connection timeout
    # - Invalid JSON
    # ------------------------------------------------------------

    except Exception:

        return []


# ============================================================
# MODEL NAME NORMALIZATION UTILITY
# ============================================================
# PURPOSE:
# Cleans and standardizes model name input strings so that
# model identifiers are consistent across the system.
#
# This prevents issues caused by:
# - extra whitespace
# - accidental quotes
# - inconsistent CLI / user input formatting
# ============================================================

def _normalize_model_name(raw_model_name: str) -> str:
    """
    Normalize model identifier strings into a clean format.

    This function ensures that model names coming from:
    - user input
    - CLI commands
    - config files
    - system prompts

    are all converted into a consistent format before being
    used by the model registry or execution layer.

    ------------------------------------------------------------
    NORMALIZATION RULES:
    ------------------------------------------------------------
    - Remove leading/trailing whitespace
    - Remove surrounding double quotes
    - Remove surrounding single quotes
    - Ensure safe empty fallback value
    ------------------------------------------------------------
    """

    # ─────────────────────────────────────────────────────────
    # 1. SAFE INPUT HANDLING
    # ─────────────────────────────────────────────────────────
    # Ensures None or empty values do not crash downstream logic
    # ─────────────────────────────────────────────────────────

    cleaned_name = raw_model_name or ""

    # ─────────────────────────────────────────────────────────
    # 2. STRING NORMALIZATION PIPELINE
    # ─────────────────────────────────────────────────────────
    # Step-by-step sanitization for consistent model naming
    # ─────────────────────────────────────────────────────────

    cleaned_name = cleaned_name.strip()        # remove whitespace
    cleaned_name = cleaned_name.strip('"')      # remove double quotes
    cleaned_name = cleaned_name.strip("'")      # remove single quotes

    # ─────────────────────────────────────────────────────────
    # 3. FINAL OUTPUT
    # ─────────────────────────────────────────────────────────
    # Return fully normalized model name string
    # ─────────────────────────────────────────────────────────

    return cleaned_name
    
    
# ============================================================
# DEFAULT MODEL AUTO-SELECTION
# ============================================================
# Purpose:
# Automatically select sensible default models from the
# locally installed Ollama model list.
#
# This function helps the system boot with usable defaults
# even before the user manually configures models.
#
# Selection priorities:
#
# - CODE MODEL:
#     Looks for coding-focused models
#     Example:
#         qwen2.5-coder
#         deepseek-coder
#
# - CHAT MODEL:
#     Looks for general conversational models
#     Example:
#         llama3
#         mistral
#         gemma
#
# - ROUTER MODEL:
#     Prefers code model first
#     Falls back to chat model
#
# NOTE:
# This function ONLY selects defaults.
# It does NOT validate performance or capabilities.
# ============================================================

def pick_default_models_from_tags(
    available_model_tags: list[str]
) -> dict:
    """
    Automatically choose default models from Ollama tags.

    Returns:
        {
            "router": str | None,
            "chat":   str | None,
            "code":   str | None
        }
    """

    # ========================================================
    # NORMALIZE MODEL TAGS
    # ========================================================
    # Ensure list exists and create lowercase copies
    # for safe case-insensitive matching.
    # ========================================================

    available_model_tags = available_model_tags or []

    lowercase_model_tags = [
        model_tag.lower()
        for model_tag in available_model_tags
    ]


    # ========================================================
    # INTERNAL MODEL MATCH HELPER
    # ========================================================
    # Finds the first model matching a rule.
    #
    # The matcher receives:
    # - original model name
    # - lowercase model name
    # ========================================================

    def find_first_matching_model(match_function):

        for original_model_name, lowercase_model_name in zip(
            available_model_tags,
            lowercase_model_tags
        ):

            if match_function(
                original_model_name,
                lowercase_model_name
            ):
                return original_model_name

        return None


    # ========================================================
    # DETECT CODE MODEL
    # ========================================================
    # Prefer models explicitly designed for coding.
    # ========================================================

    code_model = find_first_matching_model(
        lambda original_name, lowercase_name:
            "coder" in lowercase_name
            or "code" in lowercase_name
    )


    # ========================================================
    # DETECT GENERAL CHAT MODEL
    # ========================================================
    # Avoid selecting coding models for conversation.
    #
    # Prefer common general-purpose model families.
    # ========================================================

    chat_model = find_first_matching_model(
        lambda original_name, lowercase_name:
            (
                "coder" not in lowercase_name
                and "code" not in lowercase_name
            )
            and any(
                family_name in lowercase_name
                for family_name in (
                    "llama",
                    "mistral",
                    "qwen",
                    "phi",
                    "gemma"
                )
            )
    )


    # ========================================================
    # DETERMINE ROUTER MODEL
    # ========================================================
    # Router prefers strongest reasoning/code model first.
    #
    # Fallback:
    # - chat model
    # ========================================================

    router_model = (
        code_model
        or chat_model
    )


    # ========================================================
    # RETURN STRUCTURED MODEL MAP
    # ========================================================

    return {
        "router": router_model,
        "chat":   chat_model,
        "code":   code_model,
    }



# ============================================================
# MODEL COMMAND HANDLER
# ============================================================
# Centralized model-management command system.
#
# PURPOSE:
# - Manage active AI model configuration
# - Control routing models
# - Handle session overrides
# - Configure auto-model behavior
# - Display installed Ollama models
#
# RESPONSIBILITY:
# This function ONLY handles:
# - Parsing model-related commands
# - Updating configuration state
# - Updating session-level overrides
# - Returning formatted status information
#
# THIS FUNCTION DOES NOT:
# - Run inference
# - Perform AI reasoning
# - Execute tools
# - Access memory systems
#
# FILE LOCATION:
# core/model_registry.py
# ============================================================

def handle_model_command(user_input: str, session: dict):
    """
    Handle all model-management commands.

    Supported Commands:
        model show
        model list
        model use <model>
        model clear
        model auto on|off
        model process on|off
        model set chat|code|router <model>
        model preset core
        model pick defaults
    """

    # ========================================================
    # LOAD SYSTEM SETTINGS
    # ========================================================
    # Pull persistent configuration settings from the
    # centralized configuration manager.
    # ========================================================

    settings = load_settings()

    normalized_input = (user_input or "").strip()
    lowercase_input  = normalized_input.lower()

    # ========================================================
    # INTERNAL STATUS VIEW BUILDER
    # ========================================================
    # Builds a formatted system status display showing:
    # - Current active models
    # - Auto-model settings
    # - Session overrides
    # - Web-search settings
    # ========================================================

    def build_model_status_display():

        configured_models = settings.get("models", {})
        session_override  = session.get("model_override")

        web_search_settings = settings.get("web_search", {}) or {}

        status_lines = [
            "MODEL SETTINGS:",
            f"  auto_model   = {bool(settings.get('auto_model', True))}",
            f"  show_process = {bool(settings.get('show_process', True))}",
            f"  router       = {configured_models.get('router')}",
            f"  chat         = {configured_models.get('chat')}",
            f"  code         = {configured_models.get('code')}",
            f"  override     = {session_override or '(none)'}",
            (
                f"  web_search   = "
                f"{bool(web_search_settings.get('enabled', False))} "
                f"provider={web_search_settings.get('provider', 'ddg')}"
            ),
        ]

        return "\n".join(status_lines)

    # ========================================================
    # MODEL STATUS DISPLAY
    # ========================================================
    # Show currently configured model state.
    # ========================================================

    if lowercase_input in (
        "model",
        "models",
        "model show",
        "models show",
    ):

        return build_model_status_display()

    # ========================================================
    # INSTALLED MODEL LISTING
    # ========================================================
    # Query Ollama for installed local models.
    # ========================================================

    if (
        lowercase_input.startswith("model list")
        or lowercase_input.startswith("models list")
    ):

        installed_models = ollama_models()

        if not installed_models:
            return "No Ollama models found or Ollama is offline."

        output_lines = ["INSTALLED OLLAMA MODELS:"]

        for model_name in installed_models:
            output_lines.append(f"  - {model_name}")

        return "\n".join(output_lines)

    # ========================================================
    # SESSION MODEL OVERRIDE
    # ========================================================
    # Temporarily override the active model for the
    # current user session only.
    # ========================================================

    if lowercase_input.startswith("model use "):

        split_input = normalized_input.split(" ", 2)

        requested_model = (
            split_input[2]
            if len(split_input) >= 3
            else ""
        )

        normalized_model_name = _normalize_model_name(requested_model)

        if not normalized_model_name:
            return "Usage: model use <model_name>"

        session["model_override"] = normalized_model_name

        return f"Model override enabled -> {normalized_model_name}"

    # ========================================================
    # CLEAR SESSION OVERRIDE
    # ========================================================
    # Removes temporary session model override.
    # ========================================================

    if lowercase_input in (
        "model clear",
        "models clear",
        "model override clear",
    ):

        session.pop("model_override", None)

        return "Model override cleared."

    # ========================================================
    # AUTO-MODEL TOGGLE
    # ========================================================
    # Enables or disables automatic model routing.
    # ========================================================

    if lowercase_input.startswith("model auto "):

        toggle_value = lowercase_input.split()[-1]

        if toggle_value in ("on", "true", "1"):

            settings["auto_model"] = True

        elif toggle_value in ("off", "false", "0"):

            settings["auto_model"] = False

        else:
            return "Usage: model auto on|off"

        save_settings(settings)

        return f"auto_model -> {settings['auto_model']}"

    # ========================================================
    # PROCESS DISPLAY TOGGLE
    # ========================================================
    # Enables or disables process/debug visibility.
    # ========================================================

    if lowercase_input.startswith("model process "):

        toggle_value = lowercase_input.split()[-1]

        if toggle_value in ("on", "true", "1"):

            settings["show_process"] = True

        elif toggle_value in ("off", "false", "0"):

            settings["show_process"] = False

        else:
            return "Usage: model process on|off"

        save_settings(settings)

        return f"show_process -> {settings['show_process']}"

    # ========================================================
    # DIRECT MODEL ASSIGNMENT
    # ========================================================
    # Allows explicit assignment of:
    # - chat model
    # - code model
    # - router model
    # ========================================================

    model_assignment_match = re.match(
        r"model\s+set\s+(chat|code|router)\s+(.+)$",
        normalized_input,
        re.IGNORECASE,
    )

    if model_assignment_match:

        model_role = model_assignment_match.group(1).lower()

        requested_model = model_assignment_match.group(2)

        normalized_model_name = _normalize_model_name(
            requested_model
        )

        if not normalized_model_name:
            return (
                "Usage: model set "
                "chat|code|router <model_name>"
            )

        settings.setdefault("models", {})[
            model_role
        ] = normalized_model_name

        save_settings(settings)

        return (
            f"{model_role} model -> "
            f"{normalized_model_name}"
        )

    # ========================================================
    # CORE PRESET APPLICATION
    # ========================================================
    # Applies recommended production-ready model stack.
    # ========================================================

    if lowercase_input in (
        "model preset core",
        "models preset core",
        "model core",
    ):

        core_model_preset = {
            "chat":   "gpt-oss:20b",
            "code":   "qwen2.5-coder:32b",
            "router": "qwen2.5-coder:14b",
        }

        settings.setdefault("models", {}).update(
            core_model_preset
        )

        save_settings(settings)

        installed_models = ollama_models()

        response_lines = [
            "Applied CORE model preset:",
            f"  chat   -> {core_model_preset['chat']}",
            f"  code   -> {core_model_preset['code']}",
            f"  router -> {core_model_preset['router']}",
        ]

        # ----------------------------------------------------
        # Check whether required models exist locally.
        # ----------------------------------------------------

        if installed_models:

            missing_models = [
                model_name
                for model_name in core_model_preset.values()
                if model_name not in installed_models
            ]

            if missing_models:

                response_lines.append("")
                response_lines.append(
                    "Missing local Ollama models:"
                )

                for model_name in missing_models:
                    response_lines.append(
                        f"  - {model_name}"
                    )

        return "\n".join(response_lines)

    # ========================================================
    # AUTO DEFAULT MODEL PICKER
    # ========================================================
    # Automatically selects recommended models from
    # currently installed Ollama models.
    # ========================================================

    if lowercase_input in (
        "model pick defaults",
        "model defaults",
        "models defaults",
    ):

        installed_models = ollama_models()

        selected_defaults = (
            pick_default_models_from_tags(
                installed_models
            )
        )

        configuration_changed = False

        for model_role, model_name in (
            selected_defaults.items()
        ):

            if (
                model_name
                and settings["models"].get(model_role)
                != model_name
            ):

                settings["models"][model_role] = model_name

                configuration_changed = True

        if configuration_changed:

            save_settings(settings)

            return (
                "Picked recommended defaults "
                "from installed models.\n\n"
                + build_model_status_display()
            )

        return (
            "Defaults unchanged "
            "(or no models found).\n\n"
            + build_model_status_display()
        )

    # ========================================================
    # HELP FALLBACK
    # ========================================================
    # Returned when no valid model command matched.
    # ========================================================

    return (
        "MODEL COMMANDS:\n"
        "\n"
        "  model show\n"
        "  model list\n"
        "  model use <name>\n"
        "  model clear\n"
        "  model auto on|off\n"
        "  model process on|off\n"
        "  model set chat|code|router <name>\n"
        "  model preset core\n"
        "  model pick defaults"
    )


TOOL_META = {
    "name": "model",
    "category": "models",
    "description": "Shows and updates the existing Ollama model routing settings.",
    "usage": (
        "model show|list|clear | model use <name> | model auto on|off | "
        "model process on|off | model set chat|code|router <name> | "
        "model preset core | model pick defaults"
    ),
    "examples": [
        "model show",
        "model list",
        "model use qwen2.5-coder:14b",
        "model set chat qwen2.5:14b",
    ],
    "options": [
        "show",
        "list",
        "use <name>",
        "clear",
        "auto on|off",
        "process on|off",
        "set chat|code|router <name>",
        "preset core",
        "pick defaults",
    ],
    "confirmation_required": False,
}

register_tool(TOOL_META, handle_model_command)
