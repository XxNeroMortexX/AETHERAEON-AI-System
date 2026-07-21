"""
Aetheraeon AI - Memory Context Builder

Purpose:
Assembles selected conversation and memory information into structured context for the current request.

Architecture Layer:
Memory Intelligence Layer - retrieval-context assembly support.

Responsibilities:
- Build context blocks from current conversation history and approved long-term recall results.
- Normalize and organize the sources actually supplied to downstream cognition and generation.
- Provide the integration point for planned Short-Term Scoped Memory retrieval.

Boundaries:
- This module does not authorize storage, classify candidate memories, promote candidates, or persist memory.
- Conversation Context is not permanent memory, and scoped information is not automatically forgotten or deleted.
- The Retrieval Coordinator and broader memory-decision flow are planned services unless separately implemented.
"""


# ============================================================
# CORE STANDARD LIBRARY IMPORTS
# ============================================================
# Built-in Python modules used for structured formatting,
# serialization, memory processing, and lightweight utilities.
# ============================================================

import json                      # JSON serialization for memory blocks
from datetime import datetime   # Timestamp generation for memory metadata


# ============================================================
# INTERNAL SYSTEM IMPORTS (ARCHITECTURE LAYERS)
# ============================================================
# Core AI system modules used for memory assembly and
# contextual intelligence construction.
#
# RULES:
# - No frontend/UI imports
# - No Flask imports
# - No direct model execution here
# - No tool execution here
#
# This file is responsible ONLY for:
# - memory context assembly
# - memory normalization
# - memory formatting preparation
# ============================================================

# ------------------------------------------------------------
# MEMORY DATABASE LAYER
# Handles ChromaDB + persistent memory retrieval
# ------------------------------------------------------------


# ------------------------------------------------------------
# AGENT IDENTITY LAYER
# AI personality / identity / system persona memory
# ------------------------------------------------------------
from core import agent_identity

# ------------------------------------------------------------
# CONFIGURATION SYSTEM
# Centralized configuration access layer
# ------------------------------------------------------------
from core import config_loader
from core import memory_database


def build_user_preferences_context(user_id: int) -> dict:
    """Load authenticated per-user settings and traits for AI context assembly."""
    settings = memory_database.get_user_settings(user_id)
    traits = memory_database.get_user_personality_traits(user_id)
    feedback = memory_database.get_personality_trait_feedback(user_id)
    return {
        "settings": settings,
        "traits": traits,
        "user_traits": [row for row in traits if row.get("owner") == "user"],
        "aetheraeon_traits": [
            row for row in traits if row.get("owner") == "aetheraeon"
        ],
        "trait_feedback": feedback,
    }

# ============================================================
# SHORT-TERM MEMORY CONTEXT BUILDER (INCREMENTAL MODE)
# ============================================================

def build_short_term_memory(
    session_history: list,
    current_input: str,
    existing_summary: str = ""
) -> dict:
    """
    ============================================================
    INCREMENTAL SHORT-TERM MEMORY ENGINE
    ============================================================

    PURPOSE:
    Builds and updates a live rolling memory summary instead
    of recomputing the entire conversation every time.

    KEY FEATURE:
    - Memory is continuously updated (not rebuilt)
    - Maintains evolving understanding of conversation
    - Optimized for long-running chat sessions

    THIS FUNCTION DOES NOT:
    - perform reasoning
    - access database
    - execute tools
    """

    # --------------------------------------------------------
    # 1. INPUT NORMALIZATION
    # --------------------------------------------------------

    if session_history is None:
        session_history = []

    if current_input is None:
        current_input = ""

    if existing_summary is None:
        existing_summary = ""

    # --------------------------------------------------------
    # 2. GET LATEST MESSAGE ONLY
    # --------------------------------------------------------
    # We only process NEW data instead of full history
    # This is the core of incremental memory design
    # --------------------------------------------------------

    latest_message = session_history[-1] if session_history else None

    # --------------------------------------------------------
    # 3. EXTRACT NEW MEMORY SIGNAL
    # --------------------------------------------------------

    new_memory_piece = ""

    if isinstance(latest_message, dict):
        role = latest_message.get("role", "unknown")
        content = latest_message.get("content", "")
        new_memory_piece = f"{role}: {content}"

    elif isinstance(latest_message, str):
        new_memory_piece = f"user: {latest_message}"

    # --------------------------------------------------------
    # 4. UPDATE RUNNING SUMMARY
    # --------------------------------------------------------
    # Instead of recomputing everything, we append new meaning
    # This creates a "living memory stream"
    # --------------------------------------------------------

    if new_memory_piece:
        updated_summary = (
            existing_summary + "\n" + new_memory_piece
            if existing_summary
            else new_memory_piece
        )
    else:
        updated_summary = existing_summary

    # --------------------------------------------------------
    # 5. BUILD SHORT-TERM MEMORY OBJECT
    # --------------------------------------------------------

    short_term_memory_context = {
        "memory_type": "short_term_memory",

        # Current input (highest priority)
        "current_input": current_input,

        # Live evolving summary (core intelligence layer)
        "conversation_summary": updated_summary,

        # Optional raw last message for precision
        "latest_message": latest_message,

        # Metadata
        "message_count": len(session_history),
        "is_incremental": True
    }

    # --------------------------------------------------------
    # 6. RETURN CONTEXT
    # --------------------------------------------------------

    return short_term_memory_context


