from __future__ import annotations

from io import BytesIO
from typing import Any
import urllib.error

import pytest

from protocol_re.llm import analyze
from protocol_re.llm.analyze import LLMAPIError, LLMRequestConfig, call_openai_compatible_chat_with_raw


class _Logger:
    def __init__(self) -> None:
        self.entries: list[tuple[str, str, dict[str, Any]]] = []

    def info(self, message: str, **kwargs: Any) -> None:
        self.entries.append(("info", message, kwargs))

    def warning(self, message: str, **kwargs: Any) -> None:
        self.entries.append(("warning", message, kwargs))

    def error(self, message: str, **kwargs: Any) -> None:
        self.entries.append(("error", message, kwargs))


class _Response:
    def __init__(self, body: str) -> None:
        self.body = body.encode("utf-8")

    def __enter__(self) -> "_Response":
        return self

    def __exit__(self, *_args: Any) -> None:
        return None

    def read(self) -> bytes:
        return self.body


def _config(logger: _Logger) -> LLMRequestConfig:
    return LLMRequestConfig(
        model="test-model",
        base_url="https://example.test/v1",
        api_key="test-key",
        timeout=1,
        max_retries=1,
        retry_delay_seconds=0,
        request_interval_seconds=0,
        logger=logger,
    )


def test_temporary_network_error_is_retried(monkeypatch: pytest.MonkeyPatch) -> None:
    logger = _Logger()
    calls = {"count": 0}

    def fake_urlopen(_request: Any, timeout: int) -> _Response:
        calls["count"] += 1
        if calls["count"] == 1:
            raise urllib.error.URLError(TimeoutError("timed out"))
        return _Response('{"choices":[{"message":{"content":"{}"}}]}')

    monkeypatch.setattr(analyze.urllib.request, "urlopen", fake_urlopen)

    response, raw = call_openai_compatible_chat_with_raw("prompt", _config(logger), "test request")

    assert calls["count"] == 2
    assert response["choices"][0]["message"]["content"] == "{}"
    assert raw.startswith('{"choices"')
    assert [entry[1] for entry in logger.entries].count("sending request for test request") == 2
    assert any(entry[0] == "warning" and "timeout" in entry[1] for entry in logger.entries)
    assert any(entry[0] == "info" and "success" in entry[1] for entry in logger.entries)


def test_invalid_api_key_is_not_retried(monkeypatch: pytest.MonkeyPatch) -> None:
    logger = _Logger()
    calls = {"count": 0}

    def fake_urlopen(_request: Any, timeout: int) -> _Response:
        calls["count"] += 1
        raise urllib.error.HTTPError(
            url="https://example.test/v1/chat/completions",
            code=401,
            msg="Unauthorized",
            hdrs=None,
            fp=BytesIO(b'{"error":{"message":"invalid api key"}}'),
        )

    monkeypatch.setattr(analyze.urllib.request, "urlopen", fake_urlopen)

    with pytest.raises(LLMAPIError) as exc_info:
        call_openai_compatible_chat_with_raw("prompt", _config(logger), "auth request")

    assert calls["count"] == 1
    assert exc_info.value.category == "invalid_api_key"
    assert exc_info.value.retryable is False
    assert any(entry[0] == "error" and "invalid_api_key" in entry[1] for entry in logger.entries)


def test_context_limit_error_is_classified_as_non_retryable(monkeypatch: pytest.MonkeyPatch) -> None:
    logger = _Logger()
    calls = {"count": 0}

    def fake_urlopen(_request: Any, timeout: int) -> _Response:
        calls["count"] += 1
        raise urllib.error.HTTPError(
            url="https://example.test/v1/chat/completions",
            code=400,
            msg="Bad Request",
            hdrs=None,
            fp=BytesIO(b'{"error":{"message":"maximum context length exceeded"}}'),
        )

    monkeypatch.setattr(analyze.urllib.request, "urlopen", fake_urlopen)

    with pytest.raises(LLMAPIError) as exc_info:
        call_openai_compatible_chat_with_raw("prompt", _config(logger), "large request")

    assert calls["count"] == 1
    assert exc_info.value.category == "context_limit_reached"
    assert exc_info.value.retryable is False

