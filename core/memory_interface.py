"""
Aetheraeon AI - Memory Interface

Purpose:
Provides the stable abstraction used by current callers to access memory and related persistence operations.

Architecture Layer:
Memory Intelligence Layer - memory access abstraction.

Responsibilities:
- Execute approved memory operations through the current persistence implementation.
- Normalize retrieval, storage, update, deletion, and similarity results.
- Isolate higher-level components from MariaDB and ChromaDB implementation details.

Boundaries:
- This interface does not decide whether information is Conversation Context, Short-Term Scoped Memory, Candidate Memory, or Long-Term Memory.
- It does not authorize candidate promotion, bypass ownership or security policy, or automatically forget retained information.
- Memory Intelligence and the planned Cognitive Decision Engine determine policy; storage layers persist approved outcomes.
"""

# ============================================================
# CORE STANDARD LIBRARY IMPORTS
# ============================================================
# Built-in Python modules used for memory parsing,
# routing, pattern matching, file handling, and runtime state.
# ============================================================

import json          # JSON serialization / memory persistence
import re            # Natural language pattern matching for memory commands
import os            # File system operations (memory storage paths)
import time          # Timing / debug utilities (optional tracing)
from uuid import uuid4
from datetime import datetime  # Timestamp generation for memory entries


# ============================================================
# EXTERNAL DEPENDENCIES (PIP INSTALLED PACKAGES)
# ============================================================
# Third-party libraries used for database connectivity
# and potential future expansion.
# ============================================================

import mysql.connector  # MySQL database connection (user + conversation storage)


# ============================================================
# INTERNAL SYSTEM IMPORTS (ARCHITECTURE LAYERS)
# ============================================================
# This file acts as the MEMORY INTERFACE LAYER:
#
# ROLE:
# - Bridge between AI system and storage systems
# - Handles ChromaDB + MySQL + JSON memory coordination
#
# RULES:
# - No AI reasoning allowed here
# - No orchestration logic
# - No tool execution
# - ONLY memory access + command handling
# ============================================================


# ------------------------------------------------------------
# CONFIGURATION LAYER
# (Central system configuration + environment variables)
# ------------------------------------------------------------
from core import config_loader


# ------------------------------------------------------------
# SYSTEM PATHS
# (Memory file locations, storage directories, etc.)
# ------------------------------------------------------------
from core import system_paths


# ------------------------------------------------------------
# SYSTEM UTILITIES
# (Helper functions like timestamps, safe strings, etc.)
# ------------------------------------------------------------
from core import system_utils


# ------------------------------------------------------------
# MEMORY DATABASE LAYER
# (ChromaDB + MySQL operations for persistent storage)
# ------------------------------------------------------------
from core.memory_database import (
    chroma_get_by_type,
    chroma_get_all,
)

from core.memory_database import get_memory_state as db_get_memory_state

def get_memory_state():
    return db_get_memory_state()
    
    
from core.memory_database import update_memory_state as db_update_memory_state

def update_memory_state(memory_state):
    return db_update_memory_state(memory_state)

from core.memory_database import (
    save_message_user as db_save_message_user,
    save_message_ai as db_save_message_ai,
)

def save_message_user(conversation_id, user_id, message):
    return db_save_message_user(conversation_id, user_id, message)

from core.memory_database import (
    get_user_settings as db_get_user_settings,
    upsert_user_settings as db_upsert_user_settings,
    get_user_personality_traits as db_get_user_personality_traits,
    add_user_personality_trait as db_add_user_personality_trait,
    update_user_personality_trait as db_update_user_personality_trait,
    create_aetheraeon_personality_trait as db_create_aetheraeon_personality_trait,
    update_aetheraeon_personality_trait as db_update_aetheraeon_personality_trait,
    delete_aetheraeon_personality_trait as db_delete_aetheraeon_personality_trait,
    add_personality_trait_feedback as db_add_personality_trait_feedback,
    get_personality_trait_feedback as db_get_personality_trait_feedback,
    get_personality_trait_history as db_get_personality_trait_history,
    get_personality_trait_candidates as db_get_personality_trait_candidates,
    delete_user_personality_trait as db_delete_user_personality_trait,
)

def get_user_settings(user_id: int) -> dict:
    return db_get_user_settings(user_id)

def upsert_user_settings(user_id: int, settings: dict) -> None:
    return db_upsert_user_settings(user_id, settings)

def get_user_personality_traits(user_id: int, owner=None, include_inactive=False) -> list[dict]:
    return db_get_user_personality_traits(user_id, owner, include_inactive)

def add_user_personality_trait(user_id: int, trait: str = None, **fields) -> dict | None:
    return db_add_user_personality_trait(user_id, trait, **fields)

def update_user_personality_trait(user_id: int, trait_id: int, changes: dict) -> dict | None:
    return db_update_user_personality_trait(user_id, trait_id, changes)

def create_aetheraeon_personality_trait(user_id: int, **fields) -> dict | None:
    return db_create_aetheraeon_personality_trait(user_id, **fields)

def update_aetheraeon_personality_trait(user_id: int, trait_id: int, changes: dict) -> dict | None:
    return db_update_aetheraeon_personality_trait(user_id, trait_id, changes)

