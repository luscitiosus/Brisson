"""Separa palabras pegadas por el OCR: VERSALITAS+minúscula (FVRANDIconsilio) y minúscula+versalitas mal leídas (coMES)."""
import re,json,collections,random,sys
A=re.compile(r"(?<![A-Za-zæœÆŒ])([A-ZÆŒ]{4,})([a-zæœ]{3,})(?![A-Za-zæœ])")
B=re.compile(r"(?<![A-Za-zæœÆŒ])([a-zæœ]{1,2})([A-ZÆŒ]{3,})(?![A-Za-zæœ])")
def vocab(d):
    c=collections.Counter()
    for e in d:
        for s in e['segs']:
            for w in re.findall(r"[a-zæœ]{3,}",s['t']): c[w]+=1
    return c
def sep(t,V,log=None):
    def a(m):
        if V.get(m.group(2),0)>=5 and m.group(2) not in ("que","que"):
            if log is not None: log.append(m.group(0))
            return m.group(1)+' '+m.group(2)
        return m.group(0)
    t=A.sub(a,t)
    def b(m):
        if log is not None: log.append(m.group(0))
        return (m.group(1)+m.group(2)).upper()
    return B.sub(b,t)
if __name__=='__main__':
    d=json.load(open('brisson.json'));V=vocab(d);log=[];n=0
    for e in d:
        for s in e['segs']:
            x=sep(s['t'],V,log)
            if x!=s['t']: s['t']=x;n+=1
    print(n,'segmentos',len(log),'palabras');random.seed(8);print(random.sample(log,45))
    if len(sys.argv)>1: json.dump(d,open('brisson.json','w',encoding='utf-8'),ensure_ascii=False)
