#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json

from protocol_re.export.html import render_protocol_model_html


def _load_optional_json(path: str | None):
    if not path:
        return None
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a self-contained HTML protocol report from protocol_model.json.")
    parser.add_argument("protocol_model_json")
    parser.add_argument("output_html")
    parser.add_argument("--evaluation-json", help="Optional evaluation report JSON from 13_evaluate_pipeline.py")
    args = parser.parse_args()

    with open(args.protocol_model_json, "r", encoding="utf-8") as handle:
        model = json.load(handle)

    html = render_protocol_model_html(model, evaluation=_load_optional_json(args.evaluation_json))
    with open(args.output_html, "w", encoding="utf-8") as handle:
        handle.write(html)

    print(f"[+] Wrote HTML protocol report to {args.output_html}")


if __name__ == "__main__":
    main()
