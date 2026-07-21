"""
Aetheraeon AI - System Health Monitor

Purpose:
Checks the operational availability and readiness of services required by the current Aetheraeon runtime.

Architecture Layer:
Service Infrastructure Layer - diagnostics and health monitoring.

Responsibilities:
- Report readiness for configured models, databases, memory storage, services, and integrations.
- Return structured health and startup diagnostic information.
- Support operational monitoring without changing the systems being observed.

Boundaries:
- Health checks are passive and do not perform reasoning, route user requests, authorize actions, or repair services automatically.
- Future monitoring and dashboard capabilities remain planned until separately implemented.
"""

# ============================================================
# CHROMADB GLOBAL RUNTIME OBJECTS
# ============================================================
# PURPOSE:
# Stores active ChromaDB runtime references after successful
# initialization during system startup.
#
# These globals are shared across the memory subsystem to
# avoid repeated database initialization calls.
#
# VARIABLES:
# - CHROMA_AVAILABLE  -> overall memory system availability
# - CHROMA_CLIENT     -> active ChromaDB client instance
# - CHROMA_COLLECTION -> active vector collection reference
# ============================================================

CHROMA_AVAILABLE = False

CHROMA_CLIENT = None

CHROMA_COLLECTION = None
  

# ============================================================
# CORE STANDARD LIBRARY IMPORTS
# ============================================================
# These are built-in Python modules used for:
# - process management
# - networking
# - startup timing
# - operating system interaction
# - runtime diagnostics
# ============================================================

import os                    # Filesystem + environment access
import time                  # Startup timing and retry delays
import socket                # Local/LAN IP detection
import subprocess            # Launching external services/processes


# ============================================================
# EXTERNAL DEPENDENCIES (PIP INSTALLED PACKAGES)
# ============================================================
# Third-party runtime dependencies used for:
# - HTTP service health checks
# - AI backend communication
# - vector memory systems
# ============================================================

import requests              # HTTP requests for subsystem health validation
import ollama                # Ollama local AI backend interface


# ============================================================
# INTERNAL SYSTEM IMPORTS (ARCHITECTURE LAYERS)
# ============================================================
# Internal architecture dependencies required for:
# - configuration access
# - system path resolution
# - model selection state
# - runtime startup validation
#
# RULES:
# - ONLY import architecture layers here
# - DO NOT execute startup logic in import section
# - DO NOT place runtime code here
# ============================================================

# ------------------------------------------------------------
# CONFIGURATION LAYER
# ------------------------------------------------------------
# Centralized system configuration loading and constants
# ------------------------------------------------------------

from core import config_loader
from core.config_manager import VERSION
from core import memory_database
from core import tool_executor
from core.tool_registry import register_tool

# ------------------------------------------------------------
# SYSTEM PATH LAYER
# ------------------------------------------------------------
# Centralized filesystem + installation path management
# ------------------------------------------------------------

from core.system_paths import (
    AISYSTEM_ROOT,
    N8N_PATH,
)

# ------------------------------------------------------------
# MODEL REGISTRY LAYER
# ------------------------------------------------------------
# Access to active/default AI model configuration
# ------------------------------------------------------------

from core import model_registry

# ============================================================
# SERVICE ORCHESTRATION LAYER
# ============================================================
# Runtime service control (start/check/stop coordination)
# ============================================================
from core.service_registry import register_service
from core.service_manager import shutdown_all
from core.service_manager import check_all
from core.service_manager import service_state, format_status
from core.memory_database import check_chromadb, get_chroma_collection

# ============================================================
# SYSTEM STARTUP BANNER
# ============================================================
# PURPOSE:
# Displays the initial boot banner for the Aetheraeon system.
# This is the first visible output when the system initializes.
# ============================================================

