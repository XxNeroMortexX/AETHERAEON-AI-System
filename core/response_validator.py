"""Aetheraeon architecture: Phase 8 Report-Only Response Validator.

Response Validator responsibility:
    Inspect a generated response transiently and produce a Phase 0A
    ``ResponseValidationResult`` containing observable check outcomes only.

Architecture layer:
    Cognitive Intelligence Layer validation boundary after generation and before
    a future enforcement phase.

Responsibilities:
    - report structural, privacy, evidence-reference, retrieval-receipt, tool-
      receipt, and memory-receipt validation outcomes when applicable;
    - preserve opaque correlation identifiers, provenance, warnings, and
      unavailable confidence without retaining response text;
    - remain explicitly report-only with no retry, rewrite, or enforcement.

Boundaries:
    - observational only; it cannot block, rewrite, regenerate, retry, route,
      authorize, execute tools, modify memory, prompts, permissions, or state;
    - does not retain private chain-of-thought, scratch work, prompts, secrets,
      credentials, tokens, or raw private memory content;
    - does not replace ai_orchestrator.py or any current response path.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import math
import re
import time
from typing import Any, Callable, Mapping

from core.cognitive_contracts import (
    COGNITIVE_CONTRACT_SCHEMA_VERSION,
    ResponseValidationResult,
    ValidationCheck,
    ValidationCheckStatus,
    ValidationOutcome,
)


REPORT_ONLY_VALIDATOR_MODE = "report_only"
REPORT_ONLY_VALIDATOR_AUTHORITATIVE = False
REPORT_ONLY_VALIDATOR_POLICY_VERSION = "report-only-validator-1.0"
_SAFE_REFERENCE_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_PRIVATE_REASONING_PATTERN = re.compile(
    r"chain(?:-|\s+)of(?:-|\s+)thought|hidden\s+scratch|scratch\s*(?:work|pad)|"
    r"system\s+prompt",
    re.IGNORECASE,
)
_SECRET_PATTERN = re.compile(
    r"(?:api[_ -]?key|password|credential|secret|token)\s*(?:=|:)\s*\S+",
    re.IGNORECASE,
)


class ResponseValidationError(ValueError):
    """Raised when report-only validator inputs would be unsafe or invalid."""


def _nonempty_string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ResponseValidationError(f"{name} must be a non-empty string")
    return value.strip()


def _safe_references(value: Any, name: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, (str, bytes)) or not isinstance(value, (list, tuple)):
        raise ResponseValidationError(f"{name} must be a sequence of opaque references")
    references = tuple(value)
    if any(not isinstance(reference, str) or not _SAFE_REFERENCE_PATTERN.fullmatch(reference) for reference in references):
        raise ResponseValidationError(f"{name} must contain opaque safe references")
    return references


def _provenance(value: Any) -> Mapping[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise ResponseValidationError("provenance must be a mapping")
    normalized: dict[str, Any] = {}
    for key, item in value.items():
        normalized_key = _nonempty_string(key, "provenance key")
        if isinstance(item, (str, bool, int)) or item is None:
            normalized[normalized_key] = item
        elif isinstance(item, float) and math.isfinite(item):
            normalized[normalized_key] = item
        else:
            raise ResponseValidationError("provenance contains a non-observable value")
    return normalized


def _warnings(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, (str, bytes)) or not isinstance(value, (list, tuple)):
        raise ResponseValidationError("warnings must be a sequence of strings")
    return tuple(_nonempty_string(item, "warning") for item in value)


@dataclass(frozen=True, slots=True)
class ReportOnlyValidation:
    """Observable validation envelope that deliberately contains no response text."""

    validation_result: ResponseValidationResult
    status: str
    confidence: float | None
    provenance: Mapping[str, Any] = field(default_factory=dict)
    warnings: tuple[str, ...] = ()
    latency_ms: float = 0.0
    policy_version: str = REPORT_ONLY_VALIDATOR_POLICY_VERSION

    MODE = REPORT_ONLY_VALIDATOR_MODE
    AUTHORITATIVE = REPORT_ONLY_VALIDATOR_AUTHORITATIVE

    def __post_init__(self) -> None:
        if not isinstance(self.validation_result, ResponseValidationResult):
            raise ResponseValidationError("validation_result must use the Phase 0A ResponseValidationResult contract")
        object.__setattr__(self, "status", _nonempty_string(self.status, "status"))
        if self.confidence is not None:
            if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)) or not math.isfinite(float(self.confidence)) or not 0 <= self.confidence <= 1:
                raise ResponseValidationError("confidence must be None or a number between 0 and 1")
        object.__setattr__(self, "provenance", _provenance(self.provenance))
        object.__setattr__(self, "warnings", _warnings(self.warnings))
        if isinstance(self.latency_ms, bool) or not isinstance(self.latency_ms, (int, float)) or not math.isfinite(float(self.latency_ms)) or self.latency_ms < 0:
            raise ResponseValidationError("latency_ms must be a finite non-negative number")
        if self.policy_version != REPORT_ONLY_VALIDATOR_POLICY_VERSION:
            raise ResponseValidationError("unsupported validator policy_version")

    @property
    def trace_id(self) -> str:
        return self.validation_result.trace_id

    def to_metadata_dict(self) -> dict[str, Any]:
        """Serialize only observable validation metadata, never response text."""

        return {
            "mode": self.MODE,
            "authoritative": self.AUTHORITATIVE,
            "status": self.status,
            "confidence": self.confidence,
            "validation_result": self.validation_result.to_dict(),
            "provenance": dict(self.provenance),
            "warnings": list(self.warnings),
            "latency_ms": self.latency_ms,
            "policy_version": self.policy_version,
            "schema_version": COGNITIVE_CONTRACT_SCHEMA_VERSION,
        }


class ReportOnlyResponseValidator:
    """Deterministic observer that reports but never enforces validation results."""

    def validate(
        self,
        response_text: Any,
        *,
        trace_id: str,
        evidence_references: tuple[str, ...] = (),
        retrieval_references: tuple[str, ...] = (),
        tool_receipt_references: tuple[str, ...] = (),
        memory_receipt_references: tuple[str, ...] = (),
        provenance: Mapping[str, Any] | None = None,
        warnings: tuple[str, ...] = (),
        monotonic_clock: Callable[[], float] = time.monotonic,
    ) -> ReportOnlyValidation:
        if not isinstance(response_text, str):
            raise ResponseValidationError("response_text must be a string")
        trace_id = _nonempty_string(trace_id, "trace_id")
        evidence_references = _safe_references(evidence_references, "evidence_references")
        retrieval_references = _safe_references(retrieval_references, "retrieval_references")
        tool_receipt_references = _safe_references(tool_receipt_references, "tool_receipt_references")
        memory_receipt_references = _safe_references(memory_receipt_references, "memory_receipt_references")
        provenance = _provenance(provenance)
        warnings = _warnings(warnings)
        if not callable(monotonic_clock):
            raise ResponseValidationError("monotonic_clock must be callable")

        started = monotonic_clock()
        normalized_response = response_text.strip()
        checks = [
            ValidationCheck(
                name="response_structure",
                status=ValidationCheckStatus.PASS if normalized_response else ValidationCheckStatus.FAIL,
                reason_code=None if normalized_response else "response_empty",
                summary="Response contains visible output." if normalized_response else "Response is empty.",
            ),
            ValidationCheck(
                name="privacy_output",
                status=(
                    ValidationCheckStatus.FAIL
                    if _PRIVATE_REASONING_PATTERN.search(response_text) or _SECRET_PATTERN.search(response_text)
                    else ValidationCheckStatus.PASS
                ),
                reason_code=(
                    "restricted_output_pattern"
                    if _PRIVATE_REASONING_PATTERN.search(response_text) or _SECRET_PATTERN.search(response_text)
                    else None
                ),
                summary=(
                    "Response contains a restricted private or secret-shaped pattern."
                    if _PRIVATE_REASONING_PATTERN.search(response_text) or _SECRET_PATTERN.search(response_text)
                    else "No restricted output pattern was detected."
                ),
            ),
            ValidationCheck(
                name="evidence_references",
                status=ValidationCheckStatus.PASS if evidence_references else ValidationCheckStatus.NOT_APPLICABLE,
                summary="Opaque evidence references were available." if evidence_references else "No evidence references were available.",
                evidence_references=evidence_references,
            ),
            ValidationCheck(
                name="retrieval_references",
                status=ValidationCheckStatus.PASS if retrieval_references else ValidationCheckStatus.NOT_APPLICABLE,
                summary="Opaque retrieval references were available." if retrieval_references else "No retrieval references were available.",
                evidence_references=retrieval_references,
            ),
            ValidationCheck(
                name="tool_receipts",
                status=ValidationCheckStatus.PASS if tool_receipt_references else ValidationCheckStatus.NOT_APPLICABLE,
                summary="Opaque tool receipt references were available." if tool_receipt_references else "No tool receipt references were available.",
                evidence_references=tool_receipt_references,
            ),
            ValidationCheck(
                name="memory_receipts",
                status=ValidationCheckStatus.PASS if memory_receipt_references else ValidationCheckStatus.NOT_APPLICABLE,
                summary="Opaque memory receipt references were available." if memory_receipt_references else "No memory receipt references were available.",
                evidence_references=memory_receipt_references,
            ),
        ]
        failed = tuple(check for check in checks if check.status is ValidationCheckStatus.FAIL)
        result = ResponseValidationResult(
            trace_id=trace_id,
            outcome=ValidationOutcome.BLOCK if failed else ValidationOutcome.PASS,
            checks=tuple(checks),
            report_only=True,
            retry_count=0,
            maximum_retries=0,
            reason_codes=tuple(check.reason_code for check in failed if check.reason_code),
            warnings=warnings,
        )
        latency_ms = round(max(0.0, (monotonic_clock() - started) * 1000), 6)
        return ReportOnlyValidation(
            validation_result=result,
            status="reported",
            confidence=None,
            provenance={"validator": "deterministic_report_only", **provenance},
            warnings=warnings,
            latency_ms=latency_ms,
        )


def validate_report_only(
    response_text: Any,
    *,
    trace_id: str,
    **kwargs: Any,
) -> ReportOnlyValidation:
    """Run a transient report-only validation with no response-path authority."""

    return ReportOnlyResponseValidator().validate(response_text, trace_id=trace_id, **kwargs)