def delete_aetheraeon_personality_trait(user_id: int, trait_id: int) -> bool:
    return db_delete_aetheraeon_personality_trait(user_id, trait_id)

def add_personality_trait_feedback(user_id: int, trait_id: int, correction: str) -> dict | None:
    return db_add_personality_trait_feedback(user_id, trait_id, correction)

def get_personality_trait_feedback(user_id: int) -> list[dict]:
    return db_get_personality_trait_feedback(user_id)

def get_personality_trait_history(user_id: int) -> list[dict]:
    return db_get_personality_trait_history(user_id)

def get_personality_trait_candidates(user_id: int, include_promoted=False) -> list[dict]:
    return db_get_personality_trait_candidates(user_id, include_promoted)

def delete_user_personality_trait(
    user_id: int,
    trait_id: int = None,
    trait: str = None
) -> bool:
    return db_delete_user_personality_trait(user_id, trait_id, trait)
    
# ------------------------------------------------------------
# MEMORY CONTEXT BUILDER
# (Used to format memory into AI-readable context blocks)
# ------------------------------------------------------------
from core.memory_database import fmt_entry

# ------------------------------------------------------------
# MEMORY INTERFACE WRAPPER (Chroma / Semantic Memory)
# ------------------------------------------------------------

from core.memory_database import delete_conversation as db_delete_conversation

def delete_conversation(conv_uuid: str, user_id: int) -> bool:
    return db_delete_conversation(conv_uuid, user_id)

from core.memory_database import pin_conversation as db_pin_conversation

def pin_conversation(conv_uuid: str, user_id: int, pinned: bool) -> bool:
    return db_pin_conversation(conv_uuid, user_id, pinned)

def save_message_user(conversation_id, user_id, content):
    return db_save_message_user(conversation_id, user_id, content)

def save_message_ai(
    conversation_id,
    user_id,
    content,
    tool_used=None,
    metadata=None,
):
    """Persist an AI reply through the database interface.

    ``tool_used`` and ``metadata`` remain optional so legacy three- and
    four-argument callers keep working. The database owns timestamp creation
    and accepts either structured metadata or an existing serialized value.
    """
    if metadata is not None:
        return db_save_message_ai(
            conversation_id, user_id, content, tool_used, metadata
        )
    if tool_used is not None:
        return db_save_message_ai(conversation_id, user_id, content, tool_used)
    return db_save_message_ai(conversation_id, user_id, content)
    
# ============================================================
# MEMORY STORAGE INTERFACE
# ============================================================
# Stores semantic memories through the centralized
# ChromaDB persistence layer.
# ============================================================

from core.memory_database import chroma_store


def memory_store(
    text,
    meta=None
):
    """
    Store semantic memory in the centralized memory database.
    """

    return chroma_store(
        text,
        meta
    )



# ============================================================
# MEMORY RECALL INTERFACE
# ============================================================
# Performs semantic memory retrieval through the centralized
# ChromaDB memory database layer.
# ============================================================

from core.memory_database import chroma_recall_with_meta
from core.retrieval_coordinator import ChromaRetrievalAdapter, CoordinatedRetrieval


def memory_recall_with_contract(
    query,
    n=5,
    user_id=None,
    return_status=False,
    *,
    trace_id=None,
) -> CoordinatedRetrieval:
    """Observe an unchanged existing ChromaDB recall through RetrievalResult.

    The existing recall callable receives the same arguments as the legacy
    wrapper.  This helper is the Phase 6 structured retrieval boundary; it
    neither selects memory policy nor transforms, filters, injects, or stores
    the returned content.
    """

    result_limit = n if isinstance(n, int) and not isinstance(n, bool) and n >= 0 else None
    correlation_id = trace_id or f"retrieval-{uuid4().hex}"
    return ChromaRetrievalAdapter(chroma_recall_with_meta).retrieve(
        query,
        n,
        user_id=user_id,
        return_status=return_status,
        trace_id=correlation_id,
        result_limit=result_limit,
        raise_on_error=True,
    )


def memory_recall(
    query,
    n=5,
    user_id=None,
    return_status=False,
):
    """
    Retrieve semantic memories with metadata from ChromaDB.
    """

    return memory_recall_with_contract(
        query,
        n,
        user_id=user_id,
        return_status=return_status,
    ).raw_output
    

# ============================================================
# MEMORY UPDATE INTERFACE
# ============================================================
# Updates an existing semantic memory through the centralized
# ChromaDB memory database layer.
# ============================================================

from core.memory_database import chroma_update_by_id


def memory_update(
    memory_id,
    new_text,
    new_metadata=None,
    *,
    return_receipt=False,
):
    """
    Update an existing memory entry and optionally replace
    its metadata.
    """

    success = chroma_update_by_id(
        memory_id,
        new_text,
        new_metadata
    )
    if not return_receipt:
        return success
    return {
        "operation": "update",
        "memory_id": memory_id,
        "success": bool(success),
        "status": "completed" if success else "failed",
        "reason": None if success else "ChromaDB did not confirm the update.",
    }


