"""
Aetheraeon AI - Tool Executor

Purpose:
Validates and executes approved structured tool actions through registered internal and external handlers.

Architecture Layer:
Tool Execution Layer.

Responsibilities:
- Validate tool request shape, parameters, registration, and execution prerequisites.
- Resolve approved tools through the registry and invoke the appropriate execution path.
- Return structured results, receipts, metadata, and errors to calling layers.

Boundaries:
- The executor does not infer intent, select policy, grant permission, or decide which tool the user needs.
- Upstream approval never replaces execution-time security and payload validation.
- Memory operations use approved interfaces, and the planned Cognitive Decision Engine owns future tool-policy decisions.
"""


# ============================================================
# CORE STANDARD LIBRARY IMPORTS
# ============================================================
# Built-in Python modules used for:
# - shell execution
# - filesystem operations
# - process management
# - command validation
# - JSON payload formatting
# - regex parsing
# ============================================================

import os                    # Filesystem + path operations
import re                    # Command parsing / validation
import json                  # Structured payload formatting
import subprocess            # Shell + external process execution
from datetime import datetime  # Timestamp generation for logs/debug


# ============================================================
# EXTERNAL DEPENDENCIES (PIP INSTALLED PACKAGES)
# ============================================================
# Third-party libraries used for:
# - HTTP requests
# - webhook communication
# ============================================================

import requests              # HTTP API + webhook requests


# ============================================================
# INTERNAL SYSTEM IMPORTS (ARCHITECTURE LAYERS)
# ============================================================
# Internal AETHERAEON system modules.
#
# RULES:
# - tool_executor executes actions ONLY
# - No orchestration logic here
# - No database logic here
# - No frontend/UI logic here
#
# This layer acts as:
# "Execution + Action Runtime Layer"
# ============================================================

# SYSTEM SECURITY LAYER
from core.system_security import (
    BLOCKED_SHELL_TOKENS,
    READ_ONLY_SHELL_COMMANDS,
    WRITE_ALLOWED_SHELL_COMMANDS,
    validate_command_security,
    sanitize_file_path,
)

# ------------------------------------------------------------
# SYSTEM LOGGER
# Centralized logging / debugging system
# ------------------------------------------------------------
from core import system_logger


# ------------------------------------------------------------
# CONFIGURATION SYSTEM
# Centralized environment + runtime configuration
# ------------------------------------------------------------
from core import config_loader
from core import config_manager
from core import system_security
# ------------------------------------------------------------
# SYSTEM PATH MANAGEMENT
# Centralized filesystem path definitions
# ------------------------------------------------------------
from core import system_paths
from core import system_utils

# ------------------------------------------------------------
# EXTERNAL TOOLKIT
# Shared external integrations + helper execution tools
# ------------------------------------------------------------
from core import external_toolkit
from core.tool_registry import register_tool


def _execution_authorization_valid(tool_name, effective_user, authorization):
    """Validate an Access Control receipt without making a policy decision."""

    context = effective_user if isinstance(effective_user, dict) else {}
    receipt = authorization if isinstance(authorization, dict) else {}
    return bool(
        receipt.get("authorized")
        and receipt.get("tool") == str(tool_name or "").strip().lower()
        and receipt.get("effective_user_id")
        and receipt.get("effective_user_id") == str(context.get("user_id") or "").strip()
    )


def _authorization_denied_result(tool_name):
    """Return a stable execution-boundary denial without exposing identities."""

    return {
        "success": False,
        "tool": tool_name,
        "message": "Administrator permission is required for that tool.",
        "error": "authorization_denied",
    }


# ============================================================
# DEFAULT AIDER MODEL CONFIGURATION
# ============================================================
# Defines the default AI model used by the Aider code-editing
# system when no override model is specified.
#
# FORMAT:
#   ollama/<model_name>
#
# EXAMPLES:
#   ollama/qwen2.5-coder:14b
#   ollama/deepseek-coder:33b
#   gpt-4o
#
# PURPOSE:
# - Centralized default model selection
# - Easy future model swapping
# - Prevents hardcoded model strings throughout system
# ============================================================

