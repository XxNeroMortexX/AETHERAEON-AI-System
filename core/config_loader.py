"""
Aetheraeon AI - Configuration Loader

Purpose:
Loads and normalizes the configuration values used by the current Aetheraeon runtime.

Architecture Layer:
Configuration Layer.

Responsibilities:
- Read supported environment and configuration sources.
- Apply established defaults and validate required values.
- Provide consistent configuration data to calling modules.

Boundaries:
- Configuration values influence supported behavior but do not execute actions or establish cognitive policy.
- This module does not make routing, memory, permission, security, model, or tool decisions.
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
