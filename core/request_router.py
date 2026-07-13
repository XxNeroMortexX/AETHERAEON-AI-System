"""
========================================================
AETHERAEON — REQUEST ROUTER (SYSTEM ROUTING LAYER)
========================================================

FILE PURPOSE:
This file is the central routing and decision gateway
of the AI system.

It determines where requests should go and what
subsystems should handle them.

========================================================
SYSTEM ROLE:
"Traffic Control Layer"

This file does NOT perform deep reasoning.
This file does NOT execute tools directly.

It ONLY:
- Routes requests
- Selects execution paths
- Coordinates system layers
- Enforces architecture boundaries

========================================================
RESPONSIBILITIES:
(request_router.py)

- Receive normalized user requests
- Detect request category / route type
- Decide whether AI reasoning is needed
- Decide whether tool execution is needed
- Route memory commands correctly
- Route system commands correctly
- Route web/tool requests correctly
- Build execution pipeline order
- Return structured execution results

========================================================
STRICT BOUNDARIES (DO NOT BREAK):
(request_router.py)

This file MUST NOT:

- Perform heavy AI reasoning
  (ai_orchestrator.py handles this)

- Execute tools directly
  (tool_executor.py handles this)

- Access databases directly
  (memory_database.py handles this)

- Handle HTTP/API requests directly
  (api_gateway.py handles this)

- Modify frontend/UI state

This file ONLY routes and coordinates execution flow.

========================================================
REQUEST_ROUTER INTERNAL FLOW:
(request_router.py functions)

Incoming Request
    ↓
normalize_request()
    ↓
classify_route()
    ↓
determine_execution_path()
    ↓
route_to_handler()
    ↓
AI Route?
    ├─→ ai_orchestrator.py
    │
    ├─→ tool_executor.py
    │
    ├─→ memory_interface.py
    │
    └─→ system command handlers
    ↓
collect structured result
    ↓
return response object to api_gateway.py

========================================================
SYSTEM WIDE FLOW:
(full system architecture)

User Input (Web UI / API)
    ↓
api_gateway.py
    ↓
request_router.py   ← THIS FILE
    ↓
ai_orchestrator.py
    ↓
tool_executor.py (if tool required)
    ↓
external_toolkit.py
    ↓
memory_database.py
    ↓
model_registry.py
    ↓
api_gateway.py
    ↓
Web UI (index.html)

========================================================
KEY FILE DEPENDENCIES:

request_router.py depends on:
- ai_orchestrator.py
- tool_executor.py
- memory_interface.py
- model_registry.py
- personality_engine.py
- help_system.py

========================================================
CORE FUNCTIONS (THIS FILE):

- normalize_request()
- classify_route()
- determine_execution_path()
- route_to_handler()
- build_execution_context()
- process_request()

========================================================
OUTPUT CONTRACT:
(request_router.py returns)

- success (bool)
- response (string or structured object)
- optional tool_request
- optional metadata
- optional error

========================================================
DESIGN PHILOSOPHY:

"Centralized Routing, Decentralized Execution"

- Router DIRECTS
- Orchestrator THINKS
- tool_executor ACTS
- Database STORES
- API Gateway TRANSPORTS
- UI DISPLAYS

========================================================
"""


# ============================================================
# CORE STANDARD LIBRARY IMPORTS
# ============================================================
# Built-in Python modules used for parsing, routing logic,
# pattern matching, system control, and input normalization.
# ============================================================

import re          # Regex engine for intent detection + pattern matching
import os          # Environment / system access (light usage if needed)
import json        # Structured parsing for routing decisions (future expansion)


# ============================================================
# EXTERNAL DEPENDENCIES (PIP INSTALLED PACKAGES)
# ============================================================
# Third-party libraries installed via pip.
# Used for optional system integrations and API communication.
# ============================================================

import requests    # HTTP calls (only if router triggers external services)


# ============================================================
# INTERNAL SYSTEM IMPORTS (ARCHITECTURE LAYERS)
# ============================================================
# Core AI system modules (ALL located inside Core folder)
#
# RULES:
# - request_router = decision + routing layer ONLY
# - NO AI reasoning
# - NO tool execution
# - NO database access
# ============================================================