DEFAULT_AIDER_MODEL = "ollama/qwen2.5-coder:14b"


# ============================================================
# WEB COMMAND ROUTER (SETTINGS + TOOL SIGNAL GENERATION)
# ============================================================
# PURPOSE:
# Interprets user "web control commands" and either:
# - updates system web settings
# - or returns a structured tool request
#
# This function does NOT execute web searches directly.
# It ONLY routes intent to system components.
# ============================================================

def handle_web_command(user_input):
    """
    Web Command Interface

    Supported Commands:
    - web on
    - web off
    - web search <query>
    - web provider google | ddg
    """

    # --------------------------------------------------------
    # LOAD CURRENT SYSTEM SETTINGS
    # --------------------------------------------------------
    # PURPOSE:
    # Retrieve current web search configuration so we can
    # modify or query it safely.
    # --------------------------------------------------------

    system_settings = config_manager.load_settings()
    web_search_settings = system_settings.get("web_search", {}) or {}

    normalized_input = (user_input or "").strip().lower()

    # ========================================================
    # ENABLE WEB SEARCH
    # ========================================================

    if normalized_input == "web on":

        web_search_settings["enabled"] = True
        system_settings["web_search"] = web_search_settings

        config_manager.save_settings(system_settings)

        print("AI: web_search -> ENABLED")
        return {"status": "web_search_enabled"}

    # ========================================================
    # DISABLE WEB SEARCH
    # ========================================================

    if normalized_input == "web off":

        web_search_settings["enabled"] = False
        system_settings["web_search"] = web_search_settings

        config_manager.save_settings(system_settings)

        print("AI: web_search -> DISABLED")
        return {"status": "web_search_disabled"}

    # ========================================================
    # WEB SEARCH TOOL REQUEST
    # ========================================================

    if normalized_input.startswith("web search "):

        search_query = user_input.strip()[len("web search "):].strip()

        if not search_query:
            print("AI: Usage → web search <query>")
            return {"error": "missing_query"}

        # ----------------------------------------------------
        # TOOL EXECUTION SIGNAL
        # ----------------------------------------------------
        # PURPOSE:
        # Instead of executing search here, we return a structured
        # request for tool_executor to handle safely.
        # ----------------------------------------------------

        return {
            "tool": "web_search",
            "query": search_query,
            "max_results": web_search_settings.get("max_results", 5)
        }

    # ========================================================
    # SWITCH WEB SEARCH PROVIDER
    # ========================================================

    provider_match = re.match(
        r"web\s+provider\s+(google|ddg)\s*$",
        user_input.strip(),
        re.IGNORECASE
    )

    if provider_match:

        provider_value = provider_match.group(1).lower()

        web_search_settings["provider"] = (
            "google_cse" if provider_value == "google" else "ddg"
        )

        system_settings["web_search"] = web_search_settings
        config_manager.save_settings(system_settings)

        print(f"AI: web_search provider -> {provider_value}")
        return {"status": "provider_updated", "provider": provider_value}

    # ========================================================
    # INVALID COMMAND HELP RESPONSE
    # ========================================================

    print(
        "AI: Web commands available → "
        "web on | web off | web search <query> | web provider google|ddg"
    )

    return {"error": "invalid_web_command"}
    
    
# ============================================================
# AIDER PROJECT SESSION STATE
# ============================================================
# Store the currently active Aider project path
# inside the user's active runtime session.
#
# This allows the executor layer to remember
# which project directory Aider should operate on.
# ============================================================

def set_aider_project(
    session: dict,
    project_path: str,
) -> None:
    """
    Store the active Aider project path in session state.

    Parameters:
    - session:
        Active runtime session dictionary

    - project_path:
        Absolute or normalized project directory path
    """

    # ========================================================
    # SESSION STATE UPDATE
    # ========================================================
    # Persist active Aider project location for
    # future execution calls.
    # ========================================================

    session["aider_project"] = project_path


