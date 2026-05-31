#!/usr/bin/env python3
"""
Test script to demonstrate the structured logging system.

This script shows all features of the logging system:
- Basic logging (debug, info, warning, error)
- Decision logging
- Metric logging
- Stage tracking with automatic timing
- Context tracking
- Progress tracking
- Performance summary
"""

from __future__ import annotations

import time
from pathlib import Path

from protocol_re.utils.logging import setup_stage_logging, ProgressTracker


def simulate_work(duration: float = 0.1):
    """Simulate some work."""
    time.sleep(duration)


def main():
    # Setup logging
    log_dir = Path("logs/test")
    logger = setup_stage_logging("logging_test", log_dir)

    logger.info("Starting logging system test")

    # Test basic logging levels
    with logger.stage("test_basic_logging"):
        logger.debug("This is a debug message (file only)")
        logger.info("This is an info message")
        logger.warning("This is a warning message")
        logger.error("This is an error message")

    # Test decision logging
    with logger.stage("test_decision_logging"):
        logger.decision(
            decision="Using HDBSCAN clustering",
            reason="Better for variable density clusters",
            min_cluster_size=50,
            eps=40.0,
        )

        logger.decision(
            decision="Fallback to raw_bytes mode",
            reason="Neural model not available",
            requested_mode="neural",
            effective_mode="raw_bytes",
        )

    # Test metric logging
    with logger.stage("test_metric_logging"):
        logger.metric("messages_processed", 10000, "messages")
        logger.metric("families_discovered", 11, "families")
        logger.metric("clustering_time", 2.5, "seconds")
        logger.metric("memory_usage", 512, "MB")

    # Test context tracking
    with logger.stage("test_context_tracking"):
        families = ["family_0", "family_1", "family_2"]

        for family_id in families:
            with logger.context(family_id=family_id):
                logger.info(f"Processing {family_id}")
                logger.metric("message_count", 1500, "messages")
                logger.metric("segments", 5, "segments")
                simulate_work(0.05)

    # Test progress tracking
    with logger.stage("test_progress_tracking"):
        items = list(range(100))
        progress = ProgressTracker(
            total=len(items),
            description="Processing items",
            logger=logger,
            update_interval=20,
        )

        for item in items:
            simulate_work(0.01)
            progress.update()

        progress.finish()

    # Test nested stages
    with logger.stage("test_nested_operations"):
        logger.info("Starting nested operations")

        with logger.stage("load_data"):
            logger.info("Loading data from disk")
            simulate_work(0.2)
            logger.metric("records_loaded", 5000, "records")

        with logger.stage("process_data"):
            logger.info("Processing data")
            simulate_work(0.3)
            logger.metric("records_processed", 5000, "records")

        with logger.stage("save_results"):
            logger.info("Saving results")
            simulate_work(0.1)
            logger.metric("records_saved", 5000, "records")

    # Test error handling
    with logger.stage("test_error_handling"):
        try:
            logger.info("Attempting risky operation")
            simulate_work(0.1)
            # Simulate an error
            if True:  # Would normally be some condition
                logger.warning("Risky operation succeeded, but with warnings")
        except Exception as e:
            logger.error(f"Operation failed: {e}")

    logger.info("Logging system test completed")

    # Print performance summary
    logger.log_stage_summary()

    print("\n" + "=" * 60)
    print("Test completed successfully!")
    print("=" * 60)
    print(f"\nLog files created in: {log_dir}")
    print(f"  - {log_dir / 'logging_test.log'} (human-readable)")
    print(f"  - {log_dir / 'logging_test.jsonl'} (structured JSON)")
    print("\nTry these commands to analyze the logs:")
    print(f"  # View all decisions:")
    print(f"  cat {log_dir}/logging_test.jsonl | jq 'select(.decision != null)'")
    print(f"\n  # View all metrics:")
    print(f"  cat {log_dir}/logging_test.jsonl | jq 'select(.metric_name != null)'")
    print(f"\n  # View stage timings:")
    print(f"  cat {log_dir}/logging_test.jsonl | jq 'select(.event == \"stage_complete\")'")
    print(f"\n  # View logs for a specific family:")
    print(f"  cat {log_dir}/logging_test.jsonl | jq 'select(.context.family_id == \"family_0\")'")


if __name__ == "__main__":
    main()
