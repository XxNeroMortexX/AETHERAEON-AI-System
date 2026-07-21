"""Turn-local conversation reference, explanation-depth, and mood helpers.

This module is deliberately stateless.  It reads only the active conversation
history supplied by the caller and never reads or writes long-term memory.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import re
from typing import Iterable

from core.conversation_memory import matching_conversation_only_fact


@dataclass(frozen=True)
class ConversationResolution:
    original_request: str
    resolved_request: str
    kind: str = "new_request"
    resolved: bool = False
    requires_history: bool = False
    suppress_long_term_memory: bool = False
    ambiguous: bool = False
    explanation_depth: int = 2

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class AdaptivePersonalityState:
    """Temporary presentation state for one request; never persisted."""

    mood: str = "balanced"
    warmth: str = "normal"
    patience: str = "normal"
    clarity: str = "normal"
    enthusiasm: str = "normal"
    humor: str = "low"
    identity: str = "Aetheraeon"

    def to_dict(self) -> dict:
        return asdict(self)


_FOLLOW_UPS = (
    (r"(?:make it simpler|simplify(?: it)?|simple explanation)", "simplify", 1),
    (r"(?:explain more|give (?:me )?examples?)", "expand", 2),
    (r"(?:(?:now )?give me (?:the )?)?(?:technical breakdown|technical version)", "technical", 3),
    (r"(?:(?:now )?give me (?:the )?)?academic version|go deeper", "academic", 4),
    (r"compare them", "compare", 3),
    (r"explain the second part", "second_part", 3),
    (r"continue", "continue", 2),
)

_CURRENT_RECALL = re.compile(
    r"(?:what(?:'s| (?:was|is|were)) my\b|what did i (?:say|tell you)\b|"
    r"what did you (?:say|call)\b|do you remember my name\b|"
    r"remind me what i\b)",
    re.IGNORECASE,
)

_USER_NAME_QUESTION = re.compile(
    r"(?:what(?:'s| is| was) my name\b|do you remember my name\b)",
    re.IGNORECASE,
)

_USER_NAME_STATEMENT = re.compile(
    r"\b(?:my name is|you can call me|call me)\s+"
    r"(?P<name>[^\r\n,;.!?]{1,80})",
    re.IGNORECASE,
)

_ACTIVE_REFERENCE = re.compile(
    r"\b(?:this|that|it|these|those|they|them|same|above|previous|earlier|"
    r"former|latter)\b|^(?:also|and|but|so|then|now|what about|how about)\b",
    re.IGNORECASE,
)

# These are continuity signals, not a project knowledge base.  Both the
# current request and active chat must contain a signal before project context
# is injected, so unrelated history is not treated as current-project fact.
_PROJECT_CONTEXT_TERMS = (
    "aetheraeon",
    "frontend",
    "backend",
    "webui",
    "apache",
    "mariadb",
    "database",
    "api",
    "deployment",
    "architecture",
    "codebase",
    "repository",
    "configuration",
    "project",
)


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


def _last_substantive_user_message(history) -> str:
    for message in reversed(_history_messages(history)):
        if str(message.get("role", "")).lower() != "user":
            continue
        content = str(message.get("content", "")).strip()
        if content:
            return content
    return ""


def _active_user_name(history) -> str:
    """Return only a name the user explicitly stated in the active chat."""

    for message in reversed(_history_messages(history)):
        if str(message.get("role", "")).lower() != "user":
            continue
        match = _USER_NAME_STATEMENT.search(str(message.get("content", "")))
        if match:
            return match.group("name").strip(" \t\"'")
    return ""


def needs_active_conversation_context(user_input: str, history=None) -> bool:
    """Detect turns whose meaning depends on the active conversation.

    This deliberately excludes generic topic similarity.  It recognizes an
    explicit reference, a current-chat recall, or shared project terminology.
    The caller remains responsible for loading only the authenticated active
    conversation.
    """

    messages = _history_messages(history)
    if not messages:
        return False

    current = str(user_input or "").strip().lower()
    if not current:
        return False
    if _CURRENT_RECALL.search(current) or _ACTIVE_REFERENCE.search(current):
        return True

    recent_text = " ".join(
        str(message.get("content") or "").lower()
        for message in messages[-8:]
    )
    current_terms = {
        term for term in _PROJECT_CONTEXT_TERMS if term in current
    }
    recent_terms = {
        term for term in _PROJECT_CONTEXT_TERMS if term in recent_text
    }
    return bool(current_terms.intersection(recent_terms))


def determine_explanation_depth(user_input: str, explicit_depth: int | None = None) -> int:
    if explicit_depth is not None:
        return max(1, min(4, int(explicit_depth)))

    text = str(user_input or "").lower()
    if re.search(r"\b(academic|formally|formal proof|derive|derivation|theorem|literature)\b", text):
        return 4
    if re.search(r"\b(technical|implementation|algorithm|architecture|internals?|mechanism)\b", text):
        return 3
    if re.search(
        r"\b(quantum|cryptograph|concurren|distributed system|compiler|bayesian|"
        r"eigenvalue|asymptotic|thermodynamic|neural network|protocol)\w*\b",
        text,
    ):
        return 3
    if re.search(r"\b(simple|simply|brief|one sentence|eli5)\b", text):
        return 1
    return 2


def resolve_conversation_reference(
    user_input: str,
    history=None,
    authenticated_user: dict | None = None,
) -> ConversationResolution:
    """Resolve only well-known short references against the active chat."""

    original = str(user_input or "").strip()
    normalized = re.sub(r"[.!?]+$", "", original.lower()).strip()
    antecedent = _last_substantive_user_message(history)

    scoped_fact = matching_conversation_only_fact(original, history)
    if _CURRENT_RECALL.search(normalized) and scoped_fact:
        fact_label, fact_value = scoped_fact
        return ConversationResolution(
            original,
            f'Answer from conversation-only memory. The user\'s temporary '
            f'{fact_label} is "{fact_value}". Do not describe this as saved '
            "or available outside the active conversation.",
            kind="conversation_only_memory_recall",
            resolved=True,
            requires_history=True,
            suppress_long_term_memory=True,
            explanation_depth=determine_explanation_depth(original),
        )

    # User identity and assistant identity are separate namespaces. An
    # explicitly stated active-chat name is scoped to that conversation and
    # takes precedence; otherwise use the authenticated account username.
    if _USER_NAME_QUESTION.search(normalized):
        stated_user_name = _active_user_name(history)
        account_username = str(
            (authenticated_user or {}).get("username") or ""
        ).strip()
        resolved_name = stated_user_name or account_username
        if resolved_name:
            source = (
                "active conversation"
                if stated_user_name
                else "authenticated user account"
            )
            return ConversationResolution(
                original,
                f'Answer the user\'s question from the {source}. '
                f'The user\'s name is "{resolved_name}". '
                "Here, 'my' refers to the user; Aetheraeon is the assistant.",
                kind="user_identity_recall",
                resolved=True,
                requires_history=bool(stated_user_name),
                suppress_long_term_memory=True,
                explanation_depth=determine_explanation_depth(original),
            )

    # A direct current-chat recall must prefer active history over persistent
    # memory.  The history itself remains the factual source supplied to the LLM.
    if _CURRENT_RECALL.search(normalized):
        if antecedent:
            resolved_request = (
                f"Answer this using only the active conversation: {original}"
            )
            return ConversationResolution(
                original,
                resolved_request,
                kind="current_conversation_recall",
                resolved=True,
                requires_history=True,
                suppress_long_term_memory=True,
                explanation_depth=determine_explanation_depth(original),
            )
        return ConversationResolution(
            original,
            original,
            kind="current_conversation_recall",
            ambiguous=True,
            suppress_long_term_memory=True,
            explanation_depth=determine_explanation_depth(original),
        )

    # Exact/short transformation phrases are intentionally constrained so a
    # new, content-rich question containing similar words is left untouched.
    if len(normalized.split()) <= 8:
        for pattern, kind, depth in _FOLLOW_UPS:
            if re.fullmatch(pattern, normalized, re.I):
                if not antecedent:
                    return ConversationResolution(
                        original,
                        original,
                        kind=kind,
                        ambiguous=True,
                        explanation_depth=depth,
                    )
                instruction = {
                    "simplify": "Give a simpler explanation of",
                    "expand": "Expand the explanation of",
                    "technical": "Give a technical breakdown of",
                    "academic": "Give an academic, deep explanation of",
                    "compare": "Compare the referenced items in",
                    "second_part": "Explain the second part of",
                    "continue": "Continue the response to",
                }[kind]
                return ConversationResolution(
                    original,
                    f'{instruction} the prior user request: "{antecedent}"',
                    kind=kind,
                    resolved=True,
                    requires_history=True,
                    suppress_long_term_memory=True,
                    explanation_depth=depth,
                )

    return ConversationResolution(
        original,
        original,
        explanation_depth=determine_explanation_depth(original),
    )


def build_adaptive_personality_state(
    user_input: str,
    trait_corrections: Iterable[str] | None = None,
    conversation_history=None,
) -> AdaptivePersonalityState:
    """Infer a safe, temporary communication adjustment for this turn."""

    text = str(user_input or "").lower()
    corrections = " ".join(str(item) for item in (trait_corrections or ())).lower()
    recent_user_text = " ".join(
        str(item.get("content") or "").lower()
        for item in _history_messages(conversation_history)[-6:]
        if str(item.get("role") or "").lower() == "user"
    )
    frustrated = bool(re.search(
        r"\b(frustrated|annoyed|confusing|confused|wrong again|not what i asked|"
        r"you missed|doesn'?t make sense)\b",
        text + " " + recent_user_text,
    ))
    positive = bool(re.search(r"\b(thanks|thank you|great|excellent|perfect|awesome)\b", text))
    avoid_harshness = bool(re.search(r"\b(angry|harsh|hostile|aggressive)\b", corrections))
    repeated_clarification = len(re.findall(
        r"\b(?:simplify|simpler|explain again|not clear)\b",
        recent_user_text,
    )) >= 2

    if frustrated or avoid_harshness or repeated_clarification:
        return AdaptivePersonalityState(
            mood="calm_supportive",
            warmth="warm",
            patience="high",
            clarity="high",
            enthusiasm="restrained",
            humor="none",
        )
    if positive:
        return AdaptivePersonalityState(
            mood="positive",
            warmth="high",
            patience="normal",
            clarity="normal",
            enthusiasm="high",
            humor="light",
        )
    return AdaptivePersonalityState()


def conversation_intelligence_prompt(
    resolution: ConversationResolution,
    state: AdaptivePersonalityState,
) -> str:
    depth_rules = {
        1: "Give a concise, plain-language answer.",
        2: "Answer clearly with a basic explanation; for approachable topics, offer a technical or academic follow-up.",
        3: "Give a technical explanation with mechanisms, concrete details, and examples where useful.",
        4: "Give a formal, deep explanation with precise terminology, assumptions, and derivation where relevant.",
    }
    return (
        "TURN-LOCAL CONVERSATION GUIDANCE\n"
        f"Contextual request: {resolution.resolved_request}\n"
        f"Explanation depth: Level {resolution.explanation_depth}. "
        f"{depth_rules[resolution.explanation_depth]}\n"
        "Temporary style adjustment: "
        f"mood={state.mood}, warmth={state.warmth}, patience={state.patience}, "
        f"clarity={state.clarity}, enthusiasm={state.enthusiasm}, humor={state.humor}.\n"
        "This style state applies only to this response. Preserve the fixed Aetheraeon identity."
    )
