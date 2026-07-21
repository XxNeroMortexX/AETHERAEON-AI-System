"""
Aetheraeon AI - Personality Engine

Purpose:
Provides user-configurable communication-style modifiers for Aetheraeon responses.

Architecture Layer:
Identity and Personality Layer - communication presentation.

Responsibilities:
- Load and save supported personality and communication preferences.
- Produce tone, style, verbosity, greeting, formatting, and empathy modifiers.
- Supply observable personality metadata to current response-generation callers.

Boundaries:
- Personality controls communication style only.
- It does not control truth, reasoning policy, permissions, security, memory storage, candidate promotion, tool authorization, or validation outcomes.
- Personality modifiers cannot override approved facts, operation results, ownership rules, or safety policy.
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
        {"name": "Efficient", "description": "Keeps responses purposeful.",
         "category": "communication", "strength": 80, "owner": "aetheraeon"},
        {"name": "Focused", "description": "Stays centered on the user's goal.",
         "category": "reasoning", "strength": 85, "owner": "aetheraeon"},
        {"name": "Direct", "description": "Uses clear and candid language.",
         "category": "communication", "strength": 75, "owner": "aetheraeon"},
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
    base_traits = list(profile.get("traits", []) or [])
    stored_traits = list(preference_context["traits"])
    combined_traits = base_traits + stored_traits
    latest_feedback_by_trait = {}
    for item in preference_context["trait_feedback"]:
        if isinstance(item, dict):
            latest_feedback_by_trait[item.get("trait_id")] = item
    latest_trait_feedback = list(latest_feedback_by_trait.values())
    base_settings = {
        "style": settings.get("personality_style", "balanced"),
        "tone": settings.get("response_tone", "direct"),
        "verbosity": settings.get("response_detail", "normal"),
        "humor": settings.get("humor_level", "low"),
        "greeting_style": settings.get("greeting_style", "friendly"),
    }

    profile.update({
        **base_settings,
        "base_settings": dict(base_settings),
        "traits": combined_traits,
        "user_traits": preference_context["user_traits"],
        "aetheraeon_traits": base_traits + preference_context["aetheraeon_traits"],
        "trait_feedback": latest_trait_feedback,
        "trait_corrections": [
            item.get("correction", "")
            for item in latest_trait_feedback
            if item.get("correction")
        ],
        "user_preferences": {
            "router_model": settings.get("preferred_router_model"),
            "chat_model": settings.get("preferred_chat_model"),
            "code_model": settings.get("preferred_code_model"),
            "ui_theme": settings.get("ui_theme"),
            "web_search_enabled": bool(settings.get("web_search_enabled")),
        },
    })
    # AI-owned tendencies have priority over user-owned preference defaults.
    ordered_traits = (
        list(preference_context["aetheraeon_traits"])
        + list(preference_context["user_traits"])
    )
    _apply_trait_influences(profile, ordered_traits)
    return profile


def _apply_trait_influences(profile: dict, traits: list) -> list[str]:
    """Apply bounded style defaults; explicit user requests remain superior."""
    effects = []
    modifier_details = []
    base_settings = dict(profile.get("base_settings") or {
        key: profile.get(key)
        for key in ("style", "tone", "verbosity", "humor", "greeting_style")
    })
    ordered_traits = sorted(
        list(traits or []),
        key=lambda item: (
            0 if isinstance(item, dict) and item.get("owner") == "aetheraeon"
            else 1 if isinstance(item, dict) and item.get("owner") == "user"
            else 2
        ),
    )
    for trait in ordered_traits:
        if not isinstance(trait, dict) or not trait.get("active", True):
            continue
        try:
            strength = int(trait.get("strength") or 0)
        except (TypeError, ValueError):
            strength = 0
        if strength < 50:
            continue
        name = str(trait.get("name") or trait.get("trait") or "").lower()
        trait_effects = []

        if "humor" in name or "playful" in name:
            if profile.get("humor") in {None, "none", "low"}:
                profile["humor"] = "medium"
                effects.append("humor: medium")
                trait_effects.append("Humor: low to medium")
            if profile.get("greeting_style") in {None, "minimal", "friendly"}:
                profile["greeting_style"] = "conversational"
                effects.append("greeting style: conversational")
                trait_effects.append("Greeting: friendly to conversational")
            if profile.get("style") in {None, "balanced"}:
                profile["style"] = "friendly"
                effects.append("personality style: friendly")
                trait_effects.append("Style: balanced to friendly")

        if "detailed explanation" in name or "structured explanation" in name:
            if profile.get("verbosity") in {None, "normal"}:
                profile["verbosity"] = "detailed"
                effects.append("verbosity: detailed")
                trait_effects.append("Verbosity: normal to detailed")
            if profile.get("style") in {None, "balanced"}:
                profile["style"] = "professional"
                effects.append("personality style: professional")
                trait_effects.append("Style: balanced to professional")

        if "friendly" in name and profile.get("tone") in {None, "direct"}:
            profile["tone"] = "friendly"
            effects.append("tone: friendly")
            trait_effects.append("Tone: direct to friendly")

        if trait_effects:
            modifier_details.append({
                "trait": str(trait.get("name") or trait.get("trait") or "Trait"),
                "owner": str(trait.get("owner") or "aetheraeon"),
                "strength_level": max(1, min(10, (strength + 5) // 10)),
                "modifier": f"+{1 if strength < 70 else 2 if strength < 90 else 3}",
                "effects": trait_effects,
            })

    profile["trait_influences"] = effects
    profile["trait_modifier_details"] = modifier_details
    effective = {
        key: profile.get(key)
        for key in ("style", "tone", "verbosity", "humor", "greeting_style")
    }
    profile["effective_personality"] = effective
    profile["personality_debug"] = {
        "base_settings": base_settings,
        "trait_modifiers": modifier_details,
        "effective_personality": effective,
    }
    profile["behavior_instructions"] = personality_behavior_instructions(profile)
    return effects


def personality_behavior_instructions(personality_profile: dict) -> list[str]:
    """Translate effective style values into concrete, bounded LLM behavior."""
    profile = personality_profile if isinstance(personality_profile, dict) else {}
    instructions = []
    humor = str(profile.get("humor") or "low").lower()
    greeting = str(profile.get("greeting_style") or "friendly").lower()
    verbosity = str(profile.get("verbosity") or "normal").lower()
    tone = str(profile.get("tone") or "direct").lower()
    style = str(profile.get("style") or "balanced").lower()

    if humor in {"medium", "high"}:
        instructions.extend([
            "Use light humor naturally when appropriate.",
            "Do not force jokes in serious, sensitive, or frustrated conversations.",
        ])
    elif humor in {"none", "low"}:
        instructions.append("Keep humor restrained unless the user explicitly invites it.")
    if greeting == "conversational":
        instructions.extend([
            "Keep greetings warm and conversational.",
            "Avoid robotic or generic assistant openings.",
        ])
    elif greeting == "minimal":
        instructions.append("Keep greetings concise and purposeful.")
    if verbosity == "detailed":
        instructions.append("Give structured explanations with useful detail and examples when the request allows it.")
    elif verbosity == "brief":
        instructions.append("Prefer concise answers unless more detail is explicitly requested.")
    if tone == "friendly" or style == "friendly":
        instructions.append("Sound approachable and human while remaining clear and accurate.")
    if style == "professional":
        instructions.append("Organize complex answers clearly and use precise language.")

    for feedback in profile.get("trait_feedback", []) or []:
        if not isinstance(feedback, dict):
            continue
        correction = str(feedback.get("correction") or "").strip()
        if not correction:
            continue
        related_trait = str(feedback.get("related_trait") or "Aetheraeon trait").strip()
        instructions.append(
            f'Apply the user correction for "{related_trait}": {correction}'
        )

    # Backward compatibility for profiles that only provide correction strings.
    if not profile.get("trait_feedback"):
        for correction in profile.get("trait_corrections", []) or []:
            correction = str(correction or "").strip()
            if correction:
                instructions.append(f"Apply this user correction to Aetheraeon traits: {correction}")

    # Preserve order while removing duplicates.
    return list(dict.fromkeys(instructions))


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
        traits = [traits]

    structured_traits = []
    for trait in traits:
        if isinstance(trait, dict):
            try:
                trait_strength = max(0, min(100, int(trait.get("strength") or 0)))
            except (TypeError, ValueError):
                trait_strength = 50
            structured_traits.append({
                "name": str(trait.get("name") or trait.get("trait") or "").strip(),
                "description": str(trait.get("description") or "").strip(),
                "category": str(trait.get("category") or "communication").strip(),
                "strength": trait_strength,
                "owner": str(trait.get("owner") or "aetheraeon").strip(),
            })
        else:
            structured_traits.append({
                "name": str(trait), "description": "", "category": "general",
                "strength": 50, "owner": "aetheraeon",
            })

    user_traits = [item for item in structured_traits if item["owner"] == "user"]
    ai_traits = [item for item in structured_traits if item["owner"] == "aetheraeon"]
    trait_corrections = personality_profile.get("trait_corrections", []) or []
    user_trait_text = "; ".join(
        f'{item["name"]} ({item["description"]})' for item in user_traits
    ) or "none defined"
    ai_trait_text = "; ".join(
        f'{item["name"]} [strength {max(1, min(10, (item["strength"] + 5) // 10))}/10] '
        f'({item["description"]})'
        for item in ai_traits
    ) or "none defined"
    correction_text = "; ".join(str(item) for item in trait_corrections) or "none"
    behavior_instructions = personality_profile.get("behavior_instructions")
    if not isinstance(behavior_instructions, list):
        behavior_instructions = personality_behavior_instructions(personality_profile)
    behavior_text = "\n".join(f"- {item}" for item in behavior_instructions)


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
        f"User traits/preferences: {user_trait_text}\n"
        f"Aetheraeon behavioral traits: {ai_trait_text}\n"
        f"User corrections to Aetheraeon traits: {correction_text}\n"
        f"Verbosity: {verbosity}\n"
        f"Humor: {humor}\n"
        f"Greeting style: {greeting_style}\n"
        "User account preferences (context only): "
        f"theme={user_preferences.get('ui_theme', 'dark')}, "
        f"web_search={bool(user_preferences.get('web_search_enabled', False))}, "
        f"router_model={user_preferences.get('router_model')}, "
        f"chat_model={user_preferences.get('chat_model')}, "
        f"code_model={user_preferences.get('code_model')}\n"
        "\nEFFECTIVE BEHAVIOR INSTRUCTIONS\n"
        f"{behavior_text or '- Use the active personality values as communication defaults.'}\n"
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
        "- For communication style, apply this priority: explicit current request; safety/system rules; current conversation context; Aetheraeon traits; user traits; default settings\n"
        "- Explicit instructions in the current user request override all trait-based style defaults, but never safety or system rules\n"
        "- Traits modify only the effective runtime personality and never overwrite saved user settings\n"
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
            "  Traits     : "
            + ", ".join(
                item.get("name", item.get("trait", ""))
                if isinstance(item, dict) else str(item)
                for item in personality_profile.get("traits", [])
            )
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
