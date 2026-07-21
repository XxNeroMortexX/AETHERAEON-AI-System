"""
Aetheraeon AI - Persistence Database

Purpose:
Provides the current persistence implementation for structured application data and long-term semantic memory.

Architecture Layer:
Persistence and Storage Layer.

Responsibilities:
- Execute current MariaDB operations for users, settings, conversations, messages, and related records.
- Execute current ChromaDB operations for approved long-term semantic-memory storage and recall.
- Return structured persistence results, identifiers, and failure information to calling interfaces.

Boundaries:
- Storage persists approved information; it does not decide significance, scope, candidacy, retrieval policy, or cognitive truth.
- ChromaDB is the current semantic-memory implementation, not a permanent architectural requirement.
- This module does not automatically forget, expire, or delete retained memory without an authorized operation.
- Planned repository decomposition is not implemented merely by this module header.
"""


# ============================================================
# CORE STANDARD LIBRARY IMPORTS
# ============================================================
# Built-in Python modules used for:
# - ID generation
# - text processing
# - pattern matching
# ============================================================

import base64
import binascii
import json
import re     # Text chunking, filtering, and pattern cleanup
import uuid   # Unique identifiers for memory entries (ChromaDB + SQL IDs)


# ============================================================
# EXTERNAL DEPENDENCIES (PIP INSTALLED PACKAGES)
# ============================================================
# Third-party libraries required for database and vector memory
# ============================================================

import mysql.connector   # MySQL relational database driver
import chromadb           # Vector database for long-term memory storage


# ============================================================
# INTERNAL SYSTEM IMPORTS (ARCHITECTURE LAYER BOUNDARY)
# ============================================================
# ONLY low-level system utilities allowed in this file.
# NO AI, NO routing, NO tool execution imports.
# ============================================================

from core import config_loader     # Database credentials + environment config
from core import system_paths      # Path resolution utilities (safe file handling)
from core import system_utils      # Safe helpers (timestamps, string cleaning, etc.)
from core.system_utils import get_utc_timestamp

# ============================================================
# CHROMADB RUNTIME STATE
# ============================================================
# Active ChromaDB connection objects.
#
# This module owns the vector memory database.
# Other modules should access Chroma through
# get_chroma_collection().
# ============================================================

CHROMA_AVAILABLE = False
CHROMA_CLIENT = None
CHROMA_COLLECTION = None

# ============================================================
# RUNTIME MEMORY STATE
# ============================================================
# Temporary runtime memory cache used by:
#
# - ai_orchestrator.py
# - api_gateway.py
# - memory_interface.py
#
# Long-term memories remain in ChromaDB.
# ============================================================

MEMORY_STATE = {}

# Last memory search/display results.
# Used for resolving memory selection operations.
_LAST_MEMORY_LIST = []


# ============================================================
# LAST MEMORY LIST ACCESS
# ============================================================

def get_last_memory_list():
    """
    Returns the most recent memory search results.

    Used by:
    - memory edit
    - memory delete
    - UI memory selection
    """

    return _LAST_MEMORY_LIST
    

# ============================================================
# LAST MEMORY LIST ACCESS
# ============================================================
# PURPOSE:
# Stores the most recently displayed memory results.
#
# RESPONSIBILITY:
# - Keeps numeric memory references stable
#   (memory edit 3, memory delete 2, etc.)
# - Centralizes ownership of runtime memory state
# - Prevents other modules from modifying globals directly
# ============================================================

def update_last_memory_list(memory_list):
    """
    Replace the cached list of recently displayed memories.

    Args:
        memory_list (list):
            Latest memory entries shown to the user.
    """

    global _LAST_MEMORY_LIST

    _LAST_MEMORY_LIST = list(memory_list or [])

    
# ============================================================
# MEMORY STATE RETRIEVAL
# ============================================================
# Returns active runtime memory state.
# ============================================================

def get_memory_state():
    """
    Return active runtime memory state.

    Returns:
        dict
    """

    return MEMORY_STATE
    
    
# ============================================================
# MEMORY STATE UPDATE
# ============================================================
# Updates active runtime memory state.
# ============================================================

def update_memory_state(memory_state):
    """
    Replace active runtime memory state.

    Args:
        memory_state (dict)
    """

    global MEMORY_STATE

    MEMORY_STATE = dict(memory_state or {})



# ============================================================
# CHROMADB MEMORY SYSTEM HEALTH CHECK
# ============================================================
# PURPOSE:
# Initializes and validates the ChromaDB vector memory system.
#
# This system powers long-term semantic memory storage for AI.
# If this fails, AI memory persistence is disabled.
# ============================================================

def check_chromadb():
    """
    ChromaDB Initialization & Health Validation
    -------------------------------------------
    - Loads persistent ChromaDB client
    - Creates or loads memory collection
    - Updates system-wide memory availability flags
    - Returns success/failure state
    """

    # --------------------------------------------------------
    # GLOBAL MEMORY SYSTEM STATE
    # --------------------------------------------------------
    # These globals are used across memory_interface and
    # memory_database layers to determine availability.
    # --------------------------------------------------------

    global CHROMA_AVAILABLE
    global CHROMA_CLIENT
    global CHROMA_COLLECTION

    try:

        # ----------------------------------------------------
        # INITIALIZE PERSISTENT VECTOR DATABASE
        # ----------------------------------------------------
        # This creates or connects to local memory storage.
        # ----------------------------------------------------

        CHROMA_CLIENT = chromadb.PersistentClient(
            path=str(system_paths.AISYSTEM_ROOT / "chroma_memory")
        )

        CHROMA_COLLECTION = CHROMA_CLIENT.get_or_create_collection(
            "aetheraeon"
        )

        # ----------------------------------------------------
        # UPDATE SYSTEM STATE FLAGS
        # ----------------------------------------------------

        CHROMA_AVAILABLE = True

        # ----------------------------------------------------
        # DEBUG OUTPUT (SYSTEM VERIFICATION)
        # ----------------------------------------------------
        # Provides insight into memory system health.
        # ----------------------------------------------------

        record_count = CHROMA_COLLECTION.count()

        print("  [OK]   ChromaDB -> loaded successfully")
        print(f"         Memory records: {record_count}")
        print("         Collection: aetheraeon")

        return True

    except ImportError:
        # ----------------------------------------------------
        # MISSING DEPENDENCY ERROR
        # ----------------------------------------------------

        CHROMA_AVAILABLE = False
        CHROMA_CLIENT = None
        CHROMA_COLLECTION = None


        print(
            "  [FAIL] ChromaDB -> not installed\n"
            "         Install with: pip install chromadb"
        )

        return False

    except Exception as error:
        # ----------------------------------------------------
        # GENERAL INITIALIZATION FAILURE
        # ----------------------------------------------------

        CHROMA_AVAILABLE = False
        CHROMA_CLIENT = None
        CHROMA_COLLECTION = None

        print(f"  [FAIL] ChromaDB -> initialization error: {error}")

        return False

        
# ============================================================
# CHROMADB COLLECTION ACCESS
# ============================================================

def get_chroma_collection():
    """
    Retrieve the active global ChromaDB collection instance.

    PURPOSE:
    - Ensures ChromaDB is initialized before usage
    - Returns the active shared collection object
    - Prevents downstream calls from accessing a null collection

    RETURNS:
    - ChromaDB collection object
    - None if initialization failed
    """

    # --------------------------------------------------------
    # INITIALIZE CHROMADB COLLECTION IF NOT READY
    # --------------------------------------------------------
    # The collection is lazily initialized so startup does not
    # immediately fail if ChromaDB is temporarily unavailable.
    # --------------------------------------------------------
    if CHROMA_COLLECTION is None:

        chromadb_ready = check_chromadb()

        if not chromadb_ready:
            return None

    # --------------------------------------------------------
    # RETURN ACTIVE SHARED COLLECTION INSTANCE
    # --------------------------------------------------------
    return CHROMA_COLLECTION


def initialize_memory() -> bool:
    """Ensure the shared ChromaDB client and collection are ready."""

    return get_chroma_collection() is not None


def get_memory_count() -> int:
    """Return the current collection size, initializing ChromaDB if needed."""

    collection = get_chroma_collection()
    return collection.count() if collection is not None else 0
    
    
# ============================================================
# CHROMADB MEMORY STORAGE ENGINE
# ============================================================

def chroma_store(text, meta=None):
    """
    ============================================================
    CHROMADB — MEMORY INGESTION PIPELINE
    ============================================================

    PURPOSE:
    This function is responsible for safely storing long-term
    memory into ChromaDB vector storage.

    It ensures:
    - Only meaningful user/AI content is stored
    - System noise and debug logs are filtered out
    - Input is broken into atomic semantic chunks
    - Metadata is normalized and enriched
    - Each memory entry is stored as a separate embedding

    ============================================================
    MEMORY SAFETY RULES:
    ============================================================

    This function MUST NOT store:
    - Debug logs or runtime traces
    - Tool execution output
    - Router/system explanations
    - Internal AI reasoning text

    Only store:
    - User facts
    - Conversation content
    - Meaningful AI responses
    - Semantic memory-worthy information
    """

    # ─────────────────────────────────────────────
    # 0. SYSTEM CHECK — CHROMADB AVAILABILITY
    # ─────────────────────────────────────────────
    # ─────────────────────────────────────────────
    # 1. INPUT NORMALIZATION
    # ─────────────────────────────────────────────
    # Ensure all inputs are safe, clean strings before processing
    # ─────────────────────────────────────────────

    if isinstance(text, bytes):
        text = text.decode("utf-8", errors="ignore")

    text = str(text).strip()

    if not text:
        return {
            "success": False,
            "ids": [],
            "count": 0,
            "reason": "Memory content is empty.",
        }

    # ─────────────────────────────────────────────
    # 2. SYSTEM NOISE FILTERING
    # ─────────────────────────────────────────────
    # Prevent accidental storage of logs or system-level output
    # that would pollute long-term semantic memory
    # ─────────────────────────────────────────────

    noise_signatures = (
        "[DEBUG]",
        "[TRACE]",
        "[PROCESS]",
        "AI ERROR",
        "router model",
        "Internal error",
        "b'",
    )

    if any(text.startswith(sig) for sig in noise_signatures):
        return {
            "success": False,
            "ids": [],
            "count": 0,
            "reason": "Memory content was rejected by the system-noise filter.",
        }

    if "AI explained" in text or "Tool usage rules" in text:
        return {
            "success": False,
            "ids": [],
            "count": 0,
            "reason": "Memory content was rejected by the memory safety filter.",
        }

    # ─────────────────────────────────────────────
    # 3. SEMANTIC CHUNKING ENGINE
    # ─────────────────────────────────────────────
    # Break input into atomic memory units for better embeddings
    # Each chunk represents a single semantic idea
    # ─────────────────────────────────────────────

    raw_sentences = re.split(r"\n+|\.\s+", text)

    memory_chunks = []

    for sentence in raw_sentences:
        sentence = sentence.strip()

        # Require meaningful semantic weight (avoid fragments)
        if len(sentence.split()) >= 4:
            memory_chunks.append(sentence)

    # Fallback safety — ensure at least one entry
    if not memory_chunks:
        memory_chunks = [text]

    # ─────────────────────────────────────────────
    # 4. MEMORY TYPE CLASSIFICATION ENGINE
    # ─────────────────────────────────────────────

    def classify_memory_type(content: str) -> str:
        content_lower = content.lower()

        if any(k in content_lower for k in ("meditation", "energy", "vibration")):
            return "spiritual"

        if "my name" in content_lower or "name is" in content_lower:
            return "identity"

        if "ai" in content_lower or "system" in content_lower:
            return "system_note"

        return "general"

    # ─────────────────────────────────────────────
    # 5. METADATA NORMALIZATION LAYER
    # ─────────────────────────────────────────────

    base_metadata = {
        "type": "general",
        "timestamp": get_utc_timestamp(),
        "source": "user"
    }

    explicit_memory_type = None

    if meta:
        sanitized_meta = {}

        for key, value in meta.items():

            if isinstance(value, bytes):
                value = value.decode("utf-8", errors="ignore")

            sanitized_meta[key] = str(value)

        base_metadata.update(sanitized_meta)
        explicit_memory_type = str(sanitized_meta.get("type") or "").strip() or None

    # ─────────────────────────────────────────────
    # 6. PERSISTENCE LAYER — CHROMADB INSERTION
    # ─────────────────────────────────────────────

    collection = get_chroma_collection()
    if collection is None:
        return {
            "success": False,
            "ids": [],
            "count": 0,
            "reason": "ChromaDB collection is unavailable.",
        }

    stored_ids = []
    for memory_text in memory_chunks:

        memory_type = explicit_memory_type or classify_memory_type(memory_text)

        final_metadata = dict(base_metadata)
        final_metadata["type"] = memory_type

        memory_id = str(uuid.uuid4())
        try:
            collection.add(
                documents=[memory_text],
                metadatas=[final_metadata],
                ids=[memory_id]
            )
            stored_ids.append(memory_id)
        except Exception as error:
            return {
                "success": False,
                "ids": stored_ids,
                "count": len(stored_ids),
                "reason": str(error) or type(error).__name__,
            }

    return {
        "success": bool(stored_ids),
        "ids": stored_ids,
        "count": len(stored_ids),
        "reason": None if stored_ids else "ChromaDB did not insert a memory.",
    }
        
        
# ============================================================
# CHROMADB — BASIC SEMANTIC RECALL ENGINE
# ============================================================

def chroma_recall(query, n=3):
    """
    ============================================================
    CHROMADB — BASIC MEMORY RECALL
    ============================================================

    PURPOSE:
    Performs a lightweight semantic search against ChromaDB.

    USE CASES:
    - Fast memory lookup
    - Chat context retrieval
    - Simple semantic similarity search

    RETURNS:
    - List of matching document strings
    - Empty list on failure or no matches
    """

    # ─────────────────────────────────────────────
    # 1. SAFETY & VALIDATION GUARDS
    # ─────────────────────────────────────────────

    if not query:
        return []

    # ─────────────────────────────────────────────
    # 2. COLLECTION ACCESS LAYER
    # ─────────────────────────────────────────────

    collection = get_chroma_collection()

    if collection is None:
        return []

    # ─────────────────────────────────────────────
    # 3. VECTOR SEARCH EXECUTION
    # ─────────────────────────────────────────────

    try:
        search_results = collection.query(
            query_texts=[query],
            n_results=n
        )

        # ─────────────────────────────────────────────
        # 4. RESPONSE NORMALIZATION
        # ─────────────────────────────────────────────
        # ChromaDB returns nested structure:
        # {
        #   "documents": [[...results...]]
        # }
        # We extract the first result batch safely
        # ─────────────────────────────────────────────

        documents = search_results.get("documents", [[]])[0]
        return documents

    except Exception:
        # ─────────────────────────────────────────────
        # 5. FAILSAFE ERROR HANDLING
        # ─────────────────────────────────────────────
        return []


# ============================================================
# CHROMADB — SEMANTIC RECALL (WITH METADATA)
# ============================================================

def chroma_recall_with_meta(query, n=5, user_id=None, return_status=False):
    """
    ============================================================
    CHROMADB — FULL MEMORY RECALL (IDS + CONTENT + METADATA)
    ============================================================

    PURPOSE:
    Performs semantic vector search and returns full memory
    structure including:

    - Memory ID
    - Stored document text
    - Associated metadata

    USED FOR:
    - Debugging memory state
    - Advanced AI reasoning
    - Context reconstruction
    - Memory auditing
    """

    # ─────────────────────────────────────────────
    # 1. SAFETY GUARDS
    # ─────────────────────────────────────────────

    def recall_result(results, attempted, completed, error=None):
        if return_status:
            return results, {
                "attempted": bool(attempted),
                "completed": bool(completed),
                "error": str(error) if error else None,
            }
        return results

    if not query:
        return recall_result([], False, False, "Memory search query is empty.")

    # ─────────────────────────────────────────────
    # 2. COLLECTION ACCESS LAYER
    # ─────────────────────────────────────────────

    collection = get_chroma_collection()

    if collection is None:
        return recall_result([], True, False, "ChromaDB collection is unavailable.")

    # ─────────────────────────────────────────────
    # 3. VECTOR SEARCH EXECUTION
    # ─────────────────────────────────────────────

    try:
        query_options = {
            "query_texts": [query],
            "n_results": n,
            "include": ["documents", "metadatas", "distances"],
        }
        if user_id is not None:
            query_options["where"] = {"user_id": str(user_id)}
        search_results = collection.query(
            **query_options
        )

        print("[CHROMA SEARCH DEBUG]")
        print(search_results.get("distances"))
        

        # ─────────────────────────────────────────────
        # 4. RESPONSE NORMALIZATION
        # ─────────────────────────────────────────────
        # ChromaDB returns structured response:
        #
        # {
        #   "ids": [[...]],
        #   "documents": [[...]],
        #   "metadatas": [[...]]
        # }
        #
        # We safely extract first batch of results
        # and zip them into structured tuples
        # ─────────────────────────────────────────────

        ids = search_results.get("ids", [[]])[0]
        documents = search_results.get("documents", [[]])[0]
        metadatas = search_results.get("metadatas", [[]])[0]

        distances = search_results.get("distances", [[]])[0]

        results = []

        # --------------------------------------------------------
        # SEMANTIC DISTANCE FILTER
        # --------------------------------------------------------
        # Lower Chroma distance = closer semantic match.
        # Prevents unrelated memories from being returned.
        # --------------------------------------------------------

        CHROMA_DISTANCE_THRESHOLD = 1.73

        print("[CHROMA MATCH DEBUG]")

        for memory_id, document, metadata, distance in zip(
            ids,
            documents,
            metadatas,
            distances
        ):

            print(memory_id, distance)

            if distance <= CHROMA_DISTANCE_THRESHOLD:

                results.append(
                    (
                        memory_id,
                        document,
                        metadata
                    )
                )

        return recall_result(results, True, True)

    except Exception as error:
        # ─────────────────────────────────────────────
        # 5. FAILSAFE ERROR HANDLING
        # ─────────────────────────────────────────────
        return recall_result([], True, False, error)
        
        

# ============================================================
# CHROMADB — MEMORY FILTERING BY TYPE
# ============================================================

