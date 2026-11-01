import re,collections,json
REF=re.compile(r'\[(?:D|C|I|N)[^\]]*\]')
def norm(w): return re.sub(r'^\W+|\W+$','',w).lower()
def build_vocab(entries):
    c=collections.Counter()
    for e in entries:
        for s in e['segs']:
            for w in re.findall(r"[^\W\d_]+",REF.sub(' ',s['t'])): c[w.lower()]+=1
    return c
ODD=re.compile(r"[^A-Za-z\s\W\d]|[A-Za-z][0-9]|[0-9][A-Za-z]")
def odd(core):
    """caracteres no latinos o mezcla letra-dígito"""
    nl=[ch for ch in core if ch.isalpha() and not ch.isascii() and ch not in 'ſęæœ' ]
    ae=[ch for ch in core if ch in 'ęæœẽĩũõàèìòù']
    return len(nl)+(len(ae)>=1)
def score(w,voc):
    core=re.sub(r'^\W+|\W+$','',w)
    if len(core)<2: return 0
    lw=core.lower()
    f=voc.get(lw,0)
    if f>=4 and core.isascii(): return 0
    s=0
    s+=sum(1 for ch in core if ch.isalpha() and not ch.isascii() and ch not in 'ſ')
    if re.search(r'[A-Za-z]\d|\d[A-Za-z]',core): s+=1
    if len(core)>=4 and not re.search(r'[aeiouyæœ]',lw): s+=2
    if re.search(r'[a-z][A-Z]',core): s+=1
    if f<=1: s+=0.5
    # latin ordinario con ę/æ y alta frecuencia tras normalizar
    ln=re.sub('[ęæœ]','ae',lw)
    if voc.get(ln,0)>=4 and not re.search(r'[ẽĩũõ\d]',core): return 0
    return s
def runs(text,voc):
    clean=REF.sub(lambda m:' '*len(m.group()),text)
    toks=[(m.start(),m.end(),m.group()) for m in re.finditer(r'\S+',clean)]
    sc=[score(t[2],voc) for t in toks]
    out=[];i=0
    while i<len(toks):
        if sc[i]>=1.5:
            j=i;k=i;gap=0
            while k+1<len(toks) and gap<=1:
                if sc[k+1]>=1.5: j=k+1;gap=0
                elif len(toks[k+1][2])<=3 or voc.get(norm(toks[k+1][2]),0)<3: gap+=1
                else: break
                k+=1
            fl=[x for x in sc[i:j+1] if x>=1.5]
            if len(fl)>=2 or sc[i]>=3: out.append((toks[i][0],toks[j][1]))
            i=j+1
        else: i+=1
    return out
