"""Protocol inventory of a capture set: which flows tshark dissects as known protocols, and which are unknown.

Each payload-carrying packet gets an application protocol from tshark's ``frame.protocols`` stack: the first layer
above the transport (TCP/UDP) or above the Ethernet type for layer-2 frames, skipping generic layers (``data``,
``tcp.segments``, malformed markers, ...). A flow (one TCP or UDP stream of one capture file; one ethertype for
layer-2 frames) is *known* when most of its payload packets carry the same dissected protocol, otherwise *unknown*.
Unknown TCP/UDP flows are grouped by transport and server port, the unit the reverse-engineering pipeline runs on.

``treat_as_unknown`` lists dissector names that are reverse-engineered anyway; ``treat_as_known`` lists dissector
names or ``tcp/PORT`` / ``udp/PORT`` groups that are excluded even when tshark cannot dissect them.
"""
from __future__ import annotations

import subprocess
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Sequence, Set, Tuple

# layers that say nothing about the application protocol
GENERIC_LAYERS = {
    "data", "tcp.segments", "udp.segments", "_ws.malformed", "_ws.short", "_ws.expert", "malformed", "short",
    "ip.data", "ipv6.data", "frame", "eth", "ethertype", "vlan", "sll", "sll2", "ip", "ipv6", "tcp", "udp",
    "padding", "eth.trailer", "_ws.unreassembled", "ipv6.hopopts", "llc", "mpls", "pppoes", "ppp",
}
TRANSPORTS = ("tcp", "udp")
EPHEMERAL_PORT_START = 49152

FIELDS = ("frame.protocols", "tcp.stream", "udp.stream", "tcp.srcport", "tcp.dstport", "udp.srcport", "udp.dstport",
          "tcp.len", "udp.length", "eth.type", "tcp.flags.syn", "tcp.flags.ack")


@dataclass
class Flow:
    file: str
    transport: str                  # tcp, udp or l2
    key: str                        # stream index, or ethertype for layer 2
    ports: Tuple[int, int] = (0, 0)
    server_port: int = 0
    packets: int = 0
    apps: Counter = field(default_factory=Counter)

    @property
    def app(self) -> Optional[str]:
        """Dissected protocol of most of the flow's payload packets, else None (unknown)."""
        if not self.apps:
            return None
        name, count = self.apps.most_common(1)[0]
        return name if name != "unknown" and count >= 0.5 * self.packets else None


def application_protocol(stack: str) -> str:
    """First non-generic layer above the transport (or the ethertype for layer 2), else 'unknown'."""
    layers = [x for x in stack.split(":") if x]
    if not layers:
        return "unknown"
    start = 0
    for i, name in enumerate(layers):
        if name in TRANSPORTS:
            start = i + 1
            break
    else:
        for i, name in enumerate(layers):
            if name in ("ethertype", "vlan", "llc", "sll", "sll2"):
                start = i + 1
    for name in layers[start:]:
        if name not in GENERIC_LAYERS:
            return name
    return "unknown"


def _int(value: str) -> int:
    try:
        return int(value.split(",")[0]) if value else 0
    except ValueError:
        return int(value.split(",")[0], 16) if value.startswith("0x") else 0


def server_port(a: int, b: int, syn_dst: Optional[int] = None) -> int:
    """The service side of a flow: the destination of its first SYN, else the non-ephemeral / lower port."""
    if syn_dst:
        return syn_dst
    if (a < EPHEMERAL_PORT_START) != (b < EPHEMERAL_PORT_START):
        return a if a < EPHEMERAL_PORT_START else b
    return min(a, b)


def tshark_rows(pcap: Path, tshark: str = "tshark") -> Iterator[List[str]]:
    cmd = [tshark, "-n", "-r", str(pcap), "-T", "fields", "-E", "separator=\t", "-E", "occurrence=f"]
    for name in FIELDS:
        cmd += ["-e", name]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, encoding="utf-8", errors="replace")
    assert proc.stdout is not None
    for line in proc.stdout:
        row = line.rstrip("\n").split("\t")
        yield row + [""] * (len(FIELDS) - len(row))
    proc.wait()


