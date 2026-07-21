"""
Aetheraeon AI - Request Router

Purpose:
Provides the current lightweight classification and dispatch layer for incoming requests.

Architecture Layer:
Core Intelligence Layer - system traffic control.

Responsibilities:
- Normalize routing inputs and identify current request domains and fast paths.
- Select the existing subsystem or orchestration path for a request.
- Return structured routing metadata to calling layers.

Boundaries:
- Routing signals are not permissions, tool authorization, memory authorization, or proof that a subsystem was used.
- This module does not perform deep reasoning or establish Cognitive Decision Engine policy.
- Natural Language Understanding and the Cognitive Decision Engine are planned services; security remains authoritative for every dispatched path.
"""


# ============================================================
# CORE STANDARD LIBRARY IMPORTS
# ============================================================
# Built-in Python modules used for parsing, routing logic,
# pattern matching, system control, and input normalization.
# ============================================================

import re          # Regex engine for intent detection + pattern matching
import os          # Environment / system access (light usage if needed)
import json        # Structured parsing for routing decisions (future expansion)
from dataclasses import dataclass


# ============================================================
# EXTERNAL DEPENDENCIES (PIP INSTALLED PACKAGES)
# ============================================================
# Third-party libraries installed via pip.
# Used for optional system integrations and API communication.
# ============================================================

import requests    # HTTP calls (only if router triggers external services)


# ============================================================
# INTERNAL SYSTEM IMPORTS (ARCHITECTURE LAYERS)
# ============================================================
# Core AI system modules (ALL located inside Core folder)
#
# RULES:
# - request_router = decision + routing layer ONLY
# - NO AI reasoning
# - NO tool execution
# - NO database access
# ============================================================

# ------------------------------------------------------------
# LLM / AI INTERFACE LAYER
# (Only referenced for metadata awareness or routing hints)
# ------------------------------------------------------------
from core import llm_interface


# ------------------------------------------------------------
# CONFIGURATION LAYER
# (System settings, runtime configuration access)
# ------------------------------------------------------------
from core import config_loader
from core import config_manager


# ------------------------------------------------------------
# TOOL SYSTEM LAYER
# (Tool registry + execution dispatcher reference)
# ------------------------------------------------------------
from core.tool_registry import get_tools
from core import tool_executor


# ------------------------------------------------------------
# MEMORY SYSTEM LAYER
# (Used ONLY for routing classification, not execution)
# ------------------------------------------------------------
from core import memory_interface
from core import memory_database


# ------------------------------------------------------------
# IDENTITY / PERSONALITY LAYER
# (Used for routing personality-related commands)
# ------------------------------------------------------------
from core import agent_identity
from core import personality_engine
from core.conversation_memory import is_conversation_only_memory_request
from core.creative_cognition import detect_creative_intent
from core.command_system import validate_slash_command


# ------------------------------------------------------------
# HELP SYSTEM
# (Used for dynamic help command routing)
# ------------------------------------------------------------
from core.help_system import build_help


# ------------------------------------------------------------
# SYSTEM UTILITIES
# (Input cleaning, timestamps, helpers if needed)
# ------------------------------------------------------------
from core import system_utils


# ============================================================
# MEMORY SAVE INTENT PATTERNS
# ============================================================

MEMORY_SAVE_PATTERNS = [
    r"^remember\s+.+=.+",
    r"^(?:please\s+)?remember\s+(?:permanently\s+)?(?:that\s+)?(?!when\b|what\b|where\b|who\b|how\b).+",
    r"^i\s+(?:want|need)\s+you\s+to\s+remember\s+(?:permanently\s+)?(?:that\s+)?(.+)",
    r"^save\s+this[:\s]",
    r"^store[:\s]",
    r"^don'?t\s+forget[:\s]",
    r"^make\s+a\s+note[:\s]",
    r"^note\s+that[:\s]",
    r"^keep\s+in\s+mind[:\s]",
    r"^log\s+this[:\s]",
]


# ============================================================
# MEMORY SEARCH INTENT PATTERNS
# ============================================================

MEMORY_SEARCH_PATTERNS = [
    r"^recall\s+",
    r"^look\s+up\s+in\s+memory",
    r"^search\s+memory\s+for",
    r"^remind\s+me\s+of",
]


# ============================================================
# MEMORY DELETE INTENT PATTERNS
# ============================================================

MEMORY_DELETE_PATTERNS = [
    r"^forget\s+(that|about|memory|this)",
    r"^remove\s+from\s+memory",
    r"^delete\s+from\s+memory",
    r"^erase\s+(that|from\s+memory)",
    r"^clear\s+that\s+(memory|from)",
]


# Classification-only action vocabulary.  These labels describe the request;
# they do not authorize a tool, select a filesystem scope, or execute anything.
_KNOWN_SYSTEM_COMMANDS = re.compile(
    r"\b(?:whoami|hostname|ipconfig|systeminfo|ping|tracert|nslookup|netstat|"
    r"tasklist|wmic|driverquery)\b",
    re.IGNORECASE,
)

_ADMINISTRATIVE_ACTION = re.compile(
    r"\b(?:manage|create|delete|disable|enable|lock|unlock|grant|revoke|reset|"
    r"change)\b.*\b(?:users?|accounts?|roles?|permissions?|access control|"
    r"agent mode|security boundar(?:y|ies))\b",
    re.IGNORECASE,
)

_COMMAND_EXECUTION = re.compile(
    r"\b(?:run|execute|launch|start)\b.*\b(?:command|script|program|executable|"
    r"process|service|python|powershell|cmd|batch)\b",
    re.IGNORECASE,
)