def startup_banner():
    """
    Startup Banner Display
    ----------------------
    Prints a formatted system initialization header to the console.
    Used to signal that the AI system is booting and subsystems
    are beginning initialization.
    """

    # --------------------------------------------------------
    # MAIN HEADER OUTPUT
    # --------------------------------------------------------
    # Displays system name, version, and visual separator
    # for startup clarity in terminal logs.
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print(f"  AETHERAEON v{VERSION} — AI SYSTEM CONTROLLER")
    print("=" * 60)

    # --------------------------------------------------------
    # INITIALIZATION STATUS MESSAGE
    # --------------------------------------------------------
    # Indicates that system subsystems are being loaded.
    # Helps track startup progression during boot sequence.
    # --------------------------------------------------------

    print("   Initializing all subsystems...")

    # --------------------------------------------------------
    # FOOTER SEPARATOR
    # --------------------------------------------------------
    # Visual break for clean terminal formatting.
    # --------------------------------------------------------

    print("-" * 60)



# ============================================================
# OLLAMA SERVICE HEALTH CHECK
# ============================================================
# PURPOSE:
# Validates that the local Ollama LLM server is running and
# confirms whether the required model is available.
#
# This is critical for AI inference functionality.
# ============================================================

def check_ollama():
    """
    Ollama Availability Check
    -------------------------
    - Pings local Ollama API server
    - Validates service availability
    - Checks installed models
    - Confirms required model presence
    """

    try:
        # ----------------------------------------------------
        # API HEALTH CHECK REQUEST
        # ----------------------------------------------------
        # Sends a lightweight request to Ollama's tag endpoint
        # to confirm service is running and responsive.
        # ----------------------------------------------------

        response = requests.get(
            "http://localhost:11434/api/tags",
            timeout=5
        )

        # ----------------------------------------------------
        # SUCCESS PATH — OLLAMA IS ONLINE
        # ----------------------------------------------------

        if response.status_code == 200:

            # Extract available model names safely
            available_models = [
                model.get("name")
                for model in response.json().get("models", [])
                if model.get("name")
            ]

            # Mark system as healthy
            service_state["ollama"]["status"] = True

            # ------------------------------------------------
            # MODEL VALIDATION CHECK
            # ------------------------------------------------
            # Ensures required model exists in local Ollama
            # installation before AI system proceeds.
            # ------------------------------------------------

            required_model_base = router_model.split(":")[0]

            if any(required_model_base in model for model in available_models):
                print(f"  [OK]   Ollama  -> {router_model} ready")
            else:
                print(
                    f"  [WARN] Ollama up but '{router_model}' not found.\n"
                    f"         Available: {', '.join(available_models)}"
                )

        else:
            # ------------------------------------------------
            # SERVICE RESPONDING BUT NOT HEALTHY
            # ------------------------------------------------
            service_state["ollama"]["status"] = False
            print("  [FAIL] Ollama  -> not responding correctly")

    except Exception:
        # ----------------------------------------------------
        # SERVICE NOT RUNNING OR UNREACHABLE
        # ----------------------------------------------------

        service_state["ollama"]["status"] = False
        print("  [FAIL] Ollama  -> not running (start: ollama serve)")
   
        

# ============================================================
# N8N WORKFLOW ENGINE HEALTH CHECK + AUTO-START
# ============================================================
# PURPOSE:
# Validates that the n8n automation engine is running.
# If not running, attempts to automatically start it and
# verifies successful boot within a retry window.
#
# This system enables workflow automation + webhook execution.
# ============================================================

