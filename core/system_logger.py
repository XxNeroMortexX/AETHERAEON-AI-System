"""
Aetheraeon AI - System Logger

Purpose:
Provides centralized operational logging and event reporting for the current Aetheraeon runtime.

Architecture Layer:
Cognitive Observability Layer - logging support.

Responsibilities:
- Record formatted runtime, warning, error, security, tool, memory, and service events.
- Provide consistent operational metadata for diagnostics and correlation.
- Support current console and configured logging destinations.

Boundaries:
- Logging observes outcomes and does not make decisions, execute actions, or modify application state.
- Logs must not capture private chain-of-thought, hidden reasoning traces, private prompts, secrets, credentials, or raw embeddings.
- Cognitive Trace summaries and the Admin Cognitive Inspector are planned capabilities; the logger is not their policy authority.
"""

# ============================================================
# CORE STANDARD LIBRARY IMPORTS
# ============================================================
# Built-in Python modules used for:
# - timestamps
# - filesystem operations
# - structured logging
# - debug formatting
# - runtime inspection
# ============================================================

import os                    # Filesystem operations and path handling
import json                  # Structured JSON formatting/log payloads
from datetime import datetime  # Timestamp generation for log entries


# ============================================================
# DATABASE / STORAGE DEPENDENCIES
# ============================================================
# Database connection layer used for persistent log storage.
# ============================================================

import mysql.connector       # MariaDB / MySQL database driver


# ============================================================
# INTERNAL SYSTEM IMPORTS (ARCHITECTURE LAYERS)
# ============================================================
# Internal AETHERAEON system dependencies.
#
# RULES:
# - Only import architecture layers or utilities
# - No execution logic here
# - Keep imports grouped by responsibility
# ============================================================

# ------------------------------------------------------------
# DATABASE ACCESS LAYER
# ------------------------------------------------------------
# Provides centralized database connection handling.
# ------------------------------------------------------------

from core.memory_database import get_db


# ------------------------------------------------------------
# CONFIGURATION LAYER
# ------------------------------------------------------------
# Provides system configuration values and runtime settings.
# ------------------------------------------------------------

from core import config_loader


# ------------------------------------------------------------
# PATH MANAGEMENT LAYER
# ------------------------------------------------------------
# Centralized filesystem path definitions.
# ------------------------------------------------------------

from core import system_paths


# ============================================================
# SYSTEM LOGGER — WRITE LOG ENTRY
# ============================================================
# Centralized persistent logging system for:
# - AI decisions
# - tool execution
# - runtime diagnostics
# - audit history
# - analytics and debugging
#
# This function stores structured operational events
# inside the SQL logging database.
#
# FILE:
#   system_logger.py
# ============================================================

def write_log(
    user_id: int,
    action: str,
    input_data: str = None,
    output_data: str = None,
    tool_name: str = None,
) -> None:
    """
    Persist a structured system log entry.

    Args:
        user_id:
            Internal user/session identifier.

        action:
            High-level event description.
            Example:
                "tool_execution"
                "memory_store"
                "model_switch"

        input_data:
            Original input or request payload.

        output_data:
            Result or response generated.

        tool_name:
            Tool/subsystem responsible for the action.
    """

    # --------------------------------------------------------
    # Initialize database connection
    # --------------------------------------------------------
    # Logging should always use a short-lived connection
    # to avoid stale sessions and connection leaks.
    # --------------------------------------------------------

    database_connection = get_db()

    database_cursor = database_connection.cursor()

    try:

        # ----------------------------------------------------
        # Insert structured log record
        # ----------------------------------------------------
        # Stores:
        # - actor/user
        # - event type
        # - input/output payloads
        # - originating subsystem/tool
        # ----------------------------------------------------

        database_cursor.execute(
            """
            INSERT INTO logs (
                user_id,
                action,
                input,
                output,
                tool
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                user_id,
                action,
                input_data,
                output_data,
                tool_name,
            )
        )

        # ----------------------------------------------------
        # Commit transaction
        # ----------------------------------------------------
        # Makes the log entry persistent immediately.
        # ----------------------------------------------------

        database_connection.commit()

    except Exception as logging_error:

        # ----------------------------------------------------
        # Logging safety fallback
        # ----------------------------------------------------
        # Logging should NEVER crash the AI system.
        # If logging fails, print a lightweight warning
        # and continue system execution.
        # ----------------------------------------------------

        print(
            f"[LOGGER ERROR] Failed to write log entry: "
            f"{logging_error}"
        )

    finally:

        # ----------------------------------------------------
        # Cleanup database resources
        # ----------------------------------------------------
        # Always close:
        # - cursor
        # - connection
        #
        # Prevents connection leaks and pool exhaustion.
        # ----------------------------------------------------

        try:
            database_cursor.close()
        except Exception:
            pass

        try:
            database_connection.close()
        except Exception:
            pass
