"""
Aetheraeon AI - LLM Interface

Purpose:
Provides the current communication boundary between Aetheraeon and configured language-model backends.

Architecture Layer:
Core Intelligence Layer - model communication.

Responsibilities:
- Send prepared prompts to configured models and receive generated output.
- Normalize transport results and handle model communication failures.
- Validate response availability and shape for downstream processing.

Boundaries:
- The LLM and this interface do not own cognitive policy, memory decisions, permissions, security, or tool authorization.
- Transport and format checks do not replace the planned Response Validator.
- Language generation is one component of the Cognitive Core, not the complete intelligence system.
"""



# ============================================================
# CORE STANDARD LIBRARY IMPORTS
# ============================================================
# Built-in Python modules used for validation, parsing,
# debugging, timing, and response normalization.
# ============================================================

import json          # Structured response parsing / JSON validation
import re            # Final-answer cleanup without exposing private reasoning
import time          # Timing / latency measurement / debug tracking
from datetime import datetime  # Timestamp generation for logs


# ============================================================
# EXTERNAL DEPENDENCIES (PIP INSTALLED PACKAGES)
# ============================================================
# Third-party libraries installed through pip.
# ============================================================

import ollama        # Ollama local LLM backend interface


# ============================================================
# INTERNAL SYSTEM IMPORTS (ARCHITECTURE LAYERS)
# ============================================================
# Internal AI system modules used by the LLM layer.
#
# RULES:
# - Only import architecture layers here
# - No frontend/UI imports
# - No direct database imports
# - No tool execution imports
#
# This file should remain a pure model communication layer.
# ============================================================

# ------------------------------------------------------------
# SYSTEM LOGGER
# Centralized debug + error logging system
# ------------------------------------------------------------
from core import system_logger

# ------------------------------------------------------------
# MODEL REGISTRY
# Handles model selection and routing configuration
# ------------------------------------------------------------
from core import model_registry

# ------------------------------------------------------------
# CONFIGURATION SYSTEM
# Centralized system configuration loader
# ------------------------------------------------------------
from core import config_loader


# ============================================================
# MAIN LLM REQUEST FUNCTION
# Sends prompts to the configured LLM and safely returns
# validated text responses from Ollama.
# ============================================================

def _response_field(response, field_name, default=None):
    if isinstance(response, dict):
        return response.get(field_name, default)
    return getattr(response, field_name, default)


def _response_field_names(response) -> list[str]:
    """Return response field names without logging any field values."""
    if response is None:
        return []
    if isinstance(response, dict):
        return sorted(str(key) for key in response.keys())
    model_fields = getattr(response, "model_fields", None)
    if isinstance(model_fields, dict):
        return sorted(str(key) for key in model_fields.keys())
    object_fields = getattr(response, "__dict__", None)
    if isinstance(object_fields, dict):
        return sorted(str(key) for key in object_fields.keys())
    return []


def extract_final_response(response) -> tuple[str, dict]:
    """
    Extract only Ollama's public final-answer fields.

    Private thinking/reasoning/analysis fields are detected for diagnostics but
    are never returned, printed, or used as a fallback.
    """
    message = _response_field(response, "message")
    response_fields = _response_field_names(response)
    message_fields = _response_field_names(message)
    private_fields = ("thinking", "reasoning", "analysis")
    thinking_present = any(
        bool(_response_field(message, field_name))
        or bool(_response_field(response, field_name))
        for field_name in private_fields
    )

    final_candidates = (
        ("message.content", _response_field(message, "content")),
        ("message.final", _response_field(message, "final")),
        ("message.final_answer", _response_field(message, "final_answer")),
        ("message.answer", _response_field(message, "answer")),
        ("response", _response_field(response, "response")),
        ("final", _response_field(response, "final")),
        ("final_answer", _response_field(response, "final_answer")),
        ("answer", _response_field(response, "answer")),
    )
    final_field = ""
    final_answer = ""
    for candidate_field, candidate_value in final_candidates:
        if isinstance(candidate_value, str) and candidate_value.strip():
            final_field = candidate_field
            final_answer = candidate_value.strip()
            break
    embedded_private_thought = bool(re.search(
        r"<(?:think|thinking|analysis|reasoning)>",
        final_answer,
        re.IGNORECASE,
    ))
    thinking_present = thinking_present or embedded_private_thought

    # Some older models embed private thought in tagged content. Remove complete
    # private blocks; an unterminated private block is treated as no final answer.
    closing_private_tags = list(re.finditer(
        r"</(?:think|thinking|analysis|reasoning)>",
        final_answer,
        re.IGNORECASE,
    ))
    if closing_private_tags:
        thinking_present = True
        final_answer = final_answer[closing_private_tags[-1].end():].strip()

    final_answer = re.sub(
        r"<(?:think|thinking|analysis|reasoning)>[\s\S]*?</(?:think|thinking|analysis|reasoning)>",
        "",
        final_answer,
        flags=re.IGNORECASE,
    ).strip()
    if re.search(r"<(?:think|thinking|analysis|reasoning)>", final_answer, re.IGNORECASE):
        final_answer = ""

    done_reason = (
        _response_field(response, "done_reason")
        or _response_field(response, "stop_reason")
        or _response_field(message, "done_reason")
        or _response_field(message, "stop_reason")
        or ""
    )
    done_value = _response_field(response, "done")
    truncated = str(done_reason).casefold() in {
        "length", "max_length", "max_tokens", "token_limit",
    } or done_value is False

    diagnostics = {
        "content_length": len(final_answer),
        "thinking_present": thinking_present,
        "final_used": bool(final_answer),
        "final_field": final_field,
        "response_fields": response_fields,
        "message_fields": message_fields,
        "truncated": truncated,
    }
    return final_answer, diagnostics

