"""
========================================================
AETHERAEON — SYSTEM PATH MANAGEMENT LAYER
========================================================

FILE PURPOSE:
This file is responsible for all path-related operations
across the AI system.

It ensures that file system access is safe, validated,
and consistent across all modules that interact with
local directories or external file paths.

========================================================
SYSTEM ROLE:
"Path Safety + Resolution Layer" of the architecture.

It does NOT execute system commands.
It does NOT perform AI reasoning.

It ONLY validates, normalizes, and resolves file paths.

========================================================
RESPONSIBILITIES:
(system_paths.py)

- Normalize and sanitize file paths
- Validate directory boundaries (security enforcement)
- Prevent directory traversal attacks
- Extract and parse system paths from commands
- Ensure safe access to allowed directories only
- Provide utility functions for file system operations

========================================================
STRICT BOUNDARIES (DO NOT BREAK):
(system_paths.py)

This file MUST NOT:
- Execute shell commands (tool_executor.py handles this)
- Perform AI reasoning (core_cognition.py handles this)
- Access or modify memory (memory_database.py handles this)
- Perform HTTP/API requests (external_toolkit.py handles this)
- Manage tool execution logic

It ONLY handles safe path logic.

========================================================
PATH SAFETY MODEL:
(system_paths.py)

All paths entering the system must be:

INPUT
  ↓
sanitize_file_path()
  ↓
_validate_format()
  ↓
_is_within_allowed_directories()
  ↓
return SAFE_PATH or None

========================================================
SYSTEM WIDE FLOW:

User Input / Tool Request
    ↓
request_router.py
    ↓
ai_orchestrator.py
    ↓
tool_executor.py
    ↓
system_paths.py   ← THIS FILE
    ↓
system_security.py (enforcement layer)
    ↓
filesystem access (SAFE ONLY)

========================================================
KEY FILE DEPENDENCIES:

system_paths.py is used by:
- tool_executor.py        (file operations)
- system_security.py      (validation enforcement)
- external_toolkit.py     (file-based tools)
- api_gateway.py          (path normalization for requests)

========================================================
OUTPUT CONTRACT:
(system_paths.py returns)

- sanitized_path (string or None)
- validation_result (bool)
- extracted_paths (list)

========================================================
DESIGN PHILOSOPHY:

"Never trust raw paths"

- System must assume ALL input paths are unsafe
- Only validated paths may reach execution layer
- Security is enforced BEFORE execution

========================================================
"""

# ============================================================
# SYSTEM PATH REGISTRY (AETHERAEON CORE INFRASTRUCTURE)
# ============================================================
# PURPOSE:
# Centralized definition of ALL system file paths,
# directories, and service endpoints.
#
# RULE:
# - ALL modules must import paths from here
# - NO hardcoded paths anywhere else in system
# - This is the SINGLE SOURCE OF TRUTH
# ============================================================

from pathlib import Path
import os


# ============================================================
# ROOT DIRECTORY (SYSTEM BASE)
# ============================================================
# This resolves the absolute project root dynamically
# regardless of where the file is executed from.
# ============================================================

AISYSTEM_ROOT = Path(__file__).resolve().parent.parent


# ============================================================
# CORE SYSTEM STRUCTURE
# ============================================================
# These define the main architecture folders
# ============================================================

CORE_PATH     = AISYSTEM_ROOT / "core"
WEBUI_PATH    = AISYSTEM_ROOT / "WebUI"
DATA_PATH     = AISYSTEM_ROOT / "Data"
SERVICES_PATH = AISYSTEM_ROOT / "Services"


# ============================================================
# DATA LAYER PATHS
# ============================================================
# All persistent system data lives here
# ============================================================

MEMORY_PATH   = DATA_PATH / "Memory"
LOGS_PATH     = DATA_PATH / "Logs"
BACKUPS_PATH  = DATA_PATH / "Backups"
TEMP_PATH     = DATA_PATH / "Temp"


# ============================================================
# MEMORY SYSTEM FILES (LEGACY + MIGRATED SUPPORT)
# ============================================================
# NOTE:
# These are transitional constants for backward compatibility
# while system migrates fully to structured Data/Memory layer.
# ============================================================

SETTINGS_FILE          = MEMORY_PATH / "settings.json"
PERSONALITY_FILE       = MEMORY_PATH / "personality.json"
PLAYBOOK_DIR           = AISYSTEM_ROOT / "playbooks"


# ============================================================
# SERVICES LAYER
# ============================================================
# External system integrations and local services
# ============================================================

N8N_PATH = None  # no filesystem dependency
OLLAMA_PATH  = SERVICES_PATH / "Ollama"


# ============================================================
# SERVICE ENDPOINTS (NETWORK CONFIGURATION)
# ============================================================
# These are runtime service URLs used by the system
# ============================================================

N8N_URL = os.getenv("N8N_URL", "http://localhost:5678")
OLLAMA_URL = "http://localhost:11434/api/generate"


# ============================================================
# EXPORT CONTRACT (OPTIONAL FUTURE USE)
# ============================================================
# Centralized export list for system introspection tools
# ============================================================

__all__ = [
    "AISYSTEM_ROOT",
    "CORE_PATH",
    "WEBUI_PATH",
    "DATA_PATH",
    "SERVICES_PATH",
    "MEMORY_PATH",
    "LOGS_PATH",
    "BACKUPS_PATH",
    "TEMP_PATH",
    "SETTINGS_FILE",
    "PERSONALITY_FILE",
    "PLAYBOOK_DIR",
    "N8N_PATH",
    "OLLAMA_PATH",
    "N8N_URL",
    "OLLAMA_URL",
]