def chroma_get_by_type(mtype, limit=50, user_id=None):
    """
    ============================================================
    CHROMADB — FILTERED MEMORY RETRIEVAL (BY TYPE)
    ============================================================

    PURPOSE:
    Retrieves stored memory entries filtered by semantic type.

    USED FOR:
    - Identity memory lookup
    - Spiritual memory filtering
    - System categorization views
    - Debugging memory segmentation

    RETURNS:
    List of tuples:
        (id, document, metadata)
    """

    # ─────────────────────────────────────────────
    # 1. SAFETY GUARD
    # ─────────────────────────────────────────────

    if not mtype:
        return []

    # ─────────────────────────────────────────────
    # 2. COLLECTION ACCESS LAYER
    # ─────────────────────────────────────────────

    collection = get_chroma_collection()

    if collection is None:
        return []

    # ─────────────────────────────────────────────
    # 3. FILTERED QUERY EXECUTION
    # ─────────────────────────────────────────────

    try:
        where = {"type": mtype}
        if user_id is not None:
            where = {"$and": [{"type": mtype}, {"user_id": str(user_id)}]}
        search_results = collection.get(where=where, limit=limit)

        # ─────────────────────────────────────────────
        # 4. RESPONSE NORMALIZATION
        # ─────────────────────────────────────────────
        # ChromaDB returns flat arrays:
        #
        # {
        #   "ids": [...],
        #   "documents": [...],
        #   "metadatas": [...]
        # }
        #
        # We normalize into structured tuples for system use
        # ─────────────────────────────────────────────

        ids = search_results.get("ids", [])
        documents = search_results.get("documents", [])
        metadatas = search_results.get("metadatas", [])

        results = list(zip(ids, documents, metadatas))
        return results

    except Exception:
        # ─────────────────────────────────────────────
        # 5. FAILSAFE ERROR HANDLING
        # ─────────────────────────────────────────────
        return []
        
        
        
# ============================================================
# CHROMADB — FULL MEMORY RETRIEVAL (ALL ENTRIES)
# ============================================================

def chroma_get_all(limit=200, user_id=None, return_diagnostics=False):
    """
    ============================================================
    CHROMADB — FULL MEMORY DUMP (ADMIN / DEBUG USE)
    ============================================================

    PURPOSE:
    Retrieves all stored memory entries from ChromaDB.

    USED FOR:
    - Admin memory inspection
    - Debugging vector database state
    - API endpoint: /api/memory/all
    - System diagnostics

    WARNING:
    This bypasses semantic filtering and returns raw dataset.
    Should NOT be used in AI reasoning pipelines.
    """

    # ─────────────────────────────────────────────
    # 1. SAFETY GUARD
    # ─────────────────────────────────────────────

    # ─────────────────────────────────────────────
    # 2. COLLECTION ACCESS LAYER
    # ─────────────────────────────────────────────

    collection = get_chroma_collection()

    if collection is None:
        diagnostics = {"completed": False, "error": "collection_unavailable"}
        return ([], diagnostics) if return_diagnostics else []

    # ─────────────────────────────────────────────
    # 3. RAW DATA RETRIEVAL
    # ─────────────────────────────────────────────

    try:
        options = {"limit": limit}
        if user_id is not None:
            options["where"] = {"user_id": str(user_id)}
        search_results = collection.get(**options)

        # ─────────────────────────────────────────────
        # 4. RESPONSE NORMALIZATION
        # ─────────────────────────────────────────────
        # ChromaDB returns:
        #
        # {
        #   "ids": [...],
        #   "documents": [...],
        #   "metadatas": [...]
        # }
        #
        # We convert into structured tuples for API use
        # ─────────────────────────────────────────────

        ids = search_results.get("ids", [])
        documents = search_results.get("documents", [])
        metadatas = search_results.get("metadatas", [])

        results = list(zip(ids, documents, metadatas))
        diagnostics = {"completed": True, "error": None}
        return (results, diagnostics) if return_diagnostics else results

    except Exception as error:
        # ─────────────────────────────────────────────
        # 5. FAILSAFE ERROR HANDLING
        # ─────────────────────────────────────────────
        diagnostics = {
            "completed": False,
            "error": type(error).__name__,
        }
        return ([], diagnostics) if return_diagnostics else []
        
        
# ============================================================
# CHROMADB — DELETE MEMORY ENTRY (BY ID)
# ============================================================

def _chroma_entry_exists(collection, memory_id):
    """Confirm that a specific Chroma record currently exists."""

    try:
        result = collection.get(ids=[memory_id])
    except Exception:
        return False

    ids = result.get("ids") if isinstance(result, dict) else None
    return isinstance(ids, list) and memory_id in ids


def _chroma_entry_text_matches(collection, memory_id, expected_text):
    """Confirm that a completed update is visible through Chroma."""

    try:
        result = collection.get(ids=[memory_id], include=["documents"])
    except Exception:
        return False

    if not isinstance(result, dict):
        return False
    return (
        memory_id in (result.get("ids") or [])
        and expected_text in (result.get("documents") or [])
    )


def chroma_delete_by_id(memory_id):
    """
    ============================================================
    CHROMADB — DELETE MEMORY ENTRY
    ============================================================

    PURPOSE:
    Deletes a specific memory entry from ChromaDB using its ID.

    USED FOR:
    - Memory cleanup
    - User-triggered deletion
    - API: /api/memory/delete
    - Privacy / data removal requests

    SAFETY NOTE:
    This operation is permanent and cannot be undone.
    """

    # ─────────────────────────────────────────────
    # 1. SAFETY GUARD (SYSTEM STATE CHECK)
    # ─────────────────────────────────────────────

    if not memory_id:
        return False

    # ─────────────────────────────────────────────
    # 2. COLLECTION ACCESS LAYER
    # ─────────────────────────────────────────────

    collection = get_chroma_collection()

    if collection is None:
        return False

    # ─────────────────────────────────────────────
    # 3. DELETE OPERATION (IMMUTABLE ACTION)
    # ─────────────────────────────────────────────

    try:
        if not _chroma_entry_exists(collection, memory_id):
            return False
        collection.delete(ids=[memory_id])
        return not _chroma_entry_exists(collection, memory_id)

    except Exception:
        # ─────────────────────────────────────────────
        # 4. FAILSAFE ERROR HANDLING
        # ─────────────────────────────────────────────
        return False



# ============================================================
# CHROMADB — UPDATE MEMORY ENTRY (BY ID)
# ============================================================

def chroma_update_by_id(memory_id, new_text, new_metadata=None):
    """
    ============================================================
    CHROMADB — UPDATE MEMORY ENTRY
    ============================================================

    PURPOSE:
    Updates an existing memory entry in ChromaDB.

    USED FOR:
    - Memory correction
    - User edits
    - AI memory refinement
    - API: /api/memory/update

    BEHAVIOR:
    - Overwrites document text
    - Replaces or merges metadata
    - Keeps memory ID unchanged
    """

    # ─────────────────────────────────────────────
    # 1. SAFETY GUARD (SYSTEM CHECK)
    # ─────────────────────────────────────────────

    if not memory_id or not new_text:
        return False


    # ─────────────────────────────────────────────
    # 2. BASE METADATA STRUCTURE
    # ─────────────────────────────────────────────
    # Ensures all entries maintain consistent schema

    base_metadata = {
        "type": "general",
        "timestamp": get_utc_timestamp(),
        "source": "user"
    }

    # ─────────────────────────────────────────────
    # 3. MERGE CUSTOM METADATA
    # ─────────────────────────────────────────────

    if new_metadata:
        base_metadata.update(new_metadata)

    # ─────────────────────────────────────────────
    # 4. COLLECTION ACCESS LAYER
    # ─────────────────────────────────────────────

    collection = get_chroma_collection()

    if collection is None:
        return False

    # ─────────────────────────────────────────────
    # 5. UPDATE OPERATION (OVERWRITE VECTOR ENTRY)
    # ─────────────────────────────────────────────

    try:
        if not _chroma_entry_exists(collection, memory_id):
            return False
        collection.update(
            ids=[memory_id],
            documents=[new_text],
            metadatas=[base_metadata]
        )
        return _chroma_entry_text_matches(collection, memory_id, new_text)

    except Exception:
        # ─────────────────────────────────────────────
        # 6. FAILSAFE ERROR HANDLING
        # ─────────────────────────────────────────────
        return False
        
        
# ============================================================
# CHROMADB — SIMILAR MEMORY DETECTION (DEDUPLICATION)
# ============================================================

def chroma_delete_by_user(user_id) -> bool:
    """Delete long-term vector memories explicitly owned by one account."""
    if user_id is None:
        return False
    collection = get_chroma_collection()
    if collection is None:
        return False
    try:
        collection.delete(where={"user_id": str(user_id)})
        return True
    except Exception:
        return False


def chroma_claim_legacy_memories(user_id) -> int:
    """Assign pre-user-isolation memories to the bootstrap administrator."""
    if user_id is None:
        return 0
    collection = get_chroma_collection()
    if collection is None:
        return 0
    try:
        records = collection.get(include=["metadatas"])
        legacy_ids = []
        claimed_metadata = []
        for memory_id, metadata in zip(
            records.get("ids", []), records.get("metadatas", [])
        ):
            normalized_metadata = dict(metadata or {})
            if normalized_metadata.get("user_id") in (None, ""):
                normalized_metadata["user_id"] = str(user_id)
                legacy_ids.append(memory_id)
                claimed_metadata.append(normalized_metadata)
        if legacy_ids:
            collection.update(ids=legacy_ids, metadatas=claimed_metadata)
        return len(legacy_ids)
    except Exception:
        return 0


def chroma_exists_similar(text, threshold=0.95, user_id=None):
    """
    ============================================================
    CHROMADB — DUPLICATE MEMORY DETECTION
    ============================================================

    PURPOSE:
    Prevents storing near-identical memory entries in ChromaDB.

    USED FOR:
    - Memory deduplication before insert
    - Reducing embedding noise
    - Preventing repeated user facts
    - Improving semantic storage quality

    LOGIC:
    - Uses vector similarity distance
    - Also performs exact text match fallback
    """

    # ─────────────────────────────────────────────
    # 1. SAFETY CHECK
    # ─────────────────────────────────────────────

    if not text:
        return False

    # ─────────────────────────────────────────────
    # 2. COLLECTION ACCESS LAYER
    # ─────────────────────────────────────────────

    collection = get_chroma_collection()

    if collection is None:
        return False

    # ─────────────────────────────────────────────
    # 3. SIMILARITY QUERY EXECUTION
    # ─────────────────────────────────────────────

    try:
        query_options = {
            "query_texts": [text],
            "n_results": 3,
        }
        if user_id is not None:
            query_options["where"] = {"user_id": str(user_id)}
        search_results = collection.query(**query_options)

        documents = search_results.get("documents", [[]])[0]
        distances = search_results.get("distances", [[]])[0]

        # ─────────────────────────────────────────────
        # 4. SIMILARITY EVALUATION ENGINE
        # ─────────────────────────────────────────────
        # Chroma distance meaning:
        # - 0.0 = identical
        # - higher = more different
        #
        # We convert threshold into distance space:
        # similarity >= threshold → distance <= (1 - threshold)
        # ─────────────────────────────────────────────

        max_allowed_distance = 1 - threshold

        for doc, distance in zip(documents, distances):

            # ─────────────────────────────────────────────
            # EXACT MATCH CHECK (HIGHEST PRIORITY)
            # ─────────────────────────────────────────────
            if doc and doc.strip().lower() == text.strip().lower():
                return True

            # ─────────────────────────────────────────────
            # SEMANTIC SIMILARITY CHECK
            # ─────────────────────────────────────────────
            if distance is not None and distance < max_allowed_distance:
                return True

        return False

    except Exception:
        # ─────────────────────────────────────────────
        # FAILSAFE: NEVER BLOCK SYSTEM ON ERROR
        # ─────────────────────────────────────────────
        return False



# ============================================================
# DATABASE CONNECTION FACTORY
# ============================================================

def get_db():
    """
    ============================================================
    DATABASE CONNECTION LAYER (MYSQL / MARIADB)
    ============================================================

    PURPOSE:
    Creates and returns a fresh MySQL/MariaDB database connection.

    USED FOR:
    - User authentication
    - Conversations
    - Messages
    - Playbooks
    - System persistence layer

    DESIGN RULE:
    This function MUST be the only entry point for DB connections.
    """

    # ─────────────────────────────────────────────
    # 1. IMPORT EXPECTATION (TOP-LEVEL ONLY)
    # ─────────────────────────────────────────────
    # NOTE:
    # mysql.connector and config_loader MUST be imported at file top
    # This function assumes they are already available globally.
    # ─────────────────────────────────────────────

    # ─────────────────────────────────────────────
    # 2. CONNECTION CREATION
    # ─────────────────────────────────────────────
    # Every call returns a NEW connection instance
    # (No connection pooling here unless added later)
    # ─────────────────────────────────────────────

    connection = mysql.connector.connect(
        host=config_loader.DB_HOST,
        port=config_loader.DB_PORT,
        user=config_loader.DB_USER,
        password=config_loader.DB_PASS,
        database=config_loader.DB_NAME,

        # ─────────────────────────────────────────
        # 3. UNICODE SAFETY CONFIGURATION
        # ─────────────────────────────────────────
        # Ensures full UTF-8 support:
        # - emojis
        # - special symbols
        # - multilingual text
        # - UI characters
        # ─────────────────────────────────────────

        charset="utf8mb4",
        collation="utf8mb4_unicode_ci",
        use_unicode=True,
    )

    return connection



# ============================================================
# USER MANAGEMENT — CREATE NEW USER ACCOUNT
# ============================================================

def create_user(
    full_name: str,
    username: str,
    email: str,
    password_hash: str,
    avatar: str = None
) -> int:
    """
    ============================================================
    USER CREATION SYSTEM (AUTH CORE)
    ============================================================

    PURPOSE:
    Creates a new user account in the database.

    RESPONSIBILITIES:
    - Inserts user into MariaDB users table
    - Stores hashed password (NEVER plaintext)
    - Assigns default role = 'user'
    - Handles system bootstrap (first user becomes owner)

    RETURNS:
    - Newly created user ID (int)

    SECURITY RULE:
    This function assumes password is already hashed externally.
    """

    # ─────────────────────────────────────────────
    # 1. DATABASE CONNECTION INITIALIZATION
    # ─────────────────────────────────────────────

    db_connection = get_db()
    cursor = db_connection.cursor()

    try:

        # ─────────────────────────────────────────
        # 2. INSERT USER RECORD
        # ─────────────────────────────────────────
        # Stores all core identity fields in users table
        # ─────────────────────────────────────────

        new_user_uid = str(uuid.uuid4())
        cursor.execute(
            """
            INSERT INTO users
                (user_uid, username, email, full_name, password_hash, role, is_active, avatar)
            VALUES (%s, %s, %s, %s, %s, 'user', 1, %s)
            """,
            (
                new_user_uid,
                username,
                email,
                full_name,
                password_hash,
                avatar
            )
        )

        db_connection.commit()

        # Retrieve newly generated primary key
        new_user_id = cursor.lastrowid

        # ─────────────────────────────────────────
        # 3. SYSTEM BOOTSTRAP LOGIC (FIRST USER)
        # ─────────────────────────────────────────
        # If this is the first user in system,
        # establish them as the single OWNER automatically.
        # ─────────────────────────────────────────

        cursor.execute("SELECT COUNT(*) FROM users")
        is_first_account = int(cursor.fetchone()[0]) == 1
        if is_first_account:
            cursor.execute(
                "UPDATE users SET role = 'owner' WHERE id = %s",
                (new_user_id,)
            )
            db_connection.commit()

        # Workspace provisioning is identity setup only. It creates the
        # account's empty sandbox and dormant ACL; no file capability uses it.
        from core.workspace_security import provision_user_foundation
        provision_user_foundation(new_user_uid)

        return new_user_id

    finally:
        # ─────────────────────────────────────────
        # 4. CLEAN RESOURCE HANDLING
        # ─────────────────────────────────────────
        # Always close DB resources to prevent leaks
        # ─────────────────────────────────────────

        cursor.close()
        db_connection.close()


# ============================================================
# USER MANAGEMENT — GET USER BY ID
# ============================================================

def get_user_by_id(user_id: int) -> dict | None:
    """
    ============================================================
    USER LOOKUP SYSTEM (PRIMARY IDENTITY RESOLVER)
    ============================================================

    PURPOSE:
    Retrieves a full user record from the database using user ID.

    USED FOR:
    - Session validation
    - Authentication checks
    - API authorization layers
    - User profile retrieval

    RETURNS:
    - Dictionary containing user data if found
    - None if user does not exist
    """

    # ─────────────────────────────────────────────
    # 1. DATABASE CONNECTION
    # ─────────────────────────────────────────────

    db_connection = get_db()

    # Dictionary cursor returns rows as key/value pairs
    cursor = db_connection.cursor(dictionary=True)

    try:

        # ─────────────────────────────────────────
        # 2. USER QUERY EXECUTION
        # ─────────────────────────────────────────

        cursor.execute(
            "SELECT * FROM users WHERE id = %s",
            (user_id,)
        )

        user_record = cursor.fetchone()

        return user_record

    finally:

        # ─────────────────────────────────────────
        # 3. RESOURCE CLEANUP
        # ─────────────────────────────────────────

        cursor.close()
        db_connection.close()


# ============================================================
# USER MANAGEMENT — GET USER BY EMAIL
# ============================================================