# ------------------------------------------------------------
# LLM / AI INTERFACE LAYER
# (Only referenced for metadata awareness or routing hints)
# ------------------------------------------------------------
from core import llm_interface


# ------------------------------------------------------------
# CONFIGURATION LAYER
# (System settings, runtime configuration access)
# ------------------------------------------------------------
from core import config_loader
from core import config_manager


# ------------------------------------------------------------
# TOOL SYSTEM LAYER
# (Tool registry + execution dispatcher reference)
# ------------------------------------------------------------
from core.tool_registry import get_tools
from core import tool_executor


# ------------------------------------------------------------
# MEMORY SYSTEM LAYER
# (Used ONLY for routing classification, not execution)
# ------------------------------------------------------------
from core import memory_interface
from core import memory_database


# ------------------------------------------------------------
# IDENTITY / PERSONALITY LAYER
# (Used for routing personality-related commands)
# ------------------------------------------------------------
from core import agent_identity
from core import personality_engine


# ------------------------------------------------------------
# HELP SYSTEM
# (Used for dynamic help command routing)
# ------------------------------------------------------------
from core.help_system import build_help


# ------------------------------------------------------------
# SYSTEM UTILITIES
# (Input cleaning, timestamps, helpers if needed)
# ------------------------------------------------------------
from core import system_utils


# ============================================================
# MEMORY SAVE INTENT PATTERNS
# ============================================================

MEMORY_SAVE_PATTERNS = [
    r"^remember\s+.+=.+",
    r"^save\s+this[:\s]",
    r"^store[:\s]",
    r"^don'?t\s+forget[:\s]",
    r"^make\s+a\s+note[:\s]",
    r"^note\s+that[:\s]",
    r"^keep\s+in\s+mind[:\s]",
    r"^log\s+this[:\s]",
]


# ============================================================
# MEMORY SEARCH INTENT PATTERNS
# ============================================================

MEMORY_SEARCH_PATTERNS = [
    r"^recall\s+",
    r"^look\s+up\s+in\s+memory",
    r"^search\s+memory\s+for",
    r"^remind\s+me\s+of",
]


# ============================================================
# MEMORY DELETE INTENT PATTERNS
# ============================================================

MEMORY_DELETE_PATTERNS = [
    r"^forget\s+(that|about|memory|this)",
    r"^remove\s+from\s+memory",
    r"^delete\s+from\s+memory",
    r"^erase\s+(that|from\s+memory)",
    r"^clear\s+that\s+(memory|from)",
]

# ============================================================
# REQUEST CLASSIFICATION
# Detects the type of user request for early system routing.
# ============================================================