_CONFIGURATION_ACTION = re.compile(
    r"\b(?:configure|reconfigure|edit|change|update|create|read|inspect)\b.*"
    r"\b(?:configuration|config(?:uration)? file|environment variable|"
    r"server settings?|database settings?|application settings?)\b",
    re.IGNORECASE,
)

_CODE_EDIT_ACTION = re.compile(
    r"\b(?:edit|modify|update|change|refactor|patch)\b.*\b(?:code|script|"
    r"function|class|implementation|source file)\b",
    re.IGNORECASE,
)

_PROJECT_SEARCH_ACTION = re.compile(
    r"\b(?:search|find|locate|look for)\b.*\b(?:project|repository|repo|"
    r"codebase)\b|\b(?:search|find|locate)\b.*\bin (?:the |this )?"
    r"(?:project|repository|repo|codebase)\b",
    re.IGNORECASE,
)

_FILESYSTEM_READ_ACTION = re.compile(
    r"\b(?:read|open|show|view|display|inspect)\b.*\b(?:file|files|folder|"
    r"directory|directories|file contents|project files)\b",
    re.IGNORECASE,
)

_FILESYSTEM_SEARCH_ACTION = re.compile(
    r"\b(?:list|find|locate|search|enumerate)\b.*\b(?:file|files|folder|"
    r"folders|directory|directories|path|paths)\b",
    re.IGNORECASE,
)

_FILESYSTEM_WRITE_ACTION = re.compile(
    r"\b(?:create|write|save|delete|remove|rename|move|copy)\b.*\b(?:file|"
    r"files|folder|folders|directory|directories)\b",
    re.IGNORECASE,
)

_COMMAND_WORDS = (
    "open", "run", "delete", "remove", "show", "list", "edit", "copy",
    "move", "create", "execute", "shell",
)

_COMMAND_WORD_PATTERN = re.compile(
    r"\b(?:" + "|".join(_COMMAND_WORDS) + r")\b",
    re.IGNORECASE,
)

_ACTION_REQUEST_PATTERN = re.compile(
    r"^(?:(?:please)\s+)?(?P<action>open|run|delete|remove|show|list|edit|"
    r"create|copy|move|execute|shell|read|view|display|inspect|find|locate|"
    r"search|enumerate|write|save|rename|manage|configure|reconfigure|change|"
    r"update|refactor|patch|launch|start|grant|revoke|enable|disable|lock|"
    r"unlock|reset)\b(?P<target>.*)$|"
    r"^(?:can|could|would|will)\s+you\s+(?:please\s+)?"
    r"(?P<polite_action>open|run|delete|remove|show|list|edit|create|copy|"
    r"move|execute|shell|read|view|display|inspect|find|locate|search|"
    r"enumerate|write|save|rename|manage|configure|reconfigure|change|update|"
    r"refactor|patch|launch|start|grant|revoke|enable|disable|lock|unlock|"
    r"reset)\b(?P<polite_target>.*)$|"
    r"^i\s+(?:want|need|would\s+like)\s+you\s+to\s+"
    r"(?P<wanted_action>open|run|delete|remove|show|list|edit|create|copy|"
    r"move|execute|shell|read|view|display|inspect|find|locate|search|"
    r"enumerate|write|save|rename|manage|configure|reconfigure|change|update|"
    r"refactor|patch|launch|start|grant|revoke|enable|disable|lock|unlock|"
    r"reset)\b(?P<wanted_target>.*)$",
    re.IGNORECASE,
)

_INFORMATION_REQUEST_PATTERN = re.compile(
    r"^(?:what|why|how|when|where|who|which|is|are|do|does|did|should)\b|"
    r"^(?:can|could|would|will)\s+you\s+(?:explain|describe|define|tell|teach)\b|"
    r"^(?:please\s+)?(?:explain|describe|define|tell\s+me|teach\s+me)\b|"
    r"\b(?:how\s+to|what\s+does\s+.+\s+mean)\b",
    re.IGNORECASE,
)

_PAST_ACTION_STATEMENT = re.compile(
    r"^(?:(?:yesterday|earlier|previously|last\s+\w+)\s*,?\s+)?"
    r"(?:i|we)\s+(?:opened|ran|deleted|removed|showed|listed|edited|created|"
    r"copied|moved|executed)\b",
    re.IGNORECASE,
)

_RESPONSE_GENERATION_TARGET = re.compile(
    r"^(?:me\s+)?(?:an?\s+|the\s+)?(?:answer|example|explanation|summary|"
    r"story|poem|scene|character|idea|concept|plan|list\s+of\s+ideas|"
    r"code\s+example|code\s+snippet|(?:python|javascript|typescript|java|"
    r"rust|c\+\+|c#)?\s*code|function|class)\b",
    re.IGNORECASE,
)

_EXTERNAL_ACTION_TARGET = re.compile(
    r"\b(?:files?|folders?|director(?:y|ies)|paths?|projects?|repositories|"
    r"repos?|workspaces?|scripts?|commands?|programs?|executables?|processes?|"
    r"services?|backups?|accounts?|users?|settings?|config(?:uration)?|"
    r"documents?|applications?|apps?)\b|[a-z]:\\|(?:^|\s)[./~][\\/]",
    re.IGNORECASE,
)

_VAGUE_TARGET_REFERENCE = re.compile(
    r"^(?:my|this|that|these|those)\b",
    re.IGNORECASE,
)

