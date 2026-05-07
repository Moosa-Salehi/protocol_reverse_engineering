from __future__ import annotations

from html import escape
from typing import Any, Dict, Iterable, List, Optional


def _families(model: Dict[str, Any], limit: int = 40) -> List[Dict[str, Any]]:
    return sorted(
        model.get("families", []) or [],
        key=lambda item: (-int(item.get("message_count", 0) or 0), str(item.get("family_id", ""))),
    )[:limit]


def _relations(model: Dict[str, Any], limit: int = 20) -> List[Dict[str, Any]]:
    return sorted(
        model.get("relations", []) or [],
        key=lambda item: (-int(item.get("pair_count", 0) or 0), -float(item.get("avg_pair_score", 0.0) or 0.0)),
    )[:limit]


def _text(value: Any) -> str:
    return escape(str(value))


def _pct(value: Any) -> str:
    try:
        return f"{float(value) * 100:.1f}%"
    except Exception:
        return "0.0%"


def _bar(value: Any, label: str = "") -> str:
    try:
        pct = max(0.0, min(100.0, float(value) * 100.0))
    except Exception:
        pct = 0.0
    return f'<div class="bar" aria-label="{escape(label)}"><span style="width:{pct:.1f}%"></span></div>'


def _pill(label: Any, tone: str = "") -> str:
    return f'<span class="pill {escape(tone)}">{_text(label)}</span>'


def _metric(label: str, value: Any, hint: str = "") -> str:
    hint_html = f'<small>{_text(hint)}</small>' if hint else ""
    return f'<article class="metric"><strong>{_text(value)}</strong><span>{_text(label)}</span>{hint_html}</article>'


def _flatten_usage(value: Any, prefix: str = "") -> List[tuple[str, Any]]:
    if not isinstance(value, dict):
        return []
    items: List[tuple[str, Any]] = []
    for key, item in value.items():
        label = f"{prefix}.{key}" if prefix else str(key)
        if isinstance(item, dict):
            items.extend(_flatten_usage(item, label))
        elif isinstance(item, (str, int, float, bool)) or item is None:
            items.append((label, item))
    return items


def _kv_rows(items: Dict[str, Any]) -> str:
    rows = []
    for key, value in items.items():
        rows.append(f'<tr><th>{_text(key)}</th><td>{_text(value)}</td></tr>')
    return "".join(rows)


def _field_rows(fields: Iterable[Dict[str, Any]], limit: int = 8) -> str:
    rows = []
    sorted_fields = sorted(
        list(fields),
        key=lambda item: (-float(item.get("confidence", 0.0) or 0.0), int(item.get("start", 0) or 0)),
    )[:limit]
    for field in sorted_fields:
        start = int(field.get("start", 0) or 0)
        length = int(field.get("length", 0) or 0)
        rows.append(
            "<tr>"
            f"<td><code>{start}..{max(start, start + length - 1)}</code></td>"
            f"<td>{_text(field.get('field_type') or field.get('label') or 'unknown')}</td>"
            f"<td>{_text(field.get('confidence', 0.0))}</td>"
            "</tr>"
        )
    return "".join(rows) or '<tr><td colspan="3">No field evidence.</td></tr>'


def _segment_map(segments: List[Dict[str, Any]], max_width: int = 80) -> str:
    if not segments:
        return '<div class="segment-map empty">No segments</div>'
    total = max(int(segment.get("end", 0) or 0) for segment in segments) or 1
    parts = []
    for segment in segments[:max_width]:
        start = int(segment.get("start", 0) or 0)
        end = int(segment.get("end", start) or start)
        width = max(2.5, ((end - start) / total) * 100.0)
        kind = str(segment.get("kind", "unknown"))
        parts.append(
            f'<span class="seg {escape(kind)}" style="width:{width:.2f}%" title="{start}..{end - 1} {escape(kind)}"></span>'
        )
    return f'<div class="segment-map">{"".join(parts)}</div>'


