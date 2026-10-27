import time,urllib.error,json,sys,urllib.request,urllib.parse,concurrent.futures as cf,collections
H={'User-Agent':'JournalClubAssistant/0.1 (mailto:dumber73@gmail.com)'}
CACHE={}
def get(doi):
    u='https://api.crossref.org/works/'+urllib.parse.quote(doi)
    if doi in CACHE: return CACHE[doi]
    for i in range(6):
        try:
            m=json.load(urllib.request.urlopen(urllib.request.Request(u,headers=H),timeout=30))['message']; CACHE[doi]=m; return m
        except urllib.error.HTTPError as e:
            if e.code==404: CACHE[doi]=None; return None
            time.sleep(2*(i+1))
        except Exception: time.sleep(2*(i+1))
    return None
def grade(m):
    if not m: return 'unknown'
    for l in m.get('license',[]):
        if 'creativecommons' in l['URL'] and l.get('content-version') in('vor','unspecified'):
            u=l['URL']; return 'CC BY' if '/by/' in u else 'CC BY-NC-ND' if 'by-nc-nd' in u else 'CC BY-NC' if 'by-nc' in u else 'CC other'
    return 'L'
def year(m):
    for k in('issued','published'):
        try: return m[k]['date-parts'][0][0]
        except: pass
dois=[d.strip() for d in sys.argv[1].split(',')]
res={}
for d in dois:
    m=get(d)
    if not m: res[d]={'err':True};continue
    refs=m.get('reference',[])
    rd=[r['DOI'].lower() for r in refs if r.get('DOI')]
    with cf.ThreadPoolExecutor(3) as ex: rm=list(ex.map(get,rd))
    gr=[grade(x) for x in rm]; yr=[year(x) if x else None for x in rm]
    res[d]={'title':m['title'][0][:70],'journal':m.get('container-title',[''])[0],'self':grade(m),'nrefs':len(refs),'nrefdoi':len(rd),'refgrades':gr,'refyears':yr}
    print(d,res[d]['self'],len(refs),len(rd),flush=True)
json.dump(res,open('grades.json','w'))
