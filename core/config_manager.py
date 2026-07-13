"""
# ============================================================
# AETHERAEON — CONFIGURATION MANAGEMENT SYSTEM
# ============================================================
#
# FILE PURPOSE:
# This file manages all system configuration state,
# including runtime settings, persistent config values,
# and environment-driven behavior changes.
#
# ============================================================
# SYSTEM ROLE:
# "Configuration Control Layer" of the architecture.
#
# This file acts as the single source of truth for:
# - system-wide settings
# - runtime feature toggles
# - persistent configuration state
#
# ============================================================
# RESPONSIBILITIES:
# (config_manager.py)
#
# - Load configuration from disk / environment
# - Save updated configuration safely
# - Provide structured access to config values
# - Merge defaults with user overrides
# - Validate configuration integrity
# - Support live updates without restart (where possible)
#
# ============================================================
# STRICT BOUNDARIES (DO NOT BREAK):
# (config_manager.py)
#
# This file MUST NOT:
# - Execute AI reasoning (ai_orchestrator.py handles that)
# - Run external tools or commands (tool_executor.py handles that)
# - Directly modify memory database (memory_database.py handles that)
# - Perform system execution logic outside config scope
#
# It ONLY manages configuration state and validation.
#
# ============================================================
# SYSTEM CONFIGURATION FLOW:
# (config_manager.py lifecycle)
#
# Load Default Config
#     ↓
# Merge Environment Variables
#     ↓
# Apply User Overrides
#     ↓
# Validate Schema
#     ↓
# Provide Config to System Modules
#     ↓
# Save Updates (if changed)
#
# ============================================================
# KEY DEPENDENCIES:
#
# config_manager.py interacts with:
# - system_paths.py (config file locations)
# - json_helpers.py (safe serialization)
# - system_utils.py (validation utilities)
#
# ============================================================
# DESIGN PHILOSOPHY:
#
# "Configuration is Control — Not Logic"
#
# - Config defines behavior
# - It does NOT execute behavior
# - It does NOT reason
# - It only describes system state
#
# ============================================================
"""

# ============================================================
# CORE STANDARD LIBRARY IMPORTS
# ============================================================
# These are built-in Python modules used for configuration,
# file handling, parsing, and system-level operations.
# ============================================================

import json          # JSON parsing for settings + structured config storage
import os            # File system access for config persistence
import re            # Pattern cleanup for model name normalization


# ============================================================
# EXTERNAL DEPENDENCIES (PIP INSTALLED PACKAGES)
# ============================================================
# Third-party libraries installed via pip.
# ============================================================

import requests      # HTTP requests (used for model/service validation if needed)


# ============================================================
# INTERNAL SYSTEM IMPORTS (ARCHITECTURE LAYERS)
# ============================================================
# This section defines ALL internal AI system dependencies.
#
# RULES:
# - These imports are part of the core AI configuration layer
# - DO NOT execute logic here
# - DO NOT mix external libraries here
# - ONLY import system modules or configuration helpers
#
# The configuration system is responsible for:
# 1. System settings loading and persistence
# 2. Model configuration management
# 3. Runtime feature toggles
# 4. Environment-driven overrides
# ============================================================

# ------------------------------------------------------------
# CONFIGURATION LAYER (CORE SETTINGS ENGINE)
# ------------------------------------------------------------
from core.system_paths import SETTINGS_FILE  # Centralized path management for config files


# ============================================================
# CONFIGURATION VERSIONING
# ============================================================
# Used to track schema evolution of config file.
# ============================================================

VERSION = "4.3"


# ============================================================
# EXTERNAL SERVICE ENDPOINTS
# ============================================================
# Centralized API endpoints used by the system.
# ============================================================

OLLAMA_URL = "http://localhost:11434/api/generate"


# ============================================================
# DEFAULT SYSTEM CONFIGURATION
# ============================================================
# This defines the base configuration for the entire AI system.
#
# NOTES:
# - This is the fallback config if no file exists
# - User settings override these values at runtime
# - Models are routed through model_registry.py logic
# ============================================================

DEFAULT_SETTINGS = {
    "models": {
        # Core model roles used across AI system routing
        "router": "qwen2.5-coder:14b",
        "chat": "gpt-oss:20b",
        "code": "qwen2.5-coder:32b",
    },

    "auto_model": True,          # Auto-select best model per task
    "show_process": True,        # Debug visibility toggle
    "ollama_timeout_s": 180,     # Timeout for local model calls

    # --------------------------------------------------------
    # WEB SEARCH CONFIGURATION
    # --------------------------------------------------------
    "web_search": {
        "enabled": False,

        # Provider selection:
        # - google_cse → Google Custom Search API
        # - ddg → DuckDuckGo fallback (no API key required)
        "provider": "google_cse",

        # Secure key handling:
        # Prefer environment variables instead of file storage
        "google_cse_api_key": "",
        "google_cse_cx": "",

        "max_results": 5,
    },
}