def _feature_panel(feature_summary: Dict[str, Any]) -> str:
    if not feature_summary:
        return '<p class="muted">No feature summary attached.</p>'
    length_profile = ((feature_summary.get("structure_stats") or {}).get("length_profile") or {})
    motif_stats = feature_summary.get("motif_stats", {}) or {}
    motifs = motif_stats.get("top_motifs", []) or []
    wide = motif_stats.get("wide_repeated_motifs", []) or []
    motif_html = "".join(_pill(f"{m.get('ngram')} x{m.get('count')}", "motif") for m in motifs[:5]) or '<span class="muted">None</span>'
    wide_html = "".join(_pill(f"{m.get('ngram')} x{m.get('count')}", "wide") for m in wide[:5]) or '<span class="muted">None</span>'
    return (
        '<div class="feature-grid">'
        f'{_metric("Length profile", length_profile.get("kind", "unknown"), "modal " + str(length_profile.get("modal_length", "?")))}'
        f'{_metric("Entropy mean", (feature_summary.get("entropy_summary") or {}).get("mean", 0))}'
        f'{_metric("Repetition ratio", _pct(motif_stats.get("messages_with_repetition_ratio", 0)))}'
        f'{_metric("Wide repeats", motif_stats.get("wide_repeated_instances", 0))}'
        '</div>'
        f'<div class="motif-row"><b>Top motifs</b>{motif_html}</div>'
        f'<div class="motif-row"><b>Wide motifs</b>{wide_html}</div>'
    )


def _format_panel(keyword_summary: Dict[str, Any], subcluster_summary: Dict[str, Any]) -> str:
    if not keyword_summary and not subcluster_summary:
        return '<p class="muted">No keyword or subcluster evidence attached.</p>'
    keyword = keyword_summary.get("keyword") or {}
    subformats = keyword_summary.get("subclusters", {}) or {}
    formats = subcluster_summary.get("formats", {}) or {}
    return (
        '<div class="feature-grid">'
        f'{_metric("Keyword offset", keyword.get("offset", "none"), "candidate discriminator")}'
        f'{_metric("Keyword cardinality", keyword.get("cardinality", 0), "observed values")}'
        f'{_metric("Subcluster strategy", subcluster_summary.get("best_strategy", "unknown"))}'
        f'{_metric("Subcluster formats", len(formats), str(len(subformats)) + " keyword formats")}'
        '</div>'
    )


def _family_card(family: Dict[str, Any]) -> str:
    family_id = family.get("family_id", "unknown")
    semantic = family.get("semantic_summary") or {}
    feature = family.get("feature_summary") or {}
    keyword = family.get("keyword_summary") or {}
    subcluster = family.get("subcluster_summary") or {}
    fields = family.get("field_hypotheses", []) or []
    labels = semantic.get("field_labels", []) or []
    role = family.get("role", "unknown")
    role_tone = "request" if role == "request" else "response" if role == "response" else "unknown"
    template = family.get("template", "")
    template_short = template if len(template) <= 180 else template[:180] + " ..."
    related = family.get("related_families", []) or []
    related_html = "".join(_pill(item, "related") for item in related[:8]) or '<span class="muted">No direct relation links</span>'
    return f"""
    <section class="family-card">
      <header>
        <div>
          <h3>{_text(family_id)}</h3>
          <p>{_pill(role, role_tone)} {_text(family.get('message_count', 0))} messages</p>
        </div>
        <div class="confidence">
          <span>Semantic confidence</span>
          {_bar(semantic.get('confidence', 0.0), 'semantic confidence')}
        </div>
      </header>
      {_segment_map(family.get('segments', []) or [])}
      <details open>
        <summary>Template</summary>
        <code class="template">{_text(template_short)}</code>
      </details>
      <div class="card-grid">
        <div>
          <h4>Field Hypotheses</h4>
          <table><thead><tr><th>Bytes</th><th>Type</th><th>Conf.</th></tr></thead><tbody>{_field_rows(fields)}</tbody></table>
        </div>
        <div>
          <h4>Semantic Labels</h4>
          <table><thead><tr><th>Bytes</th><th>Label</th><th>Conf.</th></tr></thead><tbody>{_field_rows(labels)}</tbody></table>
        </div>
      </div>
      <h4>Feature Evidence</h4>
      {_feature_panel(feature)}
      <h4>Format Evidence</h4>
      {_format_panel(keyword, subcluster)}
      <h4>Related Families</h4>
      <div class="pill-row">{related_html}</div>
    </section>
    """


def _relation_rows(model: Dict[str, Any]) -> str:
    rows = []
    for relation in _relations(model):
        rows.append(
            "<tr>"
            f"<td><code>{_text(relation.get('request_family_id'))}</code></td>"
            f"<td><code>{_text(relation.get('response_family_id'))}</code></td>"
            f"<td>{_text(relation.get('pair_count', 0))}</td>"
            f"<td>{_text(relation.get('avg_pair_score', 0.0))}</td>"
            f"<td>{len(relation.get('echo_fields', []) or [])}</td>"
            f"<td>{len(relation.get('length_relations', []) or [])}</td>"
            "</tr>"
        )
    return "".join(rows) or '<tr><td colspan="6">No relation evidence.</td></tr>'


