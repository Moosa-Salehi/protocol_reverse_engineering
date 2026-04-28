#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json

from protocol_re.export.markdown import render_protocol_model_markdown


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a human-readable Markdown protocol specification from protocol_model.json.")
    parser.add_argument("protocol_model_json")
    parser.add_argument("output_md")
    args = parser.parse_args()

    with open(args.protocol_model_json, "r", encoding="utf-8") as handle:
        model = json.load(handle)

    markdown = render_protocol_model_markdown(model)
    with open(args.output_md, "w", encoding="utf-8") as handle:
        handle.write(markdown)

    print(f"[+] Wrote Markdown protocol specification to {args.output_md}")


if __name__ == "__main__":
    main()
