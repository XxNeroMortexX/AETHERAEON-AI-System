"""
========================================================
AETHERAEON — PERSISTENCE DATABASE LAYER
========================================================

FILE PURPOSE:

This file currently provides the central persistence
implementation layer for the Aetheraeon AI system.

It manages storage and retrieval operations for:

- User identity data
- Conversations
- Messages
- User settings
- Automation playbooks
- Long-term semantic memory (ChromaDB)

This file acts as the current backend storage provider
until the persistence layer is separated into dedicated
repository components.

========================================================
SYSTEM ROLE:

"Persistence Layer"

Current Responsibility:

This file provides:
- Database communication
- Storage operations
- Retrieval operations
- Data persistence
- ChromaDB semantic memory access


IMPORTANT ARCHITECTURE NOTE:

This file is intentionally planned for future
decomposition.

As the system matures, responsibilities should be
migrated into dedicated repository modules.

========================================================
TARGET FUTURE ARCHITECTURE:

database/
│
├── database_connection.py
│       MariaDB connection management
│
├── user_repository.py
│       User identity and account data
│
├── conversation_repository.py
│       Conversations and message history
│
├── settings_repository.py
│       User configuration storage
│
├── playbook_repository.py
│       Automation workflow storage
│
└── memory_repository.py
        ChromaDB semantic memory


Future access pattern:

memory_interface.py

        |
        |
        ├── memory_repository.py
        |
        ├── conversation_repository.py
        |
        └── other persistence repositories


The goal is to prevent higher-level AI components
from directly depending on database implementations.

========================================================
CURRENT RESPONSIBILITIES:

(memory_database.py)

- Manage MariaDB operations
- Manage ChromaDB operations
- Store structured records
- Retrieve persistent data
- Update stored information
- Delete persistent records
- Provide normalized storage results

========================================================
STRICT BOUNDARIES:

This file MUST NOT:

- Perform AI reasoning
- Generate AI responses
- Execute tools
- Handle HTTP requests
- Control frontend behavior
- Make intelligence decisions
- Perform business logic unrelated to storage

This layer only manages persistence.

========================================================
ARCHITECTURAL DIRECTION:

Current:

AI Layers
    ↓
memory_interface.py
    ↓
memory_database.py
    ↓
MariaDB / ChromaDB


Future:

AI Layers
    ↓
memory_interface.py
    ↓
Repository Layer
    ↓
Database / Vector Storage


========================================================
DESIGN PHILOSOPHY:

"Storage Should Be Predictable"

Persistence stores state.
Persistence does not create intelligence.

The database remembers.
The cognitive system understands.

========================================================
"""


# ============================================================
# CORE STANDARD LIBRARY IMPORTS
# ============================================================
# Built-in Python modules used for:
# - ID generation
# - text processing
# - pattern matching
# ============================================================

import uuid   # Unique identifiers for memory entries (ChromaDB + SQL IDs)
import re     # Text chunking, filtering, and pattern cleanup


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

    global CHROMA_COLLECTION

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
        return

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
        return

    if "AI explained" in text or "Tool usage rules" in text:
        return

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

    if meta:
        sanitized_meta = {}

        for key, value in meta.items():

            if isinstance(value, bytes):
                value = value.decode("utf-8", errors="ignore")

            sanitized_meta[key] = str(value)

        base_metadata.update(sanitized_meta)

    # ─────────────────────────────────────────────
    # 6. PERSISTENCE LAYER — CHROMADB INSERTION
    # ─────────────────────────────────────────────

    collection = get_chroma_collection()
    if collection is None:
        return

    for memory_text in memory_chunks:

        memory_type = classify_memory_type(memory_text)

        final_metadata = dict(base_metadata)
        final_metadata["type"] = memory_type

        collection.add(
            documents=[memory_text],
            metadatas=[final_metadata],
            ids=[str(uuid.uuid4())]
        )
        
        
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

def chroma_recall_with_meta(query, n=5):
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
            n_results=n,
            include=["documents", "metadatas", "distances"]
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

        return results

    except Exception:
        # ─────────────────────────────────────────────
        # 5. FAILSAFE ERROR HANDLING
        # ─────────────────────────────────────────────
        return []
        
        

# ============================================================
# CHROMADB — MEMORY FILTERING BY TYPE
# ============================================================

def chroma_get_by_type(mtype, limit=50):
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
        search_results = collection.get(
            where={"type": mtype},
            limit=limit
        )

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

