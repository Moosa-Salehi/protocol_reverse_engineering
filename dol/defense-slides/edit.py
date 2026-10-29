"""Text edits for the defense deck (exact <a:t> replacements, each must match once) and bar geometry on slide 8."""
import re
from xml.sax.saxutils import escape
D = 'unpacked/ppt/slides/'
def edit(f, pairs):
    x = open(D + f, encoding='utf-8').read()
    for old, new in pairs:
        o, n = f'<a:t>{escape(old)}</a:t>', f'<a:t>{escape(new)}</a:t>'
        assert x.count(o) == 1, (f, old, x.count(o)); x = x.replace(o, n)
    open(D + f, 'w', encoding='utf-8').write(x)

# slide 4: LLM layer
edit('slide4.xml', [('Naming, relation checks and documentation; every suggestion passes verification gates',
                     'Naming and documentation proposals behind verification gates; no measurable gain in our evaluation')])
# slide 7: metrics and baselines
edit('slide7.xml', [('Overall score (types, boundaries, semantics, relations) and per-message boundary F1',
                     'Overall score (types, boundaries, semantics, relations); per-message boundary F1 and exact-field F1'),
                    ('Plus three open-source tools on the same messages and four held-out protocols.',
                     'Plus three open-source tools, trivial and supervised baselines on the same messages, and four held-out protocols.')])
# slide 8: main results (rescored, truth-aligned evaluator)
vals = [('0.435', 0.454), ('0.478', 0.513), ('0.519', 0.590), ('0.533', 0.605), ('0.540', 0.620)]
x = open(D + 'slide8.xml', encoding='utf-8').read()
bars = re.findall(r'<a:off x="3251200" y="(\d+)"/><a:ext cx="(\d+)" cy="304800"/>', x)
assert len(bars) == 5
for (y, cx), (old, v) in zip(bars, vals):
    w = round(7620000 * v)
    x = x.replace(f'<a:off x="3251200" y="{y}"/><a:ext cx="{cx}" cy="304800"/>', f'<a:off x="3251200" y="{y}"/><a:ext cx="{w}" cy="304800"/>')
    m = re.search(r'<a:off x="(\d+)" y="(\d+)"/>(<a:ext cx="575882" cy="274320"/>(?:(?!</p:sp>).)*<a:t>' + re.escape(old) + '</a:t>)', x, flags=re.S)
    x = x[:m.start()] + f'<a:off x="{3251200 + w + 152400}" y="{m.group(2)}"/>' + m.group(3).replace(f'<a:t>{old}</a:t>', f'<a:t>{v:.3f}</a:t>') + x[m.end():]
open(D + 'slide8.xml', 'w', encoding='utf-8').write(x)
edit('slide8.xml', [(' +0.043, 95% CI [+0.010, +0.081], 9 protocols up, 3 down', ' +0.059, 95% CI [+0.024, +0.097], 9 protocols up, 2 down'),
                    (' +0.105, 95% CI [+0.051, +0.170], 11 up, 1 down', ' +0.166, 95% CI [+0.101, +0.235], 12 up, 0 down'),
                    ('8 · strict family-level evaluator; absolute scores are low by design',
                     '8 · strict family-level evaluator, fields compared at their wire offsets; five label seeds give 0.620–0.626 for 50 labels')])
# slide 19 (new, after 8): component ablation, from the three-card layout
edit('slide19.xml', [('MESSAGE-TYPE CLUSTERING · 13 MULTI-TYPE PROTOCOLS', 'COMPONENT ABLATION · OVERALL SCORE, 14 PROTOCOLS'),
                     ('Explicit type-field detection groups messages better than alignment', 'Family refinement matters most; most special-case detectors do not'),
                     ('Ours', 'Family refinement'), ('0.579', '−0.128'), ('V-measure · ARI 0.385', 'without it · 95% CI [−0.251, −0.017]'),
                     ('NetPlier', 'Neural encoder'), ('0.440', '−0.049'), ('V-measure · ARI 0.233 · clusters 9 of 13', 'structural features instead · CI [−0.090, −0.013]'),
                     ('Netzob', 'Hierarchical boundaries'), ('0.251', '−0.045'), ('V-measure · ARI 0.097', 'and −0.026 per-message F1 · 12 protocols down'),
                     ('Better than NetPlier on every protocol both cluster except POWERLINK (64 messages). NetPlier fails on broadcast layer-2 traffic and picks a wrong keyword on BACnet and MMS.',
                      'Also significant: zero-shot gate (−0.026) and correlation-id detection (−0.016). No significant mean effect: stacked-header anchor, periodic arrays, merging, length protection, opcode isolation, post-processors. TLV/BER handling matters only for GOOSE and MMS.'),
                     ('11 · against truth-file message types', '11 · default configuration minus one component; paired bootstrap over 14 protocols')])
