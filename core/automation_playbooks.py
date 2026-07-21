"""
Aetheraeon AI - Automation Playbooks

Purpose:
Manages reusable workflow definitions and coordinates approved multi-step automation through existing execution systems.

Architecture Layer:
Workflow automation support within the Tool Execution Layer.

Responsibilities:
- Store and validate workflow definitions and ordered steps.
- Coordinate workflow state and collect step results.
- Delegate executable actions to registered tool and external integration paths.

Boundaries:
- Playbooks do not infer user intent, make cognitive policy, authorize tools, or perform AI reasoning.
- Every action remains subject to permissions, security checks, and execution-time validation.
- The Cognitive Decision Engine and Planning System are planned policy and planning services, not implementations in this module.
"""

# ============================================================
# CORE STANDARD LIBRARY IMPORTS
# ============================================================
# These are built-in Python modules used for playbook parsing,
# filesystem operations, timing control, and regex routing.
# ============================================================

import json          # JSON parsing for playbook definitions
import re            # Pattern matching for playbook commands
import os            # Filesystem access for playbook loading
import time          # Execution delays for playbook steps
from typing import Dict, Any, Optional  # Type safety for playbook system


# ============================================================
# EXTERNAL DEPENDENCIES (PIP INSTALLED PACKAGES)
# ============================================================
# Third-party libraries used for system-level automation and
# external service communication.
# ============================================================

import requests      # HTTP requests for external services (e.g. n8n)


# ============================================================
# INTERNAL SYSTEM IMPORTS (ARCHITECTURE LAYERS)
# ============================================================
# This section defines ALL internal AI system dependencies.
#
# RULES:
# - These imports are part of the core AI architecture
# - DO NOT mix external libraries here (requests, flask, etc.)
# - DO NOT execute logic here
# - ONLY import system layers or registries
#
# The system is layered as:
# 1. Tool System (execution layer)
# 2. Configuration / system state
# 3. Memory / context injection
# ============================================================

# SYSTEM SECURITY LAYER
from core.system_security import (
    validate_command_security,
    sanitize_file_path,
)

# ------------------------------------------------------------
# TOOL SYSTEM LAYER
# (Executes shell, aider, n8n, and other tool decisions)
# ------------------------------------------------------------

from core.system_utils import clean_dir_output
from core import tool_executor
from core.tool_executor import (
    run_shell,
    run_aider,
    run_n8n,  
)
from core.ai_orchestrator import orchestrate_tool_plan

# ------------------------------------------------------------
# MEMORY / CONTEXT LAYER
# (Shared state passed through playbook execution)
# ------------------------------------------------------------

from core import memory_interface  # if used elsewhere in system
from core.memory_database import chroma_store
from core.system_paths import PLAYBOOK_DIR
from core.tool_registry import register_tool
from core.service_manager import service_state

# ------------------------------------------------------------
# SYSTEM CONFIGURATION / STATUS
# (Global execution flags and runtime system state)
# ------------------------------------------------------------

from core import system_health_check  # optional if centralized elsewhere


# ============================================================
# PLAYBOOK ACTION ROUTING MAP
# ============================================================
# PURPOSE:
# Defines the translation layer between playbook actions
# and tool_executor-compatible decision objects.
#
# FILE:
# automation_playbooks.py
#
# ROLE:
# Action → Execution adapter registry
#
# DESCRIPTION:
# This mapping converts high-level automation commands
# (from JSON playbooks) into structured tool_executor
# decisions that the system can execute safely.
# ============================================================