# ============================================================
# AIDER PROJECT SESSION RETRIEVAL
# ============================================================
# Retrieve the currently active Aider project path
# from the user's active runtime session.
#
# This is used by the execution layer to determine
# which project directory Aider should operate within.
# ============================================================

def get_aider_project(
    session: dict,
) -> str | None:
    """
    Retrieve the active Aider project path from session state.

    Parameters:
    - session:
        Active runtime session dictionary

    Returns:
    - Project path string if configured
    - None if no active project exists
    """

    # ========================================================
    # SESSION STATE LOOKUP
    # ========================================================
    # Return the stored Aider project path safely.
    # ========================================================

    return session.get("aider_project")


# ============================================================
# SHELL COMMAND EXECUTION
# ============================================================
# Execute validated operating system shell commands.
#
# RESPONSIBILITIES:
# - Validate command safety
# - Execute approved shell commands
# - Handle explorer path launching
# - Capture command output
# - Maintain lightweight session state
#
# IMPORTANT:
# This function is EXECUTION ONLY.
# No AI reasoning or orchestration belongs here.
# ============================================================

def run_shell(
    cmd: str,
    session: dict,
    *,
    effective_user=None,
    authorization=None,
) -> dict:
    """
    Execute a validated shell command safely.

    Parameters:
    - cmd:
        Raw shell command string

    - session:
        Active runtime session state

    Returns:
    - Structured execution result dictionary
    """

    if not _execution_authorization_valid(
        "shell", effective_user, authorization
    ):
        return _authorization_denied_result("shell")

    # ========================================================
    # COMMAND NORMALIZATION
    # ========================================================
    # Clean incoming command formatting before validation.
    # ========================================================

    command = normalize_shell_command(cmd, session=session)

    if not command:

        return {
            "success": False,
            "tool": "shell",
            "message": "No command provided.",
        }

    # ========================================================
    # SECURITY VALIDATION
    # ========================================================
    # Prevent unsafe or restricted command execution.
    # ========================================================

    if not validate_command_security(
        command,
        session=session,
    ):

        return {
            "success": False,
            "tool": "shell",
            "message": (
                f"Blocked unsafe command: {command}"
            ),
        }

    print(f"[SHELL] EXECUTE -> {command}")

    # ========================================================
    # WINDOWS EXPLORER HANDLING
    # ========================================================
    # Special-case handling for opening folders/files
    # in Windows Explorer.
    # ========================================================

    if command.lower().startswith("explorer"):

        target_path = (
            system_security.sanitize_file_path(command)
            or os.getcwd()
        )

        try:

            subprocess.Popen(
                ["explorer", target_path],
                shell=False,
            )

            # ------------------------------------------------
            # Lightweight runtime session tracking
            # ------------------------------------------------

            session["cwd"] = target_path
            session["last_command"] = (
                f'explorer "{target_path}"'
            )

            return {
                "success": True,
                "tool": "shell",
                "message": (
                    f"Opened Explorer at: {target_path}"
                ),
                "path": target_path,
            }

        except Exception as error:

            return {
                "success": False,
                "tool": "shell",
                "message": (
                    f"Explorer execution failed: {error}"
                ),
            }

    # ========================================================
    # STANDARD SHELL EXECUTION
    # ========================================================
    # Execute normal shell commands through subprocess.
    # ========================================================

    try:

        execution_result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
        )

        # ----------------------------------------------------
        # Output normalization
        # ----------------------------------------------------

        command_output = (
            execution_result.stdout.strip()
            or execution_result.stderr.strip()
        )

        # ----------------------------------------------------
        # Directory listing cleanup
        # ----------------------------------------------------

        if (
            command.lower().startswith("dir")
            and "<DIR>" in command_output
        ):

            cleaned_output = system_utils.clean_dir_output(
                command_output
            )

        else:

            cleaned_output = command_output

        # ----------------------------------------------------
        # Lightweight runtime session tracking
        # ----------------------------------------------------

        session["last_listing"] = cleaned_output

        # ----------------------------------------------------
        # Detect directory navigation references
        # ----------------------------------------------------

        detected_path_match = re.search(
            r'"([A-Za-z]:\\[^"]+)"',
            command,
        )

        if detected_path_match:

            detected_path = system_security.sanitize_file_path(
                detected_path_match.group(1)
            )

            if detected_path:

                session["cwd"] = detected_path

        command_verb = command.lower().split(maxsplit=1)[0]
        execution_succeeded = (
            0 <= execution_result.returncode <= 7
            if command_verb == "robocopy"
            else execution_result.returncode == 0
        )

        return {
            "success": execution_succeeded,
            "tool": "shell",
            "command": command,
            "output": cleaned_output,
            "return_code": execution_result.returncode,
        }

    # ========================================================
    # TIMEOUT HANDLING
    # ========================================================
    # Prevent runaway shell execution.
    # ========================================================

    except subprocess.TimeoutExpired:

        return {
            "success": False,
            "tool": "shell",
            "message": "Shell command timed out.",
        }

    # ========================================================
    # GENERAL EXECUTION FAILURE
    # ========================================================
    # Catch unexpected subprocess/system errors safely.
    # ========================================================

    except Exception as error:

        return {
            "success": False,
            "tool": "shell",
            "message": f"Shell execution failed: {error}",
        }



