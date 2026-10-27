# usage: python3 make_inputs.py [xml_dir]
# Fetches 3 PMC OA articles (or reads <name>.xml from xml_dir) and writes <name>_full.txt (body, no references)
# and <name>_methods.txt (Materials and Methods section only). Prints sha256 of each file.
import re,sys,os,hashlib,urllib.request,xml.etree.ElementTree as ET
PAPERS={'song':'PMC11227931','chew':'PMC9807853','kaji':'PMC8718338'}
def fetch(name,pmc,d):
    p=os.path.join(d,name+'.xml') if d else None
    if p and os.path.exists(p): return open(p,encoding='utf-8').read()
    u=f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id={pmc}&rettype=xml'
    return urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'JCA-test'}),timeout=60).read().decode('utf-8')
def txt(e):
    return re.sub(r'\s+',' ',''.join(e.itertext())).strip()
def render(sec,depth=0,out=None):
    out=out if out is not None else []
    t=sec.find('title')
    if t is not None: out.append('\n'+'#'*(depth+1)+' '+txt(t))
    for c in sec:
        if c.tag=='p': out.append(txt(c))
        elif c.tag=='sec': render(c,depth+1,out)
        elif c.tag=='table-wrap':
            cap=c.find('caption'); out.append('[Table] '+(txt(cap) if cap is not None else ''))
            for tr in c.iter('tr'): out.append(' | '.join(txt(td) for td in tr))
        elif c.tag=='fig':
            cap=c.find('caption'); out.append('[Figure] '+(txt(cap) if cap is not None else ''))
    return out
d=sys.argv[1] if len(sys.argv)>1 else None
for name,pmc in PAPERS.items():
    root=ET.fromstring(fetch(name,pmc,d).encode('utf-8'))
    body=root.find('.//body')
    full='\n'.join(x for s in body.findall('sec') for x in render(s))
    meth=''
    for s in body.findall('sec'):
        t=s.find('title')
        if t is not None and 'METHODS' in txt(t).upper(): meth='\n'.join(render(s))
    for suf,v in (('full',full),('methods',meth)):
        fn=f'{name}_{suf}.txt'; open(fn,'w',encoding='utf-8').write(v+'\n')
        print(fn,len(v),'chars',hashlib.sha256((v+'\n').encode()).hexdigest()[:16])
