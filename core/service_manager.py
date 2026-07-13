import shutil
import psutil
import time

NPX_PATH = shutil.which("npx")

# ============================================================
# SERVICE MANAGER — AETHERAEON
# ============================================================
# Brain layer: start / check / stop services
# "check" here means: verify + auto-start if missing
# ============================================================

import subprocess
import socket

from core.service_registry import (
    register_service,
    shutdown_service,
    SERVICE_REGISTRY
)

from colorama import Fore, Style
        
# ============================================================
# SERVICE DEFINITIONS
# ============================================================
SERVICES = {
    "n8n": {
        "type": "process",
        "group": "PROCESS",
        "managed": True,
        "port": 5678,
        "start_cmd": [NPX_PATH, "n8n", "start"],
        "version_cmd": [NPX_PATH, "n8n", "--version"]
    },

    "ollama": {
        "type": "process",
        "group": "PROCESS",
        "managed": True,
        "port": 11434,
        "start_cmd": ["ollama", "serve"],
        "version_cmd": ["ollama", "--version"]
    },

    "aider": {
        "type": "tool",
        "group": "TOOLS",
        "cmd": ["aider", "--version"]
    },

    "chromadb": {
        "type": "embedded",
        "group": "DATABASE"
    }
}

# ============================================================
# RUNTIME STATE TRACKING
# ============================================================

service_state = {}


# ============================================================
# UTIL — PORT CHECK
# ============================================================

def is_port_open(port: int) -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(("127.0.0.1", port))
    sock.close()
    return result == 0


