"""Deterministic task calibration for Aetheraeon's dual cognition pipeline.

This module classifies cognitive priority only.  It does not execute actions,
retrieve memory, alter personality, or select tools.  The existing left- and
right-brain engines remain responsible for producing their structured signals.
"""

from dataclasses import dataclass
import re

from core.creative_cognition import (
    creative_generation_guidance,
    detect_creative_intent,
    extract_forbidden_concepts,
)


_TECHNICAL_ROUTES = {
    "coding",
    "code_analysis",
    "code_edit",
    "debugging",
    "calculation",
    "logical_reasoning",
}

_CREATIVE_ROUTES = {
    "creative_writing",
    "creative_ideation",
}

_TECHNICAL_DOMAIN = re.compile(
    r"\b(?:"
    r"programming|coding|code|debug(?:ging)?|bug|traceback|exception|"
    r"python|javascript|typescript|java|php|powershell|sql|mysql|mariadb|"
    r"database|schema|query|api|endpoint|frontend|backend|network(?:ing)?|"
    r"cybersecurity|security|rbac|acl|architecture|system design|"
    r"algorithm|function|class|method|operating systems?|kernel|process|"
    r"hardware|cpu|gpu|ram|ssd|memory module|motherboard|firmware|"
    r"mathematics?|arithmetic|algebra|geometry|equation|calculate|"
    r"logic problem|logical|troubleshoot(?:ing)?"
    r")\b",
    re.IGNORECASE,
)

_TECHNICAL_ACTION = re.compile(
    r"\b(?:explain|compare|list(?:\s+\w+){0,3}\s+causes|debug|review|"
    r"calculate|compute|solve|analy[sz]e|audit|diagnose|troubleshoot)\b",
    re.IGNORECASE,
)

_NEGATED_TECHNICAL_ACTION = re.compile(
    r"\b(?:do\s+not|don't|never|without|avoid(?:\s+trying\s+to)?)\s+"
    r"(?:explain|compare|debug|review|calculate|compute|solve|analy[sz]e|"
    r"audit|diagnose|troubleshoot)\b",
    re.IGNORECASE,
)

_LOGIC_STRUCTURE = re.compile(
    r"\b(?:every|all)\s+\w+\s+(?:is|are)\s+(?:a\s+)?\w+\b.*"
    r"\b(?:every|all)\s+\w+\s+(?:is|are)\s+(?:a\s+)?\w+\b",
    re.IGNORECASE | re.DOTALL,
)

_QUANTITATIVE_CHANGE = re.compile(
    r"\b(?:buys?|gives?|eats?|adds?|removes?|spends?|receives?|"
    r"another|half|remain|left|total)\b",
    re.IGNORECASE,
)

_ANALYTICAL_TASK_ACTION = re.compile(
    r"\b(?:design|architect|build|implement|review|debug|explain|compare|"
    r"calculate|compute|solve|analy[sz]e|audit|diagnose|troubleshoot)\b",
    re.IGNORECASE,
)

