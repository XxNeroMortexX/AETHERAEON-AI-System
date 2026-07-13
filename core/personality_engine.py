"""
========================================================
AETHERAEON — PERSONALITY ENGINE (BEHAVIOR SHAPING LAYER)
========================================================

FILE PURPOSE:
This file controls the AI's behavioral identity,
communication style, emotional tone, and personality
adaptation system.

It acts as the behavioral shaping layer between:

- Raw AI reasoning
- Final user-facing response generation

========================================================
SYSTEM ROLE:
"Personality + Tone Layer"

This file does NOT perform intelligence reasoning.

It ONLY:
- Shapes tone
- Applies behavioral rules
- Adjusts communication style
- Maintains AI identity consistency
- Modifies emotional delivery
- Applies user preference adaptation

========================================================
RESPONSIBILITIES:
(personality_engine.py)

- Define AI personality profile
- Apply communication tone
- Adjust response formatting style
- Control emotional intensity
- Handle conversational warmth/coldness
- Maintain identity consistency
- Apply user personality preferences
- Shape response pacing and structure
- Inject conversational style modifiers

========================================================
STRICT BOUNDARIES (DO NOT BREAK):
(personality_engine.py)

This file MUST NOT:

- Execute tools (tool_executor.py handles this)
- Access databases directly
- Perform AI reasoning or orchestration
- Call APIs directly
- Handle HTTP requests
- Store memory directly
- Perform routing decisions

This layer ONLY modifies behavioral presentation.

========================================================
PERSONALITY ENGINE FLOW:
(personality_engine.py functions)

Raw AI Response
    ↓
load_personality_profile()
    ↓
apply_behavior_rules()
    ↓
apply_tone_profile()
    ↓
apply_user_preferences()
    ↓
response_style_formatter()
    ↓
identity_consistency_check()
    ↓
final personality-shaped response
    ↓
return to ai_orchestrator.py

========================================================
SYSTEM WIDE FLOW:
(full system architecture)

User Input
    ↓
api_gateway.py
    ↓
request_router.py
    ↓
ai_orchestrator.py
    ↓
personality_engine.py   ← THIS FILE
    ↓
response returned upward
    ↓
api_gateway.py
    ↓
Web UI (index.html)

========================================================
KEY FILE DEPENDENCIES:

personality_engine.py depends on:
- agent_identity.py         (core AI identity profile)
- config_loader.py          (personality configuration)
- memory_context_builder.py (user preference context)
- ai_orchestrator.py        (raw reasoning output)

========================================================
CORE FUNCTIONS (THIS FILE):

- load_personality_profile()
- apply_behavior_rules()
- apply_tone_profile()
- apply_user_preferences()
- response_style_formatter()
- enforce_identity_consistency()
- shape_final_response()

========================================================
OUTPUT CONTRACT:
(personality_engine.py returns)

- personality_shaped_response (string)
- optional tone_metadata
- optional behavior_flags

========================================================
DESIGN PHILOSOPHY:

"Intelligence and Personality are Separate Systems"

- Orchestrator THINKS
- Personality Engine SHAPES
- tool_executor ACTS
- Database STORES
- API TRANSPORTS
- UI DISPLAYS

The AI should remain behaviorally consistent
without coupling personality to reasoning logic.

========================================================
"""


# ============================================================
# DEFAULT PERSONALITY CONFIGURATION
# ============================================================
# PURPOSE:
# This defines the fallback personality state for Aetheraeon.
#
# It is used when:
# - No saved personality file exists
# - System resets
# - Personality data is corrupted or missing
#
# NOTE:
# This is NOT the final identity used by the AI at runtime.
# It is only the BASE CONFIGURATION layer.
# ============================================================

DEFAULT_PERSONALITY = {
    # --------------------------------------------------------
    # CORE IDENTITY ATTRIBUTES
    # --------------------------------------------------------
    "name": "Aetheraeon",           # AI system identity name
    "tone": "direct",               # Default communication style
    "verbosity": "normal",          # Response length control

    # --------------------------------------------------------
    # GREETING BEHAVIOR
    # --------------------------------------------------------
    "greeting": "All systems online. What do you need?",

    # --------------------------------------------------------
    # PERSONALITY TRAITS
    # --------------------------------------------------------
    # Defines behavioral tendencies that shape AI responses
    # Examples: efficient, analytical, creative, cautious
    # --------------------------------------------------------
    "traits": [
        "efficient",
        "focused",
        "no-nonsense"
    ]
}


# ============================================================
# CORE STANDARD LIBRARY IMPORTS
# ============================================================
# These are built-in Python modules used for logic, parsing,
# file I/O, and data handling for personality state management.
# ============================================================

