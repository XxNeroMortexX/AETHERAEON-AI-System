"""Centralized dual-deployment configuration for Aetheraeon.

Deployment mode controls transport and frontend delivery only. It must never
alter AI, routing, memory, personality, CDE, trait, or authorization behavior.
The runtime snapshot is intentionally immutable: changing the configured mode
requires a process restart before behavior changes.
"""

from __future__ import annotations

from dataclasses import dataclass
import ipaddress
import os
from pathlib import Path
import re
import threading

from core.config_loader import ENV_PATH


DEPLOYMENT_MODE_ENV = "DEPLOYMENT_MODE"
TRUSTED_PROXIES_ENV = "DEPLOYMENT_TRUSTED_PROXY_IPS"
VALID_DEPLOYMENT_MODES = frozenset({"development", "production"})
_WRITE_LOCK = threading.RLock()


def normalize_deployment_mode(value: object) -> str:
    mode = str(value or "development").strip().lower()
    return mode if mode in VALID_DEPLOYMENT_MODES else "development"


def _trusted_proxy_ips(value: object) -> frozenset[str]:
    trusted: set[str] = set()
    for item in str(value or "").split(","):
        candidate = item.strip()
        if not candidate:
            continue
        try:
            trusted.add(str(ipaddress.ip_address(candidate)))
        except ValueError:
            # Invalid entries never broaden access.
            continue
    return frozenset(trusted)


@dataclass(frozen=True, slots=True)
class DeploymentRuntimeConfig:
    mode: str
    trusted_proxy_ips: frozenset[str]

    @property
    def is_development(self) -> bool:
        return self.mode == "development"

    @property
    def is_production(self) -> bool:
        return self.mode == "production"

    @property
    def serves_frontend(self) -> bool:
        return self.is_development

    def source_is_allowed(self, remote_address: object) -> bool:
        if self.is_development:
            return True
        candidate = str(remote_address or "").strip()
        if candidate in {"127.0.0.1", "::1"}:
            return True
        try:
            normalized = str(ipaddress.ip_address(candidate))
        except ValueError:
            return False
        return normalized in self.trusted_proxy_ips


_RUNTIME_CONFIG = DeploymentRuntimeConfig(
    mode=normalize_deployment_mode(os.getenv(DEPLOYMENT_MODE_ENV)),
    trusted_proxy_ips=_trusted_proxy_ips(os.getenv(TRUSTED_PROXIES_ENV)),
)


def get_runtime_deployment() -> DeploymentRuntimeConfig:
    """Return the immutable startup snapshot."""

    return _RUNTIME_CONFIG


def configured_deployment_mode(env_path: Path | str = ENV_PATH) -> str:
    """Read the restart-target mode without changing runtime behavior."""

    path = Path(env_path)
    if not path.exists():
        return "development"
    configured = None
    pattern = re.compile(rf"^\s*{re.escape(DEPLOYMENT_MODE_ENV)}\s*=\s*(.*?)\s*$")
    for line in path.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line)
        if match:
            configured = match.group(1).strip().strip('"').strip("'")
    return normalize_deployment_mode(configured)


def deployment_status(env_path: Path | str = ENV_PATH) -> dict[str, object]:
    runtime = get_runtime_deployment()
    configured = configured_deployment_mode(env_path)
    return {
        "current_mode": runtime.mode,
        "configured_mode": configured,
        "restart_required": configured != runtime.mode,
        "frontend_provider": "backend" if runtime.serves_frontend else "apache",
        "apache_proxy_expected": runtime.is_production,
        "trusted_proxy_configured": bool(runtime.trusted_proxy_ips),
    }


def write_configured_deployment_mode(
    mode: object,
    *,
    env_path: Path | str = ENV_PATH,
) -> str:
    """Atomically update only DEPLOYMENT_MODE in the server-side env file."""

    normalized = str(mode or "").strip().lower()
    if normalized not in VALID_DEPLOYMENT_MODES:
        raise ValueError("deployment mode must be development or production")

    path = Path(env_path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    with _WRITE_LOCK:
        original = path.read_text(encoding="utf-8") if path.exists() else ""
        newline = "\r\n" if "\r\n" in original else "\n"
        replacement = f"{DEPLOYMENT_MODE_ENV}={normalized}"
        lines = original.splitlines()
        pattern = re.compile(rf"^\s*{re.escape(DEPLOYMENT_MODE_ENV)}\s*=")
        found = False
        updated: list[str] = []
        for line in lines:
            if pattern.match(line):
                if not found:
                    updated.append(replacement)
                    found = True
                continue
            updated.append(line)
        if not found:
            updated.append(replacement)
        content = newline.join(updated) + newline
        temporary = path.with_name(f"{path.name}.deployment.tmp")
        try:
            temporary.write_text(content, encoding="utf-8", newline="")
            os.replace(temporary, path)
        finally:
            if temporary.exists():
                temporary.unlink()
    return normalized