# ============================================================
# MEMORY DELETE INTERFACE
# ============================================================
# Deletes a semantic memory through the centralized
# ChromaDB memory database layer.
# ============================================================

from core.memory_database import chroma_delete_by_id


def memory_delete(
    memory_id,
    *,
    return_receipt=False,
):
    """
    Delete a memory entry by its unique identifier.
    """

    success = chroma_delete_by_id(memory_id)
    if not return_receipt:
        return success
    return {
        "operation": "delete",
        "memory_id": memory_id,
        "success": bool(success),
        "status": "completed" if success else "failed",
        "reason": None if success else "ChromaDB did not confirm the deletion.",
    }
    
from core.memory_database import create_conversation as db_create_conversation

def create_conversation(user_id: int, conv_uuid: str, name: str = "New Conversation") -> None:
    """
    Creates a new conversation record in the database.
    Interface layer isolates API from DB implementation.
    """

    return db_create_conversation(user_id, conv_uuid, name)
   
   
# ============================================================
# MEMORY CLASSIFICATION SCHEMA
# ============================================================
# Defines all valid memory categories used across:
# - ChromaDB tagging
# - memory commands
# - filtering + search
# ============================================================

MEMORY_TYPES = [
    "user_fact",
    "navigation",
    "code_edit",
    "playbook",
    "shortcut",
    "config",
    "conversation",
    "n8n",
    "system_event",
    "preference",
    "general"
]

# ============================================================
# MEMORY DUPLICATE DETECTION
# ============================================================
# Wrapper around the ChromaDB similarity search.
#
# PURPOSE:
# Prevent duplicate or near-duplicate memories from being
# stored in the long-term memory database.
# ============================================================

from core.memory_database import chroma_exists_similar

def memory_exists_similar(
    text,
    threshold=0.95,
    user_id=None,
):
    """
    Returns True if a semantically similar memory already exists.
    """

    return chroma_exists_similar(
        text,
        threshold,
        user_id=user_id,
    )

# ============================================================
# MEMORY LOADER (LOCAL FILE BACKEND)
# ============================================================

def load_memory():
    """
    ============================================================
    MEMORY LOAD SYSTEM (MODERN ARCHITECTURE)
    ============================================================

    PURPOSE:
    Load runtime memory from the active memory database layer.

    DESIGN:
    - No file-based persistence
    - No JSON storage
    - No legacy migration
    - Pure database-backed memory state

    RETURNS:
    dict → structured in-memory state
    ============================================================
    """

    # --------------------------------------------------------
    # 1. LOAD FROM MEMORY DATABASE LAYER
    # --------------------------------------------------------
    # Centralized memory system (ChromaDB / memory_database.py)
    # --------------------------------------------------------

    try:

        memory_state = get_memory_state()

        if memory_state is None:
            return {}

        return memory_state

    except Exception as error:

        # ----------------------------------------------------
        # SAFE FALLBACK (NO FILE IO)
        # ----------------------------------------------------
        # System should NEVER touch disk for memory fallback
        # ----------------------------------------------------

        print(f"[MEMORY ERROR] load_memory failed: {error}")

        return {}
    
    
    
# ============================================================
# MEMORY PERSISTENCE SAVER (LOCAL JSON STORAGE)
# ============================================================

def save_memory(memory_data: dict):
    """
    ============================================================
    MEMORY SAVE SYSTEM (MODERN ARCHITECTURE)
    ============================================================

    PURPOSE:
    Persist memory state through the database abstraction layer.

    DESIGN:
    - No file system access
    - No JSON serialization
    - No disk writes
    - Centralized persistence only

    RESPONSIBILITY:
    Forward memory state to memory_database layer.
    """

    try:

        # --------------------------------------------------------
        # DATABASE LAYER DELEGATION
        # --------------------------------------------------------
        # All persistence handled in memory_database.py
        # --------------------------------------------------------

        if not memory_data:
            return False

        update_memory_state(memory_data)

        return True

    except Exception as error:

        print(f"[MEMORY ERROR] save_memory failed: {error}")

        return False
        
        
# ============================================================
# MEMORY TEXT EXTRACTION
# ============================================================
# Purpose:
# Extract readable text content from a memory record.
#
# Supported Types:
# - dict    → memory["text"]
# - tuple   → second element
# - str     → returned directly
#
# Returns:
# Text string or None
# ============================================================

def extract_memory_text(memory_record):

    # --------------------------------------------------------
    # Null Protection
    # --------------------------------------------------------

    if memory_record is None:
        return None

    # --------------------------------------------------------
    # Dictionary Memory Record
    # --------------------------------------------------------

    if isinstance(memory_record, dict):

        return memory_record.get("text")

    # --------------------------------------------------------
    # Tuple Memory Record
    # --------------------------------------------------------

    if isinstance(memory_record, tuple):

        if len(memory_record) >= 2:
            return memory_record[1]

        return None

    # --------------------------------------------------------
    # Plain String Memory
    # --------------------------------------------------------

    if isinstance(memory_record, str):
        return memory_record

    # --------------------------------------------------------
    # Unsupported Memory Type
    # --------------------------------------------------------

    return None        