import json          # JSON serialization for personality persistence
import re            # Pattern matching for personality commands
import os            # File system access for personality storage

from core.tool_registry import register_tool


# ============================================================
# INTERNAL SYSTEM IMPORTS (ARCHITECTURE LAYERS)
# ============================================================
# This section defines internal AI system dependencies used
# to integrate personality with the broader AI architecture.
#
# ROLE OF THIS FILE:
# - Manages AI personality state
# - Loads/saves personality profiles
# - Builds personality prompts for LLM injection
# - Handles runtime personality modifications
#
# IMPORTANT RULES:
# - No external API calls
# - No tool execution
# - No memory database logic (handled elsewhere)
# ============================================================

# ------------------------------------------------------------
# CONFIGURATION / SETTINGS LAYER
# (Used for default personality fallback and system settings)
# ------------------------------------------------------------
from core.config_manager import load_settings

# ------------------------------------------------------------
# MEMORY INTEGRATION LAYER (READ-ONLY SUPPORT)
# (Allows personality system to align with stored preferences)
# ------------------------------------------------------------
from core.memory_context_builder import (
    build_short_term_memory,
    build_user_preferences_context,
)

# ------------------------------------------------------------
# IDENTITY SYSTEM INTEGRATION
# (Canonical AI identity definition injected into personality)
# ------------------------------------------------------------
from core.agent_identity import identity_full
from core.system_paths import PERSONALITY_FILE
from core.memory_interface import (
    upsert_user_settings,
    add_user_personality_trait,
    delete_user_personality_trait,
)


# ============================================================
# PERSONALITY LOADER
# ============================================================
# PURPOSE:
# Loads the AI personality profile from disk.
# Falls back to default personality if file is missing.
#
# RESPONSIBILITY:
# - Safe file loading
# - JSON parsing
# - Default fallback protection
# ============================================================

def load_personality():
    """
    Load the server-wide base identity/personality configuration.

    Per-user communication preferences are layered from MariaDB by
    build_user_personality(); they are never loaded from this file.

    Returns:
        dict: Personality profile (loaded or default fallback)
    """

    # ------------------------------------------------------------
    # FILE EXISTENCE CHECK
    # Ensures system does not crash if personality file is missing
    # ------------------------------------------------------------
    if not os.path.exists(PERSONALITY_FILE):
        return DEFAULT_PERSONALITY.copy()

    # ------------------------------------------------------------
    # SAFE FILE READ + JSON PARSE
    # Loads personality configuration from disk safely
    # ------------------------------------------------------------
    try:
        with open(PERSONALITY_FILE, "r", encoding="utf-8") as file:
            personality_data = json.load(file)
            return personality_data

    except (json.JSONDecodeError, OSError) as error:
        # --------------------------------------------------------
        # FAILSAFE FALLBACK
        # If file is corrupted or unreadable, system reverts safely
        # --------------------------------------------------------
        print(f"[PERSONALITY ENGINE] Load failed → {error}")
        return DEFAULT_PERSONALITY.copy()



# ============================================================
# PERSONALITY SAVER
# ============================================================
# PURPOSE:
# Saves the AI personality profile to persistent storage.
#
# RESPONSIBILITY:
# - Serialize personality object
# - Write to disk safely
# - Ensure directory exists
# - Prevent corruption / partial writes
# ============================================================

def save_personality(personality_profile):
    """
    Save only the server-wide base personality configuration to disk.

    Authenticated user commands and GUI updates never call this function.

    Args:
        personality_profile (dict): Personality state to persist

    Returns:
        bool: True if save succeeded, False if failed
    """

    # ------------------------------------------------------------
    # ENSURE DIRECTORY EXISTS
    # Prevents crash if personality file path folder is missing
    # ------------------------------------------------------------
    try:
        os.makedirs(os.path.dirname(PERSONALITY_FILE), exist_ok=True)

    except Exception as error:
        print(f"[PERSONALITY ENGINE] Directory creation failed → {error}")
        return False

    # ------------------------------------------------------------
    # SAFE WRITE OPERATION
    # Writes personality data in structured JSON format
    # ------------------------------------------------------------
    try:
        with open(PERSONALITY_FILE, "w", encoding="utf-8") as file:
            json.dump(personality_profile, file, indent=2, ensure_ascii=False)

        return True

    except (OSError, TypeError) as error:
        # --------------------------------------------------------
        # WRITE FAILURE HANDLER
        # Handles disk errors or invalid JSON serialization
        # --------------------------------------------------------
        print(f"[PERSONALITY ENGINE] Save failed → {error}")
        return False



