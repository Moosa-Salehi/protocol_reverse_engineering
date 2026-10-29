"""For each '+'/'-' followed by a digit (in content-stream order), report whether the sign is drawn left of that
digit (correct for an LTR number) or right of it (reversed). usage: signcheck.py <pdf> [pages]"""
import sys, pymupdf
d = pymupdf.open(sys.argv[1]); pages = [int(x) - 1 for x in sys.argv[2:]] or range(len(d))
for i in pages:
    chars = []
    for b in d[i].get_text('rawdict')['blocks']:
        for l in b.get('lines', []):
            for s in l['spans']:
                for c in s['chars']:
                    chars.append((c['c'], c['bbox'][0], round(c['bbox'][1])))
    ok = bad = 0; ex = []
    for k, (c, x, y) in enumerate(chars):
        if c in '+-−' and k + 1 < len(chars) and chars[k + 1][0].isdigit() and chars[k + 1][2] == y:
            if x < chars[k + 1][1]: ok += 1
            else:
                bad += 1; ex.append(''.join(ch for ch, _, _ in chars[k:k + 6]))
    if ok or bad:
        print(f'page {i+1}: sign left of number {ok}, right of number {bad}', ex[:3])