def ask_llm(
    prompt: str,
    model: str = "qwen2.5-coder:14b",
    temperature: float = 0.7,
    num_predict: int = 256,
    system: str | None = None,
    debug_label: str | None = None,
    think: bool | str | None = None,
    return_metadata: bool = False,
) -> str | tuple[str, dict]:

    """
    Send a prompt to the LLM and return a validated response.
    """

    # ========================================================
    # BUILD MESSAGE PAYLOAD
    # ========================================================

    messages = []

    def _return_result(text, diagnostics=None):
        result_diagnostics = diagnostics or {
            "content_length": len(text),
            "thinking_present": False,
            "final_used": bool(text),
            "truncated": False,
        }
        return (text, result_diagnostics) if return_metadata else text

    # Optional system instruction message
    if system:
        messages.append({
            "role": "system",
            "content": str(system)
        })

    # Main user prompt message
    messages.append({
        "role": "user",
        "content": str(prompt)
    })

    # ========================================================
    # VALIDATE MESSAGE STRUCTURE
    # ========================================================

    try:

        greeting_request = debug_label == "GREETING"

        if not greeting_request:
            print("\n[ASK_LLM DEBUG]")
            print(f"model = {model}")

        for index, message in enumerate(messages):

            role = message.get("role")
            content = message.get("content")

            if not greeting_request:
                print(f"[MSG {index}] role={role}")
                print(f"[MSG {index}] content_type={type(content)}")
                print(
                    f"[MSG {index}] content_preview="
                    f"{repr(str(content)[:120])}"
                )

            # ------------------------------------------------
            # CONTENT MUST EXIST
            # ------------------------------------------------

            if content is None:

                if not greeting_request:
                    print(f"[ASK_LLM ERROR] message {index} content is None")

                return _return_result("")

            # ------------------------------------------------
            # CONTENT MUST BE STRING
            # ------------------------------------------------

            if not isinstance(content, str):

                if not greeting_request:
                    print(f"[ASK_LLM ERROR] message {index} content is not a string")

                return _return_result("")

        # ====================================================
        # SEND REQUEST TO OLLAMA
        # ====================================================

        chat_arguments = {
            "model": model,
            "messages": messages,
            "options": {
                "temperature": temperature,
                "num_predict": num_predict,
            },
        }
        if think is not None:
            chat_arguments["think"] = think

        response = ollama.chat(**chat_arguments)

        final_response, diagnostics = extract_final_response(response)

        if debug_label == "GREETING":
            print("[GREETING MODEL]")
            print(f"model={model}")
            print("[GREETING RESPONSE]")
            print(f"content_length={diagnostics['content_length']}")
            print(f"thinking_present={diagnostics['thinking_present']}")
            print(f"final_used={diagnostics['final_used']}")
            print(f"truncated={diagnostics['truncated']}")
            print(f"success={bool(final_response)}")

        if not final_response:
            if not greeting_request:
                print("[OLLAMA ERROR] final answer field is empty")
            return _return_result("", diagnostics)

        return _return_result(final_response, diagnostics)

    # ========================================================
    # GLOBAL FAILURE SAFETY CATCH
    # ========================================================

    except Exception as error:

        if debug_label == "GREETING":
            print("[GREETING RESPONSE]")
            print("success=False")
            print(f"failure={type(error).__name__}")
        else:
            print("[OLLAMA EXCEPTION]", error)

        return _return_result("")
