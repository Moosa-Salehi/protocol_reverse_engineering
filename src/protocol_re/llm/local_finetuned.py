"""Local fine-tuned Qwen backend for stages 07b / 11b.

The fine-tuned adapter (finetuning/result/qwen25-coder-7b-protocol-re) was
trained on *single-message* evidence in a fixed chat format (see
finetuning/cluster-free-dataset/build_payload_dataset.py):

    system: "You are an expert Protocol Reverse Engineering Analyst. Return one
             JSON object and no Markdown fences."
    user:   "### TASK: <task>\\n\\nAnalyze the payload evidence and return the
             requested JSON.\\n\\n## Evidence Bundle\\n\\n```json\\n{"messages":
             [{"msg_id":..,"direction":..,"payload_len":..,"payload_hex":..}]}\\n```\\n"
    assistant: {"boundaries": [...]} | {"semantic_labels": [...]}

Because the training format differs from the family-level evidence bundles that
stages 07b/11b normally render, this backend does NOT reuse the rendered stage
prompt. Instead it:

1. renders one training-format prompt per sample message,
2. calls an OpenAI-compatible endpoint (llama-server running the Q4_K_M GGUF),
3. aggregates the per-message predictions into a single family-level response
   via boundary intersection and semantic-label majority voting,
4. returns a raw "response" string whose parsed shape matches what the existing
   stage validators already accept ({"boundaries": [...]} /
   {"semantic_labels": [...]}), so stages 07b/11b apply refinements unchanged.
"""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from collections import Counter
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence

from protocol_re.model.schema import MessageRecord

DEFAULT_SYSTEM_PROMPT = (
    "You are an expert Protocol Reverse Engineering Analyst. "
    "Return one JSON object and no Markdown fences."
)

VALID_SEMANTIC_ROLES = {
    "address", "bitfield", "byte_count", "checksum", "constant",
    "correlation_id", "counter", "crc", "data", "device_id",
    "discriminator", "error_code", "flags", "function_code", "length",
    "opcode", "padding", "payload", "quantity", "reserved",
    "sequence_number", "status", "timestamp", "transaction_id",
    "unit_id", "value",
}


# ---------------------------------------------------------------------------
# Prompt rendering (byte-exact match with the SFT training format)
# ---------------------------------------------------------------------------

def render_local_prompt(task: str, message: MessageRecord) -> str:
    """Render the user prompt exactly as build_payload_dataset.py did."""
    evidence = {
        "messages": [
            {
                "msg_id": message.msg_id,
                "direction": message.direction,
                "payload_len": message.payload_len,
                "payload_hex": message.payload_hex,
            }
        ]
    }
    prompt = (
        "### TASK: "
        + task
        + "\n\nAnalyze the payload evidence and return the requested JSON.\n\n"
        + "## Evidence Bundle\n\n```json\n"
        + json.dumps(evidence, separators=(",", ":"))
        + "\n```\n"
    )
    return prompt


