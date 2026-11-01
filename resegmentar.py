"""Rehace cortes de palabra mal puestos por el OCR: «velad astiones» -> «vel ad actiones»."""
import re,json,math,collections,sys,random
import ocrfix
TOK=re.compile(r"[a-zæœ]+")
SMALL={'ad','et','in','ex','ab','de','vel','non','est','sed','per','pro','cum','sub','nec','aut','vt'}
def vocab(d):
    c=collections.Counter()
    for e in d:
        for s in e['segs']:
            for w in TOK.findall(s['t']): c[w]+=1
    return c
def piece(p,V):
    """(coste, forma) si p es una palabra válida (o con un único cambio OCR muy seguro)"""
    f=V.get(p,0)
    if p in SMALL: return (1.0,p)
    if len(p)>=4 and f>=60: return (math.log(1e5/f)+1.5,p)
    if len(p)>=5:
        best=None
        for q in ocrfix.cands(p)|{p.replace('s','c',1)}|{p.replace('c','s',1)}:
            fq=V.get(q,0)
            if fq>=60 and (best is None or fq>best[0]): best=(fq,q)
        if best: return (math.log(1e5/best[0])+3.5,best[1])
    return None
def seg(s,V,maxp=3):
    n=len(s);best=[None]*(n+1);best[0]=(0,[])
    for i in range(n):
        if best[i] is None or len(best[i][1])>=maxp: continue
        for j in range(i+2,n+1):
            pc=piece(s[i:j],V)
            if pc:
                c=best[i][0]+pc[0]
                if best[j] is None or c<best[j][0]: best[j]=(c,best[i][1]+[pc[1]])
    return best[n]
def fix(t,V,log=None):
    toks=list(re.finditer(r"[a-zæœ]+",t));out=[];i=0;pos=0
    def ok(w): return V.get(w,0)>=3 or w in SMALL
    while i<len(toks):
        m=toks[i];a=m.group(0)
        cand=None
        # par (a,b) separados por un solo espacio
        if i+1<len(toks) and t[m.end():toks[i+1].start()]==' ':
            b=toks[i+1].group(0)
            if V.get(a,0)<3 and V.get(b,0)<3 and a not in SMALL and b not in SMALL and len(a+b)>=7:
                r=seg(a+b,V)
                if r and [a,b]!=r[1] and len(r[1])>=2: cand=(r[1],2)
        if cand is None and 4<=len(a)<=7 and V.get(a,0)<=3:
            r=seg(a,V,2)
            if r and len(r[1])==2 and all(x in SMALL for x in r[1]): cand=(r[1],1)
        if cand is None and V.get(a,0)==0 and len(a)>=8:
            r=seg(a,V)
            if r and len(r[1])>=2: cand=(r[1],1)
        if cand:
            parts,k=cand
            out.append(t[pos:m.start()]);out.append(' '.join(parts))
            if log is not None: log.append((' '.join(x.group(0) for x in toks[i:i+k]),' '.join(parts)))
            pos=toks[i+k-1].end();i+=k
        else: i+=1
    out.append(t[pos:]);return ''.join(out)
if __name__=='__main__':
    d=json.load(open('brisson.json'));V=vocab(d);log=[];n=0
    print(fix('et hoc velad astiones pertinet',V))
    for e in d:
        for s in e['segs']:
            x=fix(s['t'],V,log)
            if x!=s['t']: n+=1;s['t']=x if len(sys.argv)>1 else s['t']
    print(n,len(log));random.seed(9);print(random.sample(log,min(70,len(log))))
    if len(sys.argv)>1: json.dump(d,open('brisson.json','w',encoding='utf-8'),ensure_ascii=False)
