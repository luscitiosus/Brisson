"""Resolución de títulos por subsecuencia: «de adquir. poss.» -> D.41.2 (de adquirenda vel amittenda possessione)."""
import re,sys
sys.path.insert(0,'.')
import cites
from cites import nz,lev,STOP,ALIAS
W=cites.W
def load_cth():
    T=[]
    for ln in open(W+'cthtitles.txt',encoding='utf-8'):
        k,t=ln.strip().split('|');b,i=map(int,k.split('.'))
        T.append((b,i,t,[nz(x) for x in re.split(r'[\s,:]+',t) if nz(x)]))
    return T
CTH=load_cth()
def tm(tok,w,fuzzy):
    if tok==w: return True
    if len(tok)<3 or tok in STOP: return False
    if w.startswith(tok): return True
    if 'qu' in tok and w.startswith(tok.replace('qu','c')): return True
    if fuzzy:
        if len(tok)>=4 and lev(tok,w[:len(tok)])<=1: return True
        if len(tok)>=6 and lev(tok,w[:len(tok)])<=2: return True
    return False
def expand(tokens):
    out=[]
    for t in tokens:
        n=nz(t)
        if not n: break
        if n in ALIAS and (t.rstrip(',').endswith('.') or n=='sc'): out.extend(ALIAS[n])
        else: out.append(n)
    return out
def match(toks,words,fuzzy,maxskip=3):
    """consume tokens en orden sobre words; devuelve (k tokens consumidos, palabras saltadas)"""
    pos=0;k=0;skipped=0
    for n,tok in enumerate(toks):
        found=None
        lim=0 if n==0 else maxskip
        for d in range(0,lim+1):
            if pos+d<len(words) and tm(tok,words[pos+d],fuzzy): found=d;break
        if found is None: break
        skipped+=found;pos+=found+1;k+=1
    return k,skipped,pos
def strength(tok,w):
    if tok==w: return 2
    if len(tok)<3 or tok in STOP: return 0
    if w.startswith(tok) or ('qu' in tok and w.startswith(tok.replace('qu','c'))): return 2
    if len(tok)>=4 and min(lev(tok,w[:len(tok)]),lev(tok,w[:len(tok)+1]))<=1: return 1
    if len(tok)>=6 and min(lev(tok,w[:len(tok)]),lev(tok,w[:len(tok)+1]))<=2: return 0.5
    return 0
def score(toks,ws):
    """suma de fuerza por token (palabras de contenido), sin repetir palabra del título; devuelve (puntos, k, ordenado, saltadas)"""
    ws=list(ws)+[ws[i]+ws[i+1] for i in range(len(ws)-1)]
    used=set();tot=0;k=0;last=-1;ordered=True;sk=0
    for n,tok in enumerate(toks):
        best=None
        for j,w in enumerate(ws):
            if j in used: continue
            st=strength(tok,w)
            if st and (best is None or st>best[0] or (st==best[0] and j>last and best[1]<=last)): best=(st,j)
        if best is None:
            if n==0: return None
            break
        used.add(best[1]);k+=1
        if tok not in STOP: tot+=best[0]
        if best[1]<last: ordered=False
        else: sk+=best[1]-last-1 if last>=0 else best[1]
        last=best[1]
    if n==0 and k==0: return None
    return tot,k,ordered,sk
def resolve(tokens,TT):
    toks=expand(tokens)[:9]
    if not toks: return None,0
    best=[];bk=None
    for (b,t,tt,ws) in TT:
        r=score(toks,ws)
        if not r or r[0]==0: continue
        tot,k,ordered,sk=r
        full=(k and len(ws)<=k+3)
        key=(tot,ordered,-sk,k)
        if bk is None or key>bk: best=[(b,t)];bk=key
        elif key==bk: best.append((b,t))
    if not best: return None,0
    k=bk[3]
    if len(best)==1: return best[0],k
    return ('AMBIG',best[:3]),k
if __name__=='__main__':
    for s in ['de adquir. poss.','de iniur.','de reg. iur.','de act. emti.','de offic. procos.','de pignor.','de contrah. emt.','de rer. diuision.','de vsufr.','ad leg. Aquil.']:
        print(s,resolve(s.split(),cites.TITLES))
    print('th',resolve('de oper. publ.'.split(),CTH),resolve('de episc. eccles.'.split(),CTH))
