"""
Aetheraeon AI - System Paths

Purpose:
Provides centralized project paths, path normalization, and reusable filesystem-boundary checks.

Architecture Layer:
Configuration and Utility Layers - filesystem support.

Responsibilities:
- Resolve established project and runtime locations consistently.
- Normalize and validate path values for calling modules.
- Support security and execution components with path-boundary information.

Boundaries:
- Path checks support security enforcement but do not authorize an operation.
- This module does not execute commands, perform cognitive processing, access memory, or establish tool policy.
- Security components remain authoritative before filesystem actions execute.
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
