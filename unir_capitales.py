import re,json,sys,random
UP=re.compile(r'^[A-ZÆŒ]+$')
STOP={'ET','IN','AB','AD','DE','EX','SI','NON','AC','VT','VEL','NEC','CVM','PER','PRO','SED','AVT','EST','SVNT','SIC','QVI','QVAE','QVOD'}
def cls(tok):
    """('1',tok) letra suelta; ('W',tok) palabra en mayúsculas (puede llevar puntuación final); None"""
    core=tok.rstrip('.,;:?!)')
    punt=tok[len(core):]
    if not UP.match(core): return None
    if len(core)==1 and not punt: return '1'
    return 'W' if core not in STOP else None
VOC=None
def nv(w): return w.lower().replace('v','u').replace('j','i').replace('æ','ae').replace('œ','oe')
def build(d):
    import collections
    c=collections.Counter()
    for e in d:
        for s in e['segs']:
            for w in re.findall(r'[A-Za-zæœÆŒ]{4,}',s['t']):
                if not (w.isupper() and False): c[nv(w)]+=1
    return c
def unir(t):
    toks=t.split(' ');out=[];i=0
    while i<len(toks):
        c=cls(toks[i])
        if c is None: out.append(toks[i]);i+=1;continue
        j=i;singles=1 if c=='1' else 0
        while j+1<len(toks):
            c2=cls(toks[j+1]);c1=cls(toks[j])
            if c2 is None: break
            if (c1=='1' or c2=='1') and not re.search(r'[.,;:?!)]$',toks[j]):
                j+=1;singles+=(c2=='1')
            else: break
        if singles>=1 and j>i:
            m=''.join(toks[i:j+1]);core=m.rstrip('.,;:?!)')
            if VOC is not None and len(core)>=5 and VOC.get(nv(core),0)>=3 and not re.match(r'^(DEVERB|VERBORV|LIBER[IVXL]|IVSPERT|[IVXLCDM]+$)',core): out.append(m);i=j+1
            else: out.append(toks[i]);i+=1
        else: out.append(toks[i]);i+=1
    return ' '.join(out)
if __name__=='__main__':
    d=json.load(open(sys.argv[1]));ch=[];VOC=build(d)
    for e in d:
        for s in e['segs']:
            n=unir(s['t'])
            if n!=s['t']:
                a=s['t'].split(' ');b=n.split(' ')
                ch.append((e['hw'],len(a)-len(b)))
                s['t']=n
    print(len(ch),'segmentos cambiados')
    json.dump(d,open(sys.argv[2],'w',encoding='utf-8'),ensure_ascii=False)