# ============================================================
# AIDER EXECUTION ENGINE
# ============================================================
# Execute Aider AI-assisted code editing sessions.
#
# RESPONSIBILITIES:
# - Resolve project/file locations
# - Build Aider CLI execution command
# - Launch Aider subprocess safely
# - Stream output live to terminal
# - Return structured execution results
#
# IMPORTANT:
# This function is EXECUTION ONLY.
# No orchestration, memory logic, or AI reasoning belongs here.
# ============================================================

def run_aider(
    file_name: str,
    instruction: str,
    session: dict,
    approved: bool | None = None,
    *,
    effective_user=None,
    authorization=None,
) -> dict:
    """
    Execute an Aider code editing session.

    Parameters:
    - file_name:
        Target file for editing

    - instruction:
        Natural-language code editing request

    - session:
        Active runtime session state

    - approved:
        Execution approval state
            True  -> auto approve
            False -> cancel immediately
            None  -> ask terminal confirmation

    Returns:
    - Structured execution result dictionary
    """

    if not _execution_authorization_valid(
        "aider", effective_user, authorization
    ):
        return _authorization_denied_result("aider")

    # ========================================================
    # AIDER AVAILABILITY CHECK
    # ========================================================
    # Ensure Aider is installed and available before execution.
    # ========================================================

    if not shutil.which("aider"):

        return {
            "success": False,
            "tool": "aider",
            "message": (
                "Aider is not installed. "
                "Install using: pip install aider-chat"
            ),
        }

    # ========================================================
    # ACTIVE PROJECT RESOLUTION
    # ========================================================
    # Retrieve active Aider project workspace from session.
    # ========================================================

    aider_project_path = get_aider_project(session)

    # ========================================================
    # FILE VALIDATION
    # ========================================================
    # Aider requires a target file path.
    # ========================================================

    if not file_name:

        return {
            "success": False,
            "tool": "aider",
            "message": (
                "No filename provided. "
                "Example: aider fix app.py"
            ),
        }

    # ========================================================
    # FULL FILE PATH RESOLUTION
    # ========================================================
    # Build absolute working file path safely.
    # ========================================================

    if (
        aider_project_path
        and not os.path.isabs(file_name)
    ):

        full_file_path = os.path.join(
            aider_project_path,
            file_name,
        )

    else:

        full_file_path = file_name

    # ========================================================
    # DEFAULT INSTRUCTION FALLBACK
    # ========================================================
    # Provide safe fallback behavior if instruction missing.
    # ========================================================

    aider_instruction = (
        instruction
        or "Review and improve code quality."
    )

    # ========================================================
    # WORKING DIRECTORY RESOLUTION
    # ========================================================
    # Determine subprocess execution directory.
    # ========================================================

    execution_directory = (
        aider_project_path
        or os.path.dirname(full_file_path)
        or os.getcwd()
    )

    # ========================================================
    # EXECUTION PLAN OUTPUT
    # ========================================================
    # Display execution context before launch.
    # ========================================================

    print()
    print("┌─ AIDER EXECUTION PLAN ─────────────────────")
    print(f"│ File:        {full_file_path}")
    print(f"│ Project:     {execution_directory}")
    print(f"│ Model:       {DEFAULT_AIDER_MODEL or 'default'}")
    print(f"│ Instruction: {aider_instruction}")
    print("└────────────────────────────────────────────")

    if not os.path.exists(full_file_path):

        print(
            "[AIDER] File does not exist. "
            "Aider may create it."
        )

    # ========================================================
    # EXECUTION APPROVAL HANDLING
    # ========================================================
    # Optional human approval safety layer.
    # ========================================================

    if approved is False:

        return {
            "success": False,
            "tool": "aider",
            "message": (
                "Aider execution cancelled."
            ),
        }

    if approved is None:

        try:

            confirmation = (
                input("Approve execution? [y/N] -> ")
                .strip()
                .lower()
            )

        except (EOFError, KeyboardInterrupt):

            return {
                "success": False,
                "tool": "aider",
                "message": (
                    "Aider execution cancelled."
                ),
            }

        if confirmation not in ("y", "yes"):

            return {
                "success": False,
                "tool": "aider",
                "message": (
                    "Aider execution cancelled."
                ),
            }

    # ========================================================
    # AIDER COMMAND CONSTRUCTION
    # ========================================================
    # Build CLI execution command safely.
    # ========================================================

    aider_command = [
        "aider",
        full_file_path,
        "--yes",
        "--message",
        aider_instruction,
    ]

    if DEFAULT_AIDER_MODEL:

        aider_command.extend([
            "--model",
            DEFAULT_AIDER_MODEL,
        ])

    print(
        f"\n[AIDER] EXECUTE → "
        f"{' '.join(aider_command[:4])} ..."
    )

    # ========================================================
    # SUBPROCESS ENVIRONMENT SETUP
    # ========================================================
    # Improve subprocess stability for web/server environments.
    # ========================================================

    try:

        child_environment = os.environ.copy()

        child_environment.setdefault("TERM", "dumb")
        child_environment.setdefault("NO_COLOR", "1")
        child_environment.setdefault("PYTHONUTF8", "1")
        child_environment.setdefault(
            "PYTHONIOENCODING",
            "utf-8",
        )

        # ====================================================
        # AIDER PROCESS EXECUTION
        # ====================================================
        # Launch subprocess and stream output live.
        # ====================================================

        aider_process = subprocess.Popen(
            aider_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
            text=True,
            cwd=execution_directory,
            env=child_environment,
        )

        execution_output_lines = []

        # ----------------------------------------------------
        # Live output streaming
        # ----------------------------------------------------

        for output_line in aider_process.stdout:

            print(output_line, end="", flush=True)

            execution_output_lines.append(
                output_line
            )

        aider_process.wait(timeout=300)

        # ====================================================
        # SUCCESS RESULT
        # ====================================================

        if aider_process.returncode == 0:

            session["last_edited_file"] = (
                full_file_path
            )

            session["last_aider_task"] = (
                aider_instruction
            )

            return {
                "success": True,
                "tool": "aider",
                "file": full_file_path,
                "instruction": aider_instruction,
                "output": "".join(
                    execution_output_lines
                ),
            }

        # ====================================================
        # NON-ZERO EXIT RESULT
        # ====================================================

        return {
            "success": False,
            "tool": "aider",
            "message": (
                f"Aider exited with code "
                f"{aider_process.returncode}"
            ),
            "output": "".join(
                execution_output_lines
            ),
        }

    # ========================================================
    # EXECUTABLE NOT FOUND
    # ========================================================

    except FileNotFoundError:

        return {
            "success": False,
            "tool": "aider",
            "message": (
                "Aider executable not found."
            ),
        }

    # ========================================================
    # PROCESS TIMEOUT
    # ========================================================

    except subprocess.TimeoutExpired:

        aider_process.kill()

        return {
            "success": False,
            "tool": "aider",
            "message": (
                "Aider execution timed out "
                "(5 minute limit)."
            ),
        }

    # ========================================================
    # GENERAL EXECUTION FAILURE
    # ========================================================

    except Exception as error:

        return {
            "success": False,
            "tool": "aider",
            "message": (
                f"Aider execution failed: {error}"
            ),
        }


