from __future__ import annotations

from typing import Dict, List, Optional


def _sort_float(value: object) -> float:
    try:
        return float(value)
    except Exception:
        return 0.0


def _sort_int(value: object) -> int:
    try:
        return int(value)
    except Exception:
        return 0


def _top_relations(relations: List[Dict[str, object]], limit: int = 25) -> List[Dict[str, object]]:
    return sorted(
        relations,
        key=lambda item: (
            -_sort_int(item.get("pair_count", 0)),
            -_sort_float(item.get("support_ratio", 0.0)),
            -_sort_float(item.get("edge_lift", 0.0)),
            -_sort_float(item.get("avg_pair_score", 0.0)),
            item.get("request_family_id", ""),
            item.get("response_family_id", ""),
        ),
    )[:limit]



def _interesting_families(families: List[Dict[str, object]], limit: int = 50) -> List[Dict[str, object]]:
    return sorted(
        families,
        key=lambda item: (
            -int(item.get("message_count", 0)),
            -len(item.get("related_families", [])),
            item.get("family_id", ""),
        ),
    )[:limit]


def _fmt_metric(value: object) -> str:
    if isinstance(value, float):
        return f"{value:.4f}".rstrip("0").rstrip(".")
    return str(value)


def _flatten_usage(value: object, prefix: str = "") -> List[tuple[str, object]]:
    if not isinstance(value, dict):
        return []
    items: List[tuple[str, object]] = []
    for key, item in value.items():
        label = f"{prefix}.{key}" if prefix else str(key)
        if isinstance(item, dict):
            items.extend(_flatten_usage(item, label))
        elif isinstance(item, (str, int, float, bool)) or item is None:
            items.append((label, item))
    return items


def _evaluation_section(evaluation: Optional[Dict[str, object]]) -> List[str]:
    if not evaluation:
        return []

    lines: List[str] = ["## Evaluation", ""]
    corpus = evaluation.get("corpus", {}) or {}
    clustering = evaluation.get("clustering", {}) or {}
    boundaries = evaluation.get("boundaries", {}) or {}
    pairs = evaluation.get("pairs", {}) or {}
    relations = evaluation.get("relations", {}) or {}
    semantics = evaluation.get("semantics", {}) or {}
    framing = evaluation.get("framing", {}) or {}
    diagnostics = evaluation.get("diagnostics", {}) or {}
    diagnostic_summary = diagnostics.get("summary", {}) or {}

    lines.append(f"- Messages: `{corpus.get('message_count', 0)}` across `{corpus.get('session_count', 0)}` sessions")
    lines.append(
        f"- Corpus assignment coverage: `{_fmt_metric(clustering.get('corpus_assignment_coverage_ratio', clustering.get('assignment_coverage_ratio', 0.0)))}` "
        f"with `{clustering.get('family_count', 0)}` families"
    )
    if clustering.get("clustering_sample_ratio") is not None:
        lines.append(
            f"- Clustering sample: `{clustering.get('sample_size', 0)}` messages "
            f"ratio=`{_fmt_metric(clustering.get('clustering_sample_ratio', 0.0))}`"
        )
    lines.append(
        f"- Parseable families: `{boundaries.get('parseable_family_count', 0)}` "
        f"of `{boundaries.get('family_count', 0)}`"
    )
    lines.append(
        f"- Pair hypotheses: `{pairs.get('pair_count', 0)}` "
        f"direction_unknown_ratio=`{_fmt_metric(pairs.get('direction_unknown_pair_ratio', 0.0))}`"
    )
    lines.append(
        f"- Relation edges: `{relations.get('edge_count', 0)}` "
        f"echo_edges=`{relations.get('edges_with_echo_fields', 0)}` "
        f"length_relation_edges=`{relations.get('edges_with_length_relations', 0)}`"
    )
    if semantics:
        lines.append(
            f"- Semantic coverage: `{semantics.get('semantic_family_count', 0)}` "
            f"of `{semantics.get('family_count', 0)}` families "
            f"ratio=`{_fmt_metric(semantics.get('semantic_coverage_ratio', 0.0))}`"
        )
        top_labels = semantics.get("top_field_labels", []) or []
        if top_labels:
            labels = ", ".join(f"`{item.get('value')}`x{item.get('count')}" for item in top_labels[:8])
            lines.append(f"- Top semantic labels: {labels}")
    if framing:
        lines.append(
            f"- Framing coverage: `{framing.get('usable_family_count', 0)}` "
            f"of `{framing.get('family_count', 0)}` families "
            f"ratio=`{_fmt_metric(framing.get('usable_family_ratio', 0.0))}`"
        )
    if diagnostic_summary:
        lines.append(
            f"- Clustering diagnostics: warning_families=`{diagnostic_summary.get('warning_family_count', 0)}` "
            f"split_candidates=`{diagnostic_summary.get('split_candidate_count', 0)}` "
            f"merge_candidates=`{diagnostic_summary.get('merge_candidate_count', 0)}`"
        )
    lines.append("")

    top_warnings = diagnostic_summary.get("top_warning_families", []) or []
    if top_warnings:
        lines.append("### Clustering Diagnostic Warnings")
        lines.append("")
        for item in top_warnings[:10]:
            warning_text = ", ".join(str(warning) for warning in (item.get("diagnostic_warnings", []) or [])[:4])
            lines.append(
                f"- `{item.get('family_id')}` | messages=`{item.get('message_count', 0)}` "
                f"split=`{_fmt_metric(item.get('split_suspicion', 0.0))}` "
                f"under_split=`{_fmt_metric(item.get('under_split_score', 0.0))}` "
                f"over_split=`{_fmt_metric(item.get('over_split_score', 0.0))}` warnings={warning_text}"
            )
        lines.append("")

    top_merges = diagnostic_summary.get("top_merge_candidates", []) or []
    if top_merges:
        lines.append("### Clustering Merge Candidates")
        lines.append("")
        for item in top_merges[:10]:
            lines.append(
                f"- `{item.get('family_id')}` -> `{item.get('candidate_family_id')}` "
                f"distance=`{_fmt_metric(item.get('distance', 0.0))}` score=`{_fmt_metric(item.get('score', 0.0))}`"
            )
        lines.append("")

    top_edges = relations.get("top_edges", []) or []
    if top_edges:
        lines.append("### Evaluation Top Relation Edges")
        lines.append("")
        for edge in top_edges[:10]:
            lines.append(
                f"- `{edge.get('request_family_id')}` -> `{edge.get('response_family_id')}` | "
                f"pairs=`{edge.get('pair_count')}` avg_score=`{edge.get('avg_pair_score')}` "
                f"support=`{_fmt_metric(edge.get('support_ratio', 0.0))}` lift=`{_fmt_metric(edge.get('edge_lift', 0.0))}` "
                f"direction=`{_fmt_metric(edge.get('direction_consistency', 0.0))}` order=`{_fmt_metric(edge.get('temporal_order_consistency', 0.0))}` "
                f"echo_fields=`{edge.get('echo_field_count')}` length_rules=`{edge.get('length_relation_count')}`"
            )
        lines.append("")

    return lines


