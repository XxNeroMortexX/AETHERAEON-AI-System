"""
Aetheraeon AI - System Utilities

Purpose:
Provides small reusable helpers shared across the current Aetheraeon runtime.

Architecture Layer:
Utility and Support Layer.

Responsibilities:
- Perform generic formatting, normalization, and lightweight data transformations.
- Reduce duplicated helper logic across core modules.
- Return predictable values to calling components.

Boundaries:
- Utilities do not own cognitive policy, routing, orchestration, storage, security decisions, or tool execution.
- Module-specific business logic remains with the component that owns that responsibility.
"""


# ============================================================
# CORE STANDARD LIBRARY IMPORTS
# ============================================================
# These are built-in Python modules used for utility logic,
# time handling, string processing, and system-level helpers.
# ============================================================

import json          # JSON parsing (safe serialization if needed)
import re            # Pattern matching for text extraction / validation
import os            # System path utilities (used in path helpers)
from datetime import datetime, timezone  # Time utilities (UTC + local timestamps)


# ============================================================
# EXTERNAL DEPENDENCIES (PIP INSTALLED PACKAGES)
# ============================================================
# NOTE:
# system_utils.py is a PURE utility layer.
# It intentionally avoids external dependencies where possible.
# ============================================================

# (No external dependencies required for this module)


# ============================================================
# INTERNAL SYSTEM IMPORTS (ARCHITECTURE LAYERS)
# ============================================================
# This module is a SHARED UTILITY LAYER used across the system.
#
# RULES:
# - No AI reasoning logic here
# - No tool execution logic here
# - Only safe helper functions
#
# COMMON DEPENDENCY USAGE:
# - memory_database.py (string sanitation before inserts)
# - system_security.py (path validation helpers)
# - tool_executor.py (path parsing / normalization)
# - api_gateway.py (logging + timestamps)
# ============================================================

# ------------------------------------------------------------
# CORE SYSTEM INTEGRATION NOTE
# ------------------------------------------------------------
# system_utils.py is intentionally dependency-light.
# It does NOT import other core modules to avoid circular imports
# and to remain a shared foundational utility layer.
# ------------------------------------------------------------


# ============================================================
# HUMAN-READABLE LOCAL TIMESTAMP GENERATOR
# ============================================================
# Purpose:
# Generate a formatted local timestamp for system-wide usage.
#
# Common Uses:
# - Logging events
# - Debug output
# - UI display timestamps
# - Conversation history tracking
#
# Format:
# YYYY-MM-DD HH:MM:SS
# ============================================================

def get_timestamp() -> str:

    # --------------------------------------------------------
    # Generate Current Local Time
    # --------------------------------------------------------

    current_time = datetime.now()

    # --------------------------------------------------------
    # Format into Human-Readable String
    # --------------------------------------------------------

    formatted_timestamp = current_time.strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # --------------------------------------------------------
    # Return Result
    # --------------------------------------------------------

    return formatted_timestamp


# ============================================================
# HUMAN-READABLE UTC TIMESTAMP GENERATOR
# ============================================================
# Purpose:
# Generate a standardized UTC timestamp for global system sync.
#
# Use Cases:
# - Distributed logging systems
# - API event tracking
# - Cross-device synchronization
# - Memory consistency timestamps
#
# Format:
# YYYY-MM-DD HH:MM:SS (UTC)
# ============================================================

def get_utc_timestamp() -> str:

    # --------------------------------------------------------
    # Import UTC Timezone Context
    # --------------------------------------------------------
    # Ensures timestamp is generated in universal time standard
    # --------------------------------------------------------

    current_utc_time = datetime.now(timezone.utc)

    # --------------------------------------------------------
    # Format UTC Timestamp
    # --------------------------------------------------------

    formatted_utc_timestamp = current_utc_time.strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # --------------------------------------------------------
    # Return Final UTC String
    # --------------------------------------------------------

    return formatted_utc_timestamp


# ============================================================
# UNIX TIMESTAMP GENERATOR (EPOCH TIME)
# ============================================================
# Purpose:
# Generate a Unix timestamp representing seconds since
# 1970-01-01 00:00:00 UTC.
#
# Use Cases:
# - Database indexing and sorting
# - Memory timestamping (fast comparisons)
# - Event tracking and logging
# - Performance measurement systems
#
# Advantage:
# - Integer-based (fast operations)
# - Globally standardized
# - Efficient for AI memory systems
# ============================================================

def get_unix_timestamp() -> int:

    # --------------------------------------------------------
    # Capture Current UTC Time
    # --------------------------------------------------------
    # Ensures consistency across distributed systems
    # --------------------------------------------------------

    current_utc_time = datetime.now(timezone.utc)

    # --------------------------------------------------------
    # Convert to Unix Epoch Timestamp
    # --------------------------------------------------------

    unix_timestamp = int(current_utc_time.timestamp())

    # --------------------------------------------------------
    # Return Final Integer Value
    # --------------------------------------------------------

    return unix_timestamp


