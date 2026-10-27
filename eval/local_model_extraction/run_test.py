# usage: python3 run_test.py BASE_URL MODEL [OUTFILE]
# e.g.   python3 run_test.py http://localhost:11434/v1 gemma4:e4b results.jsonl
# Reads <paper>_full.txt / <paper>_methods.txt (from make_inputs.py), asks each question per paper and condition,
# writes one JSON line per call: question id, condition, raw reply, parsed JSON, wall seconds, usage.
import json,sys,time,urllib.request
BASE,MODEL=sys.argv[1].rstrip('/'),sys.argv[2]
OUT=sys.argv[3] if len(sys.argv)>3 else 'results.jsonl'
Q=[
 ('S1','song','What amount of Irosustat was mixed into the feed (per kg of feed), and in what solvent was it dissolved?'),
 ('S2','song','For measuring the systemic CS level in serum: how many rats were sampled, by what blood collection route, and at which time points?'),
 ('S3','song','Which precursor and product ion m/z values were monitored for CS in the mass spectrometry analysis?'),
 ('S4','song','Does the text report that body weight or daily feed intake of the rats was measured or recorded during the Irosustat feeding period?'),
 ('K1','kaji','How is the percentage of bone in the furcation (PBF) calculated, and how are the boundaries of the furcation area (FA) and the bone area (BA) defined?'),
 ('K2','kaji','How was periodontitis induced: what ligature material was used and when was the ligature removed?'),
 ('K3','kaji','Does the text define the junctional epithelium length (JEL), meaning a measured distance from the cementoenamel junction to the apical end of the junctional epithelium?'),
 ('K4','kaji','Does the text define a bone crest length (BCL) measurement, meaning the distance from the cementoenamel junction to the alveolar bone crest?'),
 ('C1','chew','Does the text describe a protocol for inducing periodontitis by placing a ligature around a natural tooth of a rat (not around an implant), including the ligature material and the tooth used?'),
 ('C2','chew','Which electronic databases were searched for the systematic review?'),
]
SYS=('You extract information from a scientific article. Use ONLY the article text given by the user. '
 'Reply with a single JSON object and nothing else: {"found": true or false, "answer": "short answer in your own words", '
 '"quote": "the exact sentence or sentences copied character-for-character from the article that support the answer"}. '
 'If the article does not contain the information, reply {"found": false, "answer": "", "quote": ""}. Never invent text. Do not quote text that is not in the article.')
def call(text,q):
    body={'model':MODEL,'temperature':0,'max_tokens':6000,'messages':[
      {'role':'system','content':SYS},{'role':'user','content':'ARTICLE TEXT:\n'+text+'\n\nQUESTION: '+q}]}
    t=time.time()
    r=urllib.request.urlopen(urllib.request.Request(BASE+'/chat/completions',json.dumps(body).encode(),{'Content-Type':'application/json','Authorization':'Bearer x'}),timeout=3600)
    d=json.load(r); return d,time.time()-t
def parse(s):
    s=s.strip()
    if s.startswith('```'): s=s.strip('`').lstrip('json').strip()
    a,b=s.find('{'),s.rfind('}')
    try: return json.loads(s[a:b+1])
    except Exception: return None
with open(OUT,'a',encoding='utf-8') as f:
    for cond in ('methods','full'):
        for qid,paper,q in Q:
            text=open(f'{paper}_{cond}.txt',encoding='utf-8').read()
            try: d,sec=call(text,q); msg=d['choices'][0]['message']; raw=msg.get('content') or ''
            except Exception as e: d,sec,raw={},0,'ERROR '+repr(e)
            rec={'q':qid,'cond':cond,'sec':round(sec,1),'usage':d.get('usage'),'raw':raw,'parsed':parse(raw)}
            f.write(json.dumps(rec,ensure_ascii=False)+'\n'); f.flush()
            print(qid,cond,round(sec,1),'s',(rec['parsed'] or {}).get('found'),flush=True)