# ============================================================
# LONG-TERM MEMORY CONTEXT BUILDER
# ============================================================

def build_long_term_memory(
    chroma_results: list,
    identity_memory: dict,
    user_profile: dict
) -> dict:
    """
    ============================================================
    LONG-TERM MEMORY ENGINE (FACTUAL MEMORY FUSION LAYER)
    ============================================================

    PURPOSE:
    Builds a unified long-term memory context by merging:
    - semantic memory (ChromaDB results)
    - identity memory (AI + user identity)
    - user profile data (preferences, settings)
    - persistent system knowledge

    ROLE IN ARCHITECTURE:
    This is the FACTUAL MEMORY LAYER.

    It does NOT:
    - interpret meaning
    - make decisions
    - execute reasoning logic

    It ONLY:
    - gathers stored knowledge
    - normalizes memory structure
    - prepares AI-readable knowledge base
    """

    # --------------------------------------------------------
    # 1. INPUT SAFETY NORMALIZATION
    # --------------------------------------------------------

    if chroma_results is None:
        chroma_results = []

    if identity_memory is None:
        identity_memory = {}

    if user_profile is None:
        user_profile = {}

    # --------------------------------------------------------
    # 2. PROCESS CHROMA SEMANTIC MEMORY
    # --------------------------------------------------------
    # Convert vector search results into structured memory
    # --------------------------------------------------------

    semantic_memory_blocks = []

    for item in chroma_results:

        # Preserve the existing dictionary format and normalize the
        # (memory_id, document, metadata) tuples returned by Chroma recall.
        if isinstance(item, dict):
            content = str(item.get("document", ""))
            metadata = item.get("metadata", {})
        elif isinstance(item, tuple) and len(item) >= 3:
            content = str(item[1])
            metadata = item[2] if isinstance(item[2], dict) else {}
        else:
            content = str(item)
            metadata = {}

        if not content:
            continue

        semantic_memory_blocks.append({
            "content": content,
            "metadata": metadata
        })

    # --------------------------------------------------------
    # 3. PROCESS IDENTITY MEMORY
    # --------------------------------------------------------
    # This includes:
    # - AI identity state
    # - user identity facts
    # --------------------------------------------------------

    identity_context = {
        "ai_identity": identity_memory.get("ai_identity", {}),
        "user_identity": identity_memory.get("user_identity", {}),
        "relationship_state": identity_memory.get("relationship_state", {})
    }

    # --------------------------------------------------------
    # 4. PROCESS USER PROFILE MEMORY
    # --------------------------------------------------------
    # Stable user preferences + configuration layer
    # --------------------------------------------------------

    profile_context = {
        "preferences": user_profile.get("preferences", {}),
        "settings": user_profile.get("settings", {}),
        "behavior_flags": user_profile.get("behavior_flags", {})
    }

    # --------------------------------------------------------
    # 5. BUILD LONG-TERM MEMORY STRUCTURE
    # --------------------------------------------------------
    # This is the unified memory object for AI reasoning
    # --------------------------------------------------------

    long_term_memory_context = {
        "memory_type": "long_term_memory",

        # Semantic memory from vector DB
        "semantic_memory": semantic_memory_blocks,

        # Identity layer (AI + user)
        "identity_context": identity_context,

        # User configuration / preferences
        "profile_context": profile_context,

        # Metadata for orchestration
        "memory_count": len(semantic_memory_blocks),
        "sources": [
            "chroma_db",
            "identity_memory",
            "user_profile"
        ]
    }

    # --------------------------------------------------------
    # 6. RETURN CONSOLIDATED MEMORY CONTEXT
    # --------------------------------------------------------

    return long_term_memory_context