# ============================================================
# N8N WEBHOOK EXECUTION
# ============================================================
# Execute outbound n8n automation webhooks.
#
# RESPONSIBILITIES:
# - Validate webhook execution request
# - Build webhook endpoint URL
# - Send structured JSON payload
# - Capture webhook response safely
# - Return normalized execution results
#
# IMPORTANT:
# This function is EXECUTION ONLY.
# No orchestration, memory logic, or AI reasoning belongs here.
# ============================================================

def run_n8n(
    webhook_path: str,
    payload: dict,
    *,
    effective_user=None,
    authorization=None,
) -> dict:
    """
    Execute an n8n webhook request.

    Parameters:
    - webhook_path:
        Relative n8n webhook endpoint path

    - payload:
        JSON payload dictionary to send

    Returns:
    - Structured execution result dictionary
    """

    if not _execution_authorization_valid(
        "n8n", effective_user, authorization
    ):
        return _authorization_denied_result("n8n")

    # ========================================================
    # WEBHOOK PATH VALIDATION
    # ========================================================
    # n8n execution requires a valid webhook route.
    # ========================================================

    if not webhook_path:

        return {
            "success": False,
            "tool": "n8n",
            "message": (
                "No webhook path provided."
            ),
        }

    # ========================================================
    # WEBHOOK URL CONSTRUCTION
    # ========================================================
    # Build full outbound webhook URL safely.
    # ========================================================

    webhook_url = (
        f"{N8N_URL}/webhook/{webhook_path}"
    )

    print(
        f"[N8N] EXECUTE → POST {webhook_url}"
    )

    print(
        f"[N8N] PAYLOAD → "
        f"{json.dumps(payload, indent=2)}"
    )

    # ========================================================
    # WEBHOOK EXECUTION
    # ========================================================
    # Send outbound POST request to n8n instance.
    # ========================================================

    try:

        response = requests.post(
            webhook_url,
            json=payload,
            timeout=15,
        )

        response_preview = response.text[:500]

        print(
            f"[N8N] RESPONSE ← "
            f"{response.status_code}"
        )

        # ====================================================
        # SUCCESS RESPONSE
        # ====================================================

        return {
            "success": (
                200 <= response.status_code < 300
            ),
            "tool": "n8n",
            "status_code": response.status_code,
            "webhook": webhook_path,
            "response": response_preview,
        }

    # ========================================================
    # CONNECTION FAILURE
    # ========================================================
    # Triggered when n8n instance cannot be reached.
    # ========================================================

    except requests.exceptions.ConnectionError:

        return {
            "success": False,
            "tool": "n8n",
            "message": (
                f"Unable to connect to n8n at "
                f"{N8N_URL}"
            ),
        }

    # ========================================================
    # REQUEST TIMEOUT
    # ========================================================
    # Prevent hanging webhook requests.
    # ========================================================

    except requests.exceptions.Timeout:

        return {
            "success": False,
            "tool": "n8n",
            "message": (
                "n8n webhook request timed out."
            ),
        }

    # ========================================================
    # GENERAL REQUEST FAILURE
    # ========================================================
    # Catch unexpected execution/network failures safely.
    # ========================================================

    except Exception as error:

        return {
            "success": False,
            "tool": "n8n",
            "message": (
                f"n8n execution failed: {error}"
            ),
        }