# slide 10: exact-field F1
edit('slide10.xml', [(' [+0.089, +0.227]; with equal data (only the 500-message sample): +0.147 [+0.074, +0.218].',
                      ' [+0.089, +0.227]; with equal data: +0.147 [+0.074, +0.218]. Exact-field F1, which does not reward over-splitting: 0.377 vs 0.275 (every byte 0.271).')])
# slide 20 (new, after 10): few-shot vs supervised baselines, from the stat-box layout
edit('slide20.xml', [('EVALUATION METHODOLOGY', 'FEW-SHOT VS SUPERVISED BASELINES · PER-MESSAGE F1, SAME 50 LABELS'),
                     ('What counts as a field depends on the reference, and it can reverse a conclusion', 'Copying the nearest labelled message is as accurate as few-shot'),
                     ('0.834 · 0.731', '0.942 · 0.834'),
                     ('Few-shot F1 on the truth files vs on parser annotations: the same predictions.',
                      'Copy the nearest labelled message’s offsets vs few-shot family field lists (truth files); 0.732 vs 0.731 on parser annotations.'),
                     ('≈ 0.91', '0.934'),
                     ('A variant tuned to parser labels: excellent there, no significant gain on the truth files.',
                      'Few-shot per-message edges before the family lists: level with copying. On the held-out protocols copying reaches 0.997–1.000.'),
                     ('Recommendation:', 'Takeaway:'),
                     (' report boundary results with the reference convention, on more than one reference, with paired intervals over many protocols — not on Modbus alone.',
                      ' the lead over unsupervised tools comes from the labels; the few-shot mode turns them into a complete protocol model (families, fields, semantics, relations).')])
# slide 12: held-out
edit('slide12.xml', [('FOUR HELD-OUT PROTOCOLS · NEVER USED IN ANY DESIGN DECISION', 'FOUR HELD-OUT PROTOCOLS · NOT USED IN DEVELOPMENT'),
                     ('Rules alone are below the best tool on all four; on C37.118 they find no correct edge. DoIP and CN/IP were chosen after the design was frozen and run once.',
                      'Rules alone are below the best tool on all four. Copying the nearest labelled message reaches 0.997–1.000, so few-shot’s lead comes from the labels. DoIP and CN/IP were run once after the design was frozen; ADS was seen once in a rejected design option.')])
x = open(D + 'slide12.xml', encoding='utf-8').read()
t = [p for p in re.findall(r'<a:t>([^<]*)</a:t>', x) if 'generalizes' in p or 'level with' in p]
print('slide12 title runs:', t)
# slide 13: limits
edit('slide13.xml', [('Reference convention', 'Family discovery'),
                     ('On a plant Modbus capture the model splits register arrays the truth file keeps whole: 0.770 vs 0.884.',
                      'The largest remaining error: with perfect family matching, boundary F1 would rise from 0.470 to 0.635. Two-level type keys (S7comm, OPC UA) are merged.')])
# slide 14: LLM role
edit('slide14.xml', [('Role in the framework: naming, relation checks and documentation, always under evidence gates.',
                      'In the pipeline, under gates: the local model’s semantic labels change no score (right in 63 vs 10 disagreements, in-distribution); relation validation was not evaluated.')])
# slide 16: answers
edit('slide16.xml', [('Yes, with uneven quality: 0.971 on a single-device Modbus capture, 0.478 on average over 14 protocols, no per-protocol tuning.',
                      'Yes, with uneven quality: 0.971 on a single-device Modbus capture, 0.513 on average over 14 protocols; family discovery is the main remaining error.'),
                     ('The encoder gives very pure clusters (purity 0.999); its errors are splits, which type-field refinement repairs.',
                      'Very pure clusters (purity 0.999, in-sample); in the pipeline it adds 0.049 over structural features.'),
                     ('Few-shot: clearly yes, on the benchmark and on four unseen protocols. Zero-shot: yes on the benchmark, level with the tools on unseen ones.',
                      'Zero-shot: yes when gated (+0.059 over rules), level with the tools on unseen protocols. Few-shot: accurate, but copying the labels matches it on boundaries; its value is the full model.'),
                     ('Not for boundaries; useful for naming and checks, only behind evidence gates.',
                      'No measurable gain: no significant boundary gain, signs of memorisation, no score change under gates.'),
                     ('Many protocols, explicit reference conventions, paired intervals, and held-out protocols.',
                      'Many protocols, explicit reference conventions, paired intervals, trivial and supervised baselines, held-out protocols.')])
# slide 17: future work
edit('slide17.xml', [('Search relative to the detected header end; request/response constraints only among structurally valid candidates.',
                      'Two-level type keys: length and layout signals did not work; request/response determinism is the next candidate.')])
print('edits ok')
