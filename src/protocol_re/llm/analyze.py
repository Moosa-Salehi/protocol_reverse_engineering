from __future__ import annotations

import json
import os
import socket
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, Optional
import ssl
ssl._create_default_https_context = ssl._create_unverified_context


DEFAULT_SYSTEM_PROMPT = "You are an expert Protocol Reverse Engineering Analyst."

DEFAULT_ANALYSIS_TEMPLATE = """Role
You are an expert Protocol Reverse Engineering Analyst.

Task
Analyze the provided Protocol Reverse Engineering Evidence Bundle and infer the most plausible structure and semantics of the protocol. Base all reasoning strictly on the supplied evidence.

Perform the following analyses:

1. Protocol Structure Inference
Infer the most plausible high-level structure of the protocol based on the evidence across families, segments, and fields.
Identify likely header regions, opcode/function identifiers, length fields, constant markers, and payload areas.

2. Field Boundary and Type Review
Evaluate the correctness of inferred field boundaries and field types.
- Detect likely boundary errors or merged/split fields
- Suggest corrected start/end offsets when evidence indicates mistakes
- Identify likely field types (opcode, length, counter, flags, identifier, payload, checksum)
Provide corrected field definitions where appropriate.

3. Semantic Interpretation
Improve the semantic meaning of fields using evidence from:
- semantic_labels
- relations
- global_hypotheses
- structural patterns across families
Suggest meaningful names for fields.

4. Opcode Identification
Identify fields that likely represent operation codes or function identifiers.
For each candidate:
- explain the evidence
- describe the likely operation class
- map which message families correspond to each operation.

5. Request / Response Interpretation
Using relations, determine:
- which families act as requests
- which families act as responses
- how fields propagate between them (echo fields, transaction IDs, etc.)
Explain the request/response lifecycle and matching logic.

6. Clustering Evaluation
Evaluate whether the current family clustering is correct.
Identify:
- families that likely belong together
- families that should be split
- potential noise clusters
Suggest concrete clustering improvements if evidence supports them.

7. Contradictions and Inference Errors
Identify contradictions or weak areas in the current inference model:
- conflicting field interpretations
- inconsistent boundaries
- relations that do not match structural patterns
- hypotheses that lack sufficient evidence
Clearly mark these issues.

8. Protocol Layout Reconstruction
Produce a cleaned and consolidated protocol layout describing:
- common message structure
- shared header fields
- operation-specific payload regions
- request/response mapping
The goal is to provide a human-readable structural model of the protocol.

9. Similarity to Known Protocols
If strong structural evidence exists, indicate whether the protocol resembles any known protocol families (e.g., industrial control protocols).
Only report such similarity when multiple structural characteristics match.
Do not speculate when evidence is weak.

10. Answer Open Questions
Address the questions listed in open_questions using available evidence.
If insufficient evidence exists, explicitly state that additional captures or analysis are required.

FOCUS: Use the evaluation section to weigh the reliability of your findings.
CONSTRAINT: Do not invent protocol details. If evidence is insufficient, explicitly label it as "Requires Capture/Inspection".

Output requirements
Return one JSON object and no Markdown fences. The object must have:
- analysis_markdown: a concise report with the same analytical content.
- patches: an RFC 6902 JSON Patch array against data/10_protocol_model.json.

Patch constraints:
- Every patch object must include op, path, value, evidence_refs, and rationale.
- Use only add, replace, or test operations.
- Only target semantic roles, field encoding/type labels, confidence adjustments, relation labels, and metadata.protocol_hints.
- Do not change field boundaries, payload templates, message counts, family ids, examples, or raw evidence.
- Only emit a patch when the supplied statistical, symbolic, or neural evidence supports it.
- Put evidence source names in evidence_refs, such as family:F0:semantic_labels, family:F0:discriminator_candidates, relation:0, global_hypotheses.opcode_candidates, or neural_context.salience_scores.
- If no safe patch is justified, return patches: [].
"""


@dataclass
class LLMRequestConfig:
    model: str
    base_url: str
    api_key: str
    temperature: float = 0.1
    max_tokens: int = 4000
    timeout: int = 180
    max_retries: int = 3
    retry_delay_seconds: float = 1.0
    max_retry_delay_seconds: float = 10.0
    request_interval_seconds: float = 1.0
    logger: Optional[Any] = None


class LLMAPIError(RuntimeError):
    """Raised when an LLM request fails with classified API/network details."""

    def __init__(
        self,
        message: str,
        *,
        category: str,
        retryable: bool,
        status_code: Optional[int] = None,
        details: str = "",
    ):
        super().__init__(message)
        self.category = category
        self.retryable = retryable
        self.status_code = status_code
        self.details = details


