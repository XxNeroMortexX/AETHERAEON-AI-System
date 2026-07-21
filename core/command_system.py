"""Safe explicit-command definitions, parsing, and non-executing guidance."""

from dataclasses import dataclass
import re


@dataclass(frozen=True, slots=True)
class CommandParameter:
    name: str
    description: str
    required: bool = True
    example: str = ""
    greedy: bool = False


@dataclass(frozen=True, slots=True)
class CommandDefinition:
    command: str
    description: str
    required_parameters: tuple[CommandParameter, ...]
    optional_parameters: tuple[CommandParameter, ...]
    permission: str
    handler: str
    intent: str
    legacy_command: str | None = None
    confirmation_required: bool = False
    suggestions_only: bool = False


@dataclass(frozen=True, slots=True)
class CommandValidation:
    status: str
    message: str
    definition: CommandDefinition | None = None
    arguments: tuple[tuple[str, str], ...] = ()
    effective_command: str | None = None

    @property
    def valid(self) -> bool:
        return self.status in {"valid", "confirmation_required"}


def _parameter(name, description, *, required=True, example="", greedy=False):
    return CommandParameter(name, description, required, example, greedy)


COMMAND_DEFINITIONS = (
    CommandDefinition(
        "/help", "Show available commands", (), (), "user", "build_help", "help", "help",
    ),
    CommandDefinition(
        "/status", "Show system health", (), (), "admin", "print_status", "status", "status",
    ),
    CommandDefinition(
        "/memory", "Manage memories", (), (), "owner", "command_suggestions",
        "command_suggestions", suggestions_only=True,
    ),
    CommandDefinition(
        "/memory list", "Show stored memories", (),
        (_parameter("memory_type", "Optional memory type filter", required=False),),
        "owner", "handle_memory_command", "memory_cmd", "memory list",
    ),
    CommandDefinition(
        "/memory search", "Search memories",
        (_parameter("query", "Search text", example="project notes", greedy=True),),
        (), "owner", "handle_memory_command", "memory_cmd", "memory search",
    ),
    CommandDefinition(
        "/memory delete", "Delete a memory entry",
        (_parameter("memory_id", "Memory ID", example="abc123"),),
        (), "owner", "handle_memory_command", "memory_cmd", "memory delete",
        confirmation_required=True,
    ),
    CommandDefinition(
        "/model", "Manage AI models", (), (), "admin", "command_suggestions",
        "command_suggestions", suggestions_only=True,
    ),
    CommandDefinition(
        "/model show", "Show active AI models", (), (), "admin",
        "handle_model_command", "model_cmd", "model show",
    ),
    CommandDefinition(
        "/model list", "List installed AI models", (), (), "admin",
        "handle_model_command", "model_cmd", "model list",
    ),
    CommandDefinition(
        "/personality", "Manage AI traits", (), (), "owner",
        "handle_personality", "personality", "show personality",
    ),
)

_COMMANDS_BY_NAME = {definition.command: definition for definition in COMMAND_DEFINITIONS}
_CONFIRMED_STATES = {"confirmed", "approved", "yes", "true"}


def command_catalog() -> tuple[CommandDefinition, ...]:
    return COMMAND_DEFINITIONS


def command_children(parent: str) -> tuple[CommandDefinition, ...]:
    prefix = parent.rstrip() + " "
    return tuple(
        definition for definition in COMMAND_DEFINITIONS
        if definition.command.startswith(prefix)
        and " " not in definition.command[len(prefix):]
    )


def _suggestions_message(parent: str | None = None) -> str:
    definitions = command_children(parent) if parent else tuple(
        definition for definition in COMMAND_DEFINITIONS if " " not in definition.command[1:]
    )
    heading = f"Available {parent} commands:" if parent else "Available commands:"
    lines = [heading]
    for definition in definitions:
        lines.append(f"- {definition.command}\n  {definition.description}")
    return "\n".join(lines)


def _permission_allowed(requirement: str, role: str | None) -> bool:
    if role is None:
        return True
    normalized_role = str(role or "user").strip().lower()
    if requirement == "admin":
        return normalized_role == "admin"
    if requirement in {"owner", "user"}:
        return normalized_role in {"admin", "user"}
    return False


def _matching_definition(tokens: list[str]) -> tuple[CommandDefinition | None, int]:
    for token_count in range(len(tokens), 0, -1):
        candidate = " ".join(tokens[:token_count]).lower()
        definition = _COMMANDS_BY_NAME.get(candidate)
        if definition:
            return definition, token_count
    return None, 0


def _parameter_error(definition: CommandDefinition, parameter: CommandParameter) -> str:
    label = parameter.name.replace("_id", " ID").replace("_", " ").title()
    label = label.replace(" Id", " ID")
    example_value = parameter.example or f"<{parameter.name}>"
    return (
        f"{label} required\n\n"
        f"Example:\n{definition.command} {example_value}"
    )