_PLAYBOOK_ACTION_MAP: dict = {

    # --------------------------------------------------------
    # FILE SYSTEM / EXPLORER ACTIONS
    # --------------------------------------------------------
    # These actions open or inspect directories using shell.
    # --------------------------------------------------------

    "open": lambda target: {
        "tool": "shell",
        "command": f'explorer "{target}"'
    },

    "popen": lambda target: {
        "tool": "shell",
        "command": f'explorer "{target}"'
    },

    "list": lambda target: {
        "tool": "shell",
        "command": f'dir "{target}"'
    },

    "dir": lambda target: {
        "tool": "shell",
        "command": f'dir "{target}"'
    },

    "tree": lambda target: {
        "tool": "shell",
        "command": f'tree "{target}"'
    },

    # --------------------------------------------------------
    # RAW SHELL EXECUTION
    # --------------------------------------------------------
    # Pass-through execution of user-defined shell commands.
    # --------------------------------------------------------

    "shell": lambda target: {
        "tool": "shell",
        "command": target
    },

    # --------------------------------------------------------
    # AI / TOOL INTEGRATION ACTIONS
    # --------------------------------------------------------
    # Delegates execution to specialized AI tooling systems.
    # --------------------------------------------------------

    "chat": lambda _: None,  # handled inline via message field

    "aider": lambda target: {
        "tool": "aider",
        "file": target
    },

    "n8n": lambda target: {
        "tool": "n8n",
        "webhook": target
    },

    # --------------------------------------------------------
    # TIMING CONTROL
    # --------------------------------------------------------
    # Pause execution flow inside playbooks.
    # --------------------------------------------------------

    "wait": lambda target: None  # handled inline via time.sleep
}


# ============================================================
# PLAYBOOK DIRECTORY INITIALIZATION
# ============================================================
# PURPOSE:
# Ensures the automation playbook storage directory exists
# before any workflow files are read or written.
#
# FILE:
# automation_playbooks.py
#
# ROLE:
# Safe filesystem initialization utility
# (prevents runtime errors when accessing playbook storage)
# ============================================================

def ensure_playbook_directory() -> None:
    """
    Create the playbook directory if it does not exist.

    This is a safety initialization function that ensures
    the automation system always has a valid storage path
    for workflow definitions.

    Returns:
        None
    """

    # --------------------------------------------------------
    # DIRECTORY CREATION SAFETY CHECK
    # --------------------------------------------------------
    # - Prevents FileNotFoundError during playbook access
    # - Safe to call multiple times (idempotent operation)
    # --------------------------------------------------------

    os.makedirs(
        PLAYBOOK_DIR,
        exist_ok=True
    )


# ============================================================
# PLAYBOOK DISCOVERY / LISTING
# ============================================================
# PURPOSE:
# Retrieves all stored automation playbooks from disk.
#
# FILE:
# automation_playbooks.py
#
# ROLE:
# Filesystem query utility for workflow registry
# ============================================================

def list_playbooks() -> list:
    """
    Return a list of all available automation playbooks.

    Only JSON-based playbook definitions are included.

    Returns:
        list[str]:
            Filenames of available playbooks.
    """

    # --------------------------------------------------------
    # ENSURE STORAGE DIRECTORY EXISTS
    # --------------------------------------------------------
    # Prevents runtime errors if system is freshly initialized
    # or playbook directory has not yet been created.
    # --------------------------------------------------------

    ensure_playbook_directory()

    # --------------------------------------------------------
    # SCAN PLAYBOOK DIRECTORY
    # --------------------------------------------------------
    # Filter only valid automation definitions (.json files)
    # --------------------------------------------------------

    playbook_files = [
        file_name
        for file_name in os.listdir(PLAYBOOK_DIR)
        if file_name.endswith(".json")
    ]

    return playbook_files
    

# ============================================================
# PLAYBOOK LOADER (FILE DESERIALIZATION)
# ============================================================
# PURPOSE:
# Loads a single automation playbook from disk into memory.
#
# FILE:
# automation_playbooks.py
#
# ROLE:
# Converts stored JSON playbook definitions into Python objects
# for execution by tool_executor.py
# ============================================================

