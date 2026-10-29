"""Random binary-protocol generator with exact field boundaries.

Each synthetic protocol has a shared header and several message types keyed by
an opcode. Fields are drawn from the kinds seen in industrial protocols:
constants, transaction ids, length fields, unit/address ids, opcodes, counters,
timestamps, small and wide integers in either byte order, enums, flags,
byte-count-prefixed arrays, strings, opaque blobs, padding and checksums.
Per-type "device behaviour" makes some value fields constant inside one type,
as a polling master does.

generate_protocol(rng) -> list of (messages, boundaries_per_message, header_len)
per message type; boundaries are the true interior field edges of each message.
"""
import numpy as np


def _int_bytes(value, width, little):
    return int(value).to_bytes(width, 'little' if little else 'big')


class Field:
    """One field: draws its bytes for message k of a type. May be variable-width."""

    def __init__(self, kind, width, rng, little):
        self.kind, self.width, self.little = kind, width, little
        self.rng = rng
        r = rng
        if kind == 'const':
            self.value = bytes(r.integers(0, 256, width)) if r.random() < 0.6 else bytes(width)
        elif kind == 'enum':
            self.values = r.choice(256 ** min(width, 2), size=int(r.integers(2, 9)), replace=False)
            self.p = r.dirichlet(np.ones(len(self.values)) * r.uniform(0.3, 3))
        elif kind == 'smallint':
            self.hi = int(r.choice([8, 16, 64, 200, 1000, 5000])) % (256 ** width) or 200
            self.lo = int(r.integers(0, max(1, self.hi // 4)))
        elif kind == 'wideint':
            pass
        elif kind == 'counter':
            self.start = int(r.integers(0, 256 ** width))
            self.step = int(r.choice([1, 1, 1, 2, 10]))
        elif kind == 'timestamp':
            self.start = int(r.integers(1_500_000_000, 1_800_000_000)) % (256 ** width)
            self.step = float(r.uniform(0.01, 5))
        elif kind == 'address':
            self.values = r.integers(0, min(256 ** width, 40000), size=int(r.integers(1, 30)))
        elif kind == 'flags':
            self.mask = int(r.integers(1, 256 ** width))
        elif kind == 'string':
            self.words = [bytes(r.choice(list(b'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_/$.'), size=width)) for _ in range(int(r.integers(1, 6)))]
        elif kind == 'array':  # count byte + count * unit bytes
            self.unit = int(r.choice([1, 2, 2, 4]))
            self.counts = r.integers(1, int(r.choice([3, 4, 8, 12])), size=int(r.integers(1, 4)))
            self.count_width = width
            self.count_is_bytes = bool(r.random() < 0.6)

    def emit(self, k):
        r, w = self.rng, self.width
        kind = self.kind
        if kind == 'const':
            return [self.value]
        if kind == 'enum':
            return [_int_bytes(r.choice(self.values, p=self.p) % (256 ** w), w, self.little)]
        if kind == 'smallint':
            return [_int_bytes(r.integers(self.lo, self.hi + 1), w, self.little)]
        if kind == 'wideint' or kind == 'checksum':
            return [bytes(r.integers(0, 256, w))]
        if kind == 'counter':
            return [_int_bytes((self.start + k * self.step) % (256 ** w), w, self.little)]
        if kind == 'timestamp':
            return [_int_bytes(int(self.start + k * self.step) % (256 ** w), w, self.little)]
        if kind == 'address':
            return [_int_bytes(r.choice(self.values) % (256 ** w), w, self.little)]
        if kind == 'flags':
            return [_int_bytes(int(r.integers(0, 256 ** w)) & self.mask, w, self.little)]
        if kind == 'string':
            return [self.words[int(r.integers(0, len(self.words)))]]
        if kind == 'blob':
            return [bytes(r.integers(0, 256, w))]
        if kind == 'pad':
            return [bytes(w)]
        if kind == 'array':
            count = int(r.choice(self.counts))
            head = _int_bytes(count * self.unit if self.count_is_bytes else count, self.count_width, self.little)
            # each array element is its own field, as dissectors report them
            return [head] + [_small_or_wide(r, self.unit, self.little) for _ in range(count)]
        raise ValueError(kind)


def _small_or_wide(r, width, little):
    if width == 1 or r.random() < 0.5:
        return _int_bytes(r.integers(0, min(256 ** width, 2000)), width, little)
    return bytes(r.integers(0, 256, width))


BODY_KINDS = [
    ('smallint', (1, 1, 2, 2, 4)), ('wideint', (2, 2, 4)), ('enum', (1, 1, 1, 2)), ('address', (1, 2, 2, 4)),
    ('flags', (1, 1, 2)), ('counter', (1, 2, 4)), ('timestamp', (4, 8)), ('string', (4, 6, 8, 12)),
    ('blob', (3, 4, 6, 8)), ('pad', (1, 1, 2, 3)), ('const', (1, 1, 2, 4)), ('array', (1, 1, 2)),
]
# Weighted towards 1-2 byte fields: in the 14 real protocols about a quarter of
# all offsets are field edges, and 60-95% of fields are 1 or 2 bytes wide.
BODY_WEIGHTS = np.array([7, 1.5, 6, 4, 3, 1, 0.6, 0.5, 0.5, 1.5, 4, 0.8], dtype=float)
BODY_WEIGHTS /= BODY_WEIGHTS.sum()


def generate_protocol(rng, max_messages=600):
    little = bool(rng.random() < 0.3)
    endian = lambda: little if rng.random() < 0.85 else not little

    # ---- shared header -------------------------------------------------------
    header = []
    length_slot = None
    choices = ['magic', 'version', 'txn', 'length', 'unit', 'flags', 'seq', 'reserved', 'timestamp']
    picked = [c for c in choices if rng.random() < {'magic': 0.5, 'version': 0.3, 'txn': 0.5, 'length': 0.7, 'unit': 0.5,
                                                   'flags': 0.3, 'seq': 0.25, 'reserved': 0.35, 'timestamp': 0.1}[c]]
    rng.shuffle(picked)
    if 'magic' in picked:  # a magic number leads
        picked.remove('magic')
        picked.insert(0, 'magic')
    for name in picked:
        if name == 'magic':
            header.append(Field('const', int(rng.choice([1, 2, 2, 4])), rng, little))
            header[-1].value = bytes(rng.integers(1, 256, header[-1].width))
        elif name == 'version':
            header.append(Field('const', 1, rng, little))
        elif name == 'txn':
            kind = 'counter' if rng.random() < 0.6 else 'wideint'
            header.append(Field(kind, int(rng.choice([1, 2, 2, 4])), rng, endian()))
        elif name == 'length':
            length_slot = len(header)
            header.append(('length', int(rng.choice([1, 2, 2, 4])), endian(), str(rng.choice(['total', 'after', 'remaining']))))
        elif name == 'unit':
            header.append(Field('address', int(rng.choice([1, 1, 2])), rng, endian()))
        elif name == 'flags':
            header.append(Field('flags', 1, rng, little))
        elif name == 'seq':
            header.append(Field('counter', int(rng.choice([1, 2])), rng, endian()))
        elif name == 'reserved':
            header.append(Field('pad', int(rng.choice([1, 2, 2, 4])), rng, little))
        elif name == 'timestamp':
            header.append(Field('timestamp', int(rng.choice([4, 8])), rng, endian()))
    opcode_width = int(rng.choice([1, 1, 1, 2]))
    opcode_little = endian()
    has_checksum = rng.random() < 0.25
    checksum_width = int(rng.choice([1, 2, 2, 4]))

    # ---- message types -------------------------------------------------------
    n_types = int(rng.integers(2, 11))
    opcodes = rng.choice(256 if opcode_width == 1 else 4096, size=n_types, replace=False)
    types = []
    for opcode in opcodes:
        body = []
        for _ in range(int(rng.integers(1, 15))):
            kind, widths = BODY_KINDS[int(rng.choice(len(BODY_KINDS), p=BODY_WEIGHTS))]
            field = Field(kind, int(rng.choice(widths)), rng, endian())
            # device behaviour: a polling master sends the same operand every time
            if kind in ('smallint', 'address', 'enum', 'flags') and rng.random() < 0.35:
                frozen = field.emit(0)
                field.emit = lambda k, frozen=frozen: frozen
            body.append(field)
        count = int(min(max_messages, max(12, rng.lognormal(5, 1.2))))
        messages, edges = [], []
        for k in range(count):
            parts = []
            for index, item in enumerate(header):
                parts.append(None if index == length_slot else item.emit(k)[0])
            header_len_placeholder = len(parts)
            parts.append(_int_bytes(opcode, opcode_width, opcode_little))
            for field in body:
                parts.extend(field.emit(k))
            if has_checksum:
                parts.append(bytes(rng.integers(0, 256, checksum_width)))
            if length_slot is not None:
                _, lw, ll, relation = header[length_slot]
                total = sum(len(x) for x in parts if x is not None) + lw
                before = sum(len(x) for x in parts[:length_slot]) + lw
                value = {'total': total, 'after': total - before, 'remaining': total - before + lw}[relation]
                parts[length_slot] = _int_bytes(value % (256 ** lw), lw, ll)
            message = b''.join(parts)
            position, cuts = 0, []
            for part in parts[:-1]:
                position += len(part)
                cuts.append(position)
            messages.append(message)
            edges.append(cuts)
        header_len = sum(len(x) for x in parts[:header_len_placeholder])
        types.append((messages, edges, header_len))
    return types
