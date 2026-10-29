"""Random binary protocol generator (v3: capture model with few devices, polled request instances and
per-instance static values; v1/v2 kept as gen_v1.py / gen_v2.py) with exact per-message field boundaries (synthetic pretraining, idea 1).

A protocol is a stack of 1-3 header layers followed by an opcode-dependent body. Each layer draws its fields
from magic / version / length (total, after-field or rest-of-layer; 1-4 bytes, either byte order) / transaction /
sequence / unit / flags / reserved / timestamp; the last layer carries the opcode, and responses use a derived
opcode (op | 0x80, op + 1, or the same op with a direction flag). Bodies are sequences of elements: fixed integers
(enumerations, counters, slow-moving process values as scaled ints or float32, wide random values, zero padding),
fixed-width or length-prefixed strings, length-prefixed blobs, counted arrays of 1-3-field items, TLV chains
(1/2-byte tag and length), and an optional trailing CRC-16. Every primitive is one truth field, the convention of
dol/accuracy-push/annotations-truthconv (boundaries are field start offsets, 0 included).

Usage as a module: generate_protocol(rng) -> list of dicts(payload: bytes, boundaries: list[int], type: str, direction).
"""
from __future__ import annotations

import math
import random
import struct
from typing import Any, Dict, List, Optional, Tuple

WORDS = [b"temp", b"pump", b"valve", b"motor", b"line", b"tank", b"PLC", b"node", b"sensor", b"alarm", b"setpoint",
         b"station", b"device", b"input", b"output", b"status", b"level", b"flow", b"press", b"zone"]


def ib(v: int, w: int, little: bool) -> bytes:
    return int(v % (256 ** w)).to_bytes(w, "little" if little else "big")


def crc16(data: bytes) -> int:
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(8):
            crc = (crc >> 1) ^ 0xA001 if crc & 1 else crc >> 1
    return crc


def small_value(r: random.Random, w: int) -> int:
    """Field values in captures are mostly small (0, 1, small codes, short addresses)."""
    x = r.random()
    if x < 0.5:
        return r.randrange(0, 16)
    if x < 0.8:
        return r.randrange(0, 256)
    return r.randrange(0, min(256 ** w, 1 << 16))


ZIPF = [1.0 / (i + 1) ** 1.5 for i in range(256)]
T = [0.0]   # current capture time (seconds), advanced by generate_protocol
PLE = [False]  # protocol-wide byte-order preference (real protocols are mostly consistent)


def pick_le(r: random.Random) -> bool:
    return r.random() < (0.9 if PLE[0] else 0.1)

ROLE_OF_KIND = {"enum": None, "counter": "sequence_number", "pv_int": "payload", "pv_float": "payload", "wide": "payload",
                "zero": "constant", "small": None, "bool": "flags", "address": "address", "status": "status",
                "time": "timestamp"}


class Scalar:
    """A fixed-width integer-like field with a value distribution and per-protocol state."""

    def __init__(self, r: random.Random, kind: str = None, width: int = None, little: bool = None):
        self.kind = kind or r.choice(["enum", "enum", "enum", "counter", "pv_int", "pv_int", "pv_float", "wide", "zero", "zero", "small", "bool"])
        if self.kind == "pv_float":
            width = 4
        if self.kind == "time":
            width = width or r.choice([4, 8])
        self.rate = r.choice([1, 1000, 1000000])
        self.w = width or r.choice({"enum": [1, 1, 2], "counter": [1, 2, 4], "pv_int": [2, 2, 4], "wide": [2, 4, 4, 8],
                                    "zero": [1, 2, 4], "small": [1, 2], "bool": [1], "address": [1, 2, 2, 4],
                                    "status": [1, 1, 2], "time": [4, 8]}[self.kind])
        self.little = pick_le(r) if little is None else little
        self.vals = [small_value(r, self.w) for _ in range(r.randint(2, 6))]
        if self.kind == "address":
            lo = small_value(r, self.w) // 2
            self.vals = sorted({lo + r.randrange(0, 200) for _ in range(r.randint(3, 60))})
        self.base, self.amp, self.period = r.uniform(-500, 500), r.uniform(1, 200), r.uniform(20, 400)
        self.scale = r.choice([1, 10, 100])
        self.state = r.randrange(0, 256 ** min(self.w, 2))

    def emit(self, r: random.Random, k: int, rs: Optional[random.Random] = None) -> bytes:
        """r: per-message randomness (dynamic kinds); rs: per-instance randomness (static kinds), default r."""
        rs = rs or r
        w, le = self.w, self.little
        if self.kind == "enum":
            return ib(rs.choices(self.vals, ZIPF[:len(self.vals)])[0], w, le)
        if self.kind == "counter":
            self.state += 1
            return ib(self.state, w, le)
        if self.kind == "pv_int":
            v = (self.base + self.amp * math.sin(k / self.period) + r.gauss(0, self.amp * 0.02)) * self.scale
            return ib(int(v), w, le)
        if self.kind == "pv_float":
            v = self.base + self.amp * math.sin(k / self.period) + r.gauss(0, self.amp * 0.02)
            return struct.pack("<f" if le else ">f", v)
        if self.kind == "wide":
            return bytes(rs.randrange(256) for _ in range(w))
        if self.kind == "address":
            return ib(rs.choice(self.vals), w, le)
        if self.kind == "status":
            return ib(0 if r.random() < 0.85 else r.choice(self.vals), w, le)
        if self.kind == "time":
            return ib(int(T[0] * self.rate), w, le)
        if self.kind == "zero":
            return bytes(w)
        if self.kind == "small":
            return ib(rs.randrange(0, 40), w, le)
        return ib(rs.randrange(2), w, le)