# ============================================================
# START SERVICE (ONLY FOR MANAGED)
# ============================================================
def start_service(name: str):
    
    svc = SERVICES[name]

    if not svc.get("managed"):
        print(f"[WARN] {name} is not managed (cannot start)")
        return False

    # ============================================================
    # STEP 1: START SERVICE (LAUNCHER ONLY)
    # ------------------------------------------------------------
    # We ONLY track the root process we spawn
    # ============================================================
    process = subprocess.Popen(
        svc["start_cmd"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
    )

    print(f"[DEBUG] {name} launcher PID = {process.pid}")

    # ============================================================
    # STEP 2: ALLOW SERVICE TO BOOT
    # ============================================================
    time.sleep(2)

    # ============================================================
    # STEP 3: REGISTER OWNERSHIP
    # ------------------------------------------------------------
    # Only launcher PID matters. No children tracking.
    # ============================================================
    register_service(name, {
        "launcher": process.pid
    })

    print(f"[OK] {name} -> started")
    return True


# ============================================================
# CHECK SERVICE (CHECK + AUTO START IF NEEDED)
# ============================================================

def check_service(name: str, start_if_offline: bool = True) -> bool:
    svc = SERVICES[name]

    result = False
    meta = {}

    print(f"[SERVICE CHECK] service checked: {name}")

    # --------------------------------------------------------
    # PROCESS SERVICES (n8n, ollama)
    # --------------------------------------------------------
    if svc.get("type") == "process":

        port = svc.get("port")

        # FIX 1: primary check = port
        port_alive = is_port_open(port)

        if port_alive:
            result = True
            meta["port"] = port
            meta["reason"] = f"port {port} is accepting connections"

        else:
            print(f"[INFO] {name} -> port closed, checking process state...")

            if not start_if_offline:
                result = False
                meta["reason"] = f"port {port} is closed"
            else:

                # FIX 2: try to detect zombie processes (optional safety layer)
                entry = SERVICE_REGISTRY.get(name)

                zombie_found = False

                if entry:
                    all_pids = []
                    if entry.get("launcher"):
                        all_pids.append(entry["launcher"])
                    all_pids += entry.get("children", [])

                    for pid in all_pids:
                        try:
                            if psutil.pid_exists(pid):
                                zombie_found = True
                                break
                        except Exception:
                            pass

                # FIX 3: decide action
                if zombie_found:
                    print(f"[WARN] {name} zombie process detected -> forcing restart")
                    stop_service(name)
                    result = start_service(name)
                    meta["reason"] = "zombie process was restarted"
                else:
                    print(f"[INFO] {name} -> not running, starting...")
                    result = start_service(name)
                    meta["reason"] = "service was started by health recovery"

        # ----------------------------------------------------
        # version (optional safe call)
        # ----------------------------------------------------
        try:
            if "version_cmd" in svc:

                res = subprocess.run(
                    svc["version_cmd"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                version = res.stdout.strip() or res.stderr.strip()

                if version:
                    meta["version"] = version

        except Exception as e:
            print(f"[DEBUG] version error for {name}: {e}")

    # --------------------------------------------------------
    # TOOL SERVICES (aider)
    # --------------------------------------------------------
    elif svc.get("type") == "tool":
        try:
            res = subprocess.run(
                svc["cmd"],
                capture_output=True,
                text=True,
                timeout=10
            )

            result = (res.returncode == 0)
            meta["version"] = res.stdout.strip() or res.stderr.strip()
            meta["reason"] = (
                "version command completed successfully"
                if result
                else f"version command exited with code {res.returncode}"
            )

        except Exception as error:
            result = False
            meta["reason"] = f"tool check failed: {error}"

    # --------------------------------------------------------
    # EMBEDDED SERVICES (chromadb)
    # --------------------------------------------------------
    elif svc.get("type") == "embedded":

        if name == "chromadb":
            try:
                import chromadb
                meta["version"] = getattr(chromadb, "__version__", "unknown")
                from core.memory_database import initialize_memory, get_memory_count
                result = initialize_memory()
                meta["memories"] = get_memory_count() if result else None
                meta["reason"] = (
                    "embedded collection loaded successfully"
                    if result
                    else "embedded collection could not be loaded"
                )

            except Exception as error:
                result = False
                meta["version"] = "unknown"
                meta["reason"] = f"embedded service check failed: {error}"

    # --------------------------------------------------------
    # DEFAULT
    # --------------------------------------------------------
    else:
        result = False

    # --------------------------------------------------------
    # STATE TRACKING (FINAL OUTPUT)
    # --------------------------------------------------------
    service_state[name] = {
        "status": result,
        "meta": meta,
        "group": svc.get("group")
    }

    print(
        f"[SERVICE CHECK] detected state: {name}="
        f"{'online' if result else 'offline'} | "
        f"reason: {meta.get('reason', 'no reason reported')}"
    )

    return result
    
# ============================================================
# STOP SERVICE
# ------------------------------------------------------------
# Stops a managed service owned by Aetheraeon.
# Kills the launcher process tree, verifies shutdown,
# then clears registry ownership tracking.
# ============================================================
def stop_service(name: str):

    print(f"[DEBUG] stop_service({name}) called")

    entry = SERVICE_REGISTRY.get(name)

    if not entry:
        print(f"[WARN] {name} not found in registry")
        return False

    port = SERVICES.get(name, {}).get("port")

    try:

        launcher = entry.get("launcher")

        print(f"[DEBUG] stop_service launcher = {launcher}")

        # ====================================================
        # STEP 1: KILL OWNED PROCESS TREE
        # ----------------------------------------------------
        # Kill only the launcher we started and all children.
        # ====================================================
        if launcher:

            print(f"[KILL] owned launcher PID {launcher}")

            kill_tree(launcher)

        # ====================================================
        # STEP 2: PORT CLEANUP (OWNED SERVICES ONLY)
        # ----------------------------------------------------
        # Safety net in case the launcher spawned detached
        # workers that survived the tree kill.
        # ====================================================
        if port and launcher:

            kill_port_if_owned(port, launcher)

        # ====================================================
        # STEP 3: WAIT FOR OS CLEANUP
        # ====================================================

        time.sleep(1)

        # ====================================================
        # STEP 4: FINAL PORT VERIFICATION
        # ====================================================
        if port and is_port_open(port):

            print(
                f"[WARN] {name} still running "
                f"(port {port} still active)"
            )

            return False

        # ====================================================
        # STEP 5: CLEAN REGISTRY
        # ----------------------------------------------------
        # Service successfully stopped.
        # ====================================================
        shutdown_service(name)

        print(f"[OK] {name} fully stopped")

        return True

    except Exception as e:

        print(f"[WARN] {name} stop error: {e}")

        return False

# ============================================================
# PORT-BASED PROCESS KILL (NETSTAT STYLE)
# ------------------------------------------------------------
# Mirrors PowerShell Kill-Port behavior:
# - Uses netstat to find PID owning a port
# - Force kills every matching PID
# - Reliable for Node / n8n / Ollama cleanup on Windows
# ============================================================
def kill_port_if_owned(port, owned_pid):
    try:
        output = subprocess.check_output(
            f'netstat -ano | findstr ":{port}"',
            shell=True,
            text=True
        )
    except subprocess.CalledProcessError:
        return

    for line in output.splitlines():
        parts = line.split()
        if len(parts) >= 5:
            pid = int(parts[-1])

            # ONLY kill if we own it
            if pid == owned_pid:
                print(f"[KILL-OWNED] Port {port} -> PID {pid}")
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)])