# ============================================================
# SHORT-TERM MEMORY PROMPT BLOCK BUILDER
# ============================================================

def build_short_term_memory_block(summary, history, session_memory):
    """
    ============================================================
    SHORT-TERM MEMORY PROMPT BUILDER
    ============================================================

    PURPOSE:
    Converts structured short-term memory into a clean,
    LLM-ready prompt block.

    THIS FUNCTION:
    - formats memory for model input
    - ensures consistent structure
    - prevents prompt pollution
    - improves LLM comprehension

    THIS FUNCTION DOES NOT:
    - modify memory
    - store data
    - perform reasoning
    """

    # --------------------------------------------------------
    # 1. SAFE INITIALIZATION
    # --------------------------------------------------------

    summary = summary or ""
    history = history or []
    session_memory = session_memory or {}

    # --------------------------------------------------------
    # 2. HISTORY NORMALIZATION
    # --------------------------------------------------------
    # Ensure history is always readable and safe
    # Supports both string and list formats
    # --------------------------------------------------------

    formatted_history = ""

    if isinstance(history, list):

        history_lines = []

        for msg in history:

            # Handle dict-based messages
            if isinstance(msg, dict):

                role = str(msg.get("role", "unknown")).upper()
                content = str(msg.get("content", "")).strip()

            else:
                role = "UNKNOWN"
                content = str(msg).strip()

            if not content:
                continue

            # Light safety trim (prevents prompt explosion)
            trimmed_content = (
                content[:300] + "..."
                if len(content) > 300
                else content
            )

            history_lines.append(f"{role}: {trimmed_content}")

        formatted_history = "\n".join(history_lines)

    else:
        # If already string format
        formatted_history = str(history)

    # --------------------------------------------------------
    # 3. SESSION MEMORY CLEAN FORMAT
    # --------------------------------------------------------
    # Keep structured but readable for LLM
    # --------------------------------------------------------

    formatted_session_memory = json.dumps(
        session_memory,
        indent=2,
        ensure_ascii=False
    )

    # --------------------------------------------------------
    # 4. BUILD FINAL PROMPT BLOCK
    # --------------------------------------------------------

    blocks = []

    # Short-term summary section
    if summary.strip():
        blocks.append(
            "╔════════════════════════════╗\n"
            "║ SHORT TERM SUMMARY         ║\n"
            "╚════════════════════════════╝\n"
            f"{summary.strip()}"
        )

    # Recent conversation history section
    if formatted_history.strip():
        blocks.append(
            "╔════════════════════════════╗\n"
            "║ RECENT CHAT HISTORY        ║\n"
            "╚════════════════════════════╝\n"
            f"{formatted_history.strip()}"
        )

    # Session state section
    if session_memory:
        blocks.append(
            "╔════════════════════════════╗\n"
            "║ SESSION MEMORY STATE       ║\n"
            "╚════════════════════════════╝\n"
            f"{formatted_session_memory}"
        )

    # --------------------------------------------------------
    # 5. FINAL OUTPUT
    # --------------------------------------------------------

    return "\n\n".join(blocks)


# ============================================================
# LONG-TERM MEMORY PROMPT BLOCK BUILDER
# ============================================================

def build_long_term_memory_block(recall_block):
    """
    ============================================================
    LONG-TERM MEMORY PROMPT BUILDER
    ============================================================

    PURPOSE:
    Converts long-term memory (ChromaDB + persistent data)
    into a structured LLM-ready prompt block.

    THIS FUNCTION:
    - formats semantic recall data
    - improves readability for LLM reasoning
    - separates memory domains clearly

    THIS FUNCTION DOES NOT:
    - modify memory
    - retrieve memory
    - perform reasoning
    """

    # --------------------------------------------------------
    # 1. SAFE INPUT NORMALIZATION
    # --------------------------------------------------------

    if not recall_block:
        return ""

    recall_block = str(recall_block).strip()

    if not recall_block:
        return ""

    # --------------------------------------------------------
    # 2. MEMORY BLOCK STRUCTURING
    # --------------------------------------------------------
    # We explicitly label this as persistent factual memory
    # so the LLM treats it differently from short-term context
    # --------------------------------------------------------

    formatted_block = (
        "╔════════════════════════════╗\n"
        "║ LONG TERM MEMORY           ║\n"
        "╚════════════════════════════╝\n\n"
        "TYPE: Persistent Factual Memory\n"
        "SOURCE: ChromaDB + Stored Knowledge Base\n\n"
        "────────────────────────────\n"
        f"{recall_block}\n"
        "────────────────────────────\n"
    )

    # --------------------------------------------------------
    # 3. RETURN FINAL STRUCTURED BLOCK
    # --------------------------------------------------------

    return formatted_block
    


