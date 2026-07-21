"""Conversation-scoped fact helpers with no persistence side effects.

This module reads only the active history supplied by its caller. It does not
read or write ChromaDB, SQL memory tables, or runtime state shared by chats.
"""

from __future__ import annotations

import re
from typing import Iterable


_CONVERSATION_ONLY_MARKER = re.compile(
    r"\b(?:remember|keep)\b.{0,80}\b(?:this|current) conversation only\b|"
    r"\bconversation[- ]only\b",
    re.IGNORECASE,
)

_QUESTION_PREFIX = re.compile(
    r"^(?:what|why|how|when|where|who|which|is|are|do|does|did)\b",
    re.IGNORECASE,
)

_TEMPORARY_FACT = re.compile(
    r"\bmy\s+(?P<label>[a-z0-9 _-]{1,60}?)\s+is\s+"
    r"(?P<value>[^\r\n.!?]{1,120})",
    re.IGNORECASE,
)


def is_conversation_only_memory_request(text: str) -> bool:
    """Return true only for an instruction explicitly scoped to this chat."""

    normalized = re.sub(r"\s+", " ", str(text or "")).strip()
    if not normalized or _QUESTION_PREFIX.match(normalized):
        return False
    return bool(_CONVERSATION_ONLY_MARKER.search(normalized))


def _history_messages(history) -> list[dict]:
    if not history:
        return []
    if isinstance(history, str):
        messages = []
        for line in history.splitlines():
            match = re.match(r"\s*(User|AI|Assistant)\s*:\s*(.+)", line, re.I)
            if match:
                role = "user" if match.group(1).lower() == "user" else "ai"
                messages.append({"role": role, "content": match.group(2).strip()})
        return messages
    if isinstance(history, Iterable):
        return [item for item in history if isinstance(item, dict)]
    return []


def _fact_from_text(text: str) -> tuple[str, str] | None:
    match = _TEMPORARY_FACT.search(str(text or ""))
    if not match:
        return None
    label = re.sub(r"\s+", " ", match.group("label")).strip().lower()
    if label.endswith(" name"):
        label = label[:-5].strip()
    value = match.group("value").strip(" \t\"'")
    return (label, value) if label and value else None


def conversation_only_facts(history) -> dict[str, str]:
    """Extract facts explicitly marked conversation-only in active history."""

    facts = {}
    previous_user_text = ""
    for message in _history_messages(history):
        if str(message.get("role") or "").lower() != "user":
            continue
        content = str(message.get("content") or "").strip()
        if is_conversation_only_memory_request(content):
            fact = _fact_from_text(content) or _fact_from_text(previous_user_text)
            if fact:
                facts[fact[0]] = fact[1]
        previous_user_text = content
    return facts


def matching_conversation_only_fact(user_input: str, history) -> tuple[str, str] | None:
    """Match a current recall question to an explicitly scoped chat fact."""

    facts = conversation_only_facts(history)
    if not facts:
        return None
    query_tokens = set(re.findall(r"[a-z0-9]+", str(user_input or "").lower()))
    query_tokens.difference_update({"what", "is", "was", "my", "the", "name"})
    ranked = []
    for label, value in facts.items():
        label_tokens = set(re.findall(r"[a-z0-9]+", label))
        score = len(query_tokens.intersection(label_tokens))
        if score:
            ranked.append((score, len(label_tokens), label, value))
    if not ranked:
        return None
    _, _, label, value = max(ranked)
    return label, value