TOOL_META = [
    {
        "name": "navigation",
        "category": "navigation",
        "description": "Opens or lists local folders and files.",
        "usage": "open <path> | open that folder | show files in <path> | dir <path> | tree <path>",
        "examples": ["open H:\\AISystem", "show files in H:\\AISystem", "tree H:\\AISystem"],
        "command_words": ["open", "show", "list"],
        "confirmation_required": False,
    },
    {
        "name": "aider",
        "category": "code",
        "description": "Sets an Aider project or requests an AI-assisted code change.",
        "usage": "aider project <path> | aider <change request>",
        "examples": ["aider project H:\\AISystem", "aider add logging to app.py"],
        "confirmation_required": True,
    },
    {
        "name": "web",
        "category": "web",
        "description": "Controls or invokes the configured web search provider.",
        "usage": "web on|off | web search <query> | web provider google|ddg",
        "examples": ["web on", "web search current Python release"],
        "options": ["on", "off", "provider google", "provider ddg"],
        "confirmation_required": False,
    },
    {
        "name": "shell",
        "category": "system",
        "description": "Runs commands permitted by the existing shell safety policy.",
        "usage": "<permitted shell command>",
        "examples": ["whoami", "systeminfo", "ipconfig", "dir H:\\AISystem"],
        "options": READ_ONLY_SHELL_COMMANDS + WRITE_ALLOWED_SHELL_COMMANDS,
        "confirmation_required": "required for permitted write operations",
    },
    {
        "name": "n8n",
        "category": "automation",
        "description": "Triggers a configured n8n workflow.",
        "usage": "trigger workflow <name>",
        "examples": ["trigger workflow daily-report"],
        "confirmation_required": "depends on the workflow action",
    },
]