_REQUEST_LOCK = threading.Lock()
_LAST_REQUEST_COMPLETED_AT = 0.0


def render_analysis_prompt(
    evidence: Dict[str, Any],
    template: str = DEFAULT_ANALYSIS_TEMPLATE,
    minify_json: bool = False,
) -> str:
    if minify_json:
        evidence_json = json.dumps(evidence, separators=(",", ":"), ensure_ascii=False)
    else:
        evidence_json = json.dumps(evidence, indent=2, ensure_ascii=False)
    return (
        template.rstrip()
        + "\n\nProtocol Reverse Engineering Evidence Bundle\n"
        + "```json\n"
        + evidence_json
        + "\n```\n"
    )


def _chat_completions_url(base_url: str) -> str:
    base = base_url.rstrip("/")
    if base.endswith("/chat/completions"):
        return base
    return base + "/chat/completions"


def _emit(config: LLMRequestConfig, level: str, message: str, **kwargs: Any) -> None:
    logger = config.logger
    log_method = getattr(logger, level, None) if logger is not None else None
    if callable(log_method):
        try:
            log_method(message, **kwargs)
        except TypeError:
            log_method(message)
    else:
        print(message)


def _summarize_body(body: str, limit: int = 1200) -> str:
    compact = " ".join((body or "").split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3] + "..."


def _classify_http_error(status_code: int, body: str) -> tuple[str, bool, str]:
    body_lower = body.lower()
    if status_code in (401, 403):
        return "invalid_api_key", False, "API key is invalid or unauthorized"
    if status_code == 429:
        if any(token in body_lower for token in ("insufficient_quota", "quota", "billing", "exceeded your current quota")):
            return "api_key_limit_reached", False, "API key quota or billing limit reached"
        return "rate_limit_reached", True, "API rate limit reached"
    if status_code in (400, 413) and any(
        token in body_lower
        for token in ("context_length", "maximum context", "context window", "too many tokens", "token limit")
    ):
        return "context_limit_reached", False, "Context limit reached"
    if status_code in (408, 409) or status_code >= 500:
        return "temporary_api_error", True, f"Temporary API HTTP {status_code}"
    return "api_error", False, f"LLM API HTTP {status_code}"


def _classify_network_error(exc: BaseException) -> tuple[str, bool, str]:
    text = str(exc)
    reason = getattr(exc, "reason", None)
    if isinstance(reason, TimeoutError) or isinstance(exc, (TimeoutError, socket.timeout)):
        return "timeout", True, "LLM API request timed out"
    if "timed out" in text.lower():
        return "timeout", True, "LLM API request timed out"
    return "network_error", True, "LLM API network request failed"


def _wait_for_request_slot(config: LLMRequestConfig) -> None:
    global _LAST_REQUEST_COMPLETED_AT
    interval = max(float(config.request_interval_seconds or 0.0), 0.0)
    if interval <= 0:
        return
    elapsed = time.monotonic() - _LAST_REQUEST_COMPLETED_AT
    remaining = interval - elapsed
    if remaining > 0:
        time.sleep(remaining)


def _mark_request_completed() -> None:
    global _LAST_REQUEST_COMPLETED_AT
    _LAST_REQUEST_COMPLETED_AT = time.monotonic()


def _raise_http_error(exc: urllib.error.HTTPError) -> None:
    body = exc.read().decode("utf-8", errors="replace")
    category, retryable, summary = _classify_http_error(exc.code, body)
    detail = _summarize_body(body)
    message = f"{summary}: HTTP {exc.code}"
    if detail:
        message += f" - {detail}"
    raise LLMAPIError(
        message,
        category=category,
        retryable=retryable,
        status_code=exc.code,
        details=detail,
    ) from exc


def _raise_network_error(exc: BaseException) -> None:
    category, retryable, summary = _classify_network_error(exc)
    detail = _summarize_body(str(exc))
    message = summary
    if detail:
        message += f": {detail}"
    raise LLMAPIError(message, category=category, retryable=retryable, details=detail) from exc


