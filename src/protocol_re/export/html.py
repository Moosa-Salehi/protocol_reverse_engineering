from __future__ import annotations

import math
from html import escape
from typing import Any, Dict, Iterable, List, Optional, Tuple


def _families(model: Dict[str, Any], limit: int = 40) -> List[Dict[str, Any]]:
    return sorted(
        model.get("families", []) or [],
        key=lambda item: (-int(item.get("message_count", 0) or 0), str(item.get("family_id", ""))),
    )[:limit]


def _relations(model: Dict[str, Any], limit: int = 20) -> List[Dict[str, Any]]:
    return sorted(
        model.get("relations", []) or [],
        key=lambda item: (
            -int(item.get("pair_count", 0) or 0),
            -float(item.get("support_ratio", 0.0) or 0.0),
            -float(item.get("edge_lift", 0.0) or 0.0),
            -float(item.get("avg_pair_score", 0.0) or 0.0),
        ),
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


def _metric(label: str, value: Any, hint: str = "", tip: str = "") -> str:
    hint_html = f'<small>{_text(hint)}</small>' if hint else ""
    tip_attr = f' data-tip="{escape(str(tip))}"' if tip else ""
    info = '<i class="tip-dot">i</i>' if tip else ""
    return (
        f'<article class="metric"{tip_attr}><strong>{_text(value)}{info}</strong>'
        f'<span>{_text(label)}</span>{hint_html}</article>'
    )


# ---------------------------------------------------------------------------
# Visualization helpers (hand-rolled inline SVG + CSS, no JS dependencies)
# ---------------------------------------------------------------------------

# Stable, colour-blind-friendly palette reused across every chart so that the
# same family keeps the same colour in the bar chart, donut, treemap and graph.
_PALETTE = [
    "#d7ff64", "#44d7b6", "#7aa2ff", "#ff9f6b", "#ff6bd6",
    "#b388ff", "#5ad1ff", "#ffd166", "#9bff8f", "#ff8f8f",
    "#8ed0c4", "#c0a0ff", "#ffc08a", "#8ab4ff", "#e0ff9b",
]


def _color_for(index: int) -> str:
    return _PALETTE[index % len(_PALETTE)]


def _role_tone(role: str) -> str:
    return "request" if role == "request" else "response" if role == "response" else "unknown"


def _role_color(role: str) -> str:
    return {"request": "#44d7b6", "response": "#d7ff64"}.get(role, "#ffb86b")


def _tip(content: str) -> str:
    """Inline info dot carrying a hover tooltip (CSS-only)."""
    if not content:
        return ""
    return f'<i class="tip-dot" data-tip="{escape(str(content))}">i</i>'


def _num(value: Any, digits: int = 2) -> str:
    try:
        number = float(value)
    except Exception:
        return _text(value)
    if number == int(number):
        return str(int(number))
    return f"{number:.{digits}f}"


def _svg_bar_chart(rows: List[Tuple[str, float, str, str]], unit: str = "") -> str:
    """Horizontal bar chart. rows = [(label, value, color, tooltip), ...]."""
    rows = [r for r in rows if r is not None]
    if not rows:
        return '<p class="muted">No data.</p>'
    peak = max((r[1] for r in rows), default=0.0) or 1.0
    bars = []
    for label, value, color, tip in rows:
        width = max(1.5, (float(value) / peak) * 100.0)
        bars.append(
            '<div class="hbar-row"'
            + (f' data-tip="{escape(str(tip))}"' if tip else "")
            + ">"
            f'<span class="hbar-label">{_text(label)}</span>'
            '<span class="hbar-track">'
            f'<span class="hbar-fill" style="width:{width:.1f}%;background:{color}"></span>'
            "</span>"
            f'<span class="hbar-value">{_text(_num(value))}{_text(unit)}</span>'
            "</div>"
        )
    return f'<div class="hbar-chart">{"".join(bars)}</div>'


def _svg_donut(slices: List[Tuple[str, float, str]], center_label: str = "", center_value: str = "") -> str:
    """Donut chart. slices = [(label, value, color), ...]."""
    slices = [s for s in slices if s and float(s[1]) > 0]
    total = sum(float(s[1]) for s in slices) or 1.0
    radius, stroke = 52.0, 22.0
    circumference = 2 * math.pi * radius
    offset = 0.0
    arcs = []
    legend = []
    for label, value, color in slices:
        fraction = float(value) / total
        dash = fraction * circumference
        arcs.append(
            f'<circle r="{radius}" cx="70" cy="70" fill="none" stroke="{color}" '
            f'stroke-width="{stroke}" stroke-dasharray="{dash:.2f} {circumference - dash:.2f}" '
            f'stroke-dashoffset="{-offset:.2f}" transform="rotate(-90 70 70)">'
            f'<title>{escape(label)}: {_num(value)} ({fraction*100:.1f}%)</title></circle>'
        )
        offset += dash
        legend.append(
            f'<li><span class="swatch" style="background:{color}"></span>'
            f'{_text(label)} <b>{_text(_num(value))}</b> '
            f'<span class="muted">{fraction*100:.0f}%</span></li>'
        )
    center = ""
    if center_value or center_label:
        center = (
            f'<text x="70" y="66" text-anchor="middle" class="donut-num">{_text(center_value)}</text>'
            f'<text x="70" y="86" text-anchor="middle" class="donut-cap">{_text(center_label)}</text>'
        )
    return (
        '<div class="donut-wrap">'
        f'<svg viewBox="0 0 140 140" class="donut" role="img">{"".join(arcs)}{center}</svg>'
        f'<ul class="donut-legend">{"".join(legend)}</ul>'
        "</div>"
    )


def _squarified_treemap(items: List[Tuple[str, float, str, str]], width: float = 100.0, height: float = 100.0) -> str:
    """Squarified treemap layout. items = [(label, value, color, tooltip), ...].

    Returns positioned <div> tiles inside a relative container (percentage units).
    """
    items = [i for i in items if i and float(i[1]) > 0]
    if not items:
        return '<p class="muted">No data.</p>'
    items = sorted(items, key=lambda i: -float(i[1]))
    total = sum(float(i[1]) for i in items)
    scale = (width * height) / total
    areas = [(label, float(value) * scale, color, tip) for label, value, color, tip in items]

    tiles: List[Tuple[str, float, str, str, float, float, float, float]] = []
    x, y, w, h = 0.0, 0.0, width, height

    def worst(row: List[float], length: float) -> float:
        if not row or length == 0:
            return math.inf
        s = sum(row)
        side = s / length
        rmax = max(row)
        rmin = min(row)
        return max((side * side) / (rmin or 1e-9), rmax / (side * side or 1e-9)) if side else math.inf

    def layout_row(row_items, x, y, w, h, horizontal):
        s = sum(a[1] for a in row_items)
        if horizontal:
            row_h = s / (w or 1e-9)
            cx = x
            for label, area, color, tip in row_items:
                tw = area / (row_h or 1e-9)
                tiles.append((label, area, color, tip, cx, y, tw, row_h))
                cx += tw
            return x, y + row_h, w, h - row_h
        else:
            row_w = s / (h or 1e-9)
            cy = y
            for label, area, color, tip in row_items:
                th = area / (row_w or 1e-9)
                tiles.append((label, area, color, tip, x, cy, row_w, th))
                cy += th
            return x + row_w, y, w - row_w, h

    i = 0
    n = len(areas)
    row: List = []
    while i < n:
        horizontal = w >= h
        length = w if horizontal else h
        current = [a[1] for a in row]
        nxt = areas[i]
        if not row or worst(current + [nxt[1]], length) <= worst(current, length):
            row.append(nxt)
            i += 1
        else:
            x, y, w, h = layout_row(row, x, y, w, h, horizontal)
            row = []
    if row:
        layout_row(row, x, y, w, h, w >= h)

    cells = []
    for label, area, color, tip, tx, ty, tw, th in tiles:
        big = tw > 9 and th > 7
        text = f'<span class="tm-label">{_text(label)}</span>' if big else ""
        cells.append(
            f'<div class="tm-cell" style="left:{tx:.2f}%;top:{ty:.2f}%;width:{tw:.2f}%;height:{th:.2f}%;'
            f'background:{color}"'
            + (f' data-tip="{escape(str(tip))}"' if tip else "")
            + f">{text}</div>"
        )
    return f'<div class="treemap">{"".join(cells)}</div>'


def _gauge(value: Any, label: str, tip: str = "") -> str:
    """Small radial gauge for a 0..1 score."""
    try:
        frac = max(0.0, min(1.0, float(value)))
    except Exception:
        frac = 0.0
    radius = 30.0
    circumference = 2 * math.pi * radius
    dash = frac * circumference
    hue = 120 * frac  # red -> green
    color = f"hsl({hue:.0f} 72% 58%)"
    tip_attr = f' data-tip="{escape(str(tip))}"' if tip else ""
    return (
        f'<div class="gauge"{tip_attr}>'
        '<svg viewBox="0 0 76 76">'
        f'<circle cx="38" cy="38" r="{radius}" fill="none" stroke="rgba(255,255,255,.1)" stroke-width="8"/>'
        f'<circle cx="38" cy="38" r="{radius}" fill="none" stroke="{color}" stroke-width="8" '
        f'stroke-linecap="round" stroke-dasharray="{dash:.2f} {circumference - dash:.2f}" '
        'transform="rotate(-90 38 38)"/>'
        f'<text x="38" y="43" text-anchor="middle" class="gauge-num">{frac*100:.0f}</text>'
        "</svg>"
        f'<span class="gauge-label">{_text(label)}{_tip(tip)}</span>'
        "</div>"
    )


def _short_text(value: Any, limit: int = 12000) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if len(text) <= limit:
        return text
    return text[:limit] + f"\n\n... truncated {len(text) - limit} characters ..."


def _text_pre(value: Any, empty: str = "No text available.") -> str:
    text = _short_text(value)
    if not text:
        return f'<p class="muted">{_text(empty)}</p>'
    return f"<pre>{_text(text)}</pre>"


def _json_pre(value: Any, empty: str = "No result details available.") -> str:
    if value in (None, "", [], {}):
        return f'<p class="muted">{_text(empty)}</p>'
    try:
        import json

        text = json.dumps(value, indent=2, ensure_ascii=False)
    except Exception:
        text = str(value)
    return _text_pre(text, empty=empty)


def _stage_status_metrics(result: Optional[Dict[str, Any]], stage_label: str) -> str:
    result = result or {}
    success = result.get("success")
    status = "unknown" if success is None else "success" if success else "failed"
    applied = result.get("applied_count", result.get("kept_count", result.get("applied", 0)))
    rejected = result.get("rejected_count", result.get("discarded_count", result.get("rejected", 0)))
    metrics = (
        f'{_metric("Stage", stage_label)}'
        f'{_metric("Status", status)}'
        f'{_metric("Applied/kept", applied)}'
        f'{_metric("Rejected/discarded", rejected)}'
    )
    if result.get("error"):
        metrics += _metric("Error", result.get("error"), str(result.get("error_category", "")))
    return f'<div class="metric-grid">{metrics}</div>'


def _stage_text_details(stage: Optional[Dict[str, Any]], title: str, stage_label: str) -> str:
    if not stage:
        return f'<section class="llm-stage-block"><h4>{_text(title)}</h4><p class="muted">No LLM stage artifact found.</p></section>'
    result = stage.get("result") if isinstance(stage.get("result"), dict) else {}
    if stage_label == "boundary_refinement":
        details = _boundary_stage_table(result)
    elif stage_label == "semantic_labeling":
        details = _semantic_stage_table(result)
    elif stage_label == "relation_validation":
        details = _relation_stage_table(result)
    else:
        details = _generic_stage_summary(result)
    return f"""
    <section class="llm-stage-block">
      <h4>{_text(title)}</h4>
      {_stage_status_metrics(result, stage_label)}
      {details}
    </section>
    """


def _list_text(items: Any, limit: int = 3) -> str:
    if not items:
        return ""
    if not isinstance(items, list):
        return str(items)
    shown = [str(item) for item in items[:limit]]
    suffix = f" +{len(items) - limit} more" if len(items) > limit else ""
    return "; ".join(shown) + suffix


def _compact_json(value: Any, limit: int = 180) -> str:
    if value in (None, "", [], {}):
        return ""
    try:
        import json

        text = json.dumps(value, ensure_ascii=False, sort_keys=True)
    except Exception:
        text = str(value)
    return text if len(text) <= limit else text[:limit] + "..."


def _generic_stage_summary(result: Dict[str, Any]) -> str:
    rows = []
    for key in ("result_path", "error", "error_category"):
        if result.get(key):
            rows.append(f"<tr><th>{_text(key)}</th><td>{_text(result.get(key))}</td></tr>")
    return f'<table class="llm-detail-table"><tbody>{"".join(rows) or "<tr><td>No additional details.</td></tr>"}</tbody></table>'


def _boundary_stage_table(result: Dict[str, Any]) -> str:
    rows = []
    for entry in result.get("validation_log", []) or []:
        suggestion = entry.get("suggestion") or {}
        merged = suggestion.get("merged_field") or {}
        fields = suggestion.get("fields_to_merge", [])
        span = ""
        if merged:
            span = f"{merged.get('start_offset', merged.get('start', ''))}..{merged.get('end_offset', merged.get('end', ''))}"
        rows.append(
            "<tr>"
            f"<td>{_pill('applied' if entry.get('applied') else 'rejected', 'related' if entry.get('applied') else 'unknown')}</td>"
            f"<td>{_text(_list_text(fields, limit=8))}</td>"
            f"<td><code>{_text(span)}</code></td>"
            f"<td>{_text(suggestion.get('confidence', ''))}</td>"
            f"<td>{_text(suggestion.get('rationale') or entry.get('reason') or '')}</td>"
            "</tr>"
        )
    if not rows:
        rows.append('<tr><td colspan="5">No boundary merge suggestions.</td></tr>')
    return (
        '<table class="llm-detail-table"><thead><tr>'
        '<th>Status</th><th>Fields</th><th>Merged Span</th><th>Conf.</th><th>Reason</th>'
        f'</tr></thead><tbody>{"".join(rows)}</tbody></table>'
    )


def _semantic_stage_table(result: Dict[str, Any]) -> str:
    rows = []
    for entry in result.get("validation_log", []) or []:
        label = entry.get("label") or {}
        width = label.get("width", label.get("length", ""))
        byte_range = f"{label.get('offset', label.get('start', ''))}+{width}"
        role = label.get("semantic_role") or label.get("label") or "unknown"
        field_type = label.get("encoding_type") or label.get("field_type") or ""
        evidence = _list_text(label.get("evidence", []))
        rows.append(
            "<tr>"
            f"<td>{_pill('applied' if entry.get('applied') else 'rejected', 'related' if entry.get('applied') else 'unknown')}</td>"
            f"<td>{_text(label.get('field_index', ''))}</td>"
            f"<td><code>{_text(byte_range)}</code></td>"
            f"<td>{_text(role)}</td>"
            f"<td>{_text(field_type)}</td>"
            f"<td>{_text(label.get('confidence', ''))}</td>"
            f"<td>{_text(evidence or entry.get('reason') or '')}</td>"
            "</tr>"
        )
    if not rows:
        rows.append('<tr><td colspan="7">No semantic label suggestions.</td></tr>')
    return (
        '<table class="llm-detail-table"><thead><tr>'
        '<th>Status</th><th>Field</th><th>Bytes</th><th>Role</th><th>Type</th><th>Conf.</th><th>Evidence</th>'
        f'</tr></thead><tbody>{"".join(rows)}</tbody></table>'
    )


def _relation_stage_table(result: Dict[str, Any]) -> str:
    rows = []
    for entry in result.get("validation_log", []) or []:
        decision = entry.get("decision") or {}
        rows.append(
            "<tr>"
            f"<td><code>{_text(decision.get('request_family_id', ''))}</code></td>"
            f"<td><code>{_text(decision.get('response_family_id', ''))}</code></td>"
            f"<td>{_pill(decision.get('decision', 'unknown'), 'related' if decision.get('decision') == 'keep' else 'unknown')}</td>"
            f"<td>{_text(decision.get('confidence', ''))}</td>"
            f"<td>{_text('yes' if entry.get('applied') else 'no')}</td>"
            f"<td>{_text(decision.get('rationale') or entry.get('reason') or '')}</td>"
            "</tr>"
        )
    if not rows:
        rows.append('<tr><td colspan="6">No relation validation decisions.</td></tr>')
    return (
        '<table class="llm-detail-table"><thead><tr>'
        '<th>Request</th><th>Response</th><th>Decision</th><th>Conf.</th><th>Applied</th><th>Reason</th>'
        f'</tr></thead><tbody>{"".join(rows)}</tbody></table>'
    )


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


def _segment_map(
    segments: List[Dict[str, Any]],
    max_width: int = 80,
    labels: Optional[List[Dict[str, Any]]] = None,
) -> str:
    if not segments:
        return '<div class="segment-map empty">No segments</div>'
    total = max(int(segment.get("end", 0) or 0) for segment in segments) or 1
    # Build an offset -> semantic label index so each byte span can be named.
    label_at: Dict[int, Dict[str, Any]] = {}
    for lab in labels or []:
        try:
            label_at[int(lab.get("start", -1))] = lab
        except Exception:
            continue
    parts = []
    for segment in segments[:max_width]:
        start = int(segment.get("start", 0) or 0)
        end = int(segment.get("end", start) or start)
        width = max(2.5, ((end - start) / total) * 100.0)
        kind = str(segment.get("kind", "unknown"))
        lab = label_at.get(start)
        name = ""
        if lab:
            name = str(lab.get("label") or lab.get("field_type") or "")
        conf = segment.get("confidence")
        tip = f"bytes {start}..{end - 1} · {kind}"
        if name:
            tip = f"{name} · {tip}"
        if conf is not None:
            tip += f" · conf {_num(conf)}"
        inner = f'<b>{_text(name)}</b>' if (name and width > 8) else ""
        parts.append(
            f'<span class="seg {escape(kind)}" style="width:{width:.2f}%" '
            f'data-tip="{escape(tip)}" title="{escape(tip)}">{inner}'
            f'<i class="seg-off">{start}</i></span>'
        )
    ruler = (
        '<div class="byte-ruler"><span>byte 0</span>'
        f'<span class="muted">{total} bytes (template span)</span></div>'
    )
    legend = (
        '<div class="seg-legend">'
        '<span><i class="sw constant"></i>constant</span>'
        '<span><i class="sw variable"></i>variable</span>'
        '<span><i class="sw unknown"></i>unknown</span>'
        "</div>"
    )
    return f'<div class="segment-wrap">{ruler}<div class="segment-map">{"".join(parts)}</div>{legend}</div>'


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


def _format_panel(keyword_summary: Dict[str, Any]) -> str:
    if not keyword_summary:
        return '<p class="muted">No discriminator evidence attached.</p>'
    candidate = keyword_summary.get("keyword") or {}
    candidates = keyword_summary.get("discriminator_candidates", []) or keyword_summary.get("opcode_candidates", []) or []
    salience = candidate.get("salience_score", 0.0) if candidate else 0.0
    mutual_information = candidate.get("mutual_information", 0.0) if candidate else 0.0
    contrastive = candidate.get("contrastive_separation", 0.0) if candidate else 0.0
    candidate_html = "".join(
        _pill(
            f"{int(item.get('start', item.get('offset', 0)))} conf={item.get('confidence', 0.0)} sal={item.get('salience_score', 0.0)}",
            "field",
        )
        for item in candidates[:5]
    ) or '<span class="muted">No candidates</span>'
    return (
        '<div class="feature-grid">'
        f'{_metric("Discriminator offset", candidate.get("offset", "none"), "opcode/message-type candidate")}'
        f'{_metric("Cardinality", candidate.get("cardinality", 0), "observed values")}'
        f'{_metric("Salience", salience, "learned offset score")}'
        f'{_metric("Mutual info", mutual_information, "family separation")}'
        f'{_metric("Contrast", contrastive, "value/family purity")}'
        '</div>'
        f'<div class="motif-row"><b>Top discriminator candidates</b>{candidate_html}</div>'
    )


def _framing_panel(framing_summary: Dict[str, Any]) -> str:
    layouts = framing_summary.get("layout_hypotheses", []) if framing_summary else []
    if not layouts:
        return '<p class="muted">No framing hypotheses attached.</p>'
    best = layouts[0]
    fields = best.get("field_regions", []) or []
    field_html = "".join(
        _pill(f"{field.get('start')}..{int(field.get('end', 0) or 0) - 1} {field.get('field_type')}", "field")
        for field in fields[:6]
    ) or '<span class="muted">No header fields</span>'
    return (
        '<div class="feature-grid">'
        f'{_metric("Header end", best.get("header_end", 0), "body starts " + str(best.get("body_start", 0)))}'
        f'{_metric("Framing confidence", best.get("confidence", 0.0))}'
        f'{_metric("Hypotheses", len(layouts))}'
        '</div>'
        f'<div class="motif-row"><b>Header fields</b>{field_html}</div>'
    )


def _family_refinement_blocks(family_id: str, llm_stage_results: Optional[Dict[str, Any]]) -> str:
    if not llm_stage_results:
        return ""
    boundary = (llm_stage_results.get("boundary_refinement") or {}).get(family_id)
    semantic = (llm_stage_results.get("semantic_labeling") or {}).get(family_id)
    if not boundary and not semantic:
        return ""
    return (
        '<h4>LLM Boundary Refinement</h4>'
        f'{_stage_text_details(boundary, "Boundary Detection Refinement", "boundary_refinement")}'
        '<h4>LLM Semantic Refinement</h4>'
        f'{_stage_text_details(semantic, "Semantic Labeling Refinement", "semantic_labeling")}'
    )


def _family_card(family: Dict[str, Any], llm_stage_results: Optional[Dict[str, Any]] = None) -> str:
    family_id = family.get("family_id", "unknown")
    semantic = family.get("semantic_summary") or {}
    feature = family.get("feature_summary") or {}
    keyword = family.get("keyword_summary") or {}
    framing = family.get("framing_summary") or {}
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
      {_segment_map(family.get('segments', []) or [], labels=labels)}
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
      <h4>Discriminator Evidence</h4>
      {_format_panel(keyword)}
      <h4>Framing Evidence</h4>
      {_framing_panel(framing)}
      {_family_refinement_blocks(str(family_id), llm_stage_results)}
      <h4>Related Families</h4>
      <div class="pill-row">{related_html}</div>
    </section>
    """


def _relation_llm_decision(relation: Dict[str, Any], relation_stage: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not relation_stage:
        return None
    result = relation_stage.get("result") if isinstance(relation_stage.get("result"), dict) else {}
    req = relation.get("request_family_id")
    resp = relation.get("response_family_id")
    for entry in result.get("validation_log", []) or []:
        decision = entry.get("decision") or {}
        if decision.get("request_family_id") == req and decision.get("response_family_id") == resp:
            return {
                "decision": decision.get("decision"),
                "confidence": decision.get("confidence"),
                "rationale": decision.get("rationale"),
                "valid": entry.get("valid"),
                "applied": entry.get("applied"),
                "reason": entry.get("reason"),
            }
    return None


def _relation_rows(model: Dict[str, Any], llm_stage_results: Optional[Dict[str, Any]] = None) -> str:
    rows = []
    relation_stage = (llm_stage_results or {}).get("relation_validation")
    for relation in _relations(model):
        llm_decision = _relation_llm_decision(relation, relation_stage)
        llm_html = '<span class="muted">No decision</span>'
        if llm_decision:
            llm_html = (
                f"{_pill(llm_decision.get('decision', 'unknown'), 'related')} "
                f"{_text(llm_decision.get('confidence', ''))}"
                f"<br><small>{_text(llm_decision.get('rationale') or llm_decision.get('reason') or '')}</small>"
            )
        elif relation.get("llm_rationale"):
            llm_html = (
                f"{_pill('model-attached', 'related')} {_text(relation.get('llm_confidence', ''))}"
                f"<br><small>{_text(relation.get('llm_rationale'))}</small>"
            )
        rows.append(
            "<tr>"
            f"<td><code>{_text(relation.get('request_family_id'))}</code></td>"
            f"<td><code>{_text(relation.get('response_family_id'))}</code></td>"
            f"<td>{_text(relation.get('pair_count', 0))}</td>"
            f"<td>{_text(relation.get('avg_pair_score', 0.0))}</td>"
            f"<td>{_text(relation.get('support_ratio', 0.0))}</td>"
            f"<td>{_text(relation.get('edge_lift', 0.0))}</td>"
            f"<td>{_text(relation.get('direction_consistency', 0.0))}</td>"
            f"<td>{_text(relation.get('temporal_order_consistency', 0.0))}</td>"
            f"<td>{_text(relation.get('dominant_direction', 'unknown'))}</td>"
            f"<td>{len(relation.get('echo_fields', []) or [])}</td>"
            f"<td>{len(relation.get('length_relations', []) or [])}</td>"
            f"<td>{llm_html}</td>"
            "</tr>"
        )
    return "".join(rows) or '<tr><td colspan="12">No relation evidence.</td></tr>'


def _evaluation_block(evaluation: Optional[Dict[str, Any]]) -> str:
    if not evaluation:
        return '<section class="panel"><h2>Evaluation</h2><p class="muted">No evaluation report supplied.</p></section>'
    corpus = evaluation.get("corpus", {}) or {}
    clustering = evaluation.get("clustering", {}) or {}
    boundaries = evaluation.get("boundaries", {}) or {}
    pairs = evaluation.get("pairs", {}) or {}
    relations = evaluation.get("relations", {}) or {}
    diagnostics = evaluation.get("diagnostics", {}) or {}
    diagnostic_summary = diagnostics.get("summary", {}) or {}
    warning_rows = "".join(
        "<tr>"
        f"<td><code>{_text(item.get('family_id'))}</code></td>"
        f"<td>{_text(item.get('message_count', 0))}</td>"
        f"<td>{_text(item.get('split_suspicion', 0.0))}</td>"
        f"<td>{_text(item.get('over_split_score', 0.0))}</td>"
        f"<td>{_text(', '.join(item.get('diagnostic_warnings', []) or []))}</td>"
        "</tr>"
        for item in (diagnostic_summary.get("top_warning_families", []) or [])[:10]
    )
    diagnostics_html = ""
    if diagnostic_summary:
        diagnostics_html = (
            '<h3>Clustering Diagnostics</h3>'
            '<div class="metric-grid">'
            f'{_metric("Warning families", diagnostic_summary.get("warning_family_count", 0))}'
            f'{_metric("Split candidates", diagnostic_summary.get("split_candidate_count", 0))}'
            f'{_metric("Merge candidates", diagnostic_summary.get("merge_candidate_count", 0))}'
            '</div>'
            '<table><thead><tr><th>Family</th><th>Messages</th><th>Split</th><th>Over-split</th><th>Warnings</th></tr></thead>'
            f'<tbody>{warning_rows or "<tr><td colspan=\"5\">No family warnings.</td></tr>"}</tbody></table>'
        )
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
      {diagnostics_html}
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
        # f'{_metric("Prompt bytes", prompt_stats.get("bytes", 0), prompt_hint)}'
        f'{_metric("Prompt chars", prompt_stats.get("characters", 0))}'
        f'{_metric("Prompt est. tokens", prompt_stats.get("estimated_tokens", 0))}'
        f'{usage_metrics}'
        '</div>'
    )
    analysis_markdown = llm_analysis.get("markdown_summary") or llm_analysis.get("analysis_markdown")
    if analysis_markdown:
        body = f"<pre>{_text(str(analysis_markdown).strip())}</pre>"
    elif llm_analysis.get("render_only"):
        body = '<p class="muted">LLM analysis was skipped because stage 15 ran in render-only mode.</p>'
    elif llm_analysis.get("error"):
        body = f'<p class="muted">LLM analysis was unavailable: {_text(str(llm_analysis.get("error")))}.</p>'
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


def _framing_summary_block(summary: Optional[Dict[str, Any]]) -> str:
    if not summary:
        return ""
    header_ends = summary.get("common_header_ends", []) or []
    field_type_counts = summary.get("field_type_counts", {}) or {}
    top_metrics = (
        f'{_metric("Mean best confidence", summary.get("mean_best_confidence", 0.0))}'
        f'{_metric("Families with header candidate", summary.get("families_with_header_candidate", 0))}'
    )
    header_cards = "".join(
        _metric(
            f"Header end {item.get('header_end', 0)}",
            f"{item.get('family_count', 0)} families",
            _pct(item.get('family_ratio', 0)) + " of families",
        )
        for item in header_ends
    ) or '<p class="muted">No common header ends.</p>'
    field_pills = "".join(
        _pill(f"{key} x{value}", "field") for key, value in field_type_counts.items()
    ) or '<span class="muted">None</span>'
    return f"""
    <section class="panel">
      <h2>Framing Summary</h2>
      <div class="metric-grid">{top_metrics}</div>
      <h4>Common Header Ends</h4>
      <div class="metric-grid">{header_cards}</div>
      <h4>Field Type Counts</h4>
      <div class="motif-row">{field_pills}</div>
    </section>
    """


def _llm_refinement_block(summary: Optional[Dict[str, Any]]) -> str:
    if not summary:
        return ""
    metrics = (
        f'{_metric("Input patches", summary.get("input_patch_count", 0))}'
        f'{_metric("Accepted patches", summary.get("accepted_patch_count", 0))}'
        f'{_metric("Rejected patches", summary.get("rejected_patch_count", 0))}'
    )
    created = summary.get("created_at")
    caption = " · ".join(
        part for part in (summary.get("artifact_type"), created) if part
    )
    caption_html = f'<p class="muted">{_text(caption)}</p>' if caption else ""
    patch_table = _patch_validation_table(summary)
    return f"""
    <section class="panel">
      <h2>LLM Refinement</h2>
      <div class="metric-grid">{metrics}</div>
      {caption_html}
      {patch_table}
    </section>
    """


def _patch_validation_table(summary: Dict[str, Any]) -> str:
    results = summary.get("results", []) or []
    if not results:
        return '<p class="muted">No patch-level validation details supplied.</p>'
    rows = []
    for item in results:
        patch = item.get("patch") or {}
        accepted = bool(item.get("accepted"))
        rows.append(
            "<tr>"
            f"<td>{_pill('applied' if accepted else 'rejected', 'related' if accepted else 'unknown')}</td>"
            f"<td>{_text(patch.get('op', ''))}</td>"
            f"<td><code>{_text(patch.get('path', ''))}</code></td>"
            f"<td>{_text(_compact_json(patch.get('value'), limit=140))}</td>"
            f"<td>{_text(patch.get('rationale') or '')}</td>"
            f"<td>{_text(_list_text(item.get('evidence_support', []) or [], limit=4))}</td>"
            f"<td>{_text(_list_text(item.get('reasons', []) or [], limit=3))}</td>"
            "</tr>"
        )
    return (
        '<h4>Patch Decisions</h4>'
        '<table class="llm-detail-table patch-table"><thead><tr>'
        '<th>Status</th><th>Op</th><th>Path</th><th>Value</th><th>Rationale</th><th>Evidence</th><th>Rejection Reason</th>'
        f'</tr></thead><tbody>{"".join(rows)}</tbody></table>'
    )


def _overview_block(model: Dict[str, Any]) -> str:
    families = sorted(
        model.get("families", []) or [],
        key=lambda f: -int(f.get("message_count", 0) or 0),
    )
    if not families:
        return ""
    color_index = {f.get("family_id"): _color_for(i) for i, f in enumerate(families)}

    bar_rows = [
        (
            str(f.get("family_id")),
            float(f.get("message_count", 0) or 0),
            color_index[f.get("family_id")],
            f"{f.get('family_id')} · {_role_tone(f.get('role', 'unknown'))} · "
            f"{int(f.get('message_count', 0) or 0):,} messages",
        )
        for f in families
    ]

    role_totals: Dict[str, float] = {}
    for f in families:
        role = _role_tone(f.get("role", "unknown"))
        role_totals[role] = role_totals.get(role, 0.0) + float(f.get("message_count", 0) or 0)
    role_slices = [
        (role.capitalize(), role_totals.get(role, 0.0), _role_color(role))
        for role in ("request", "response", "unknown")
        if role_totals.get(role, 0.0) > 0
    ]
    total_msgs = sum(role_totals.values())

    tree_items = [
        (
            str(f.get("family_id")),
            float(f.get("message_count", 0) or 0),
            color_index[f.get("family_id")],
            f"{f.get('family_id')}: {int(f.get('message_count', 0) or 0):,} messages "
            f"({_role_tone(f.get('role', 'unknown'))})",
        )
        for f in families
    ]

    return f"""
    <section class="panel">
      <h2>Family Overview</h2>
      <div class="viz-grid">
        <div class="viz-card">
          <h4>Messages per family {_tip('How many corpus messages were assigned to each discovered family. Larger families are usually the core request/response types of the protocol.')}</h4>
          {_svg_bar_chart(bar_rows, unit=" msgs")}
        </div>
        <div class="viz-card">
          <h4>Role distribution {_tip('Share of messages classified as request vs response vs unknown direction.')}</h4>
          {_svg_donut(role_slices, center_label="messages", center_value=f"{int(total_msgs):,}")}
        </div>
      </div>
      <h4>Proportional map {_tip('Treemap: each tile area is proportional to the message count of that family. A quick sense of how traffic concentrates across message types.')}</h4>
      {_squarified_treemap(tree_items)}
    </section>
    """


def _truth_comparison_block(
    model: Dict[str, Any],
    final_evaluation: Optional[Dict[str, Any]],
) -> str:
    if not final_evaluation:
        return ""
    matches = final_evaluation.get("matches", {}) or {}
    metrics = final_evaluation.get("metrics", {}) or {}
    summary = final_evaluation.get("summary", {}) or {}
    mt_matches = matches.get("message_types", []) or []
    field_matches = matches.get("fields", []) or []
    if not mt_matches and not metrics:
        return ""

    # Per-family message-count lookup for richer tooltips.
    msg_by_family = {
        str(f.get("family_id")): int(f.get("message_count", 0) or 0)
        for f in model.get("families", []) or []
    }
    # Aggregate field match quality per (family -> gt type).
    field_stats: Dict[Tuple[str, str], Dict[str, float]] = {}
    for fm in field_matches:
        pred = fm.get("predicted", {}) or {}
        gt = fm.get("ground_truth", {}) or {}
        key = (str(pred.get("owner_id")), str(gt.get("owner_id")))
        bucket = field_stats.setdefault(key, {"n": 0, "boundary": 0.0, "semantic": 0.0})
        bucket["n"] += 1
        bucket["boundary"] += float(fm.get("boundary_score", 0.0) or 0.0)
        bucket["semantic"] += float(fm.get("semantic_score", 0.0) or 0.0)

    rows = []
    for m in sorted(mt_matches, key=lambda x: str(x.get("predicted_family_id"))):
        fam = str(m.get("predicted_family_id"))
        gt = str(m.get("ground_truth_message_type_id"))
        score = float(m.get("score", 0.0) or 0.0)
        fkey = (fam, gt)
        fstat = field_stats.get(fkey)
        if fstat and fstat["n"]:
            field_cell = (
                f'{int(fstat["n"])} fields · '
                f'b={fstat["boundary"]/fstat["n"]:.2f} '
                f's={fstat["semantic"]/fstat["n"]:.2f}'
            )
        else:
            field_cell = '<span class="muted">—</span>'
        tone = "request" if score >= 0.85 else "response" if score >= 0.6 else "unknown"
        rows.append(
            "<tr>"
            f'<td><code>{_text(fam)}</code><br><small class="muted">{msg_by_family.get(fam, 0):,} msgs</small></td>'
            '<td class="map-arrow">→</td>'
            f"<td>{_text(gt)}</td>"
            f'<td style="min-width:120px">{_bar(score, "match score")}<small class="muted">{score:.2f} · {_text(m.get("reason", ""))}</small></td>'
            f"<td>{field_cell}</td>"
            "</tr>"
        )
    mapping_table = (
        '<table class="map-table"><thead><tr>'
        '<th>Discovered family</th><th></th><th>Ground-truth type</th>'
        f'<th>Match score {_tip("Similarity between the discovered family and the ground-truth message type it was aligned to (token/field/role similarity).")}</th>'
        f'<th>Field quality {_tip("Average boundary (b) and semantic (s) score across matched fields. 1.0 = perfect byte-offset and meaning match.")}</th>'
        f'</tr></thead><tbody>{"".join(rows)}</tbody></table>'
    )

    def _metric_gauges() -> str:
        defs = [
            ("message_type_matching", "Msg types", "Did each ground-truth message type get a matching discovered family? F1 of the type-level matching."),
            ("field_boundary", "Field bounds", "Were field byte-offsets/lengths recovered correctly? F1 over field boundary matches."),
            ("field_semantics", "Field meaning", "Were field roles/types labelled correctly (e.g. function_code, length)? F1 over semantic labels."),
            ("relations", "Relations", "Were request↔response relationships recovered? F1 over relation edges."),
        ]
        gauges = []
        for key, label, tip in defs:
            block = metrics.get(key, {}) or {}
            f1 = block.get("f1_score", 0.0)
            extra = (
                f"{tip}  |  precision {_num(block.get('precision', 0))}, "
                f"recall {_num(block.get('recall', 0))}, "
                f"TP {block.get('true_positives', 0)} / FP {block.get('false_positives', 0)} / FN {block.get('false_negatives', 0)}"
            )
            gauges.append(_gauge(f1, label, extra))
        return f'<div class="gauge-row">{"".join(gauges)}</div>'

    verdict = str(summary.get("verdict", "unknown"))
    verdict_tone = "request" if verdict == "pass" else "unknown"
    overall = summary.get("overall_score", 0.0)

    return f"""
    <section class="panel eval-panel">
      <h2>Discovered vs Ground Truth</h2>
      <div class="truth-head">
        <div class="truth-score">
          {_gauge(overall, "Overall", "Weighted overall agreement between the discovered protocol model and the ground-truth specification.")}
          <div>
            <p>{_pill(verdict, verdict_tone)}</p>
            <p class="muted">{_text(summary.get("matched_message_type_count", 0))} of {_text(summary.get("ground_truth_message_type_count", 0))} ground-truth types matched · {_text(summary.get("predicted_family_count", 0))} families discovered</p>
          </div>
        </div>
        {_metric_gauges()}
      </div>
      <h4>Family → Ground-truth mapping</h4>
      {mapping_table}
    </section>
    """


def _relation_graph_block(model: Dict[str, Any]) -> str:
    families = model.get("families", []) or []
    relations = model.get("relations", []) or []
    # Only edges between two distinct, known families are worth drawing.
    edges = [
        r for r in relations
        if r.get("request_family_id") and r.get("response_family_id")
        and r.get("request_family_id") != r.get("response_family_id")
    ]
    if not edges:
        return ""
    # Nodes that actually participate in an edge.
    node_ids: List[str] = []
    for r in edges:
        for key in ("request_family_id", "response_family_id"):
            nid = str(r.get(key))
            if nid not in node_ids:
                node_ids.append(nid)
    fam_by_id = {str(f.get("family_id")): f for f in families}
    color_index = {
        str(f.get("family_id")): _color_for(i)
        for i, f in enumerate(sorted(families, key=lambda f: -int(f.get("message_count", 0) or 0)))
    }

    # Circular layout — deterministic, no physics needed.
    n = len(node_ids)
    W = H = 460.0
    cx = cy = W / 2.0
    ring = W / 2.0 - 70.0
    pos: Dict[str, Tuple[float, float]] = {}
    for i, nid in enumerate(node_ids):
        angle = (2 * math.pi * i) / max(1, n) - math.pi / 2
        pos[nid] = (cx + ring * math.cos(angle), cy + ring * math.sin(angle))

    max_pairs = max((int(r.get("pair_count", 0) or 0) for r in edges), default=1) or 1
    edge_svg = []
    for r in edges:
        a = str(r.get("request_family_id"))
        b = str(r.get("response_family_id"))
        if a not in pos or b not in pos:
            continue
        (x1, y1), (x2, y2) = pos[a], pos[b]
        pc = int(r.get("pair_count", 0) or 0)
        width = 1.0 + 5.0 * (pc / max_pairs)
        tip = (
            f"{a} → {b} · {pc:,} pairs · "
            f"score {_num(r.get('avg_pair_score', 0))} · "
            f"support {_num(r.get('support_ratio', 0))} · lift {_num(r.get('edge_lift', 0))} · "
            f"{r.get('relation_type', 'relation')}"
        )
        edge_svg.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="rgba(238,244,223,.28)" stroke-width="{width:.2f}" class="graph-edge" '
            f'data-tip="{escape(tip)}"><title>{escape(tip)}</title></line>'
        )

    max_msg = max((int(f.get("message_count", 0) or 0) for f in families), default=1) or 1
    node_svg = []
    for nid in node_ids:
        x, y = pos[nid]
        fam = fam_by_id.get(nid, {})
        msg = int(fam.get("message_count", 0) or 0)
        role = _role_tone(fam.get("role", "unknown"))
        radius = 14.0 + 20.0 * math.sqrt(msg / max_msg)
        color = color_index.get(nid, "#9eaa9c")
        tip = f"{nid} · {role} · {msg:,} messages"
        node_svg.append(
            f'<g class="graph-node" data-tip="{escape(tip)}">'
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{radius:.1f}" fill="{color}" '
            f'fill-opacity="0.85" stroke="#0b0f0e" stroke-width="2"/>'
            f'<text x="{x:.1f}" y="{y + 3:.1f}" text-anchor="middle" class="graph-label">{_text(nid.replace("family_", "f"))}</text>'
            f'<title>{escape(tip)}</title></g>'
        )

    legend = (
        '<div class="graph-legend">'
        '<span><span class="swatch" style="background:#44d7b6"></span>request</span>'
        '<span><span class="swatch" style="background:#d7ff64"></span>response</span>'
        '<span><span class="swatch" style="background:#ffb86b"></span>unknown</span>'
        '<span class="muted">node size = message volume · edge width = pair count</span>'
        "</div>"
    )
    return f"""
    <section class="panel">
      <h2>Relation Graph {_tip('Request↔response family relationships. Each node is a discovered family; edges link families that were observed as request/response pairs.')}</h2>
      <div class="graph-wrap">
        <svg viewBox="0 0 {W:.0f} {H:.0f}" class="relation-graph" role="img" aria-label="Family relation graph">
          {"".join(edge_svg)}
          {"".join(node_svg)}
        </svg>
      </div>
      {legend}
    </section>
    """


def render_protocol_model_html(
    model: Dict[str, Any],
    evaluation: Optional[Dict[str, Any]] = None,
    llm_analysis: Optional[Dict[str, Any]] = None,
    final_evaluation: Optional[Dict[str, Any]] = None,
    llm_stage_results: Optional[Dict[str, Any]] = None,
) -> str:
    families = _families(model)
    family_cards = "\n".join(_family_card(family, llm_stage_results) for family in families)
    # Pull structured summaries out of the flat metadata table so they can be
    # rendered as their own card-based blocks instead of stringified dicts.
    metadata = dict(model.get("metadata", {}) or {})
    framing_summary_block = _framing_summary_block(metadata.pop("framing_global_summary", None))
    patch_validation_summary = metadata.pop("llm_patch_validation", None)
    compact_refinement_summary = metadata.pop("llm_refinement", None)
    llm_refinement_block = _llm_refinement_block(patch_validation_summary or compact_refinement_summary)
    metadata_rows = _kv_rows(metadata)
    metadata_section = (
        f'<section class="panel"><h2>Metadata</h2>'
        f'<table class="meta-table"><tbody>{metadata_rows}</tbody></table></section>'
        if metadata_rows else ""
    )
    relation_rows = _relation_rows(model, llm_stage_results)
    llm_block = _llm_analysis_block(llm_analysis)
    final_evaluation_block = _final_evaluation_block(final_evaluation)
    overview_block = _overview_block(model)
    truth_comparison_block = _truth_comparison_block(model, final_evaluation)
    relation_graph_block = _relation_graph_block(model)
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
.llm-stage-block {{ margin: 12px 0 18px; padding: 16px; background: rgba(255,255,255,.035); border: 1px solid var(--line); border-radius: 16px; }}
.llm-stage-block h4 {{ margin-top: 0; }}
.llm-stage-block pre {{ max-height: 520px; overflow:auto; white-space: pre-wrap; word-break: break-word; padding: 14px; background: #0b0f0e; border: 1px solid var(--line); border-radius: 14px; color: #dbe8d2; line-height: 1.45; }}
.llm-stage-block .metric strong {{ font-size: 1.1rem; }}
.llm-detail-table td {{ max-width: 360px; overflow-wrap: anywhere; }}
.llm-detail-table code {{ white-space: normal; overflow-wrap: anywhere; }}
.patch-table td:nth-child(3) {{ min-width: 220px; }}
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

/* --- Tooltips (CSS-only) --- */
[data-tip] {{ position: relative; }}
[data-tip]:hover:after {{
  content: attr(data-tip);
  position: absolute; left: 50%; bottom: calc(100% + 8px); transform: translateX(-50%);
  width: max-content; max-width: 320px; white-space: normal; text-align: left;
  background: #05201b; color: #eef4df; border: 1px solid var(--accent-2);
  padding: 9px 12px; border-radius: 12px; font-size: .82rem; line-height: 1.4;
  box-shadow: 0 14px 40px rgba(0,0,0,.55); z-index: 50; pointer-events: none;
}}
[data-tip]:hover:before {{
  content: ""; position: absolute; left: 50%; bottom: calc(100% + 2px); transform: translateX(-50%);
  border: 6px solid transparent; border-top-color: var(--accent-2); z-index: 50; pointer-events: none;
}}
.tip-dot {{
  display:inline-flex; align-items:center; justify-content:center; width: 15px; height: 15px;
  margin-left: 6px; border-radius: 50%; background: rgba(68,215,182,.18); color: var(--accent-2);
  font-style: normal; font-size: .68rem; font-weight: 700; cursor: help; vertical-align: middle;
}}

/* --- Visualization grids --- */
.viz-grid {{ display:grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 18px; margin-bottom: 8px; }}
.viz-card {{ background: rgba(255,255,255,.03); border: 1px solid var(--line); border-radius: 18px; padding: 18px; }}
.viz-card h4 {{ margin-top: 0; }}

/* Horizontal bar chart */
.hbar-chart {{ display:flex; flex-direction: column; gap: 7px; }}
.hbar-row {{ display:grid; grid-template-columns: 86px 1fr auto; align-items:center; gap: 10px; }}
.hbar-label {{ font-size: .82rem; color: var(--muted); font-family: "Cascadia Code", monospace; }}
.hbar-track {{ height: 16px; background: rgba(255,255,255,.06); border-radius: 999px; overflow:hidden; }}
.hbar-fill {{ display:block; height:100%; border-radius: 999px; transition: width .6s ease; }}
.hbar-value {{ font-size: .8rem; color: var(--ink); font-variant-numeric: tabular-nums; }}

/* Donut */
.donut-wrap {{ display:flex; gap: 18px; align-items:center; flex-wrap: wrap; }}
.donut {{ width: 150px; height: 150px; flex: 0 0 auto; }}
.donut circle {{ transition: stroke-dasharray .6s ease; }}
.donut-num {{ fill: var(--ink); font-size: 20px; font-weight: 700; }}
.donut-cap {{ fill: var(--muted); font-size: 9px; }}
.donut-legend {{ list-style:none; padding:0; margin:0; display:flex; flex-direction:column; gap: 6px; font-size: .88rem; }}
.donut-legend li {{ display:flex; align-items:center; gap: 8px; }}
.swatch {{ width: 12px; height: 12px; border-radius: 4px; display:inline-block; flex: 0 0 auto; }}

/* Treemap */
.treemap {{ position: relative; width: 100%; height: 240px; border-radius: 16px; overflow:hidden; border: 1px solid var(--line); }}
.tm-cell {{ position:absolute; border: 1px solid rgba(11,15,14,.65); display:flex; align-items:center; justify-content:center;
  padding: 4px; overflow:hidden; transition: filter .2s; }}
.tm-cell:hover {{ filter: brightness(1.15); z-index: 2; }}
.tm-label {{ font-size: .8rem; font-weight: 700; color: rgba(11,15,14,.82); font-family: "Cascadia Code", monospace; text-align:center; }}

/* Gauges */
.gauge-row {{ display:flex; gap: 14px; flex-wrap: wrap; }}
.gauge {{ display:flex; flex-direction: column; align-items:center; gap: 4px; width: 92px; }}
.gauge svg {{ width: 76px; height: 76px; }}
.gauge-num {{ fill: var(--ink); font-size: 20px; font-weight: 700; }}
.gauge-label {{ font-size: .78rem; color: var(--muted); text-align:center; }}

/* Truth comparison */
.truth-head {{ display:flex; gap: 28px; align-items:center; flex-wrap: wrap; margin-bottom: 14px; }}
.truth-score {{ display:flex; gap: 14px; align-items:center; }}
.truth-score .gauge {{ width: 100px; }}
.truth-score .gauge svg {{ width: 92px; height: 92px; }}
.map-table td {{ vertical-align: middle; }}
.map-table .map-arrow {{ color: var(--accent); font-size: 1.2rem; text-align:center; padding: 0 4px; }}
.map-table small {{ display:block; margin-top: 4px; }}

/* Relation graph */
.graph-wrap {{ display:flex; justify-content:center; }}
.relation-graph {{ width: 100%; max-width: 520px; height: auto; }}
.graph-edge {{ transition: stroke .2s, stroke-width .2s; }}
.graph-edge:hover {{ stroke: var(--accent) !important; }}
.graph-node {{ cursor: pointer; }}
.graph-node:hover circle {{ fill-opacity: 1; stroke: var(--accent); }}
.graph-label {{ fill: #0b0f0e; font-size: 11px; font-weight: 700; font-family: "Cascadia Code", monospace; pointer-events: none; }}
.graph-legend {{ display:flex; gap: 16px; flex-wrap: wrap; justify-content:center; margin-top: 12px; font-size: .85rem; color: var(--ink); }}
.graph-legend span {{ display:flex; align-items:center; gap: 6px; }}

/* Byte ruler / segment map upgrades */
.segment-wrap {{ margin: 16px 0; }}
.byte-ruler {{ display:flex; justify-content: space-between; font-size: .72rem; color: var(--muted); margin-bottom: 4px; }}
.segment-map .seg {{ position: relative; display:flex; align-items:center; justify-content:center; height: 30px; cursor: help; }}
.segment-map {{ height: 30px; }}
.seg b {{ font-size: .68rem; color: rgba(11,15,14,.82); font-weight: 700; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; padding: 0 3px; }}
.seg .seg-off {{ position:absolute; left: 2px; top: -15px; font-size: .6rem; font-style: normal; color: var(--muted); }}
.seg:hover {{ filter: brightness(1.2); }}
.seg-legend {{ display:flex; gap: 14px; margin-top: 6px; font-size: .76rem; color: var(--muted); }}
.seg-legend .sw {{ display:inline-block; width: 11px; height: 11px; border-radius: 3px; margin-right: 5px; vertical-align: middle; }}
.seg-legend .sw.constant {{ background: var(--accent); }}
.seg-legend .sw.variable {{ background: var(--accent-2); }}
.seg-legend .sw.unknown {{ background: var(--warn); }}

@media (max-width: 760px) {{ .family-card header {{ flex-direction: column; }} .panel, .family-card {{ margin-inline: 14px; padding: 18px; }} .hero {{ padding-inline: 14px; }} table {{ font-size: .86rem; }} .hbar-row {{ grid-template-columns: 64px 1fr auto; }} }}
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
  {overview_block}
  {truth_comparison_block}
  {final_evaluation_block}
  {_evaluation_block(evaluation)}
  {llm_block}
  {llm_refinement_block}
  {framing_summary_block}
  {metadata_section}
  {relation_graph_block}
  <section class="panel">
    <h2>Strongest Relations</h2>
    <details><summary>Show full relation metrics table</summary>
    <table><thead><tr><th>Request</th><th>Response</th><th>Pairs</th><th>Score</th><th>Support</th><th>Lift</th><th>Direction</th><th>Order</th><th>Flow</th><th>Echoes</th><th>Length Rules</th><th>LLM Validation</th></tr></thead><tbody>{relation_rows}</tbody></table>
    </details>
  </section>
  <main>
    <section class="panel"><h2>Families</h2><p class="muted">Showing {len(families)} largest families.</p></section>
    {family_cards}
  </main>
  <footer class="footer">Generated by Protocol RE. Raw payloads are omitted from this report.</footer>
</body>
</html>
"""