def classify_request(user_input: str) -> tuple[str, str]:

    # --------------------------------------------------------
    # INPUT NORMALIZATION
    # Convert input into lowercase safe text for matching.
    # --------------------------------------------------------

    normalized_input = (user_input or "").strip().lower()

    # --------------------------------------------------------
    # EXPLICIT AIDER REQUEST
    # Highest-priority direct coding route.
    # --------------------------------------------------------

    if normalized_input.startswith("aider "):

        return (
            "code",
            "explicit aider request"
        )

    # --------------------------------------------------------
    # CODE / DEVELOPMENT REQUEST DETECTION
    # --------------------------------------------------------

    code_keywords = (

        # ====================================================
        # GENERAL DEBUGGING / DEVELOPMENT
        # ====================================================

        "traceback",
        "stack trace",
        "exception",
        "debug",
        "debugging",
        "error:",
        "bug",
        "fix bug",
        "refactor",
        "optimize",
        "rewrite",
        "generate",
        "example",
        "snippet",
        "compile",
        "build",
        "syntax",
        "parser",
        "framework",
        "library",
        "api",

        # ====================================================
        # GENERAL PROGRAMMING TERMS
        # ====================================================

        "code",
        "coding",
        "program",
        "script",
        "function",
        "class",
        "method",
        "object",
        "algorithm",
        "logic",
        "source code",

        # ====================================================
        # LANGUAGES
        # ====================================================

        "python",
        "py",

        "c++",
        "cpp",
        "c#",
        "csharp",
        "c language",

        "javascript",
        "typescript",
        "nodejs",
        "node.js",

        "php",
        "java",
        "powershell",
        "batch",
        "cmd",

        "html",
        "css",
        "xml",
        "json",
        "yaml",
        "toml",

        "sql",
        "mysql",
        "mariadb",
        "sqlite",

        "lua",
        "mq2",

        # ====================================================
        # WEB DEVELOPMENT
        # ====================================================

        "website",
        "web app",
        "frontend",
        "backend",
        "fullstack",
        "full stack",
        "responsive design",
        "bootstrap",
        "tailwind",
        "react",
        "vue",
        "flask",
        "fastapi",

        # ====================================================
        # PACKAGE / DEVELOPMENT TOOLING
        # ====================================================

        "pip ",
        "npm ",
        "composer",
        "docker",
        "git",
        "github",

        # ====================================================
        # REVERSE ENGINEERING / DISASSEMBLY
        # ====================================================

        "disassembly",
        "reverse engineer",
        "reverse engineering",
        "hex editing",
        "memory editing",
        "opcode",
        "assembly",
        "asm",

        "x64dbg",
        "x32dbg",
        "ollydbg",
        "ida",
        "ghidra",

        "hex editor",
        ".alf",

        # ====================================================
        # FILE EXTENSIONS
        # ====================================================

        # Python
        ".py",

        # C / C++
        ".cpp",
        ".cxx",
        ".cc",
        ".c",
        ".hpp",
        ".h",

        # Web
        ".html",
        ".htm",
        ".css",
        ".js",
        ".ts",
        ".jsx",
        ".tsx",
        ".php",

        # Java
        ".java",

        # Batch / PowerShell
        ".bat",
        ".cmd",
        ".ps1",

        # Data / Config
        ".json",
        ".xml",
        ".yaml",
        ".yml",
        ".toml",

        # Database
        ".sql",

        # MQ2 / Lua
        ".lua",
        ".mac",
        ".inc",

        # Reverse engineering
        ".alf"
    )

    if any(keyword in normalized_input for keyword in code_keywords):

        return (
            "code",
            "code/development keywords"
        )

    # --------------------------------------------------------
    # SYSTEM / SHELL COMMAND DETECTION
    # --------------------------------------------------------

    shell_keywords = (

        "dir ",
        "tree ",
        "where ",
        "systeminfo",
        "ipconfig",
        "ping ",
        "tracert",
        "nslookup",
        "netstat",
        "arp ",
        "tasklist",
        "wmic",
        "driverquery",
        "hostname",
        "whoami",
        "ver",
        "date",
        "time "
    )

    if any(keyword in normalized_input for keyword in shell_keywords):

        return (
            "shell",
            "system command keywords"
        )

    # --------------------------------------------------------
    # DEFAULT CHAT ROUTE
    # --------------------------------------------------------

    return (
        "chat",
        "general conversation"
    )


# ============================================================
# FAST PATH INTENT ROUTER
# Detects direct commands before AI reasoning is used.
# ============================================================

