"""Netzob 2.0 (Bossert et al.) on the sampled messages: Format.clusterByAlignment (UPGMA over Needleman-Wunsch
similarity, internal slick) at a fixed similarity threshold; each symbol's alignment fields give the per-message
boundaries, the symbols give the message-type clustering. Run with ~/.venvs/nemesys39.
usage: run_netzob.py [--min-eq 50] [--max-messages 500] [protocols...]"""
import argparse, os, sys, time, random
from netzob.all import Format, RawMessage
from common import PROTOCOLS, load_sample, write_preds

ap = argparse.ArgumentParser()
ap.add_argument('--min-eq', type=int, default=50)          # Netzob's default
ap.add_argument('--max-messages', type=int, default=500)   # pairwise alignment is quadratic
ap.add_argument('--tool-name', default='netzob')     # preds/<tool-name>/
ap.add_argument('protocols', nargs='*')
args = ap.parse_args()
tool = args.tool_name
for protocol in (args.protocols or PROTOCOLS):
    records = load_sample(protocol)
    if len(records) > args.max_messages:
        keep = set(random.Random(1).sample(range(len(records)), args.max_messages))
        records = [r for i, r in enumerate(records) if i in keep]
    raw = [RawMessage(bytes.fromhex(r['payload_hex'])) for r in records]
    start = time.time()
    symbols = Format.clusterByAlignment(raw, minEquivalence=args.min_eq, internalSlick=True)
    rows_by_id = {}
    for sid, symbol in enumerate(symbols):
        cells = symbol.getMessageCells(encoded=False)
        for message, fields in cells.items():
            offset, edges = 0, set()
            for value in fields:
                offset += len(value)
                edges.add(offset)
            rows_by_id[id(message)] = {'boundaries': sorted({0} | edges), 'cluster': sid}
    elapsed = time.time() - start
    rows = []
    for record, message in zip(records, raw):
        row = rows_by_id.get(id(message), {'boundaries': [], 'cluster': -1})
        rows.append({'msg_id': record['msg_id'], **row})
    write_preds(tool, protocol, rows, {'messages': len(rows), 'seconds': round(elapsed, 2), 'symbols': len(symbols),
                                       'min_equivalence': args.min_eq})
    print(f'{protocol:10s} {len(rows):5d} msgs {len(symbols):4d} symbols {elapsed:7.1f}s', flush=True)
