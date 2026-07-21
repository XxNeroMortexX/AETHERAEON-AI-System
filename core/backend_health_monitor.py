"""Non-blocking cached service health for API consumers.

The monitor owns the authoritative in-process health snapshot. Expensive service
checks run at startup, on the background refresh thread, or through the explicit
administrator-only full-health endpoint. Request handlers only read snapshots.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import threading
import time
from typing import Callable, Mapping, MutableMapping, Optional


def _online(value) -> bool:
    if isinstance(value, Mapping):
        return bool(value.get("status"))
    return bool(value)


class BackendHealthMonitor:
    """Cache and periodically refresh backend service availability."""

    def __init__(
        self,
        *,
        service_state: MutableMapping,
        full_check: Callable[[], object],
        database_check: Callable[[], bool],
        refresh_interval_seconds: float = 60.0,
    ) -> None:
        self.service_state = service_state
        self.full_check = full_check
        self.database_check = database_check
        self.refresh_interval_seconds = float(refresh_interval_seconds)
        self._lock = threading.RLock()
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._refreshing = False
        self._cache = {
            "api": "online",
            "database": "unknown",
            "ollama": "online" if _online(service_state.get("ollama")) else "offline",
            "n8n": "online" if _online(service_state.get("n8n")) else "offline",
            "aider": "online" if _online(service_state.get("aider")) else "offline",
            "chromadb": "online" if _online(service_state.get("chromadb")) else "offline",
            "last_checked": None,
            "health_duration_ms": 0.0,
            "stale": True,
            "error": "not_checked",
        }

    def snapshot(self) -> dict:
        """Return immediately with the last completed snapshot."""
        with self._lock:
            result = deepcopy(self._cache)
            result["refreshing"] = self._refreshing
            return result

    def service_snapshot(self) -> dict:
        """Return service detail for the administrator-only diagnostic route."""
        with self._lock:
            return deepcopy(dict(self.service_state))

    def refresh_now(self, *, check: Optional[Callable[[], object]] = None) -> dict:
        """Perform a full scan unless another scan is already in progress."""
        with self._lock:
            if self._refreshing:
                return self.snapshot()
            self._refreshing = True

        started = time.perf_counter()
        try:
            (check or self.full_check)()
            database_online = bool(self.database_check())
            checked_at = datetime.now(timezone.utc).isoformat()
            duration_ms = round((time.perf_counter() - started) * 1000.0, 3)
            with self._lock:
                self._cache.update({
                    "api": "online",
                    "database": "online" if database_online else "offline",
                    "ollama": "online" if _online(self.service_state.get("ollama")) else "offline",
                    "n8n": "online" if _online(self.service_state.get("n8n")) else "offline",
                    "aider": "online" if _online(self.service_state.get("aider")) else "offline",
                    "chromadb": "online" if _online(self.service_state.get("chromadb")) else "offline",
                    "last_checked": checked_at,
                    "health_duration_ms": duration_ms,
                    "stale": False,
                    "error": None,
                })
        except Exception as error:
            duration_ms = round((time.perf_counter() - started) * 1000.0, 3)
            with self._lock:
                # Preserve all last-known values. Only freshness metadata changes.
                self._cache["health_duration_ms"] = duration_ms
                self._cache["stale"] = True
                self._cache["error"] = type(error).__name__
            print(f"[HEALTH REFRESH FAILURE] type={type(error).__name__}")
        finally:
            with self._lock:
                self._refreshing = False
        return self.snapshot()

    def start(self, *, initial_check: Optional[Callable[[], object]] = None) -> dict:
        """Run one startup scan and begin the 60-second refresh loop."""
        result = self.refresh_now(check=initial_check)
        with self._lock:
            if self._thread and self._thread.is_alive():
                return result
            self._stop_event.clear()
            self._thread = threading.Thread(
                target=self._refresh_loop,
                name="aetheraeon-health-monitor",
                daemon=True,
            )
            self._thread.start()
        return result

    def stop(self) -> None:
        self._stop_event.set()

    def _refresh_loop(self) -> None:
        while not self._stop_event.wait(self.refresh_interval_seconds):
            self.refresh_now()
