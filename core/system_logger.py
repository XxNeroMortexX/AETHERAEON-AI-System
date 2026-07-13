"""
========================================================
AETHERAEON — SYSTEM OBSERVABILITY & LOGGING LAYER
========================================================

FILE PURPOSE:
This file provides centralized logging, diagnostics,
observability, telemetry, and runtime event tracking for
the entire Aetheraeon AI platform.

It serves as the unified logging interface used by every
major subsystem to record operational activity, assist
debugging, improve transparency, and support long-term
system maintainability.

Rather than influencing system behavior, this component
records what happens throughout the AI architecture and
provides a historical view of system operation.

========================================================
SYSTEM ROLE:
"Observability & Logging Layer" of the architecture.

This file does NOT:
- Perform AI reasoning
- Execute tools
- Route requests
- Modify application state
- Store AI memory

It ONLY:
- Records
- Formats
- Reports
- Observes
- Diagnoses

========================================================
CURRENT RESPONSIBILITIES:
(system_logger.py)

- Record runtime events
- Display informational messages
- Record warnings and errors
- Provide consistent log formatting
- Support startup diagnostics
- Assist development debugging
- Improve system observability
- Provide centralized logging utilities

========================================================
FUTURE RESPONSIBILITIES (ARCHITECTURE ROADMAP):

As Aetheraeon evolves, this component is planned to
become the centralized observability and telemetry
subsystem for the entire AI platform.

Future capabilities may include:

- Structured logging
- Configurable log levels
- Log categorization
- Session tracing
- AI reasoning traces
- Tool execution traces
- Memory operation auditing
- Database diagnostics
- Performance timing metrics
- Resource utilization reporting
- Security audit logging
- Event correlation IDs
- Persistent log storage
- Automatic log rotation
- Historical diagnostics
- Distributed logging
- External monitoring integrations
- Dashboard and analytics support

These capabilities represent planned architectural goals
and may be implemented incrementally as the platform
continues to mature.

========================================================
STRICT BOUNDARIES (DO NOT BREAK):
(system_logger.py)

This file MUST NOT:

- Perform AI reasoning or orchestration
- Execute tools or external commands
- Modify databases or memory
- Change system configuration
- Handle HTTP/API requests
- Route user requests
- Generate AI responses
- Implement business logic

It ONLY records and reports operational events.

========================================================
SYSTEM LOGGER FLOW:
(system_logger.py)

System Event
        ↓
Receive logging request
        ↓
Format log entry
        ↓
Assign log level/category
        ↓
Output to configured destinations
        ↓
Return control to calling component

========================================================
SYSTEM WIDE POSITION:

                User
                  │
                  ▼
          api_gateway.py
                  │
                  ▼
        request_router.py
                  │
                  ▼
        ai_orchestrator.py
                  │
     ┌────────────┼────────────┐
     │            │            │
     ▼            ▼            ▼
tool_executor  memory_interface  external_toolkit
     │            │            │
     └────────────┼────────────┘
                  │
                  ▼
        system_logger.py
                  │
                  ▼
     Console • Log Files • Telemetry
        Diagnostics • Monitoring

========================================================
KEY FILE DEPENDENCIES:

system_logger.py may be used by:

- api_gateway.py
- request_router.py
- ai_orchestrator.py
- tool_executor.py
- memory_interface.py
- memory_database.py
- system_health_check.py
- external_toolkit.py
- model_registry.py

========================================================
OUTPUT CONTRACT:

This component returns or produces:

- Formatted log messages
- Runtime diagnostics
- Error reports
- Warning messages
- Debug information
- Telemetry events
- Optional logging metadata

========================================================
DESIGN PHILOSOPHY:

"Everything Important Leaves a Trace."

Every major event within Aetheraeon should be observable,
traceable, and diagnosable.

The logging system exists to improve transparency,
reliability, maintainability, and operational insight
without influencing how the AI thinks or behaves.

By separating observability from execution, Aetheraeon
remains modular, predictable, and easier to debug as the
platform continues to evolve.

========================================================
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