def chroma_get_all(limit=200):
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
        return []

    # ─────────────────────────────────────────────
    # 3. RAW DATA RETRIEVAL
    # ─────────────────────────────────────────────

    try:
        search_results = collection.get(limit=limit)

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
        return results

    except Exception:
        # ─────────────────────────────────────────────
        # 5. FAILSAFE ERROR HANDLING
        # ─────────────────────────────────────────────
        return []
        
        
# ============================================================
# CHROMADB — DELETE MEMORY ENTRY (BY ID)
# ============================================================

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
        collection.delete(ids=[memory_id])
        return True

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
        collection.update(
            ids=[memory_id],
            documents=[new_text],
            metadatas=[base_metadata]
        )
        return True

    except Exception:
        # ─────────────────────────────────────────────
        # 6. FAILSAFE ERROR HANDLING
        # ─────────────────────────────────────────────
        return False
        
        
# ============================================================
# CHROMADB — SIMILAR MEMORY DETECTION (DEDUPLICATION)
# ============================================================

def chroma_exists_similar(text, threshold=0.95):
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
        search_results = collection.query(
            query_texts=[text],
            n_results=3
        )

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
    - Handles system bootstrap (first user becomes admin)

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

        cursor.execute(
            """
            INSERT INTO users
                (username, email, full_name, password_hash, role, is_active, avatar)
            VALUES (%s, %s, %s, %s, 'user', 1, %s)
            """,
            (
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
        # promote them to ADMIN automatically.
        # ─────────────────────────────────────────

        if new_user_id == 1:
            cursor.execute(
                "UPDATE users SET role = 'admin' WHERE id = %s",
                (new_user_id,)
            )
            db_connection.commit()

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
                ON c.conversation_id = m.conversation_id
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
        )

        for statement in schema_updates:
            cursor.execute(statement)

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_personality_traits (
                id INT NOT NULL AUTO_INCREMENT,
                user_id INT NOT NULL,
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
                greeting_style
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
                greeting_style       = VALUES(greeting_style)
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
                greeting_style
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

def get_user_personality_traits(user_id: int) -> list[dict]:
    """Return only the authenticated user's ordered personality traits."""
    db_connection = get_db()
    cursor = db_connection.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id, trait, created_at
            FROM user_personality_traits
            WHERE user_id = %s
            ORDER BY created_at, id
            """,
            (user_id,)
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        db_connection.close()


def add_user_personality_trait(user_id: int, trait: str) -> dict | None:
    """Add a unique trait for one user and return its stored record."""
    db_connection = get_db()
    cursor = db_connection.cursor(dictionary=True)
    try:
        cursor.execute(
            "INSERT IGNORE INTO user_personality_traits (user_id, trait) VALUES (%s, %s)",
            (user_id, trait)
        )
        db_connection.commit()
        cursor.execute(
            """
            SELECT id, trait, created_at
            FROM user_personality_traits
            WHERE user_id = %s AND trait = %s
            """,
            (user_id, trait)
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        db_connection.close()


def delete_user_personality_trait(
    user_id: int,
    trait_id: int = None,
    trait: str = None
) -> bool:
    """Remove a trait scoped by user_id and either id or trait text."""
    db_connection = get_db()
    cursor = db_connection.cursor()
    try:
        if trait_id is not None:
            cursor.execute(
                "DELETE FROM user_personality_traits WHERE id = %s AND user_id = %s",
                (trait_id, user_id)
            )
        elif trait is not None:
            cursor.execute(
                "DELETE FROM user_personality_traits WHERE user_id = %s AND trait = %s",
                (user_id, trait)
            )
        else:
            return False
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
    tool_used: str = None
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
        tool_used
    )
    
# ============================================================
# MESSAGE SYSTEM — GET MESSAGES (CONVERSATION READ ENGINE)
# ============================================================

def get_messages(conv_uuid: str) -> list[dict]:
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

        cursor.execute(
            """
            SELECT
                role,
                content,
                tool_used,
                created_at
            FROM messages
            WHERE conversation_id = %s
            ORDER BY created_at ASC, id ASC
            """,
            (internal_conversation_id,)
        )

        message_rows = cursor.fetchall()

        # ─────────────────────────────────────────
        # 4. TIMESTAMP SERIALIZATION FOR FRONTEND
        # ─────────────────────────────────────────
        # Converts datetime objects → string format
        # Ensures JSON compatibility for Flask API
        # ─────────────────────────────────────────

        for message in message_rows:

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