Field = Tuple[bytes, ...]  # one primitive = one bytes object; an element emits a list of primitives


class Element:
    """A body element: emits a list of primitive byte strings (each one truth field)."""

    def __init__(self, r: random.Random, depth: int = 0):
        kinds = ["scalar"] * 6 + ["address", "quantity", "fstring", "lpstring", "blob", "array", "tlv", "ber", "items"]
        if depth:
            kinds = ["scalar"] * 6 + ["fstring", "lpstring"]
        self.kind = r.choice(kinds)
        self.little = pick_le(r)
        if self.kind == "scalar":
            self.s = Scalar(r)
        elif self.kind == "address":
            self.s = Scalar(r, "address")
        elif self.kind == "quantity":
            self.qw = r.choice([1, 2, 2]); self.qmax = r.choice([8, 125, 2000])
        elif self.kind == "fstring":
            self.w = r.choice([4, 8, 16, 32])
        elif self.kind in ("lpstring", "blob"):
            self.lw = r.choice([1, 1, 2])
            self.maxlen = r.choice([8, 16, 32, 64])
        elif self.kind == "array":
            self.cw = r.choice([1, 1, 2])
            self.items = [Scalar(r, kind=r.choice(["enum", "pv_int", "pv_float", "small", "wide"])) for _ in range(r.randint(1, 3))]
            self.maxn = r.choice([4, 8, 16])
            self.fixed_n = r.randint(1, self.maxn) if r.random() < 0.3 else None
        elif self.kind == "ber":
            self.tags = [r.choice([0x80, 0x81, 0x82, 0x83, 0x84, 0x85, 0x86, 0x87, 0x02, 0x04, 0x0a, 0x1a, 0x91])
                         for _ in range(r.randint(2, 6))]
            self.ctag = r.choice([0x30, 0xa0, 0xa1, 0xa2, 0xa3])
            self.nested = r.random() < 0.6
        elif self.kind == "items":
            self.types = {r.randrange(1, 0x200): [Scalar(r, kind=r.choice(["address", "pv_int", "wide", "enum"]))
                                                   for _ in range(r.randint(1, 3))] for _ in range(r.randint(2, 4))}
        elif self.kind == "tlv":
            self.tw, self.lw = r.choice([(1, 1), (1, 1), (1, 2), (2, 2)])
            self.tags = {r.randrange(1, 256 ** self.tw if self.tw == 1 else 4096): r.choice(["int", "str", "blob"])
                         for _ in range(r.randint(2, 6))}
            self.maxn = r.choice([2, 4, 6])

    def emit(self, r: random.Random, k: int, rs: Optional[random.Random] = None) -> List[Tuple[bytes, Optional[str]]]:
        rs = rs or r
        if self.kind in ("scalar", "address"):
            return [(self.s.emit(r, k, rs), ROLE_OF_KIND[self.s.kind])]
        if self.kind == "quantity":
            return [(ib(rs.randint(1, self.qmax), self.qw, self.little), "quantity")]
        if self.kind == "fstring":
            s = rs.choice(WORDS) + str(rs.randrange(100)).encode()
            return [((s + bytes(self.w))[: self.w], "payload")]
        if self.kind == "lpstring":
            s = (rs.choice(WORDS) + b"_" + rs.choice(WORDS))[: self.maxlen]
            return [(ib(len(s), self.lw, self.little), "length"), (s, "payload")]
        if self.kind == "blob":
            b = bytes(rs.randrange(256) for _ in range(rs.randint(2, self.maxlen)))
            return [(ib(len(b), self.lw, self.little), "length"), (b, "payload")]
        if self.kind == "array":
            n = self.fixed_n or rs.randint(1, self.maxn)
            out = [(ib(n, self.cw, self.little), "quantity")]
            for _ in range(n):
                out += [(it.emit(r, k, rs), ROLE_OF_KIND[it.kind]) for it in self.items]
            return out
        if self.kind == "ber":
            def berlen(n):
                if n < 128 and rs.random() < 0.9:
                    return bytes([n])
                return bytes([0x81, n]) if n < 256 else bytes([0x82, n >> 8, n & 0xFF])
            inner = []
            for tag in rs.sample(self.tags, rs.randint(1, len(self.tags))):
                v = (ib(rs.randrange(1 << 16), rs.choice([1, 2, 4]), False) if tag in (0x02, 0x0a, 0x80, 0x85)
                     else (rs.choice(WORDS) if tag in (0x1a, 0x81, 0x83) else bytes(rs.randrange(256) for _ in range(rs.randint(1, 10)))))
                inner += [(bytes([tag]), None), (berlen(len(v)), "length"), (v, "payload")]
            if not self.nested:
                return inner
            n = sum(len(x) for x, _ in inner)
            return [(bytes([self.ctag]), None), (berlen(n), "length")] + inner
        if self.kind == "items":
            chosen = [rs.choice(list(self.types)) for _ in range(rs.randint(1, 3))]
            out = [(ib(len(chosen), 2, self.little), "quantity")]
            for t in chosen:
                data = [(sc.emit(r, k, rs), ROLE_OF_KIND[sc.kind]) for sc in self.types[t]]
                out += [(ib(t, 2, self.little), None), (ib(sum(len(x) for x, _ in data), 2, self.little), "length")] + data
            return out
        out = []
        for _ in range(rs.randint(1, self.maxn)):
            tag = rs.choice(list(self.tags))
            t = self.tags[tag]
            v = (ib(rs.randrange(1 << 16), rs.choice([1, 2, 4]), self.little) if t == "int"
                 else (rs.choice(WORDS) if t == "str" else bytes(rs.randrange(256) for _ in range(rs.randint(1, 12)))))
            out += [(ib(tag, self.tw, False), None), (ib(len(v), self.lw, self.little), "length"), (v, "payload")]
        return out