_CONFIRMATION_ACTIONS = frozenset({
    "run", "delete", "remove", "edit", "create", "copy", "move",
    "execute", "shell", "write", "save", "rename", "manage", "configure",
    "reconfigure", "change", "update", "refactor", "patch", "launch",
    "start", "grant", "revoke", "enable", "disable", "lock", "unlock",
    "reset",
})

_CONFIRMED_STATES = frozenset({"confirmed", "approved", "yes", "true"})
_DENIED_STATES = frozenset({"denied", "rejected", "cancelled", "canceled", "no", "false"})


@dataclass(frozen=True, slots=True)
class InteractionIntentAnalysis:
    """Conversation/action separation without authorizing tool execution."""

    intent: str
    action: str | None
    target: str | None
    missing_details: tuple[str, ...]
    confirmation_required: bool
    confirmation_state: str
    ready_for_execution: bool
    reason: str


def _normalized_confirmation_state(confirmation_state) -> str:
    if confirmation_state is True:
        return "confirmed"
    if confirmation_state is False:
        return "denied"
    normalized = str(confirmation_state or "").strip().lower()
    if normalized in _CONFIRMED_STATES:
        return "confirmed"
    if normalized in _DENIED_STATES:
        return "denied"
    return "pending"


def _action_requires_confirmation(action: str) -> bool:
    write_shell_commands = getattr(tool_executor, "WRITE_ALLOWED_SHELL_COMMANDS", ())
    return action in _CONFIRMATION_ACTIONS or action in write_shell_commands


def _action_match_parts(match: re.Match[str]) -> tuple[str, str]:
    action = next(
        (match.group(name) for name in ("action", "polite_action", "wanted_action") if match.group(name)),
        "",
    )
    target = next(
        (match.group(name) for name in ("target", "polite_target", "wanted_target") if match.group(name) is not None),
        "",
    )
    return action.lower(), re.sub(r"^(?:me\s+)", "", target.strip(), flags=re.IGNORECASE)


def analyze_interaction_intent(
    user_input: str,
    *,
    confirmation_state=None,
) -> InteractionIntentAnalysis:
    """Separate conversational requests from requests to act on external state.

    This result is descriptive only.  It never grants permission or executes a
    tool.  Confirmation must be supplied as explicit caller state; words in the
    user's message are not treated as confirmation receipts.
    """

    normalized = re.sub(r"\s+", " ", str(user_input or "")).strip()
    lowered = normalized.lower()
    conversational_reason = "no external action requested"

    if not lowered:
        return InteractionIntentAnalysis(
            "conversation", None, None, (), False, "not_required", False,
            "empty input",
        )

    if _INFORMATION_REQUEST_PATTERN.search(lowered):
        return InteractionIntentAnalysis(
            "conversation", None, None, (), False, "not_required", False,
            "question or explanation request",
        )

    if _PAST_ACTION_STATEMENT.search(lowered):
        return InteractionIntentAnalysis(
            "conversation", None, None, (), False, "not_required", False,
            "past action described rather than requested",
        )

    match = _ACTION_REQUEST_PATTERN.match(normalized)
    if not match:
        # Recognized shell syntax is action-related, but a lone command token is
        # deliberately never execution-ready.
        if tool_executor.is_supported_shell_command(normalized):
            parts = normalized.split(maxsplit=1)
            action = parts[0].lower()
            target = parts[1].strip() if len(parts) > 1 else None
            missing = () if target else ("target_or_arguments",)
            requires_confirmation = _action_requires_confirmation(action)
            state = _normalized_confirmation_state(confirmation_state)
            if not requires_confirmation:
                state = "not_required"
            return InteractionIntentAnalysis(
                "action_request", action, target, missing,
                requires_confirmation, state,
                bool(target and (not requires_confirmation or state == "confirmed")),
                "recognized shell command syntax",
            )
        return InteractionIntentAnalysis(
            "conversation", None, None, (), False, "not_required", False,
            conversational_reason,
        )

    action, target = _action_match_parts(match)
    if (
        action in {"create", "write", "show", "display", "list"}
        and target
        and _RESPONSE_GENERATION_TARGET.search(target)
        and not _EXTERNAL_ACTION_TARGET.search(target)
    ):
        return InteractionIntentAnalysis(
            "conversation", None, None, (), False, "not_required", False,
            "requested content can be answered without an external action",
        )

    if not target:
        missing_details = ("target",)
    elif _VAGUE_TARGET_REFERENCE.search(target):
        missing_details = ("concrete_target",)
    else:
        missing_details = ()
    requires_confirmation = _action_requires_confirmation(action)
    state = _normalized_confirmation_state(confirmation_state)
    if not requires_confirmation:
        state = "not_required"
    ready = bool(
        target
        and not missing_details
        and (not requires_confirmation or state == "confirmed")
        and state != "denied"
    )
    return InteractionIntentAnalysis(
        "action_request", action, target or None, missing_details,
        requires_confirmation, state, ready,
        "imperative or direct request with an action verb",
    )


def classify_interaction_intent(user_input: str, *, confirmation_state=None) -> str:
    """Return ``conversation`` or ``action_request`` for execution gating."""

    return analyze_interaction_intent(
        user_input,
        confirmation_state=confirmation_state,
    ).intent

# Technical-domain classification is intentionally separate from explanation
# style.  Words such as "explain", "how", and "design" establish that the
# user is asking for analysis; the subject determines the authoritative route.
_TECHNICAL_ANALYSIS_CUE = re.compile(
    r"\b(?:explain|describe|teach|review|compare|design|architect|analy[sz]e|"
    r"audit|diagnose|debug|troubleshoot|how|why|what|should|prevent|control)\b",
    re.IGNORECASE,
)

