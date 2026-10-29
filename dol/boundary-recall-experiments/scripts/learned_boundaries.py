"""Leave-one-protocol-out test of a learned boundary scorer.

One row per (family, offset): statistics of the bytes on either side of the
candidate edge, computed over the family's messages. Label: the offset is a
true field edge in at least half of the family's messages that reach it.
A model trained on 13 protocols predicts the edges of the 14th, and the result
is scored per message with the benchmark scorer."""
import importlib.util, json, sys
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
ROOT=Path('/mnt/d/tez/practical/protocol_re'); B=ROOT/'dol/benchmark-14-protocols'; ANN=ROOT/'finetuning/cluster-free-dataset/annotations'
OUT=ROOT/'dol/boundary-recall-experiments'
spec=importlib.util.spec_from_file_location('bench',ROOT/'scripts/diagnostics/31_benchmark_message_boundaries.py'); bench=importlib.util.module_from_spec(spec); spec.loader.exec_module(bench)
PROTOS='modbus,hart_ip,zigbee,bacnet,powerlink,s7comm,mms,goose,dnp3,enip,cip,ethercat,opcua,iec104'.split(',')
MAXLEN=256; CAP=2000
def col_stats(M, lens):
    """Per-offset stats over a (n, MAXLEN) uint8 matrix with per-row lengths."""
    n=M.shape[0]; valid=np.arange(MAXLEN)[None,:]<lens[:,None]; cov=valid.mean(0)
    H=np.zeros(MAXLEN); distinct=np.zeros(MAXLEN); zero=np.zeros(MAXLEN); mean=np.zeros(MAXLEN); ascii_=np.zeros(MAXLEN); top=np.zeros(MAXLEN)
    for j in range(MAXLEN):
        v=M[valid[:,j],j]
        if v.size==0: continue
        c=np.bincount(v,minlength=256); p=c[c>0]/v.size
        H[j]=-(p*np.log2(p)).sum()/8; distinct[j]=min(1.0,(c>0).sum()/min(v.size,256)); zero[j]=c[0]/v.size; mean[j]=v.mean()/255
        ascii_[j]=c[32:127].sum()/v.size; top[j]=c.max()/v.size
    return valid,cov,H,distinct,zero,mean,ascii_,top
def family_rows(msgs):
    msgs=msgs[:CAP]; n=len(msgs); lens=np.array([min(len(m),MAXLEN) for m in msgs]); M=np.zeros((n,MAXLEN),dtype=np.uint8)
    for i,m in enumerate(msgs): M[i,:lens[i]]=np.frombuffer(m[:MAXLEN],dtype=np.uint8)
    valid,cov,H,distinct,zero,mean,ascii_,top=col_stats(M,lens)
    med=float(np.median(lens)); rows=[]; offs=[]
    g=lambda a,j:(a[j] if 0<=j<MAXLEN else 0.0)
    for i in range(1,int(lens.max())):
        both=valid[:,i]
        if both.sum()<max(3,0.05*n): break
        a=M[both,i-1]; b=M[both,i]
        change=float((a!=b).mean())
        # normalised mutual information between the two neighbouring bytes
        ja=np.bincount(a.astype(np.int32)*256+b,minlength=65536); pj=ja[ja>0]/a.size; hj=-(pj*np.log2(pj)).sum()/8
        mi=max(0.0,H[i-1]+H[i]-hj); nmi=mi/max(min(H[i-1],H[i]),1e-6) if min(H[i-1],H[i])>1e-6 else 0.0
        # does the 16-bit big/little-endian value behave like one number? (high byte ~constant, low byte varies)
        rows.append([H[i-1],H[i],H[i]-H[i-1],abs(H[i]-H[i-1]),g(H,i-2),g(H,i+1),distinct[i-1],distinct[i],top[i-1],top[i],
                     zero[i-1],zero[i],mean[i-1],mean[i],ascii_[i-1],ascii_[i],change,min(nmi,1.0),cov[i],cov[i]-g(cov,i+1),g(cov,i-1)-cov[i],
                     i%2==0,i%4==0,min(i,64)/64,i/max(med,1),float(H[i-1]<1e-9),float(H[i]<1e-9),np.log2(n)/15])
        offs.append(i)
    return np.array(rows,dtype=float),offs
