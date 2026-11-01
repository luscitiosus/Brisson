"""El OCR lee a veces ER como EE (SEE VIRE → SERVIRE). Corrige palabras (y pares de palabras) cuando la variante con ER existe en el libro."""
import re,json,collections,sys,random
def nv(w): return w.lower().replace('v','u').replace('j','i').replace('æ','ae').replace('œ','oe')
def vocab(d):
    c=collections.Counter()
    for e in d:
        for s in e['segs']:
            for w in re.findall(r"[A-Za-zæœÆŒ]{3,}",s['t']): c[nv(w)]+=1
    return c
def variants(w):
    out=set();i=0
    for m in re.finditer(r'EE|ee|Ee',w):
        r={'EE':'ER','ee':'er','Ee':'Er'}[m.group(0)]
        out.add(w[:m.start()]+r+w[m.end():])
    # todas las sustituciones a la vez
    allr=re.sub(r'EE','ER',w) if 'EE' in w else re.sub(r'ee','er',w)
    if allr!=w: out.add(allr)
    return out
TOK=re.compile(r"(?<![A-Za-zæœÆŒ])([A-Za-zæœÆŒ]{2,})(?![A-Za-zæœÆŒ])")
def fix(t,V,log=None):
    # 1) pares en mayúsculas: SEE VIRE -> SERVIRE
    def par(m):
        a,b=m.group(1),m.group(2);j=a+b
        if V.get(nv(a),0)>=5 and V.get(nv(b),0)>=5: return m.group(0)
        for c in [j]+sorted(variants(j)):
            if (c!=j or V.get(nv(j),0)>=5) and V.get(nv(c),0)>=5 and V.get(nv(j),0)<3:
                if log is not None: log.append((m.group(0),c))
                return c
        return m.group(0)
    t=re.sub(r"(?<![A-Za-zæœÆŒ])([A-ZÆŒ]{2,6}) ([A-ZÆŒ]{3,10})(?![A-Za-zæœÆŒ])",par,t)
    # 2) palabras sueltas con EE
    def pal(m):
        w=m.group(1)
        if len(w)<5 or not re.search('ee|EE|Ee',w) or V.get(nv(w),0)>=3: return m.group(0)
        for c in sorted(variants(w)):
            if V.get(nv(c),0)>=5:
                if log is not None: log.append((w,c))
                return c
        return m.group(0)
    return TOK.sub(pal,t)
if __name__=='__main__':
    d=json.load(open('brisson.json'));V=vocab(d);log=[];n=0
    print(fix('et SEE VIRE ait',V))
    for e in d:
        for s in e['segs']:
            x=fix(s['t'],V,log)
            if x!=s['t']: n+=1;s['t']=x
    print(n,len(log));random.seed(1);print(random.sample(log,min(60,len(log))))
    if len(sys.argv)>1: json.dump(d,open('brisson.json','w',encoding='utf-8'),ensure_ascii=False)
