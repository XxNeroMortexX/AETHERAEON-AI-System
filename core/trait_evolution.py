"""Deterministic, memory-independent AI trait observation and evolution.

The service recognizes explicit interaction-style preferences only.  It does
not infer private reasoning, query ChromaDB, route requests, or authorize any
operation.  One signal creates an observing candidate; repeated distinct
signals are required before promotion.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import logging
import re


PROMOTION_THRESHOLD = 75
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TraitSignal:
    candidate_name: str
    candidate_description: str
    promoted_name: str
    promoted_description: str
    category: str
    reason: str
    event_summary: str
    promoted_strength: int

    def to_dict(self) -> dict:
        return asdict(self)


_SIGNAL_RULES = (
    (
        re.compile(
            r"(?:\bi\s+(?:really\s+)?(?:like|love|enjoy|prefer|appreciate)\b"
            r".{0,100}\b(?:jokes?|humou?r|funny|fun|playful)\b|"
            r"\bmake\s+(?:the\s+)?greetings?\s+(?:more\s+)?funny\b|"
            r"\bgreet\s+me\b.*\b(?:humou?r|jokes?|funny)\b|"
            r"\balways\s+greet\s+me\b.*\b(?:humou?r|jokes?|funny)\b|"
            r"\b(?:funny|humorous|playful)\s+greetings?\b.{0,100}"
            r"\b(?:friendly|better|enjoyable|welcoming)\b)",
            re.IGNORECASE,
        ),
        TraitSignal(
            candidate_name="Humor Preference",
            candidate_description="User enjoys humorous greetings and playful conversation.",
            promoted_name="Humor Preference",
            promoted_description="Uses light humor in suitable greetings and casual interactions.",
            category="communication",
            reason="Repeated user preference detected.",
            event_summary="Explicit preference for humor or funny greetings.",
            promoted_strength=70,
        ),
    ),
    (
        re.compile(
            r"(?:\bi\s+(?:like|love|enjoy|prefer)\s+(?:detailed|technical|step[- ]by[- ]step)\s+explanations?\b|"
            r"\balways\s+explain\b.*\b(?:in detail|step[- ]by[- ]step|technically)\b)",
            re.IGNORECASE,
        ),
        TraitSignal(
            candidate_name="Detailed Explanation Preference",
            candidate_description="User appears to prefer detailed, structured explanations.",
            promoted_name="Structured Explanation Preference",
            promoted_description="Provides detailed and structured explanations when appropriate.",
            category="communication",
            reason="User repeatedly requested detailed or step-by-step explanations.",
            event_summary="Explicit preference for detailed or structured explanations.",
            promoted_strength=70,
        ),
    ),
)


def detect_trait_signals(user_message: str) -> list[TraitSignal]:
    text = re.sub(r"\s+", " ", str(user_message or "")).strip()
    if not text:
        return []
    return [signal for pattern, signal in _SIGNAL_RULES if pattern.search(text)]


def candidate_confidence(evidence_count: int) -> int:
    """Require three distinct signals: 40%, 60%, then 80% promotion."""
    count = max(0, int(evidence_count or 0))
    return min(100, 20 + (20 * count)) if count else 0


def next_candidate_state(existing: dict | None) -> dict:
    evidence_count = int((existing or {}).get("evidence_count") or 0) + 1
    confidence = candidate_confidence(evidence_count)
    was_promoted = str((existing or {}).get("status") or "observing") == "promoted"
    should_promote = not was_promoted and confidence >= PROMOTION_THRESHOLD
    return {
        "evidence_count": evidence_count,
        "confidence_score": confidence,
        "status": "promoted" if (was_promoted or should_promote) else "observing",
        "should_promote": should_promote,
    }


def observation_event_key(conversation_id: str, user_message: str, candidate_name: str) -> str:
    normalized = re.sub(r"\s+", " ", str(user_message or "").lower()).strip()
    material = f"{conversation_id}|{candidate_name}|{normalized}".encode("utf-8")
    return hashlib.sha256(material).hexdigest()


def observe_conversation_for_traits(
    user_id: int,
    conversation_id: str,
    user_message: str,
    recorder=None,
) -> list[dict]:
    """Record explicit preference signals through the personality repository."""
    if recorder is None:
        from core.memory_database import record_personality_trait_candidate_evidence
        recorder = record_personality_trait_candidate_evidence

    observations = []
    for signal in detect_trait_signals(user_message):
        logger.info("Preference signal detected: %s", signal.candidate_name)
        observation = recorder(
            user_id=user_id,
            conversation_id=conversation_id,
            event_key=observation_event_key(
                conversation_id, user_message, signal.candidate_name
            ),
            signal=signal.to_dict(),
        )
        observations.append(observation)
        if observation:
            evidence_count = observation.get("evidence_count", "unknown")
            candidate_action = "created" if evidence_count == 1 else "updated"
            logger.info(
                "Trait candidate %s %s: status=%s confidence=%s evidence=%s",
                signal.candidate_name,
                candidate_action,
                observation.get("status", "unknown"),
                observation.get("confidence_score", "unknown"),
                evidence_count,
            )
            if observation.get("status") == "promoted":
                logger.info("Trait promotion triggered: %s", signal.promoted_name)
    return [item for item in observations if item]