def load_playbook(playbook_name: str):
    """
    Load a playbook JSON file and return its structured data.

    Args:
        playbook_name (str):
            Name of the playbook (with or without .json extension)

    Returns:
        dict | None:
            Parsed playbook content if found, otherwise None.
    """

    # --------------------------------------------------------
    # ENSURE PLAYBOOK STORAGE DIRECTORY EXISTS
    # --------------------------------------------------------
    # Prevents file access errors on fresh installs or resets
    # --------------------------------------------------------

    ensure_playbook_directory()

    # --------------------------------------------------------
    # NORMALIZE FILE NAME
    # --------------------------------------------------------
    # Ensures consistent file format handling
    # --------------------------------------------------------

    if not playbook_name.endswith(".json"):
        playbook_name += ".json"

    # --------------------------------------------------------
    # BUILD FULL FILE PATH
    # --------------------------------------------------------
    # Resolves absolute playbook location on disk
    # --------------------------------------------------------

    file_path = os.path.join(PLAYBOOK_DIR, playbook_name)

    # --------------------------------------------------------
    # VALIDATE FILE EXISTENCE
    # --------------------------------------------------------
    # Prevents crashes when playbook is missing
    # --------------------------------------------------------

    if not os.path.exists(file_path):
        return None

    # --------------------------------------------------------
    # LOAD AND PARSE PLAYBOOK
    # --------------------------------------------------------
    # Converts JSON file into usable Python dictionary
    # --------------------------------------------------------

    with open(file_path, "r", encoding="utf-8") as file_handle:
        playbook_data = json.load(file_handle)

    return playbook_data
    

# ============================================================
# PLAYBOOK STEP EXECUTION ENGINE
# ============================================================
# PURPOSE:
# Executes a single step inside an automation playbook.
#
# FILE:
# automation_playbooks.py
#
# ROLE:
# Translates abstract playbook actions into executable
# tool_executor decisions.
# ============================================================

def run_playbook_step(
    step_index: int,
    action_type: str,
    target: str,
    message: str,
    payload: dict,
    session: dict,
    memory: dict,
    *,
    effective_user=None,
) -> dict:
    """
    Execute a single automation playbook step.

    This function acts as the bridge between:
    - high-level playbook definitions
    - low-level tool_executor execution layer

    Args:
        step_index:
            Index of the step in the playbook sequence.

        action_type:
            Type of automation action (chat, wait, aider, etc.)

        target:
            Primary target of the action (file, command, duration, etc.)

        message:
            Optional message content for chat/aider actions.

        payload:
            Additional structured data for execution.

        session:
            Current runtime session state.

        memory:
            Shared system memory context.
    """

    # --------------------------------------------------------
    # ACTION: WAIT / DELAY EXECUTION
    # --------------------------------------------------------
    # Used for timed automation pauses between steps.
    # --------------------------------------------------------

    if action_type == "wait":

        try:
            wait_seconds = float(target) if target else 1
        except ValueError:
            wait_seconds = 1

        print(f"      [PLAYBOOK] Waiting {wait_seconds}s...")

        time.sleep(wait_seconds)
        return {"success": True, "tool": "wait"}

    # --------------------------------------------------------
    # ACTION: CHAT RESPONSE
    # --------------------------------------------------------
    # Sends a structured chat message through tool_executor.
    # --------------------------------------------------------

    if action_type == "chat":

        result = orchestrate_tool_plan(
            {
                "tool": "chat",
                "message": message
            },
            session,
            memory,
            chroma_store,
            memory_interface.memory_recall,
            service_state,
            effective_user=effective_user,
        )

        return result if isinstance(result, dict) else {"success": True, "tool": "chat"}

    # --------------------------------------------------------
    # ACTION: MAPPED TOOL EXECUTION
    # --------------------------------------------------------
    # Converts playbook action into tool_executor decision
    # using internal action mapping registry.
    # --------------------------------------------------------

    action_handler = _PLAYBOOK_ACTION_MAP.get(action_type)

    if action_handler:
        decision_payload = action_handler(target)

        if decision_payload is None:
            return {"success": True, "tool": "playbook"}

        # ----------------------------------------------------
        # OPTIONAL FIELD ENRICHMENT
        # ----------------------------------------------------
        # Injects playbook-provided context into decision
        # before execution.
        # ----------------------------------------------------

        if message:
            decision_payload["message"] = message

        if payload:
            decision_payload["payload"] = payload

        if message and action_type == "aider":
            decision_payload["instruction"] = message

        # ----------------------------------------------------
        # EXECUTE FINAL DECISION
        # ----------------------------------------------------

        result = orchestrate_tool_plan(
            decision_payload,
            session,
            memory,
            chroma_store,
            memory_interface.memory_recall,
            service_state,
            effective_user=effective_user,
        )

        return result if isinstance(result, dict) else {
            "success": True,
            "tool": decision_payload.get("tool", "playbook"),
        }

    # --------------------------------------------------------
    # UNKNOWN ACTION HANDLING
    # --------------------------------------------------------
    # Safely ignore unsupported playbook actions to avoid
    # breaking automation flow.
    # --------------------------------------------------------

    print(
        f"      [PLAYBOOK WARNING] Unknown action '{action_type}' "
        f"for target '{target}' — skipping step {step_index}."
    )
    return {
        "success": False,
        "tool": "playbook",
        "message": f"Unsupported playbook action: {action_type}",
    }
    
    
    
