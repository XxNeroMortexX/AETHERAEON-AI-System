"""
Aetheraeon AI - Conversation Title Engine

Purpose:
Produces concise human-readable titles from supplied conversation context for navigation and display.

Architecture Layer:
Identity and Personality Layer - conversation metadata support.

Responsibilities:
- Extract local topic signals from provided conversation text.
- Generate and normalize short conversation titles.
- Return title data to the caller for persistence and presentation.

Boundaries:
- Topic analysis for a title is not the governing Natural Language Understanding contract or a cognitive policy decision.
- This module does not persist conversations, modify memory, execute tools, or perform full reasoning.
- Personality may influence presentation style only.
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