def get_user_by_email(email: str) -> dict | None:
    """
    ============================================================
    USER AUTH LOOKUP (EMAIL-BASED LOGIN CORE)
    ============================================================

    PURPOSE:
    Retrieves a user record from the database using email address.

    USED FOR:
    - Login authentication
    - Password verification flow
    - Account recovery / validation
    - Duplicate email checks (registration safety)

    RETURNS:
    - Full user dictionary if found
    - None if no matching email exists

    SECURITY NOTE:
    Includes password_hash ONLY for authentication layer use.
    Should NOT be exposed to frontend responses.
    """

    # ─────────────────────────────────────────────
    # 1. DATABASE CONNECTION INITIALIZATION
    # ─────────────────────────────────────────────

    db_connection = get_db()
    cursor = db_connection.cursor(dictionary=True)

    try:

        # ─────────────────────────────────────────
        # 2. USER QUERY EXECUTION (EMAIL LOOKUP)
        # ─────────────────────────────────────────

        cursor.execute(
            """
            SELECT
                id,
                username,
                email,
                full_name,
                password_hash,
                role,
                is_active,
                avatar
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        user_record = cursor.fetchone()

        return user_record

    finally:

        # ─────────────────────────────────────────
        # 3. RESOURCE CLEANUP
        # ─────────────────────────────────────────

        cursor.close()
        db_connection.close()


# ============================================================
# USER MANAGEMENT — GET USER BY USERNAME
# ============================================================

def get_user_by_username(username: str) -> dict | None:
    """
    ============================================================
    USER LOOKUP SYSTEM (USERNAME-BASED IDENTITY RESOLVER)
    ============================================================

    PURPOSE:
    Retrieves a user record using username instead of ID or email.

    USED FOR:
    - Username login flows
    - Account validation
    - Duplicate username checks during registration
    - Admin/user search tools

    RETURNS:
    - User dictionary if found
    - None if no matching username exists
    """

    # ─────────────────────────────────────────────
    # 1. DATABASE CONNECTION INITIALIZATION
    # ─────────────────────────────────────────────

    db_connection = get_db()
    cursor = db_connection.cursor(dictionary=True)

    try:

        # ─────────────────────────────────────────
        # 2. USER QUERY EXECUTION (USERNAME LOOKUP)
        # ─────────────────────────────────────────

        cursor.execute(
            """
            SELECT
                id,
                username,
                email,
                full_name,
                role,
                is_active,
                avatar
            FROM users
            WHERE username = %s
            """,
            (username,)
        )

        user_record = cursor.fetchone()

        return user_record

    finally:

        # ─────────────────────────────────────────
        # 3. RESOURCE CLEANUP
        # ─────────────────────────────────────────

        cursor.close()
        db_connection.close()


# ============================================================
# USER MANAGEMENT — UPDATE LAST LOGIN TIMESTAMP
# ============================================================

def update_last_login(user_id: int) -> None:
    """
    ============================================================
    USER ACTIVITY TRACKING (SESSION SYSTEM CORE)
    ============================================================

    PURPOSE:
    Updates the user's last_login timestamp to current database time.

    USED FOR:
    - Login tracking
    - User activity analytics
    - Security auditing
    - Session freshness validation

    NOTE:
    Uses database server time (NOW()) for consistency across systems.
    """

    # ─────────────────────────────────────────────
    # 1. DATABASE CONNECTION INITIALIZATION
    # ─────────────────────────────────────────────

    db_connection = get_db()
    cursor = db_connection.cursor()

    try:

        # ─────────────────────────────────────────
        # 2. TIMESTAMP UPDATE OPERATION
        # ─────────────────────────────────────────

        cursor.execute(
            """
            UPDATE users
            SET last_login = NOW()
            WHERE id = %s
            """,
            (user_id,)
        )

        db_connection.commit()

    finally:

        # ─────────────────────────────────────────
        # 3. RESOURCE CLEANUP
        # ─────────────────────────────────────────

        cursor.close()
        db_connection.close()


# ============================================================
# USER MANAGEMENT — UPDATE USERNAME
# ============================================================

def update_username(
    user_id: int,
    new_username: str = None,
    new_full_name: str = None
) -> bool:
    """
    ============================================================
    USER IDENTITY MODIFICATION (USERNAME UPDATE SYSTEM)
    ============================================================

    PURPOSE:
    Updates changed profile identity fields for an existing user.

    USED FOR:
    - Profile editing
    - Account renaming
    - Identity updates in UI settings panel

    RETURNS:
    - True  → username successfully updated
    - False → update failed (usually due to duplicate username)

    SAFETY RULE:
    Username must be unique across all users.
    """

    # ─────────────────────────────────────────────
    # 1. DATABASE CONNECTION INITIALIZATION
    # ─────────────────────────────────────────────

    db_connection = get_db()
    cursor = db_connection.cursor()

    try:

        # ─────────────────────────────────────────
        # 2. USERNAME UPDATE OPERATION
        # ─────────────────────────────────────────
        # This will fail if username violates UNIQUE constraint
        # in the database schema.
        # ─────────────────────────────────────────

        updates = []
        values = []

        if new_username is not None:
            updates.append("username = %s")
            values.append(new_username)

        if new_full_name is not None:
            updates.append("full_name = %s")
            values.append(new_full_name)

        if not updates:
            return True

        values.append(user_id)
        cursor.execute(
            f"UPDATE users SET {', '.join(updates)} WHERE id = %s",
            tuple(values)
        )

        db_connection.commit()

        # ─────────────────────────────────────────
        # 3. SUCCESS VALIDATION
        # ─────────────────────────────────────────
        # rowcount > 0 means a row was actually updated
        # ─────────────────────────────────────────

        return cursor.rowcount > 0

    except mysql.connector.IntegrityError:

        # ─────────────────────────────────────────
        # 4. DUPLICATE USERNAME HANDLING
        # ─────────────────────────────────────────
        # Triggered when UNIQUE constraint is violated
        # ─────────────────────────────────────────

        return False

    finally:

        # ─────────────────────────────────────────
        # 5. RESOURCE CLEANUP
        # ─────────────────────────────────────────

        cursor.close()
        db_connection.close()


# ============================================================
# USER MANAGEMENT — UPDATE PASSWORD
# ============================================================

def update_password(
    user_id: int,
    new_hash: str = None,
    new_email: str = None
) -> bool:
    """
    ============================================================
    SECURITY CORE FUNCTION (PASSWORD UPDATE SYSTEM)
    ============================================================

    PURPOSE:
    Updates changed account credentials for a user account.

    USED FOR:
    - Password reset flows
    - User account security updates
    - Admin password changes
    - Recovery system operations

    SECURITY RULE:
    This function ONLY accepts pre-hashed passwords.
    Never pass raw/plaintext passwords into this function.

    CRITICAL:
    This is a high-sensitivity operation affecting authentication.
    """

    # ─────────────────────────────────────────────
    # 1. DATABASE CONNECTION INITIALIZATION
    # ─────────────────────────────────────────────

    db_connection = get_db()
    cursor = db_connection.cursor()

    try:

        # ─────────────────────────────────────────
        # 2. PASSWORD HASH UPDATE OPERATION
        # ─────────────────────────────────────────
        # Replaces existing password_hash with new secure hash
        # ─────────────────────────────────────────

        updates = []
        values = []

        if new_hash is not None:
            updates.append("password_hash = %s")
            values.append(new_hash)

        if new_email is not None:
            updates.append("email = %s")
            values.append(new_email)

        if not updates:
            return True

        values.append(user_id)
        cursor.execute(
            f"UPDATE users SET {', '.join(updates)} WHERE id = %s",
            tuple(values)
        )

        db_connection.commit()
        return cursor.rowcount > 0

    except mysql.connector.IntegrityError:
        return False

    finally:

        # ─────────────────────────────────────────
        # 3. RESOURCE CLEANUP
        # ─────────────────────────────────────────

        cursor.close()
        db_connection.close()


# ============================================================
# USER MANAGEMENT — DELETE USER ACCOUNT (HARD DELETE)
# ============================================================

def delete_user(user_id: int) -> None:
    """
    ============================================================
    USER LIFECYCLE DESTRUCTION (FULL ACCOUNT REMOVAL)
    ============================================================

    PURPOSE:
    Permanently deletes a user and all associated data.

    AFFECTED DATA:
    - Messages (linked via conversations)
    - Conversations
    - User account record

    WARNING:
    This is a HARD DELETE operation.
    Data is NOT recoverable after execution.

    DATABASE ORDER RULE:
    Must delete child records BEFORE parent records
    to maintain foreign key integrity.
    """

    # ─────────────────────────────────────────────
    # 1. DATABASE CONNECTION INITIALIZATION
    # ─────────────────────────────────────────────

    db_connection = get_db()
    cursor = db_connection.cursor()

    try:

        # ─────────────────────────────────────────
        # 2. DELETE USER MESSAGES (CHILD TABLE)
        # ─────────────────────────────────────────
        # Step 1: Remove messages linked through conversations
        # This prevents orphaned message records
        # ─────────────────────────────────────────

        cursor.execute(
            """
            DELETE m FROM messages m
            JOIN conversations c
                ON c.id = m.conversation_id
            WHERE c.user_id = %s
            """,
            (user_id,)
        )

        # ─────────────────────────────────────────
        # 3. DELETE CONVERSATIONS
        # ─────────────────────────────────────────
        # Step 2: Remove all user conversations
        # Required before deleting user record
        # ─────────────────────────────────────────

        cursor.execute(
            "DELETE FROM conversations WHERE user_id = %s",
            (user_id,)
        )

        # ─────────────────────────────────────────
        # 4. DELETE USER RECORD (PARENT TABLE)
        # ─────────────────────────────────────────
        # Final step: remove user identity record
        # ─────────────────────────────────────────

        cursor.execute(
            "DELETE FROM users WHERE id = %s",
            (user_id,)
        )

        db_connection.commit()

    finally:

        # ─────────────────────────────────────────
        # 5. RESOURCE CLEANUP
        # ─────────────────────────────────────────

        cursor.close()
        db_connection.close()


# ============================================================
# PHASE 1 SECURITY / ADMINISTRATION PERSISTENCE
# ============================================================

def _users_foreign_key_table_spec(cursor) -> tuple[str, str, str, str]:
    """Return the exact users.id and users table storage attributes for FKs."""
    cursor.execute(
        """
        SELECT COLUMN_TYPE
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'users'
          AND COLUMN_NAME = 'id'
        """
    )
    column_row = cursor.fetchone()
    if not column_row:
        raise RuntimeError("Cannot migrate security tables: users.id was not found")
    user_id_type = str(column_row[0]).strip().lower()
    if not re.fullmatch(
        r"(?:tinyint|smallint|mediumint|int|bigint)(?:\(\d+\))?(?: unsigned)?",
        user_id_type,
    ):
        raise RuntimeError("Cannot migrate security tables: unsupported users.id type")

    cursor.execute(
        """
        SELECT ENGINE, TABLE_COLLATION
        FROM information_schema.TABLES
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'users'
        """
    )
    table_row = cursor.fetchone()
    if not table_row:
        raise RuntimeError("Cannot migrate security tables: users table was not found")
    engine = str(table_row[0] or "").strip()
    collation = str(table_row[1] or "").strip()
    charset = collation.split("_", 1)[0]
    if engine.lower() != "innodb":
        raise RuntimeError("Cannot create foreign keys: users must use InnoDB")
    for value in (engine, charset, collation):
        if not re.fullmatch(r"[A-Za-z0-9_]+", value):
            raise RuntimeError("Cannot migrate security tables: invalid table metadata")
    return user_id_type, engine, charset, collation

def ensure_user_identity_schema() -> None:
    """Create and backfill the public UUID identity before any user query.

    Existing non-null UUIDs are validation inputs only and are never rewritten.
    Integer primary keys and all foreign-key relationships remain untouched.
    """

    print("[DATABASE MIGRATION]")
    print("Checking user identity schema...")
    db_connection = get_db()
    cursor = db_connection.cursor()
    try:
        cursor.execute(
            """
            SELECT DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, IS_NULLABLE
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = 'users'
              AND COLUMN_NAME = 'user_uid'
            """
        )
        column = cursor.fetchone()
        if column is None:
            cursor.execute(
                "ALTER TABLE users ADD COLUMN user_uid CHAR(36) NULL"
            )
            column_is_nullable = True
        else:
            data_type = str(column[0] or "").lower()
            length = int(column[1] or 0)
            column_is_nullable = str(column[2] or "YES").upper() == "YES"
            if data_type != "char" or length != 36:
                raise RuntimeError(
                    "users.user_uid exists but is not CHAR(36); "
                    "automatic conversion was refused"
                )
        print("[OK] user_uid column exists")

        cursor.execute("SELECT id, user_uid FROM users ORDER BY id")
        users = cursor.fetchall()
        seen_uids = set()
        missing_user_ids = []
        for user_id, existing_uid in users:
            if existing_uid is None:
                missing_user_ids.append(user_id)
                continue
            existing_text = str(existing_uid).strip()
            try:
                uuid.UUID(existing_text)
            except (ValueError, AttributeError, TypeError) as error:
                raise RuntimeError(
                    f"users.user_uid contains an invalid non-null UUID for id {user_id}"
                ) from error
            identity_key = existing_text.casefold()
            if identity_key in seen_uids:
                raise RuntimeError(
                    "users.user_uid contains duplicate existing UUID values"
                )
            seen_uids.add(identity_key)

        for user_id in missing_user_ids:
            generated_uid = str(uuid.uuid4())
            while generated_uid.casefold() in seen_uids:
                generated_uid = str(uuid.uuid4())
            cursor.execute(
                "UPDATE users SET user_uid = %s "
                "WHERE id = %s AND user_uid IS NULL",
                (generated_uid, user_id),
            )
            seen_uids.add(generated_uid.casefold())
        db_connection.commit()
        print("[OK] UUID backfill complete")

        cursor.execute(
            """
            SELECT INDEX_NAME
            FROM information_schema.STATISTICS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = 'users'
              AND NON_UNIQUE = 0
            GROUP BY INDEX_NAME
            HAVING COUNT(*) = 1
               AND MAX(CASE WHEN COLUMN_NAME = 'user_uid' THEN 1 ELSE 0 END) = 1
            LIMIT 1
            """
        )
        unique_index = cursor.fetchone()
        if unique_index is None:
            cursor.execute(
                "ALTER TABLE users ADD UNIQUE INDEX "
                "uq_users_user_uid (user_uid)"
            )

        if column_is_nullable:
            cursor.execute(
                "ALTER TABLE users MODIFY COLUMN user_uid CHAR(36) NOT NULL"
            )
        db_connection.commit()
        print("[OK] user_uid unique protection exists")
        print("[OK] User identity ready")
    finally:
        cursor.close()
        db_connection.close()


def ensure_security_schema() -> None:
    """Apply additive role, activity, reset-token, and audit schema changes."""
    db_connection = get_db()
    cursor = db_connection.cursor()
    try:
        user_id_type, users_engine, users_charset, users_collation = (
            _users_foreign_key_table_spec(cursor)
        )
        cursor.execute(
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS role "
            "VARCHAR(32) NOT NULL DEFAULT 'user'"
        )
        cursor.execute(
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active "
            "TINYINT(1) NOT NULL DEFAULT 1"
        )
        cursor.execute(
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS last_activity "
            "TIMESTAMP NULL DEFAULT NULL"
        )
        cursor.execute(
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS updated_at "
            "TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP "
            "ON UPDATE CURRENT_TIMESTAMP"
        )
        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS password_reset_tokens (
                id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
                user_id {user_id_type} NULL,
                email_hash CHAR(64) NOT NULL,
                token_hash CHAR(64) NULL,
                requested_ip VARCHAR(64) NOT NULL,
                expires_at DATETIME NULL,
                used_at DATETIME NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (id),
                KEY ix_reset_email_created (email_hash, created_at),
                KEY ix_reset_ip_created (requested_ip, created_at),
                UNIQUE KEY uq_reset_token_hash (token_hash),
                CONSTRAINT fk_reset_user FOREIGN KEY (user_id)
                    REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE={users_engine} DEFAULT CHARACTER SET {users_charset}
              COLLATE {users_collation}
            """
        )
        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS admin_audit_logs (
                id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
                admin_user_id {user_id_type} NULL,
                target_user_id {user_id_type} NULL,
                action VARCHAR(100) NOT NULL,
                details VARCHAR(500) NULL,
                ip_address VARCHAR(64) NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (id),
                KEY ix_admin_audit_created (created_at),
                KEY ix_admin_audit_actor (admin_user_id, created_at),
                CONSTRAINT fk_admin_audit_actor FOREIGN KEY (admin_user_id)
                    REFERENCES users(id) ON DELETE SET NULL,
                CONSTRAINT fk_admin_audit_target FOREIGN KEY (target_user_id)
                    REFERENCES users(id) ON DELETE SET NULL
            ) ENGINE={users_engine} DEFAULT CHARACTER SET {users_charset}
              COLLATE {users_collation}
            """
        )
        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS system_settings (
                setting_key VARCHAR(100) NOT NULL,
                setting_value TEXT NOT NULL,
                updated_by {user_id_type} NULL,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                    ON UPDATE CURRENT_TIMESTAMP,
                PRIMARY KEY (setting_key),
                CONSTRAINT fk_system_settings_user FOREIGN KEY (updated_by)
                    REFERENCES users(id) ON DELETE SET NULL
            ) ENGINE={users_engine} DEFAULT CHARACTER SET {users_charset}
              COLLATE {users_collation}
            """
        )
        cursor.execute(
            """
            INSERT INTO system_settings (setting_key, setting_value)
            VALUES ('maintenance_mode', '0'), ('session_generation', '1')
            ON DUPLICATE KEY UPDATE setting_key = VALUES(setting_key)
            """
        )
        db_connection.commit()
    finally:
        cursor.close()
        db_connection.close()


def get_system_setting(setting_key: str, default=None):
    """Read one persisted global setting without exposing a write surface."""
    db_connection = get_db()
    cursor = db_connection.cursor()
    try:
        cursor.execute(
            "SELECT setting_value FROM system_settings WHERE setting_key = %s",
            (setting_key,),
        )
        row = cursor.fetchone()
        return row[0] if row else default
    finally:
        cursor.close()
        db_connection.close()


def set_system_setting(setting_key: str, setting_value, updated_by: int = None) -> None:
    """Persist one allowlisted global setting through a parameterized upsert."""
    if setting_key not in {"maintenance_mode", "session_generation"}:
        raise ValueError("Unsupported system setting")
    db_connection = get_db()
    cursor = db_connection.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO system_settings (setting_key, setting_value, updated_by)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
                setting_value = VALUES(setting_value),
                updated_by = VALUES(updated_by)
            """,
            (setting_key, str(setting_value), updated_by),
        )
        db_connection.commit()
    finally:
        cursor.close()
        db_connection.close()


def increment_session_generation(updated_by: int = None) -> int:
    """Atomically invalidate sessions and return the new generation number."""
    db_connection = get_db()
    cursor = db_connection.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO system_settings (setting_key, setting_value, updated_by)
            VALUES ('session_generation', '1', %s)
            ON DUPLICATE KEY UPDATE
                setting_value = CAST(setting_value AS UNSIGNED) + 1,
                updated_by = VALUES(updated_by)
            """,
            (updated_by,),
        )
        cursor.execute(
            "SELECT setting_value FROM system_settings "
            "WHERE setting_key = 'session_generation'"
        )
        generation = int(cursor.fetchone()[0])
        db_connection.commit()
        return generation
    finally:
        cursor.close()
        db_connection.close()