_CODE_SECURITY_ANALYSIS = re.compile(
    r"\b(?:os\.system|subprocess(?:\.\w+)?|eval|exec)\s*\(|"
    r"\b(?:command|shell|code)\s+injection\b",
    re.IGNORECASE,
)

_CODE_IMPLEMENTATION_CONTEXT = re.compile(
    r"\b(?:python|javascript|typescript|node\.js|php|java|code|script|"
    r"functions?|methods?|classes?|api\s+endpoints?|json|seriali[sz]ation|"
    r"return\s+values?|response\s+bod(?:y|ies))\b|\bdef\s+\w+\s*\(",
    re.IGNORECASE,
)

_CODE_FAILURE_OR_REVIEW = re.compile(
    r"\b(?:debug(?:ging)?|troubleshoot(?:ing)?|review|bugs?|exceptions?|"
    r"errors?|stack\s+traces?|tracebacks?|fail(?:s|ed|ure)?|broken|"
    r"empty\s+response|missing\s+response|json\s+response\s+problems?|"
    r"seriali[sz]ation\s+(?:issues?|problems?|errors?|failures?)|"
    r"returns?\s+(?:none|null|empty)|missing\s+return|most\s+likely\s+causes)\b",
    re.IGNORECASE,
)

_SECURITY_ARCHITECTURE_DOMAIN = re.compile(
    r"\b(?:permissions?|authorization|authentication|access control|rbac|acl|"
    r"role[ -]based|privileges?|sandbox|execute permission|execution rights|"
    r"file access|file execution|security model|security architecture|"
    r"user roles?|admin permissions?|running programs?|execute programs?)\b",
    re.IGNORECASE,
)

_DATABASE_ARCHITECTURE_DOMAIN = re.compile(
    r"\b(?:database|schema|tables?|columns?|indexes?|sql|migrations?|"
    r"foreign keys?|relationships?|normalization|data model|database design)\b",
    re.IGNORECASE,
)

_SYSTEM_ARCHITECTURE_DOMAIN = re.compile(
    r"\b(?:front[ -]?end|back[ -]?end|api|gateway|microservices?|components?|"
    r"service boundaries|system design|deployment design|scalability)\b",
    re.IGNORECASE,
)

_ARCHITECTURE_DESIGN_CUE = re.compile(
    r"\b(?:design|architect|architecture|boundaries|components?|scalability|"
    r"separation|tradeoffs?|decisions?)\b",
    re.IGNORECASE,
)

_INFRASTRUCTURE_ANALYSIS_DOMAIN = re.compile(
    r"\b(?:servers?|networks?|ports?|firewalls?|apache|configuration|"
    r"deployment|services?|linux|windows server|cpu|memory pressure|"
    r"disk(?:\s+space|\s+usage)?|production outage|database\s+(?:server|"
    r"outage|availability|connection failure|operational problem))\b",
    re.IGNORECASE,
)

_TECHNICAL_INTENT_CONTEXT = {
    "security_architecture": "security architecture permissions authorization",
    "database_architecture": "database architecture schema sql",
    "system_architecture": "system architecture api components",
    "infrastructure_analysis": (
        "system architecture networking operating systems infrastructure"
    ),
    "code_analysis": "code analysis programming",
}


def cognition_routing_context(user_input: str, route: str) -> str:
    """Attach descriptive technical intent without changing the user request.

    The returned text is only an input to cognition selection.  It does not
    alter command routing, authorization, tool inputs, or the final user prompt.
    """

    intent_context = _TECHNICAL_INTENT_CONTEXT.get(str(route or "").lower())
    if not intent_context:
        return str(user_input or "")
    return f"{intent_context}\n{str(user_input or '')}"

def slash_command_spec(user_input: str) -> dict | None:
    """Parse an explicit slash-prefixed command without executing it."""

    validation = validate_slash_command(user_input)
    if validation is None:
        return None
    if validation.definition is None:
        return {
            "intent": "unknown_slash_command",
            "legacy_command": None,
            "validation_status": validation.status,
        }
    definition = validation.definition
    intent = (
        "command_suggestions"
        if validation.status == "suggestions"
        else definition.intent
    )
    return {
        "name": definition.command.lstrip("/").split(" ", 1)[0],
        "intent": intent,
        "legacy_command": validation.effective_command,
        "description": definition.description,
        "validation_status": validation.status,
    }


def normalize_slash_command(user_input: str) -> str | None:
    spec = slash_command_spec(user_input)
    return spec.get("legacy_command") if spec else None


def classify_command_utterance(user_input: str, *, confirmation_state=None) -> str:
    """Describe command directness without authorizing or executing anything."""

    normalized = re.sub(r"\s+", " ", str(user_input or "")).strip().lower()
    if not normalized:
        return "not_command_related"

    supported_shell_syntax = tool_executor.is_supported_shell_command(normalized)
    if not _COMMAND_WORD_PATTERN.search(normalized) and not supported_shell_syntax:
        return "not_command_related"

    analysis = analyze_interaction_intent(
        normalized,
        confirmation_state=confirmation_state,
    )
    if analysis.intent == "conversation":
        return "question" if _INFORMATION_REQUEST_PATTERN.search(normalized) else "conversation"

    if re.match(
        r"^(?:can|could|would|will) you\b|^(?:please\s+)?(?:can|could|would)\b|"
        r"^i (?:want|need) you to\b",
        normalized,
    ):
        return "action_request"

    command_prefix = re.match(
        r"^(?:" + "|".join(_COMMAND_WORDS) + r")\b",
        normalized,
    )
    if command_prefix:
        # Compound natural-language instructions must go through the normal AI
        # path instead of executing the first recognized verb as a shell line.
        if re.search(r"\b(?:and|then)\b|\btell me\b|\bexplain\b", normalized):
            return "action_request"
        if re.search(r"\b(?:my|this|these|those)\b", analysis.target or ""):
            return "action_request"
        return "direct_command" if analysis.ready_for_execution else "action_request"

    if supported_shell_syntax:
        return "direct_command" if analysis.ready_for_execution else "action_request"

    return "action_request"

