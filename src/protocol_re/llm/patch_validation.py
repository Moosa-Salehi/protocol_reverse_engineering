from __future__ import annotations

import copy
import re
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Sequence

from protocol_re.llm.patches import (
    ALLOWED_FIELD_TYPES,
    ALLOWED_PATCH_OPS,
    ALLOWED_SEMANTIC_ROLES,
    JsonPatchOperation,
    apply_json_patch,
)


ALLOWED_PATH_PATTERNS = [
    re.compile(r"^/families/\d+/role$"),
    re.compile(r"^/families/\d+/semantic_summary$"),
    re.compile(r"^/families/\d+/semantic_summary/(role|confidence|field_labels|notes)$"),
    re.compile(r"^/families/\d+/semantic_summary/field_labels/(-|\d+)$"),
    re.compile(r"^/families/\d+/field_hypotheses/\d+/(field_type|confidence|endian|attributes)$"),
    re.compile(r"^/families/\d+/field_hypotheses/\d+/attributes/(encoding|semantic_role|label|llm_refined)$"),
    re.compile(r"^/relations/\d+/(relation_type|semantic_label|confidence|attributes)$"),
    re.compile(r"^/relations/\d+/attributes/(relation_label|llm_refined)$"),
    re.compile(r"^/metadata/protocol_hints$"),
    re.compile(r"^/metadata/protocol_hints/(-|\d+)$"),
    re.compile(r"^/metadata/llm_refinement$"),
]


@dataclass
class PatchValidationResult:
    patch: Dict[str, Any]
    accepted: bool
    reasons: List[str] = field(default_factory=list)
    evidence_support: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def validate_and_filter_patches(
    model: Dict[str, Any],
    patches: Sequence[JsonPatchOperation],
    evidence: Optional[Dict[str, Any]] = None,
    schema: Optional[Dict[str, Any]] = None,
) -> tuple[List[JsonPatchOperation], Dict[str, Any]]:
    working = copy.deepcopy(model)
    accepted: List[JsonPatchOperation] = []
    results: List[PatchValidationResult] = []

    for patch in patches:
        reasons = _basic_patch_rejections(working, patch)
        support = _evidence_support(patch, evidence or {})
        support_categories = {item for item in support if item in {"statistical", "symbolic", "neural"}}
        if not support_categories:
            reasons.append("Patch lacks statistical, symbolic, or neural evidence support")
        if not reasons:
            try:
                candidate = apply_json_patch(working, [patch])
                schema_errors = validate_protocol_model(candidate, schema=schema)
                if schema_errors:
                    reasons.extend([f"Schema validation failed: {error}" for error in schema_errors])
                else:
                    working = candidate
                    accepted.append(patch)
            except Exception as exc:
                reasons.append(f"Patch application failed: {exc}")
        results.append(
            PatchValidationResult(
                patch=patch.to_dict(),
                accepted=not reasons,
                reasons=reasons,
                evidence_support=support,
            )
        )

    return accepted, {
        "artifact_type": "llm_patch_validation",
        "input_patch_count": len(patches),
        "accepted_patch_count": len(accepted),
        "rejected_patch_count": len(patches) - len(accepted),
        "results": [result.to_dict() for result in results],
    }


def validate_protocol_model(model: Dict[str, Any], schema: Optional[Dict[str, Any]] = None) -> List[str]:
    try:
        import jsonschema  # type: ignore

        if schema:
            validator = jsonschema.Draft202012Validator(schema)
            return [error.message for error in validator.iter_errors(model)]
    except Exception:
        pass
    return _fallback_protocol_model_errors(model)