def touch_user_activity(user_id: int) -> None:
    db_connection = get_db()
    cursor = db_connection.cursor()
    try:
        cursor.execute("UPDATE users SET last_activity = NOW() WHERE id = %s", (user_id,))
        db_connection.commit()
    finally:
        cursor.close()
        db_connection.close()


def list_users_for_admin() -> list[dict]:
    db_connection = get_db()
    cursor = db_connection.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id, user_uid, username, full_name, email, role, is_active, avatar,
                   created_at, updated_at, last_login, last_activity,
                   CASE WHEN is_active = 1
                             AND last_activity >= (NOW() - INTERVAL 5 MINUTE)
                        THEN 1 ELSE 0 END AS is_online
            FROM users
            ORDER BY username, id
            """
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        db_connection.close()


def count_active_admins() -> int:
    db_connection = get_db()
    cursor = db_connection.cursor()
    try:
        cursor.execute(
            "SELECT COUNT(*) FROM users "
            "WHERE role IN ('owner', 'admin') AND is_active = 1"
        )
        return int(cursor.fetchone()[0])
    finally:
        cursor.close()
        db_connection.close()


def admin_update_user(user_id: int, changes: dict) -> bool:
    """Update only explicitly allowlisted identity/access fields."""
    allowed_columns = {
        "username": "username",
        "full_name": "full_name",
        "email": "email",
        "role": "role",
        "is_active": "is_active",
        "password_hash": "password_hash",
    }
    updates = []
    values = []
    for key, value in (changes or {}).items():
        column = allowed_columns.get(key)
        if column:
            updates.append(f"{column} = %s")
            values.append(value)
    if not updates:
        return False

    db_connection = get_db()
    cursor = db_connection.cursor()
    try:
        values.append(user_id)
        cursor.execute(f"UPDATE users SET {', '.join(updates)} WHERE id = %s", tuple(values))
        db_connection.commit()
        return cursor.rowcount > 0
    except mysql.connector.IntegrityError:
        return False
    finally:
        cursor.close()
        db_connection.close()


def write_admin_audit(
    admin_user_id: int,
    action: str,
    target_user_id: int = None,
    details: str = None,
    ip_address: str = None,
) -> None:
    db_connection = get_db()
    cursor = db_connection.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO admin_audit_logs
                (admin_user_id, target_user_id, action, details, ip_address)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (admin_user_id, target_user_id, action, details, ip_address),
        )
        db_connection.commit()
    finally:
        cursor.close()
        db_connection.close()


def get_admin_audit_logs(limit: int = 200) -> list[dict]:
    db_connection = get_db()
    cursor = db_connection.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT a.id, a.action, a.details, a.ip_address, a.created_at,
                   actor.username AS admin_username,
                   target.username AS target_username
            FROM admin_audit_logs a
            LEFT JOIN users actor ON actor.id = a.admin_user_id
            LEFT JOIN users target ON target.id = a.target_user_id
            ORDER BY a.created_at DESC, a.id DESC
            LIMIT %s
            """,
            (max(1, min(int(limit), 500)),),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        db_connection.close()


def password_reset_rate_count(email_hash: str, requested_ip: str, minutes: int = 15) -> int:
    db_connection = get_db()
    cursor = db_connection.cursor()
    try:
        window_minutes = max(1, min(int(minutes), 1440))
        cursor.execute(
            f"""
            SELECT COUNT(*) FROM password_reset_tokens
            WHERE created_at >= (NOW() - INTERVAL {window_minutes} MINUTE)
              AND (email_hash = %s OR requested_ip = %s)
            """,
            (email_hash, requested_ip),
        )
        return int(cursor.fetchone()[0])
    finally:
        cursor.close()
        db_connection.close()


def create_password_reset_record(
    user_id: int,
    email_hash: str,
    requested_ip: str,
    token_hash: str = None,
    expires_at=None,
) -> None:
    db_connection = get_db()
    cursor = db_connection.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO password_reset_tokens
                (user_id, email_hash, token_hash, requested_ip, expires_at)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (user_id, email_hash, token_hash, requested_ip, expires_at),
        )
        db_connection.commit()
    finally:
        cursor.close()
        db_connection.close()


def consume_password_reset_token(token_hash: str) -> int | None:
    """Atomically mark a valid, unexpired token used and return its user id."""
    db_connection = get_db()
    cursor = db_connection.cursor(dictionary=True)
    try:
        db_connection.start_transaction()
        cursor.execute(
            """
            SELECT id, user_id FROM password_reset_tokens
            WHERE token_hash = %s AND used_at IS NULL AND expires_at > NOW()
            FOR UPDATE
            """,
            (token_hash,),
        )
        record = cursor.fetchone()
        if not record or not record.get("user_id"):
            db_connection.rollback()
            return None
        cursor.execute(
            "UPDATE password_reset_tokens SET used_at = NOW() WHERE id = %s AND used_at IS NULL",
            (record["id"],),
        )
        if cursor.rowcount != 1:
            db_connection.rollback()
            return None
        db_connection.commit()
        return int(record["user_id"])
    finally:
        cursor.close()
        db_connection.close()


# ============================================================
# USER SETTINGS — GET USER PREFERENCES
# ============================================================

DEFAULT_USER_SETTINGS = {
    "preferred_router_model": "qwen2.5-coder:14b",
    "preferred_chat_model": "gpt-oss:20b",
    "preferred_code_model": "qwen2.5-coder:32b",
    "spiritual_mode": 0,
    "financial_mode": 0,
    "ui_theme": "dark",
    "web_search_enabled": 0,
    "personality_style": "balanced",
    "response_tone": "direct",
    "response_detail": "normal",
    "humor_level": "low",
    "greeting_style": "friendly",
    "show_processing_details": 1,
    "processing_details_expanded": 0,
    "processing_details_mode": "compact",
    "font_family": "mono",
    "font_size": 18,
    "chat_text_size": 16,
    "button_size": 16,
    "menu_size": 16,
    "header_size": 18,
    "code_size": 15,
    "text_style": "normal",
    "custom_text_color": "",
    "custom_chat_color": "",
    "custom_ui_color": "",
    "custom_accent_color": "",
    "custom_theme_json": "{}",
}


def ensure_user_settings_schema() -> None:
    """Extend the existing per-user settings schema in place."""
    db_connection = get_db()
    cursor = db_connection.cursor()

    try:
        schema_updates = (
            "ALTER TABLE user_settings ADD COLUMN IF NOT EXISTS "
            "preferred_router_model VARCHAR(100) NULL DEFAULT 'qwen2.5-coder:14b'",
            "ALTER TABLE user_settings ADD COLUMN IF NOT EXISTS "
            "personality_style VARCHAR(32) NOT NULL DEFAULT 'balanced'",
            "ALTER TABLE user_settings ADD COLUMN IF NOT EXISTS "
            "response_tone VARCHAR(32) NOT NULL DEFAULT 'direct'",
            "ALTER TABLE user_settings ADD COLUMN IF NOT EXISTS "
            "response_detail VARCHAR(32) NOT NULL DEFAULT 'normal'",
            "ALTER TABLE user_settings ADD COLUMN IF NOT EXISTS "
            "humor_level VARCHAR(32) NOT NULL DEFAULT 'low'",
            "ALTER TABLE user_settings ADD COLUMN IF NOT EXISTS "
            "greeting_style VARCHAR(32) NOT NULL DEFAULT 'friendly'",
            "ALTER TABLE user_settings ADD COLUMN IF NOT EXISTS updated_at "
            "TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
            "ALTER TABLE user_settings ADD COLUMN IF NOT EXISTS "
            "show_processing_details TINYINT(1) NOT NULL DEFAULT 1",
            "ALTER TABLE user_settings ADD COLUMN IF NOT EXISTS "
            "processing_details_expanded TINYINT(1) NOT NULL DEFAULT 0",
            "ALTER TABLE user_settings ADD COLUMN IF NOT EXISTS "
            "processing_details_mode VARCHAR(16) NOT NULL DEFAULT 'compact'",
            "ALTER TABLE user_settings ADD COLUMN IF NOT EXISTS "
            "font_family VARCHAR(32) NOT NULL DEFAULT 'mono'",
            "ALTER TABLE user_settings ADD COLUMN IF NOT EXISTS "
            "font_size SMALLINT UNSIGNED NOT NULL DEFAULT 18",
            "ALTER TABLE user_settings ADD COLUMN IF NOT EXISTS "
            "chat_text_size SMALLINT UNSIGNED NOT NULL DEFAULT 16",
            "ALTER TABLE user_settings ADD COLUMN IF NOT EXISTS "
            "button_size SMALLINT UNSIGNED NOT NULL DEFAULT 16",
            "ALTER TABLE user_settings ADD COLUMN IF NOT EXISTS "
            "menu_size SMALLINT UNSIGNED NOT NULL DEFAULT 16",
            "ALTER TABLE user_settings ADD COLUMN IF NOT EXISTS "
            "header_size SMALLINT UNSIGNED NOT NULL DEFAULT 18",
            "ALTER TABLE user_settings ADD COLUMN IF NOT EXISTS "
            "code_size SMALLINT UNSIGNED NOT NULL DEFAULT 15",
            "ALTER TABLE user_settings ADD COLUMN IF NOT EXISTS "
            "text_style VARCHAR(16) NOT NULL DEFAULT 'normal'",
            "ALTER TABLE user_settings ADD COLUMN IF NOT EXISTS "
            "custom_text_color VARCHAR(16) NOT NULL DEFAULT ''",
            "ALTER TABLE user_settings ADD COLUMN IF NOT EXISTS "
            "custom_chat_color VARCHAR(16) NOT NULL DEFAULT ''",
            "ALTER TABLE user_settings ADD COLUMN IF NOT EXISTS "
            "custom_ui_color VARCHAR(16) NOT NULL DEFAULT ''",
            "ALTER TABLE user_settings ADD COLUMN IF NOT EXISTS "
            "custom_accent_color VARCHAR(16) NOT NULL DEFAULT ''",
            "ALTER TABLE user_settings ADD COLUMN IF NOT EXISTS "
            "custom_theme_json LONGTEXT NULL",
            "ALTER TABLE user_settings ALTER COLUMN font_size SET DEFAULT 18",
            "ALTER TABLE user_settings ALTER COLUMN chat_text_size SET DEFAULT 16",
            "ALTER TABLE user_settings ALTER COLUMN button_size SET DEFAULT 16",
            "ALTER TABLE user_settings ALTER COLUMN menu_size SET DEFAULT 16",
        )

        for statement in schema_updates:
            cursor.execute(statement)

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_personality_traits (
                id INT UNSIGNED NOT NULL AUTO_INCREMENT,
                user_id INT UNSIGNED NOT NULL,
                trait VARCHAR(255) NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (id),
                UNIQUE KEY uq_user_personality_trait (user_id, trait),
                CONSTRAINT fk_personality_traits_user
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
            """
        )

        cursor.execute(
            """
            INSERT INTO user_settings (
                user_id, preferred_router_model, preferred_chat_model,
                preferred_code_model, personality_style, response_tone,
                response_detail, humor_level, greeting_style
            )
            SELECT id, %s, %s, %s, %s, %s, %s, %s, %s FROM users
            ON DUPLICATE KEY UPDATE user_id = VALUES(user_id)
            """,
            (
                DEFAULT_USER_SETTINGS["preferred_router_model"],
                DEFAULT_USER_SETTINGS["preferred_chat_model"],
                DEFAULT_USER_SETTINGS["preferred_code_model"],
                DEFAULT_USER_SETTINGS["personality_style"],
                DEFAULT_USER_SETTINGS["response_tone"],
                DEFAULT_USER_SETTINGS["response_detail"],
                DEFAULT_USER_SETTINGS["humor_level"],
                DEFAULT_USER_SETTINGS["greeting_style"],
            )
        )
        cursor.execute(
            """
            UPDATE user_settings
            SET preferred_router_model = COALESCE(NULLIF(preferred_router_model, ''), %s),
                preferred_chat_model = COALESCE(NULLIF(preferred_chat_model, ''), %s),
                preferred_code_model = COALESCE(NULLIF(preferred_code_model, ''), %s)
            """,
            (
                DEFAULT_USER_SETTINGS["preferred_router_model"],
                DEFAULT_USER_SETTINGS["preferred_chat_model"],
                DEFAULT_USER_SETTINGS["preferred_code_model"],
            )
        )
        db_connection.commit()
    finally:
        cursor.close()
        db_connection.close()


def get_user_settings(user_id: int) -> dict:
    """
    ============================================================
    USER PREFERENCE SYSTEM (AI BEHAVIOR CONFIGURATION)
    ============================================================

    PURPOSE:
    Retrieves user-specific AI and UI configuration settings.

    USED FOR:
    - AI model selection preferences
    - UI theme configuration
    - Feature toggles (spiritual mode, financial mode, etc.)
    - Web search behavior control

    FALLBACK BEHAVIOR:
    If no settings record exists, returns a default configuration
    ensuring system stability and predictable AI behavior.
    """

    # ─────────────────────────────────────────────
    # 1. DATABASE CONNECTION INITIALIZATION
    # ─────────────────────────────────────────────

    db_connection = get_db()
    cursor = db_connection.cursor(dictionary=True)

    try:

        # ─────────────────────────────────────────
        # 2. FETCH USER SETTINGS RECORD
        # ─────────────────────────────────────────

        cursor.execute(
            """
            SELECT *
            FROM user_settings
            WHERE user_id = %s
            """,
            (user_id,)
        )

        settings_row = cursor.fetchone()

        if settings_row:
            merged_settings = dict(DEFAULT_USER_SETTINGS)
            merged_settings["user_id"] = user_id
            merged_settings.update({
                key: value
                for key, value in settings_row.items()
                if value is not None
            })
            try:
                merged_settings["custom_theme"] = json.loads(
                    merged_settings.get("custom_theme_json") or "{}"
                )
            except (TypeError, ValueError, json.JSONDecodeError):
                merged_settings["custom_theme"] = {}
            return merged_settings

        # ─────────────────────────────────────────
        # 3. DEFAULT SETTINGS FALLBACK
        # ─────────────────────────────────────────
        # If user has no settings row yet, return safe defaults
        # This prevents null behavior in AI routing system
        # ─────────────────────────────────────────

        if not settings_row:
            return {
                "user_id": user_id,

                # ───────────────────────────────
                # AI MODEL PREFERENCES
                # ───────────────────────────────
                "preferred_router_model": DEFAULT_USER_SETTINGS["preferred_router_model"],
                "preferred_chat_model": DEFAULT_USER_SETTINGS["preferred_chat_model"],
                "preferred_code_model": DEFAULT_USER_SETTINGS["preferred_code_model"],

                # ───────────────────────────────
                # AI BEHAVIOR MODES
                # ───────────────────────────────
                "spiritual_mode": 0,
                "financial_mode": 0,

                # ───────────────────────────────
                # UI CONFIGURATION
                # ───────────────────────────────
                "ui_theme": "dark",

                # ───────────────────────────────
                # WEB SEARCH BEHAVIOR CONTROL
                # ───────────────────────────────
                # 0 = disabled
                # 1 = always allow web search
                "web_search_enabled": 0,

                "personality_style": DEFAULT_USER_SETTINGS["personality_style"],
                "response_tone": DEFAULT_USER_SETTINGS["response_tone"],
                "response_detail": DEFAULT_USER_SETTINGS["response_detail"],
                "humor_level": DEFAULT_USER_SETTINGS["humor_level"],
                "greeting_style": DEFAULT_USER_SETTINGS["greeting_style"]
            }

        return settings_row

    finally:

        # ─────────────────────────────────────────
        # 4. RESOURCE CLEANUP
        # ─────────────────────────────────────────

        cursor.close()
        db_connection.close()


# ============================================================
# USER SETTINGS — UPSERT USER CONFIGURATION
# ============================================================

def upsert_user_settings(user_id: int, settings: dict) -> None:
    """
    ============================================================
    USER PREFERENCE SYSTEM (CONFIGURATION PERSISTENCE ENGINE)
    ============================================================

    PURPOSE:
    Inserts or updates a user's settings in a single atomic operation.

    BEHAVIOR:
    - If settings row does NOT exist → INSERT
    - If settings row EXISTS → UPDATE existing row

    USED FOR:
    - AI model preference updates
    - UI theme changes
    - Feature toggles (spiritual / financial / web search)
    - Full user personalization persistence

    SAFETY RULES:
    - Boolean-like values are normalized to 0/1 integers
    - Defaults applied for missing fields
    - Prevents partial or malformed configuration writes
    """

    # ─────────────────────────────────────────────
    # 1. DATABASE CONNECTION INITIALIZATION
    # ─────────────────────────────────────────────

    db_connection = get_db()
    cursor = db_connection.cursor()

    try:

        # ─────────────────────────────────────────
        # 2. SETTINGS NORMALIZATION
        # ─────────────────────────────────────────
        # Convert incoming settings into DB-safe values
        # Ensures consistent schema storage format
        # ─────────────────────────────────────────

        merged = get_user_settings(user_id)
        merged.update(settings or {})

        router_model = merged.get("preferred_router_model")
        chat_model = merged.get("preferred_chat_model")
        code_model = merged.get("preferred_code_model")
        spiritual_mode = int(bool(merged.get("spiritual_mode", 0)))
        financial_mode = int(bool(merged.get("financial_mode", 0)))
        ui_theme = merged.get("ui_theme", "dark")
        web_search_enabled = int(bool(merged.get("web_search_enabled", 0)))
        personality_style = merged.get("personality_style", "balanced")
        response_tone = merged.get("response_tone", "direct")
        response_detail = merged.get("response_detail", "normal")
        humor_level = merged.get("humor_level", "low")
        greeting_style = merged.get("greeting_style", "friendly")
        show_processing_details = int(bool(merged.get("show_processing_details", 1)))
        processing_details_expanded = int(bool(merged.get("processing_details_expanded", 0)))
        processing_details_mode = merged.get("processing_details_mode", "compact")
        font_family = merged.get("font_family", "mono")
        font_size = int(merged.get("font_size", 18))
        chat_text_size = int(merged.get("chat_text_size", 16))
        button_size = int(merged.get("button_size", 16))
        menu_size = int(merged.get("menu_size", 16))
        header_size = int(merged.get("header_size", 18))
        code_size = int(merged.get("code_size", 15))
        text_style = merged.get("text_style", "normal")
        custom_text_color = merged.get("custom_text_color", "")
        custom_chat_color = merged.get("custom_chat_color", "")
        custom_ui_color = merged.get("custom_ui_color", "")
        custom_accent_color = merged.get("custom_accent_color", "")
        custom_theme_value = merged.get("custom_theme", merged.get("custom_theme_json", "{}"))
        custom_theme_json = (
            json.dumps(custom_theme_value, separators=(",", ":"), sort_keys=True)
            if isinstance(custom_theme_value, dict)
            else str(custom_theme_value or "{}")
        )

        # ─────────────────────────────────────────
        # 3. UPSERT OPERATION (INSERT OR UPDATE)
        # ─────────────────────────────────────────
        # Uses ON DUPLICATE KEY UPDATE to maintain single row per user
        # ─────────────────────────────────────────

        cursor.execute(
            """
            INSERT INTO user_settings (
                user_id,
                preferred_router_model,
                preferred_chat_model,
                preferred_code_model,
                spiritual_mode,
                financial_mode,
                ui_theme,
                web_search_enabled,
                personality_style,
                response_tone,
                response_detail,
                humor_level,
                greeting_style,
                show_processing_details,
                processing_details_expanded,
                processing_details_mode,
                font_family,
                font_size,
                chat_text_size,
                button_size,
                menu_size,
                header_size,
                code_size,
                text_style,
                custom_text_color,
                custom_chat_color,
                custom_ui_color,
                custom_accent_color,
                custom_theme_json
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                preferred_router_model = VALUES(preferred_router_model),
                preferred_chat_model = VALUES(preferred_chat_model),
                preferred_code_model = VALUES(preferred_code_model),
                spiritual_mode       = VALUES(spiritual_mode),
                financial_mode       = VALUES(financial_mode),
                ui_theme             = VALUES(ui_theme),
                web_search_enabled   = VALUES(web_search_enabled),
                personality_style    = VALUES(personality_style),
                response_tone        = VALUES(response_tone),
                response_detail      = VALUES(response_detail),
                humor_level          = VALUES(humor_level),
                greeting_style       = VALUES(greeting_style),
                show_processing_details = VALUES(show_processing_details),
                processing_details_expanded = VALUES(processing_details_expanded),
                processing_details_mode = VALUES(processing_details_mode),
                font_family = VALUES(font_family),
                font_size = VALUES(font_size),
                chat_text_size = VALUES(chat_text_size),
                button_size = VALUES(button_size),
                menu_size = VALUES(menu_size),
                header_size = VALUES(header_size),
                code_size = VALUES(code_size),
                text_style = VALUES(text_style),
                custom_text_color = VALUES(custom_text_color),
                custom_chat_color = VALUES(custom_chat_color),
                custom_ui_color = VALUES(custom_ui_color),
                custom_accent_color = VALUES(custom_accent_color),
                custom_theme_json = VALUES(custom_theme_json)
            """,
            (
                user_id,
                router_model,
                chat_model,
                code_model,
                spiritual_mode,
                financial_mode,
                ui_theme,
                web_search_enabled,
                personality_style,
                response_tone,
                response_detail,
                humor_level,
                greeting_style,
                show_processing_details,
                processing_details_expanded,
                processing_details_mode,
                font_family,
                font_size,
                chat_text_size,
                button_size,
                menu_size,
                header_size,
                code_size,
                text_style,
                custom_text_color,
                custom_chat_color,
                custom_ui_color,
                custom_accent_color,
                custom_theme_json
            )
        )

        db_connection.commit()

    finally:

        # ─────────────────────────────────────────
        # 4. RESOURCE CLEANUP
        # ─────────────────────────────────────────

        cursor.close()
        db_connection.close()


# ============================================================
# CONVERSATION SYSTEM — UUID → NUMERIC ID RESOLVER
# ============================================================

def _normalize_personality_trait(record: dict | None) -> dict | None:
    if not record:
        return record
    normalized = dict(record)
    normalized["name"] = normalized.get("name") or normalized.get("trait") or ""
    normalized["trait"] = normalized["name"]  # legacy API compatibility
    normalized["description"] = normalized.get("description") or ""
    normalized["category"] = normalized.get("category") or "communication"
    normalized["owner"] = normalized.get("owner") or "user"
    normalized["strength"] = int(normalized.get("strength") or 0)
    normalized["active"] = bool(normalized.get("active", True))
    return normalized


def _record_trait_history(cursor, user_id, trait_id, name, action, reason, source):
    cursor.execute(
        """
        INSERT INTO personality_trait_history
            (user_id, trait_id, trait_name, action, reason, source)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (user_id, trait_id, name, action, reason or "", source),
    )


def get_user_personality_traits(
    user_id: int,
    owner: str = None,
    include_inactive: bool = False,
) -> list[dict]:
    """Return structured traits scoped to one authenticated user."""
    db_connection = get_db()
    cursor = db_connection.cursor(dictionary=True)
    try:
        filters = ["user_id = %s"]
        params = [user_id]
        if owner in {"user", "aetheraeon"}:
            filters.append("owner = %s")
            params.append(owner)
        if not include_inactive:
            filters.append("active = 1")
        cursor.execute(
            f"""
            SELECT id, trait, name, description, category, strength, owner,
                   created_by, reason_created, influence_summary, active,
                   created_at, updated_at
            FROM user_personality_traits
            WHERE {' AND '.join(filters)}
            ORDER BY created_at, id
            """,
            tuple(params),
        )
        return [_normalize_personality_trait(row) for row in cursor.fetchall()]
    finally:
        cursor.close()
        db_connection.close()


def add_user_personality_trait(
    user_id: int,
    trait: str = None,
    *,
    name: str = None,
    description: str = "",
    category: str = "communication",
    strength: int = 50,
    created_by: str = "user",
) -> dict | None:
    """Create a user-owned trait.  This path can never create an AI trait."""
    from core.trait_authority import require_trait_operation
    require_trait_operation("user", "user", "create")
    name = str(name or trait or "").strip()
    if not name:
        return None
    strength = max(0, min(100, int(strength)))
    db_connection = get_db()
    cursor = db_connection.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            INSERT IGNORE INTO user_personality_traits
                (user_id, trait, name, description, category, strength, owner, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, 'user', %s)
            """,
            (user_id, name, name, description, category, strength, created_by),
        )
        if cursor.rowcount:
            _record_trait_history(
                cursor, user_id, cursor.lastrowid, name, "created",
                "User-created communication preference.", created_by,
            )
        db_connection.commit()
        cursor.execute(
            """
            SELECT id, trait, name, description, category, strength, owner,
                   created_by, reason_created, influence_summary, active,
                   created_at, updated_at
            FROM user_personality_traits
            WHERE user_id = %s AND trait = %s AND owner = 'user'
            """,
            (user_id, name),
        )
        return _normalize_personality_trait(cursor.fetchone())
    finally:
        cursor.close()
        db_connection.close()


def update_user_personality_trait(user_id: int, trait_id: int, changes: dict) -> dict | None:
    """Edit a user-owned trait; AI-owned rows are excluded by the query."""
    from core.trait_authority import require_trait_operation
    require_trait_operation("user", "user", "edit")
    allowed = {"name", "description", "category", "strength", "active"}
    updates = {key: value for key, value in (changes or {}).items() if key in allowed}
    if not updates:
        return None
    if "strength" in updates:
        updates["strength"] = max(0, min(100, int(updates["strength"])))
    if "name" in updates:
        updates["name"] = str(updates["name"]).strip()
        if not updates["name"]:
            return None
        updates["trait"] = updates["name"]

    db_connection = get_db()
    cursor = db_connection.cursor(dictionary=True)
    try:
        assignments = ", ".join(f"{key} = %s" for key in updates)
        cursor.execute(
            f"UPDATE user_personality_traits SET {assignments} "
            "WHERE id = %s AND user_id = %s AND owner = 'user'",
            (*updates.values(), trait_id, user_id),
        )
        if not cursor.rowcount:
            return None
        cursor.execute(
            "SELECT name FROM user_personality_traits WHERE id = %s AND user_id = %s",
            (trait_id, user_id),
        )
        name = cursor.fetchone()["name"]
        _record_trait_history(cursor, user_id, trait_id, name, "updated", "User edit.", "user")
        db_connection.commit()
        return get_personality_trait(user_id, trait_id, connection=db_connection, cursor=cursor)
    finally:
        cursor.close()
        db_connection.close()


def get_personality_trait(user_id: int, trait_id: int, connection=None, cursor=None):
    owns_resources = connection is None or cursor is None
    db_connection = connection or get_db()
    db_cursor = cursor or db_connection.cursor(dictionary=True)
    try:
        db_cursor.execute(
            """
            SELECT id, trait, name, description, category, strength, owner,
                   created_by, reason_created, influence_summary, active,
                   created_at, updated_at
            FROM user_personality_traits WHERE id = %s AND user_id = %s
            """,
            (trait_id, user_id),
        )
        return _normalize_personality_trait(db_cursor.fetchone())
    finally:
        if owns_resources:
            db_cursor.close()
            db_connection.close()


def create_aetheraeon_personality_trait(
    user_id: int,
    *,
    name: str,
    description: str,
    category: str,
    strength: int,
    reason_created: str,
    influence_summary: str,
) -> dict | None:
    """Internal AI-only creation path with mandatory transparency fields."""
    from core.trait_authority import require_trait_operation
    require_trait_operation("aetheraeon", "aetheraeon", "create")
    name = str(name or "").strip()
    reason_created = str(reason_created or "").strip()
    influence_summary = str(influence_summary or "").strip()
    if not name or not reason_created or not influence_summary:
        return None
    strength = max(0, min(100, int(strength)))
    db_connection = get_db()
    cursor = db_connection.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            INSERT IGNORE INTO user_personality_traits
                (user_id, trait, name, description, category, strength, owner,
                 created_by, reason_created, influence_summary)
            VALUES (%s, %s, %s, %s, %s, %s, 'aetheraeon', 'aetheraeon', %s, %s)
            """,
            (user_id, name, name, description, category, strength,
             reason_created, influence_summary),
        )
        trait_id = cursor.lastrowid
        if cursor.rowcount:
            _record_trait_history(
                cursor, user_id, trait_id, name, "created",
                reason_created, "aetheraeon",
            )
        db_connection.commit()
        cursor.execute(
            "SELECT id FROM user_personality_traits "
            "WHERE user_id = %s AND trait = %s AND owner = 'aetheraeon'",
            (user_id, name),
        )
        row = cursor.fetchone()
        return get_personality_trait(user_id, row["id"], connection=db_connection, cursor=cursor)
    finally:
        cursor.close()
        db_connection.close()