def check_n8n():
    """
    N8N Service Health Monitor
    --------------------------
    - Checks if n8n is reachable via health endpoint
    - Attempts automatic startup if not running
    - Retries until service becomes available
    - Updates global system status
    """

    # --------------------------------------------------------
    # GLOBAL SYSTEM STATE ACCESS
    # --------------------------------------------------------

    global service_state

    # --------------------------------------------------------
    # PHASE 1 — INITIAL HEALTH CHECK
    # --------------------------------------------------------
    # Primary truth source is PORT (not subprocess, not timing)
    # --------------------------------------------------------

    try:

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        port_result = sock.connect_ex(("127.0.0.1", 5678))
        sock.close()

        if port_result == 0:
            # Optional confirmation via health endpoint
            try:
                response = requests.get(
                    f"{N8N_URL}/healthz",
                    timeout=3
                )

                if response.status_code == 200:
                    service_state["n8n"]["status"] = True
                    print(f"  [OK]   n8n -> running at {N8N_URL}")
                    return

            except Exception:
                # Port is open = still considered running
                service_state["n8n"]["status"] = True
                print(f"  [OK]   n8n -> running at {N8N_URL} (port confirmed)")
                return

    except Exception:
        # Service not reachable — proceed to recovery
        pass

    # --------------------------------------------------------
    # PHASE 2 — AUTO START ATTEMPT
    # --------------------------------------------------------
    # If service is offline, attempt to start n8n via CLI.
    # --------------------------------------------------------

    print("  [INFO] n8n -> not running, attempting startup...")

    try:

        # ----------------------------------------------------
        # START PROCESS (WINDOWS-SAFE)
        # ----------------------------------------------------
        process = subprocess.Popen(
            "npx n8n start",
            cwd=AISYSTEM_ROOT,
            shell=True,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        
        register_service("n8n", process)
        
        # ----------------------------------------------------
        # PHASE 3 — BOOT VERIFICATION LOOP
        # ----------------------------------------------------
        # Wait for port to become available (REAL truth source)
        # ----------------------------------------------------

        for _ in range(12):
            time.sleep(5)

            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex(("127.0.0.1", 5678))
                sock.close()

                if result == 0:
                    service_state["n8n"]["status"] = True
                    print("  [OK]   n8n -> started successfully (port open)")
                    return

            except Exception:
                pass

        # ----------------------------------------------------
        # BOOT FAILED (PORT NEVER OPENED)
        # ----------------------------------------------------

        service_state["n8n"]["status"] = False
        print("  [WARN] n8n -> started but not responding yet")

        # ----------------------------------------------------
        # DEBUG ONLY ON FAILURE
        # ----------------------------------------------------

        try:
            import shutil

            print("  [DEBUG] cwd =", AISYSTEM_ROOT)
            print("  [DEBUG] npx =", shutil.which("npx"))
            print("  [DEBUG] node =", shutil.which("node"))

        except Exception:
            pass

    except Exception as error:
        # ----------------------------------------------------
        # GENERAL STARTUP FAILURE
        # ----------------------------------------------------

        service_state["n8n"]["status"] = False
        print(f"  [FAIL] n8n -> startup error: {error}")
        

def check_aider():
    global service_state
    try:
        res = subprocess.run(["aider","--version"], capture_output=True, text=True, timeout=10)
        ver = res.stdout.strip() or res.stderr.strip()
        service_state["aider"]["status"] = True
        print(f"  [OK]   Aider   -> {ver or 'installed'}")
    except FileNotFoundError:
        print(f"  [FAIL] Aider   -> not installed  (pip install aider-chat)")
    except Exception as e:
        print(f"  [FAIL] Aider   -> {e}")

    
# ============================================================
# SYSTEM STATUS REPORTING
# ============================================================
# Generates a formatted runtime status summary for:
# - subsystem health
# - service availability
# - active Aider project state
# - ChromaDB memory statistics
#
# NOTE:
# This function belongs in:
#   system_health_check.py
#
# Reason:
# This is operational/runtime monitoring logic,
# not logging behavior.
# ============================================================

def print_status(active_session):
    """
    Build a formatted runtime system status report.

    Returns:
        str:
            Multi-line formatted status summary.
    """

    # --------------------------------------------------------
    # Initialize output container
    # --------------------------------------------------------
    # The function returns text instead of printing directly
    # so both:
    # - API responses
    # - CLI output
    # can reuse the same formatter.
    # --------------------------------------------------------

    check_all(start_if_offline=False)

    status_lines = ["SYSTEM STATUS:"]

    # --------------------------------------------------------
    # Human-readable subsystem state labels
    # --------------------------------------------------------

    status_labels = {
        True:  "[Online]",
        False: "[Offline]",
    }

    # --------------------------------------------------------
    # Render subsystem health states
    # --------------------------------------------------------
    # Example:
    #   [Online]  ollama      online
    #   [Offline] n8n         offline
    # --------------------------------------------------------

    for subsystem_name, subsystem_state_record in service_state.items():

        if isinstance(subsystem_state_record, dict):
            subsystem_online = bool(
                subsystem_state_record.get("status", False)
            )
        else:
            subsystem_online = bool(subsystem_state_record)

        subsystem_label = status_labels[subsystem_online]

        subsystem_state = (
            "online"
            if subsystem_online
            else "offline"
        )

        status_lines.append(
            f"  {subsystem_label}  "
            f"{subsystem_name.ljust(12)} "
            f"{subsystem_state}"
        )

        if isinstance(subsystem_state_record, dict):
            state_reason = subsystem_state_record.get(
                "meta", {}
            ).get("reason")
            if state_reason:
                status_lines[-1] += f" ({state_reason})"

    # --------------------------------------------------------
    # Active Aider project context
    # --------------------------------------------------------
    # If an Aider project is currently attached to the
    # session, include it in the status report.
    # --------------------------------------------------------

    aider_project_path = tool_executor.get_aider_project(
        active_session
    )

    if aider_project_path:

        status_lines.append(
            f"  Aider Project: {aider_project_path}"
        )

    # --------------------------------------------------------
    # ChromaDB memory statistics
    # --------------------------------------------------------
    # Include memory record count if ChromaDB is online.
    # --------------------------------------------------------

    if memory_database.CHROMA_AVAILABLE:

        try:

            chroma_collection = memory_database.get_chroma_collection()

            memory_record_count = chroma_collection.count()

            status_lines.append(
                f"  ChromaDB Records: "
                f"{memory_record_count}"
            )

        except Exception:

            # ------------------------------------------------
            # Silent fail:
            # status reporting should never crash the system.
            # ------------------------------------------------

            pass

    # --------------------------------------------------------
    # Return formatted status block
    # --------------------------------------------------------

    return "\n".join(status_lines)
    

def print_status_summary():
    print("-" * 60)

    from collections import defaultdict

    groups = defaultdict(list)

    # --------------------------------------------------------
    # GROUP SERVICES
    # --------------------------------------------------------
    for name, state in service_state.items():
        group = state.get("group", "OTHER")
        groups[group].append((name, state))

    # --------------------------------------------------------
    # PRINT ORDERED GROUPS
    # --------------------------------------------------------
    for group_name in ["PROCESS", "TOOLS", "DATABASE", "OTHER"]:

        if group_name not in groups:
            continue

        print(group_name + " SERVICES")
        print("-" * 40)

        for name, state in groups[group_name]:
            print(format_status(name, state))

        print()

    print("-" * 60 + "\n")
    
def run_startup_checks():
    startup_banner()
    check_all()
    print_status_summary()
    
# ── IP DETECTION ──────────────────────────────────────────────

def get_lan_ip():
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8",80)); ip = s.getsockname()[0]; s.close(); return ip
    except: return "127.0.0.1"

def get_public_ip():
    for url in ("https://api.ipify.org","https://icanhazip.com"):
        try:
            r = requests.get(url, timeout=4)
            if r.status_code == 200: return r.text.strip()
        except: pass
    return "(unavailable)"


TOOL_META = {
    "name": "status",
    "category": "system",
    "description": "Shows current Aetheraeon service and project status.",
    "usage": "status",
    "examples": ["status", "system status", "check status"],
    "confirmation_required": False,
}

register_tool(TOOL_META, print_status)