# ============================================================
# REQUEST CLASSIFICATION
# Detects the type of user request for early system routing.
# ============================================================

def classify_request(user_input: str) -> tuple[str, str]:

    # --------------------------------------------------------
    # INPUT NORMALIZATION
    # Convert input into lowercase safe text for matching.
    # --------------------------------------------------------

    normalized_input = (user_input or "").strip().lower()
    interaction_intent = classify_interaction_intent(normalized_input)
    is_action_request = interaction_intent == "action_request"

    if is_conversation_only_memory_request(normalized_input):
        return (
            "conversation_memory",
            "explicit memory request scoped to the active conversation",
        )

    if any(re.match(pattern, normalized_input) for pattern in MEMORY_SAVE_PATTERNS):
        return ("memory_storage", "explicit long-term memory storage request")

    memory_recall_patterns = (
        r"^(?:what|who|where|when)\s+(?:is|are|was|were)\s+my\b",
        r"^what\s+do\s+you\s+know\s+about\s+(?:my|me)\b",
        r"^(?:do\s+you\s+remember|can\s+you\s+recall|recall|remind\s+me)\b",
        r"^(?:search|look\s+up)\s+(?:my\s+)?memor(?:y|ies)\b",
    )
    if any(re.search(pattern, normalized_input) for pattern in memory_recall_patterns):
        return ("memory_recall", "request for stored personal information")

    # Preserve the established system-command route for known shell commands.
    # The broader execution label below remains descriptive only.
    if is_action_request and _KNOWN_SYSTEM_COMMANDS.search(normalized_input):
        return ("system_command", "system command keywords")

    # Technical subjects take precedence over generic explanation or teaching
    # style.  These routes describe analysis only and authorize no action.
    if (
        _TECHNICAL_ANALYSIS_CUE.search(normalized_input)
        and _CODE_SECURITY_ANALYSIS.search(normalized_input)
    ):
        return ("code_analysis", "code execution security analysis request")

    if (
        _CODE_IMPLEMENTATION_CONTEXT.search(normalized_input)
        and _CODE_FAILURE_OR_REVIEW.search(normalized_input)
    ):
        return (
            "code_analysis",
            "code implementation, backend API, or serialization failure analysis",
        )

    if (
        _TECHNICAL_ANALYSIS_CUE.search(normalized_input)
        and _SECURITY_ARCHITECTURE_DOMAIN.search(normalized_input)
    ):
        return (
            "security_architecture",
            "security, permissions, or access-control design request",
        )

    if (
        _ARCHITECTURE_DESIGN_CUE.search(normalized_input)
        and _SYSTEM_ARCHITECTURE_DOMAIN.search(normalized_input)
    ):
        return (
            "system_architecture",
            "system component, service-boundary, or API architecture request",
        )

    if (
        _TECHNICAL_ANALYSIS_CUE.search(normalized_input)
        and _INFRASTRUCTURE_ANALYSIS_DOMAIN.search(normalized_input)
    ):
        return (
            "infrastructure_analysis",
            "infrastructure, deployment, or operations analysis request",
        )

    if (
        _TECHNICAL_ANALYSIS_CUE.search(normalized_input)
        and _SYSTEM_ARCHITECTURE_DOMAIN.search(normalized_input)
    ):
        return (
            "system_architecture",
            "system component or API architecture request",
        )

    if (
        _TECHNICAL_ANALYSIS_CUE.search(normalized_input)
        and _DATABASE_ARCHITECTURE_DOMAIN.search(normalized_input)
    ):
        return (
            "database_architecture",
            "database schema or data-architecture request",
        )

    if is_action_request and _ADMINISTRATIVE_ACTION.search(normalized_input):
        return (
            "administrative_action",
            "administrative request; authorization remains external to routing",
        )

    if is_action_request and _COMMAND_EXECUTION.search(normalized_input):
        return (
            "command_execution",
            "execution request; classification does not authorize execution",
        )

    if is_action_request and _CONFIGURATION_ACTION.search(normalized_input):
        return ("configuration", "configuration request")

    if is_action_request and _PROJECT_SEARCH_ACTION.search(normalized_input):
        return ("project_search", "project or repository search request")

    if is_action_request and _FILESYSTEM_READ_ACTION.search(normalized_input):
        return ("filesystem_read", "filesystem read request")

    if is_action_request and _FILESYSTEM_SEARCH_ACTION.search(normalized_input):
        return ("filesystem_search", "filesystem search or listing request")

    if is_action_request and _FILESYSTEM_WRITE_ACTION.search(normalized_input):
        return (
            "filesystem_write",
            "filesystem mutation request; classification does not authorize writes",
        )

    if is_action_request and _CODE_EDIT_ACTION.search(normalized_input):
        return ("code_edit", "existing code edit request")

    if re.search(r"\b(traceback|stack trace|debug|debugging|fix (?:this |the )?bug|exception|error:)\b", normalized_input):
        return ("debugging", "debugging or failure-analysis request")

    if re.search(r"\b(review|analy[sz]e|audit|explain)\b.*\b(code|script|function|class|implementation)\b", normalized_input):
        return ("code_analysis", "code inspection or explanation request")

    if re.search(r"\b(write|create|generate|implement|build)\b.*\b(code|script|function|class|api|program)\b", normalized_input):
        return ("coding", "code creation request")

    # Once action, filesystem, code, security, and database routes have had
    # precedence, explicit invention/worldbuilding intent must precede numeric
    # heuristics.  Numbered creative requirements describe output structure;
    # they do not turn the request into a calculation.
    creative_intent = detect_creative_intent(normalized_input)
    if creative_intent == "creative_writing":
        return (
            "creative_writing",
            "creative writing, fiction, or worldbuilding request",
        )
    if creative_intent == "creative_ideation":
        return ("creative_ideation", "creative invention or ideation request")

    if re.search(r"\b(calculate|compute|solve|arithmetic|percentage|equation)\b", normalized_input) or re.fullmatch(
        r"[\d\s.+*/()%=-]+", normalized_input
    ):
        return ("calculation", "calculation request")

    if (
        len(re.findall(r"\b\d+(?:\.\d+)?\b", normalized_input)) >= 2
        and re.search(
            r"\b(?:buys?|gives?|eats?|adds?|removes?|spends?|receives?|"
            r"another|half|remain|left|total)\b",
            normalized_input,
        )
    ):
        return ("calculation", "quantitative word problem")

    if re.search(
        r"\b(?:every|all)\s+\w+\s+(?:is|are)\s+(?:a\s+)?\w+\b.*"
        r"\b(?:every|all)\s+\w+\s+(?:is|are)\s+(?:a\s+)?\w+\b",
        normalized_input,
    ):
        return ("logical_reasoning", "formal logic relationship question")

    if re.search(r"\b(research|web search|search the web|look online|latest|current sources|find sources)\b", normalized_input):
        return ("research", "research or current-information request")

    if re.search(r"\b(plan|planning|architecture|architect|roadmap|system design|design an? system)\b", normalized_input):
        return ("planning_architecture", "planning or architecture request")

    if re.search(r"\b(compare|choose|decide|decision|pros and cons|tradeoffs?|which should|should i)\b", normalized_input):
        return ("decision_support", "comparison or decision-support request")

    if re.search(r"\b(set|change|adjust|prefer)\b.*\b(tone|style|personality|preference|verbosity|theme)\b", normalized_input):
        return ("personalization", "personalization request")

    if re.search(r"\b(teach|teach me|help me learn|lesson|tutorial|how does|explain how|explain why)\b", normalized_input):
        return ("teaching_learning", "teaching or learning request")

    # --------------------------------------------------------
    # EXPLICIT AIDER REQUEST
    # Highest-priority direct coding route.
    # --------------------------------------------------------

    if normalized_input.startswith("aider "):

        return (
            "coding",
            "explicit aider request"
        )

    # --------------------------------------------------------
    # CODE / DEVELOPMENT REQUEST DETECTION
    # --------------------------------------------------------

    code_keywords = (

        # ====================================================
        # GENERAL DEBUGGING / DEVELOPMENT
        # ====================================================

        "traceback",
        "stack trace",
        "exception",
        "debug",
        "debugging",
        "error:",
        "bug",
        "fix bug",
        "refactor",
        "optimize",
        "rewrite",
        "generate",
        "example",
        "snippet",
        "compile",
        "build",
        "syntax",
        "parser",
        "framework",
        "library",
        "api",

        # ====================================================
        # GENERAL PROGRAMMING TERMS
        # ====================================================

        "code",
        "coding",
        "program",
        "script",
        "function",
        "class",
        "method",
        "object",
        "algorithm",
        "logic",
        "source code",

        # ====================================================
        # LANGUAGES
        # ====================================================

        "python",
        "py",

        "c++",
        "cpp",
        "c#",
        "csharp",
        "c language",

        "javascript",
        "typescript",
        "nodejs",
        "node.js",

        "php",
        "java",
        "powershell",
        "batch",
        "cmd",

        "html",
        "css",
        "xml",
        "json",
        "yaml",
        "toml",

        "sql",
        "mysql",
        "mariadb",
        "sqlite",

        "lua",
        "mq2",

        # ====================================================
        # WEB DEVELOPMENT
        # ====================================================

        "website",
        "web app",
        "frontend",
        "backend",
        "fullstack",
        "full stack",
        "responsive design",
        "bootstrap",
        "tailwind",
        "react",
        "vue",
        "flask",
        "fastapi",

        # ====================================================
        # PACKAGE / DEVELOPMENT TOOLING
        # ====================================================

        "pip ",
        "npm ",
        "composer",
        "docker",
        "git",
        "github",

        # ====================================================
        # REVERSE ENGINEERING / DISASSEMBLY
        # ====================================================

        "disassembly",
        "reverse engineer",
        "reverse engineering",
        "hex editing",
        "memory editing",
        "opcode",
        "assembly",
        "asm",

        "x64dbg",
        "x32dbg",
        "ollydbg",
        "ida",
        "ghidra",

        "hex editor",
        ".alf",

        # ====================================================
        # FILE EXTENSIONS
        # ====================================================

        # Python
        ".py",

        # C / C++
        ".cpp",
        ".cxx",
        ".cc",
        ".c",
        ".hpp",
        ".h",

        # Web
        ".html",
        ".htm",
        ".css",
        ".js",
        ".ts",
        ".jsx",
        ".tsx",
        ".php",

        # Java
        ".java",

        # Batch / PowerShell
        ".bat",
        ".cmd",
        ".ps1",

        # Data / Config
        ".json",
        ".xml",
        ".yaml",
        ".yml",
        ".toml",

        # Database
        ".sql",

        # MQ2 / Lua
        ".lua",
        ".mac",
        ".inc",

        # Reverse engineering
        ".alf"
    )

    code_context_markers = (
        "code", "coding", "program", "script", "function", "class", "method",
        "algorithm", "python", "javascript", "typescript", "powershell", "sql",
        "html", "css", "flask", "fastapi", "react", "vue", "node.js", "api",
        ".py", ".js", ".ts", ".html", ".css", ".sql", ".ps1", ".lua",
    )

    if (
        any(keyword in normalized_input for keyword in code_keywords)
        and any(marker in normalized_input for marker in code_context_markers)
    ):

        return (
            "coding",
            "code/development keywords"
        )

    # --------------------------------------------------------
    # SYSTEM / SHELL COMMAND DETECTION
    # --------------------------------------------------------

    shell_command_pattern = re.compile(
        r"\b(?:dir|tree|where|systeminfo|ipconfig|ping|tracert|nslookup|"
        r"netstat|arp|tasklist|wmic|driverquery|hostname|whoami|ver|date|time)\b",
        re.IGNORECASE,
    )

    if shell_command_pattern.search(normalized_input):

        return (
            "system_command",
            "system command keywords"
        )

    if re.match(
        r"^(?:what|why|how|when|where|who|which|is|are|can|could|would|"
        r"should|do|does|did)\b",
        normalized_input,
    ):
        return (
            "question",
            "general question"
        )

    # --------------------------------------------------------
    # DEFAULT CHAT ROUTE
    # --------------------------------------------------------

    return (
        "conversation",
        "general conversation"
    )