_MIXED_TASK_CONNECTOR = re.compile(
    r"\b(?:and|also|plus|with|as\s+well\s+as)\b|[.;]",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class CognitionCalibration:
    """Final cognitive priority and intent-confidence telemetry."""

    analytical: int
    creative: int
    routing_confidence: int
    priority: str
    reason: str
    creative_constraints_present: bool = False

    @property
    def prompt_guidance(self) -> str:
        if self.priority == "analytical":
            return (
                "COGNITION ROUTING: Use analytical reasoning as the dominant "
                f"mode ({self.analytical}% analytical, {self.creative}% creative). "
                "Detailed, friendly, example-driven, and step-by-step explanation "
                "is presentation style, not creative cognition."
            )
        if self.priority == "creative":
            return (
                "COGNITION ROUTING: Use creative cognition as the dominant mode "
                f"({self.creative}% creative, {self.analytical}% analytical). "
                + creative_generation_guidance(
                    self.creative_constraints_present
                )
            )
        if self.priority == "mixed":
            return (
                "COGNITION ROUTING: This request has distinct analytical and "
                "creative deliverables; keep both active "
                f"({self.analytical}% analytical, {self.creative}% creative). "
                + creative_generation_guidance(
                    self.creative_constraints_present
                )
            )
        return ""


def _is_quantitative_problem(text: str) -> bool:
    numbers = re.findall(r"\b\d+(?:\.\d+)?\b", text)
    return len(numbers) >= 2 and bool(_QUANTITATIVE_CHANGE.search(text))


def _has_affirmative_technical_action(text: str) -> bool:
    """Ignore analytical verbs that the user explicitly prohibited."""

    without_negated_actions = _NEGATED_TECHNICAL_ACTION.sub("", text)
    return bool(_TECHNICAL_ACTION.search(without_negated_actions))


def _is_mixed_request(text: str) -> bool:
    """Detect separate analytical and creative deliverables in one request."""

    clauses = [
        clause.strip()
        for clause in _MIXED_TASK_CONNECTOR.split(text)
        if clause.strip()
    ]
    if len(clauses) < 2:
        return False
    analytical_clause = any(
        _ANALYTICAL_TASK_ACTION.search(clause)
        and (
            _TECHNICAL_DOMAIN.search(clause)
            or _is_quantitative_problem(clause)
            or _LOGIC_STRUCTURE.search(clause)
        )
        for clause in clauses
    )
    creative_clause = any(detect_creative_intent(clause) for clause in clauses)
    return analytical_clause and creative_clause


def _routing_confidence(route: str, strong_domain_match: bool) -> int:
    if strong_domain_match or route in _TECHNICAL_ROUTES | _CREATIVE_ROUTES:
        return 95
    if route in {
        "memory_storage", "memory_recall", "conversation_memory",
        "filesystem_read", "filesystem_write", "filesystem_search",
        "project_search", "configuration", "administrative_action",
        "command_execution", "system_command", "research",
        "planning_architecture", "decision_support", "personalization",
        "teaching_learning",
    }:
        return 90
    if route == "question":
        return 75
    if route == "conversation":
        return 60
    return 70


def calibrate_cognition(
    user_input: str,
    route: str,
    analytical_signal_count: int = 0,
    creative_signal_count: int = 0,
) -> CognitionCalibration:
    """Calibrate cognition from task semantics, then fall back to signal counts.

    Technical and logical requests receive a deterministic analytical override.
    Explicit creative requests receive a creative override.  Requests outside
    those domains retain the legacy measured-signal ratio.
    """

    text = str(user_input or "").strip()
    normalized_route = str(route or "conversation").strip().lower()
    creative_request = normalized_route in _CREATIVE_ROUTES or bool(
        detect_creative_intent(text)
    )
    creative_constraints_present = bool(extract_forbidden_concepts(text))
    technical_domain = (
        normalized_route in _TECHNICAL_ROUTES
        or bool(_TECHNICAL_DOMAIN.search(text))
        or bool(_LOGIC_STRUCTURE.search(text))
        or _is_quantitative_problem(text)
    )
    technical_action = _has_affirmative_technical_action(text)

    if creative_request and _is_mixed_request(text):
        return CognitionCalibration(
            analytical=50,
            creative=50,
            routing_confidence=95,
            priority="mixed",
            reason="distinct analytical and creative tasks detected",
            creative_constraints_present=creative_constraints_present,
        )

    # Once routing establishes a pure creative request, raw signal counts and
    # analytical-sounding words inside its constraints cannot invert cognition.
    # Distinct technical deliverables were already preserved as mixed above.
    if creative_request:
        return CognitionCalibration(
            analytical=5,
            creative=95,
            routing_confidence=_routing_confidence(normalized_route, True),
            priority="creative",
            reason="explicit creative task detected",
            creative_constraints_present=creative_constraints_present,
        )

    if technical_domain:
        reason = (
            "technical domain and analytical action detected"
            if technical_action
            else "technical, mathematical, or logical domain detected"
        )
        return CognitionCalibration(
            analytical=95,
            creative=5,
            routing_confidence=_routing_confidence(normalized_route, True),
            priority="analytical",
            reason=reason,
        )

    analytical_count = max(0, int(analytical_signal_count or 0))
    creative_count = max(0, int(creative_signal_count or 0))
    total = analytical_count + creative_count
    if total:
        analytical = round(analytical_count * 100 / total)
        creative = 100 - analytical
    else:
        analytical = 0
        creative = 0

    return CognitionCalibration(
        analytical=analytical,
        creative=creative,
        routing_confidence=_routing_confidence(normalized_route, False),
        priority="measured",
        reason="legacy cognitive signal ratio retained",
    )