def is_supported_shell_command(command: str) -> bool:
    """Return whether input begins with a recognized shell command."""

    normalized_command = normalize_shell_command(command).lower()
    if not normalized_command:
        return False

    command_match = re.match(
        r'^"([^"]+)"|^([^\s&|<>;]+)',
        normalized_command,
    )
    command_token = next(
        (group for group in command_match.groups() if group),
        "",
    ) if command_match else ""
    command_verb = re.split(r"[\\/]", command_token)[-1]
    if command_verb.endswith(".exe"):
        command_verb = command_verb[:-4]
    return command_verb in (
        READ_ONLY_SHELL_COMMANDS
        + WRITE_ALLOWED_SHELL_COMMANDS
        + BLOCKED_SHELL_TOKENS
    )


def normalize_shell_command(command: str, session: dict | None = None) -> str:
    """Translate supported navigation phrases into existing shell commands."""

    raw_command = (command or "").strip()
    lowered = raw_command.lower()

    if lowered.startswith("show files in "):
        return "dir " + raw_command[len("show files in "):].strip()

    if lowered == "show files":
        target = (session or {}).get("cwd")
        return f'dir "{target}"' if target else "dir"

    if lowered.startswith("open "):
        target = raw_command[len("open "):].strip()
        if target.lower() in ("that folder", "the folder", "folder"):
            target = (session or {}).get("cwd") or ""
        return f'explorer "{target}"' if target else "explorer"

    if lowered == "time":
        return "time /t"

    if lowered == "date":
        return "date /t"

    return raw_command

for tool_meta in TOOL_META:
    handler = {
        "navigation": run_shell,
        "aider": run_aider,
        "web": handle_web_command,
        "shell": run_shell,
        "n8n": run_n8n,
    }[tool_meta["name"]]
    register_tool(tool_meta, handler)
