"""Protocol survey of the raw captures: tshark protocol hierarchy per file, frame counts per protocol summed over
files, plus which files contain each protocol. Output: dol/heldout-search/survey.json."""
import json, os, re, subprocess, sys
from collections import defaultdict
ROOT = '/mnt/d/tez/practical/traffic'
OUT = '/mnt/d/tez/practical/protocol_re/dol/heldout-search/survey.json'
frames = defaultdict(int); files = defaultdict(list); done = 0
paths = [os.path.join(dp, f) for d in ('caps', 'pcap_iman', 'pcaps', 'pcaps2', 'sajjad') for dp, _, fs in os.walk(os.path.join(ROOT, d))
         for f in fs if f.lower().endswith(('.pcap', '.pcapng', '.cap'))]
for path in paths:
    try:
        out = subprocess.run(['tshark', '-r', path, '-qz', 'io,phs'], capture_output=True, text=True, timeout=180).stdout
    except subprocess.TimeoutExpired:
        continue
    seen = set()
    for line in out.splitlines():
        m = re.match(r'\s*([\w.\-]+)\s+frames:(\d+)', line)
        if m and m.group(1) not in seen:
            seen.add(m.group(1)); frames[m.group(1)] += int(m.group(2)); files[m.group(1)].append(path)
    done += 1
    if done % 50 == 0:
        print(done, 'of', len(paths), flush=True)
        json.dump({'frames': frames, 'files': files, 'done': done}, open(OUT, 'w'))
json.dump({'frames': frames, 'files': files, 'done': done}, open(OUT, 'w'))
print('DONE', done)
