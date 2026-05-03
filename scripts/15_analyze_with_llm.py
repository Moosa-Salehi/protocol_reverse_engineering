#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from protocol_re.llm.analyze import (
    LLMRequestConfig,
    call_openai_compatible_chat,
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


def _load_config(path: str) -> dict:
    config_path = Path(path)
    if not config_path.is_file():
        raise SystemExit(f"Error: LLM config file does not exist: {config_path}")
    with open(config_path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _env_api_key() -> str | None:
    import os

    return os.environ.get("OPENAI_API_KEY") or os.environ.get("LLM_API_KEY")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render an LLM prompt from llm_evidence.json and optionally call an OpenAI-compatible chat-completions API."
    )
    parser.add_argument("llm_evidence_json", help="Input evidence bundle from 14_export_llm_evidence.py")
    parser.add_argument("output_json", help="Output LLM analysis JSON")
    parser.add_argument("--config", default="LLM_config.json", help="LLM config JSON containing openai_base_url and model")
    parser.add_argument("--prompt-out", help="Optional path to write the rendered prompt Markdown")
    parser.add_argument("--template", help="Optional custom prompt-template Markdown file")
    parser.add_argument("--render-only", action="store_true", help="Only render prompt and metadata; do not call the LLM API")
    parser.add_argument("--temperature", type=float, help="Override temperature from LLM_config.json")
    parser.add_argument("--max-tokens", type=int, help="Override max_tokens from LLM_config.json")
    parser.add_argument("--timeout", type=int, help="Override timeout from LLM_config.json")
    args = parser.parse_args()

    config = _load_config(args.config)
    model = config.get("model")
    base_url = config.get("openai_base_url")
    if not model:
        raise SystemExit("Error: LLM_config.json must define model.")
    if not base_url:
        raise SystemExit("Error: LLM_config.json must define openai_base_url.")
    temperature = args.temperature if args.temperature is not None else float(config.get("temperature", 0.1))
    max_tokens = args.max_tokens if args.max_tokens is not None else int(config.get("max_tokens", 6000))
    timeout = args.timeout if args.timeout is not None else int(config.get("timeout", 120))

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
        "config_path": args.config,
        "model": model,
        "render_only": args.render_only,
        "analysis_markdown": None,
        "usage": None,
        "raw_response": None,
    }

    if not args.render_only:
        api_key = _env_api_key()
        if not api_key and config.get("api_key_required") == "yes":
            raise SystemExit("Error: API key required via OPENAI_API_KEY or LLM_API_KEY. Use --render-only to skip API call.")
        response = call_openai_compatible_chat(
            prompt,
            LLMRequestConfig(
                model=model,
                base_url=base_url,
                api_key=api_key if api_key else "api_key",
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=timeout,
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
