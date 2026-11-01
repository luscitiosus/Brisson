import re,json,sys,collections,itertools
TOK=re.compile(r"[A-Za-zæœĩãẽõũęàèìòùẽꝑꝗꝓ]{4,}")
HEAD=re.compile(r"\s*D ?E ?V ?E ?R ?B ?O ?R ?V ?M\s+S ?I ?G ?N ?I ?F ?I ?C ?A ?T ?I? ?O? ?N? ?E? ?S?\.?")
BASE=str.maketrans({'ꝑ':'p','ꝗ':'q','ꝓ':'p','ã':'a','ẽ':'e','ĩ':'i','õ':'o','ũ':'u','à':'a','è':'e','ì':'i','ò':'o','ù':'u','ę':'e'})
CONF=[('c','e'),('e','c'),('i','l'),('l','i'),('u','n'),('n','u'),('f','s'),('s','f'),('h','b'),('b','h'),('m','rn'),('rn','m'),('ii','u'),('r','t'),('t','r'),('i','t'),('li','h')]
def cands(w):
    lw=w.lower();out=set()
    b=lw.translate(BASE)
    if b!=lw: out.add(b)
    if re.search(r'[ęœæ]',lw): out.add(re.sub('[ęœæ]','ae',lw));out.add(re.sub('[ęœæ]','e',lw))
    for a,c in CONF:
        for m in re.finditer(re.escape(a),b if b!=lw else lw):
            src=b if b!=lw else lw
            out.add(src[:m.start()]+c+src[m.end():])
    out.discard(lw);return out
def build(d):
    c=collections.Counter()
    for e in d:
        for s in e['segs']:
            for w in TOK.findall(s['t']): c[w.lower()]+=1
    return c
def fix_word(w,V):
    lw=w.lower();f=V.get(lw,0)
    if f>=3 or w.isupper() or len(w)<5 or re.fullmatch(r'[ivxlcdmIVXLCDM]+',w): return w
    best=[(V.get(c,0),c) for c in cands(w) if V.get(c,0)>=20 and V.get(c,0)>=10*max(f,1)]
    if not best: return w
    best.sort(reverse=True)
    if len(best)>1 and best[0][0]<2*best[1][0]: return w   # ambiguo
    c=best[0][1]
    if w.isupper(): return c.upper()
    if w[0].isupper(): return c[0].upper()+c[1:]
    return c
def fix_text(t,V,log=None):
    t=HEAD.sub(' ',t)
    t=re.sub(r'(?<=[a-z])- (?=[a-z]{2,})',lambda m:'\0',t)  # marca
    def join(m): 
        a,b=m.group(1),m.group(2);j=(a+b).lower()
        return a+b if V.get(j,0)>=2 else a+'- '+b
    t=t.replace('\0','- ')
    t=re.sub(r'\b([a-zæœ]{2,})- ([a-zæœ]{2,})\b',join,t)
    def rep(m):
        w=m.group(0);n=fix_word(w,V)
        if n!=w and log is not None: log.append((w,n))
        return n
    return TOK.sub(rep,t)
if __name__=='__main__':
    d=json.load(open(sys.argv[1]));V=build(d);log=[];ch=0
    for e in d:
        for s in e['segs']:
            n=fix_text(s['t'],V,log)
            if n!=s['t']: ch+=1;s['t']=n
    print(ch,'segmentos',len(log),'palabras corregidas')
    json.dump(d,open(sys.argv[2],'w',encoding='utf-8'),ensure_ascii=False)
    json.dump(log,open(sys.argv[2]+'.log','w',encoding='utf-8'),ensure_ascii=False)
