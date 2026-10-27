# usage: python3 score.py results.jsonl   (run in the folder that holds the input .txt files used for the run)
# present items: correct if the model says found=true and all key strings appear in its answer/quote.
#   Items whose key strings are missing from the INPUT text itself (OCR/PDF damage) are counted separately as input_damaged.
# absent items: correct if found=false. found=true is a false positive.
# quotes: exact = whole quote is a contiguous piece of the input; sentence-level = each sentence is; near = a sentence matches >=90% of its characters in one run.
import json,sys,re,unicodedata,collections,difflib
def norm(s): return re.sub(r'\s+',' ',unicodedata.normalize('NFKC',s)).strip().lower()
def has(k,t): return k in t or k.replace(' ','') in t.replace(' ','')   # OCR often drops spaces ("4 mm" -> "4mm")
TRUTH={ # present: key strings that must appear in answer or quote; absent: None
 'S1':['253','dimethyl sulfoxide'],'S2':['three rats','retro-orbital','2, 3, and 4 weeks'],'S3':['465.4','97.1'],'S4':None,
 'K1':['apex','100'],'K2':['cotton','7 days'],'K3':None,'K4':None,'C1':None,'C2':['pubmed','embase'],
 'S5':['tiletamine','0.66','xylazine','0.43'],'S6':['8 rats','80%'],'S7':['4 mm','2 mm'],'S8':None,
 'K5':['20%','15%'],'K6':['thiopental','150 mg/kg'],'K7':['xylazine','6 mg/kg','ketamine','70 mg/kg'],'K8':None,
 'C3':['syrcle'],'C4':['prospero','crd42020209776']}
PAPER={'S':'song','K':'kaji','C':'chew'}
def fname(q,src,cond): return f"{PAPER[q[0]]}_{cond}.txt" if src=='xml' else f"{PAPER[q[0]]}_{src}_{cond}.txt"
rows=[json.loads(l) for l in open(sys.argv[1],encoding='utf-8')]
stat=collections.defaultdict(collections.Counter); cache={}
for r in rows:
    q,c,src=r['q'],r['cond'],r.get('src','xml'); fn=fname(q,src,c)
    if fn not in cache: cache[fn]=norm(open(fn,encoding='utf-8').read())
    text=cache[fn]; tag=(src,c)
    p=r['parsed'] or {}; found=bool(p.get('found')); raw_quote=p.get('quote') or ''; quote=norm(raw_quote)
    ans=norm((p.get('answer') or '')+' '+raw_quote); key=TRUTH[q]; s=stat[tag]; s['n']+=1
    if r['parsed'] is None: s['unparsable']+=1
    if found and quote:   # quotes attached to found=false are discarded, as the engine would
        s['quotes']+=1
        if quote in text: s['quotes_exact']+=1
        for sent in re.split(r'(?<=[.;?!])\s+(?=[A-Z\[])',raw_quote):
            ns=norm(sent)
            if len(ns)<15: continue
            s['sentences']+=1
            if ns in text: s['sentences_verbatim']+=1; s['sentences_near']+=1
            else:
                m=difflib.SequenceMatcher(None,ns,text,autojunk=False).find_longest_match(0,len(ns),0,len(text))
                if m.size/len(ns)>=0.9: s['sentences_near']+=1
                else: s['sentences_not_in_input']+=1; print('QUOTE NOT IN INPUT',tag,q,'|',ns[:100])
    if key is None:
        s['absent_n']+=1
        if not found: s['absent_correct']+=1
        else: s['absent_false_positive']+=1; print('FALSE POSITIVE',tag,q,'|',(p.get('answer') or '')[:120])
    else:
        if not all(has(k,text) for k in key): s['present_input_damaged']+=1; print('INPUT DAMAGED',tag,q,[k for k in key if not has(k,text)]); continue
        s['present_n']+=1
        if found and all(has(k,ans) for k in key): s['present_correct']+=1
        else: print('MISS',tag,q,'found=',found,'|',(p.get('answer') or '')[:120])
    s['sec']+=r['sec']; s['prompt_tokens']+=(r['usage'] or {}).get('prompt_tokens',0)
for tag,s in sorted(stat.items()): print(tag,dict(s))