# ============================================================
# PLAYBOOK ORCHESTRATION ENGINE
# ============================================================
# PURPOSE:
# Executes a full automation playbook from start to finish.
#
# FILE:
# automation_playbooks.py
#
# ROLE:
# High-level controller for sequential workflow execution.
# ============================================================

def run_playbook(
    playbook_name: str,
    session: dict,
    memory: dict,
    *,
    effective_user=None,
) -> dict:
    """
    Execute a full automation playbook.

    This function:
    - Loads a playbook definition
    - Resolves fuzzy name matches
    - Iterates through all steps
    - Delegates execution to run_playbook_step()

    Args:
        playbook_name:
            Name (or partial name) of the playbook to execute.

        session:
            Runtime session state.

        memory:
            Shared memory context.
    """

    # --------------------------------------------------------
    # LOAD PLAYBOOK FROM DISK
    # --------------------------------------------------------
    # Attempts exact match first, then fallback fuzzy match
    # --------------------------------------------------------

    playbook_definition = load_playbook(playbook_name)

    if not playbook_definition:

        available_playbooks = list_playbooks()

        matching_playbooks = [
            playbook_file
            for playbook_file in available_playbooks
            if playbook_name.lower() in playbook_file.lower()
        ]

        if matching_playbooks:
            playbook_definition = load_playbook(matching_playbooks[0])

        if not playbook_definition:
            print(f"AI: Playbook '{playbook_name}' not found.")
            print(
                f"    Available: {', '.join(list_playbooks()) or 'none'}"
            )
            return {
                "success": False,
                "tool": "playbook",
                "message": f"Playbook '{playbook_name}' not found.",
            }

    # --------------------------------------------------------
    # PLAYBOOK HEADER OUTPUT
    # --------------------------------------------------------
    # Displays metadata before execution begins
    # --------------------------------------------------------

    print(f"\n  [PLAYBOOK] Running: {playbook_definition['name']}")

    if playbook_definition.get("description"):
        print(f"  [PLAYBOOK] {playbook_definition['description']}\n")

    # --------------------------------------------------------
    # STEP EXECUTION LOOP
    # --------------------------------------------------------
    # Sequentially processes each automation step
    # --------------------------------------------------------

    for step_index, step in enumerate(playbook_definition.get("steps", []), start=1):

        action_type = step.get("action", "").lower().strip()
        target      = step.get("target", "")
        message     = step.get("message", "")
        payload     = step.get("payload", {})

        print(
            f"  [STEP {step_index}] "
            f"[{action_type}] {target or message}"
        )

        step_result = run_playbook_step(
            step_index,
            action_type,
            target,
            message,
            payload,
            session,
            memory,
            effective_user=effective_user,
        )

        if isinstance(step_result, dict) and step_result.get("success") is False:
            message = step_result.get("message") or "A playbook step did not complete."
            print(f"  [PLAYBOOK] Stopped: {message}")
            return {
                "success": False,
                "tool": "playbook",
                "step": step_index,
                "message": message,
            }

    # --------------------------------------------------------
    # PLAYBOOK COMPLETION
    # --------------------------------------------------------
    # Final status output after workflow finishes
    # --------------------------------------------------------

    print(f"\n  [PLAYBOOK] '{playbook_definition['name']}' complete.")
    return {"success": True, "tool": "playbook"}
    
    

