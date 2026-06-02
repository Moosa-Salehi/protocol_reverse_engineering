"""Shared helpers for surfacing LLM stage failures loudly.

The multi-stage runners (``run_*_stage``) catch their own exceptions and return a
``StageResult`` with ``success=False`` and an ``error`` string instead of raising.
Without an explicit check, a stage script would then write an empty prompt/output
and exit 0 — so a render-only run could silently produce empty prompt files while
the pipeline reports success. These helpers detect those cases. LLM API failures
can be downgraded to warnings so the deterministic pipeline can continue with
fallback artifacts.
"""
from __future__ import annotations

import sys
from typing import List, Optional, Sequence, Tuple

from protocol_re.llm.multi_stage import StageResult

LLM_API_ERROR_CATEGORY = "llm_api"


def collect_stage_failures(
    items: Sequence[Tuple[str, StageResult]],
    *,
    render_only: bool,
) -> List[Tuple[str, str]]:
    """Return ``(label, reason)`` pairs for sub-stages that failed.

    A sub-stage is considered failed when it caught an exception
    (``success=False``) or, in render-only mode, when it produced an empty prompt
    (the whole point of render-only is to emit a usable prompt).
    """
    failures: List[Tuple[str, str]] = []
    for label, result in items:
        if not result.success:
            failures.append((label, result.error or "unknown error"))
        elif render_only and not (result.prompt or "").strip():
            failures.append((label, "render-only mode produced an empty prompt"))
    return failures


def fail_loudly_if_any(
    failures: Sequence[Tuple[str, str]],
    *,
    stage_name: str,
    logger: Optional[object] = None,
) -> None:
    """Print a prominent error banner and exit non-zero if there are failures.

    Artifacts should already be written before calling this so that partial
    results remain available for debugging. Exiting non-zero causes the pipeline
    runner to abort, preventing silent masking of empty prompts/outputs.
    """
    if not failures:
        return
    header = (
        f"[!] ERROR: {stage_name} had {len(failures)} failed sub-stage(s); "
        "prompt/output may be empty or incomplete."
    )
    print("", file=sys.stderr)
    print(header, file=sys.stderr)
    if logger is not None:
        logger.error(header)
    for label, reason in failures:
        line = f"      - {label}: {reason}"
        print(line, file=sys.stderr)
        if logger is not None:
            logger.error(f"{stage_name} failure [{label}]: {reason}")
    sys.exit(1)


def warn_or_fail_stage_failures(
    items: Sequence[Tuple[str, StageResult]],
    *,
    render_only: bool,
    stage_name: str,
    logger: Optional[object] = None,
) -> None:
    """Warn for LLM API failures, but fail loudly for other stage failures."""
    llm_api_failures: List[Tuple[str, str]] = []
    blocking_failures: List[Tuple[str, str]] = []

    for label, result in items:
        if not result.success:
            reason = result.error or "unknown error"
            if getattr(result, "error_category", None) == LLM_API_ERROR_CATEGORY:
                llm_api_failures.append((label, reason))
            else:
                blocking_failures.append((label, reason))
        elif render_only and not (result.prompt or "").strip():
            blocking_failures.append((label, "render-only mode produced an empty prompt"))

    if llm_api_failures:
        header = (
            f"[!] WARNING: {stage_name} could not use the LLM for "
            f"{len(llm_api_failures)} sub-stage(s); continuing without LLM output."
        )
        print("", file=sys.stderr)
        print(header, file=sys.stderr)
        if logger is not None:
            logger.warning(header)
        for label, reason in llm_api_failures:
            line = f"      - {label}: {reason}"
            print(line, file=sys.stderr)
            if logger is not None:
                logger.warning(f"{stage_name} LLM unavailable [{label}]: {reason}")

    fail_loudly_if_any(blocking_failures, stage_name=stage_name, logger=logger)
