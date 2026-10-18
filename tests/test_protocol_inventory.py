from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from protocol_re.io import protocol_inventory as pinv


def test_application_protocol_skips_generic_layers():
    assert pinv.application_protocol("eth:ethertype:ip:tcp:mbtcp:modbus") == "mbtcp"
    assert pinv.application_protocol("eth:ethertype:ip:tcp:data") == "unknown"
    assert pinv.application_protocol("eth:ethertype:ip:udp") == "unknown"
    assert pinv.application_protocol("eth:ethertype:goose") == "goose"
    assert pinv.application_protocol("eth:ethertype:ip:tcp:tcp.segments:tpkt:cotp:s7comm") == "tpkt"


def _row(stack, transport, stream, sport, dport, length, syn="0", ack="1", etype=""):
    tcp = transport == "tcp"
    return [stack, stream if tcp else "", "" if tcp else stream,
            str(sport) if tcp else "", str(dport) if tcp else "", "" if tcp else str(sport), "" if tcp else str(dport),
            str(length) if tcp else "", "" if tcp else str(length + 8), etype, syn, ack]


def test_flows_known_unknown_and_server_port():
    rows = [_row("eth:ethertype:ip:tcp", "tcp", "0", 51000, 502, 0, syn="1", ack="0")]
    rows += [_row("eth:ethertype:ip:tcp:mbtcp:modbus", "tcp", "0", 51000, 502, 12) for _ in range(5)]
    rows += [_row("eth:ethertype:ip:tcp:data", "tcp", "1", 20000, 52000, 30) for _ in range(30)]
    rows += [_row("eth:ethertype:ip:udp:data", "udp", "0", 61000, 48898, 40) for _ in range(3)]
    rows += [_row("eth:ethertype:data", "l2", "", 0, 0, 0, etype="0x88b5") for _ in range(4)]
    flows = {(f.transport, f.key): f for f in pinv.flows_from_rows("cap.pcap", rows)}
    assert flows[("tcp", "0")].app == "mbtcp" and flows[("tcp", "0")].server_port == 502
    assert flows[("tcp", "1")].app is None and flows[("tcp", "1")].server_port == 20000
    assert flows[("udp", "0")].server_port == 48898
    assert ("l2", "0x88b5") in flows

    inv = pinv.build_inventory(list(flows.values()), min_packets=20)
    assert inv.known == {"mbtcp": {"flows": 1, "packets": 5, "files": 1}}
    groups = {g["name"]: g for g in inv.unknown_groups}
    assert groups["tcp_20000"]["reverse_engineer"] and groups["tcp_20000"]["filter"] == "tcp.port == 20000"
    assert not groups["udp_48898"]["reverse_engineer"]          # 3 packets < min_packets
    assert inv.unknown_l2 == [{"ethertype": "0x88b5", "packets": 4, "files": 1}]


def test_overrides():
    rows = [_row("eth:ethertype:ip:tcp:mbtcp:modbus", "tcp", "0", 51000, 502, 12) for _ in range(25)]
    rows += [_row("eth:ethertype:ip:tcp:data", "tcp", "1", 20000, 52000, 30) for _ in range(25)]
    flows = pinv.flows_from_rows("cap.pcap", rows)
    inv = pinv.build_inventory(flows, treat_as_unknown=["mbtcp"], treat_as_known=["tcp/20000"])
    assert "tcp/20000" in inv.known
    groups = {g["name"]: g for g in inv.unknown_groups}
    assert groups["tcp_502"]["forced_from"] == {"mbtcp": 25} and groups["tcp_502"]["reverse_engineer"]


def test_render_links_reports():
    rows = [_row("eth:ethertype:ip:tcp:data", "tcp", "1", 20000, 52000, 30) for _ in range(25)]
    inv = pinv.build_inventory(pinv.flows_from_rows("cap.pcap", rows))
    md = pinv.render_markdown(inv, {"tcp_20000": "unknown/tcp_20000/protocol_report.html"})
    assert "[report](unknown/tcp_20000/protocol_report.html)" in md
    html = pinv.render_html(md)
    assert '<a href="unknown/tcp_20000/protocol_report.html">report</a>' in html and "<table>" in html
