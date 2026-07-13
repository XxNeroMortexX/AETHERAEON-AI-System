"""
========================================================
AETHERAEON — Cognitive Processing Layer
========================================================

FILE PURPOSE:
This file is the foundational cognition engine of the AI.

It handles low-level reasoning primitives, decision logic,
and cognitive processing utilities used across the system.

It is NOT the full orchestrator.
It is the internal "thinking machinery" used by higher layers
such as ai_orchestrator.py and request_router.py.

========================================================
SYSTEM ROLE:
"Brain Core Layer" of the architecture.

It provides raw cognitive functions that higher systems
use to build intelligence workflows.

It does NOT directly respond to users.

========================================================
RESPONSIBILITIES:
(core_cognition.py)

- Low-level reasoning functions
- Cognitive pattern evaluation
- Decision scoring and weighting logic
- Thought structuring utilities
- Signal processing for AI interpretation
- Pre-processing of reasoning inputs
- Supporting orchestration layer decisions

========================================================
STRICT BOUNDARIES (DO NOT BREAK):
(core_cognition.py)

This file MUST NOT:
- Handle user I/O directly
- Execute tools or external commands
- Access databases directly
- Perform API/network calls
- Format final AI responses
- Manage UI or routing logic

It ONLY provides cognitive computation utilities.

========================================================
COGNITIVE FLOW ROLE:

Input Signal
    ↓
pattern analysis
    ↓
context weighting
    ↓
reasoning evaluation
    ↓
decision scoring
    ↓
output cognitive signals
    ↓
used by ai_orchestrator.py

========================================================
SYSTEM WIDE POSITION:

User Input
    ↓
api_gateway.py
    ↓
request_router.py
    ↓
ai_orchestrator.py
    ↓
core_cognition.py   ← THIS FILE (support engine)
    ↓
tool_executor.py (if needed)
    ↓
external_toolkit.py
    ↓
memory_database.py
    ↓
model_registry.py
    ↓
api_gateway.py
    ↓
UI

========================================================
KEY DEPENDENCIES:

core_cognition.py is used by:
- ai_orchestrator.py
- request_router.py
- memory_context_builder.py

It may reference:
- config_loader.py
- system_utils.py

========================================================
CORE FUNCTIONS (THIS FILE):

- pattern_score()
- intent_weighting()
- context_evaluator()
- decision_ranker()
- cognitive_fusion()
- signal_normalizer()

========================================================
DESIGN PHILOSOPHY:

"Pure Cognition Without Action"

- No execution
- No persistence
- No user interface
- Only structured thinking logic

========================================================
"""


# ============================================================
# CORE STANDARD LIBRARY IMPORTS
# ============================================================
# These are built-in Python modules used for cognitive
# reasoning, parsing, serialization, and utility operations.
# ============================================================

import json          # Structured cognitive state serialization
import re            # Pattern extraction and text normalization


# ============================================================
# EXTERNAL DEPENDENCIES (PIP INSTALLED PACKAGES)
# ============================================================
# Third-party libraries used for model interaction and
# external reasoning support.
# ============================================================

import requests      # HTTP communication for LLM/router calls


# ============================================================
# INTERNAL SYSTEM IMPORTS (ARCHITECTURE LAYERS)
# ============================================================
# Core cognition depends ONLY on reasoning and identity layers.
#
# RULES:
# - No database access here
# - No API/server imports here
# - No execution/tool logic here
# - No frontend/UI logic here
#
# This file operates as a pure cognition layer.
# ============================================================

# ------------------------------------------------------------
# LLM INTERFACE LAYER
# (Handles direct model reasoning calls)
# ------------------------------------------------------------
from core.llm_interface import ask_llm


# ------------------------------------------------------------
# IDENTITY / PERSONALITY LAYER
# (Provides cognitive identity grounding)
# ------------------------------------------------------------
from core.agent_identity import AI_IDENTITY
from core.personality_engine import personality_prompt
from core.json_helpers import (
    extract_first_json_object,
    repair_json_like,
)

# ============================================================
# LEFT BRAIN COGNITIVE ANALYSIS ENGINE (SEMANTIC)
# ============================================================
# PURPOSE:
# Converts raw user input into structured logical components
# using semantic understanding (not keyword matching).
#
# LEFT BRAIN ROLE:
# - Extract factual statements
# - Identify entities and subjects
# - Detect objectives and constraints
# - Maintain structured logical representation
#
# DOES NOT:
# - Interpret meaning or emotion (Right Brain responsibility)
# - Decide response or actions (Orchestrator responsibility)
# ============================================================

