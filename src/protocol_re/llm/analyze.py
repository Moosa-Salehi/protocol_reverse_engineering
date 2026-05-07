from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, Optional


DEFAULT_SYSTEM_PROMPT = "You are an expert Protocol Reverse Engineering Analyst."

DEFAULT_ANALYSIS_TEMPLATE = """Role
You are an expert Protocol Reverse Engineering Analyst.

Task
Analyze the provided Protocol Reverse Engineering Evidence Bundle and infer the most plausible structure and semantics of the protocol. Base all reasoning strictly on the supplied evidence.

Perform the following analyses:

1. Protocol Structure Inference
Infer the most plausible high-level structure of the protocol based on the evidence across families, segments, and fields.
Identify likely header regions, opcode/function identifiers, length fields, constant markers, and payload areas.

2. Field Boundary and Type Review
Evaluate the correctness of inferred field boundaries and field types.
- Detect likely boundary errors or merged/split fields
- Suggest corrected start/end offsets when evidence indicates mistakes
- Identify likely field types (opcode, length, counter, flags, identifier, payload, checksum)
Provide corrected field definitions where appropriate.

3. Semantic Interpretation
Improve the semantic meaning of fields using evidence from:
- semantic_labels
- relations
- global_hypotheses
- structural patterns across families
Suggest meaningful names for fields.

4. Opcode Identification
Identify fields that likely represent operation codes or function identifiers.
For each candidate:
- explain the evidence
- describe the likely operation class
- map which message families correspond to each operation.

5. Request / Response Interpretation
Using relations, determine:
- which families act as requests
- which families act as responses
- how fields propagate between them (echo fields, transaction IDs, etc.)
Explain the request/response lifecycle and matching logic.

6. Clustering Evaluation
Evaluate whether the current family clustering is correct.
Identify:
- families that likely belong together
- families that should be split
- potential noise clusters
Suggest concrete clustering improvements if evidence supports them.

7. Contradictions and Inference Errors
Identify contradictions or weak areas in the current inference model:
- conflicting field interpretations
- inconsistent boundaries
- relations that do not match structural patterns
- hypotheses that lack sufficient evidence
Clearly mark these issues.

8. Protocol Layout Reconstruction
Produce a cleaned and consolidated protocol layout describing:
- common message structure
- shared header fields
- operation-specific payload regions
- request/response mapping
The goal is to provide a human-readable structural model of the protocol.

9. Similarity to Known Protocols
If strong structural evidence exists, indicate whether the protocol resembles any known protocol families (e.g., industrial control protocols).
Only report such similarity when multiple structural characteristics match.
Do not speculate when evidence is weak.

10. Answer Open Questions
Address the questions listed in open_questions using available evidence.
If insufficient evidence exists, explicitly state that additional captures or analysis are required.

FOCUS: Use the evaluation section to weigh the reliability of your findings.
CONSTRAINT: Do not invent protocol details. If evidence is insufficient, explicitly label it as "Requires Capture/Inspection".

Output requirements
Return a concise but complete Markdown report with these exact section headings:
- Executive Summary
- Inferred Protocol Structure
- Field Boundary Review
- Semantic Field Map
- Opcode Candidates
- Request Response Lifecycle
- Clustering Assessment
- Contradictions And Weak Evidence
- Reconstructed Protocol Layout
- Similarity To Known Protocols
- Answers To Open Questions
- Recommended Next Captures Or Analysis
"""


@dataclass
class LLMRequestConfig:
    model: str
    base_url: str
    api_key: str
    temperature: float = 0.1
    max_tokens: int = 6000
    timeout: int = 120


def render_analysis_prompt(
    evidence: Dict[str, Any],
    template: str = DEFAULT_ANALYSIS_TEMPLATE,
    minify_json: bool = False,
) -> str:
    if minify_json:
        evidence_json = json.dumps(evidence, separators=(",", ":"), ensure_ascii=False)
    else:
        evidence_json = json.dumps(evidence, indent=2, ensure_ascii=False)
    return (
        template.rstrip()
        + "\n\nProtocol Reverse Engineering Evidence Bundle\n"
        + "```json\n"
        + evidence_json
        + "\n```\n"
    )


def _chat_completions_url(base_url: str) -> str:
    base = base_url.rstrip("/")
    if base.endswith("/chat/completions"):
        return base
    return base + "/chat/completions"


def call_openai_compatible_chat(prompt: str, config: LLMRequestConfig) -> Dict[str, Any]:
    payload = {
        "model": config.model,
        "messages": [
            {"role": "system", "content": DEFAULT_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "temperature": config.temperature,
        "max_tokens": config.max_tokens,
    }
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        _chat_completions_url(config.base_url),
        data=data,
        headers={
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=config.timeout) as response:
            body = response.read().decode("utf-8")
            return json.loads(body)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"LLM API HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"LLM API request failed: {exc}") from exc


def extract_message_text(response: Dict[str, Any]) -> str:
    choices = response.get("choices", []) or []
    if not choices:
        return ""
    message = choices[0].get("message", {}) or {}
    content = message.get("content", "")
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict):
                parts.append(str(item.get("text") or item.get("content") or ""))
            else:
                parts.append(str(item))
        return "".join(parts)
    return str(content)


def env_value(primary: Optional[str], *names: str) -> Optional[str]:
    if primary:
        return primary
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return None