def _fallback_protocol_model_errors(model: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    if not isinstance(model.get("protocol_name"), str):
        errors.append("protocol_name must be a string")
    if not isinstance(model.get("version"), str):
        errors.append("version must be a string")
    families = model.get("families")
    if not isinstance(families, list):
        errors.append("families must be an array")
        return errors
    for family_index, family in enumerate(families):
        if not isinstance(family, dict):
            errors.append(f"families/{family_index} must be an object")
            continue
        for key in ("family_id", "role", "template"):
            if not isinstance(family.get(key), str):
                errors.append(f"families/{family_index}/{key} must be a string")
        if not isinstance(family.get("message_count"), int) or family.get("message_count", 0) < 0:
            errors.append(f"families/{family_index}/message_count must be a non-negative integer")
        semantic = family.get("semantic_summary")
        if semantic is not None:
            if not isinstance(semantic, dict):
                errors.append(f"families/{family_index}/semantic_summary must be object or null")
            elif "confidence" in semantic and not _is_probability(semantic.get("confidence")):
                errors.append(f"families/{family_index}/semantic_summary/confidence must be 0..1")
        for field_index, item in enumerate(family.get("field_hypotheses", []) or []):
            if not isinstance(item, dict):
                errors.append(f"families/{family_index}/field_hypotheses/{field_index} must be an object")
                continue
            if "confidence" in item and not _is_probability(item.get("confidence")):
                errors.append(f"families/{family_index}/field_hypotheses/{field_index}/confidence must be 0..1")
            if not isinstance(item.get("field_type"), str):
                errors.append(f"families/{family_index}/field_hypotheses/{field_index}/field_type must be a string")
    return errors


def _basic_patch_rejections(model: Dict[str, Any], patch: JsonPatchOperation) -> List[str]:
    reasons: List[str] = []
    if patch.op not in ALLOWED_PATCH_OPS:
        reasons.append(f"Patch op is not allowed: {patch.op}")
    if not any(pattern.match(patch.path) for pattern in ALLOWED_PATH_PATTERNS):
        reasons.append(f"Patch path is not in the initial safe allow-list: {patch.path}")
    if patch.op == "add" and not _path_allows_add(patch.path):
        reasons.append(f"Add operation is not allowed for path: {patch.path}")
    if patch.op == "test":
        return reasons
    reasons.extend(_value_rejections(patch))
    if not _path_exists_for_replace(model, patch):
        reasons.append(f"Replace path does not exist: {patch.path}")
    return reasons


def _path_allows_add(path: str) -> bool:
    return (
        "/field_labels/" in path
        or path.startswith("/metadata/protocol_hints")
        or path in {"/metadata/llm_refinement", "/families/0/semantic_summary"}
        or re.match(r"^/families/\d+/semantic_summary$", path) is not None
    )


def _path_exists_for_replace(model: Dict[str, Any], patch: JsonPatchOperation) -> bool:
    if patch.op != "replace":
        return True
    current: Any = model
    try:
        for part in patch.path.split("/")[1:]:
            part = part.replace("~1", "/").replace("~0", "~")
            current = current[int(part)] if isinstance(current, list) else current[part]
        return True
    except Exception:
        return False


def _value_rejections(patch: JsonPatchOperation) -> List[str]:
    path = patch.path
    value = patch.value
    reasons: List[str] = []
    if path.endswith("/confidence") and not _is_probability(value):
        reasons.append("Confidence values must be numeric probabilities in [0, 1]")
    if path.endswith("/field_type") and str(value) not in ALLOWED_FIELD_TYPES:
        reasons.append(f"Field type is not in the controlled vocabulary: {value}")
    if path.endswith("/role") and str(value) not in ALLOWED_SEMANTIC_ROLES:
        reasons.append(f"Semantic role is not in the controlled vocabulary: {value}")
    if path.endswith("/field_labels") and not isinstance(value, list):
        reasons.append("field_labels replacement must be an array")
    if "/field_labels/" in path and not _valid_field_label(value):
        reasons.append("field label additions must include start, length, label, and confidence")
    if path.startswith("/metadata/protocol_hints") and not _valid_protocol_hint(value, path):
        reasons.append("protocol hints must be short strings or objects with hint/confidence/evidence_refs")
    return reasons


def _valid_field_label(value: Any) -> bool:
    if not isinstance(value, dict):
        return False
    return (
        isinstance(value.get("start"), int)
        and isinstance(value.get("length"), int)
        and value.get("length", 0) >= 0
        and isinstance(value.get("label"), str)
        and _is_probability(value.get("confidence"))
    )


def _valid_protocol_hint(value: Any, path: str) -> bool:
    if path == "/metadata/protocol_hints":
        return isinstance(value, list)
    if isinstance(value, str):
        return len(value) <= 240
    return isinstance(value, dict) and isinstance(value.get("hint"), str) and _is_probability(value.get("confidence", 0.5))


def _is_probability(value: Any) -> bool:
    return isinstance(value, (int, float)) and 0.0 <= float(value) <= 1.0


def _evidence_support(patch: JsonPatchOperation, evidence: Dict[str, Any]) -> List[str]:
    support: List[str] = []
    evidence_refs = patch.evidence_refs or []
    if evidence_refs:
        support.extend([f"explicit_ref:{ref}" for ref in evidence_refs[:5]])
    path_context = _context_from_path(patch.path)
    if _has_statistical_support(patch, evidence, path_context):
        support.append("statistical")
    if _has_symbolic_support(patch, evidence, path_context):
        support.append("symbolic")
    if _has_neural_support(patch, evidence, path_context):
        support.append("neural")
    return sorted(set(support))


def _context_from_path(path: str) -> Dict[str, Optional[int]]:
    match = re.match(r"^/families/(\d+)", path)
    family_index = int(match.group(1)) if match else None
    field_match = re.match(r"^/families/\d+/field_hypotheses/(\d+)", path)
    field_index = int(field_match.group(1)) if field_match else None
    relation_match = re.match(r"^/relations/(\d+)", path)
    relation_index = int(relation_match.group(1)) if relation_match else None
    return {"family_index": family_index, "field_index": field_index, "relation_index": relation_index}


def _family_evidence(evidence: Dict[str, Any], family_index: Optional[int]) -> Dict[str, Any]:
    families = evidence.get("families", []) or []
    if family_index is None or family_index >= len(families):
        return {}
    item = families[family_index]
    return item if isinstance(item, dict) else {}


def _has_statistical_support(patch: JsonPatchOperation, evidence: Dict[str, Any], context: Dict[str, Optional[int]]) -> bool:
    family = _family_evidence(evidence, context.get("family_index"))
    if family.get("features") or family.get("segments") or family.get("fields"):
        return True
    return bool((evidence.get("global_hypotheses") or {}).get("low_confidence_areas"))


def _has_symbolic_support(patch: JsonPatchOperation, evidence: Dict[str, Any], context: Dict[str, Optional[int]]) -> bool:
    family = _family_evidence(evidence, context.get("family_index"))
    if family.get("semantic_labels") or family.get("discriminator_candidates") or family.get("framing"):
        return True
    relation_index = context.get("relation_index")
    relations = evidence.get("relations", []) or []
    return relation_index is not None and relation_index < len(relations)


def _has_neural_support(patch: JsonPatchOperation, evidence: Dict[str, Any], context: Dict[str, Optional[int]]) -> bool:
    family = _family_evidence(evidence, context.get("family_index"))
    neural = family.get("neural") or {}
    if any(value not in (None, {}, []) for value in neural.values()):
        return True
    neural_context = evidence.get("neural_context") or {}
    return any(value not in (None, {}, []) for value in neural_context.values())