def update_aetheraeon_personality_trait(user_id: int, trait_id: int, changes: dict) -> dict | None:
    """Internal AI path; it cannot alter a user-owned trait."""
    from core.trait_authority import require_trait_operation
    require_trait_operation("aetheraeon", "aetheraeon", "edit")
    allowed = {"description", "category", "strength", "reason_created", "influence_summary", "active"}
    updates = {key: value for key, value in (changes or {}).items() if key in allowed}
    if not updates:
        return None
    if "strength" in updates:
        updates["strength"] = max(0, min(100, int(updates["strength"])))
    db_connection = get_db()
    cursor = db_connection.cursor(dictionary=True)
    try:
        assignments = ", ".join(f"{key} = %s" for key in updates)
        cursor.execute(
            f"UPDATE user_personality_traits SET {assignments} "
            "WHERE id = %s AND user_id = %s AND owner = 'aetheraeon'",
            (*updates.values(), trait_id, user_id),
        )
        if not cursor.rowcount:
            return None
        cursor.execute(
            "SELECT name FROM user_personality_traits WHERE id = %s AND user_id = %s",
            (trait_id, user_id),
        )
        name = cursor.fetchone()["name"]
        _record_trait_history(
            cursor, user_id, trait_id, name, "updated",
            str(changes.get("reason_created") or "Aetheraeon trait adjustment."),
            "aetheraeon",
        )
        db_connection.commit()
        return get_personality_trait(user_id, trait_id, connection=db_connection, cursor=cursor)
    finally:
        cursor.close()
        db_connection.close()


