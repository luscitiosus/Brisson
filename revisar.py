"""Revisión de entradas: detecta palabras sospechosas de error de OCR contra un corpus de formas latinas declinadas
(Latin Library + Perseus, ~560.000 formas) y los nombres de juristas y autores, y propone correcciones.
No corrige nada por sí sola: da candidatos para que una persona (o Claude) los confirme."""
import gzip,os,pickle,re,unicodedata,collections
HERE=os.path.dirname(os.path.abspath(__file__))
_S={}
def norm(w):
    w=unicodedata.normalize('NFD',w.lower());w=''.join(c for c in w if unicodedata.category(c)!='Mn')
    return w.replace('v','u').replace('j','i').replace('æ','ae').replace('œ','oe')
def cargar(D):
    if _S: return _S
    d=pickle.load(gzip.open(os.path.join(HERE,'datos','latin.pkl.gz'),'rb'))
    B=collections.Counter()
    for e in D:
        for s in e['segs']:
            for m in re.finditer(r"[A-Za-zæœÆŒ]{3,}",s['t'].replace('','').replace('','')): B[norm(m.group(0))]+=1
    _S.update(V=d['V'],N=d['N'],B=B);return _S
ROM=re.compile(r'^[ivxlcdm]+$')
ABC='abcdefghilmnopqrstuxyz'
OCR=[('ii','u'),('rn','m'),('li','h'),('ni','m'),('ri','n'),('cl','d'),('ct','et'),('ſ','s'),('f','s'),('s','f'),('c','e'),('e','c'),('t','l'),('l','t'),('l','i'),('i','l'),('u','n'),('n','u'),('b','h'),('h','b'),('o','e'),('e','o'),('a','e'),('a','o'),('t','i'),('i','t'),('q','g'),('g','q'),('rr','n'),('m','in'),('in','m')]
def valida(n):
    S=_S;return S['V'].get(n,0)>=2 or S['B'].get(n,0)>=4 or n in S['N']
def freq(n): return _S['V'].get(n,0)+(_S['B'].get(n,0)>=4)*5
def edits1(w):
    sp=[(w[:i],w[i:]) for i in range(len(w)+1)]
    r=set(a+b[1:] for a,b in sp if b)|set(a+b[1]+b[0]+b[2:] for a,b in sp if len(b)>1)
    r|=set(a+c+b[1:] for a,b in sp if b for c in ABC)|set(a+c+b for a,b in sp for c in ABC)
    return r
def ocr1(w):
    out=set()
    for x,y in OCR:
        for m in re.finditer(re.escape(x),w): out.add(w[:m.start()]+y+w[m.end():])
        for m in re.finditer(re.escape(y),w): out.add(w[:m.start()]+x+w[m.end():])
    return out
def sugerir(n,sig=None,corto=False):
    """Candidatos para la forma normalizada n. sig = siguiente palabra normalizada (para uniones)."""
    c=collections.OrderedDict()
    if sig:
        j=n+sig
        if valida(j) and freq(j)>=3: c[j]=('unir con la siguiente',freq(j))
    for i in range(3,len(n)-2):
        a,b=n[:i],n[i:]
        if freq(a)>=120 and freq(b)>=120: c.setdefault(a+' '+b,('separar',min(freq(a),freq(b))))
    cand={}
    for x in ocr1(n)|edits1(n):
        if x!=n and valida(x): cand[x]=freq(x)
    if not cand and len(n)>=6 and not corto:
        for e in edits1(n):
            for x in edits1(e):
                if x!=n and valida(x) and freq(x)>=20: cand[x]=freq(x)
                if len(cand)>60: break
    for x,f in sorted(cand.items(),key=lambda t:-t[1])[:5]: c.setdefault(x,('forma',f))
    return list(c.items())[:5]
def forma(s,orig):
    """Muestra la sugerencia con las convenciones del léxico: VERSALES con V; minúsculas con u."""
    if orig.isupper(): return s.upper().replace('U','V')
    r=s
    return (r[0].upper()+r[1:]) if orig[:1].isupper() else r
TOK=re.compile(r"[A-Za-zæœÆŒ]+")
def revisar_texto(t,D,max_n=60):
    cargar(D)
    t=t.replace('','').replace('','')
    # se ignoran las referencias entre corchetes y el griego
    t2=re.sub(r"\[[^\]]*\]",lambda m:' '*len(m.group(0)),t).replace('⟦griego⟧',' '*8)
    toks=list(TOK.finditer(t2));out=[]
    for k,m in enumerate(toks):
        w=m.group(0)
        if len(w)<=2 or ROM.match(norm(w)): continue
        n=norm(w)
        if valida(n): continue
        fin=t2[m.end():m.end()+1]
        if fin=='.' and len(w)<=7: continue          # abreviatura probable
        if t2[max(0,m.start()-1):m.start()].isdigit() or fin.isdigit(): continue
        sig=None
        if k+1<len(toks) and toks[k+1].start()-m.end()<=1: sig=norm(toks[k+1].group(0))
        sg=sugerir(n,sig)
        a=max(0,m.start()-35);b=min(len(t),m.end()+35)
        out.append({'palabra':w,'ctx':re.sub(r'\s+',' ',t[a:b]),'sug':[(forma(s,w),tipo,f) for s,(tipo,f) in sg]})
        if len(out)>=max_n: break
    return out
def informe(e,D,capa='ambas'):
    res=[]
    for s in e['segs']:
        for r in revisar_texto(s['t'],D): r['capa']={'T':'Heineccio','B':'Brisson','C':'corchetes'}[s['k']];res.append(r)
    return res
