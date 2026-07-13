"""
========================================================
AETHERAEON — SYSTEM SECURITY LAYER
========================================================

FILE PURPOSE:
This file provides centralized security, validation,
sanitization, and safety enforcement for the AI system.

It protects the system from unsafe operations,
invalid inputs, unauthorized actions, and
dangerous execution requests.

========================================================
SYSTEM ROLE:
"Security & Validation Layer" of the architecture.

This layer sits between user requests and system actions.

Its job is to determine whether an operation is safe
before execution is allowed to continue.

========================================================
RESPONSIBILITIES:
(system_security.py)

- Input validation
- Command validation
- Path validation
- Filesystem safety checks
- Permission enforcement
- Execution restrictions
- Security policy enforcement
- Dangerous operation detection
- Command sanitization
- Directory boundary protection

========================================================
STRICT BOUNDARIES (DO NOT BREAK):
(system_security.py)

This file MUST NOT:

- Perform AI reasoning
- Generate AI responses
- Execute tools
- Execute shell commands
- Access LLM models directly
- Manage conversation memory
- Modify UI state
- Perform orchestration logic

It ONLY validates and protects.

========================================================
SYSTEM SECURITY FLOW:

Incoming Request
    ↓
request_router.py
    ↓
tool_executor.py
    ↓
system_security.py
    ↓
Validation
    ↓
ALLOW or DENY
    ↓
tool_executor.py
    ↓
Execution (if approved)

========================================================
SYSTEM WIDE FLOW:

User Input
    ↓
api_gateway.py
    ↓
request_router.py
    ↓
ai_orchestrator.py
    ↓
tool_executor.py
    ↓
system_security.py   ← THIS FILE
    ↓
external_toolkit.py
    ↓
Operating System / External Services

========================================================
KEY FILE DEPENDENCIES:

system_security.py commonly works with:

- tool_executor.py
- system_paths.py
- system_utils.py
- external_toolkit.py

========================================================
OUTPUT CONTRACT:

Functions in this file return:

- Boolean allow / deny decisions
- Sanitized values
- Validation results
- Security error messages
- Policy violation information

========================================================
DESIGN PHILOSOPHY:

"Trust Nothing. Validate Everything."

- User input is validated
- Paths are validated
- Commands are validated
- Operations are validated
- Security checks happen before execution

========================================================
"""

# ============================================================
# CORE STANDARD LIBRARY IMPORTS
# ============================================================
# These are built-in Python modules used for logic, parsing,
# system operations, and security validation.
# ============================================================

import json          # Structured data parsing (tool configs / settings)
import re            # Pattern matching for command + path validation
import os            # Filesystem access + environment safety checks
import time          # Timing / debugging / security tracing (optional use)
import threading     # Future-safe async protection for command execution
from datetime import datetime  # Logging + audit timestamps


# ============================================================
# EXTERNAL DEPENDENCIES (PIP INSTALLED PACKAGES)
# ============================================================
# Third-party libraries used for network or system operations.
# ============================================================

import requests      # HTTP requests (web search / external validation if needed)


# ============================================================
# INTERNAL SYSTEM IMPORTS (ARCHITECTURE LAYERS)
# ============================================================
# Security system sits BELOW orchestration and ABOVE execution.
#
# RULES:
# - This file ONLY validates and sanitizes actions
# - It does NOT execute commands
# - It does NOT access database directly
# - It DOES enforce safety boundaries for tool execution
# ============================================================

# ------------------------------------------------------------
# CONFIGURATION LAYER
# (Loads security rules, blocked tokens, allowed commands)
# ------------------------------------------------------------
from core import config_loader

# ------------------------------------------------------------
# SYSTEM PATHS LAYER
# (Defines root, project, and sandbox boundaries)
# ------------------------------------------------------------
from core import system_paths
from core import system_utils

# ------------------------------------------------------------
# TOOL REGISTRY LAYER (READ-ONLY USAGE)
# (Used for validating allowed command types if needed)
# ------------------------------------------------------------
from core.tool_registry import get_tools


# ============================================================
# CENTRAL SHELL SECURITY POLICY
# ============================================================

BLOCKED_SHELL_TOKENS = [
    "del", "erase", "format",
    "shutdown", "taskkill",
    "reg", "netsh", "cipher", "bcdedit", "diskpart", "sfc", "dism",
    "powershell", "pwsh", "cmd", "curl", "wget", "bitsadmin", "certutil",
    "rm", "mv",
]