def fast_path_intent(user_input: str):

    # --------------------------------------------------------
    # INPUT NORMALIZATION
    # Convert incoming text into normalized comparison format.
    # --------------------------------------------------------

    normalized_input = (user_input or "").lower().strip()

    # --------------------------------------------------------
    # CORE SYSTEM COMMANDS
    # Immediate local commands that bypass AI reasoning.
    # --------------------------------------------------------

    if normalized_input in (
        "help",
        "commands",
        "?",
        "what can you do"
    ):

        return "help"

    if normalized_input in (
        "status",
        "system status",
        "check status"
    ):

        return "status"

    if normalized_input in (
        "cls",
        "clear",
        "clear chat",
        "clear screen"
    ):

        return "clear_ui"

    if normalized_input.startswith("memory recall "):

        return "memory_recall"

    if normalized_input == "what have i been working on":

        return "memory_search"

    # --------------------------------------------------------
    # PERSONALITY SYSTEM COMMANDS
    # Commands related to AI behavior and personality settings.
    # --------------------------------------------------------

    personality_commands = (

        "set tone",
        "set name",
        "set verbosity",
        "add trait",
        "remove trait",
        "show personality"
    )

    if any(
        normalized_input.startswith(command)
        for command in personality_commands
    ):

        return "personality"

    # --------------------------------------------------------
    # EXPLICIT MEMORY COMMANDS
    # Structured CRUD operations for memory management.
    # --------------------------------------------------------

    if re.match(
        r"^memory\s+(list|view|search|add|delete|edit|clear|types?)",
        normalized_input
    ):

        return "memory_cmd"

    # --------------------------------------------------------
    # NATURAL LANGUAGE MEMORY SAVE
    # Human-style memory save requests.
    # --------------------------------------------------------

    if any(
        re.match(pattern, normalized_input)
        for pattern in MEMORY_SAVE_PATTERNS
    ):

        return "save_memory"

    # --------------------------------------------------------
    # NATURAL LANGUAGE MEMORY SEARCH
    # Human-style memory recall requests.
    # --------------------------------------------------------

    if any(
        re.match(pattern, normalized_input)
        for pattern in MEMORY_SEARCH_PATTERNS
    ):

        return "memory_search"

    # --------------------------------------------------------
    # NATURAL LANGUAGE MEMORY DELETE
    # Human-style memory removal requests.
    # --------------------------------------------------------

    if any(
        re.match(pattern, normalized_input)
        for pattern in MEMORY_DELETE_PATTERNS
    ):

        return "memory_forget"

    # --------------------------------------------------------
    # PLAYBOOK COMMANDS
    # Automation workflow execution commands.
    # --------------------------------------------------------

    if (
        normalized_input.startswith("run playbook")
        or
        normalized_input.startswith("list playbook")
    ):

        return "playbook"

    # --------------------------------------------------------
    # AIDER PROJECT COMMANDS
    # Sets active coding workspace/project.
    # --------------------------------------------------------

    if re.match(
        r"^aider\s+project\s+",
        normalized_input
    ):

        return "aider_project"

    # --------------------------------------------------------
    # MODEL MANAGEMENT COMMANDS
    # LLM routing and model configuration controls.
    # --------------------------------------------------------

    if (
        normalized_input.startswith("model")
        or
        normalized_input.startswith("models")
    ):

        return "model_cmd"

    # --------------------------------------------------------
    # WEB SEARCH COMMANDS
    # Enables/disables web search or performs web lookup.
    # --------------------------------------------------------

    if (
        normalized_input in ("web on", "web off")
        or
        normalized_input.startswith("web search ")
    ):

        return "web_cmd"

    # --------------------------------------------------------
    # SAFE SHELL COMMANDS
    # Uses the executor's existing allowlist as the sole source.
    # Final permission enforcement remains in system_security.
    # --------------------------------------------------------

    if tool_executor.is_supported_shell_command(normalized_input):
        print(
            "[REQUEST ROUTER] detected command:",
            repr(user_input),
        )
        print("[REQUEST ROUTER] selected tool: shell")
        return "shell"

    # --------------------------------------------------------
    # NO FAST-PATH MATCH
    # Request should continue into AI orchestration layer.
    # --------------------------------------------------------

    return None
    

# ============================================================
# MEMORY DOMAIN CLASSIFIER
# LEFT BRAIN MEMORY ROUTING LAYER
# ============================================================

