"""
Aetheraeon AI - JSON Helpers

Purpose:
Provides reusable JSON extraction, repair, parsing, and normalization utilities.

Architecture Layer:
Utility and Support Layer - structured data handling.

Responsibilities:
- Recover structured JSON from supported text outputs.
- Normalize parsing results and report malformed data safely.
- Support API, model, routing, memory, and tool callers without owning their policies.

Boundaries:
- JSON repair does not determine intent, truth, authorization, or execution policy.
- This module does not call models, databases, tools, or external services.
- It does not expose or reconstruct private chain-of-thought.
"""

# ============================================================
# CORE STANDARD LIBRARY IMPORTS
# ============================================================
# Built-in Python modules used for JSON parsing,
# text processing, and structured data normalization.
# ============================================================

import json          # JSON parsing and serialization
import re            # Pattern matching and text repair utilities


# ============================================================
# EXTERNAL DEPENDENCIES (PIP INSTALLED PACKAGES)
# ============================================================
# This file intentionally minimizes external dependencies
# to keep parsing utilities lightweight and reusable.
# ============================================================

# No external dependencies currently required.


# ============================================================
# INTERNAL SYSTEM IMPORTS (ARCHITECTURE LAYERS)
# ============================================================
# This utility layer should remain highly isolated.
#
# RULES:
# - No database imports
# - No orchestration imports
# - No API/server imports
# - No execution/tool imports
# - No frontend/UI imports
#
# This file must remain a pure structured-data utility layer.
# ============================================================

# No internal system imports currently required.


# ============================================================
# JSON OBJECT EXTRACTION ENGINE
# ============================================================
# Purpose:
# Safely extracts the FIRST complete top-level JSON object
# from mixed or malformed text produced by LLMs.
#
# This uses structural brace tracking instead of regex
# to avoid partial-object extraction failures.
# ============================================================

def extract_first_json_object(raw_text: str) -> str | None:
    """
    ============================================================
    EXTRACT FIRST COMPLETE JSON OBJECT
    ============================================================

    PURPOSE:
    - Locate the first valid JSON object inside raw text
    - Handle nested braces correctly
    - Ignore braces inside quoted strings
    - Prevent partial regex extraction failures

    INPUT:
    raw_text -> mixed LLM output or arbitrary text

    RETURNS:
    - complete JSON object string
    - None if no valid object is found
    ============================================================
    """

    # ------------------------------------------------------------
    # VALIDATE INPUT
    # ------------------------------------------------------------
    # Reject empty or invalid input immediately.
    # ------------------------------------------------------------

    if not raw_text:
        return None

    # ------------------------------------------------------------
    # FIND INITIAL JSON OBJECT START
    # ------------------------------------------------------------
    # Locate the first opening brace which signals the
    # potential beginning of a JSON object.
    # ------------------------------------------------------------

    json_start_index = raw_text.find("{")

    if json_start_index < 0:
        return None

    # ------------------------------------------------------------
    # STRUCTURAL PARSING STATE
    # ------------------------------------------------------------
    # These variables track parsing state while iterating
    # through the raw text character-by-character.
    # ------------------------------------------------------------

    brace_depth = 0
    inside_string = False
    escape_active = False

    # ------------------------------------------------------------
    # CHARACTER-BY-CHARACTER STRUCTURAL PARSING
    # ------------------------------------------------------------
    # This parser:
    # - tracks nested brace depth
    # - ignores braces inside quoted strings
    # - handles escaped quote characters safely
    # ------------------------------------------------------------

    for character_index in range(json_start_index, len(raw_text)):

        current_character = raw_text[character_index]

        # --------------------------------------------------------
        # STRING PARSING MODE
        # --------------------------------------------------------
        # When inside a JSON string:
        # - ignore braces
        # - properly handle escape sequences
        # --------------------------------------------------------

        if inside_string:

            if escape_active:
                escape_active = False

            elif current_character == "\\":
                escape_active = True

            elif current_character == "\"":
                inside_string = False

            continue

        # --------------------------------------------------------
        # NORMAL STRUCTURAL PARSING MODE
        # --------------------------------------------------------

        else:

            # Enter string parsing mode
            if current_character == "\"":
                inside_string = True
                continue

            # Opening brace increases nesting depth
            if current_character == "{":
                brace_depth += 1

            # Closing brace reduces nesting depth
            elif current_character == "}":

                brace_depth -= 1

                # ------------------------------------------------
                # COMPLETE JSON OBJECT DETECTED
                # ------------------------------------------------
                # When depth returns to zero, the first full
                # top-level JSON object has been fully parsed.
                # ------------------------------------------------

                if brace_depth == 0:

                    return raw_text[
                        json_start_index : character_index + 1
                    ]

    # ------------------------------------------------------------
    # NO COMPLETE OBJECT FOUND
    # ------------------------------------------------------------

    return None



# ============================================================
# JSON REPAIR NORMALIZATION ENGINE
# ============================================================
# Purpose:
# Repairs small malformed JSON patterns commonly produced
# by LLMs without performing dangerous transformations.
#
# This function intentionally performs ONLY minimal,
# predictable, low-risk repairs.
# ============================================================

def repair_json_like(raw_json_text: str) -> str:
    """
    ============================================================
    SAFE JSON STRUCTURE REPAIR
    ============================================================

    PURPOSE:
    Applies conservative repairs to malformed JSON-like text.

    This function is designed specifically for:
    - minor LLM formatting mistakes
    - accidental trailing quotes
    - malformed primitive value endings

    IMPORTANT:
    This is NOT a full JSON repair engine.
    It only performs targeted safe corrections.

    INPUT:
    raw_json_text -> potentially malformed JSON string

    RETURNS:
    repaired JSON-like string
    ============================================================
    """

    # ------------------------------------------------------------
    # VALIDATE INPUT
    # ------------------------------------------------------------
    # Return immediately if input is empty or invalid.
    # ------------------------------------------------------------

    if not raw_json_text:
        return raw_json_text

    # ------------------------------------------------------------
    # INITIAL NORMALIZATION
    # ------------------------------------------------------------
    # Remove surrounding whitespace before applying repairs.
    # ------------------------------------------------------------

    repaired_json_text = raw_json_text.strip()

    # ------------------------------------------------------------
    # REPAIR: INVALID QUOTE AFTER NUMERIC VALUES
    # ------------------------------------------------------------
    # Example:
    #   {"count": 5"}
    #
    # Repairs to:
    #   {"count": 5}
    #
    # Only repairs quotes directly before:
    # - closing brace
    # - comma separator
    # ------------------------------------------------------------

    repaired_json_text = re.sub(
        r':\s*(\d+(?:\.\d+)?)\s*"\s*([},])',
        r": \1\2",
        repaired_json_text
    )

    # ------------------------------------------------------------
    # REPAIR: INVALID QUOTE AFTER BOOLEAN/NULL VALUES
    # ------------------------------------------------------------
    # Example:
    #   {"enabled": true"}
    #
    # Repairs to:
    #   {"enabled": true}
    # ------------------------------------------------------------

    repaired_json_text = re.sub(
        r':\s*(true|false|null)\s*"\s*([},])',
        r": \1\2",
        repaired_json_text,
        flags=re.IGNORECASE
    )

    # ------------------------------------------------------------
    # RETURN REPAIRED JSON TEXT
    # ------------------------------------------------------------

    return repaired_json_text