def _evaluation_block(evaluation: Optional[Dict[str, Any]]) -> str:
    if not evaluation:
        return '<section class="panel"><h2>Evaluation</h2><p class="muted">No evaluation report supplied.</p></section>'
    corpus = evaluation.get("corpus", {}) or {}
    clustering = evaluation.get("clustering", {}) or {}
    boundaries = evaluation.get("boundaries", {}) or {}
    pairs = evaluation.get("pairs", {}) or {}
    relations = evaluation.get("relations", {}) or {}
    return f"""
    <section class="panel eval-panel">
      <h2>Pipeline Evaluation</h2>
      <div class="metric-grid">
        {_metric('Messages', corpus.get('message_count', 0), str(corpus.get('session_count', 0)) + ' sessions')}
        {_metric('Corpus assignment coverage', _pct(clustering.get('corpus_assignment_coverage_ratio', clustering.get('assignment_coverage_ratio', 0))), str(clustering.get('family_count', 0)) + ' families')}
        {_metric('Clustering sample', _pct(clustering.get('clustering_sample_ratio', 0)), str(clustering.get('sample_size', 0)) + ' messages')}
        {_metric('Parseable families', _pct(boundaries.get('parseable_family_ratio', 0)), str(boundaries.get('parseable_family_count', 0)) + ' families')}
        {_metric('Pair hypotheses', pairs.get('pair_count', 0), _pct(1 - float(pairs.get('direction_unknown_pair_ratio', 0) or 0)) + ' direction-known')}
        {_metric('Relation edges', relations.get('edge_count', 0), str(relations.get('edges_with_echo_fields', 0)) + ' with echoes')}
      </div>
    </section>
    """


def _llm_analysis_block(llm_analysis: Optional[Dict[str, Any]]) -> str:
    if not llm_analysis:
        return ""
    usage_items = _flatten_usage(llm_analysis.get("usage"))
    usage_metrics = "".join(_metric(key, value) for key, value in usage_items)
    prompt_stats = llm_analysis.get("prompt_stats") if isinstance(llm_analysis.get("prompt_stats"), dict) else {}
    prompt_hint = "not found" if prompt_stats.get("exists") is False else str(prompt_stats.get("path", "prompt"))
    stats_html = (
        '<div class="metric-grid">'
        f'{_metric("Model", llm_analysis.get("model", "unknown"))}'
        f'{_metric("Prompt bytes", prompt_stats.get("bytes", 0), prompt_hint)}'
        f'{_metric("Prompt chars", prompt_stats.get("characters", 0))}'
        f'{_metric("Prompt est. tokens", prompt_stats.get("estimated_tokens", 0))}'
        f'{usage_metrics}'
        '</div>'
    )
    analysis_markdown = llm_analysis.get("analysis_markdown")
    if analysis_markdown:
        body = f"<pre>{_text(str(analysis_markdown).strip())}</pre>"
    elif llm_analysis.get("render_only"):
        body = '<p class="muted">LLM analysis was skipped because stage 15 ran in render-only mode.</p>'
    else:
        body = '<p class="muted">No LLM analysis text is available.</p>'
    return f"""
    <section class="panel llm-panel">
      <h2>LLM Analysis</h2>
      {stats_html}
      {body}
    </section>
    """