# ============================================================
# FAST PATH INTENT ROUTER
# Detects direct commands before AI reasoning is used.
# ============================================================

def fast_path_intent(user_input: str, *, confirmation_state=None):

    # --------------------------------------------------------
    # INPUT NORMALIZATION
    # Convert incoming text into normalized comparison format.
    # --------------------------------------------------------

    normalized_input = (user_input or "").lower().strip()

    slash_spec = slash_command_spec(user_input)
    if slash_spec:
        return slash_spec["intent"]

    if is_conversation_only_memory_request(normalized_input):
        return "conversation_memory"

    # --------------------------------------------------------
    # CORE SYSTEM COMMANDS
    # Immediate local commands that bypass AI reasoning.
    # --------------------------------------------------------

    if normalized_input in (
        "help",
        "commands",
        "?",
        "what can you do"
    ):

        return "help"

    if normalized_input in (
        "status",
        "system status",
        "check status"
    ):

        return "status"

    if normalized_input in (
        "cls",
        "clear",
        "clear chat",
        "clear screen"
    ):

        return "clear_ui"

    if normalized_input.startswith("memory recall "):

        return "memory_recall"

    if normalized_input == "what have i been working on":

        return "memory_search"

    # --------------------------------------------------------
    # PERSONALITY SYSTEM COMMANDS
    # Commands related to AI behavior and personality settings.
    # --------------------------------------------------------

    personality_commands = (

        "set tone",
        "set name",
        "set verbosity",
        "add trait",
        "remove trait",
        "show personality"
    )

    if any(
        normalized_input.startswith(command)
        for command in personality_commands
    ):

        return "personality"

    # --------------------------------------------------------
    # EXPLICIT MEMORY COMMANDS
    # Structured CRUD operations for memory management.
    # --------------------------------------------------------

    if re.match(
        r"^memory\s+(list|view|search|add|delete|edit|clear|types?)",
        normalized_input
    ):

        return "memory_cmd"

    # --------------------------------------------------------
    # NATURAL LANGUAGE MEMORY SAVE
    # Human-style memory save requests.
    # --------------------------------------------------------

    if any(
        re.match(pattern, normalized_input)
        for pattern in MEMORY_SAVE_PATTERNS
    ):

        return "save_memory"

    # --------------------------------------------------------
    # NATURAL LANGUAGE MEMORY SEARCH
    # Human-style memory recall requests.
    # --------------------------------------------------------

    if any(
        re.match(pattern, normalized_input)
        for pattern in MEMORY_SEARCH_PATTERNS
    ):

        return "memory_search"

    # --------------------------------------------------------
    # NATURAL LANGUAGE MEMORY DELETE
    # Human-style memory removal requests.
    # --------------------------------------------------------

    if any(
        re.match(pattern, normalized_input)
        for pattern in MEMORY_DELETE_PATTERNS
    ):

        return "memory_forget"

    # --------------------------------------------------------
    # PLAYBOOK COMMANDS
    # Automation workflow execution commands.
    # --------------------------------------------------------

    if (
        normalized_input.startswith("run playbook")
        or
        normalized_input.startswith("list playbook")
    ):

        return "playbook"

    # --------------------------------------------------------
    # AIDER PROJECT COMMANDS
    # Sets active coding workspace/project.
    # --------------------------------------------------------

    if re.match(
        r"^aider\s+project\s+",
        normalized_input
    ):

        return "aider_project"

    # --------------------------------------------------------
    # MODEL MANAGEMENT COMMANDS
    # LLM routing and model configuration controls.
    # --------------------------------------------------------

    if (
        normalized_input.startswith("model")
        or
        normalized_input.startswith("models")
    ):

        return "model_cmd"

    # --------------------------------------------------------
    # WEB SEARCH COMMANDS
    # Enables/disables web search or performs web lookup.
    # --------------------------------------------------------

    if (
        normalized_input in ("web on", "web off")
        or
        normalized_input.startswith("web search ")
    ):

        return "web_cmd"

    # --------------------------------------------------------
    # SAFE SHELL COMMANDS
    # Uses the executor's existing allowlist as the sole source.
    # Final permission enforcement remains in system_security.
    # --------------------------------------------------------

    if (
        tool_executor.is_supported_shell_command(normalized_input)
        and classify_command_utterance(
            normalized_input,
            confirmation_state=confirmation_state,
        ) == "direct_command"
    ):
        print(
            "[REQUEST ROUTER] detected command:",
            repr(user_input),
        )
        print("[REQUEST ROUTER] selected tool: shell")
        return "shell"

    # --------------------------------------------------------
    # NO FAST-PATH MATCH
    # Request should continue into AI orchestration layer.
    # --------------------------------------------------------

    return None
    