data={}
for p in PROTOS:
    d=B/p/'data'; a={int(x['msg_id']):x['family_id'] for x in json.load(open(d/'02_family_assignments.json'))['assignments']}
    by=defaultdict(list)
    for m in bench._iter_jsonl(d/'01_messages.jsonl'):
        fam=a.get(int(m['msg_id']))
        if fam and fam!='noise': by[fam].append(bytes.fromhex(m['payload_hex']))
    votes=defaultdict(Counter); reach=defaultdict(Counter)
    for r in bench._iter_jsonl(ANN/f'{p}.jsonl'):
        fam=a.get(int(r['msg_id']))
        if fam is None: continue
        votes[fam].update(e for e in r['boundaries'][1:-1]); end=r['boundaries'][-1]
        reach[fam]['n']+=1
        for e in r['boundaries'][1:-1]: pass
    # reach count per offset = messages longer than offset
    fams={}
    for fam,msgs in by.items():
        X,offs=family_rows(msgs)
        if not len(offs): continue
        lens=np.array([len(m) for m in msgs]); y=np.array([votes[fam][o]>=0.5*max(1,(lens>o).sum()) for o in offs])
        fams[fam]=(X,offs,y,len(msgs))
    data[p]=fams; print(p,'families',len(fams),'rows',sum(len(v[1]) for v in fams.values()),'pos',int(sum(v[2].sum() for v in fams.values())),flush=True)
results={}
for held in PROTOS:
    Xtr=np.vstack([v[0] for p in PROTOS if p!=held for v in data[p].values()]); ytr=np.concatenate([v[2] for p in PROTOS if p!=held for v in data[p].values()])
    # every protocol counts equally, however many families/offsets it has
    wtr=np.concatenate([np.full(len(v[1]),1.0/sum(len(u[1]) for u in data[p].values())) for p in PROTOS if p!=held for v in data[p].values()])
    clf=HistGradientBoostingClassifier(max_iter=200,learning_rate=0.08,max_depth=4,random_state=0).fit(Xtr,ytr,sample_weight=wtr*len(wtr))
    fams={}
    for fam,(X,offs,y,n) in data[held].items():
        pr=clf.predict_proba(X)[:,1]
        fams[fam]={'field_hypotheses':[{'start':o,'length':0} for o,q in zip(offs,pr) if q>=0.5]}
    name='05_families.exp-learned-lopo.json'; json.dump(fams,open(B/held/'data'/name,'w'))
    results[held]=bench.score_protocol(B/held/'data',ANN/f'{held}.jsonl',name)
prev=json.load(open(OUT/'results-all14.json'))
print(f"\n{'protocol':10s} {'base F1':>8s} {'cap200':>8s} {'learned LOPO (P / R / F1)':>28s} {'ceiling':>8s}")
for p in PROTOS:
    r=results[p]; print(f"{p:10s} {prev[p]['base']['f1']:8.3f} {prev[p]['cap200']['f1']:8.3f} {r['precision']:10.2f} / {r['recall']:.2f} / {r['f1']:.3f} {prev[p]['oracle50']['f1']:8.3f}")
m=lambda k:sum(prev[p][k]['f1'] for p in PROTOS)/len(PROTOS)
print(f"{'macro F1':10s} {m('base'):8.3f} {m('cap200'):8.3f} {'':>19s}{sum(r['f1'] for r in results.values())/len(PROTOS):.3f} {m('oracle50'):8.3f}")
json.dump(results,open(OUT/'results-learned-lopo.json','w'),indent=1)