def _final_evaluation_block(final_evaluation: Optional[Dict[str, Any]]) -> str:
    if not final_evaluation:
        return ""
    summary = final_evaluation.get("summary", {}) or {}
    metrics = final_evaluation.get("metrics", {}) or {}
    return f"""
    <section class="panel eval-panel">
      <h2>Final Ground Truth Evaluation</h2>
      <div class="metric-grid">
        {_metric('Overall score', summary.get('overall_score', 0.0), str(summary.get('verdict', 'unknown')))}
        {_metric('Matched message types', summary.get('matched_message_type_count', 0), 'of ' + str(summary.get('ground_truth_message_type_count', 0)))}
        {_metric('Message type accuracy', (metrics.get('message_type_matching', {}) or {}).get('accuracy', 0.0))}
        {_metric('Message type F1', (metrics.get('message_type_matching', {}) or {}).get('f1_score', 0.0))}
        {_metric('Field boundary accuracy', (metrics.get('field_boundary', {}) or {}).get('accuracy', 0.0))}
        {_metric('Field boundary F1', (metrics.get('field_boundary', {}) or {}).get('f1_score', 0.0))}
        {_metric('Field semantics accuracy', (metrics.get('field_semantics', {}) or {}).get('accuracy', 0.0))}
        {_metric('Field semantics F1', (metrics.get('field_semantics', {}) or {}).get('f1_score', 0.0))}
        {_metric('Relation accuracy', (metrics.get('relations', {}) or {}).get('accuracy', 0.0))}
        {_metric('Relation F1', (metrics.get('relations', {}) or {}).get('f1_score', 0.0))}
      </div>
    </section>
    """


