#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from protocol_re.llm.analyze import (
    LLMRequestConfig,
    call_openai_compatible_chat,
    env_value,
    extract_message_text,
    render_analysis_prompt,
)


def _load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _load_template(path: str | None) -> str | None:
    if not path:
        return None
    return Path(path).read_text(encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render an LLM prompt from llm_evidence.json and optionally call an OpenAI-compatible chat-completions API."
    )
    parser.add_argument("llm_evidence_json", help="Input evidence bundle from 14_export_llm_evidence.py")
    parser.add_argument("output_json", help="Output LLM analysis JSON")
    parser.add_argument("--prompt-out", help="Optional path to write the rendered prompt Markdown")
    parser.add_argument("--template", help="Optional custom prompt-template Markdown file")
    parser.add_argument("--render-only", action="store_true", help="Only render prompt and metadata; do not call the LLM API")
    parser.add_argument("--model", default="gpt-4o-mini", help="OpenAI-compatible model name")
    parser.add_argument("--base-url", help="OpenAI-compatible base URL; falls back to OPENAI_BASE_URL or LLM_BASE_URL")
    parser.add_argument("--api-key", help="API key; falls back to OPENAI_API_KEY or LLM_API_KEY")
    parser.add_argument("--temperature", type=float, default=0.1)
    parser.add_argument("--max-tokens", type=int, default=6000)
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()

    evidence = _load_json(args.llm_evidence_json)
    template = _load_template(args.template)
    prompt = render_analysis_prompt(evidence, template=template) if template else render_analysis_prompt(evidence)

    if args.prompt_out:
        Path(args.prompt_out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.prompt_out).write_text(prompt, encoding="utf-8")

    output = {
        "artifact_type": "llm_protocol_analysis",
        "source_evidence": args.llm_evidence_json,
        "prompt_path": args.prompt_out,
        "model": args.model,
        "render_only": args.render_only,
        "analysis_markdown": None,
        "usage": None,
        "raw_response": None,
    }

    if not args.render_only:
        api_key = env_value(args.api_key, "OPENAI_API_KEY", "LLM_API_KEY")
        base_url = env_value(args.base_url, "OPENAI_BASE_URL", "LLM_BASE_URL")
        if not api_key:
            raise SystemExit("Error: API key required via --api-key, OPENAI_API_KEY, or LLM_API_KEY. Use --render-only to skip API call.")
        if not base_url:
            raise SystemExit("Error: base URL required via --base-url, OPENAI_BASE_URL, or LLM_BASE_URL. Use --render-only to skip API call.")
        response = call_openai_compatible_chat(
            prompt,
            LLMRequestConfig(
                model=args.model,
                base_url=base_url,
                api_key=api_key,
                temperature=args.temperature,
                max_tokens=args.max_tokens,
                timeout=args.timeout,
            ),
        )
        output["analysis_markdown"] = extract_message_text(response)
        output["usage"] = response.get("usage")
        output["raw_response"] = response

    with open(args.output_json, "w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2, ensure_ascii=False)

    status = "prompt rendered" if args.render_only else "analysis completed"
    print(f"[+] LLM {status}; wrote {args.output_json}")


if __name__ == "__main__":
    main()