# ============================================================
# PROCESS TREE TERMINATION
# ------------------------------------------------------------
# Recursively kills a process and all of its child processes.
# Used to fully terminate launcher shells (cmd) + spawned services.
# Ensures no orphaned node/ollama processes remain running.
# ============================================================

def kill_tree(pid):

    print(f"[DEBUG] kill_tree called for PID {pid}")

    try:

        parent = psutil.Process(pid)

        children = parent.children(recursive=True)

        print(
            f"[DEBUG] Found {len(children)} child processes"
        )

        # ----------------------------------------------------
        # Kill children first
        # ----------------------------------------------------
        for child in children:

            print(
                f"[KILL] Child PID {child.pid}"
            )

            child.kill()

        # ----------------------------------------------------
        # Kill parent last
        # ----------------------------------------------------
        print(
            f"[KILL] Parent PID {parent.pid}"
        )

        parent.kill()

        print(
            f"[OK] Process tree terminated"
        )

    except psutil.NoSuchProcess:

        print(
            f"[DEBUG] PID {pid} already exited"
        )

    except Exception as e:

        print(
            f"[WARN] kill_tree error: {e}"
        )



# ============================================================
# CLEAN SYSTEM SHUTDOWN
# ------------------------------------------------------------
# Stops all registry-owned services using the service manager.
# Only services started by Aetheraeon are affected.
# Manual user-started services remain untouched.
# ============================================================

def shutdown_all():

    stopped_any = False

    print("\n[INFO] Beginning managed service shutdown...")

    # --------------------------------------------------------
    # Iterate through all tracked services
    # --------------------------------------------------------
    for name in list(SERVICE_REGISTRY.keys()):

        entry = SERVICE_REGISTRY.get(name)

        # ----------------------------------------------------
        # Skip services that are already stopped
        # ----------------------------------------------------
        if not entry:
            continue

        try:

            print(f"[DEBUG] shutdown_all -> stopping {name}")

            # ------------------------------------------------
            # Delegate shutdown to service manager
            # ------------------------------------------------
            result = stop_service(name)

            if result:

                print(f"  [OK] {name} -> stopped")

                stopped_any = True

            else:

                print(f"  [WARN] {name} stop failed")

        except Exception as e:

            print(
                f"  [WARN] {name} stop failed: {e}"
            )

    # --------------------------------------------------------
    # Final shutdown status
    # --------------------------------------------------------
    if stopped_any:

        print(
            "\n[INFO] Shutting down Aetheraeon services..."
        )

    else:

        print(
            "\n[INFO] No managed services required shutdown."
        )

        
# ============================================================
# CHECK ALL SERVICES (YOUR MAIN STARTUP ENTRY)
# ============================================================

def check_all(start_if_offline: bool = True):
    for name in SERVICES.keys():
        check_service(name, start_if_offline=start_if_offline)
        
def format_status(name: str, state: dict):

    status = state.get("status", False)
    meta = state.get("meta", {})

    # --------------------------------------------------------
    # STATUS TAG + COLOR
    # --------------------------------------------------------
    if status is True:
        color = Fore.GREEN
        tag = "[OK]"
    elif status is False:
        color = Fore.RED
        tag = "[ERROR]"
    else:
        color = Fore.YELLOW
        tag = "[WARN]"

    # --------------------------------------------------------
    # NAME FORMAT
    # --------------------------------------------------------
    name_str = f"{Style.BRIGHT}{Fore.WHITE}{name.upper()}{Style.RESET_ALL}"

    # --------------------------------------------------------
    # DETAILS
    # --------------------------------------------------------
    details = []

    if meta.get("port"):
        details.append(f"{Fore.CYAN}PORT:{meta['port']}{Style.RESET_ALL}")

    if meta.get("version"):
        details.append(f"{Fore.CYAN}VER:{meta['version']}{Style.RESET_ALL}")

    if meta.get("memorys") is not None:
        details.append(f"{Fore.CYAN}MEM:{meta['memorys']}{Style.RESET_ALL}")

    extra = ""
    if details:
        extra = " | " + " | ".join(details)

    return f"{color}{tag:<8}{Style.RESET_ALL} {name_str:<12}{extra}"