def call_openai_compatible_chat_with_raw(
    prompt: str,
    config: LLMRequestConfig,
    request_label: str = "LLM chat completion",
) -> tuple[Dict[str, Any], str]:
    payload = {
        "model": config.model,
        "messages": [
            {"role": "system", "content": DEFAULT_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "temperature": config.temperature,
        "max_tokens": config.max_tokens,
    }
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        _chat_completions_url(config.base_url),
        data=data,
        headers={
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    max_retries = max(int(config.max_retries or 0), 0)
    total_attempts = max_retries + 1
    retry_delay = max(float(config.retry_delay_seconds or 0.0), 0.0)
    max_retry_delay = max(float(config.max_retry_delay_seconds or retry_delay), retry_delay)
    last_error: Optional[LLMAPIError] = None

    with _REQUEST_LOCK:
        for attempt in range(1, total_attempts + 1):
            _wait_for_request_slot(config)
            _emit(
                config,
                "info",
                f"sending request for {request_label}",
                request_label=request_label,
                attempt=attempt,
                total_attempts=total_attempts,
                model=config.model,
                prompt_characters=len(prompt),
            )
            started_at = time.monotonic()
            try:
                with urllib.request.urlopen(request, timeout=config.timeout) as response:
                    body = response.read().decode("utf-8")
                    parsed = json.loads(body)
                    elapsed = time.monotonic() - started_at
                    _emit(
                        config,
                        "info",
                        f"LLM request success for {request_label} "
                        f"(attempt {attempt}/{total_attempts}, {elapsed:.2f}s)",
                        request_label=request_label,
                        attempt=attempt,
                        total_attempts=total_attempts,
                        duration_seconds=elapsed,
                    )
                    return parsed, body
            except urllib.error.HTTPError as exc:
                try:
                    _raise_http_error(exc)
                except LLMAPIError as api_error:
                    last_error = api_error
            except (urllib.error.URLError, TimeoutError, socket.timeout, OSError) as exc:
                try:
                    _raise_network_error(exc)
                except LLMAPIError as api_error:
                    last_error = api_error
            except json.JSONDecodeError as exc:
                last_error = LLMAPIError(
                    f"LLM API returned invalid JSON: {exc}",
                    category="invalid_response",
                    retryable=False,
                    details=str(exc),
                )
            finally:
                _mark_request_completed()

            assert last_error is not None
            elapsed = time.monotonic() - started_at
            _emit(
                config,
                "error" if not last_error.retryable or attempt >= total_attempts else "warning",
                f"LLM request error for {request_label} "
                f"(attempt {attempt}/{total_attempts}, {elapsed:.2f}s): "
                f"{last_error.category}: {last_error}",
                request_label=request_label,
                attempt=attempt,
                total_attempts=total_attempts,
                duration_seconds=elapsed,
                error_category=last_error.category,
                status_code=last_error.status_code,
                retryable=last_error.retryable,
            )

            if not last_error.retryable or attempt >= total_attempts:
                raise last_error

            backoff = min(retry_delay * (2 ** (attempt - 1)), max_retry_delay)
            if backoff > 0:
                _emit(
                    config,
                    "info",
                    f"Retrying LLM request for {request_label} in {backoff:.1f}s",
                    request_label=request_label,
                    attempt=attempt,
                    retry_delay_seconds=backoff,
                )
                time.sleep(backoff)

    if last_error is not None:
        raise last_error
    raise LLMAPIError(
        f"LLM API request failed for {request_label}",
        category="unknown_error",
        retryable=False,
    )


def call_openai_compatible_chat(
    prompt: str,
    config: LLMRequestConfig,
    request_label: str = "LLM chat completion",
) -> Dict[str, Any]:
    response_json, _raw_body = call_openai_compatible_chat_with_raw(prompt, config, request_label)
    return response_json


def extract_message_text(response: Dict[str, Any]) -> str:
    choices = response.get("choices", []) or []
    if not choices:
        return ""
    message = choices[0].get("message", {}) or {}
    content = message.get("content", "")
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict):
                parts.append(str(item.get("text") or item.get("content") or ""))
            else:
                parts.append(str(item))
        return "".join(parts)
    return str(content)


def extract_message_json(response: Dict[str, Any]) -> Dict[str, Any]:
    text = extract_message_text(response).strip()
    if not text:
        return {}
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    try:
        parsed = json.loads(text)
        return parsed if isinstance(parsed, dict) else {"patches": parsed if isinstance(parsed, list) else []}
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            try:
                parsed = json.loads(text[start : end + 1])
                return parsed if isinstance(parsed, dict) else {}
            except json.JSONDecodeError:
                return {"analysis_markdown": text, "patches": []}
        return {"analysis_markdown": text, "patches": []}


def env_value(primary: Optional[str], *names: str) -> Optional[str]:
    if primary:
        return primary
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return None