def flows_from_rows(file: str, rows: Iterable[Sequence[str]]) -> List[Flow]:
    flows: Dict[Tuple[str, str], Flow] = {}
    syn_dst: Dict[Tuple[str, str], int] = {}
    for row in rows:
        stack, tstream, ustream, tsp, tdp, usp, udp_, tlen, ulen, etype, syn, ack = row[:12]
        layers = stack.split(":")
        if "tcp" in layers and tstream:
            key = ("tcp", tstream)
            a, b = _int(tsp), _int(tdp)
            if syn == "1" and ack != "1":
                syn_dst.setdefault(key, b)
            payload = _int(tlen) > 0
        elif "udp" in layers and ustream:
            key = ("udp", ustream)
            a, b = _int(usp), _int(udp_)
            payload = _int(ulen) > 8
        elif "ip" not in layers and "ipv6" not in layers and etype:
            key = ("l2", etype.split(",")[0])
            a = b = 0
            payload = True
        else:
            continue
        flow = flows.setdefault(key, Flow(file=file, transport=key[0], key=key[1], ports=(a, b)))
        if payload:
            flow.packets += 1
            flow.apps[application_protocol(stack)] += 1
    for key, flow in flows.items():
        if flow.transport in TRANSPORTS:
            flow.server_port = server_port(*flow.ports, syn_dst.get(key))
    return [f for f in flows.values() if f.packets]


@dataclass
class Inventory:
    known: Dict[str, Dict[str, int]]                  # protocol -> {flows, packets, files}
    unknown_groups: List[Dict[str, object]]           # {name, transport, port, flows, packets, files, filter, reverse_engineer}
    unknown_l2: List[Dict[str, object]]               # {ethertype, packets, files}

    def to_dict(self) -> Dict[str, object]:
        return {"known": self.known, "unknown_groups": self.unknown_groups, "unknown_layer2": self.unknown_l2}


def build_inventory(flows: Sequence[Flow], treat_as_unknown: Iterable[str] = (), treat_as_known: Iterable[str] = (),
                    min_packets: int = 20) -> Inventory:
    force_unknown = {x.strip().lower() for x in treat_as_unknown if x.strip()}
    force_known = {x.strip().lower() for x in treat_as_known if x.strip()}
    known: Dict[str, Dict[str, object]] = defaultdict(lambda: {"flows": 0, "packets": 0, "files": set()})
    groups: Dict[Tuple[str, int], Dict[str, object]] = defaultdict(lambda: {"flows": 0, "packets": 0, "files": set(), "dissected_as": Counter()})
    l2: Dict[str, Dict[str, object]] = defaultdict(lambda: {"packets": 0, "files": set()})
    for f in flows:
        app = f.app
        group_name = f"{f.transport}/{f.server_port}"
        if app and app.lower() in force_unknown:
            app_is_known = False
        elif app:
            app_is_known = True
        else:
            app_is_known = group_name in force_known
            app = group_name if app_is_known else None
        if app_is_known:
            k = known[app]
            k["flows"] += 1; k["packets"] += f.packets; k["files"].add(f.file)
        elif f.transport in TRANSPORTS:
            g = groups[(f.transport, f.server_port)]
            g["flows"] += 1; g["packets"] += f.packets; g["files"].add(f.file)
            if f.app:
                g["dissected_as"][f.app] += f.packets
        else:
            u = l2[f.key]
            u["packets"] += f.packets; u["files"].add(f.file)
    known_out = {p: {"flows": v["flows"], "packets": v["packets"], "files": len(v["files"])}
                 for p, v in sorted(known.items(), key=lambda kv: -kv[1]["packets"])}
    group_out = []
    for (transport, port), v in sorted(groups.items(), key=lambda kv: -kv[1]["packets"]):
        group_out.append({
            "name": f"{transport}_{port}", "transport": transport, "port": port, "flows": v["flows"],
            "packets": v["packets"], "files": len(v["files"]), "filter": f"{transport}.port == {port}",
            "forced_from": dict(v["dissected_as"]), "reverse_engineer": v["packets"] >= min_packets,
        })
    l2_out = [{"ethertype": k, "packets": v["packets"], "files": len(v["files"])}
              for k, v in sorted(l2.items(), key=lambda kv: -kv[1]["packets"])]
    return Inventory(known_out, group_out, l2_out)