# ============================================================
# PLAYBOOK INTENT PARSER / COMMAND ROUTER
# ============================================================
# PURPOSE:
# Interprets natural language input and routes it to
# automation playbook functions.
#
# FILE:
# automation_playbooks.py
#
# ROLE:
# Lightweight NLP router for playbook-related commands.
# ============================================================

def handle_playbook_intent(
    user_input: str,
    session: dict,
    memory: dict,
    *,
    effective_user=None,
) -> str:
    """
    Parse user input and trigger automation playbook actions.

    Supported commands:
    - list playbooks
    - run/play/execute playbook <name>

    Args:
        user_input:
            Raw user command string.

        session:
            Runtime session state.

        memory:
            Shared memory context.
    """

    # --------------------------------------------------------
    # NORMALIZE INPUT
    # --------------------------------------------------------
    # Standardizes input for pattern matching
    # --------------------------------------------------------

    normalized_input = (user_input or "").lower().strip()

    # --------------------------------------------------------
    # COMMAND: LIST PLAYBOOKS
    # --------------------------------------------------------
    # Displays all available automation workflows
    # --------------------------------------------------------

    if "list" in normalized_input:

        available_playbooks = list_playbooks()

        print("AI: Saved playbooks:")

        for playbook_file in available_playbooks:
            print(f"     {playbook_file}")

        if not available_playbooks:
            print("  (none yet)")

        if not available_playbooks:
            return "Saved playbooks:\n  (none yet)"

        return "Saved playbooks:\n" + "\n".join(
            f"  {playbook_file}"
            for playbook_file in available_playbooks
        )

    # --------------------------------------------------------
    # COMMAND: RUN PLAYBOOK
    # --------------------------------------------------------
    # Extracts playbook name from natural language input
    # --------------------------------------------------------

    match = re.search(
        r"(?:run|execute|start)\s+(?:playbook\s+)?(\S+)",
        normalized_input
    )

    if match:

        playbook_name = match.group(1).strip()

        playbook_result = run_playbook(
            playbook_name,
            session,
            memory,
            effective_user=effective_user,
        )

        if isinstance(playbook_result, dict) and not playbook_result.get("success"):
            return (
                f"Playbook '{playbook_name}' did not complete: "
                f"{playbook_result.get('message') or 'A step failed.'}"
            )

        return f"Playbook '{playbook_name}' complete."

    # --------------------------------------------------------
    # FALLBACK HELP RESPONSE
    # --------------------------------------------------------
    # Guides user toward valid commands
    # --------------------------------------------------------

    help_response = "Commands: 'run playbook <name>' or 'list playbooks'"
    print(f"AI: {help_response}")
    return help_response


TOOL_META = {
    "name": "playbooks",
    "category": "automation",
    "description": "Lists or runs saved automation playbooks.",
    "usage": "list playbooks | run playbook <name>",
    "examples": ["list playbooks", "run playbook daily-check"],
    "options": {
        "list": "show saved playbooks",
        "run <name>": "execute the named playbook",
    },
    "confirmation_required": "depends on the actions in the playbook",
}

register_tool(TOOL_META, handle_playbook_intent)
