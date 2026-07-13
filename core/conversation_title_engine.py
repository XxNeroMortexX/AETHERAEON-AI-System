"""
========================================================
AETHERAEON — CONVERSATION TITLE ENGINE (MEMORY LABELING LAYER)
========================================================

FILE PURPOSE:
This file is responsible for generating short, meaningful
titles for user conversations based on dialogue context.

It transforms raw conversation data into structured,
human-readable labels used for UI display, memory indexing,
and conversation history organization.

========================================================
SYSTEM ROLE:
"Context Labeling Layer" of the architecture.

It does NOT reason deeply or execute tools.
It ONLY summarizes conversation intent into titles.

========================================================
RESPONSIBILITIES:
(conversation_title_engine.py)

- Analyze conversation context (short-term memory)
- Detect user intent or topic theme
- Generate concise conversation titles
- Ensure consistent formatting for UI display
- Improve memory navigation and indexing clarity
- Prevent overly long or noisy titles

========================================================
STRICT BOUNDARIES (DO NOT BREAK):
(conversation_title_engine.py)

This file MUST NOT:
- Execute tools or external actions (tool_executor.py handles this)
- Modify memory database directly (memory_database.py handles this)
- Perform full reasoning chains (ai_orchestrator.py handles this)
- Call external APIs or web services
- Store persistent data

It ONLY returns formatted title strings.

========================================================
TITLE GENERATION FLOW:
(conversation_title_engine.py functions)

Conversation Context Input
    ↓
extract_key_topics()
    ↓
identify_primary_intent()
    ↓
compress_context_signal()
    ↓
generate_title()
    ↓
return short UI-friendly title

========================================================
SYSTEM WIDE FLOW:
(full system architecture integration)

User Input
    ↓
api_gateway.py
    ↓
request_router.py
    ↓
ai_orchestrator.py
    ↓
conversation_title_engine.py   ← THIS FILE
    ↓
title returned to memory system
    ↓
memory_database.py stores title
    ↓
UI displays conversation label

========================================================
KEY FILE DEPENDENCIES:

conversation_title_engine.py depends on:
- llm_interface.py          (optional for title generation)
- memory_context_builder.py (context compression input)
- personality_engine.py     (tone consistency for titles)

========================================================
CORE FUNCTIONS (THIS FILE):

- extract_key_topics()
- identify_primary_intent()
- compress_context_signal()
- generate_title()

========================================================
OUTPUT CONTRACT:
(conversation_title_engine.py returns)

- title (string)
- optional metadata (keywords, confidence)

========================================================
DESIGN PHILOSOPHY:

"Compression of Meaning"

- Orchestrator THINKS
- Title Engine SUMMARIZES
- tool_executor ACTS
- Database STORES
- UI DISPLAYS

========================================================
"""

# ============================================================
# CORE STANDARD LIBRARY IMPORTS
# ============================================================
# These are built-in Python modules used for logic, parsing,
# timing, system operations, and utility functions.
# ============================================================

import json          # JSON parsing for structured prompts / outputs (if needed)
import re            # Pattern cleanup for title sanitization
import os            # File/system access if needed (future-safe)
import time          # Optional timing / debugging support
import threading     # Background safety (future async expansion)
from datetime import datetime  # Timestamping for logs/debug traces


# ============================================================
# EXTERNAL DEPENDENCIES (PIP INSTALLED PACKAGES)
# ============================================================
# Third-party libraries installed via pip.
# ============================================================

import requests      # HTTP requests (ONLY if LLM endpoint is remote)
import ollama        # Local LLM inference backend (primary model interface)


# ============================================================
# INTERNAL SYSTEM IMPORTS (ARCHITECTURE LAYERS)
# ============================================================
# This section defines ALL internal AI system dependencies.
#
# RULES:
# - These imports are part of the core AI architecture
# - DO NOT mix external libraries here
# - DO NOT execute logic here
# - ONLY import system layers or registries
# ============================================================

# ------------------------------------------------------------
# LLM INTERFACE LAYER
# (Handles model communication and abstraction layer)
# ------------------------------------------------------------
from core import llm_interface


# ------------------------------------------------------------
# CONFIGURATION LAYER
# (Central system settings and environment configuration)
# ------------------------------------------------------------
from core import config_loader   
   
   
# ============================================================
# CONVERSATION TITLE ENGINE — AI TITLE GENERATION
# ============================================================
# PURPOSE:
# Generates short, meaningful conversation titles using the LLM.
#
# The goal is NOT to summarize text literally,
# but to extract the conceptual meaning and assign a label.
#
# OUTPUT RULE:
# - Returns a clean, human-readable title (max ~4 words)
# - Falls back safely if generation fails
# ============================================================

def generate_title(conversation_text: str) -> str:
    """
    Generates a short AI-based title for a conversation.
    """

    # ─────────────────────────────────────────────
    # 1. TITLE GENERATION PROMPT (CONCEPT EXTRACTION)
    # ─────────────────────────────────────────────
    # We force the model to:
    # - abstract meaning first
    # - avoid reusing original wording
    # - produce a clean conceptual label
    # ─────────────────────────────────────────────

    prompt = f"""
Create a short conversation title.

STEP 1 — UNDERSTAND (do not reuse words):
Read the conversation and extract the core meaning as a concept only.
Do NOT use any phrases or wording from the input at this stage.

STEP 2 — NAME:
Give that concept a short human-style title using completely new wording.

Rules:
- Keep the title concise and readable
- Use as many words as naturally fit within ~32 characters
- Prefer shorter titles, but allow longer ones if clarity improves
- Avoid unnecessary filler words
- No punctuation
- Title Case
- Do NOT reuse or modify input phrases
- Focus on meaning, not wording
- Avoid repeating the same naming structure across outputs
- Each title should feel like a natural label for an idea or project

IMPORTANT:
You are naming the concept, not rewriting the text.

Conversation:
{conversation_text}

Return only the title.
"""

    try:
        # ─────────────────────────────────────────────
        # 2. LLM CALL (TITLE GENERATION)
        # ─────────────────────────────────────────────
        raw_title = llm_interface.ask_llm(
            prompt=prompt,
            temperature=0.7,
            num_predict=12
        )

        # ─────────────────────────────────────────────
        # 3. CLEANUP + NORMALIZATION
        # ─────────────────────────────────────────────
        # Remove unsafe characters and normalize spacing
        # Limit to max 4 words for UI consistency
        # ─────────────────────────────────────────────

        clean_title = (raw_title or "").replace('"', "").replace("'", "")
        clean_title = " ".join(clean_title.split())  # normalize whitespace
        clean_title = " ".join(clean_title.split()[:4])  # enforce max words

        return clean_title or "New Conversation"

    except Exception as error:
        # ─────────────────────────────────────────────
        # 4. SAFE FALLBACK (FAILOVER HANDLING)
        # ─────────────────────────────────────────────

        print("Title generation failed:", error)
        return "New Conversation"