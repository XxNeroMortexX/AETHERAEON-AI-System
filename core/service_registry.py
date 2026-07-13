# ========================================================
# SERVICE REGISTRY — AETHERAEON
# ========================================================
# Tracks ONLY services started by this AI controller
# Used for safe shutdown and lifecycle control
# ========================================================

import subprocess

SERVICE_REGISTRY = {
    "n8n": None,
    "ollama": None
}


# ========================================================
# REGISTER SERVICE
# ========================================================
# Call this when YOU start a service
# ========================================================

def register_service(name: str, process_info):
    SERVICE_REGISTRY[name] = process_info

    print(f"[DEBUG] registered service: {name} -> {process_info}")

    launcher = process_info.get("launcher")
    print(f"[REGISTRY] Added managed service: {name} (launcher PID={launcher})")

    print(f"[REGISTRY] Managed services registered: {list(SERVICE_REGISTRY.keys())}")
    

# ============================================================
# SERVICE SHUTDOWN STATE CLEANUP
# ------------------------------------------------------------
# Marks a service as stopped and clears registry ownership.
# Does NOT kill processes directly.
# Process shutdown is handled by service_manager.stop_service().
# ============================================================

def shutdown_service(name: str):

    if name in SERVICE_REGISTRY:

        SERVICE_REGISTRY[name] = None

        print(
            f"[REGISTRY] {name} marked as stopped"
        )
