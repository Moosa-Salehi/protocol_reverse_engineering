"""NEMESYS (Kleber et al., WOOT 2018) on the sampled messages: bit-congruence-delta segmentation (sigma 0.6) plus the
original refinements, exactly as nemesys.py in vs-uulm/nemesys runs it, fed from memory instead of a PCAP.
Run with ~/.venvs/nemesys39 (netzob 2.0.0)."""
import os, sys, time
sys.path.insert(0, os.path.expanduser('~/.local/baseline-tools/nemesys/src'))
from netzob.Model.Vocabulary.Messages.RawMessage import RawMessage
from nemere.utils.loader import BaseLoader
from nemere.inference.segmentHandler import bcDeltaGaussMessageSegmentation, refinements
from common import PROTOCOLS, load_sample, write_preds

SIGMA = 0.6
for protocol in (sys.argv[1:] or PROTOCOLS):
    records = load_sample(protocol)
    raw = [RawMessage(bytes.fromhex(r['payload_hex']), date=r.get('timestamp'), source=str(r.get('src_ip')),
                      destination=str(r.get('dst_ip'))) for r in records]
    start = time.time()
    specimens = BaseLoader(raw)
    segmented = bcDeltaGaussMessageSegmentation(specimens, SIGMA)
    refined = refinements(segmented)
    elapsed = time.time() - start
    by_message = {id(segments[0].message): segments for segments in refined if segments}
    rows = []
    for record, message in zip(records, raw):
        segments = by_message.get(id(message), [])
        edges = sorted({s.offset for s in segments} | {s.offset + s.length for s in segments})
        rows.append({'msg_id': record['msg_id'], 'boundaries': edges})
    write_preds('nemesys', protocol, rows, {'messages': len(rows), 'seconds': round(elapsed, 2), 'sigma': SIGMA})
    print(f'{protocol:10s} {len(rows):5d} msgs {elapsed:7.1f}s', flush=True)
