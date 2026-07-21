"""
Aetheraeon AI - External Toolkit

Purpose:
Provides controlled adapters for interacting with external APIs, services, automation systems, and operating-system resources.

Architecture Layer:
Tool Execution Layer - external integration boundary.

Responsibilities:
- Perform approved external operations requested through existing execution paths.
- Normalize external results, errors, and operational metadata.
- Isolate provider-specific interaction details from cognitive components.

Boundaries:
- This module does not select tools, infer intent, authorize actions, or establish cognitive policy.
- Tool executors and security components validate operations before execution, and security remains authoritative.
- External results do not directly modify memory or become trusted facts without the appropriate decision and validation flow.
"""

# ============================================================
# CORE STANDARD LIBRARY IMPORTS
# ============================================================
# These are built-in Python modules used for parsing,
# command processing, and environment access.
# ============================================================

import os           # Environment variables and configuration access
import re           # Pattern matching and command parsing


# ============================================================
# EXTERNAL DEPENDENCIES (PIP INSTALLED PACKAGES)
# ============================================================
# These are third-party libraries installed via pip.
# ============================================================

import requests     # HTTP requests for web search providers


# ============================================================
# INTERNAL SYSTEM IMPORTS (ARCHITECTURE LAYERS)
# ============================================================
# External Toolkit is responsible for integrations with
# external services, APIs, automation platforms, and
# third-party systems.
#
# RULES:
# - May communicate with external services
# - May call web APIs
# - May integrate with automation platforms
# - Should NOT contain orchestration logic
# - Should NOT contain memory database logic
# - Should NOT contain personality logic
# ============================================================

# ------------------------------------------------------------
# CONFIGURATION LAYER
# (Loads runtime settings and system configuration)
# ------------------------------------------------------------

from core.config_manager import load_settings, save_settings


# ============================================================
# WEB SEARCH TOOL EXECUTOR
# ============================================================
# Purpose:
# Executes web search requests using configured provider
# (Google CSE or DuckDuckGo fallback).
#
# This function acts as a TOOL LAYER executor.
# It does NOT interpret intent — only executes search tasks.
# ============================================================

def run_web_search(query, max_results, session, memory, force_enabled=False):
    """
    Execute a web search request using configured provider.

    Flow:
        1. Validate query
        2. Load system settings
        3. Choose provider (Google CSE or DDG)
        4. Execute search
        5. Return structured results
    """

    # ============================================================
    # INPUT VALIDATION
    # ============================================================
    search_query = (query or "").strip()
    if not search_query:
        return {
            "type": "web_search",
            "error": "Missing search query"
        }

    # ============================================================
    # LOAD CONFIGURATION SETTINGS
    # ============================================================
    try:
        settings = ai_orchestrator.load_settings()
    except Exception:
        settings = {}

    web_config = settings.get("web_search", {}) or {}

    if not force_enabled and not web_config.get("enabled", False):
        return {
            "type": "web_search",
            "error": "Web search is disabled"
        }

    provider = (web_config.get("provider") or "google_cse").lower().strip()
    max_results = int(max_results or web_config.get("max_results") or 5)
    max_results = max(1, min(10, max_results))

    # ============================================================
    # RESULT STORAGE
    # ============================================================
    search_results = []

    # ============================================================
    # DUCKDUCKGO FALLBACK SEARCH
    # ============================================================
    def ddg_search():
        """
        Lightweight HTML scraping fallback for DuckDuckGo.
        Used when Google CSE is unavailable or disabled.
        """

        try:
            url = "https://duckduckgo.com/html/"
            response = requests.post(
                url,
                data={"q": search_query},
                timeout=20,
                headers={"User-Agent": "Mozilla/5.0"}
            )

            if response.status_code != 200:
                return []

            html = response.text
            results = []

            for match in re.finditer(
                r'<a rel="nofollow" class="result__a" href="([^"]+)"[^>]*>(.*?)</a>',
                html
            ):
                link = re.sub(r"&amp;", "&", match.group(1))
                title = re.sub(r"<.*?>", "", match.group(2))

                results.append({
                    "title": title,
                    "link": link
                })

                if len(results) >= max_results:
                    break

            return results

        except Exception:
            return []

    # ============================================================
    # GOOGLE CSE SEARCH
    # ============================================================
    def google_search():
        """
        Google Custom Search API execution.
        Requires API key + CX configuration.
        """

        api_key = (
            os.environ.get("GOOGLE_CSE_API_KEY")
            or web_config.get("google_cse_api_key")
            or ""
        ).strip()

        cx_id = (
            os.environ.get("GOOGLE_CSE_CX")
            or web_config.get("google_cse_cx")
            or ""
        ).strip()

        if not api_key or not cx_id:
            return None

        try:
            url = "https://www.googleapis.com/customsearch/v1"

            params = {
                "q": search_query,
                "key": api_key,
                "cx": cx_id,
                "num": min(max_results, 10)
            }

            response = requests.get(url, params=params, timeout=20)

            if response.status_code != 200:
                return None

            data = response.json() or {}
            items = data.get("items") or []

            results = []

            for item in items[:max_results]:
                results.append({
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "snippet": item.get("snippet", "")
                })

            return results if results else None

        except Exception:
            return None

    # ============================================================
    # PROVIDER EXECUTION FLOW
    # ============================================================

    if provider in ("google", "google_cse"):
        search_results = google_search()

        # fallback if Google fails
        if not search_results:
            search_results = ddg_search()
            provider = "ddg_fallback"

    else:
        search_results = ddg_search()
        provider = "ddg"

    # ============================================================
    # MEMORY UPDATE (SAFE TRACKING ONLY)
    # ============================================================
    memory["last_web_query"] = search_query
    memory["last_web_provider"] = provider
    memory["last_web_count"] = len(search_results)

    # ============================================================
    # FINAL RETURN STRUCTURE
    # ============================================================
    return {
        "type": "web_search",
        "query": search_query,
        "provider": provider,
        "results": search_results
    }