READ_ONLY_SHELL_COMMANDS = [
    "dir", "cd", "explorer", "tree", "where",
    "systeminfo", "ver", "hostname", "whoami",
    "echo", "type", "more", "find", "findstr",
    "time", "date",
    "tasklist", "wmic", "driverquery",
    "ipconfig", "ping", "tracert", "nslookup", "netstat", "arp",
]

WRITE_ALLOWED_SHELL_COMMANDS = [
    "copy", "xcopy", "robocopy",
    "move", "rename",
    "mkdir", "rmdir",
]


# ============================================================
# COMMAND SECURITY VALIDATION
# ============================================================
# Purpose:
# Validate whether a shell command is allowed to execute
# under the current security rules.
#
# Security Checks:
# - Blocks dangerous command patterns
# - Allows approved read-only commands
# - Restricts write operations to the active project
# - Prevents access outside approved project boundaries
#
# Returns:
# True  = Command is approved
# False = Command is denied
# ============================================================

def validate_command_security(
    command_text: str,
    session: dict | None = None
) -> bool:

    # --------------------------------------------------------
    # Basic Input Validation
    # --------------------------------------------------------

    if not command_text:
        return False

    normalized_command = command_text.strip().lower()

    # --------------------------------------------------------
    # Block Dangerous Command Patterns
    # --------------------------------------------------------

    if any(
        re.search(
            rf"(?<![\w-]){re.escape(blocked_token)}(?![\w-])",
            normalized_command,
        )
        for blocked_token in BLOCKED_SHELL_TOKENS
    ):
        return False

    # Shell composition, redirection, expansion, and escaping can
    # turn an allowed first command into an arbitrary second action.
    if re.search(r"[&|<>;^`%!\r\n()]", normalized_command):
        return False

    # --------------------------------------------------------
    # Extract Primary Command Verb
    # --------------------------------------------------------

    command_verb = get_first_command_token(
        normalized_command
    )

    # --------------------------------------------------------
    # Allow Approved Read-Only Commands
    # --------------------------------------------------------

    if command_verb in READ_ONLY_SHELL_COMMANDS:
        if command_verb in ("time", "date") and normalized_command not in (
            "time /t",
            "date /t",
        ):
            return False

        # WMIC supports mutating verbs even though normal queries are
        # read-only. Keep only its listing/query forms.
        if command_verb == "wmic" and re.search(
            r"\b(call|create|delete|set)\b",
            normalized_command,
        ):
            return False
        return True

    # --------------------------------------------------------
    # Validate Write Operations
    # --------------------------------------------------------

    if command_verb in WRITE_ALLOWED_SHELL_COMMANDS:

        # ----------------------------------------------------
        # Retrieve Active Project Boundary
        # ----------------------------------------------------

        active_project_path = (
            (session or {}).get("aider_project")
            or str(system_paths.AISYSTEM_ROOT)
        )

        # ----------------------------------------------------
        # Determine Current Working Directory
        # ----------------------------------------------------

        current_working_directory = None

        if session:
            current_working_directory = session.get(
                "cwd"
            )

        current_working_directory = (
            current_working_directory
            or str(system_paths.AISYSTEM_ROOT)
        )

        # ----------------------------------------------------
        # Ensure Current Directory Stays Inside Project
        # ----------------------------------------------------

        if not is_path_within_directory(
            active_project_path,
            current_working_directory
        ):
            return False

        # ----------------------------------------------------
        # Validate Referenced Paths
        # ----------------------------------------------------

        referenced_paths = system_utils.extract_windows_paths(
            command_text
        )

        for referenced_path in referenced_paths:

            if not is_path_within_directory(
                active_project_path,
                referenced_path
            ):
                return False

        # Validate relative paths too; otherwise `..` traversal could
        # escape the active project without matching the drive-path regex.
        command_arguments = re.findall(r'"[^"]*"|\S+', command_text)[1:]
        for argument in command_arguments:
            argument = argument.strip('"')
            if not argument or argument.startswith(("/", "-")):
                continue
            resolved_argument = (
                argument
                if os.path.isabs(argument)
                else os.path.join(current_working_directory, argument)
            )
            if not is_path_within_directory(
                active_project_path,
                resolved_argument,
            ):
                return False

        return True

    # --------------------------------------------------------
    # Unknown Commands Default To Deny
    # --------------------------------------------------------

    return False


# ============================================================
# COMMAND TOKEN EXTRACTION
# ============================================================
# Purpose:
# Extract the primary command token from a command string.
#
# Examples:
# "dir C:\\Temp"      -> "dir"
# "python app.py"     -> "python"
# "  git status"      -> "git"
#
# Returns:
# Lowercase command token.
#
# Returns:
# Empty string if no command exists.
# ============================================================

