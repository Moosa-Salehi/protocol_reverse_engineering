from __future__ import annotations

from typing import Dict, List, Optional



def _top_relations(relations: List[Dict[str, object]], limit: int = 25) -> List[Dict[str, object]]:
    return sorted(
        relations,
        key=lambda item: (
            -int(item.get("pair_count", 0)),
            -float(item.get("avg_pair_score", 0.0)),
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
    lines.append("")

    top_edges = relations.get("top_edges", []) or []
    if top_edges:
        lines.append("### Evaluation Top Relation Edges")
        lines.append("")
        for edge in top_edges[:10]:
            lines.append(
                f"- `{edge.get('request_family_id')}` -> `{edge.get('response_family_id')}` | "
                f"pairs=`{edge.get('pair_count')}` avg_score=`{edge.get('avg_pair_score')}` "
                f"echo_fields=`{edge.get('echo_field_count')}` length_rules=`{edge.get('length_relation_count')}`"
            )
        lines.append("")

    return lines


def _llm_analysis_section(llm_analysis: Optional[Dict[str, object]]) -> List[str]:
    if not llm_analysis:
        return []

    lines: List[str] = ["## LLM Analysis", ""]
    analysis_markdown = llm_analysis.get("analysis_markdown")
    if analysis_markdown:
        lines.append(str(analysis_markdown).strip())
    elif llm_analysis.get("render_only"):
        lines.append("_LLM analysis was skipped because stage 15 ran in render-only mode._")
    else:
        lines.append("_No LLM analysis text is available._")
    lines.append("")
    return lines



def render_protocol_model_markdown(
    model: Dict[str, object],
    evaluation: Optional[Dict[str, object]] = None,
    llm_analysis: Optional[Dict[str, object]] = None,
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
                f"pairs=`{relation['pair_count']}` avg_score=`{relation['avg_pair_score']}`"
            )
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
        keyword = keyword_summary.get("keyword") if isinstance(keyword_summary, dict) else None
        if keyword:
            lines.append(
                f"- Candidate keyword offset: `{int(keyword.get('offset', 0))}` "
                f"cardinality=`{int(keyword.get('cardinality', 0))}` entropy=`{keyword.get('entropy', 0.0)}`"
            )
        subcluster_summary = family.get("subcluster_summary") or {}
        if subcluster_summary:
            lines.append(
                f"- Best subcluster strategy: `{subcluster_summary.get('best_strategy', 'unknown')}` "
                f"formats=`{len(subcluster_summary.get('formats', {}) or {})}`"
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
