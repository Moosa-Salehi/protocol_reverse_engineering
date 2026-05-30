from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from protocol_re.llm.patches import JsonPatchOperation, apply_json_patch, extract_patches_from_analysis, parse_patch_bundle
from protocol_re.llm.patch_validation import validate_and_filter_patches


def collect_llm_patches(analysis: Dict[str, Any]) -> Dict[str, Any]:
    patches = extract_patches_from_analysis(analysis)
    return {
        "artifact_type": "llm_protocol_model_patches",
        "source_analysis": analysis.get("source_evidence"),
        "patch_count": len(patches),
        "patches": [patch.to_dict() for patch in patches],
    }


def refine_protocol_model(
    protocol_model: Dict[str, Any],
    patch_bundle: Dict[str, Any],
    evidence: Optional[Dict[str, Any]] = None,
    schema: Optional[Dict[str, Any]] = None,
) -> tuple[Dict[str, Any], Dict[str, Any]]:
    patches = parse_patch_bundle(patch_bundle)
    accepted, validation = validate_and_filter_patches(protocol_model, patches, evidence=evidence, schema=schema)
    refined = apply_json_patch(protocol_model, accepted)
    metadata = dict(refined.get("metadata", {}) or {})
    metadata["llm_refinement"] = {
        "artifact_type": "llm_refinement_summary",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "input_patch_count": validation["input_patch_count"],
        "accepted_patch_count": validation["accepted_patch_count"],
        "rejected_patch_count": validation["rejected_patch_count"],
    }
    refined["metadata"] = metadata
    return refined, validation


def refinement_delta_summary(base_model: Dict[str, Any], refined_model: Dict[str, Any]) -> Dict[str, Any]:
    base_families = base_model.get("families", []) or []
    refined_families = refined_model.get("families", []) or []
    changed_families = []
    for index, refined in enumerate(refined_families):
        base = base_families[index] if index < len(base_families) else {}
        if refined != base:
            changed_families.append(refined.get("family_id", str(index)))
    return {
        "changed_family_count": len(changed_families),
        "changed_family_ids": changed_families[:50],
        "relation_count_delta": len(refined_model.get("relations", []) or []) - len(base_model.get("relations", []) or []),
        "protocol_hint_count": len(((refined_model.get("metadata") or {}).get("protocol_hints") or []))
        - len(((base_model.get("metadata") or {}).get("protocol_hints") or [])),
    }