def left_brain_analyze(short_term_memory, long_term_memory, user_input):
    """
    Returns structured logical decomposition of user input.
    """

    # --------------------------------------------------------
    # INITIAL STRUCTURE (LEFT BRAIN OUTPUT CONTRACT)
    # --------------------------------------------------------

    analysis_state = {
        "facts": [],
        "entities": [],
        "subjects": [],
        "objectives": [],
        "constraints": [],
        "observations": []
    }

    if not user_input:
        return analysis_state

    # --------------------------------------------------------
    # BUILD CONTEXT FOR SEMANTIC EXTRACTION
    # --------------------------------------------------------

    context = f"""
You are the LEFT BRAIN of a dual cognitive AI system.

Your job is STRICTLY logical decomposition.

Do NOT interpret meaning or emotion.

Extract only:
- facts (explicit statements)
- entities (names, objects, places, numbers, systems)
- subjects (main topics)
- objectives (what user is trying to do)
- constraints (requirements or limitations)
- observations (direct input summary)

INPUT:
{user_input}

Return ONLY valid JSON in this format:

{{
  "facts": [],
  "entities": [],
  "subjects": [],
  "objectives": [],
  "constraints": [],
  "observations": []
}}
"""

    # --------------------------------------------------------
    # CALL SEMANTIC LLM EXTRACTOR
    # --------------------------------------------------------

    try:
        raw_output = ask_llm(
            prompt=context,
            temperature=0.2,
            num_predict=300
        )

        clean_json = extract_first_json_object(raw_output)

        if clean_json:
            repaired_json = repair_json_like(clean_json)
            parsed = json.loads(repaired_json)
        else:
            parsed = {}

        # ----------------------------------------------------
        # SAFE MERGE INTO STRUCTURE (FAIL-SAFE CLEANUP)
        # ----------------------------------------------------

        for key in analysis_state.keys():
            if key in parsed and isinstance(parsed[key], list):
                analysis_state[key] = parsed[key]

        # ----------------------------------------------------
        # ALWAYS STORE RAW INPUT AS OBSERVATION
        # ----------------------------------------------------

        analysis_state["observations"].append(user_input)

        # ----------------------------------------------------
        # DEDUPLICATION PASS (LIGHTWEIGHT CLEANUP)
        # ----------------------------------------------------

        for key in analysis_state:
            analysis_state[key] = list(
                dict.fromkeys(analysis_state[key])
            )

        return analysis_state

    except Exception:
        # ----------------------------------------------------
        # FALLBACK: MINIMAL SAFE STRUCTURE
        # ----------------------------------------------------

        analysis_state["observations"].append(user_input)
        return analysis_state


# ============================================================
# RIGHT BRAIN CONTEXTUAL INTERPRETATION ENGINE
# ============================================================
# PURPOSE:
# Interprets meaning, symbolism, emotional tone,
# and relational patterns behind user input.
#
# RIGHT BRAIN ROLE:
# - Emotional tone detection
# - Symbolic interpretation
# - Pattern recognition
# - Relationship mapping
#
# DOES NOT:
# - Extract facts (Left Brain responsibility)
# - Decide actions or tools (Orchestrator responsibility)
# ============================================================

