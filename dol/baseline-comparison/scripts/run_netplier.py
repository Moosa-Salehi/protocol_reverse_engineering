"""NetPlier (Ye et al., NDSS 2021) on the sampled messages: MAFFT multiple sequence alignment, keyword-candidate
fields from the alignment, constraint observations and probabilistic keyword inference, as in NetPlier's main.py.
Boundaries: the alignment fields mapped back to each message; message types: the inferred keyword value per
direction (cluster_by_kw_inferred). Run with ~/.venvs/netplier39 (netzob 1.0.2, pgmpy 0.1.9).
usage: run_netplier.py [--max-messages 500] [--mode ginsi] [protocols...]"""
import argparse, collections, logging, os, random, sys, time, traceback
sys.path.insert(0, os.path.expanduser('~/.local/baseline-tools/NetPlier/netplier'))
os.environ['PATH'] = os.path.expanduser('~/.local/baseline-tools/bin') + os.pathsep + os.environ['PATH']
from netzob.all import RawMessage
from netplier import NetPlier
from alignment import Alignment
from processing import Processing
from clustering import Clustering
from common import HERE, PROTOCOLS, load_sample, write_preds

ap = argparse.ArgumentParser()
ap.add_argument('--max-messages', type=int, default=500)
ap.add_argument('--mode', default='ginsi')
ap.add_argument('protocols', nargs='*')
args = ap.parse_args()
logging.getLogger().setLevel(logging.WARNING)

for protocol in (args.protocols or PROTOCOLS):
    records = load_sample(protocol)
    if len(records) > args.max_messages:   # same subset as run_netzob.py
        keep = set(random.Random(1).sample(range(len(records)), args.max_messages))
        records = [r for i, r in enumerate(records) if i in keep]
    records.sort(key=lambda r: (r['timestamp'], r['msg_id']))
    messages = [RawMessage(bytes.fromhex(r['payload_hex']), date=r['timestamp'],
                           source=f"{r['src_ip']}:{r['src_port']}", destination=f"{r['dst_ip']}:{r['dst_port']}")
                for r in records]
    # direction as NetPlier derives it from sessions: the first sender of a session is the client (0)
    first_sender = {}
    for r in records:
        first_sender.setdefault(r['session_id'], (r['src_ip'], r['src_port']))
    # (the capture's TCP/UDP direction when it is known)
    directions = [{'client_to_server': 0, 'server_to_client': 1}.get(
        r.get('direction'), 0 if first_sender[r['session_id']] == (r['src_ip'], r['src_port']) else 1) for r in records]
    work = os.path.join(HERE, 'work', 'netplier', protocol)
    start = time.time()
    status = 'ok'
    try:
        netplier = NetPlier(messages=messages, direction_list=directions, output_dir=work, mode=args.mode)
        fid_inferred = netplier.execute()
        aligned = Alignment.get_messages_aligned(netplier.messages, os.path.join(work, Alignment.FILENAME_OUTPUT_ONELINE))
        clustering = Clustering(fields=netplier.fields, protocol_type=None)
        keywords = clustering.cluster_by_kw_inferred(fid_inferred, aligned)
        # field ends in alignment columns (hex characters)
        columns, pos = [], 0
        for field in netplier.fields:
            pos += field.domain.dataType.size[1] // 8
            columns.append(pos)
        rows = []
        for record, message, direction, keyword in zip(records, aligned, directions, keywords):
            line = message.data
            edges = {0}
            for col in columns:
                edges.add(sum(1 for ch in line[:col] if ch != '-') // 2)
            rows.append({'msg_id': record['msg_id'], 'boundaries': sorted(edges),
                         'cluster': f"{direction}:{keyword.replace('-', '')}"})
    except Exception as error:
        # keyword inference failed (e.g. no responses in a broadcast capture): keep NetPlier's alignment fields
        # as its format output when the alignment finished; no message-type clustering then
        status = f'keyword inference failed: {type(error).__name__}: {error}'
        traceback.print_exc()
        fid_inferred = None
        oneline = os.path.join(work, Alignment.FILENAME_OUTPUT_ONELINE)
        info = os.path.join(work, Alignment.FILENAME_FIELDS_INFO)
        rows = [{'msg_id': r['msg_id'], 'boundaries': []} for r in records]
        if os.path.isfile(oneline) and os.path.isfile(info):
            lines = open(oneline).read().splitlines()
            columns, pos = [], 0
            for line in open(info):
                pos += int(line.split()[2]) // 8
                columns.append(pos)
            rows = [{'msg_id': r['msg_id'], 'boundaries': sorted({0} | {sum(1 for ch in line[:col] if ch != '-') // 2 for col in columns})}
                    for r, line in zip(records, lines)]
            status += ' (alignment fields kept)'
        else:
            status = f'alignment failed: {type(error).__name__}: {error}'
    elapsed = time.time() - start
    write_preds('netplier', protocol, rows, {'messages': len(rows), 'seconds': round(elapsed, 2), 'status': status,
                                             'keyword_fields': fid_inferred, 'mode': args.mode,
                                             'directions': dict(collections.Counter(directions))})
    print(f'{protocol:10s} {len(rows):5d} msgs {elapsed:8.1f}s {status[:120]}', flush=True)