# ============================================================
# INTERNAL STATE CACHE
# ============================================================
# Holds in-memory config to avoid repeated disk I/O.
# ============================================================

_SETTINGS_CACHE = None


# ============================================================
# SYSTEM SETTINGS LOADER
# ============================================================
# PURPOSE:
# Loads system configuration from disk with caching support,
# and safely merges user settings with default configuration.
#
# This ensures:
# - fast repeated access (in-memory cache)
# - safe fallback defaults
# - partial user config overrides
# - schema stability across updates
# ============================================================


def load_settings() -> dict:
    """
    Load and return system configuration settings.

    This function is the single entry point for retrieving
    runtime configuration for the entire AI system.

    ------------------------------------------------------------
    BEHAVIOR FLOW:
    ------------------------------------------------------------
    1. Check in-memory cache (_SETTINGS_CACHE)
    2. Load settings file from disk if needed
    3. Fallback to empty config if missing/corrupt
    4. Deep-merge with DEFAULT_SETTINGS
    5. Merge nested model configuration safely
    6. Cache final result for performance
    ------------------------------------------------------------
    """

    global _SETTINGS_CACHE

    # ─────────────────────────────────────────────────────────
    # 1. CACHE CHECK (FAST PATH)
    # ─────────────────────────────────────────────────────────
    # If settings are already loaded, return immediately
    # ─────────────────────────────────────────────────────────

    if _SETTINGS_CACHE is not None:
        return _SETTINGS_CACHE

    # ─────────────────────────────────────────────────────────
    # 2. SAFE FILE SYSTEM LOADING
    # ─────────────────────────────────────────────────────────
    # Ensures settings file path exists and is readable
    # ─────────────────────────────────────────────────────────

    try:
        settings_directory = os.path.dirname(SETTINGS_FILE)
        os.makedirs(settings_directory, exist_ok=True)

        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r", encoding="utf-8") as settings_file:
                raw_settings = json.load(settings_file)
        else:
            raw_settings = {}

    except Exception:
        # Fail-safe fallback to empty configuration
        raw_settings = {}

    # ─────────────────────────────────────────────────────────
    # 3. DEEP DEFAULT CONFIG MERGE
    # ─────────────────────────────────────────────────────────
    # Start from DEFAULT_SETTINGS and layer user overrides on top
    # ─────────────────────────────────────────────────────────

    merged_settings = json.loads(json.dumps(DEFAULT_SETTINGS))

    # Apply only valid top-level overrides
    merged_settings.update(
        {key: value for key, value in (raw_settings or {}).items() if key in merged_settings}
    )

    # ─────────────────────────────────────────────────────────
    # 4. MODEL CONFIGURATION MERGE (SPECIAL CASE)
    # ─────────────────────────────────────────────────────────
    # Ensures nested model settings are preserved correctly
    # ─────────────────────────────────────────────────────────

    if isinstance((raw_settings or {}).get("models"), dict):
        merged_settings["models"].update(raw_settings["models"])

    # ─────────────────────────────────────────────────────────
    # 5. CACHE FINAL RESULT
    # ─────────────────────────────────────────────────────────
    # Store in memory for fast future access
    # ─────────────────────────────────────────────────────────

    _SETTINGS_CACHE = merged_settings

    return merged_settings
    
    
    
# ============================================================
# CONFIG MANAGER — SAVE SETTINGS
# ============================================================
# PURPOSE:
# Persist system configuration safely to disk and update
# in-memory cache for runtime performance.
#
# FLOW:
# settings → validate directory → write JSON → update cache
# ============================================================

def save_settings(settings: dict) -> None:
    """
    Save system settings to persistent storage.

    This function ensures:
    - Settings directory exists
    - JSON file is safely written
    - In-memory cache is updated
    """

    global _SETTINGS_CACHE

    # ─────────────────────────────────────────────
    # 1. ENSURE CONFIG DIRECTORY EXISTS
    # ─────────────────────────────────────────────
    config_directory = os.path.dirname(SETTINGS_FILE)
    os.makedirs(config_directory, exist_ok=True)

    # ─────────────────────────────────────────────
    # 2. WRITE SETTINGS TO DISK
    # ─────────────────────────────────────────────
    with open(SETTINGS_FILE, "w", encoding="utf-8") as settings_file:
        json.dump(settings, settings_file, indent=2)

    # ─────────────────────────────────────────────
    # 3. UPDATE RUNTIME CACHE
    # ─────────────────────────────────────────────
    _SETTINGS_CACHE = settings