class Layer:
    """A header layer; the last layer holds the opcode. Length fields are filled after the payload is built."""

    def __init__(self, r: random.Random, last: bool):
        self.little = pick_le(r)
        p = {"magic": 0.4, "version": 0.3, "length": 0.75, "txn": 0.4, "seq": 0.2, "unit": 0.45, "flags": 0.35,
             "reserved": 0.2, "timestamp": 0.15}
        names = [n for n in p if r.random() < p[n]]
        r.shuffle(names)
        if "length" in names and r.random() < 0.6:   # length fields usually sit early in the header
            names.remove("length"); names.insert(r.randint(0, min(2, len(names))), "length")
        if last:
            names.insert(r.randint(max(0, len(names) - 2), len(names)), "opcode")
        self.fields: List[Tuple[str, Any]] = []
        for n in names:
            if n == "magic":
                w = r.choice([1, 2, 2, 4]); self.fields.append((n, bytes(r.randrange(256) for _ in range(w))))
            elif n == "version":
                self.fields.append((n, Scalar(r, "enum", 1)))
            elif n == "length":
                self.fields.append((n, (r.choice([1, 2, 2, 4]), pick_le(r), r.choice(["total", "after", "layer"]),
                                        r.choice([0, 0, 0, 2, -2]))))
            elif n in ("txn", "seq"):
                self.fields.append((n, Scalar(r, "counter" if r.random() < 0.7 else "wide", r.choice([1, 2, 2, 4]), self.little)))
            elif n == "unit":
                self.fields.append((n, Scalar(r, "enum", r.choice([1, 1, 2]), self.little)))
            elif n == "flags":
                self.fields.append((n, Scalar(r, "enum", 1)))
            elif n == "reserved":
                self.fields.append((n, Scalar(r, "zero", r.choice([1, 2]))))
            elif n == "timestamp":
                self.fields.append((n, Scalar(r, "time", r.choice([4, 8]), self.little)))
            elif n == "opcode":
                self.fields.append((n, r.choice([1, 1, 1, 2])))