# ============================================================
# MEMORY DOMAIN CLASSIFIER
# LEFT BRAIN MEMORY ROUTING LAYER
# ============================================================

def classify_memory_domain(user_input: str) -> str:

    """
    LEFT BRAIN MEMORY ROUTING LAYER

    This function determines WHICH memory domain is most
    relevant to the current user request.

    It DOES NOT retrieve memory.
    It ONLY classifies the memory category.

    Used as an early cognition-routing layer before
    memory recall and semantic processing.
    """

    # --------------------------------------------------------
    # INPUT NORMALIZATION
    # Convert input into safe lowercase comparison text.
    # --------------------------------------------------------

    normalized_input = (user_input or "").lower()

    # --------------------------------------------------------
    # IDENTITY / PERSONAL PROFILE MEMORY
    # User facts, identity, self-description, and personal data.
    # --------------------------------------------------------

    identity_keywords = (
        "name",
        "who am i",
        "about me",
        "myself",
        "my personality",
        "who i am",
        "personal info",
        "profile"
    )

    if any(
        keyword in normalized_input
        for keyword in identity_keywords
    ):
        return "identity"

    # --------------------------------------------------------
    # SPIRITUAL / EXPERIENCE MEMORY
    # Dreams, meditation, energy states, and spiritual events.
    # --------------------------------------------------------

    spiritual_keywords = (
        "meditation",
        "spiritual",
        "energy",
        "vibration",
        "dream",
        "lucid",
        "astral",
        "obe",
        "chakra",
        "frequency",
        "entity",
        "spirit",
        "awakening",
        "presence",
        "vision"
    )

    if any(
        keyword in normalized_input
        for keyword in spiritual_keywords
    ):
        return "spiritual"

    # --------------------------------------------------------
    # AI PROJECT / SYSTEM MEMORY
    # Architecture, coding, AI system, and development context.
    # --------------------------------------------------------

    project_keywords = (
        "ai",
        "system",
        "project",
        "architecture",
        "building",
        "framework",
        "tool",
        "agent",
        "memory system",
        "database",
        "orchestrator",
        "python",
        "code",
        "programming",
        "development"
    )

    if any(
        keyword in normalized_input
        for keyword in project_keywords
    ):
        return "project"

    # --------------------------------------------------------
    # DEFAULT MEMORY DOMAIN
    # Fallback when no specific category is detected.
    # --------------------------------------------------------

    return "general"

    