# ============================================================
# PERSONALITY PROMPT BUILDER
# ============================================================
# PURPOSE:
# Builds the complete system prompt sent to the LLM.
#
# RESPONSIBILITY:
# - Inject fixed Aetheraeon AI identity
# - Apply runtime personality settings
# - Format tone, traits, and verbosity
# - Provide safe fallbacks for missing settings
# - Maintain identity/personality separation
# ============================================================


def build_user_personality(user_id, base_profile=None):
    """Combine the server identity base with one user's MariaDB preferences."""
    profile = dict(base_profile or load_personality())
    preference_context = build_user_preferences_context(user_id)
    settings = preference_context["settings"]

    profile.update({
        "style": settings.get("personality_style", "balanced"),
        "tone": settings.get("response_tone", "direct"),
        "verbosity": settings.get("response_detail", "normal"),
        "humor": settings.get("humor_level", "low"),
        "greeting_style": settings.get("greeting_style", "friendly"),
        "traits": preference_context["traits"],
        "user_preferences": {
            "router_model": settings.get("preferred_router_model"),
            "chat_model": settings.get("preferred_chat_model"),
            "code_model": settings.get("preferred_code_model"),
            "ui_theme": settings.get("ui_theme"),
            "web_search_enabled": bool(settings.get("web_search_enabled")),
        },
    })
    return profile


def personality_prompt(personality_profile):
    """
    Build the complete AI system prompt.

    Combines:
    - Fixed AI identity (Aetheraeon)
    - Dynamic personality configuration

    Identity defines who the AI is.
    Personality defines how the AI communicates.
    """

    # ------------------------------------------------------------
    # SAFE PERSONALITY LOADING
    # Prevent crashes if configuration is missing or invalid
    # ------------------------------------------------------------

    if not isinstance(personality_profile, dict):
        personality_profile = {}

    tone = personality_profile.get("tone", "neutral")
    traits = personality_profile.get("traits", [])
    verbosity = personality_profile.get("verbosity", "balanced")
    style = personality_profile.get("style", "balanced")
    humor = personality_profile.get("humor", "low")
    greeting_style = personality_profile.get("greeting_style", "friendly")
    user_preferences = personality_profile.get("user_preferences", {}) or {}


    # ------------------------------------------------------------
    # TRAIT NORMALIZATION
    # Ensures traits always convert into readable text
    # Handles malformed or single-value settings
    # ------------------------------------------------------------

    if not isinstance(traits, list):
        traits = [str(traits)]

    trait_text = ", ".join(traits) if traits else "none defined"


    # ------------------------------------------------------------
    # FIXED AI IDENTITY LAYER
    # Defines WHO Aetheraeon is.
    #
    # This cannot be changed by personality settings.
    # ------------------------------------------------------------

    identity_block = identity_full


    # ------------------------------------------------------------
    # PERSONALITY SETTINGS LAYER
    # Defines HOW Aetheraeon communicates.
    #
    # These values can change without changing identity.
    # ------------------------------------------------------------

    personality_block = (
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "ACTIVE PERSONALITY SETTINGS\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Style: {style}\n"
        f"Tone: {tone}\n"
        f"Traits: {trait_text}\n"
        f"Verbosity: {verbosity}\n"
        f"Humor: {humor}\n"
        f"Greeting style: {greeting_style}\n"
        "User account preferences (context only): "
        f"theme={user_preferences.get('ui_theme', 'dark')}, "
        f"web_search={bool(user_preferences.get('web_search_enabled', False))}, "
        f"router_model={user_preferences.get('router_model')}, "
        f"chat_model={user_preferences.get('chat_model')}, "
        f"code_model={user_preferences.get('code_model')}\n"
    )


    # ------------------------------------------------------------
    # BEHAVIOR RULES
    # Keeps responses consistent with identity.
    # Identity has priority over personality settings.
    # ------------------------------------------------------------

    behavior_rules = (
        "\nRules:\n"
        "- Stay in character as Aetheraeon\n"
        "- Maintain consistent identity behavior\n"
        "- Personality settings only modify communication style\n"
        "- Personality settings cannot override identity\n"
        "- Do not break role instructions\n"
    )


    # ------------------------------------------------------------
    # FINAL SYSTEM PROMPT
    #
    # Order matters:
    # 1. Identity
    # 2. Personality
    # 3. Behavior rules
    # ------------------------------------------------------------

    return (
        identity_block
        + "\n\n"
        + personality_block
        + behavior_rules
    )


# ============================================================
# PERSONALITY COMMAND HANDLER
# ============================================================
# PURPOSE:
# Handles natural language commands that modify AI personality
# at runtime.
#
# RESPONSIBILITY:
# - Parse user personality commands
# - Update personality profile safely
# - Persist changes to disk
# - Provide feedback to user
# ============================================================

