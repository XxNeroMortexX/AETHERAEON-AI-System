"""
========================================================
AETHERAEON — CONFIG LOADER (SYSTEM CONFIGURATION LAYER)
========================================================

FILE PURPOSE:
This file is responsible for loading, validating,
and providing system configuration values used across
the entire AI architecture.

It acts as the central configuration access layer
for both runtime and startup settings.

========================================================
SYSTEM ROLE:
"Configuration Backbone" of the architecture.

It does NOT process AI reasoning.
It does NOT execute tools.
It ONLY loads, validates, and serves configuration data.

========================================================
RESPONSIBILITIES:
(config_loader.py)

- Load configuration files (JSON / ENV / system config)
- Provide centralized access to system settings
- Validate configuration structure and defaults
- Merge environment variables with file-based config
- Provide safe configuration retrieval methods
- Support runtime config updates (if enabled)
- Normalize config formats for internal system use

========================================================
STRICT BOUNDARIES (DO NOT BREAK):
(config_loader.py)

This file MUST NOT:
- Perform AI reasoning or decision making
- Execute tools or external actions
- Modify memory database directly
- Handle API routing or request logic
- Contain business logic beyond configuration handling

It ONLY manages configuration data.

========================================================
CONFIG LOADER FLOW:

Startup / Runtime Request
    ↓
load_config_file()
    ↓
merge_environment_variables()
    ↓
validate_config_schema()
    ↓
apply_defaults()
    ↓
return normalized config object
    ↓
used by all system layers

========================================================
SYSTEM WIDE USAGE:

config_loader.py is used by:
- ai_orchestrator.py
- request_router.py
- tool_executor.py
- external_toolkit.py
- system_paths.py
- memory_database.py

========================================================
KEY FUNCTIONS (THIS FILE):

- load_config()
- get_config()
- get_setting()
- reload_config()
- validate_config()
- merge_env_config()

========================================================
OUTPUT CONTRACT:

This module returns:
- configuration dictionary/object
- validated runtime settings
- environment-overridden values

========================================================
DESIGN PHILOSOPHY:

"Single Source of Truth for Configuration"

- Config is centralized
- No duplicated settings across modules
- Environment overrides always take priority
- System must remain deterministic and reproducible

========================================================
"""


# ============================================================
# CONFIG LOADER (ENVIRONMENT + SYSTEM CONFIG ACCESS LAYER)
# ============================================================
# PURPOSE:
# Loads environment variables and provides centralized access
# to system-wide configuration values.
#
# This ensures configuration is:
# - consistent
# - secure
# - loaded from AISystem root
# ============================================================

import os
from dotenv import load_dotenv

from core.system_paths import AISYSTEM_ROOT


# ============================================================
# ENVIRONMENT LOADING (SYSTEM ROOT BASED)
# ============================================================
# PURPOSE:
# Ensures .env is always loaded from the AI system root folder,
# NOT from the current working directory.
#
# This prevents:
# - broken configs when running from different entry points
# - environment mismatches in production vs dev
# ============================================================

ENV_PATH = AISYSTEM_ROOT / ".env"
load_dotenv(dotenv_path=ENV_PATH)


# ============================================================
# DATABASE CONFIGURATION (CORE SYSTEM CONNECTION)
# ============================================================
# PURPOSE:
# Centralized database connection settings used across:
# - memory_database.py
# - api_gateway.py
# - tool_executor.py (if needed)
# ============================================================

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")


# ============================================================
# SECURITY CONFIGURATION
# ============================================================
# PURPOSE:
# System-wide security keys and encryption anchors.
# Used for:
# - session validation
# - API security
# - token signing
# ============================================================

SECRET_KEY = os.getenv("SECRET_KEY")