def right_brain_interpret(short_term_memory, long_term_memory, user_input):
    """
    Returns contextual and symbolic interpretation of input.
    """

    # --------------------------------------------------------
    # INITIAL STRUCTURE (RIGHT BRAIN OUTPUT CONTRACT)
    # --------------------------------------------------------

    interpretation_state = {
        "themes": [],
        "patterns": [],
        "relationships": [],
        "emotional_tone": [],
        "symbolism": [],
        "contextual_meaning": []
    }

    if not user_input:
        return interpretation_state

    # --------------------------------------------------------
    # BUILD RIGHT BRAIN PROMPT (SEMANTIC MODE)
    # --------------------------------------------------------

    prompt = f"""
You are the RIGHT BRAIN of a dual cognitive AI system.

Your job is STRICTLY interpretive and symbolic.

Do NOT extract facts or literal statements.

Focus ONLY on:
- emotional tone
- symbolic meaning
- hidden patterns
- relational connections
- contextual interpretation

INPUT:
{user_input}

Return ONLY valid JSON in this format:

{{
  "themes": [],
  "patterns": [],
  "relationships": [],
  "emotional_tone": [],
  "symbolism": [],
  "contextual_meaning": []
}}

Rules:
- No facts
- No instructions
- No summaries of events
- Only meaning and interpretation
"""

    # --------------------------------------------------------
    # SEMANTIC INTERPRETATION CALL
    # --------------------------------------------------------

    try:
        raw_output = ask_llm(
            prompt=prompt,
            temperature=0.6,
            num_predict=300
        )

        clean_json = extract_first_json_object(raw_output)

        if clean_json:
            repaired_json = repair_json_like(clean_json)
            parsed = json.loads(repaired_json)
        else:
            parsed = {}

        # ----------------------------------------------------
        # SAFE MERGE INTO STRUCTURE
        # ----------------------------------------------------

        for key in interpretation_state.keys():
            if key in parsed and isinstance(parsed[key], list):
                interpretation_state[key] = parsed[key]

        # ----------------------------------------------------
        # OPTIONAL CONTEXT ENHANCEMENT (FROM MEMORY)
        # ----------------------------------------------------

        if long_term_memory:
            interpretation_state["contextual_meaning"].append(
                "Long-term memory context influencing interpretation"
            )

        if short_term_memory:
            interpretation_state["relationships"].append(
                "Connected to recent conversation context"
            )

        # ----------------------------------------------------
        # CLEAN DUPLICATION
        # ----------------------------------------------------

        for key in interpretation_state:
            interpretation_state[key] = list(
                dict.fromkeys(interpretation_state[key])
            )

        return interpretation_state

    except Exception:
        # ----------------------------------------------------
        # FALLBACK SAFE STATE
        # ----------------------------------------------------

        interpretation_state["emotional_tone"].append("neutral")
        interpretation_state["contextual_meaning"].append("fallback interpretation mode")

        return interpretation_state


# ============================================================
# SYNTHESIS ENGINE — DUAL BRAIN MERGE CORE
# ============================================================
# PURPOSE:
# Merge LEFT BRAIN (logic) + RIGHT BRAIN (meaning)
# into a unified cognitive representation.
#
# DESIGN RULE:
# Both brains are weighted equally.
# Neither dominates interpretation.
# ============================================================

def synthesis_engine(left, right):
    """
    Combines structured logic and contextual meaning
    into a unified cognitive state.
    """

    # --------------------------------------------------------
    # BASE SYNTHESIS STRUCTURE
    # --------------------------------------------------------

    synthesis = {
        "facts": [],
        "entities": [],
        "intent": None,

        "themes": [],
        "tone": None,
        "symbolism": [],

        "merged_context": [],
        "cognitive_alignment": {},
        "summary": ""
    }

    # ============================================================
    # LEFT BRAIN INTEGRATION (STRUCTURE SIDE)
    # ============================================================

    if isinstance(left, dict):

        synthesis["facts"] = left.get("facts", [])
        synthesis["entities"] = left.get("entities", [])
        synthesis["intent"] = left.get("objectives", left.get("intent"))

    # ============================================================
    # RIGHT BRAIN INTEGRATION (MEANING SIDE)
    # ============================================================

    if isinstance(right, dict):

        synthesis["themes"] = right.get("themes", [])
        synthesis["tone"] = right.get("emotional_tone", right.get("tone"))
        synthesis["symbolism"] = right.get("symbolism", [])
        synthesis["merged_context"] = right.get("contextual_meaning", [])

    # ============================================================
    # BALANCED COGNITIVE ALIGNMENT (IMPORTANT)
    # ============================================================
    # This is where BOTH brains contribute equally.
    # We are not prioritizing either side.
    # We are mapping relationships between them.
    # ============================================================

    synthesis["cognitive_alignment"] = {
        "logical_focus": synthesis["facts"][:5],
        "meaning_focus": synthesis["themes"][:5],
        "shared_signal": list(
            set(synthesis["facts"]) &
            set(synthesis["themes"])
        )
    }

    # ============================================================
    # BUILD UNIFIED SUMMARY (TRUE SYNTHESIS)
    # ============================================================

    intent = synthesis["intent"] or "unknown intent"

    fact_block = ", ".join(synthesis["facts"][:5]) or "no explicit facts"
    theme_block = ", ".join(synthesis["themes"][:5]) or "no detected themes"

    tone_block = (
        ", ".join(synthesis["tone"])
        if isinstance(synthesis["tone"], list)
        else (synthesis["tone"] or "neutral")
    )

    synthesis["summary"] = (
        f"[Intent] {intent} | "
        f"[Logic] {fact_block} | "
        f"[Meaning] {theme_block} | "
        f"[Tone] {tone_block}"
    )

    # ============================================================
    # DEBUG OUTPUT
    # ============================================================

    print("\n[SYNTHESIS ENGINE]")
    print(synthesis["summary"])

    return synthesis
