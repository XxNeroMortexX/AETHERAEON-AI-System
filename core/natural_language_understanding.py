"""Deterministic Natural Language Understanding for Phase 1 shadow analysis.

This module is deliberately non-authoritative.  It produces a versioned
``NLUResult`` and an observable shadow envelope, but it does not import or call
the current request router, memory, tools, prompts, persistence, API, or UI.
Nothing in the live application imports this module during Phase 1.

The optional current-router intent is comparison data only.  It never changes
the NLU result and cannot authorize routing or any side effect.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import json
import math
import re
import time
from typing import Any, Callable, ClassVar, Mapping

from core.cognitive_contracts import (
    COGNITIVE_CONTRACT_SCHEMA_VERSION,
    ContextScope,
    Entity,
    NLUResult,
    ProvenanceSource,
    TemporalScope,
)
from core.cognitive_trace import generate_correlation_id


SHADOW_NLU_MODE = "shadow"
SHADOW_NLU_AUTHORITATIVE = False
SHADOW_NLU_POLICY_VERSION = "shadow-rule-policy-1.0"
MAX_SHADOW_NLU_INPUT_LENGTH = 20_000


class ShadowNLUError(ValueError):
    """Raised when shadow NLU input or measurement data is invalid."""


class UrgencyLevel(str, Enum):
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True, slots=True)
class _IntentRule:
    intent: str
    router_name: str
    patterns: tuple[tuple[re.Pattern[str], float, str], ...]


@dataclass(frozen=True, slots=True)
class _IntentScore:
    intent: str
    router_name: str
    confidence: float
    evidence_codes: tuple[str, ...]


def _compiled(pattern: str) -> re.Pattern[str]:
    return re.compile(pattern, re.IGNORECASE)


_INTENT_RULES = (
    _IntentRule(
        "Memory Storage",
        "memory_storage",
        (
            (_compiled(r"^(?:remember|save|store|memorize)\s+(?:that\s+)?"), 0.88, "memory_store_prefix"),
            (_compiled(r"\b(?:save|store)\b.*\b(?:memory|permanently)\b"), 0.90, "memory_store_explicit"),
            (_compiled(r"\b(?:don't|do not)\s+forget\b"), 0.90, "memory_do_not_forget"),
            (_compiled(r"\b(?:update|edit|change|delete|remove|clear)\b.*\bmemor(?:y|ies)\b"), 0.88, "memory_mutation"),
        ),
    ),
    _IntentRule(
        "Memory Recall",
        "memory_recall",
        (
            (_compiled(r"^(?:do\s+you\s+remember|can\s+you\s+recall|recall|remind\s+me)\b"), 0.92, "memory_recall_prefix"),
            (_compiled(r"^(?:search|look\s+up|show|list)\s+(?:my\s+)?memor(?:y|ies)\b"), 0.92, "memory_recall_command"),
            (_compiled(r"^memory\s+(?:list|show|search|recall)\b"), 0.96, "memory_direct_command"),
            (_compiled(r"\bwhat\s+do\s+you\s+know\s+about\s+(?:me|my)\b"), 0.88, "memory_personal_query"),
            (_compiled(r"^(?:what|who|where|when)\s+(?:is|are|was|were)\s+my\b"), 0.84, "memory_possessive_query"),
        ),
    ),
    _IntentRule(
        "Debugging",
        "debugging",
        (
            (_compiled(r"\b(?:traceback|stack\s+trace|exception|debug(?:ging)?|error:)\b"), 0.84, "debug_failure_term"),
            (_compiled(r"\bfix\s+(?:this\s+|the\s+)?bug\b"), 0.86, "debug_fix_bug"),
            (_compiled(r"\bwhy\s+(?:does|is|did)\b.*\b(?:fail|error|crash|broken)\b"), 0.76, "debug_failure_question"),
        ),
    ),
    _IntentRule(
        "Code Analysis",
        "code_analysis",
        (
            (_compiled(r"\b(?:review|analy[sz]e|audit|explain)\b.*\b(?:code|script|function|class|implementation)\b"), 0.84, "code_analysis_action"),
            (_compiled(r"\bcode\s+review\b"), 0.88, "code_review_phrase"),
        ),
    ),
    _IntentRule(
        "Coding",
        "coding",
        (
            (_compiled(r"\b(?:write|create|generate|implement|build)\b.*\b(?:code|script|function|class|api|program)\b"), 0.82, "code_creation_action"),
            (_compiled(r"^aider\s+"), 0.97, "aider_direct_command"),
            (_compiled(r"\b(?:python|javascript|typescript|rust|sql|html|css)\b.*\b(?:code|function|script|implementation)\b"), 0.75, "code_language_context"),
        ),
    ),
    _IntentRule(
        "Calculation",
        "calculation",
        (
            (_compiled(r"\b(?:calculate|compute|solve|arithmetic|percentage|equation)\b"), 0.86, "calculation_term"),
            (_compiled(r"^[\d\s.+*/()%=-]+$"), 0.94, "calculation_expression"),
        ),
    ),
    _IntentRule(
        "Creative Writing",
        "creative_writing",
        (
            (_compiled(r"\b(?:write|create|draft)\b.*\b(?:story|poem|lyrics|fiction|scene|character|novel)\b"), 0.86, "creative_writing_action"),
            (_compiled(r"\b(?:story|poem|fiction|novel)\s+(?:about|where|in which)\b"), 0.74, "creative_subject"),
        ),
    ),
    _IntentRule(
        "Research",
        "research",
        (
            (_compiled(r"\b(?:research|web\s+search|search\s+the\s+web|look\s+online|find\s+sources)\b"), 0.88, "research_explicit"),
            (_compiled(r"\b(?:latest|current)\b.*\b(?:sources|information|news|version|release)\b"), 0.78, "research_current_info"),
        ),
    ),
    _IntentRule(
        "Planning / Architecture",
        "planning_architecture",
        (
            (_compiled(r"\b(?:plan|planning|architecture|architect|roadmap|system\s+design)\b"), 0.80, "planning_term"),
            (_compiled(r"\bdesign\s+(?:a|an|the)\s+system\b"), 0.84, "system_design_action"),
        ),
    ),
    _IntentRule(
        "Decision Support",
        "decision_support",
        (
            (_compiled(r"\b(?:compare|choose|decide|decision|pros\s+and\s+cons|tradeoffs?)\b"), 0.79, "decision_term"),
            (_compiled(r"\b(?:which\s+should|should\s+i)\b"), 0.76, "decision_question"),
        ),
    ),
    _IntentRule(
        "Personalization",
        "personalization",
        (
            (_compiled(r"\b(?:set|change|adjust|prefer)\b.*\b(?:tone|style|personality|preference|verbosity|theme)\b"), 0.86, "personalization_setting"),
            (_compiled(r"\bhow\s+you\s+(?:speak|respond|write)\b"), 0.74, "personalization_response_style"),
        ),
    ),
    _IntentRule(
        "Teaching / Learning",
        "teaching_learning",
        (
            (_compiled(r"\b(?:teach|teach\s+me|help\s+me\s+learn|lesson|tutorial)\b"), 0.82, "teaching_explicit"),
            (_compiled(r"\b(?:how\s+does|explain\s+how|explain\s+why)\b"), 0.74, "teaching_explanation"),
        ),
    ),
    _IntentRule(
        "System Command",
        "system_command",
        (
            (_compiled(r"^(?:shell|n8n|playbook|model)\b"), 0.95, "system_direct_command"),
            (_compiled(r"^status(?:\s|$)"), 0.95, "status_direct_command"),
            (_compiled(r"^help(?:\s+(?:commands?|topics?|system|status))?$"), 0.95, "help_direct_command"),
            (_compiled(r"\b(?:start|stop|restart)\b.*\b(?:service|server|system)\b"), 0.84, "system_service_command"),
        ),
    ),
)

_ROUTER_INTENT_ALIASES = {
    "conversation": "conversation",
    "creative_writing": "creative_writing",
    "coding": "coding",
    "code_analysis": "code_analysis",
    "debugging": "debugging",
    "calculation": "calculation",
    "memory_recall": "memory_recall",
    "memory_storage": "memory_storage",
    "system_command": "system_command",
    "research": "research",
    "planning_architecture": "planning_architecture",
    "decision_support": "decision_support",
    "personalization": "personalization",
    "teaching_learning": "teaching_learning",
}

_DIRECT_COMMAND_PREFIXES = (
    "aider ",
    "shell ",
    "n8n ",
    "playbook ",
    "model ",
    "memory ",
)
_DIRECT_COMMAND_EXACT = frozenset({"status", "help"})


@dataclass(frozen=True, slots=True)
class ShadowNLUAnalysis:
    """Non-authoritative observation containing the canonical NLU contract."""

    MODE: ClassVar[str] = SHADOW_NLU_MODE
    AUTHORITATIVE: ClassVar[bool] = SHADOW_NLU_AUTHORITATIVE

    nlu_result: NLUResult
    memory_intent: str
    urgency: UrgencyLevel
    routing_hints: tuple[str, ...]
    latency_ms: float
    confidence_policy_version: str = SHADOW_NLU_POLICY_VERSION
    current_router_intent: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.nlu_result, NLUResult):
            raise ShadowNLUError("nlu_result must use the Phase 0A NLUResult contract")
        if not isinstance(self.memory_intent, str) or not self.memory_intent:
            raise ShadowNLUError("memory_intent must be a non-empty string")
        if not isinstance(self.urgency, UrgencyLevel):
            try:
                object.__setattr__(self, "urgency", UrgencyLevel(self.urgency))
            except (TypeError, ValueError) as exc:
                raise ShadowNLUError("invalid urgency level") from exc
        if isinstance(self.routing_hints, str):
            raise ShadowNLUError("routing_hints must be a sequence, not a string")
        if not isinstance(self.routing_hints, tuple):
            try:
                object.__setattr__(self, "routing_hints", tuple(self.routing_hints))
            except TypeError as exc:
                raise ShadowNLUError("routing_hints must be a sequence") from exc
        if any(not isinstance(item, str) or not item for item in self.routing_hints):
            raise ShadowNLUError("routing_hints must contain non-empty strings")
        if (
            isinstance(self.latency_ms, bool)
            or not isinstance(self.latency_ms, (int, float))
            or not math.isfinite(float(self.latency_ms))
            or self.latency_ms < 0
        ):
            raise ShadowNLUError("latency_ms must be a finite non-negative number")
        if self.current_router_intent is not None and (
            not isinstance(self.current_router_intent, str)
            or not self.current_router_intent.strip()
        ):
            raise ShadowNLUError("current_router_intent must be None or a non-empty string")

    @property
    def intent(self) -> str:
        return self.nlu_result.primary_intent

    @property
    def entities(self) -> tuple[Entity, ...]:
        return self.nlu_result.entities

    @property
    def confidence(self) -> float | None:
        return self.nlu_result.intent_confidence

    @property
    def temporal_scope(self) -> TemporalScope:
        return self.nlu_result.temporal_scope

    @property
    def provenance(self) -> Mapping[str, str]:
        return self.nlu_result.provenance

    @property
    def schema_version(self) -> str:
        return self.nlu_result.schema_version

    @property
    def warnings(self) -> tuple[str, ...]:
        return self.nlu_result.warnings

    @property
    def matches_current_router(self) -> bool | None:
        if self.current_router_intent is None:
            return None
        router_intent = _ROUTER_INTENT_ALIASES.get(
            self.current_router_intent.strip().lower(),
            self.current_router_intent.strip().lower(),
        )
        shadow_router_name = next(
            (
                rule.router_name
                for rule in _INTENT_RULES
                if rule.intent == self.nlu_result.primary_intent
            ),
            "conversation",
        )
        return router_intent == shadow_router_name

    def to_dict(self) -> dict[str, Any]:
        contract = self.nlu_result.to_dict()
        return {
            "mode": self.MODE,
            "authoritative": self.AUTHORITATIVE,
            "schema_version": self.schema_version,
            "trace_id": self.nlu_result.trace_id,
            "intent": self.intent,
            "entities": contract["entities"],
            "confidence": self.confidence,
            "memory_intent": self.memory_intent,
            "temporal_scope": self.temporal_scope.value,
            "urgency": self.urgency.value,
            "routing_hints": list(self.routing_hints),
            "provenance": dict(self.provenance),
            "warnings": list(self.warnings),
            "latency_ms": self.latency_ms,
            "confidence_policy_version": self.confidence_policy_version,
            "current_router_intent": self.current_router_intent,
            "matches_current_router": self.matches_current_router,
            "nlu_result": contract,
        }

    def to_json(self, *, indent: int | None = None) -> str:
        return json.dumps(
            self.to_dict(),
            ensure_ascii=False,
            allow_nan=False,
            indent=indent,
            sort_keys=True,
        )


def _score_intents(text: str) -> tuple[_IntentScore, ...]:
    scores: list[_IntentScore] = []
    for rule in _INTENT_RULES:
        evidence: list[str] = []
        weights: list[float] = []
        for pattern, weight, evidence_code in rule.patterns:
            if pattern.search(text):
                evidence.append(evidence_code)
                weights.append(weight)
        if not weights:
            continue
        confidence = min(0.99, max(weights) + 0.02 * (len(weights) - 1))
        scores.append(
            _IntentScore(
                intent=rule.intent,
                router_name=rule.router_name,
                confidence=round(confidence, 3),
                evidence_codes=tuple(evidence),
            )
        )
    return tuple(sorted(scores, key=lambda item: item.confidence, reverse=True))


def _memory_signals(text: str, temporal_scope: TemporalScope) -> tuple[str, ...]:
    signals: list[str] = []
    patterns = (
        ("delete", r"\b(?:forget|delete|remove|erase|clear)\b.*\b(?:memory|memories|that|this)\b"),
        ("update", r"\b(?:update|edit|change|correct)\b.*\b(?:memory|memories|remembered)\b"),
        ("store", r"(?:^(?:remember|save|store|memorize)\s+(?:that\s+)?|\b(?:don't|do not)\s+forget\b|\b(?:save|store)\b.*\bmemory\b)"),
        ("recall", r"(?:\b(?:recall|remind\s+me|do\s+you\s+remember)\b|\b(?:show|list|search)\b.*\bmemor(?:y|ies)\b|^memory\s+(?:list|show|search|recall)\b)"),
    )
    for signal, pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            signals.append(signal)
    if temporal_scope is TemporalScope.TEMPORARY:
        signals.append("scoped_context")
    if not signals and re.search(
        r"\b(?:my\s+[A-Za-z][\w -]{0,40}\s+is|i\s+(?:prefer|like|use|work\s+on))\b",
        text,
        re.IGNORECASE,
    ):
        signals.append("candidate")
    return tuple(dict.fromkeys(signals))


def _primary_memory_intent(signals: tuple[str, ...]) -> str:
    for intent in ("delete", "update", "store", "recall", "scoped_context", "candidate"):
        if intent in signals:
            return intent
    return "none"


def _temporal_scope(text: str) -> TemporalScope:
    rules = (
        (TemporalScope.TEMPORARY, r"\b(?:for\s+now|temporar(?:y|ily)|this\s+conversation|until\s+further\s+notice)\b"),
        (TemporalScope.PERSISTENT, r"\b(?:permanent(?:ly)?|always|from\s+now\s+on|remember\s+that|don't\s+forget)\b"),
        (TemporalScope.HISTORICAL, r"\b(?:yesterday|previous(?:ly)?|in\s+the\s+past|last\s+(?:week|month|year)|used\s+to)\b"),
        (TemporalScope.FUTURE, r"\b(?:tomorrow|next\s+(?:week|month|year)|later|in\s+the\s+future|will\s+be)\b"),
        (TemporalScope.PRESENT, r"\b(?:right\s+now|currently|today|at\s+present)\b"),
    )
    for scope, pattern in rules:
        if re.search(pattern, text, re.IGNORECASE):
            return scope
    return TemporalScope.UNKNOWN


def _context_scope(text: str) -> ContextScope:
    if re.search(r"\b(?:global|globally|system-wide|all\s+users)\b", text, re.IGNORECASE):
        return ContextScope.GLOBAL
    if re.search(r"\b(?:project|repository|repo|codebase|workspace)\b", text, re.IGNORECASE):
        return ContextScope.PROJECT
    if re.search(
        r"\b(?:my\s+(?:profile|account|preference|favorite|name|editor)|"
        r"about\s+me|i\s+(?:prefer|like|use))\b",
        text,
        re.IGNORECASE,
    ):
        return ContextScope.USER
    return ContextScope.CONVERSATION


def _urgency(text: str) -> tuple[UrgencyLevel, float | None, int]:
    critical_matches = re.findall(
        r"\b(?:emergency|critical|security\s+breach|data\s+loss|production\s+outage)\b",
        text,
        re.IGNORECASE,
    )
    if critical_matches:
        return UrgencyLevel.CRITICAL, min(0.99, 0.90 + 0.02 * (len(critical_matches) - 1)), len(critical_matches)
    high_matches = re.findall(
        r"\b(?:urgent|urgently|asap|immediately|right\s+away|time-sensitive)\b",
        text,
        re.IGNORECASE,
    )
    if high_matches:
        return UrgencyLevel.HIGH, min(0.98, 0.86 + 0.02 * (len(high_matches) - 1)), len(high_matches)
    return UrgencyLevel.NORMAL, None, 0


def _tool_signals(text: str, primary_intent: str) -> tuple[str, ...]:
    signals: list[str] = []
    normalized = text.strip().lower()
    if primary_intent == "Research" or re.search(r"\b(?:web|online|sources)\b", text, re.IGNORECASE):
        signals.append("web")
    if primary_intent == "Calculation":
        signals.append("calculation")
    if normalized.startswith("shell "):
        signals.append("shell")
    if normalized.startswith("aider "):
        signals.append("aider")
    if normalized.startswith("n8n "):
        signals.append("n8n")
    if re.search(r"\b(?:run|execute)\b.*\b(?:code|script|command)\b", text, re.IGNORECASE):
        signals.append("execution_candidate")
    return tuple(dict.fromkeys(signals))


def _routing_hints(
    primary_router_name: str,
    memory_signals: tuple[str, ...],
    tool_signals: tuple[str, ...],
    planning_required: bool,
) -> tuple[str, ...]:
    hints = [f"intent_candidate:{primary_router_name}"]
    hints.extend(f"memory_candidate:{signal}" for signal in memory_signals)
    hints.extend(f"tool_candidate:{signal}" for signal in tool_signals)
    if planning_required:
        hints.append("planning_candidate:recommended")
    if not memory_signals and not tool_signals and not planning_required:
        hints.append("response_candidate:direct")
    return tuple(hints)


def _entities(text: str) -> tuple[Entity, ...]:
    found: list[Entity] = []
    occupied: list[tuple[int, int]] = []

    def add(match: re.Match[str], entity_type: str, confidence: float, group: int = 0) -> None:
        start, end = match.span(group)
        if any(start < used_end and end > used_start for used_start, used_end in occupied):
            return
        original = match.group(group)
        normalized = original.strip().lower() if entity_type in {"date", "time", "quantity"} else original.strip()
        found.append(
            Entity(
                normalized_value=normalized,
                original_text=original,
                entity_type=entity_type,
                confidence=confidence,
                source_location=f"message:{start}-{end}",
            )
        )
        occupied.append((start, end))

    patterns = (
        (r"\b\d{4}-\d{2}-\d{2}\b", "date", 0.99, 0),
        (r"\b(?:today|tomorrow|yesterday|next\s+(?:week|month|year)|last\s+(?:week|month|year))\b", "date", 0.94, 0),
        (r"\b\d{1,2}:\d{2}(?:\s?(?:am|pm))?\b", "time", 0.96, 0),
        (r"\bproject\s+(?:named|called)\s+([A-Z][\w.-]*)", "project", 0.94, 1),
        (r"\b(?:AI|assistant|system)\s+(?:named|called)\s+([A-Z][\w.-]*)", "system", 0.94, 1),
        (r"\bAetheraeon\b", "named_concept", 0.86, 0),
        (r'"([^"\n]{2,80})"', "named_concept", 0.78, 1),
        (r"(?<![\w.-])\d+(?:\.\d+)?%?(?![\w.-])", "quantity", 0.96, 0),
    )
    for pattern, entity_type, confidence, group in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            add(match, entity_type, confidence, group)
    return tuple(sorted(found, key=lambda entity: int(entity.source_location.split(":", 1)[1].split("-", 1)[0])))


def _warnings(
    text: str,
    scores: tuple[_IntentScore, ...],
    confidence: float | None,
    memory_signals: tuple[str, ...],
) -> tuple[str, ...]:
    warnings: list[str] = []
    if confidence is None or confidence < 0.65:
        warnings.append("low_confidence")
    if len(scores) > 1:
        warnings.append("multiple_intents")
        if scores[0].confidence - scores[1].confidence < 0.08:
            warnings.append("ambiguous_primary_intent")
    if len({signal for signal in memory_signals if signal in {"store", "update", "delete", "recall"}}) > 1:
        warnings.append("ambiguous_memory_intent")
    if re.search(r"\b(?:hypothetically|suppose|imagine|what\s+if)\b", text, re.IGNORECASE):
        warnings.append("hypothetical")
    if '"' in text:
        warnings.append("quotation")
    if re.search(r"\b(?:password|credential|api[ _-]?key|access[ _-]?token|secret)\b", text, re.IGNORECASE):
        warnings.append("sensitivity")
    return tuple(dict.fromkeys(warnings))


def _direct_command(text: str) -> bool:
    normalized = text.strip().lower()
    if normalized in _DIRECT_COMMAND_EXACT:
        return True
    return any(
        normalized.startswith(prefix)
        for prefix in _DIRECT_COMMAND_PREFIXES
    )


def analyze_shadow(
    user_input: str,
    *,
    trace_id: str | None = None,
    current_router_intent: str | None = None,
    monotonic_clock: Callable[[], float] | None = None,
) -> ShadowNLUAnalysis:
    """Produce a non-authoritative structured NLU observation.

    ``current_router_intent`` is never imported or calculated here.  A caller may
    provide it solely to compare the already-authoritative router result with the
    shadow classification.
    """

    if not isinstance(user_input, str):
        raise ShadowNLUError("user_input must be a string")
    text = user_input.strip()
    if not text:
        raise ShadowNLUError("user_input must not be empty")
    if len(text) > MAX_SHADOW_NLU_INPUT_LENGTH:
        raise ShadowNLUError(
            f"user_input exceeds the {MAX_SHADOW_NLU_INPUT_LENGTH} character shadow limit"
        )

    clock = monotonic_clock or time.perf_counter
    started = float(clock())
    if not math.isfinite(started):
        raise ShadowNLUError("monotonic clock must return finite numbers")

    scores = _score_intents(text)
    if scores:
        primary = scores[0]
        secondary = tuple(score.intent for score in scores[1:4])
        confidence: float | None = scores[0].confidence
    else:
        primary = _IntentScore("Conversation", "conversation", 0.0, ())
        secondary = ()
        confidence = None

    temporal_scope = _temporal_scope(text)
    context_scope = _context_scope(text)
    memory_signals = _memory_signals(text, temporal_scope)
    memory_intent = _primary_memory_intent(memory_signals)
    urgency, urgency_confidence, urgency_evidence_count = _urgency(text)
    tool_signals = _tool_signals(text, primary.intent)
    entities = _entities(text)
    warnings = _warnings(text, scores, confidence, memory_signals)
    planning_required = primary.intent == "Planning / Architecture"
    routing_hints = _routing_hints(
        primary.router_name,
        memory_signals,
        tool_signals,
        planning_required,
    )
    provenance_source = (
        ProvenanceSource.DIRECT_COMMAND.value
        if _direct_command(text)
        else ProvenanceSource.RULE.value
    )
    provenance = {
        "primary_intent": provenance_source,
        "secondary_intents": ProvenanceSource.RULE.value,
        "intent_confidence": ProvenanceSource.RULE.value,
        "entities": ProvenanceSource.RULE.value,
        "facts": ProvenanceSource.RULE.value,
        "emotion.urgency": ProvenanceSource.RULE.value,
        "temporal_scope": ProvenanceSource.RULE.value,
        "context_scope": ProvenanceSource.RULE.value,
        "explicit_memory_instruction": provenance_source,
        "memory_signals": ProvenanceSource.RULE.value,
        "tool_signals": ProvenanceSource.RULE.value,
        "routing_hints": ProvenanceSource.RULE.value,
        "warnings": ProvenanceSource.RULE.value,
    }
    for score in scores:
        for evidence_code in score.evidence_codes:
            provenance[f"intent_evidence.{evidence_code}"] = ProvenanceSource.RULE.value

    contract = NLUResult(
        trace_id=trace_id or generate_correlation_id(),
        primary_intent=primary.intent,
        secondary_intents=secondary,
        intent_confidence=confidence,
        entities=entities,
        facts=(),
        emotion={
            "urgency": {
                "level": urgency.value,
                "confidence": urgency_confidence,
                "evidence_count": urgency_evidence_count,
            }
        },
        temporal_scope=temporal_scope,
        context_scope=context_scope,
        explicit_memory_instruction=any(
            signal in {"store", "recall", "update", "delete"}
            for signal in memory_signals
        ),
        memory_signals=memory_signals,
        tool_signals=tool_signals,
        provenance=provenance,
        warnings=warnings,
        schema_version=COGNITIVE_CONTRACT_SCHEMA_VERSION,
    )

    finished = float(clock())
    if not math.isfinite(finished):
        raise ShadowNLUError("monotonic clock must return finite numbers")
    latency_ms = max(0.0, (finished - started) * 1000.0)

    return ShadowNLUAnalysis(
        nlu_result=contract,
        memory_intent=memory_intent,
        urgency=urgency,
        routing_hints=routing_hints,
        latency_ms=latency_ms,
        current_router_intent=current_router_intent,
    )


class ShadowNaturalLanguageUnderstanding:
    """Stateless facade that can only return non-authoritative observations."""

    mode = SHADOW_NLU_MODE
    authoritative = SHADOW_NLU_AUTHORITATIVE

    def analyze(
        self,
        user_input: str,
        *,
        trace_id: str | None = None,
        current_router_intent: str | None = None,
        monotonic_clock: Callable[[], float] | None = None,
    ) -> ShadowNLUAnalysis:
        return analyze_shadow(
            user_input,
            trace_id=trace_id,
            current_router_intent=current_router_intent,
            monotonic_clock=monotonic_clock,
        )


__all__ = [
    "SHADOW_NLU_MODE",
    "SHADOW_NLU_AUTHORITATIVE",
    "SHADOW_NLU_POLICY_VERSION",
    "MAX_SHADOW_NLU_INPUT_LENGTH",
    "ShadowNLUError",
    "UrgencyLevel",
    "ShadowNLUAnalysis",
    "ShadowNaturalLanguageUnderstanding",
    "analyze_shadow",
]
