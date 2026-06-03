from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional


DEFAULT_USER_RESPONSE_DIR = Path("data") / "user_provided_LLM_responses"


def make_user_response_path(
    stage_name: str,
    identifier: str | None = None,
    response_dir: str | Path = DEFAULT_USER_RESPONSE_DIR,
) -> Path:
    stem = stage_name
    if identifier:
        safe_identifier = "".join(char if char.isalnum() or char in ("-", "_", ".") else "_" for char in identifier)
        stem = f"{stem}_{safe_identifier}"
    return Path(response_dir) / f"{stem}.json"


def ensure_user_response_placeholder(
    path: str | Path,
    *,
    stage: str,
    prompt_path: str | Path | None = None,
    model: str = "",
    request_label: str = "",
    metadata: Optional[dict[str, Any]] = None,
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        return

    placeholder = {
        "stage": stage,
        "model": model,
        "request_label": request_label,
        "prompt_path": str(prompt_path) if prompt_path else "",
        "response_text": "",
        "response": None,
        "metadata": metadata or {},
        "notes": (
            "Paste the assistant response into response_text. "
            "Alternatively, paste a raw OpenAI-compatible chat completion JSON object into response."
        ),
    }
    target.write_text(json.dumps(placeholder, indent=2, ensure_ascii=False), encoding="utf-8")


def _message_response_from_text(text: str, model: str = "") -> str:
    return json.dumps(
        {
            "model": model,
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": text,
                    }
                }
            ],
        },
        ensure_ascii=False,
    )


def _raw_response_from_value(value: Any, model: str = "") -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return None
        try:
            parsed = json.loads(stripped)
        except json.JSONDecodeError:
            return _message_response_from_text(stripped, model)
        return json.dumps(parsed, ensure_ascii=False)
    if isinstance(value, dict):
        if "choices" in value:
            return json.dumps(value, ensure_ascii=False)
        return _message_response_from_text(json.dumps(value, ensure_ascii=False), model)
    if isinstance(value, list):
        return _message_response_from_text(json.dumps(value, ensure_ascii=False), model)
    return _message_response_from_text(str(value), model)


def load_user_provided_response(path: str | Path) -> Optional[str]:
    target = Path(path)
    if not target.is_file():
        raise FileNotFoundError(f"user-provided LLM response file does not exist: {target}")

    text = target.read_text(encoding="utf-8")
    if not text.strip():
        return None

    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return _message_response_from_text(text.strip())

    if not isinstance(payload, dict):
        return _raw_response_from_value(payload)

    model = str(payload.get("model") or "")
    for key in ("response", "raw_response", "api_response"):
        raw_response = _raw_response_from_value(payload.get(key), model)
        if raw_response is not None:
            return raw_response

    for key in ("response_text", "assistant_response", "content"):
        value = payload.get(key)
        if value is None:
            continue
        if isinstance(value, str):
            stripped = value.strip()
            if stripped:
                return _message_response_from_text(stripped, model)
        else:
            return _message_response_from_text(json.dumps(value, ensure_ascii=False), model)

    return None