# ============================================================
# INPUT CLEANING LAYER
# RAW USER INPUT SANITIZATION PIPELINE
# ============================================================

def clean_input(text):

    """
    INPUT SANITIZATION PIPELINE

    This function is the FIRST processing layer for all user input.

    It ensures all incoming data is:
    - safe for AI processing
    - normalized for memory storage
    - consistent for routing + intent detection

    Supports:
    - CLI input
    - API / Flask input
    - socket / byte streams
    """

    # --------------------------------------------------------
    # STEP 1: HANDLE RAW BYTES INPUT
    # --------------------------------------------------------
    # Some API layers may pass bytes instead of strings.
    # This prevents corrupted memory entries like b'hello'.
    # --------------------------------------------------------

    if isinstance(text, bytes):
        text = text.decode("utf-8", errors="ignore")

    # --------------------------------------------------------
    # STEP 2: FORCE STRING TYPE SAFETY
    # --------------------------------------------------------
    # Ensures downstream systems never receive invalid types.
    # Memory, embeddings, and LLM prompts require strict strings.
    # --------------------------------------------------------

    text = str(text).strip()

    # --------------------------------------------------------
    # STEP 3: DETECT FULL-STRING DUPLICATION
    # --------------------------------------------------------
    # Fixes accidental echo duplication:
    # Example: "hellohello"
    # or UI repeat injection bugs.
    # --------------------------------------------------------

    if len(text) > 10:

        midpoint = len(text) // 2

        if text[:midpoint] == text[midpoint:]:

            text = text[:midpoint]

    # --------------------------------------------------------
    # STEP 4: DETECT WORD-LEVEL DUPLICATION
    # --------------------------------------------------------
    # Fixes repeated sentence loops:
    # Example: "what is my name what is my name"
    # --------------------------------------------------------

    words = text.split()

    if len(words) > 6:

        midpoint = len(words) // 2

        if words[:midpoint] == words[midpoint:]:

            text = " ".join(words[:midpoint])

    # --------------------------------------------------------
    # FINAL OUTPUT CONTRACT
    # --------------------------------------------------------
    # Output is guaranteed:
    # - string
    # - trimmed
    # - de-duplicated (basic corruption handling)
    # - safe for routing, memory, and AI processing
    # --------------------------------------------------------

    return text