def validate_slash_command(
    user_input: str,
    *,
    role: str | None = None,
    confirmation_state=None,
) -> CommandValidation | None:
    """Validate slash syntax and metadata without executing a handler."""

    text = re.sub(r"\s+", " ", str(user_input or "")).strip()
    if not text.startswith("/"):
        return None
    if text == "/":
        return CommandValidation("suggestions", _suggestions_message())

    tokens = text.split(" ")
    definition, consumed = _matching_definition(tokens)
    if not definition:
        root = tokens[0].lower()
        if root in _COMMANDS_BY_NAME and command_children(root):
            return CommandValidation(
                "error",
                f"Unknown {root} command.\n\n{_suggestions_message(root)}",
            )
        return CommandValidation(
            "error",
            "Unknown slash command. Use /help to see available commands.",
        )

    if definition.suggestions_only:
        extra_tokens = tokens[consumed:]
        if extra_tokens:
            return CommandValidation(
                "error",
                f"Unknown {definition.command} command.\n\n"
                f"{_suggestions_message(definition.command)}",
                definition,
            )
        return CommandValidation(
            "suggestions",
            _suggestions_message(definition.command),
            definition,
        )

    if not _permission_allowed(definition.permission, role):
        return CommandValidation(
            "permission_denied",
            f"{definition.permission.title()} permission is required for {definition.command}.",
            definition,
        )

    remaining = tokens[consumed:]
    parsed_arguments: list[tuple[str, str]] = []
    position = 0
    for parameter in definition.required_parameters + definition.optional_parameters:
        if parameter.greedy:
            value = " ".join(remaining[position:]).strip()
            position = len(remaining)
        else:
            value = remaining[position].strip() if position < len(remaining) else ""
            position += 1 if value else 0
        if parameter.required and not value:
            return CommandValidation(
                "missing_parameter",
                _parameter_error(definition, parameter),
                definition,
                tuple(parsed_arguments),
            )
        if value:
            parsed_arguments.append((parameter.name, value))

    if position < len(remaining):
        unexpected = " ".join(remaining[position:])
        return CommandValidation(
            "error",
            f"Unexpected parameter: {unexpected}",
            definition,
            tuple(parsed_arguments),
        )

    suffix = " ".join(value for _name, value in parsed_arguments)
    effective_command = definition.legacy_command or definition.command.lstrip("/")
    if suffix:
        effective_command = f"{effective_command} {suffix}"

    confirmed = (
        confirmation_state is True
        or str(confirmation_state or "").strip().lower() in _CONFIRMED_STATES
    )
    if definition.confirmation_required and not confirmed:
        return CommandValidation(
            "confirmation_required",
            f"Command parameters are valid.\nConfirmation required before {definition.description.lower()}.\nNo action was executed.",
            definition,
            tuple(parsed_arguments),
            effective_command,
        )

    return CommandValidation(
        "valid",
        "Command parameters are valid.",
        definition,
        tuple(parsed_arguments),
        effective_command,
    )


def build_action_request_guidance(user_input: str, interaction_analysis) -> str | None:
    """Return safe non-executing guidance for natural-language actions."""

    text = re.sub(r"\s+", " ", str(user_input or "")).strip()
    lowered = text.lower()
    information_question = bool(re.match(
        r"^(?:how|what|why|when|where|who|which|do|does|did|is|are)\b",
        lowered,
    ))
    project_inspection = bool(re.search(
        r"^(?:can|could|would)\s+you\s+check\b.*\bproject\s+files?\b|"
        r"^check\b.*\bproject\s+files?\b",
        lowered,
    ))
    action_request = getattr(interaction_analysis, "intent", None) == "action_request"
    if information_question or not (action_request or project_inspection):
        return None

    if re.search(r"\b(?:web|online|internet)\b", lowered) and re.search(
        r"\b(?:search|research|look\s+up|find)\b",
        lowered,
    ):
        return None

    if project_inspection or re.search(
        r"\b(?:check|inspect|open|show|list|search)\b.*\b(?:project\s+)?files?\b",
        lowered,
    ):
        return (
            "I can help inspect files.\n\n"
            "Please choose an action:\n\n"
            "1. Open project folder\n"
            "2. Show files\n"
            "3. Search project\n"
            "4. Explain manually\n\n"
            "No action was executed."
        )

    required = ["target", "location", "permission"]
    return (
        "I understand you want me to perform this action.\n\n"
        "The required capability is not enabled yet.\n\n"
        "Required information:\n"
        + "\n".join(f"- {item}" for item in required)
        + "\n\nNo action was executed."
    )
