"""
Structured logging utilities for protocol reverse engineering pipeline.

Provides:
- Structured JSON logging with context
- Progress tracking with time estimates
- Performance profiling per stage
- Decision logging for debugging
"""

from __future__ import annotations

import json
import logging
import sys
import time
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

try:
    from colorama import Fore, Style, init
    init()
    HAS_COLOR = True
except ImportError:
    HAS_COLOR = False


class ColoredFormatter(logging.Formatter):
    """Colored console formatter with level-based colors."""

    COLORS = {
        'DEBUG': Fore.CYAN if HAS_COLOR else '',
        'INFO': Fore.GREEN if HAS_COLOR else '',
        'WARNING': Fore.YELLOW if HAS_COLOR else '',
        'ERROR': Fore.RED if HAS_COLOR else '',
        'CRITICAL': Fore.RED + Style.BRIGHT if HAS_COLOR else '',
    }
    RESET = Style.RESET_ALL if HAS_COLOR else ''

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, '')
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


class StructuredLogger:
    """
    Structured logger with JSON output and context tracking.

    Features:
    - Structured JSON logs for machine parsing
    - Human-readable console output
    - Context tracking (stage, family, session)
    - Performance metrics
    - Decision logging
    """

    def __init__(
        self,
        name: str,
        log_dir: Optional[Path] = None,
        console_level: int = logging.INFO,
        file_level: int = logging.DEBUG,
        enable_json: bool = True,
    ):
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers.clear()

        # Context stack for nested operations
        self.context_stack: list[dict[str, Any]] = []

        # Performance tracking
        self.stage_timings: dict[str, float] = {}
        self.stage_start_times: dict[str, float] = {}

        # Console handler with colors
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(console_level)
        console_formatter = ColoredFormatter(
            '[%(levelname)s] %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # File handlers
        if log_dir:
            log_dir = Path(log_dir)
            log_dir.mkdir(parents=True, exist_ok=True)

            # Human-readable log
            text_handler = logging.FileHandler(log_dir / f"{name}.log", mode='a')
            text_handler.setLevel(file_level)
            text_formatter = logging.Formatter(
                '%(asctime)s [%(levelname)s] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            text_handler.setFormatter(text_formatter)
            self.logger.addHandler(text_handler)

            # JSON structured log
            if enable_json:
                self.json_log_path = log_dir / f"{name}.jsonl"
                self.json_handler = logging.FileHandler(self.json_log_path, mode='a')
                self.json_handler.setLevel(file_level)
                self.json_handler.setFormatter(logging.Formatter('%(message)s'))
                self.logger.addHandler(self.json_handler)
                self.enable_json = True
            else:
                self.json_handler = None
                self.enable_json = False
        else:
            self.json_handler = None
            self.enable_json = False

    def _get_context(self) -> dict[str, Any]:
        """Get current context from stack."""
        context = {}
        for ctx in self.context_stack:
            context.update(ctx)
        return context

    def _log_json(self, level: str, message: str, **kwargs):
        """Write structured JSON log entry."""
        if not self.enable_json or not self.json_handler:
            return

        entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': level,
            'logger': self.name,
            'message': message,
            'context': self._get_context(),
            **kwargs
        }

        json_line = json.dumps(entry, default=str)
        record = logging.LogRecord(
            name=self.name,
            level=getattr(logging, level),
            pathname='',
            lineno=0,
            msg=json_line,
            args=(),
            exc_info=None
        )
        self.json_handler.emit(record)

    @contextmanager
    def context(self, **kwargs):
        """Add context for nested operations."""
        self.context_stack.append(kwargs)
        try:
            yield
        finally:
            self.context_stack.pop()

    @staticmethod
    def _format(message: str, args: tuple) -> str:
        """Apply %-style formatting like the stdlib logger, when args are given."""
        if args:
            try:
                return message % args
            except (TypeError, ValueError):
                return message + " " + " ".join(str(a) for a in args)
        return message

    def debug(self, message: str, *args, **kwargs):
        """Log debug message."""
        message = self._format(message, args)
        self.logger.debug(message)
        self._log_json('DEBUG', message, **kwargs)

    def info(self, message: str, *args, **kwargs):
        """Log info message."""
        message = self._format(message, args)
        self.logger.info(message)
        self._log_json('INFO', message, **kwargs)

    def warning(self, message: str, *args, **kwargs):
        """Log warning message."""
        message = self._format(message, args)
        self.logger.warning(message)
        self._log_json('WARNING', message, **kwargs)

    def error(self, message: str, *args, **kwargs):
        """Log error message."""
        message = self._format(message, args)
        self.logger.error(message)
        self._log_json('ERROR', message, **kwargs)

    def critical(self, message: str, *args, **kwargs):
        """Log critical message."""
        message = self._format(message, args)
        self.logger.critical(message)
        self._log_json('CRITICAL', message, **kwargs)

    def decision(self, decision: str, reason: str, **evidence):
        """
        Log a key decision with reasoning and evidence.

        Args:
            decision: What decision was made
            reason: Why it was made
            **evidence: Supporting evidence (metrics, values, etc.)
        """
        msg = f"DECISION: {decision} | Reason: {reason}"
        if evidence:
            evidence_str = ", ".join(f"{k}={v}" for k, v in evidence.items())
            msg += f" | Evidence: {evidence_str}"

        self.info(msg, decision=decision, reason=reason, evidence=evidence)

    def metric(self, name: str, value: Any, unit: Optional[str] = None):
        """
        Log a metric value.

        Args:
            name: Metric name
            value: Metric value
            unit: Optional unit (e.g., 'ms', 'bytes', 'count')
        """
        unit_str = f" {unit}" if unit else ""
        msg = f"METRIC: {name} = {value}{unit_str}"
        self.info(msg, metric_name=name, metric_value=value, metric_unit=unit)

    @contextmanager
    def stage(self, stage_name: str):
        """
        Context manager for tracking stage execution.

        Usage:
            with logger.stage("extract_messages"):
                # do work
                pass
        """
        self.stage_start_times[stage_name] = time.time()
        self.info(f"Starting stage: {stage_name}")
        self._log_json('INFO', f"Stage started: {stage_name}", stage=stage_name, event='stage_start')

        with self.context(stage=stage_name):
            try:
                yield
                elapsed = time.time() - self.stage_start_times[stage_name]
                self.stage_timings[stage_name] = elapsed
                self.info(f"Completed stage: {stage_name} in {elapsed:.2f}s")
                self._log_json(
                    'INFO',
                    f"Stage completed: {stage_name}",
                    stage=stage_name,
                    event='stage_complete',
                    duration_seconds=elapsed
                )
            except Exception as e:
                elapsed = time.time() - self.stage_start_times[stage_name]
                self.error(f"Stage failed: {stage_name} after {elapsed:.2f}s - {e}")
                self._log_json(
                    'ERROR',
                    f"Stage failed: {stage_name}",
                    stage=stage_name,
                    event='stage_failed',
                    duration_seconds=elapsed,
                    error=str(e)
                )
                raise

    def get_stage_timings(self) -> dict[str, float]:
        """Get all stage timings."""
        return self.stage_timings.copy()

    def log_stage_summary(self):
        """Log summary of all stage timings."""
        if not self.stage_timings:
            return

        total_time = sum(self.stage_timings.values())
        self.info("=" * 60)
        self.info("Stage Performance Summary")
        self.info("=" * 60)

        for stage, duration in sorted(self.stage_timings.items(), key=lambda x: x[1], reverse=True):
            percentage = (duration / total_time * 100) if total_time > 0 else 0
            self.info(f"  {stage:40s} {duration:8.2f}s ({percentage:5.1f}%)")

        self.info("-" * 60)
        self.info(f"  {'TOTAL':40s} {total_time:8.2f}s")
        self.info("=" * 60)

        self._log_json(
            'INFO',
            'Stage performance summary',
            event='performance_summary',
            stage_timings=self.stage_timings,
            total_duration_seconds=total_time
        )


class ProgressTracker:
    """
    Progress tracker with time estimation.

    Features:
    - Progress percentage
    - Estimated time remaining
    - Items per second rate
    - Console progress bar
    """

    def __init__(
        self,
        total: int,
        description: str = "Processing",
        logger: Optional[StructuredLogger] = None,
        update_interval: int = 1000,
    ):
        self.total = total
        self.description = description
        self.logger = logger
        self.update_interval = update_interval

        self.current = 0
        self.start_time = time.time()
        self.last_update = 0

    def update(self, n: int = 1):
        """Update progress by n items."""
        self.current += n

        if self.current - self.last_update >= self.update_interval or self.current >= self.total:
            self._report_progress()
            self.last_update = self.current

    def _report_progress(self):
        """Report current progress."""
        elapsed = time.time() - self.start_time
        percentage = (self.current / self.total * 100) if self.total > 0 else 0
        rate = self.current / elapsed if elapsed > 0 else 0

        if self.current > 0 and self.current < self.total:
            eta_seconds = (self.total - self.current) / rate if rate > 0 else 0
            eta_str = self._format_time(eta_seconds)
            msg = f"{self.description}: {self.current}/{self.total} ({percentage:.1f}%) | {rate:.0f} items/s | ETA: {eta_str}"
        else:
            msg = f"{self.description}: {self.current}/{self.total} ({percentage:.1f}%) | {rate:.0f} items/s"

        if self.logger:
            self.logger.info(msg, progress=self.current, total=self.total, rate=rate)
        else:
            print(msg)

    def _format_time(self, seconds: float) -> str:
        """Format seconds as human-readable time."""
        if seconds < 60:
            return f"{seconds:.0f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}h"

    def finish(self):
        """Mark progress as complete."""
        self.current = self.total
        self._report_progress()


def setup_pipeline_logging(
    log_dir: Path,
    console_level: int = logging.INFO,
    file_level: int = logging.DEBUG,
) -> StructuredLogger:
    """
    Set up logging for the entire pipeline.

    Args:
        log_dir: Directory for log files
        console_level: Console logging level
        file_level: File logging level

    Returns:
        Configured StructuredLogger instance
    """
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    logger = StructuredLogger(
        name='pipeline',
        log_dir=log_dir,
        console_level=console_level,
        file_level=file_level,
        enable_json=True,
    )

    logger.info("=" * 60)
    logger.info("Protocol Reverse Engineering Pipeline")
    logger.info("=" * 60)
    logger.info(f"Log directory: {log_dir}")
    logger.info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)

    return logger


def setup_stage_logging(
    stage_name: str,
    log_dir: Path,
    console_level: int = logging.INFO,
) -> StructuredLogger:
    """
    Set up logging for a specific pipeline stage.

    Args:
        stage_name: Name of the stage (e.g., 'extract_messages')
        log_dir: Directory for log files
        console_level: Console logging level

    Returns:
        Configured StructuredLogger instance
    """
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    logger = StructuredLogger(
        name=stage_name,
        log_dir=log_dir,
        console_level=console_level,
        file_level=logging.DEBUG,
        enable_json=True,
    )

    return logger


# Convenience function for quick logging setup
def get_logger(name: str, log_dir: Optional[Path] = None) -> StructuredLogger:
    """Get a logger instance with optional file logging."""
    return StructuredLogger(
        name=name,
        log_dir=log_dir,
        console_level=logging.INFO,
        file_level=logging.DEBUG,
        enable_json=log_dir is not None,
    )
