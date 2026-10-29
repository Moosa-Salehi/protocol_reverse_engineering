"""Generic CRC-16 block detector: [header h][crc] ([block k][crc])* [last block][crc], CRCs verified with a
catalogue of common CRC-16 parameterisations and both byte orders."""
from functools import lru_cache

# (name, poly, init, reflected, xorout)
CATALOGUE = [('ARC', 0x8005, 0x0000, True, 0x0000), ('MODBUS', 0x8005, 0xFFFF, True, 0x0000),
             ('USB', 0x8005, 0xFFFF, True, 0xFFFF), ('CCITT-FALSE', 0x1021, 0xFFFF, False, 0x0000),
             ('XMODEM', 0x1021, 0x0000, False, 0x0000), ('KERMIT', 0x1021, 0x0000, True, 0x0000),
             ('X25', 0x1021, 0xFFFF, True, 0xFFFF), ('DNP', 0x3D65, 0x0000, True, 0xFFFF),
             ('EN13757', 0x3D65, 0x0000, False, 0xFFFF), ('BUYPASS', 0x8005, 0x0000, False, 0x0000),
             ('DECT-X', 0x0589, 0x0000, False, 0x0000), ('GENIBUS', 0x1021, 0xFFFF, False, 0xFFFF)]


def _refl(x, w):
    return int(f'{x:0{w}b}'[::-1], 2)


@lru_cache(maxsize=None)
def _table(poly, reflected):
    t = []
    for i in range(256):
        if reflected:
            c, p = i, _refl(poly, 16)
            for _ in range(8):
                c = (c >> 1) ^ p if c & 1 else c >> 1
        else:
            c = i << 8
            for _ in range(8):
                c = ((c << 1) ^ poly) & 0xFFFF if c & 0x8000 else (c << 1) & 0xFFFF
        t.append(c)
    return t


def crc16(data, spec):
    _, poly, init, refl, xorout = spec
    t = _table(poly, refl)
    c = init
    for x in data:
        if refl:
            c = (c >> 8) ^ t[(c ^ x) & 0xFF]
        else:
            c = ((c << 8) & 0xFFFF) ^ t[((c >> 8) ^ x) & 0xFF]
    return c ^ xorout


def _ok(b, a, z, spec, order):
    return z + 2 <= len(b) and int.from_bytes(b[z:z + 2], order) == crc16(b[a:z], spec)


def find_layout(b, max_header=32, blocks=(16, 8, 32, 64)):
    """Returns (h, k, spec, order) if the message is a CRC-blocked frame with >= 2 verified CRCs."""
    for spec in CATALOGUE:
        for order in ('little', 'big'):
            for h in range(2, min(max_header, len(b) - 2)):
                if not _ok(b, 0, h, spec, order):
                    continue
                for k in blocks:
                    pos, n = h + 2, 1
                    good = True
                    while pos < len(b):
                        z = min(pos + k, len(b) - 2)
                        if z <= pos or not _ok(b, pos, z, spec, order):
                            good = False
                            break
                        pos, n = z + 2, n + 1
                    if good and pos == len(b) and n >= 2:
                        return h, k, spec, order
                if len(b) == h + 2:
                    return None
    return None


def block_edges(b, layout):
    h, k, spec, order = layout
    edges, spans = {h, h + 2}, []
    pos = h + 2
    while pos < len(b):
        z = min(pos + k, len(b) - 2)
        edges.update((pos, z, z + 2)); spans.append((pos, z))
        pos = z + 2
    return edges, spans