def render_protocol_model_html(
    model: Dict[str, Any],
    evaluation: Optional[Dict[str, Any]] = None,
    llm_analysis: Optional[Dict[str, Any]] = None,
    final_evaluation: Optional[Dict[str, Any]] = None,
) -> str:
    families = _families(model)
    family_cards = "\n".join(_family_card(family) for family in families)
    metadata_rows = _kv_rows(model.get("metadata", {}) or {})
    relation_rows = _relation_rows(model)
    llm_block = _llm_analysis_block(llm_analysis)
    final_evaluation_block = _final_evaluation_block(final_evaluation)
    total_messages = sum(int(family.get("message_count", 0) or 0) for family in model.get("families", []) or [])
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_text(model.get('protocol_name', 'Unknown Protocol'))} Report</title>
<style>
:root {{
  --bg: #0d1110;
  --panel: #151b19;
  --panel-2: #1d2522;
  --ink: #eef4df;
  --muted: #9eaa9c;
  --line: rgba(238,244,223,.14);
  --accent: #d7ff64;
  --accent-2: #44d7b6;
  --warn: #ffb86b;
  --bad: #ff6b6b;
  --shadow: 0 24px 80px rgba(0,0,0,.38);
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  background:
    radial-gradient(circle at 10% 0%, rgba(215,255,100,.15), transparent 32rem),
    radial-gradient(circle at 90% 10%, rgba(68,215,182,.12), transparent 30rem),
    linear-gradient(135deg, #0d1110 0%, #101513 52%, #080a09 100%);
  color: var(--ink);
  font-family: "Aptos Display", "Trebuchet MS", sans-serif;
}}
code, pre {{ font-family: "Cascadia Code", "Fira Code", monospace; }}
a {{ color: var(--accent); }}
.hero {{ padding: 64px min(6vw, 72px) 32px; }}
.hero-card {{ border: 1px solid var(--line); background: rgba(21,27,25,.78); box-shadow: var(--shadow); border-radius: 30px; padding: clamp(24px, 5vw, 56px); position: relative; overflow: hidden; }}
.hero-card:after {{ content:""; position:absolute; inset:auto -15% -45% 35%; height: 260px; background: linear-gradient(90deg, transparent, rgba(215,255,100,.22), transparent); transform: rotate(-8deg); }}
h1 {{ font-size: clamp(2.4rem, 7vw, 6.2rem); line-height: .9; margin: 0 0 18px; letter-spacing: -.07em; }}
h2 {{ font-size: clamp(1.6rem, 3vw, 2.6rem); margin: 0 0 20px; letter-spacing: -.04em; }}
h3 {{ font-size: 1.35rem; margin: 0 0 6px; }}
h4 {{ margin: 20px 0 10px; color: var(--accent); }}
.subhead {{ max-width: 820px; color: var(--muted); font-size: 1.08rem; }}
.metric-grid, .feature-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 14px; }}
.metric {{ background: linear-gradient(180deg, rgba(255,255,255,.06), rgba(255,255,255,.025)); border: 1px solid var(--line); border-radius: 18px; padding: 16px; }}
.metric strong {{ display:block; font-size: 1.55rem; color: var(--accent); }}
.metric span, .metric small {{ display:block; color: var(--muted); margin-top: 4px; }}
.panel, .family-card {{ margin: 24px min(6vw, 72px); padding: 24px; background: rgba(21,27,25,.82); border: 1px solid var(--line); border-radius: 24px; box-shadow: 0 18px 50px rgba(0,0,0,.22); }}
.meta-table, table {{ width: 100%; border-collapse: collapse; overflow: hidden; border-radius: 14px; }}
th, td {{ text-align:left; border-bottom: 1px solid var(--line); padding: 10px 12px; vertical-align: top; }}
th {{ color: var(--accent-2); font-weight: 700; }}
.family-card header {{ display:flex; justify-content: space-between; gap: 20px; align-items:flex-start; }}
.card-grid {{ display:grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 18px; }}
.pill-row, .motif-row {{ display:flex; flex-wrap: wrap; gap: 8px; align-items:center; margin: 10px 0; }}
.pill {{ display:inline-flex; align-items:center; border:1px solid var(--line); border-radius: 999px; padding: 5px 10px; color: var(--ink); background: rgba(255,255,255,.05); font-size: .86rem; }}
.pill.request {{ background: rgba(68,215,182,.14); color: #9ff5df; }}
.pill.response {{ background: rgba(215,255,100,.13); color: #e8ff99; }}
.pill.unknown {{ background: rgba(255,184,107,.13); color: #ffd1a1; }}
.pill.motif {{ color: #d7ff64; }}
.pill.wide {{ color: #44d7b6; }}
.template {{ display:block; white-space: pre-wrap; word-break: break-word; padding: 14px; background: #0b0f0e; border: 1px solid var(--line); border-radius: 14px; color: #dbe8d2; }}
.llm-panel pre {{ white-space: pre-wrap; word-break: break-word; padding: 18px; background: #0b0f0e; border: 1px solid var(--line); border-radius: 16px; color: #dbe8d2; line-height: 1.5; }}
.segment-map {{ display:flex; height: 18px; width:100%; overflow:hidden; border-radius: 999px; background:#0b0f0e; border:1px solid var(--line); margin: 16px 0; }}
.seg {{ min-width: 3px; border-right: 1px solid rgba(0,0,0,.35); }}
.seg.constant {{ background: var(--accent); }}
.seg.variable {{ background: var(--accent-2); }}
.seg.unknown {{ background: var(--warn); }}
.bar {{ width: 180px; max-width: 100%; height: 8px; border-radius: 999px; background: rgba(255,255,255,.12); overflow:hidden; margin-top: 8px; }}
.bar span {{ display:block; height:100%; background: linear-gradient(90deg, var(--accent-2), var(--accent)); }}
.confidence span, .muted {{ color: var(--muted); }}
details {{ margin: 14px 0; }}
summary {{ cursor:pointer; color: var(--accent-2); font-weight: 700; }}
.footer {{ padding: 28px min(6vw, 72px) 56px; color: var(--muted); }}
@media (max-width: 760px) {{ .family-card header {{ flex-direction: column; }} .panel, .family-card {{ margin-inline: 14px; padding: 18px; }} .hero {{ padding-inline: 14px; }} table {{ font-size: .86rem; }} }}
</style>
</head>
<body>
  <header class="hero">
    <div class="hero-card">
      <h1>{_text(model.get('protocol_name', 'unknown-industrial-protocol'))}</h1>
      <p class="subhead">Auto-generated reverse-engineering report for an unknown industrial protocol. Evidence is inferred from payload families, structural features, request/response links, and semantic hints.</p>
      <div class="metric-grid">
        {_metric('Families', len(model.get('families', []) or []), 'message types')}
        {_metric('Messages represented', total_messages, 'assigned family messages')}
        {_metric('Relations', len(model.get('relations', []) or []), 'family-to-family edges')}
        {_metric('Version', model.get('version', '0.1'))}
      </div>
    </div>
  </header>
  {_evaluation_block(evaluation)}
  {final_evaluation_block}
  {llm_block}
  <section class="panel">
    <h2>Metadata</h2>
    <table class="meta-table"><tbody>{metadata_rows or '<tr><td>No metadata.</td></tr>'}</tbody></table>
  </section>
  <section class="panel">
    <h2>Strongest Relations</h2>
    <table><thead><tr><th>Request</th><th>Response</th><th>Pairs</th><th>Score</th><th>Echoes</th><th>Length Rules</th></tr></thead><tbody>{relation_rows}</tbody></table>
  </section>
  <main>
    <section class="panel"><h2>Families</h2><p class="muted">Showing {len(families)} largest families.</p></section>
    {family_cards}
  </main>
  <footer class="footer">Generated by Protocol RE. Raw payloads are omitted from this report.</footer>
</body>
</html>
"""