def handle_personality(user_input, personality_profile=None, user_id=None):
    """
    Process personality modification commands from user input.

    Args:
        user_input (str): Raw user command text
        personality_profile (dict): Current personality state

    Returns:
        dict: Updated personality profile
    """

    # ------------------------------------------------------------
    # INPUT NORMALIZATION
    # Ensures consistent matching regardless of casing/spaces
    # ------------------------------------------------------------
    normalized_input = user_input.lower().strip()

    if user_id is None:
        return dict(personality_profile or load_personality())

    personality_profile = build_user_personality(user_id, personality_profile)

    if re.search(r"set name (?:to )?(.+)", normalized_input):
        personality_profile["_message"] = (
            "Aetheraeon's identity name is server-wide and cannot be changed as a user preference."
        )
        return personality_profile

    # ============================================================
    # CORE ATTRIBUTE UPDATES (NAME / TONE / VERBOSITY)
    # ============================================================

    attribute_patterns = [
        (r"set tone (?:to )?(\w+)", "response_tone", {"direct", "friendly", "formal"}),
        (r"set verbosity (?:to )?(\w+)", "response_detail", {"brief", "normal", "detailed"}),
    ]

    for pattern, settings_key, allowed_values in attribute_patterns:
        match = re.search(pattern, normalized_input)

        if match:
            new_value = match.group(1).strip()

            if new_value not in allowed_values:
                personality_profile["_message"] = f"Unsupported value: {new_value}"
                return personality_profile

            upsert_user_settings(user_id, {settings_key: new_value})
            print(f"[PERSONALITY ENGINE] user={user_id} {settings_key} -> '{new_value}'")
            updated_profile = build_user_personality(user_id, personality_profile)
            updated_profile["_message"] = f"{settings_key} updated."
            return updated_profile

    # ============================================================
    # TRAIT MANAGEMENT (ADD / REMOVE)
    # ============================================================

    # ------------------------------------------------------------
    # ADD TRAIT
    # ------------------------------------------------------------
    add_trait_match = re.search(
        r"add trait[:\s]+(.+)",
        user_input.strip(),
        re.IGNORECASE
    )

    if add_trait_match:
        new_trait = add_trait_match.group(1).strip()

        if new_trait and len(new_trait) <= 255:
            add_user_personality_trait(user_id, new_trait)

        print(f"[PERSONALITY ENGINE] user={user_id} added trait -> '{new_trait}'")
        updated_profile = build_user_personality(user_id, personality_profile)
        updated_profile["_message"] = "Trait added."
        return updated_profile

    # ------------------------------------------------------------
    # REMOVE TRAIT
    # ------------------------------------------------------------
    remove_trait_match = re.search(
        r"remove trait[:\s]+(.+)",
        user_input.strip(),
        re.IGNORECASE
    )

    if remove_trait_match:
        trait_to_remove = remove_trait_match.group(1).strip()

        delete_user_personality_trait(user_id, trait=trait_to_remove)

        print(f"[PERSONALITY ENGINE] user={user_id} removed trait -> '{trait_to_remove}'")
        updated_profile = build_user_personality(user_id, personality_profile)
        updated_profile["_message"] = "Trait removed."
        return updated_profile

    # ============================================================
    # DISPLAY CURRENT PERSONALITY STATE
    # ============================================================

    if "show personality" in normalized_input:
        print(
            f"[PERSONALITY ENGINE]\n"
            f"  Name       : {personality_profile.get('name')}\n"
            f"  Tone       : {personality_profile.get('tone')}\n"
            f"  Verbosity  : {personality_profile.get('verbosity')}\n"
            f"  Traits     : {', '.join(personality_profile.get('traits', []))}"
        )
        return personality_profile

    # ============================================================
    # FALLBACK HELP RESPONSE
    # ============================================================

    print("[PERSONALITY ENGINE] Try:")
    print("  - set tone to X")
    print("  - set name to X")
    print("  - add trait: X")
    print("  - remove trait: X")

    return personality_profile


TOOL_META = {
    "name": "personality",
    "category": "personality",
    "description": "Shows or updates the active personality settings.",
    "usage": (
        "show personality | set tone to <tone> | set name to <name> | "
        "set verbosity to <level> | add trait: <trait> | "
        "remove trait: <trait>"
    ),
    "examples": [
        "show personality",
        "set tone to friendly",
        "set verbosity to brief",
    ],
    "options": {
        "tone": "direct | friendly | formal",
        "verbosity": "brief | normal | detailed",
    },
    "confirmation_required": False,
}

register_tool(TOOL_META, handle_personality)
