"""A small declarative parser language (JSON) that the LLM writes and a deterministic interpreter runs (ideas 2/3).
No LLM-written code is executed.

  {"fields": [node, ...]}
  node:
    {"name": n, "type": "uint", "size": 1|2|4|8, "endian": "big"|"little"}
    {"name": n, "type": "bytes", "size": k}                  fixed-width opaque bytes / string
    {"name": n, "type": "bytes", "size_from": m, "adjust": c} width = value of earlier uint field m + c
    {"name": n, "type": "array", "count_from": m, "item": [node, ...]}
    {"name": n, "type": "array", "until_end": true, "item": [node, ...]}
    {"name": n, "type": "tlv", "tag_size": 1|2, "len_size": 1|2, "endian": "big"|"little"}   repeated to the end
    {"name": n, "type": "rest"}                              everything that is left, one field
A message may end exactly at a field boundary (absent optional tail). Every primitive is one field; array items share
their keys (name[].child), so values line up across messages.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

MAX_SEGS = 400


class ParseError(Exception):
    pass


def _uint(b: bytes, s: int, w: int, endian: str) -> int:
    if s + w > len(b):
        raise ParseError("short")
    return int.from_bytes(b[s:s + w], "little" if endian == "little" else "big")


def _parse(nodes: List[Dict[str, Any]], b: bytes, pos: int, end: int, env: Dict[str, int], path: str,
           out: List[Tuple[str, int, int]], derived: set) -> int:
    for node in nodes:
        if pos == end:                      # optional tail absent
            return pos
        if len(out) > MAX_SEGS:
            raise ParseError("too many segments")
        t = node.get("type")
        name = str(node.get("name", t))
        key = f"{path}{name}"
        if t == "uint":
            w = int(node.get("size", 1))
            if w not in (1, 2, 3, 4, 8):
                raise ParseError("bad size")
            if pos + w > end:
                raise ParseError("short uint")
            env[name] = _uint(b, pos, w, node.get("endian", "big"))
            out.append((key, pos, pos + w)); pos += w
        elif t == "bytes":
            if "size_from" in node:
                ref = str(node["size_from"])
                if ref not in env:
                    raise ParseError(f"unknown size_from {ref}")
                w = env[ref] + int(node.get("adjust", 0))
                derived.add(f"{path}{ref}")
            else:
                w = int(node.get("size", 1))
            if w < 0 or pos + w > end:
                raise ParseError("short bytes")
            if w:
                out.append((key, pos, pos + w))
            pos += w
        elif t == "rest":
            if end > pos:
                out.append((key, pos, end))
            pos = end
        elif t == "array":
            item = node.get("item") or []
            if not item:
                raise ParseError("empty item")
            if node.get("until_end"):
                guard = 0
                while pos < end:
                    new = _parse(item, b, pos, end, env, f"{key}[].", out, derived)
                    if new <= pos:
                        raise ParseError("no progress")
                    pos = new; guard += 1
                    if guard > 300:
                        raise ParseError("array too long")
            else:
                ref = str(node.get("count_from"))
                if ref not in env:
                    raise ParseError(f"unknown count_from {ref}")
                n = env[ref]
                if n > 300:
                    raise ParseError("count too large")
                derived.add(f"{path}{ref}")
                for _ in range(n):
                    pos = _parse(item, b, pos, end, env, f"{key}[].", out, derived)
        elif t == "tlv":
            tw, lw = int(node.get("tag_size", 1)), int(node.get("len_size", 1))
            en = node.get("endian", "big")
            while pos < end:
                if pos + tw + lw > end:
                    raise ParseError("short tlv")
                ln = _uint(b, pos + tw, lw, en)
                if pos + tw + lw + ln > end:
                    raise ParseError("tlv overrun")
                out.append((f"{key}.tag", pos, pos + tw)); out.append((f"{key}.len", pos + tw, pos + tw + lw))
                if ln:
                    out.append((f"{key}.value", pos + tw + lw, pos + tw + lw + ln))
                derived.add(f"{key}.len")
                pos += tw + lw + ln
        else:
            raise ParseError(f"unknown type {t}")
    return pos


def run(spec: Dict[str, Any], payloads: List[bytes]):
    """-> (segments per message or None if rejected, derived keys, rejection reasons)"""
    nodes = spec.get("fields") if isinstance(spec, dict) else None
    if not isinstance(nodes, list) or not nodes:
        raise ParseError("spec has no fields")
    segs, derived, reasons = [], set(), {}
    for b in payloads:
        out: List[Tuple[str, int, int]] = []
        try:
            _parse(nodes, b, 0, len(b), {}, "", out, derived)
            segs.append(out)
        except (ParseError, ValueError, TypeError, KeyError) as e:
            segs.append(None); reasons[str(e)] = reasons.get(str(e), 0) + 1
    return segs, frozenset(derived), reasons


def edges(segs: Optional[List[Tuple[str, int, int]]], n: int) -> List[int]:
    if segs is None:
        return []
    return sorted({x for _, s, e in segs for x in (s, e) if 0 < x < n})


def fixed_spec(edge_list: List[int], length: int) -> Dict[str, Any]:
    """A fixed-offset field list as a spec (for showing the pipeline's answer to the LLM)."""
    pts = [0] + [e for e in edge_list if 0 < e < length] + [length]
    fields = []
    for k, (s, t) in enumerate(zip(pts, pts[1:])):
        w = t - s
        fields.append({"name": f"f{s}", "type": "uint", "size": w, "endian": "big"} if w in (1, 2, 4) else
                      {"name": f"f{s}", "type": "bytes", "size": w})
    if fields:
        fields[-1] = {"name": fields[-1]["name"], "type": "rest"}
    return {"fields": fields}