def _llm_analysis_section(llm_analysis: Optional[Dict[str, object]]) -> List[str]:
    if not llm_analysis:
        return []

    lines: List[str] = ["## LLM Analysis", ""]
    model = llm_analysis.get("model")
    if model:
        lines.append(f"- Model: `{model}`")
    usage_items = _flatten_usage(llm_analysis.get("usage"))
    if usage_items:
        usage_text = ", ".join(f"`{key}`=`{_fmt_metric(value)}`" for key, value in usage_items)
        lines.append(f"- Token usage: {usage_text}")
    prompt_stats = llm_analysis.get("prompt_stats")
    if isinstance(prompt_stats, dict):
        if prompt_stats.get("exists") is False:
            lines.append(f"- Prompt file: `{prompt_stats.get('path')}` not found")
        else:
            lines.append(
                f"- Prompt size: `{prompt_stats.get('bytes', 0)}` bytes, "
                f"`{prompt_stats.get('characters', 0)}` characters, "
                f"estimated tokens=`{prompt_stats.get('estimated_tokens', 0)}`"
            )
    if model or usage_items or prompt_stats:
        lines.append("")
    analysis_markdown = llm_analysis.get("analysis_markdown")
    if analysis_markdown:
        lines.append(str(analysis_markdown).strip())
    elif llm_analysis.get("render_only"):
        lines.append("_LLM analysis was skipped because stage 15 ran in render-only mode._")
    else:
        lines.append("_No LLM analysis text is available._")
    lines.append("")
    return lines


def _final_evaluation_section(final_evaluation: Optional[Dict[str, object]]) -> List[str]:
    if not final_evaluation:
        return []

    summary = final_evaluation.get("summary", {}) or {}
    metrics = final_evaluation.get("metrics", {}) or {}
    lines: List[str] = ["## Final Ground Truth Evaluation", ""]
    lines.append(f"- Overall score: `{_fmt_metric(summary.get('overall_score', 0.0))}`")
    lines.append(f"- Verdict: `{summary.get('verdict', 'unknown')}`")
    lines.append(f"- Matched message types: `{summary.get('matched_message_type_count', 0)}` of `{summary.get('ground_truth_message_type_count', 0)}`")
    for label, key in [
        ("Message type matching", "message_type_matching"),
        ("Field boundary", "field_boundary"),
        ("Field semantics", "field_semantics"),
        ("Relations", "relations"),
    ]:
        metric = metrics.get(key, {}) or {}
        lines.append(
            f"- {label}: accuracy=`{_fmt_metric(metric.get('accuracy', 0.0))}` "
            f"precision=`{_fmt_metric(metric.get('precision', 0.0))}` "
            f"recall=`{_fmt_metric(metric.get('recall', 0.0))}` f1=`{_fmt_metric(metric.get('f1_score', 0.0))}`"
        )
    lines.append("")
    return lines