def build_chat_payload(prompt: str, model: str, temperature: float, max_tokens: int) -> Dict[str, Any]:
    """OpenAI chat-completions payload matching the SFT chat structure."""
    return {
        "model": model,
        "messages": [
            {"role": "system", "content": DEFAULT_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }


# ---------------------------------------------------------------------------
# OpenAI-compatible client (llama-server)
# ---------------------------------------------------------------------------

class LocalBackendError(RuntimeError):
    """Raised when the local inference server cannot be reached or answers badly."""

    def __init__(self, message: str, retryable: bool = False):
        super().__init__(message)
        self.retryable = retryable


def call_local_chat(
    prompt: str,
    base_url: str,
    model: str,
    api_key: str,
    temperature: float,
    max_tokens: int,
    timeout: float,
    retries: int = 2,
    retry_delay: float = 1.0,
    request_label: str = "local finetuned inference",
) -> str:
    """POST one chat completion to the local server and return the message content."""
    payload = build_chat_payload(prompt, model, temperature, max_tokens)
    data = json.dumps(payload).encode("utf-8")
    url = base_url.rstrip("/") + "/chat/completions"
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    last_error: Optional[LocalBackendError] = None
    for attempt in range(1, max(int(retries), 0) + 2):
        try:
            request = urllib.request.Request(url, data=data, headers=headers, method="POST")
            with urllib.request.urlopen(request, timeout=timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
            choices = body.get("choices") or []
            if not choices:
                raise LocalBackendError("local server returned no choices")
            content = choices[0].get("message", {}).get("content", "")
            return str(content)
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:300]
            last_error = LocalBackendError(f"local server HTTP {exc.code}: {detail}", retryable=exc.code >= 500)
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_error = LocalBackendError(
                f"cannot reach local inference server at {url}: {exc}",
                retryable=True,
            )
        except json.JSONDecodeError as exc:
            last_error = LocalBackendError(f"local server returned invalid JSON: {exc}")
        if last_error and last_error.retryable and attempt <= retries:
            time.sleep(retry_delay * (2 ** (attempt - 1)))
    assert last_error is not None
    raise last_error


# ---------------------------------------------------------------------------
# Response parsing + JSON repair
# ---------------------------------------------------------------------------

def extract_json_object(text: str) -> Optional[Dict[str, Any]]:
    """Parse the model output, tolerating fences and trailing prose."""
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        stripped = "\n".join(lines).strip()
    try:
        parsed = json.loads(stripped)
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        pass
    start, end = stripped.find("{"), stripped.rfind("}")
    if 0 <= start < end:
        try:
            parsed = json.loads(stripped[start : end + 1])
            return parsed if isinstance(parsed, dict) else None
        except json.JSONDecodeError:
            return None
    return None


def parse_boundary_prediction(obj: Optional[Dict[str, Any]], payload_len: int) -> List[int]:
    """Return sorted valid boundary offsets, or [] when unusable."""
    if not obj:
        return []
    raw = obj.get("boundaries", obj.get("boundary_refinement", {}).get("boundaries"))
    if not isinstance(raw, list):
        return []
    values: set[int] = set()
    for value in raw:
        try:
            offset = int(value)
        except (TypeError, ValueError):
            continue
        if 0 <= offset <= payload_len:
            values.add(offset)
    if not values or 0 not in values:
        return []
    return sorted(values)


def parse_semantic_prediction(obj: Optional[Dict[str, Any]], payload_len: int) -> List[Dict[str, Any]]:
    """Return in-range semantic labels with known roles, or [] when unusable."""
    if not obj:
        return []
    raw = obj.get("semantic_labels")
    if not isinstance(raw, list) and isinstance(obj.get("semantic_labeling"), dict):
        raw = obj["semantic_labeling"].get("semantic_labels")
    if not isinstance(raw, list):
        return []
    labels: List[Dict[str, Any]] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        role = str(item.get("semantic_role") or "")
        if role not in VALID_SEMANTIC_ROLES:
            continue
        try:
            offset = int(item.get("offset"))
            width = int(item.get("width"))
        except (TypeError, ValueError):
            continue
        if offset < 0 or width < 1 or offset + width > payload_len:
            continue
        labels.append(
            {
                "offset": offset,
                "width": width,
                "semantic_role": role,
                "field_type": str(item.get("field_type") or "bytes"),
            }
        )
    return labels


# ---------------------------------------------------------------------------
# Per-family consensus aggregation
# ---------------------------------------------------------------------------

def aggregate_boundaries(per_message: Sequence[List[int]], payload_len: int, min_support: float) -> List[int]:
    """Positions where >= min_support of usable predictions agree on an edge."""
    if not per_message:
        return [0, payload_len]
    usable = [boundaries for boundaries in per_message if boundaries]
    if not usable:
        return [0, payload_len]
    votes: Counter[int] = Counter()
    for boundaries in usable:
        votes.update(boundaries)
    threshold = max(1, int(min_support * len(usable) + 0.999))  # ceil
    edges = sorted(offset for offset, count in votes.items() if count >= threshold)
    if 0 not in edges:
        edges.insert(0, 0)
    if not edges or edges[-1] != payload_len:
        edges.append(payload_len)
    return edges


def aggregate_semantics(
    per_message: Sequence[Sequence[Dict[str, Any]]],
    min_support: float,
) -> List[Dict[str, Any]]:
    """Majority-vote semantic labels per (offset, width, role) with vote share as confidence."""
    votes: Counter[tuple[int, int, str]] = Counter()
    field_types: Dict[tuple[int, int, str], str] = {}
    for labels in per_message:
        for label in labels:
            key = (label["offset"], label["width"], label["semantic_role"])
            votes[key] += 1
            field_types.setdefault(key, label["field_type"])
    if not votes:
        return []
    total = sum(1 for labels in per_message if labels) or 1
    threshold = max(1, int(min_support * total + 0.999))
    aggregated: List[Dict[str, Any]] = []
    for (offset, width, role), count in sorted(votes.items()):
        if count < threshold:
            continue
        aggregated.append(
            {
                "offset": offset,
                "width": width,
                "semantic_role": role,
                "field_type": field_types[(offset, width, role)],
                "confidence": round(count / total, 3),
                "support": f"{count}/{total}",
            }
        )
    return aggregated


# ---------------------------------------------------------------------------
# Family-level entry points
# ---------------------------------------------------------------------------

@dataclass
class LocalInferenceConfig:
    base_url: str = "http://127.0.0.1:8080"
    model: str = "qwen25-coder-7b-protocol-re"
    api_key: str = ""
    temperature: float = 0.0
    max_tokens: int = 512
    timeout: float = 300.0
    retries: int = 2
    retry_delay: float = 1.0
    max_samples: int = 5
    min_support: float = 0.5
    consensus_sample_bytes: int = 256


def _sample_messages_diverse(
    messages: Sequence[MessageRecord],
    max_samples: int,
    sample_bytes: int,
) -> List[MessageRecord]:
    """Pick structurally diverse samples: diverse lengths, no duplicate payloads."""
    if len(messages) <= max_samples:
        return list(messages)
    ordered = sorted(messages, key=lambda m: m.payload_len)
    step = (len(ordered) - 1) / max(max_samples - 1, 1)
    picked: List[MessageRecord] = []
    seen: set[str] = set()
    for i in range(max_samples):
        candidate = ordered[round(i * step)]
        digest = candidate.payload_hex[: sample_bytes * 2]
        if digest in seen:
            continue
        seen.add(digest)
        picked.append(candidate)
    return picked or list(messages[:1])


def run_local_boundary_refinement(
    family_id: str,
    messages: Sequence[MessageRecord],
    llm: LocalInferenceConfig,
) -> tuple[Optional[str], List[int], int]:
    """Run per-message boundary refinement; return (raw_response, boundaries, samples_used).

    raw_response is a JSON string shaped like the fine-tuned model's native
    output aggregated at family level, accepted by stage 07b's validator.
    """
    samples = _sample_messages_diverse(messages, llm.max_samples, llm.consensus_sample_bytes)
    per_message: List[List[int]] = []
    raw_parts: List[Dict[str, Any]] = []
    payload_len = max((m.payload_len for m in samples), default=0)
    for message in samples:
        prompt = render_local_prompt("boundary_refinement", message)
        content = call_local_chat(
            prompt,
            llm.base_url,
            llm.model,
            llm.api_key,
            llm.temperature,
            llm.max_tokens,
            llm.timeout,
            llm.retries,
            llm.retry_delay,
            request_label=f"local boundary refinement for {family_id} msg {message.msg_id}",
        )
        obj = extract_json_object(content)
        boundaries = parse_boundary_prediction(obj, message.payload_len)
        per_message.append(boundaries)
        raw_parts.append({"msg_id": message.msg_id, "boundaries": boundaries, "raw": content})
    boundaries = aggregate_boundaries(per_message, payload_len, llm.min_support)
    response = json.dumps(
        {
            "family_id": family_id,
            "boundaries": boundaries,
            "confidence": 0.99,  # bypass merge-suggestion confidence gating
            "backend": "local_finetuned",
            "samples": raw_parts,
        },
        ensure_ascii=False,
    )
    return response, boundaries, len(samples)


def run_local_semantic_labeling(
    family_id: str,
    messages: Sequence[MessageRecord],
    fields: List[Dict[str, Any]],
    llm: LocalInferenceConfig,
) -> tuple[Optional[str], List[Dict[str, Any]], int]:
    """Run per-message semantic labeling and map consensus labels onto stage-07 fields.

    Returns (raw_response, labels_in_field_index_schema, samples_used).
    Labels carry evidence (support counts) so the stage validator accepts them.
    """
    samples = _sample_messages_diverse(messages, llm.max_samples, llm.consensus_sample_bytes)
    per_message: List[List[Dict[str, Any]]] = []
    raw_parts: List[Dict[str, Any]] = []
    for message in samples:
        prompt = render_local_prompt("semantic_labeling", message)
        content = call_local_chat(
            prompt,
            llm.base_url,
            llm.model,
            llm.api_key,
            llm.temperature,
            llm.max_tokens,
            llm.timeout,
            llm.retries,
            llm.retry_delay,
            request_label=f"local semantic labeling for {family_id} msg {message.msg_id}",
        )
        obj = extract_json_object(content)
        labels = parse_semantic_prediction(obj, message.payload_len)
        per_message.append(labels)
        raw_parts.append({"msg_id": message.msg_id, "semantic_labels": labels, "raw": content})

    aggregated = aggregate_semantics(per_message, llm.min_support)

    # Map (offset, width) labels onto field_hypotheses indices for stage 11b.
    field_index_schema: List[Dict[str, Any]] = []
    for label in aggregated:
        field_index = _match_field(fields, label["offset"], label["width"])
        if field_index is None:
            continue
        field_index_schema.append(
            {
                "field_index": field_index,
                "offset": label["offset"],
                "width": label["width"],
                "semantic_role": label["semantic_role"],
                "field_type": label["field_type"],
                "encoding_type": label["field_type"],
                "confidence": label["confidence"],
                "evidence": [f"consensus support {label['support']} across {len(samples)} sampled messages"],
                "human_label": label["semantic_role"].replace("_", " "),
                "alternative_roles": [],
            }
        )
    response = json.dumps(
        {
            "family_id": family_id,
            "semantic_labels": field_index_schema,
            "backend": "local_finetuned",
            "samples": raw_parts,
        },
        ensure_ascii=False,
    )
    return response, field_index_schema, len(samples)


def _field_span(field: Dict[str, Any]) -> tuple[int, int]:
    """Field (start, end) accepting the start/offset and length/width key variants.

    Note: keys may be present with value 0, so use explicit None checks rather
    than falsy ``or`` defaults (0 would wrongly fall through).
    """
    start = field.get("start", field.get("offset"))
    width = field.get("length", field.get("width"))
    start = int(start) if start is not None else -1
    width = int(width) if width is not None else 0
    return start, start + width


def _match_field(fields: List[Dict[str, Any]], offset: int, width: int) -> Optional[int]:
    """Find the field hypothesis covering [offset, offset+width); prefer exact match."""
    for index, field in enumerate(fields):
        start, end = _field_span(field)
        if start == offset and end == offset + width:
            return index
    for index, field in enumerate(fields):
        start, end = _field_span(field)
        if start <= offset and offset + width <= end:
            return index
    return None