def classify_memory_domain(user_input: str) -> str:

    """
    LEFT BRAIN MEMORY ROUTING LAYER

    This function determines WHICH memory domain is most
    relevant to the current user request.

    It DOES NOT retrieve memory.
    It ONLY classifies the memory category.

    Used as an early cognition-routing layer before
    memory recall and semantic processing.
    """

    # --------------------------------------------------------
    # INPUT NORMALIZATION
    # Convert input into safe lowercase comparison text.
    # --------------------------------------------------------

    normalized_input = (user_input or "").lower()

    # --------------------------------------------------------
    # IDENTITY / PERSONAL PROFILE MEMORY
    # User facts, identity, self-description, and personal data.
    # --------------------------------------------------------

    identity_keywords = (
        "name",
        "who am i",
        "about me",
        "myself",
        "my personality",
        "who i am",
        "personal info",
        "profile"
    )

    if any(
        keyword in normalized_input
        for keyword in identity_keywords
    ):
        return "identity"

    # --------------------------------------------------------
    # SPIRITUAL / EXPERIENCE MEMORY
    # Dreams, meditation, energy states, and spiritual events.
    # --------------------------------------------------------

    spiritual_keywords = (
        "meditation",
        "spiritual",
        "energy",
        "vibration",
        "dream",
        "lucid",
        "astral",
        "obe",
        "chakra",
        "frequency",
        "entity",
        "spirit",
        "awakening",
        "presence",
        "vision"
    )

    if any(
        keyword in normalized_input
        for keyword in spiritual_keywords
    ):
        return "spiritual"

    # --------------------------------------------------------
    # AI PROJECT / SYSTEM MEMORY
    # Architecture, coding, AI system, and development context.
    # --------------------------------------------------------

    project_keywords = (
        "ai",
        "system",
        "project",
        "architecture",
        "building",
        "framework",
        "tool",
        "agent",
        "memory system",
        "database",
        "orchestrator",
        "python",
        "code",
        "programming",
        "development"
    )

    if any(
        keyword in normalized_input
        for keyword in project_keywords
    ):
        return "project"

    # --------------------------------------------------------
    # DEFAULT MEMORY DOMAIN
    # Fallback when no specific category is detected.
    # --------------------------------------------------------

    return "general"

    

# ============================================================
# INPUT CLEANING LAYER
# RAW USER INPUT SANITIZATION PIPELINE
# ============================================================

def clean_input(text):

    """
    INPUT SANITIZATION PIPELINE

    This function is the FIRST processing layer for all user input.

    It ensures all incoming data is:
    - safe for AI processing
    - normalized for memory storage
    - consistent for routing + intent detection

    Supports:
    - CLI input
    - API / Flask input
    - socket / byte streams
    """

    # --------------------------------------------------------
    # STEP 1: HANDLE RAW BYTES INPUT
    # --------------------------------------------------------
    # Some API layers may pass bytes instead of strings.
    # This prevents corrupted memory entries like b'hello'.
    # --------------------------------------------------------

    if isinstance(text, bytes):
        text = text.decode("utf-8", errors="ignore")

    # --------------------------------------------------------
    # STEP 2: FORCE STRING TYPE SAFETY
    # --------------------------------------------------------
    # Ensures downstream systems never receive invalid types.
    # Memory, embeddings, and LLM prompts require strict strings.
    # --------------------------------------------------------

    text = str(text).strip()

    # --------------------------------------------------------
    # STEP 3: DETECT FULL-STRING DUPLICATION
    # --------------------------------------------------------
    # Fixes accidental echo duplication:
    # Example: "hellohello"
    # or UI repeat injection bugs.
    # --------------------------------------------------------

    if len(text) > 10:

        midpoint = len(text) // 2

        if text[:midpoint] == text[midpoint:]:

            text = text[:midpoint]

    # --------------------------------------------------------
    # STEP 4: DETECT WORD-LEVEL DUPLICATION
    # --------------------------------------------------------
    # Fixes repeated sentence loops:
    # Example: "what is my name what is my name"
    # --------------------------------------------------------

    words = text.split()

    if len(words) > 6:

        midpoint = len(words) // 2

        if words[:midpoint] == words[midpoint:]:

            text = " ".join(words[:midpoint])

    # --------------------------------------------------------
    # FINAL OUTPUT CONTRACT
    # --------------------------------------------------------
    # Output is guaranteed:
    # - string
    # - trimmed
    # - de-duplicated (basic corruption handling)
    # - safe for routing, memory, and AI processing
    # --------------------------------------------------------

    return text
