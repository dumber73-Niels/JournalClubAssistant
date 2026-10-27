# usage: python3 score.py results.jsonl   (run where <paper>_full.txt / _methods.txt exist)
import json,sys,re,unicodedata,collections
def norm(s): return re.sub(r'\s+',' ',unicodedata.normalize('NFKC',s)).strip().lower()
TRUTH={ # present: key strings that must appear in answer or quote; absent: None
 'S1':['253','dimethyl sulfoxide'],'S2':['three rats','retro-orbital','2, 3, and 4 weeks'],'S3':['465.4','97.1'],'S4':None,
 'K1':['apex','100'],'K2':['cotton','7 days'],'K3':None,'K4':None,'C1':None,'C2':['pubmed','embase']}
PAPER={'S':'song','K':'kaji','C':'chew'}
rows=[json.loads(l) for l in open(sys.argv[1],encoding='utf-8')]
stat=collections.defaultdict(lambda: collections.Counter())
for r in rows:
    q,c=r['q'],r['cond']; text=norm(open(f"{PAPER[q[0]]}_{c}.txt",encoding='utf-8').read())
    p=r['parsed'] or {}; found=bool(p.get('found')); quote=norm(p.get('quote') or ''); ans=norm((p.get('answer') or '')+' '+(p.get('quote') or ''))
    key=TRUTH[q]; s=stat[c]; s['n']+=1
    if r['parsed'] is None: s['unparsable']+=1
    if quote:
        s['quotes']+=1
        if quote in text: s['quotes_verbatim']+=1
    if key is None:
        s['absent_n']+=1
        if not found: s['absent_correct']+=1
        else: s['absent_false_positive']+=1; print('FALSE POSITIVE',c,q,'|',(p.get('answer') or '')[:120])
    else:
        s['present_n']+=1
        if found and all(k in ans for k in key): s['present_correct']+=1
        else: print('MISS',c,q,'found=',found,'|',(p.get('answer') or '')[:120])
    s['sec']+=r['sec']; s['prompt_tokens']+=(r['usage'] or {}).get('prompt_tokens',0)
for c,s in stat.items(): print(c,dict(s))
