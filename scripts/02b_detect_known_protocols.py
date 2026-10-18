#!/usr/bin/env python3
"""Stage 02b: separate known protocols (dissected by tshark) from unknown traffic in the input captures.

Writes the protocol inventory (JSON) with the known protocols and the unknown TCP/UDP groups (transport + server
port, each with the display filter that selects it), plus a Markdown and an HTML summary. main.py
(--detect-knowns, default on) then reverse-engineers each unknown group separately.
"""
from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from protocol_re.io import protocol_inventory as pinv  # noqa: E402
from protocol_re.utils.logging import setup_stage_logging  # noqa: E402

PCAP_SUFFIXES = {".pcap", ".pcapng", ".cap"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("pcap_input", type=Path, help="PCAP file or folder (searched recursively)")
    parser.add_argument("output_json", type=Path)
    parser.add_argument("--markdown", type=Path, help="Markdown summary path")
    parser.add_argument("--html", type=Path, help="HTML summary path")
    parser.add_argument("--treat-as-unknown", default="", help="Comma list of dissector names to reverse-engineer anyway")
    parser.add_argument("--treat-as-known", default="",
                        help="Comma list of dissector names or tcp/PORT, udp/PORT groups to exclude")
    parser.add_argument("--min-packets", type=int, default=20, help="Unknown groups with fewer payload packets are only reported")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--log-dir", default="logs")
    args = parser.parse_args()
    logger = setup_stage_logging("02b_detect_known_protocols", Path(args.log_dir))

    source = args.pcap_input
    pcaps = [source] if source.is_file() else sorted(p for p in source.rglob("*") if p.suffix.lower() in PCAP_SUFFIXES)
    logger.metric("pcap_files", len(pcaps), "files")
    if not pcaps:
        raise SystemExit(f"02b_detect_known_protocols: no PCAP files under {source}")

    with logger.stage("dissect_flows"):
        flows = []
        with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
            for result in pool.map(lambda p: pinv.flows_from_rows(p.name, pinv.tshark_rows(p)), pcaps):
                flows.extend(result)
        logger.metric("flows", len(flows), "flows")

    inv = pinv.build_inventory(flows, args.treat_as_unknown.split(","), args.treat_as_known.split(","), args.min_packets)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(inv.to_dict(), indent=2), encoding="utf-8")
    markdown = pinv.render_markdown(inv)
    if args.markdown:
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        args.markdown.write_text(markdown, encoding="utf-8")
    if args.html:
        args.html.parent.mkdir(parents=True, exist_ok=True)
        args.html.write_text(pinv.render_html(markdown), encoding="utf-8")

    todo = [g for g in inv.unknown_groups if g["reverse_engineer"]]
    print(f"[+] known protocols: {', '.join(f'{p} ({v['packets']} pkts)' for p, v in inv.known.items()) or 'none'}")
    print(f"[+] unknown groups: {len(inv.unknown_groups)} ({len(todo)} with >= {args.min_packets} payload packets): "
          + ", ".join(f"{g['transport']}/{g['port']} ({g['packets']} pkts)" for g in inv.unknown_groups[:10]))
    if inv.unknown_l2:
        print(f"[+] unknown layer-2 ethertypes (reported only): {', '.join(u['ethertype'] for u in inv.unknown_l2)}")
    logger.metric("known_protocols", len(inv.known), "protocols")
    logger.metric("unknown_groups", len(todo), "groups")


if __name__ == "__main__":
    main()
