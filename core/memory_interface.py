"""
========================================================
AETHERAEON — MEMORY INTERFACE (MEMORY ACCESS ABSTRACTION LAYER)
========================================================

FILE PURPOSE:

This file provides the unified memory and persistence access
interface for the Aetheraeon AI system.

It acts as the abstraction boundary between AI intelligence
layers and underlying storage implementations.

Higher-level AI components should communicate through this
layer instead of directly accessing:

- MariaDB
- ChromaDB
- Repository modules
- Storage implementations

========================================================
SYSTEM ROLE:

"Memory Access Gateway Layer"

This file provides:

- Unified memory operations
- Storage abstraction
- Data translation
- Persistence access routing
- Normalized memory responses

It does NOT create intelligence.

It only provides controlled access to stored information.

========================================================
ARCHITECTURAL PURPOSE:

The Memory Interface exists to protect AI layers from
storage implementation changes.

Current:

ai_orchestrator.py
        ↓
memory_interface.py
        ↓
memory_database.py
        ↓
MariaDB / ChromaDB


Future:

ai_orchestrator.py
        ↓
memory_interface.py
        ↓
Repository Layer
        ↓
Database / Vector Storage


The AI architecture should not need to change when the
storage architecture changes.

========================================================
RESPONSIBILITIES:
(memory_interface.py)

- Provide unified memory access functions
- Provide conversation storage access
- Provide message storage access
- Provide user settings access
- Provide semantic memory operations
- Normalize storage results
- Bridge AI layers with persistence layers
- Maintain storage abstraction boundaries

========================================================
STRICT BOUNDARIES (DO NOT BREAK):

(memory_interface.py)

This file MUST NOT:

- Perform AI reasoning
  (ai_orchestrator.py handles this)

- Generate AI responses
  (llm_interface.py handles model communication)

- Execute tools
  (tool_executor.py handles execution)

- Perform HTTP/API routing
  (api_gateway.py handles transport)

- Build cognitive context
  (memory_context_builder.py handles this)

- Implement database engines
  (database/repository layers handle storage)

This file ONLY provides access abstraction.

========================================================
MEMORY INTERFACE FLOW:

AI Request

    ↓

ai_orchestrator.py

    ↓

memory_interface.py

    ↓

Storage Provider

(memory_database.py currently)

    ↓

MariaDB / ChromaDB

    ↓

Normalized Result

    ↓

ai_orchestrator.py
or
memory_context_builder.py

========================================================
SYSTEM WIDE MEMORY FLOW:

User Input

    ↓

api_gateway.py

    ↓

request_router.py

    ↓

ai_orchestrator.py

    ↓

memory_interface.py   ← THIS FILE

    ↓

memory_database.py

    ↓

MariaDB / ChromaDB

    ↓

memory_context_builder.py

    ↓

llm_interface.py

    ↓

AI Response

========================================================
KEY FILE DEPENDENCIES:

Current:

memory_interface.py depends on:

- memory_database.py
- config_loader.py
- agent_identity.py


Used by:

- ai_orchestrator.py
- request_router.py
- memory_context_builder.py

========================================================
CORE FUNCTIONS:
(memory_interface.py)

Memory State:

- get_memory_state()
- update_memory_state()

Conversation:

- create_conversation()
- delete_conversation()
- pin_conversation()

Messages:

- save_message_user()
- save_message_ai()

User Settings:

- get_user_settings()

Semantic Memory:

- memory_store()
- memory_recall()
- memory_update()
- memory_delete()
- memory_exists_similar()

Memory Persistence:

- load_memory()
- save_memory()

Utility:

- extract_memory_text()

========================================================
OUTPUT CONTRACT:

(memory_interface.py returns)

- normalized memory objects
- conversation records
- message records
- user settings
- semantic recall results
- storage operation results
- success/failure states

========================================================
FUTURE ARCHITECTURE ROLE:

memory_interface.py becomes the permanent abstraction
gateway for all memory and persistence operations.

Future repository structure:

memory_interface.py

        ↓

├── user_repository.py
├── conversation_repository.py
├── settings_repository.py
├── playbook_repository.py
└── memory_repository.py

        ↓

MariaDB / ChromaDB

========================================================
DESIGN PHILOSOPHY:

"Memory Should Be Accessible Without Knowing Storage"

- Orchestrator THINKS
- MemoryInterface CONNECTS
- ContextBuilder STRUCTURES
- Repository Layer STORES
- Database Layer PERSISTS
- LLMInterface COMMUNICATES

This separation allows Aetheraeon AI to evolve its
memory architecture without rewriting intelligence layers.

========================================================
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
    delete_user_personality_trait as db_delete_user_personality_trait,
)

def get_user_settings(user_id: int) -> dict:
    return db_get_user_settings(user_id)

def upsert_user_settings(user_id: int, settings: dict) -> None:
    return db_upsert_user_settings(user_id, settings)

def get_user_personality_traits(user_id: int) -> list[dict]:
    return db_get_user_personality_traits(user_id)

def add_user_personality_trait(user_id: int, trait: str) -> dict | None:
    return db_add_user_personality_trait(user_id, trait)

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

def save_message_ai(conversation_id, user_id, content, tool_used=None):
    return db_save_message_ai(conversation_id, user_id, content, tool_used)
    
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


def memory_recall(
    query,
    n=5
):
    """
    Retrieve semantic memories with metadata from ChromaDB.
    """

    return chroma_recall_with_meta(
        query,
        n
    )
    

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
    new_metadata=None
):
    """
    Update an existing memory entry and optionally replace
    its metadata.
    """

    return chroma_update_by_id(
        memory_id,
        new_text,
        new_metadata
    )


# ============================================================
# MEMORY DELETE INTERFACE
# ============================================================
# Deletes a semantic memory through the centralized
# ChromaDB memory database layer.
# ============================================================

from core.memory_database import chroma_delete_by_id


def memory_delete(
    memory_id
):
    """
    Delete a memory entry by its unique identifier.
    """

    return chroma_delete_by_id(
        memory_id
    )
    
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
    threshold=0.95
):
    """
    Returns True if a semantically similar memory already exists.
    """

    return chroma_exists_similar(
        text,
        threshold
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
