#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from protocol_re.io.extract_payloads import (
    backfill_directions,
    infer_service_port,
    write_messages_from_pcaps_jsonl,
    write_messages_from_pcaps_tshark_jsonl,
)
from protocol_re.corpus.message_corpus import load_corpus_jsonl
from protocol_re.utils.logging import setup_stage_logging


def _backfill_direction_file(jsonl_path: str, service_port: int | None) -> tuple[int, int | None]:
    """Load the written corpus, fill in missing directions from ports, rewrite.

    Returns (number_updated, service_port_used). Rewrites the file only when at
    least one direction changed, preserving field order via the record schema."""
    import json

    records = load_corpus_jsonl(jsonl_path)
    if service_port is None:
        service_port = infer_service_port(records)
    updated = backfill_directions(records, service_port)
    if updated:
        with open(jsonl_path, "w", encoding="utf-8") as handle:
            for record in records:
                handle.write(json.dumps(record.to_dict(), sort_keys=True) + "\n")
    return updated, service_port


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract protocol payloads from PCAP files into a canonical JSONL corpus.")
    parser.add_argument("pcap_dir")
    parser.add_argument("output_jsonl")
    parser.add_argument(
        "--extraction-method",
        choices=["tshark", "tcp"],
        default="tshark",
        help="Use tshark display-filter extraction or legacy Scapy TCP port extraction.",
    )
    parser.add_argument("--service-port", type=int, help="Optional TCP port filter. If omitted, all TCP payloads are extracted.")
    parser.add_argument("--tshark-filter", help="TShark display filter for the target protocol, for example mbtcp or s7comm.")
    parser.add_argument(
        "--packets-dir",
        default="data/payload_extraction/packets",
        help="Directory for intermediate tshark packet metadata JSON files.",
    )
    parser.add_argument(
        "--payloads-dir",
        default="data/payload_extraction/payloads",
        help="Directory for intermediate carved payload JSON files.",
    )
    parser.add_argument("--tshark-workers", type=int, default=4, help="Maximum parallel TShark worker processes.")
    parser.add_argument("--save-field-spans", action="store_true",
                        help="Persist TShark raw field offsets in message metadata for cluster-free annotation.")
    parser.add_argument("--max-messages", type=int, help="Maximum number of messages to extract.")
    parser.add_argument(
        "--reassembly-mode",
        choices=["packet", "stream"],
        default="packet",
        help="Use packet payloads directly or reconstruct directional TCP streams first.",
    )
    parser.add_argument("--log-dir", default="logs", help="Directory for log files")
    args = parser.parse_args()

    # Setup logging
    logger = setup_stage_logging("03_extract_messages", Path(args.log_dir))

    logger.info(f"Extracting messages from {args.pcap_dir}")
    logger.decision(
        decision=f"Using {args.extraction_method} extraction method",
        reason="User configuration",
        tshark_filter=args.tshark_filter if args.extraction_method == "tshark" else None,
        service_port=args.service_port,
        max_messages=args.max_messages,
    )

    Path(args.output_jsonl).parent.mkdir(parents=True, exist_ok=True)

    with logger.stage("extract_messages"):
        if args.extraction_method == "tshark":
            if not args.tshark_filter:
                logger.error("--tshark-filter is required when --extraction-method tshark")
                raise SystemExit("--tshark-filter is required when --extraction-method tshark.")
            count = write_messages_from_pcaps_tshark_jsonl(
                args.pcap_dir,
                args.output_jsonl,
                tshark_filter=args.tshark_filter,
                packets_dir=args.packets_dir,
                payloads_dir=args.payloads_dir,
                service_port=args.service_port,
                max_messages=args.max_messages,
                max_workers=args.tshark_workers,
                save_field_spans=args.save_field_spans,
            )
        else:
            count = write_messages_from_pcaps_jsonl(
                args.pcap_dir,
                args.output_jsonl,
                service_port=args.service_port,
                reassembly_mode=args.reassembly_mode,
                max_messages=args.max_messages,
            )

        logger.metric("messages_extracted", count, "messages")
        logger.info(f"Extracted {count} messages")

    # Backfill request/response direction from ports when extraction left it
    # unknown (the common case: no --service-port was supplied). Direction is a
    # core family-signature component — without it a single opcode's short request
    # and variable-length response collapse into one family, fragmenting boundaries.
    with logger.stage("backfill_directions"):
        updated, inferred_port = _backfill_direction_file(args.output_jsonl, args.service_port)
        logger.metric("directions_backfilled", updated, "messages")
        if inferred_port is not None:
            logger.decision(
                decision=f"Inferred service port {inferred_port}",
                reason="Most-connected endpoint port; used to derive request/response direction",
                directions_backfilled=updated,
            )
            print(f"[+] Backfilled direction for {updated} messages (service port {inferred_port})")
        else:
            print("[i] No dominant service port found; direction left unknown")

    print(f"[+] Wrote {count} extracted messages to {args.output_jsonl}")

    # Log performance summary
    logger.log_stage_summary()


if __name__ == "__main__":
    main()