def render_protocol_model_markdown(
    model: Dict[str, object],
    evaluation: Optional[Dict[str, object]] = None,
    llm_analysis: Optional[Dict[str, object]] = None,
    final_evaluation: Optional[Dict[str, object]] = None,
) -> str:
    lines: List[str] = []
    lines.append(f"# {model.get('protocol_name', 'unknown-industrial-protocol')}")
    lines.append("")
    lines.append(f"Version: `{model.get('version', '0.1')}`")
    lines.append("")

    metadata = model.get("metadata", {}) or {}
    if metadata:
        lines.append("## Metadata")
        lines.append("")
        for key, value in metadata.items():
            lines.append(f"- **{key}**: {value}")
        lines.append("")

    lines.extend(_evaluation_section(evaluation))
    lines.extend(_final_evaluation_section(final_evaluation))
    lines.extend(_llm_analysis_section(llm_analysis))

    relations = model.get("relations", []) or []
    if relations:
        lines.append("## Family Relations")
        lines.append("")
        lines.append(f"- Total inferred family edges: `{len(relations)}`")
        lines.append("- Strongest edges:")
        for relation in _top_relations(relations):
            desc = (
                f"- `{relation['request_family_id']}` -> `{relation['response_family_id']}` | "
                f"pairs=`{relation['pair_count']}` avg_score=`{relation['avg_pair_score']}` "
                f"support=`{_fmt_metric(relation.get('support_ratio', 0.0))}` "
                f"lift=`{_fmt_metric(relation.get('edge_lift', 0.0))}` "
                f"direction=`{_fmt_metric(relation.get('direction_consistency', 0.0))}` "
                f"order=`{_fmt_metric(relation.get('temporal_order_consistency', 0.0))}`"
            )
            if relation.get("dominant_direction"):
                desc += f" flow=`{relation.get('dominant_direction')}`"
            if relation.get("echo_fields"):
                desc += f" echo_fields=`{len(relation['echo_fields'])}`"
            if relation.get("length_relations"):
                desc += f" length_rules=`{len(relation['length_relations'])}`"
            lines.append(desc)
        lines.append("")

    families = model.get("families", []) or []
    lines.append("## Families")
    lines.append("")
    lines.append(f"- Total families: `{len(families)}`")
    lines.append(f"- Families shown below: `{min(len(families), 50)}`")
    lines.append("")

    for family in _interesting_families(families):
        lines.append(f"### {family['family_id']}")
        lines.append("")
        lines.append(f"- Role: `{family.get('role', 'unknown')}`")
        lines.append(f"- Messages: `{family.get('message_count', 0)}`")
        lines.append(f"- Template: `{family.get('template', '')}`")
        related = family.get("related_families", [])
        if related:
            lines.append(f"- Related families: {', '.join(f'`{item}`' for item in related[:10])}")
        role_evidence = family.get("evidence", {}).get("role_hint")
        if role_evidence:
            lines.append(f"- Role hint: `{role_evidence}`")
        semantic_summary = family.get("semantic_summary")
        if semantic_summary:
            lines.append(f"- Semantic confidence: `{semantic_summary.get('confidence', 0.0)}`")
        feature_summary = family.get("feature_summary")
        if feature_summary:
            length_stats = feature_summary.get("length_stats", {})
            entropy_summary = feature_summary.get("entropy_summary", {})
            lines.append(
                f"- Length stats: min=`{length_stats.get('min', 0)}` max=`{length_stats.get('max', 0)}` "
                f"distinct=`{length_stats.get('distinct_lengths', 0)}`"
            )
            lines.append(
                f"- Entropy summary: min=`{entropy_summary.get('min', 0.0)}` "
                f"max=`{entropy_summary.get('max', 0.0)}` mean=`{entropy_summary.get('mean', 0.0)}`"
            )
        keyword_summary = family.get("keyword_summary") or {}
        discriminator = keyword_summary.get("keyword") if isinstance(keyword_summary, dict) else None
        discriminator_candidates = (keyword_summary.get("discriminator_candidates", []) or keyword_summary.get("opcode_candidates", []) or []) if isinstance(keyword_summary, dict) else []
        if discriminator:
            lines.append(
                f"- Candidate discriminator offset: `{int(discriminator.get('offset', 0))}` "
                f"cardinality=`{int(discriminator.get('cardinality', 0))}` entropy=`{discriminator.get('entropy', 0.0)}` "
                f"salience=`{discriminator.get('salience_score', 0.0)}` mutual_information=`{discriminator.get('mutual_information', 0.0)}` "
                f"contrastive_separation=`{discriminator.get('contrastive_separation', 0.0)}` confidence=`{discriminator.get('confidence', 0.0)}`"
            )
        if discriminator_candidates:
            compact_candidates = ", ".join(
                f"offset `{int(item.get('start', item.get('offset', 0)))}` conf=`{item.get('confidence', 0.0)}` salience=`{item.get('salience_score', 0.0)}`"
                for item in discriminator_candidates[:3]
            )
            lines.append(f"- Top discriminator candidates: {compact_candidates}")
        framing_summary = family.get("framing_summary") or {}
        layouts = framing_summary.get("layout_hypotheses", []) if isinstance(framing_summary, dict) else []
        if layouts:
            best_layout = layouts[0]
            lines.append(
                f"- Framing hypothesis: header=`{best_layout.get('header_start', 0)}`..`{int(best_layout.get('header_end', 0) or 0) - 1}` "
                f"body_start=`{best_layout.get('body_start', 0)}` confidence=`{best_layout.get('confidence', 0.0)}`"
            )
        lines.append("")

        segments = family.get("segments", [])
        if segments:
            lines.append("#### Segments")
            lines.append("")
            for segment in segments[:10]:
                lines.append(
                    f"- bytes `{segment['start']}`..`{segment['end'] - 1}` | "
                    f"kind=`{segment['kind']}` confidence=`{segment['confidence']}`"
                )
            lines.append("")

        field_hypotheses = family.get("field_hypotheses", [])
        if field_hypotheses:
            lines.append("#### Field Hypotheses")
            lines.append("")
            for field in sorted(field_hypotheses, key=lambda item: (-float(item.get("confidence", 0.0)), int(item.get("start", 0))))[:10]:
                desc = (
                    f"- bytes `{field['start']}`..`{field['start'] + field['length'] - 1}` | "
                    f"type=`{field['field_type']}` confidence=`{field['confidence']}`"
                )
                if field.get("endian"):
                    desc += f" endian=`{field['endian']}`"
                lines.append(desc)
            lines.append("")

        if layouts:
            lines.append("#### Framing Hypotheses")
            lines.append("")
            for layout in layouts[:3]:
                fields = layout.get("field_regions", []) or []
                field_text = ", ".join(
                    f"`{field.get('start')}`..`{int(field.get('end', 0) or 0) - 1}` {field.get('field_type')}"
                    for field in fields[:6]
                ) or "none"
                lines.append(
                    f"- header_end=`{layout.get('header_end', 0)}` body_start=`{layout.get('body_start', 0)}` "
                    f"confidence=`{layout.get('confidence', 0.0)}` fields={field_text}"
                )
            lines.append("")

        if semantic_summary:
            field_labels = semantic_summary.get("field_labels", [])
            if field_labels:
                lines.append("#### Semantic Labels")
                lines.append("")
                for item in sorted(field_labels, key=lambda entry: (-float(entry.get("confidence", 0.0)), int(entry.get("start", 0))))[:10]:
                    lines.append(
                        f"- bytes `{item['start']}`..`{item['start'] + item['length'] - 1}` | "
                        f"label=`{item['label']}` confidence=`{item['confidence']}`"
                    )
                lines.append("")
            notes = semantic_summary.get("notes", [])
            if notes:
                lines.append("#### Notes")
                lines.append("")
                for note in notes[:5]:
                    lines.append(f"- {note}")
                lines.append("")

        if feature_summary:
            motif_stats = feature_summary.get("motif_stats", {})
            top_motifs = motif_stats.get("top_motifs", [])
            if top_motifs:
                lines.append("#### Feature Summary")
                lines.append("")
                lines.append(
                    f"- Messages with repetition: `{motif_stats.get('messages_with_repetition', 0)}` "
                    f"(`{motif_stats.get('messages_with_repetition_ratio', 0.0)}`)"
                )
                lines.append(
                    f"- Repeated n-gram instances: `{motif_stats.get('repeated_ngram_instances', 0)}`"
                )
                motif_text = ", ".join(
                    f"`{item['ngram']}`x{item['count']}" for item in top_motifs[:5]
                )
                lines.append(
                    f"- Top motifs: {motif_text}"
                )
                lines.append("")

    return "\n".join(lines).rstrip() + "\n"