# ============================================================
# STRING SANITIZATION FOR DATABASE SAFETY
# ============================================================
# Purpose:
# Ensure strings are safe for storage in MariaDB columns,
# especially when legacy encodings (latin1/utf8) are used.
#
# Problem Context:
# - utf8mb4 supports full Unicode (including emojis)
# - Older encodings may reject 4-byte characters
# - This prevents insert failures and system crashes
#
# Strategy:
# - Normalize string encoding safely
# - Replace invalid or unsupported characters
# - Preserve as much readable content as possible
# ============================================================

def safe_string(text: str) -> str:

    # --------------------------------------------------------
    # Handle Empty or Null Input
    # --------------------------------------------------------

    if not text:
        return ""

    # --------------------------------------------------------
    # Normalize UTF-8 Encoding Safely
    # --------------------------------------------------------
    # - Converts string to UTF-8 bytes
    # - Re-decodes while replacing invalid sequences
    # - Prevents DB crashes from unsupported characters
    # --------------------------------------------------------

    try:
        normalized_text = text.encode(
            "utf-8",
            errors="replace"
        ).decode(
            "utf-8",
            errors="replace"
        )

    except Exception:
        # ----------------------------------------------------
        # Fail-Safe Fallback
        # ----------------------------------------------------
        normalized_text = text

    # --------------------------------------------------------
    # Return Sanitized String
    # --------------------------------------------------------

    return normalized_text


# ============================================================
# DIRECTORY OUTPUT PARSER
# ============================================================
# PURPOSE:
# Converts raw system directory command output into a
# structured, human-readable format.
#
# This is a PURE parsing utility.
# It does NOT execute system commands.
# ============================================================

def clean_dir_output(raw_output):
    """
    Parses raw directory listing output into structured format.

    Returns:
        string: formatted file + folder listing
    """

    # --------------------------------------------------------
    # INITIAL VALIDATION
    # --------------------------------------------------------
    # PURPOSE:
    # Ensure input exists before processing.
    # --------------------------------------------------------

    if not raw_output:
        return "No directory output provided."

    lines = raw_output.splitlines()

    folders = []
    files = []

    # ========================================================
    # LINE-BY-LINE PARSING
    # ========================================================

    for line in lines:

        cleaned_line = line.strip()

        if not cleaned_line:
            continue

        # ----------------------------------------------------
        # SKIP SYSTEM HEADER LINES
        # ----------------------------------------------------
        # PURPOSE:
        # Ignore Windows dir command metadata lines.
        # ----------------------------------------------------

        if any(skip_text in cleaned_line for skip_text in [
            "Volume in drive",
            "Directory of",
            "File(s)",
            "Dir(s)"
        ]):
            continue

        # ----------------------------------------------------
        # DIRECTORY DETECTION
        # ----------------------------------------------------
        # PURPOSE:
        # Detect folders using "<DIR>" marker.
        # ----------------------------------------------------

        if "<DIR>" in cleaned_line:

            parts = cleaned_line.split()

            if len(parts) >= 4:
                folder_name = parts[-1]

                if folder_name not in [".", ".."]:
                    folders.append(folder_name)

        # ----------------------------------------------------
        # FILE DETECTION
        # ----------------------------------------------------
        # PURPOSE:
        # Detect file entries using date pattern matching.
        # ----------------------------------------------------

        elif re.search(r"\d{1,2}/\d{1,2}/\d{4}", cleaned_line):

            parts = cleaned_line.split()

            if len(parts) >= 4:
                files.append(parts[-1])

    # ========================================================
    # FORMAT FINAL OUTPUT
    # ========================================================

    formatted_output = "FOLDERS:\n"

    if folders:
        formatted_output += "\n".join(f"  {folder}" for folder in folders)
    else:
        formatted_output += "  (none)"

    formatted_output += "\n\nFILES:\n"

    if files:
        formatted_output += "\n".join(f"  {file}" for file in files)
    else:
        formatted_output += "  (none)"

    return formatted_output


# ============================================================
# WINDOWS PATH EXTRACTION
# ============================================================
# Purpose:
# Extract Windows drive-based file paths from arbitrary text.
#
# Examples:
#
# "notepad C:\Temp\file.txt"
#     -> ["C:\Temp\file.txt"]
#
# "copy D:\Data\a.txt E:\Backup"
#     -> ["D:\Data\a.txt", "E:\Backup"]
#
# Returns:
# List[str]
#     Collection of detected Windows drive paths.
#
# Notes:
# - Performs extraction only
# - Does NOT validate path safety
# - Does NOT verify path existence
# - Security validation occurs in system_security.py
# ============================================================

def extract_windows_paths(command_text: str) -> list[str]:

    # --------------------------------------------------------
    # Null / Empty Input Protection
    # --------------------------------------------------------

    if not command_text:
        return []

    # --------------------------------------------------------
    # Extract Windows Drive-Based Paths
    # --------------------------------------------------------
    # Matches:
    #   C:\Folder\File.txt
    #   D:/Folder/File.txt
    #   E:\Backup
    # --------------------------------------------------------

    detected_paths = re.findall(
        r"[A-Za-z]:[\\/][^\"'\n]*",
        command_text
    )

    # --------------------------------------------------------
    # Return Extracted Paths
    # --------------------------------------------------------

    return detected_paths    