def generate_protocol(r: random.Random, n_messages: int = 400) -> List[Dict[str, Any]]:
    PLE[0] = r.random() < 0.4
    layers = [Layer(r, i == n - 1) for n in [r.choice([1, 1, 2, 2, 3])] for i in range(n)]
    opw = next(v for name, v in layers[-1].fields if name == "opcode")
    n_ops = r.randint(2, 10)
    ops = r.sample(range(1, 0x7F), n_ops)
    resp_rule = r.choice(["or80", "plus1", "same"])
    bodies = {}
    for op in ops:
        for d in ("req", "resp"):
            n_el = r.choice([0, 1, 2, 3, 4, 6, 8]) if d == "req" else r.choice([0, 1, 2, 3, 5, 8, 12, 16])
            bodies[(op, d)] = [Element(r) for _ in range(n_el)]
    has_crc = r.random() < 0.12
    msgs = []
    weights = [r.random() ** 2 + 0.05 for _ in ops]
    n_sessions = r.choice([1, 2, 4, 8, 16, 24])
    k = 0
    T[0] = r.uniform(1e6, 2e9)
    header_role = {"magic": "constant", "version": None, "txn": "transaction_id", "seq": "sequence_number",
                   "unit": "unit_id", "flags": "flags", "reserved": "constant", "timestamp": "timestamp"}
    seed_base = r.randrange(1 << 30)
    n_dev = r.choice([1, 2, 3, 5, 8, 12])
    pool = {op: r.choice([1, 1, 2, 3, 5, 10, 30]) for op in ops}   # request instances polled repeatedly
    while len(msgs) < n_messages:
        op = r.choices(ops, weights)[0]
        si = r.randrange(n_sessions)
        sess, dev = f"s{si}", si % n_dev
        j = r.choices(range(pool[op]), ZIPF[:pool[op]])[0]
        req_index = None
        for d in ("req", "resp"):
            rs_body = random.Random(seed_base * 7919 + op * 131 + j * 17 + dev * 3 + (d == "resp"))
            rs_hdr = random.Random(seed_base * 31 + dev * 1009 + (d == "resp"))
            if d == "resp" and r.random() < 0.15:
                continue
            T[0] += r.expovariate(20.0)
            code = op if d == "req" else {"or80": op | 0x80, "plus1": op + 1, "same": op}[resp_rule]
            prims: List[Tuple[bytes, Optional[str]]] = [p for el in bodies[(op, d)] for p in el.emit(r, k, rs_body)]
            # build layers inside-out so outer length fields can count inner bytes
            for layer in reversed(layers):
                fl: List[Tuple[bytes, Optional[str]]] = []
                len_slot = None
                for name, v in layer.fields:
                    if name == "magic":
                        fl.append((v, "constant"))
                    elif name == "length":
                        len_slot = len(fl); fl.append((b"", "length"))
                    elif name == "opcode":
                        fl.append((ib(code, v, False), "opcode"))
                    elif name == "flags" and resp_rule == "same":
                        fl.append((bytes([0x01 if d == "req" else 0x81]), "flags"))
                    else:
                        fl.append((v.emit(r, k, rs_hdr), header_role[name]))
                if len_slot is not None:
                    w, le, rel, adj = layer.fields[len_slot][1]
                    rest = sum(len(x) for x, _ in fl[len_slot + 1:]) + sum(len(x) for x, _ in prims)
                    before = sum(len(x) for x, _ in fl[:len_slot]) + w
                    val = {"total": before + rest, "after": rest, "layer": rest}[rel] + adj
                    fl[len_slot] = (ib(max(0, val), w, le), "length")
                prims = fl + prims
            if has_crc:
                c = crc16(b"".join(x for x, _ in prims))
                prims = prims + [(ib(c, 2, True), "checksum")]
            payload, edges, roles, off = b"", [], [], 0
            for p, role in prims:
                if not p:
                    continue
                edges.append(off); roles.append(role); off += len(p); payload += p
            m = {"payload": payload, "boundaries": edges, "roles": roles, "type": f"op{code:x}_{d}",
                 "direction": "client_to_server" if d == "req" else "server_to_client",
                 "session": sess, "t": T[0], "pair": None}
            if d == "req":
                req_index = len(msgs)
            elif req_index is not None:
                m["pair"] = req_index
            msgs.append(m)
            k += 1
    return msgs[:n_messages]


if __name__ == "__main__":
    import sys
    r = random.Random(int(sys.argv[1]) if len(sys.argv) > 1 else 0)
    for m in generate_protocol(r, 12):
        print(m["type"], m["payload"].hex(), m["boundaries"])