def inventory_from_pcaps(pcaps: Sequence[Path], treat_as_unknown: Iterable[str] = (), treat_as_known: Iterable[str] = (),
                         min_packets: int = 20, tshark: str = "tshark") -> Inventory:
    flows: List[Flow] = []
    for pcap in pcaps:
        flows.extend(flows_from_rows(pcap.name, tshark_rows(pcap, tshark)))
    return build_inventory(flows, treat_as_unknown, treat_as_known, min_packets)


def render_markdown(inv: Inventory, report_links: Optional[Dict[str, str]] = None) -> str:
    report_links = report_links or {}
    lines = ["# Protocol inventory", "",
             "Known protocols (dissected by tshark) are excluded from reverse engineering; unknown traffic is grouped by",
             "transport and server port and reverse-engineered per group.", "", "## Known protocols", ""]
    if inv.known:
        lines += ["| protocol | flows | packets | files |", "|---|---|---|---|"]
        lines += [f"| {p} | {v['flows']} | {v['packets']} | {v['files']} |" for p, v in inv.known.items()]
    else:
        lines.append("None.")
    lines += ["", "## Unknown traffic (TCP/UDP)", ""]
    if inv.unknown_groups:
        lines += ["| group | flows | packets | files | reverse-engineered | report |", "|---|---|---|---|---|---|"]
        for g in inv.unknown_groups:
            forced = f" (forced from {', '.join(g['forced_from'])})" if g["forced_from"] else ""
            link = report_links.get(g["name"], "")
            lines.append(f"| {g['transport']}/{g['port']}{forced} | {g['flows']} | {g['packets']} | {g['files']} | "
                         f"{'yes' if g['reverse_engineer'] else 'no (too few packets)'} | {f'[report]({link})' if link else ''} |")
    else:
        lines.append("None.")
    if inv.unknown_l2:
        lines += ["", "## Unknown layer-2 traffic (not reverse-engineered in this version)", "",
                  "| ethertype | packets | files |", "|---|---|---|"]
        lines += [f"| {u['ethertype']} | {u['packets']} | {u['files']} |" for u in inv.unknown_l2]
    return "\n".join(lines) + "\n"


def render_html(markdown_text: str) -> str:
    """Minimal self-contained HTML rendering of the inventory Markdown (tables, headings, links)."""
    import html
    import re
    out, in_table = [], False
    for line in markdown_text.splitlines():
        if line.startswith("|"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            if all(set(c) <= {"-"} for c in cells):
                continue
            if not in_table:
                out.append("<table>"); in_table = True
                out.append("<tr>" + "".join(f"<th>{html.escape(c)}</th>" for c in cells) + "</tr>")
                continue
            row = []
            for c in cells:
                m = re.fullmatch(r"\[(.+)\]\((.+)\)", c)
                row.append(f'<td><a href="{html.escape(m.group(2))}">{html.escape(m.group(1))}</a></td>' if m else f"<td>{html.escape(c)}</td>")
            out.append("<tr>" + "".join(row) + "</tr>")
            continue
        if in_table:
            out.append("</table>"); in_table = False
        if line.startswith("## "):
            out.append(f"<h2>{html.escape(line[3:])}</h2>")
        elif line.startswith("# "):
            out.append(f"<h1>{html.escape(line[2:])}</h1>")
        elif line.strip():
            out.append(f"<p>{html.escape(line)}</p>")
    if in_table:
        out.append("</table>")
    style = ("body{font-family:system-ui,sans-serif;margin:2rem;max-width:960px}table{border-collapse:collapse;margin:1rem 0}"
             "td,th{border:1px solid #ccc;padding:4px 10px;text-align:left}th{background:#f3f3f3}")
    return f"<!doctype html><html><head><meta charset='utf-8'><title>Protocol inventory</title><style>{style}</style></head><body>{''.join(out)}</body></html>\n"