def add_personality_trait_feedback(user_id: int, trait_id: int, correction: str) -> dict | None:
    """Attach user correction to an AI trait without editing that trait."""
    from core.trait_authority import require_trait_operation
    require_trait_operation("user", "aetheraeon", "correct")
    correction = str(correction or "").strip()
    if not correction:
        return None
    db_connection = get_db()
    cursor = db_connection.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT name FROM user_personality_traits "
            "WHERE id = %s AND user_id = %s AND owner = 'aetheraeon' AND active = 1",
            (trait_id, user_id),
        )
        trait = cursor.fetchone()
        if not trait:
            return None
        cursor.execute(
            "INSERT INTO personality_trait_feedback (user_id, trait_id, correction) VALUES (%s, %s, %s)",
            (user_id, trait_id, correction),
        )
        feedback_id = cursor.lastrowid
        _record_trait_history(
            cursor, user_id, trait_id, trait["name"], "corrected",
            correction, "user_feedback",
        )
        db_connection.commit()
        cursor.execute(
            "SELECT id, trait_id, correction, created_at FROM personality_trait_feedback WHERE id = %s",
            (feedback_id,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        db_connection.close()


def get_personality_trait_feedback(user_id: int) -> list[dict]:
    db_connection = get_db()
    cursor = db_connection.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT f.id, f.trait_id, t.name AS related_trait, f.correction, f.created_at
            FROM personality_trait_feedback f
            JOIN user_personality_traits t ON t.id = f.trait_id AND t.user_id = f.user_id
            WHERE f.user_id = %s AND t.owner = 'aetheraeon' AND t.active = 1
            ORDER BY f.created_at, f.id
            """,
            (user_id,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        db_connection.close()


def get_personality_trait_history(user_id: int) -> list[dict]:
    db_connection = get_db()
    cursor = db_connection.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT h.id, h.trait_id, h.trait_name, h.action, h.reason,
                   h.source, h.created_at,
                   CASE
                       WHEN h.source IN (
                           'aetheraeon', 'aetheraeon_evolution',
                           'user_removed_aetheraeon'
                       )
                           THEN 'aetheraeon'
                       WHEN h.source = 'user_feedback'
                           THEN COALESCE(t.owner, 'aetheraeon')
                       ELSE COALESCE(t.owner, 'user')
                   END AS owner
            FROM personality_trait_history h
            LEFT JOIN user_personality_traits t
              ON t.id = h.trait_id AND t.user_id = h.user_id
            WHERE h.user_id = %s
            ORDER BY h.created_at DESC, h.id DESC
            """,
            (user_id,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        db_connection.close()


def _normalize_trait_candidate(record: dict | None) -> dict | None:
    if not record:
        return record
    normalized = dict(record)
    events = normalized.get("influencing_events")
    if isinstance(events, str):
        try:
            events = json.loads(events)
        except (TypeError, ValueError):
            events = []
    normalized["influencing_events"] = events if isinstance(events, list) else []
    normalized["confidence_score"] = int(normalized.get("confidence_score") or 0)
    normalized["evidence_count"] = int(normalized.get("evidence_count") or 0)
    return normalized


def get_personality_trait_candidates(
    user_id: int,
    include_promoted: bool = False,
) -> list[dict]:
    """Return candidates scoped to one user; candidates are not memories."""
    db_connection = get_db()
    cursor = db_connection.cursor(dictionary=True)
    try:
        status_filter = "" if include_promoted else "AND c.status = 'observing'"
        cursor.execute(
            f"""
            SELECT c.id, c.name, c.description, c.category,
                   c.confidence_score, c.evidence_count,
                   c.first_detected_at, c.last_detected_at,
                   c.reason_detected, c.influencing_events, c.status,
                   c.promoted_trait_id, c.promoted_at,
                   t.name AS promoted_trait_name
            FROM personality_trait_candidates c
            LEFT JOIN user_personality_traits t
              ON t.id = c.promoted_trait_id AND t.user_id = c.user_id
            WHERE c.user_id = %s {status_filter}
            ORDER BY c.confidence_score DESC, c.last_detected_at DESC, c.id DESC
            """,
            (user_id,),
        )
        return [_normalize_trait_candidate(row) for row in cursor.fetchall()]
    finally:
        cursor.close()
        db_connection.close()


def record_personality_trait_candidate_evidence(
    *,
    user_id: int,
    conversation_id: str,
    event_key: str,
    signal: dict,
) -> dict | None:
    """Record one distinct observation and promote only at the threshold."""
    from core.trait_authority import require_trait_operation
    from core.trait_evolution import next_candidate_state

    require_trait_operation("aetheraeon", "aetheraeon", "create")
    candidate_name = str(signal.get("candidate_name") or "").strip()
    if not candidate_name or not event_key:
        return None

    db_connection = get_db()
    cursor = db_connection.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT * FROM personality_trait_candidates "
            "WHERE user_id = %s AND name = %s FOR UPDATE",
            (user_id, candidate_name),
        )
        existing = cursor.fetchone()
        existing_normalized = _normalize_trait_candidate(existing) or {}
        events = list(existing_normalized.get("influencing_events") or [])
        if any(item.get("event_key") == event_key for item in events if isinstance(item, dict)):
            return existing_normalized

        events.append({
            "event_key": event_key,
            "conversation_id": str(conversation_id),
            "summary": str(signal.get("event_summary") or "Explicit style preference."),
        })
        events = events[-20:]
        state = next_candidate_state(existing_normalized)
        serialized_events = json.dumps(events, ensure_ascii=False, separators=(",", ":"))

        if existing:
            cursor.execute(
                """
                UPDATE personality_trait_candidates
                SET confidence_score = %s, evidence_count = %s,
                    last_detected_at = CURRENT_TIMESTAMP,
                    reason_detected = %s, influencing_events = %s,
                    status = %s
                WHERE id = %s AND user_id = %s
                """,
                (
                    state["confidence_score"], state["evidence_count"],
                    signal.get("reason", ""), serialized_events,
                    state["status"], existing["id"], user_id,
                ),
            )
            candidate_id = existing["id"]
        else:
            cursor.execute(
                """
                INSERT INTO personality_trait_candidates
                    (user_id, name, description, category, confidence_score,
                     evidence_count, reason_detected, influencing_events, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    user_id, candidate_name, signal.get("candidate_description", ""),
                    signal.get("category", "communication"),
                    state["confidence_score"], state["evidence_count"],
                    signal.get("reason", ""), serialized_events, state["status"],
                ),
            )
            candidate_id = cursor.lastrowid

        if state["should_promote"]:
            promoted_name = str(signal.get("promoted_name") or candidate_name).strip()
            strength = max(0, min(100, int(signal.get("promoted_strength") or 70)))
            influence_summary = (
                f"Promoted from {state['evidence_count']} distinct interaction signals; "
                f"candidate confidence {state['confidence_score']}%."
            )
            cursor.execute(
                """
                INSERT IGNORE INTO user_personality_traits
                    (user_id, trait, name, description, category, strength,
                     owner, created_by, reason_created, influence_summary)
                VALUES (%s, %s, %s, %s, %s, %s,
                        'aetheraeon', 'aetheraeon', %s, %s)
                """,
                (
                    user_id, promoted_name, promoted_name,
                    signal.get("promoted_description", ""),
                    signal.get("category", "communication"), strength,
                    signal.get("reason", ""), influence_summary,
                ),
            )
            created = cursor.rowcount > 0
            cursor.execute(
                "SELECT id FROM user_personality_traits "
                "WHERE user_id = %s AND trait = %s AND owner = 'aetheraeon'",
                (user_id, promoted_name),
            )
            promoted_trait_id = cursor.fetchone()["id"]
            if created:
                _record_trait_history(
                    cursor, user_id, promoted_trait_id, promoted_name, "created",
                    str(signal.get("reason") or "Repeated interaction preference."),
                    "aetheraeon_evolution",
                )
            cursor.execute(
                """
                UPDATE personality_trait_candidates
                SET status = 'promoted', promoted_trait_id = %s,
                    promoted_at = CURRENT_TIMESTAMP
                WHERE id = %s AND user_id = %s
                """,
                (promoted_trait_id, candidate_id, user_id),
            )
        elif existing and existing.get("status") == "promoted" and existing.get("promoted_trait_id"):
            cursor.execute(
                """
                UPDATE user_personality_traits
                SET strength = LEAST(100, strength + 5),
                    influence_summary = %s
                WHERE id = %s AND user_id = %s AND owner = 'aetheraeon'
                """,
                (
                    f"Reinforced by {state['evidence_count']} distinct interaction signals.",
                    existing["promoted_trait_id"], user_id,
                ),
            )
            if cursor.rowcount:
                cursor.execute(
                    "SELECT name FROM user_personality_traits WHERE id = %s AND user_id = %s",
                    (existing["promoted_trait_id"], user_id),
                )
                promoted = cursor.fetchone()
                _record_trait_history(
                    cursor, user_id, existing["promoted_trait_id"], promoted["name"],
                    "evolved", "Additional preference evidence.",
                    "aetheraeon_evolution",
                )

        db_connection.commit()
        cursor.execute(
            "SELECT * FROM personality_trait_candidates WHERE id = %s AND user_id = %s",
            (candidate_id, user_id),
        )
        return _normalize_trait_candidate(cursor.fetchone())
    except Exception:
        db_connection.rollback()
        raise
    finally:
        cursor.close()
        db_connection.close()


def delete_user_personality_trait(
    user_id: int,
    trait_id: int = None,
    trait: str = None
) -> bool:
    """Remove a user- or AI-owned trait, as both owners permit user removal."""
    db_connection = get_db()
    cursor = db_connection.cursor(dictionary=True)
    try:
        if trait_id is not None:
            cursor.execute(
                "SELECT id, name, owner FROM user_personality_traits WHERE id = %s AND user_id = %s",
                (trait_id, user_id),
            )
        elif trait is not None:
            cursor.execute(
                "SELECT id, name, owner FROM user_personality_traits "
                "WHERE user_id = %s AND trait = %s AND owner = 'user'",
                (user_id, trait),
            )
        else:
            return False
        record = cursor.fetchone()
        if not record:
            return False
        from core.trait_authority import require_trait_operation
        require_trait_operation("user", record["owner"], "delete")
        if record["owner"] == "aetheraeon":
            cursor.execute(
                "SELECT id FROM personality_trait_candidates "
                "WHERE user_id = %s AND promoted_trait_id = %s",
                (user_id, record["id"]),
            )
            promoted_candidates = cursor.fetchall()
            if promoted_candidates:
                cursor.execute(
                    "DELETE FROM personality_trait_candidates "
                    "WHERE user_id = %s AND promoted_trait_id = %s",
                    (user_id, record["id"]),
                )
                cursor.execute(
                    "DELETE FROM personality_trait_history "
                    "WHERE user_id = %s AND trait_id = %s "
                    "AND source = 'aetheraeon_evolution'",
                    (user_id, record["id"]),
                )
        _record_trait_history(
            cursor, user_id, record["id"], record["name"], "removed",
            "Removed by user.",
            "user_removed_aetheraeon"
            if record["owner"] == "aetheraeon" else "user",
        )
        if trait_id is not None:
            cursor.execute(
                "DELETE FROM user_personality_traits WHERE id = %s AND user_id = %s",
                (trait_id, user_id)
            )
        elif trait is not None:
            cursor.execute(
                "DELETE FROM user_personality_traits "
                "WHERE user_id = %s AND trait = %s AND owner = 'user'",
                (user_id, trait)
            )
        db_connection.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        db_connection.close()


def delete_aetheraeon_personality_trait(user_id: int, trait_id: int) -> bool:
    """Internal AI removal path; user-owned traits are query-inaccessible."""
    from core.trait_authority import require_trait_operation
    require_trait_operation("aetheraeon", "aetheraeon", "delete")
    db_connection = get_db()
    cursor = db_connection.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT id, name FROM user_personality_traits "
            "WHERE id = %s AND user_id = %s AND owner = 'aetheraeon'",
            (trait_id, user_id),
        )
        record = cursor.fetchone()
        if not record:
            return False
        _record_trait_history(
            cursor, user_id, trait_id, record["name"], "removed",
            "Removed by Aetheraeon evolution.", "aetheraeon",
        )
        cursor.execute(
            "DELETE FROM user_personality_traits "
            "WHERE id = %s AND user_id = %s AND owner = 'aetheraeon'",
            (trait_id, user_id),
        )
        db_connection.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        db_connection.close()


def _get_conv_numeric_id(conversation_uuid: str) -> int | None:
    """
    ============================================================
    CONVERSATION ID BRIDGE SYSTEM (SCHEMA TRANSLATION LAYER)
    ============================================================

    PURPOSE:
    Resolves a conversation UUID (public identifier)
    into its internal numeric database ID.

    ARCHITECTURE ROLE:
    This function bridges two identity systems:
        - External Layer → UUID (string-based API ID)
        - Internal Layer → Integer primary key (DB FK system)

    USED FOR:
    - Message insertion (foreign key mapping)
    - Conversation tracking
    - Internal database joins
    - API → DB translation layer

    RETURNS:
    - Integer conversation ID if found
    - None if UUID does not exist
    """

    # ─────────────────────────────────────────────
    # 1. DATABASE CONNECTION INITIALIZATION
    # ─────────────────────────────────────────────

    db_connection = get_db()
    cursor = db_connection.cursor()

    try:

        # ─────────────────────────────────────────
        # 2. UUID LOOKUP QUERY
        # ─────────────────────────────────────────
        # Converts external conversation UUID into DB PK
        # ─────────────────────────────────────────

        cursor.execute(
            """
            SELECT id
            FROM conversations
            WHERE conversation_id = %s
            """,
            (conversation_uuid,)
        )

        result_row = cursor.fetchone()

        # ─────────────────────────────────────────
        # 3. SAFE RETURN HANDLING
        # ─────────────────────────────────────────

        return result_row[0] if result_row else None

    finally:

        # ─────────────────────────────────────────
        # 4. RESOURCE CLEANUP
        # ─────────────────────────────────────────

        cursor.close()
        db_connection.close()


# ============================================================
# CONVERSATION SYSTEM — CREATE CONVERSATION
# ============================================================

def create_conversation(user_id: int, conv_uuid: str, name: str = "New Conversation") -> None:
    """
    ============================================================
    CONVERSATION LIFECYCLE SYSTEM (CREATION ENGINE)
    ============================================================

    PURPOSE:
    Creates a new conversation record for a user.

    ARCHITECTURE ROLE:
    This function initializes a conversation container
    that will later store message history.

    USED FOR:
    - Starting new chat sessions
    - Initializing conversation threads
    - API conversation creation endpoint
    - UI "New Chat" button functionality

    DATABASE STRUCTURE:
    - user_id → owner of conversation
    - conversation_id → public UUID identifier
    - name → human-readable title
    """

    # ─────────────────────────────────────────────
    # 1. DATABASE CONNECTION INITIALIZATION
    # ─────────────────────────────────────────────

    db_connection = get_db()
    cursor = db_connection.cursor()

    try:

        # ─────────────────────────────────────────
        # 2. CONVERSATION INSERTION OPERATION
        # ─────────────────────────────────────────
        # Creates new conversation entry in database
        # linked to user and UUID identifier
        # ─────────────────────────────────────────

        cursor.execute(
            """
            INSERT INTO conversations (
                user_id,
                conversation_id,
                name
            )
            VALUES (%s, %s, %s)
            """,
            (
                user_id,
                conv_uuid,
                name
            )
        )

        db_connection.commit()

    finally:

        # ─────────────────────────────────────────
        # 3. RESOURCE CLEANUP
        # ─────────────────────────────────────────

        cursor.close()
        db_connection.close()


# ============================================================
# CONVERSATION SYSTEM — GET USER CONVERSATIONS
# ============================================================

def get_conversations(user_id: int) -> list[dict]:
    """
    ============================================================
    CONVERSATION LIST SYSTEM (UI + NAVIGATION LAYER)
    ============================================================

    PURPOSE:
    Retrieves all conversations for a specific user.

    USED FOR:
    - Chat sidebar conversation list
    - UI navigation between chats
    - Conversation sorting and prioritization
    - Frontend chat history overview

    SORTING RULE:
    - Pinned conversations appear first
    - Newest conversations appear first within each group
    """

    # ─────────────────────────────────────────────
    # 1. DATABASE CONNECTION INITIALIZATION
    # ─────────────────────────────────────────────

    db_connection = get_db()
    cursor = db_connection.cursor(dictionary=True)

    try:

        # ─────────────────────────────────────────
        # 2. CONVERSATION QUERY EXECUTION
        # ─────────────────────────────────────────
        # Fetch all user conversations with UI-relevant metadata
        # ─────────────────────────────────────────

        cursor.execute(
            """
            SELECT
                conversation_id,
                name,
                pinned,
                created_at
            FROM conversations
            WHERE user_id = %s
            ORDER BY
                pinned DESC,
                created_at DESC
            """,
            (user_id,)
        )

        conversation_rows = cursor.fetchall()

        # ─────────────────────────────────────────
        # 3. TIMESTAMP SERIALIZATION FOR JSON SAFETY
        # ─────────────────────────────────────────
        # Flask jsonify cannot serialize datetime objects directly
        # Convert to string for frontend compatibility
        # ─────────────────────────────────────────

        for conversation in conversation_rows:

            created_timestamp = conversation.get("created_at")

            if created_timestamp:
                conversation["created_at"] = str(created_timestamp)

        return conversation_rows

    finally:

        # ─────────────────────────────────────────
        # 4. RESOURCE CLEANUP
        # ─────────────────────────────────────────

        cursor.close()
        db_connection.close()


def conversation_belongs_to_user(conv_uuid: str, user_id: int) -> bool:
    """Return whether a conversation UUID belongs to the supplied user."""
    db_connection = get_db()
    cursor = db_connection.cursor()
    try:
        cursor.execute(
            "SELECT 1 FROM conversations WHERE conversation_id = %s AND user_id = %s",
            (conv_uuid, user_id),
        )
        return cursor.fetchone() is not None
    finally:
        cursor.close()
        db_connection.close()


# ============================================================
# CONVERSATION SYSTEM — RENAME CONVERSATION
# ============================================================

def rename_conversation(conv_uuid: str, user_id: int, new_name: str) -> bool:
    """
    ============================================================
    CONVERSATION METADATA SYSTEM (RENAME ENGINE)
    ============================================================

    PURPOSE:
    Updates the display name of a conversation.

    USED FOR:
    - User manual renaming of chats
    - AI-generated conversation titles
    - UI sidebar title updates
    - Conversation organization system

    SAFETY RULE:
    Only updates conversations belonging to the authenticated user.
    """

    # ─────────────────────────────────────────────
    # 1. DATABASE CONNECTION INITIALIZATION
    # ─────────────────────────────────────────────

    db_connection = get_db()
    cursor = db_connection.cursor()

    try:

        # ─────────────────────────────────────────
        # 2. UPDATE CONVERSATION NAME
        # ─────────────────────────────────────────
        # Ensures both:
        # - conversation matches UUID
        # - conversation belongs to user
        #
        # This prevents cross-user modification
        # ─────────────────────────────────────────

        cursor.execute(
            """
            UPDATE conversations
            SET name = %s
            WHERE conversation_id = %s
              AND user_id = %s
            """,
            (
                new_name,
                conv_uuid,
                user_id
            )
        )

        db_connection.commit()

        # ─────────────────────────────────────────
        # 3. RETURN SUCCESS STATE
        # ─────────────────────────────────────────
        # rowcount > 0 means update actually happened
        # ─────────────────────────────────────────

        return cursor.rowcount > 0

    finally:

        # ─────────────────────────────────────────
        # 4. RESOURCE CLEANUP
        # ─────────────────────────────────────────

        cursor.close()
        db_connection.close()


# ============================================================
# CONVERSATION SYSTEM — DELETE CONVERSATION
# ============================================================

def delete_conversation(conv_uuid: str, user_id: int) -> bool:
    """
    ============================================================
    CONVERSATION DELETION SYSTEM (FULL CLEANUP ENGINE)
    ============================================================

    PURPOSE:
    Permanently deletes a conversation and all associated messages.

    ARCHITECTURE ROLE:
    This function is responsible for complete data cleanup across:
        - conversations table
        - messages table (foreign key dependent data)

    SAFETY DESIGN:
    - Resolves numeric ID before deletion
    - Prevents orphaned message records
    - Ensures user ownership validation
    - Uses rollback on failure

    RETURN:
    - True  → conversation successfully deleted
    - False → deletion failed or conversation not found
    """

    # ─────────────────────────────────────────────
    # 1. DATABASE CONNECTION INITIALIZATION
    # ─────────────────────────────────────────────

    db_connection = get_db()
    cursor = db_connection.cursor()

    try:

        # ─────────────────────────────────────────
        # 2. RESOLVE INTERNAL NUMERIC CONVERSATION ID
        # ─────────────────────────────────────────
        # Converts UUID → internal foreign key ID
        # Required for message table cleanup
        # ─────────────────────────────────────────

        internal_conversation_id = _get_conv_numeric_id(conv_uuid)

        # ─────────────────────────────────────────
        # 3. DELETE MESSAGES (DEPENDENT DATA FIRST)
        # ─────────────────────────────────────────
        # Only executed if valid conversation exists
        # Prevents unnecessary DB operations
        # ─────────────────────────────────────────

        if internal_conversation_id is not None:
            cursor.execute(
                """
                DELETE FROM messages
                WHERE conversation_id = %s
                """,
                (internal_conversation_id,)
            )

        # ─────────────────────────────────────────
        # 4. DELETE CONVERSATION RECORD
        # ─────────────────────────────────────────
        # Ensures ownership validation via user_id
        # Prevents cross-user deletion attacks
        # ─────────────────────────────────────────

        cursor.execute(
            """
            DELETE FROM conversations
            WHERE conversation_id = %s
              AND user_id = %s
            """,
            (
                conv_uuid,
                user_id
            )
        )

        # ─────────────────────────────────────────
        # 5. COMMIT TRANSACTION
        # ─────────────────────────────────────────

        db_connection.commit()

        # ─────────────────────────────────────────
        # 6. VERIFY DELETION SUCCESS
        # ─────────────────────────────────────────
        # Double-check existence instead of relying
        # on rowcount (more reliable across DB engines)
        # ─────────────────────────────────────────

        cursor.execute(
            """
            SELECT 1
            FROM conversations
            WHERE conversation_id = %s
              AND user_id = %s
            """,
            (
                conv_uuid,
                user_id
            )
        )

        conversation_still_exists = cursor.fetchone()

        return conversation_still_exists is None

    except Exception as error:

        # ─────────────────────────────────────────
        # 7. FAILURE HANDLING / ROLLBACK SAFETY
        # ─────────────────────────────────────────

        db_connection.rollback()
        print(f"[DELETE ERROR] {error}")

        return False

    finally:

        # ─────────────────────────────────────────
        # 8. RESOURCE CLEANUP
        # ─────────────────────────────────────────

        cursor.close()
        db_connection.close()


# ============================================================
# CONVERSATION SYSTEM — PIN / UNPIN CONVERSATION
# ============================================================

def pin_conversation(conv_uuid: str, user_id: int, pinned: bool) -> bool:
    """
    ============================================================
    CONVERSATION UI PRIORITY SYSTEM (PINNING ENGINE)
    ============================================================

    PURPOSE:
    Updates the "pinned" state of a conversation.

    ARCHITECTURE ROLE:
    Controls UI-level prioritization of conversations,
    affecting how they are displayed in the chat sidebar.

    USED FOR:
    - Pinning important conversations to the top
    - UI sidebar organization
    - User productivity shortcuts
    - Persistent conversation prioritization
    """

    # ─────────────────────────────────────────────
    # 1. DATABASE CONNECTION INITIALIZATION
    # ─────────────────────────────────────────────

    db_connection = get_db()
    cursor = db_connection.cursor()

    try:

        # ─────────────────────────────────────────
        # 2. PIN STATE NORMALIZATION
        # ─────────────────────────────────────────
        # Converts boolean input into database-safe integer
        # pinned=True  → 1
        # pinned=False → 0
        # ─────────────────────────────────────────

        pin_value = 1 if pinned else 0

        # ─────────────────────────────────────────
        # 3. UPDATE CONVERSATION PIN STATE
        # ─────────────────────────────────────────
        # Ensures:
        # - correct conversation ownership
        # - only updates user's own data
        # ─────────────────────────────────────────

        cursor.execute(
            """
            UPDATE conversations
            SET pinned = %s
            WHERE conversation_id = %s
              AND user_id = %s
            """,
            (
                pin_value,
                conv_uuid,
                user_id
            )
        )

        db_connection.commit()

        # ─────────────────────────────────────────
        # 4. RETURN UPDATE RESULT
        # ─────────────────────────────────────────

        return cursor.rowcount > 0

    finally:

        # ─────────────────────────────────────────
        # 5. RESOURCE CLEANUP
        # ─────────────────────────────────────────

        cursor.close()
        db_connection.close()


# ============================================================
# MESSAGE SYSTEM — SAVE MESSAGE (CORE DATABASE WRITE ENGINE)
# ============================================================

def _save_message(
    conv_uuid: str,
    user_id: int,
    role: str,
    content: str,
    tool_used: str = None,
    metadata: str = None
) -> None:
    """
    ============================================================
    MESSAGE PERSISTENCE SYSTEM (WRITE ENGINE LAYER)
    ============================================================

    PURPOSE:
    This is the core message storage function for the AI system.

    ARCHITECTURE ROLE:
    Converts conversation-level UUID into internal database ID
    and persists chat messages into long-term storage.

    USED FOR:
    - User messages
    - AI responses
    - Tool execution logs (optional metadata)
    - Conversation history reconstruction

    IMPORTANT RULES:
    - role must be "user" or "ai"
    - silently skips if conversation does not exist
    - all inputs are sanitized before database insertion
    """

    # ─────────────────────────────────────────────
    # 1. CONVERSATION ID RESOLUTION (UUID → INT)
    # ─────────────────────────────────────────────
    # This ensures compatibility between API layer (UUID)
    # and database schema (integer foreign key)
    # ─────────────────────────────────────────────

    internal_conversation_id = _get_conv_numeric_id(conv_uuid)

    if internal_conversation_id is None:
        # Conversation does not exist or is invalid
        return

    # ─────────────────────────────────────────────
    # 2. INPUT SANITIZATION (CRITICAL SAFETY LAYER)
    # ─────────────────────────────────────────────
    # Prevents:
    # - emoji / utf8 encoding crashes
    # - None-type DB inserts
    # - corrupted metadata storage
    # ─────────────────────────────────────────────

    sanitized_content = system_utils.safe_string(content)
    sanitized_role = system_utils.safe_string(role)

    sanitized_tool_used = system_utils.safe_string(tool_used) if tool_used else None
    sanitized_metadata  = system_utils.safe_string(metadata) if metadata else None

    # ─────────────────────────────────────────────
    # 3. DEBUG TRACE (SAFE OUTPUT ONLY)
    # ─────────────────────────────────────────────
    # Only logs clean string values (no raw bytes)
    # ─────────────────────────────────────────────

    print(f"[DEBUG] MESSAGE INSERT → {sanitized_role}: {sanitized_content}")

    # ─────────────────────────────────────────────
    # 4. DATABASE CONNECTION INITIALIZATION
    # ─────────────────────────────────────────────

    db_connection = get_db()
    cursor = db_connection.cursor()

    try:

        cursor.execute(
            "SELECT 1 FROM conversations WHERE id = %s AND user_id = %s",
            (internal_conversation_id, user_id),
        )
        if cursor.fetchone() is None:
            return

        # ─────────────────────────────────────────
        # 5. MESSAGE INSERTION OPERATION
        # ─────────────────────────────────────────
        # Stores message in chronological chat history
        # ─────────────────────────────────────────

        cursor.execute(
            """
            INSERT INTO messages (
                conversation_id,
                user_id,
                role,
                content,
                tool_used,
                metadata
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                internal_conversation_id,
                user_id,
                sanitized_role,
                sanitized_content,
                sanitized_tool_used,
                sanitized_metadata
            )
        )

        db_connection.commit()

    finally:

        # ─────────────────────────────────────────
        # 6. RESOURCE CLEANUP
        # ─────────────────────────────────────────

        cursor.close()
        db_connection.close()


# ============================================================
# MESSAGE SYSTEM — SAVE USER MESSAGE (WRAPPER LAYER)
# ============================================================

def save_message_user(
    conv_uuid: str,
    user_id: int,
    content: str,
    tool_used: str = None
) -> None:
    """
    ============================================================
    MESSAGE WRAPPER SYSTEM (USER INPUT INGESTION LAYER)
    ============================================================

    PURPOSE:
    Lightweight wrapper around _save_message() for USER role messages.

    ARCHITECTURE ROLE:
    - Standardizes user message ingestion
    - Adds debug visibility before persistence
    - Ensures consistent message role tagging

    USED FOR:
    - Incoming chat messages from frontend
    - User input tracking
    - Conversation history building
    """

    # ─────────────────────────────────────────────
    # 1. DEBUG LOGGING (SAFE TRUNCATED OUTPUT)
    # ─────────────────────────────────────────────
    # Only prints preview to avoid log flooding
    # ─────────────────────────────────────────────

    print(
        f"[DEBUG] SAVE USER MESSAGE → "
        f"conv={conv_uuid} | "
        f"user={user_id} | "
        f"content_preview={content[:40]}"
    )

    # ─────────────────────────────────────────────
    # 2. DELEGATE TO CORE MESSAGE ENGINE
    # ─────────────────────────────────────────────
    # All actual persistence logic is handled by:
    # _save_message() → core database write layer
    # ─────────────────────────────────────────────

    _save_message(
        conv_uuid,
        user_id,
        "user",
        content,
        tool_used
    )


# ============================================================
# MESSAGE SYSTEM — SAVE AI MESSAGE (WRAPPER LAYER)
# ============================================================

def save_message_ai(
    conv_uuid: str,
    user_id: int,
    content: str,
    tool_used: str = None,
    metadata=None,
) -> None:
    """
    ============================================================
    MESSAGE WRAPPER SYSTEM (AI RESPONSE INGESTION LAYER)
    ============================================================

    PURPOSE:
    Lightweight wrapper around _save_message() for AI-generated messages.

    ARCHITECTURE ROLE:
    - Standardizes AI message persistence
    - Ensures consistent role tagging ("ai")
    - Maintains symmetry with user message pipeline

    USED FOR:
    - AI chat responses
    - Tool-generated responses
    - Final output messages from orchestrator
    """

    # ─────────────────────────────────────────────
    # 1. AI MESSAGE INGESTION (NO DEBUG SPAM BY DEFAULT)
    # ─────────────────────────────────────────────
    # AI messages are typically already system-generated,
    # so logging is intentionally minimal here
    # ─────────────────────────────────────────────

    # ─────────────────────────────────────────────
    # 2. DELEGATE TO CORE MESSAGE ENGINE
    # ─────────────────────────────────────────────
    # All persistence logic is handled by _save_message()
    # ensuring consistent storage behavior across roles
    # ─────────────────────────────────────────────

    _save_message(
        conv_uuid,
        user_id,
        "ai",
        content,
        tool_used,
        json.dumps(metadata, separators=(",", ":"), default=str)
        if isinstance(metadata, dict) else metadata,
    )
    
# ============================================================
# MESSAGE SYSTEM — GET MESSAGES (CONVERSATION READ ENGINE)
# ============================================================

def get_messages(conv_uuid: str, user_id: int = None) -> list[dict]:
    """
    ============================================================
    MESSAGE RETRIEVAL SYSTEM (CHAT HISTORY RECONSTRUCTION LAYER)
    ============================================================

    PURPOSE:
    Retrieves all messages for a given conversation in chronological order.

    ARCHITECTURE ROLE:
    This function reconstructs full conversation history for:
    - AI context building (orchestrator)
    - Chat UI rendering
    - Memory summarization systems

    ORDERING RULE:
    - Oldest messages first
    - Stable ordering using timestamp + id fallback
    """

    # ─────────────────────────────────────────────
    # 1. RESOLVE CONVERSATION UUID → INTERNAL ID
    # ─────────────────────────────────────────────
    # Database stores numeric foreign keys, not UUIDs
    # This ensures API layer compatibility with DB schema
    # ─────────────────────────────────────────────

    internal_conversation_id = _get_conv_numeric_id(conv_uuid)

    if internal_conversation_id is None:
        return []

    # ─────────────────────────────────────────────
    # 2. DATABASE CONNECTION INITIALIZATION
    # ─────────────────────────────────────────────

    db_connection = get_db()
    cursor = db_connection.cursor(dictionary=True)

    try:

        # ─────────────────────────────────────────
        # 3. MESSAGE HISTORY QUERY EXECUTION
        # ─────────────────────────────────────────
        # Retrieves full conversation history with:
        # - role (user/ai)
        # - content (message body)
        # - tool_used (execution context)
        # - created_at (timestamp)
        # ─────────────────────────────────────────

        ownership_clause = " AND c.user_id = %s" if user_id is not None else ""
        parameters = (internal_conversation_id, user_id) if user_id is not None else (internal_conversation_id,)
        cursor.execute(
            f"""
            SELECT
                m.id AS message_id,
                m.role,
                m.content,
                m.tool_used,
                m.metadata,
                m.created_at
            FROM messages m
            JOIN conversations c ON c.id = m.conversation_id
            WHERE m.conversation_id = %s{ownership_clause}
            ORDER BY m.created_at ASC, m.id ASC
            """,
            parameters
        )

        message_rows = cursor.fetchall()

        # ─────────────────────────────────────────
        # 4. TIMESTAMP SERIALIZATION FOR FRONTEND
        # ─────────────────────────────────────────
        # Converts datetime objects → string format
        # Ensures JSON compatibility for Flask API
        # ─────────────────────────────────────────

        for message in message_rows:

            raw_metadata = message.pop("metadata", None)
            if raw_metadata:
                try:
                    parsed_metadata = json.loads(raw_metadata)
                    message["processing"] = parsed_metadata.get("processing")
                    response_metadata = parsed_metadata.get("response_metadata")
                    if isinstance(response_metadata, dict):
                        message["response_metadata"] = response_metadata
                except (TypeError, ValueError, json.JSONDecodeError):
                    message["processing"] = None

            timestamp = message.get("created_at")

            if timestamp:
                message["created_at"] = str(timestamp)

        return message_rows

    finally:

        # ─────────────────────────────────────────
        # 5. RESOURCE CLEANUP
        # ─────────────────────────────────────────

        cursor.close()
        db_connection.close()


# ============================================================
# MESSAGE SYSTEM — SEARCH MESSAGES (FULL-TEXT MEMORY ENGINE)
# ============================================================

CHAT_SEARCH_PAGE_SIZE = 100
CHAT_SEARCH_SESSION_MAX_RESULTS = 500


class ChatSearchCursorError(ValueError):
    """Raised when a chat-history search cursor is malformed or exhausted."""


def _escape_like_literal(query: str) -> str:
    """Escape SQL LIKE metacharacters so chat search remains literal."""

    return query.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _encode_chat_search_cursor(created_at, message_id: int, returned_count: int) -> str:
    """Encode opaque pagination state; it is not an authorization token."""

    payload = {
        "created_at": str(created_at),
        "message_id": int(message_id),
        "returned_count": int(returned_count),
    }
    encoded = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return base64.urlsafe_b64encode(encoded).decode("ascii").rstrip("=")


def _decode_chat_search_cursor(cursor: str | None) -> tuple[str | None, int | None, int]:
    """Validate one opaque cursor and return its stable ordering boundary."""

    if cursor is None or not str(cursor).strip():
        return None, None, 0
    try:
        encoded = str(cursor).strip()
        padded = encoded + "=" * (-len(encoded) % 4)
        payload = json.loads(base64.urlsafe_b64decode(padded.encode("ascii")))
        created_at = str(payload["created_at"]).strip()
        message_id = int(payload["message_id"])
        returned_count = int(payload["returned_count"])
    except (KeyError, TypeError, ValueError, UnicodeDecodeError, binascii.Error, json.JSONDecodeError) as exc:
        raise ChatSearchCursorError("invalid chat search cursor") from exc
    if not created_at or len(created_at) > 64 or message_id < 1 or returned_count < 0:
        raise ChatSearchCursorError("invalid chat search cursor")
    if returned_count >= CHAT_SEARCH_SESSION_MAX_RESULTS:
        raise ChatSearchCursorError("chat search result cap reached")
    return created_at, message_id, returned_count


def search_messages_page(
    user_id: int,
    query: str,
    *,
    cursor: str | None = None,
    page_size: int = CHAT_SEARCH_PAGE_SIZE,
) -> dict:
    """Return a cursor-paginated, owner-scoped page of literal chat matches.

    Chat history remains MariaDB-backed and independent from ChromaDB semantic
    memory search. The cursor count is a user-experience cap only; every query
    still scopes results to the authenticated owner's conversations.
    """

    if not isinstance(query, str) or not query.strip():
        raise ValueError("chat search query is required")
    if isinstance(page_size, bool) or not isinstance(page_size, int) or page_size < 1:
        raise ValueError("page_size must be a positive integer")

    cursor_created_at, cursor_message_id, returned_count = _decode_chat_search_cursor(cursor)
    remaining = CHAT_SEARCH_SESSION_MAX_RESULTS - returned_count
    effective_page_size = min(page_size, CHAT_SEARCH_PAGE_SIZE, remaining)
    if effective_page_size < 1:
        raise ChatSearchCursorError("chat search result cap reached")

    db_connection = get_db()
    cursor_handle = db_connection.cursor(dictionary=True)
    search_pattern = f"%{_escape_like_literal(query.strip())}%"
    where_cursor = ""
    parameters: list = [user_id, search_pattern]
    if cursor_created_at is not None and cursor_message_id is not None:
        where_cursor = """
              AND (m.created_at < %s OR (m.created_at = %s AND m.id < %s))
        """
        parameters.extend((cursor_created_at, cursor_created_at, cursor_message_id))
    parameters.append(effective_page_size + 1)

    try:
        cursor_handle.execute(
            f"""
            SELECT
                m.id AS message_id,
                m.role,
                m.content,
                m.tool_used,
                m.created_at,
                c.conversation_id,
                c.name AS conversation_name
            FROM messages m
            INNER JOIN conversations c
                ON c.id = m.conversation_id
            WHERE c.user_id = %s
              AND m.content LIKE %s ESCAPE '\\\\'
            {where_cursor}
            ORDER BY m.created_at DESC, m.id DESC
            LIMIT %s
            """,
            tuple(parameters),
        )
        fetched_results = cursor_handle.fetchall()
        has_more = len(fetched_results) > effective_page_size
        search_results = fetched_results[:effective_page_size]
        next_cursor = None

        if has_more and search_results:
            last_result = search_results[-1]
            next_cursor = _encode_chat_search_cursor(
                last_result.get("created_at"),
                last_result.get("message_id"),
                returned_count + len(search_results),
            )
        if returned_count + len(search_results) >= CHAT_SEARCH_SESSION_MAX_RESULTS:
            has_more = False
            next_cursor = None

        for result in search_results:
            timestamp = result.get("created_at")
            if timestamp:
                result["created_at"] = str(timestamp)

        return {
            "results": search_results,
            "count": len(search_results),
            "has_more": has_more,
            "next_cursor": next_cursor,
        }
    finally:
        cursor_handle.close()
        db_connection.close()


# Legacy list-returning helper retained for non-WebUI callers.
def search_messages(user_id: int, query: str) -> list[dict]:
    """
    ============================================================
    MESSAGE SEARCH SYSTEM (GLOBAL MEMORY QUERY ENGINE)
    ============================================================

    PURPOSE:
    Performs a full-text LIKE search across all messages
    belonging to a specific user.

    ARCHITECTURE ROLE:
    This function acts as a cross-conversation memory scanner,
    allowing retrieval of relevant past messages regardless of
    conversation grouping.

    USED FOR:
    - Memory recall features
    - AI contextual search
    - User search UI
    - Debugging conversation history
    """

    # ─────────────────────────────────────────────
    # 1. DATABASE CONNECTION INITIALIZATION
    # ─────────────────────────────────────────────

    db_connection = get_db()
    cursor = db_connection.cursor(dictionary=True)

    # ─────────────────────────────────────────────
    # 2. SEARCH PATTERN PREPARATION
    # ─────────────────────────────────────────────
    # SQL LIKE wildcard search:
    # %query% → matches anywhere in text
    # ─────────────────────────────────────────────

    search_pattern = f"%{query}%"

    try:

        # ─────────────────────────────────────────
        # 3. CROSS-CONVERSATION SEARCH QUERY
        # ─────────────────────────────────────────
        # Joins:
        # - messages table (content)
        # - conversations table (ownership + metadata)
        #
        # Ensures:
        # - only messages belonging to user_id are returned
        # - results include conversation context
        # ─────────────────────────────────────────

        cursor.execute(
            """
            SELECT
                m.role,
                m.content,
                m.tool_used,
                m.created_at,
                c.conversation_id,
                c.name AS conversation_name
            FROM messages m
            INNER JOIN conversations c
                ON c.id = m.conversation_id
            WHERE c.user_id = %s
              AND m.content LIKE %s
            ORDER BY m.created_at DESC
            LIMIT 50
            """,
            (
                user_id,
                search_pattern
            )
        )

        search_results = cursor.fetchall()

        # ─────────────────────────────────────────
        # 4. TIMESTAMP SERIALIZATION FOR API
        # ─────────────────────────────────────────

        for result in search_results:

            timestamp = result.get("created_at")

            if timestamp:
                result["created_at"] = str(timestamp)

        return search_results

    finally:

        # ─────────────────────────────────────────
        # 5. RESOURCE CLEANUP
        # ─────────────────────────────────────────

        cursor.close()
        db_connection.close()


# ============================================================
# PLAYBOOK SYSTEM — RETRIEVE USER PLAYBOOKS
# ============================================================

def get_playbooks(user_id: int) -> list[dict]:
    """
    ============================================================
    PLAYBOOK RETRIEVAL SYSTEM (MEMORY-BASED TEMPLATE ENGINE)
    ============================================================

    PURPOSE:
    Retrieves all saved AI playbooks belonging to a user.

    ARCHITECTURE ROLE:
    Playbooks are stored inside the memory table using:
        type = 'playbook'

    This allows reuse of the existing memory system instead of
    creating a separate database schema.

    PLAYBOOK STRUCTURE:
    - tags     → playbook name
    - content  → JSON configuration / instructions
    - created_at → timestamp

    USED FOR:
    - AI automation templates
    - reusable workflows
    - prompt + tool execution presets
    - user-defined AI behaviors
    """

    # ─────────────────────────────────────────────
    # 1. DATABASE CONNECTION INITIALIZATION
    # ─────────────────────────────────────────────

    db_connection = get_db()
    cursor = db_connection.cursor(dictionary=True)

    try:

        # ─────────────────────────────────────────
        # 2. QUERY PLAYBOOK RECORDS
        # ─────────────────────────────────────────
        # We filter:
        # - by user ownership
        # - by memory type = playbook
        #
        # This ensures playbooks are isolated per user
        # and not mixed with general memory entries.
        # ─────────────────────────────────────────

        cursor.execute(
            """
            SELECT
                id,
                tags AS name,
                content,
                created_at
            FROM memory
            WHERE user_id = %s
              AND type = 'playbook'
            ORDER BY created_at DESC
            """,
            (user_id,)
        )

        playbook_rows = cursor.fetchall()

        # ─────────────────────────────────────────
        # 3. TIMESTAMP SERIALIZATION FOR API
        # ─────────────────────────────────────────

        for playbook in playbook_rows:

            timestamp = playbook.get("created_at")

            if timestamp:
                playbook["created_at"] = str(timestamp)

        return playbook_rows

    finally:

        # ─────────────────────────────────────────
        # 4. RESOURCE CLEANUP
        # ─────────────────────────────────────────

        cursor.close()
        db_connection.close()


# ============================================================
# PLAYBOOK SYSTEM — SAVE USER PLAYBOOK (CREATE NEW TEMPLATE)
# ============================================================

def save_playbook(user_id: int, name: str, content_json: str) -> int:
    """
    ============================================================
    PLAYBOOK CREATION SYSTEM (AUTOMATION TEMPLATE WRITER)
    ============================================================

    PURPOSE:
    Saves a new AI playbook into the memory database.

    ARCHITECTURE ROLE:
    Playbooks are stored inside the unified memory table using:
        type = 'playbook'

    This avoids schema duplication and allows playbooks to be:
    - searchable via memory system
    - reused in AI orchestration
    - managed through same persistence layer

    PLAYBOOK STRUCTURE:
    - name        → stored in tags column
    - content     → JSON automation logic / workflow definition
    - user_id     → ownership isolation
    """

    # ─────────────────────────────────────────────
    # 1. DATABASE CONNECTION INITIALIZATION
    # ─────────────────────────────────────────────

    db_connection = get_db()
    cursor = db_connection.cursor()

    try:

        # ─────────────────────────────────────────
        # 2. INSERT PLAYBOOK RECORD
        # ─────────────────────────────────────────
        # We store:
        # - type = 'playbook' (identifies memory subtype)
        # - content = JSON workflow definition
        # - tags = human-readable playbook name
        # ─────────────────────────────────────────

        cursor.execute(
            """
            INSERT INTO memory (
                user_id,
                type,
                content,
                tags
            )
            VALUES (
                %s,
                'playbook',
                %s,
                %s
            )
            """,
            (
                user_id,
                content_json,
                name
            )
        )

        # Commit transaction to persist playbook
        db_connection.commit()

        # Return newly created playbook ID
        return cursor.lastrowid

    finally:

        # ─────────────────────────────────────────
        # 3. CLEAN RESOURCE HANDLING
        # ─────────────────────────────────────────

        cursor.close()
        db_connection.close()


# ============================================================
# PLAYBOOK SYSTEM — UPDATE EXISTING PLAYBOOK
# ============================================================

def update_playbook(
    playbook_id: int,
    user_id: int,
    name: str,
    content_json: str
) -> bool:
    """
    ============================================================
    PLAYBOOK UPDATE SYSTEM (AUTOMATION TEMPLATE MODIFIER)
    ============================================================

    PURPOSE:
    Updates an existing playbook record in the memory database.

    ARCHITECTURE ROLE:
    This function is part of the PLAYBOOK MUTATION LAYER.

    It allows users to:
    - rename automation workflows
    - modify execution logic (JSON)
    - update structured AI behavior definitions

    STORAGE MODEL:
    Playbooks are stored inside the unified memory system:
        table: memory
        type: 'playbook'

    SAFETY BOUNDARIES:
    - Only updates playbooks belonging to the requesting user
    - Prevents cross-user modification
    - Ensures type isolation (only playbooks are affected)
    """

    # ─────────────────────────────────────────────
    # 1. DATABASE CONNECTION INITIALIZATION
    # ─────────────────────────────────────────────

    db_connection = get_db()
    cursor = db_connection.cursor()

    try:

        # ─────────────────────────────────────────
        # 2. EXECUTE PLAYBOOK UPDATE
        # ─────────────────────────────────────────
        # We update:
        # - content → JSON automation logic
        # - tags    → human-readable playbook name
        #
        # SECURITY FILTER:
        # Ensures:
        # - correct playbook ID
        # - correct user ownership
        # - correct memory type ('playbook')
        # ─────────────────────────────────────────

        cursor.execute(
            """
            UPDATE memory
            SET
                content = %s,
                tags    = %s
            WHERE id = %s
              AND user_id = %s
              AND type = 'playbook'
            """,
            (
                content_json,
                name,
                playbook_id,
                user_id
            )
        )

        # Commit update operation
        db_connection.commit()

        # ─────────────────────────────────────────
        # 3. RETURN OPERATION STATUS
        # ─────────────────────────────────────────

        return cursor.rowcount > 0

    finally:

        # ─────────────────────────────────────────
        # 4. RESOURCE CLEANUP
        # ─────────────────────────────────────────

        cursor.close()
        db_connection.close()


# ============================================================
# PLAYBOOK SYSTEM — DELETE EXISTING PLAYBOOK
# ============================================================

def delete_playbook(playbook_id: int, user_id: int) -> bool:
    """
    ============================================================
    PLAYBOOK DELETE SYSTEM (AUTOMATION TEMPLATE REMOVAL ENGINE)
    ============================================================

    PURPOSE:
    Permanently removes a playbook from the memory database.

    ARCHITECTURE ROLE:
    This is the final stage of the PLAYBOOK LIFECYCLE SYSTEM.

    It allows users to:
    - delete outdated automation workflows
    - remove unused AI behavior templates
    - clean up memory-based playbook storage

    STORAGE MODEL:
    Playbooks are stored inside the unified memory system:
        table: memory
        type: 'playbook'

    SAFETY BOUNDARIES:
    - Only deletes playbooks owned by the requesting user
    - Ensures only 'playbook' type entries are affected
    - Prevents accidental deletion of unrelated memory entries
    """

    # ─────────────────────────────────────────────
    # 1. DATABASE CONNECTION INITIALIZATION
    # ─────────────────────────────────────────────

    db_connection = get_db()
    cursor = db_connection.cursor()

    try:

        # ─────────────────────────────────────────
        # 2. EXECUTE DELETE OPERATION
        # ─────────────────────────────────────────
        # We enforce strict filtering:
        # - playbook_id must match
        # - user_id must match ownership
        # - type must be 'playbook'
        #
        # This prevents accidental deletion of:
        # - general memory
        # - chat history
        # - other system data
        # ─────────────────────────────────────────

        cursor.execute(
            """
            DELETE FROM memory
            WHERE id = %s
              AND user_id = %s
              AND type = 'playbook'
            """,
            (
                playbook_id,
                user_id
            )
        )

        # Commit deletion immediately
        db_connection.commit()

        # ─────────────────────────────────────────
        # 3. RETURN DELETE STATUS
        # ─────────────────────────────────────────

        return cursor.rowcount > 0

    finally:

        # ─────────────────────────────────────────
        # 4. CLEAN RESOURCE HANDLING
        # ─────────────────────────────────────────

        cursor.close()
        db_connection.close()
        
        
# ============================================================
# MEMORY ENTRY FORMATTING ENGINE
# ============================================================

def fmt_entry(
    entry_id: str,
    text_content: str,
    metadata: dict,
    index: int = None
) -> str:
    """
    ============================================================
    MEMORY ENTRY FORMATTING SYSTEM (DEBUG + DISPLAY LAYER)
    ============================================================

    PURPOSE:
    Formats a raw memory entry into a structured human-readable
    debug/display string.

    USED FOR:
    - Memory inspection tools
    - Debugging memory storage
    - Logging / visualization of stored entries

    ARCHITECTURE ROLE:
    This function belongs in memory_database.py because it is
    directly tied to how memory is stored and represented.

    It does NOT:
    - perform AI reasoning
    - modify memory
    - retrieve data

    It ONLY formats data.
    """

    # ─────────────────────────────────────────────
    # 1. INDEX PREFIX (VISUAL POSITIONING)
    # ─────────────────────────────────────────────

    index_prefix = f"  [{index}]" if index is not None else "  "

    # ─────────────────────────────────────────────
    # 2. EXTRACT CORE METADATA FIELDS
    # ─────────────────────────────────────────────

    memory_type = metadata.get("type", "?")
    timestamp   = metadata.get("timestamp", "")
    source      = metadata.get("source", "")

    # ─────────────────────────────────────────────
    # 3. EXTRACT ADDITIONAL METADATA (NON-CORE FIELDS)
    # ─────────────────────────────────────────────
    # Remove known keys so only custom metadata remains
    # ─────────────────────────────────────────────

    additional_metadata = {
        key: value
        for key, value in metadata.items()
        if key not in ("type", "timestamp", "source")
    }

    # ─────────────────────────────────────────────
    # 4. BUILD FORMATTED OUTPUT STRING
    # ─────────────────────────────────────────────

    formatted_line = (
        f"{index_prefix} [TAG] {memory_type:<14} {timestamp} [{source}]\n"
        f"       [TEXT] {text_content}\n"
        f"       [ID] {entry_id}\n"
    )

    # ─────────────────────────────────────────────
    # 5. APPEND EXTRA METADATA (IF EXISTS)
    # ─────────────────────────────────────────────

    if additional_metadata:
        extra_formatted = "  ".join(
            f"{key}={value}"
            for key, value in additional_metadata.items()
        )
        formatted_line += f"           {extra_formatted}\n"

    # ─────────────────────────────────────────────
    # 6. RETURN FINAL FORMATTED ENTRY
    # ─────────────────────────────────────────────

    return formatted_line


# ============================================================
# MEMORY ENTRY REFERENCE RESOLVER
# ============================================================

def _resolve_entry_by_ref(reference_value, memory_entries):
    """
    ============================================================
    MEMORY ENTRY REFERENCE RESOLUTION
    ============================================================

    PURPOSE:
    Resolve a user-provided memory reference into a single
    valid memory entry tuple.

    SUPPORTED REFERENCES:
    - Numeric index reference
        Example:
            "3"

    - Partial memory ID reference
        Example:
            "6e0bdf"

    RETURNS:
    - (entry_id, memory_text, metadata)
    - None if resolution fails
    """

    # --------------------------------------------------------
    # 1. INPUT NORMALIZATION
    # --------------------------------------------------------

    reference_value = str(reference_value).strip()

    if not reference_value:
        return None

    # --------------------------------------------------------
    # 2. NUMERIC MEMORY INDEX RESOLUTION
    # --------------------------------------------------------
    # Allows users to reference memories from the most recent
    # displayed memory list.
    #
    # Example:
    #   memory delete 3
    # --------------------------------------------------------

    if reference_value.isdigit():

        memory_index = int(reference_value) - 1

        memory_list = get_last_memory_list()

        if 0 <= memory_index < len(memory_list):
            return memory_list[memory_index]

        print(
            f"AI: No memory entry #{reference_value} "
            f"exists in the current memory list."
        )

        return None

    # --------------------------------------------------------
    # 3. MEMORY ID PREFIX MATCHING
    # --------------------------------------------------------
    # Allows partial UUID matching for convenience.
    #
    # Example:
    #   forget 6e0bdf
    # --------------------------------------------------------

    matching_entries = []

    for entry_id, memory_text, metadata in memory_entries:

        if (
            entry_id.startswith(reference_value)
            or entry_id[:20].startswith(reference_value)
        ):
            matching_entries.append(
                (entry_id, memory_text, metadata)
            )

    # --------------------------------------------------------
    # 4. NO MATCH FOUND
    # --------------------------------------------------------

    if not matching_entries:

        print(
            f"AI: No memory entry matches "
            f"reference '{reference_value}'."
        )

        return None

    # --------------------------------------------------------
    # 5. MULTIPLE MATCHES FOUND
    # --------------------------------------------------------
    # Prevent ambiguous deletion/update operations
    # --------------------------------------------------------

    if len(matching_entries) > 1:

        print(
            "AI: Multiple memory entries matched. "
            "Please use a more specific reference:"
        )

        for entry_id, memory_text, _ in matching_entries:

            preview_text = (
                memory_text[:60] + "..."
                if len(memory_text) > 60
                else memory_text
            )

            print(
                f"  {entry_id[:20]}... → {preview_text}"
            )

        return None

    # --------------------------------------------------------
    # 6. SUCCESSFUL MATCH RESOLUTION
    # --------------------------------------------------------

    return matching_entries[0]    


# ============================================================
# SEMANTIC MEMORY COORDINATOR — USAGE ROTATION PERSISTENCE
# ============================================================

def get_recent_semantic_conversation_candidates(user_id, *, limit=12):
    """Return a bounded recent-message pool for greeting semantic selection.

    This is not a transcript export: the query is owner scoped, capped, and
    consumed only by the coordinator's relevance/compression boundary.
    """

    if isinstance(user_id, bool) or not isinstance(user_id, int) or user_id < 1:
        raise ValueError("user_id must be a positive integer")
    if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
        raise ValueError("limit must be a positive integer")
    effective_limit = min(limit, 12)
    db_connection = get_db()
    cursor = db_connection.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT m.id AS message_id, m.role, m.content, m.created_at,
                   c.conversation_id, c.name AS conversation_name
            FROM messages m
            INNER JOIN conversations c ON c.id = m.conversation_id
            WHERE c.user_id = %s
              AND m.user_id = %s
              AND m.role IN ('user', 'assistant')
            ORDER BY m.created_at DESC, m.id DESC
            LIMIT %s
            """,
            (user_id, user_id, effective_limit),
        )
        return [dict(row, user_id=user_id) for row in cursor.fetchall()]
    finally:
        cursor.close()
        db_connection.close()


SEMANTIC_MEMORY_USAGE_SOURCES = {"chromadb", "conversation_history"}


def get_semantic_memory_usage(user_id, source, source_item_ids):
    """Return content-free selection usage for one owner and one source.

    Phase 5.1A does not call this from production chat or greeting retrieval.
    The owner and source constraints are deliberately mandatory so this helper
    cannot become an unscoped memory enumeration path.
    """

    if isinstance(user_id, bool) or not isinstance(user_id, int) or user_id < 1:
        raise ValueError("user_id must be a positive integer")
    if source not in SEMANTIC_MEMORY_USAGE_SOURCES:
        raise ValueError("unsupported semantic memory usage source")
    normalized_ids = tuple(dict.fromkeys(
        str(item_id).strip() for item_id in source_item_ids if str(item_id).strip()
    ))
    if not normalized_ids:
        return {}

    db_connection = get_db()
    cursor = db_connection.cursor(dictionary=True)
    placeholders = ", ".join(["%s"] * len(normalized_ids))
    try:
        cursor.execute(
            f"""
            SELECT source_item_id, memory_type, last_selected_at,
                   selection_count, rotation_cycle
            FROM semantic_memory_usage
            WHERE user_id = %s
              AND source = %s
              AND source_item_id IN ({placeholders})
            """,
            (user_id, source, *normalized_ids),
        )
        return {
            str(row["source_item_id"]): {
                **row,
                "last_selected_at": (
                    str(row["last_selected_at"])
                    if row.get("last_selected_at") is not None else None
                ),
            }
            for row in cursor.fetchall()
        }
    finally:
        cursor.close()
        db_connection.close()


def record_semantic_memory_usage(user_id, selections):
    """Atomically upsert content-free selection counters for one owner."""

    if isinstance(user_id, bool) or not isinstance(user_id, int) or user_id < 1:
        raise ValueError("user_id must be a positive integer")
    normalized = []
    for selection in selections:
        source = str(selection.get("source") or "").strip()
        source_item_id = str(selection.get("source_item_id") or "").strip()
        memory_type = str(selection.get("memory_type") or "unknown").strip()[:64]
        rotation_cycle = selection.get("rotation_cycle", 1)
        if source not in SEMANTIC_MEMORY_USAGE_SOURCES:
            raise ValueError("unsupported semantic memory usage source")
        if not source_item_id or len(source_item_id) > 191:
            raise ValueError("source_item_id must contain 1-191 characters")
        if (
            isinstance(rotation_cycle, bool)
            or not isinstance(rotation_cycle, int)
            or rotation_cycle < 1
        ):
            raise ValueError("rotation_cycle must be a positive integer")
        normalized.append((source, source_item_id, memory_type, rotation_cycle))
    if not normalized:
        return

    db_connection = get_db()
    cursor = db_connection.cursor()
    try:
        cursor.executemany(
            """
            INSERT INTO semantic_memory_usage (
                user_id, source, source_item_id, memory_type,
                last_selected_at, selection_count, rotation_cycle
            )
            VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP, 1, %s)
            ON DUPLICATE KEY UPDATE
                memory_type = VALUES(memory_type),
                last_selected_at = CURRENT_TIMESTAMP,
                selection_count = selection_count + 1,
                rotation_cycle = VALUES(rotation_cycle),
                updated_at = CURRENT_TIMESTAMP
            """,
            [(user_id, *selection) for selection in normalized],
        )
        db_connection.commit()
    except Exception:
        db_connection.rollback()
        raise
    finally:
        cursor.close()
        db_connection.close()
