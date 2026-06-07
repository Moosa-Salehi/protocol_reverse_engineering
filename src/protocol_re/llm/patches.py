from __future__ import annotations

import copy
import json
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Iterable, List, Optional


ALLOWED_PATCH_OPS = {"add", "replace", "remove", "test"}

ALLOWED_FIELD_TYPES = {
    "blob",
    "bytes",
    "checksum",
    "constant",
    "counter",
    "counter_or_transaction_id",
    "discriminator",
    "flags",
    "identifier",
    "keyword",
    "length",
    "opcode",
    "payload",
    "selector",
    "status",
    "timestamp",
    "uint8",
    "uint16",
    "uint16_be",
    "uint16_le",
    "uint32",
    "uint32_be",
    "uint32_le",
    "uint64",
    "uint64_be",
    "uint64_le",
    "unknown",
}

ALLOWED_SEMANTIC_ROLES = {"request", "response", "mixed", "unknown", "command", "reply", "event", "ack", "error"}


@dataclass
class JsonPatchOperation:
    op: str
    path: str
    value: Any = None
    from_path: Optional[str] = None
    evidence_refs: List[str] = field(default_factory=list)
    rationale: str = ""

    @classmethod
    def from_dict(cls, item: Dict[str, Any]) -> "JsonPatchOperation":
        return cls(
            op=str(item.get("op", "")),
            path=str(item.get("path", "")),
            value=item.get("value"),
            from_path=item.get("from"),
            evidence_refs=[str(ref) for ref in item.get("evidence_refs", []) or []],
            rationale=str(item.get("rationale", "")),
        )

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        if self.from_path is None:
            data.pop("from_path", None)
        else:
            data["from"] = data.pop("from_path")
        if self.value is None and self.op not in {"add", "replace", "test"}:
            data.pop("value", None)
        return data


def parse_patch_bundle(payload: Any) -> List[JsonPatchOperation]:
    if isinstance(payload, str):
        payload = _loads_json_like(payload)
    if isinstance(payload, dict):
        if isinstance(payload.get("patches"), list):
            payload = payload["patches"]
        elif isinstance(payload.get("json_patches"), list):
            payload = payload["json_patches"]
        elif isinstance(payload.get("patch"), list):
            payload = payload["patch"]
        else:
            payload = []
    if not isinstance(payload, list):
        return []
    return [JsonPatchOperation.from_dict(item) for item in payload if isinstance(item, dict)]


def extract_patches_from_analysis(analysis: Dict[str, Any]) -> List[JsonPatchOperation]:
    for key in ("patches", "json_patches", "accepted_patches"):
        if isinstance(analysis.get(key), list):
            return parse_patch_bundle(analysis[key])
    synthesis = analysis.get("synthesis")
    if isinstance(synthesis, dict):
        for key in ("patches", "json_patches", "accepted_patches"):
            if isinstance(synthesis.get(key), list):
                return parse_patch_bundle(synthesis[key])
    text = analysis.get("patches_json") or analysis.get("analysis_json") or analysis.get("analysis_markdown")
    if isinstance(text, str) and text.strip():
        return parse_patch_bundle(text)
    return []


def apply_json_patch(document: Dict[str, Any], patches: Iterable[JsonPatchOperation]) -> Dict[str, Any]:
    result = copy.deepcopy(document)
    for patch in patches:
        _apply_operation(result, patch)
    return result


def _loads_json_like(text: str) -> Any:
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        stripped = "\n".join(lines).strip()
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        start = min((pos for pos in [stripped.find("["), stripped.find("{")] if pos >= 0), default=-1)
        if start < 0:
            return []
        end = max(stripped.rfind("]"), stripped.rfind("}"))
        if end <= start:
            return []
        try:
            return json.loads(stripped[start : end + 1])
        except json.JSONDecodeError:
            return []


def _decode_pointer(path: str) -> List[str]:
    if path == "":
        return []
    if not path.startswith("/"):
        raise ValueError(f"JSON pointer must start with '/': {path}")
    return [part.replace("~1", "/").replace("~0", "~") for part in path.split("/")[1:]]


def _resolve_parent(document: Any, path: str) -> tuple[Any, str]:
    parts = _decode_pointer(path)
    if not parts:
        raise ValueError("Patch path must not target the document root")
    current = document
    for part in parts[:-1]:
        if isinstance(current, list):
            current = current[int(part)]
        elif isinstance(current, dict):
            current = current[part]
        else:
            raise ValueError(f"Cannot traverse through scalar at {path}")
    return current, parts[-1]


def _get_value(document: Any, path: str) -> Any:
    current = document
    for part in _decode_pointer(path):
        if isinstance(current, list):
            current = current[int(part)]
        elif isinstance(current, dict):
            current = current[part]
        else:
            raise ValueError(f"Cannot traverse through scalar at {path}")
    return current


def _apply_operation(document: Dict[str, Any], patch: JsonPatchOperation) -> None:
    if patch.op not in ALLOWED_PATCH_OPS:
        raise ValueError(f"Unsupported patch op: {patch.op}")
    if patch.op == "test":
        if _get_value(document, patch.path) != patch.value:
            raise ValueError(f"Patch test failed at {patch.path}")
        return
    parent, key = _resolve_parent(document, patch.path)
    if isinstance(parent, list):
        if key == "-":
            if patch.op != "add":
                raise ValueError("Only add may append to arrays")
            parent.append(copy.deepcopy(patch.value))
            return
        index = int(key)
        if patch.op == "add":
            parent.insert(index, copy.deepcopy(patch.value))
        elif patch.op == "remove":
            del parent[index]
        else:
            parent[index] = copy.deepcopy(patch.value)
        return
    if not isinstance(parent, dict):
        raise ValueError(f"Cannot apply patch below scalar at {patch.path}")
    if patch.op == "remove":
        if key not in parent:
            raise ValueError(f"Cannot remove missing key at {patch.path}")
        del parent[key]
        return
    if patch.op == "replace" and key not in parent:
        raise ValueError(f"Cannot replace missing key at {patch.path}")
    parent[key] = copy.deepcopy(patch.value)