# ============================================================
# CONVERSATION CONTEXT BUILDER
# ============================================================
# PURPOSE:
# Builds optimized conversation context for AI inference.
#
# RESPONSIBILITIES:
# - Load conversation history
# - Limit excessive token growth
# - Build lightweight summaries
# - Format conversational prompt history
#
# RETURNS:
# {
#     "history": list,
#     "formatted_history": str,
#     "conversation_summary": str
# }
#
# IMPORTANT:
# This function ONLY prepares context.
# It does NOT perform AI reasoning.
# ============================================================

def _build_conversation_context(
    conversation_id,
    user_id=None,
    max_history_messages=20,
    summary_keep_recent=5,
    summary_max_entries=10,
):

    # --------------------------------------------------------
    # LOAD CONVERSATION HISTORY
    # --------------------------------------------------------
    # Retrieve stored conversation messages from database.
    # --------------------------------------------------------

    conversation_history = memory_database.get_messages(conversation_id, user_id=user_id)
    print("[CTX DEBUG] get_messages type:", type(memory_database.get_messages))
    # --------------------------------------------------------
    # HISTORY LIMITING
    # --------------------------------------------------------
    # Prevent runaway prompt growth and excessive token usage.
    # Keep only the most recent conversation messages.
    # --------------------------------------------------------

    if len(conversation_history) > max_history_messages:

        conversation_history = conversation_history[
            -max_history_messages:
        ]

    # --------------------------------------------------------
    # CONVERSATION SUMMARY GENERATION
    # --------------------------------------------------------
    # Compress older messages into lightweight summary text
    # while preserving recent conversational flow.
    # --------------------------------------------------------

    conversation_summary = ""

    if len(conversation_history) > summary_keep_recent:

        older_messages = conversation_history[
            :-summary_keep_recent
        ]

        summary_parts = []

        for message in older_messages:

            message_role = message.get("role", "unknown")

            message_content = (
                message.get("content", "")
            ).strip()

            # ------------------------------------------------
            # ROLE NORMALIZATION
            # ------------------------------------------------
            # Convert DB role values into human-readable labels.
            # ------------------------------------------------

            readable_role = (
                "User"
                if message_role == "user"
                else "AI"
            )

            # ------------------------------------------------
            # SUMMARY COMPRESSION
            # ------------------------------------------------
            # Keep summaries lightweight to reduce prompt size.
            # ------------------------------------------------

            summary_parts.append(
                f"{readable_role} said: "
                f"{message_content[:120]}"
            )

        # Prefer the entries closest to the recent-message window.  Taking the
        # first entries caused newer context to disappear whenever the summary
        # itself reached its cap.
        conversation_summary = " | ".join(
            summary_parts[-summary_max_entries:]
        )

    # --------------------------------------------------------
    # FORMATTED HISTORY CONSTRUCTION
    # --------------------------------------------------------
    # Convert structured message history into formatted prompt
    # text suitable for LLM conversational context.
    # --------------------------------------------------------

    formatted_history_lines = []

    for message in conversation_history:

        message_role = message.get("role", "unknown")

        message_content = (
            message.get("content", "")
        ).strip()

        readable_role = (
            "User"
            if message_role == "user"
            else "AI"
        )

        formatted_history_lines.append(
            f"{readable_role}: {message_content}"
        )

    formatted_history = "\n".join(
        formatted_history_lines
    )

    # --------------------------------------------------------
    # RETURN STRUCTURED CONTEXT OBJECT
    # --------------------------------------------------------
    # Returning structured objects keeps orchestration cleaner.
    # --------------------------------------------------------

    return {

        "history": conversation_history,

        "formatted_history": formatted_history,

        "conversation_summary": conversation_summary
    }    