def get_first_command_token(
    command_text: str
) -> str:

    # --------------------------------------------------------
    # Normalize Input
    # --------------------------------------------------------

    normalized_command = (
        command_text or ""
    ).strip()

    if not normalized_command:
        return ""

    # --------------------------------------------------------
    # Extract First Command Token
    # --------------------------------------------------------

    command_parts = normalized_command.split()

    command_token = command_parts[0]

    # --------------------------------------------------------
    # Return Standardized Result
    # --------------------------------------------------------

    return command_token.lower()
    
 
# ============================================================
# DIRECTORY CONTAINMENT VALIDATION
# ============================================================
# Purpose:
# Validate that a target filesystem path remains inside a
# permitted base directory boundary.
#
# Security Use Case:
# - Prevent path traversal attacks
# - Restrict file access to approved project scope
# - Enforce sandboxed execution boundaries
#
# Returns:
# True  -> target path is safely contained within base directory
# False -> target path escapes allowed directory scope
# ============================================================

def is_path_within_directory(
    base_directory: str,
    target_path: str
) -> bool:

    # --------------------------------------------------------
    # Safety Guard: Invalid Input Protection
    # --------------------------------------------------------

    if not base_directory or not target_path:
        return False

    try:

        # ----------------------------------------------------
        # Normalize Absolute File System Paths
        # ----------------------------------------------------

        normalized_base_path = os.path.abspath(
            base_directory
        )

        normalized_target_path = os.path.abspath(
            target_path
        )

        # ----------------------------------------------------
        # Direct Path Match Check
        # ----------------------------------------------------
        # Allow exact base directory match as valid access
        # ----------------------------------------------------

        if normalized_target_path == normalized_base_path:
            return True

        # ----------------------------------------------------
        # Normalize Base Path for Containment Check
        # ----------------------------------------------------
        # Ensures directory boundary consistency
        # ----------------------------------------------------

        if not normalized_base_path.endswith(os.sep):
            normalized_base_path += os.sep

        # ----------------------------------------------------
        # Directory Containment Validation
        # ----------------------------------------------------

        is_within_boundary = normalized_target_path.startswith(
            normalized_base_path
        )

        return is_within_boundary

    except Exception:
        # ----------------------------------------------------
        # Fail-Safe Security Policy (Default Deny)
        # ----------------------------------------------------

        return False


# ============================================================
# FILE PATH SANITIZATION ENGINE
# ============================================================
# Purpose:
# Normalize and sanitize raw user input into a safe,
# structured filesystem path.
#
# Security Role:
# - Removes shell-style command prefixes
# - Strips unsafe wrappers and quoting artifacts
# - Extracts valid Windows-style absolute paths
# - Prevents malformed input from reaching security layer
#
# Output:
# - Clean filesystem path string
# - None if no valid path can be resolved
# ============================================================

def sanitize_file_path(
    raw_input: str
) -> str | None:

    # --------------------------------------------------------
    # Input Validation Guard
    # --------------------------------------------------------

    if not raw_input:
        return None

    cleaned_path = raw_input.strip()

    # --------------------------------------------------------
    # Remove Shell Command Prefixes
    # --------------------------------------------------------
    # Example:
    # "explorer C:\Temp" → "C:\Temp"
    # --------------------------------------------------------

    while re.match(
        r"^explorer\b",
        cleaned_path,
        re.IGNORECASE
    ):
        cleaned_path = cleaned_path[
            len("explorer"):
        ].strip()

    # --------------------------------------------------------
    # Remove Wrapping Quotes / Noise Characters
    # --------------------------------------------------------

    cleaned_path = cleaned_path.strip(
        '"'
    ).strip("'").strip()

    # --------------------------------------------------------
    # Extract Windows Absolute Path Pattern
    # --------------------------------------------------------
    # Only accepts drive-based paths (C:\, D:\, etc.)
    # --------------------------------------------------------

    path_match = re.search(
        r"[A-Za-z]:\\[^\"'\n]*",
        cleaned_path
    )

    if path_match:

        extracted_path = path_match.group().strip()

        # Fix: remove trailing quotes safely
        cleaned_path = extracted_path.rstrip('"').strip()

    # --------------------------------------------------------
    # Final Safety Check
    # --------------------------------------------------------

    if not cleaned_path:
        return None

    return cleaned_path    
