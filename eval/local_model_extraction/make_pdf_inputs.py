# usage: python3 make_pdf_inputs.py
# Downloads the 3 OA PDFs from the PMC Open Data bucket (an approved PMC route) and writes, per paper:
#   <name>_pdf_full.txt     pdftotext of the whole PDF (references and headers included, as a real PDF reader would give)
#   <name>_pdf_methods.txt  Materials-and-Methods section cut out of that text by a simple heading heuristic
#   <name>_ocr_full.txt     same pages rasterised at 300 dpi and read with Tesseract (simulates a scan)
#   <name>_ocr_methods.txt  heuristic cut of the OCR text
# Needs poppler (pdftotext, pdftoppm) and tesseract on PATH. Prints sizes, sha256 and whether the section cut fell back to full text.
import os,re,sys,glob,shutil,hashlib,subprocess,tempfile,urllib.request
PAPERS={'song':'PMC11227931','chew':'PMC9807853','kaji':'PMC8718338'}
for tool in ('pdftotext','pdftoppm','tesseract'):
    if not shutil.which(tool): sys.exit(f'missing tool: {tool}')
def cut(text):
    m=re.search(r'^\s*MATERIALS\s+AND\s+METHODS\s*$',text,re.I|re.M)
    if not m: return text,True
    e=re.search(r'^\s*RESULTS\s*$',text[m.end():],re.I|re.M)
    return (text[m.start():m.end()+e.start()] if e else text[m.start():]),(e is None)
for name,pmc in PAPERS.items():
    pdf=f'{name}.pdf'
    if not os.path.exists(pdf):
        urllib.request.urlretrieve(f'https://pmc-oa-opendata.s3.amazonaws.com/{pmc}.1/{pmc}.1.pdf',pdf)
    texts={}
    subprocess.run(['pdftotext','-enc','UTF-8',pdf,f'{name}_tmp.txt'],check=True)
    texts['pdf']=open(f'{name}_tmp.txt',encoding='utf-8').read(); os.remove(f'{name}_tmp.txt')
    with tempfile.TemporaryDirectory() as d:
        subprocess.run(['pdftoppm','-r','300','-gray','-png',pdf,os.path.join(d,'p')],check=True)
        parts=[]
        for img in sorted(glob.glob(os.path.join(d,'p*.png'))):
            parts.append(subprocess.run(['tesseract',img,'stdout','-l','eng'],capture_output=True,text=True,check=True).stdout)
        texts['ocr']='\n'.join(parts)
    for src,t in texts.items():
        meth,fb=cut(t)
        for suf,v in (('full',t),('methods',meth)):
            fn=f'{name}_{src}_{suf}.txt'; open(fn,'w',encoding='utf-8').write(v)
            print(fn,len(v),'chars',hashlib.sha256(v.encode()).hexdigest()[:16],'(section cut fell back to full text)' if suf=='methods' and fb else '')
