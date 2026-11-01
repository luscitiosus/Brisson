import re,json,sys
sys.path.insert(0,'/tmp/claude-0/-home-claude/89e928e4-4473-5419-887c-3a2085f1b398/scratchpad')
import cites
from cites import resolve,CT,TITLES
D=r"[0-9iIl&æ|]"
RX=re.compile(r"(?<![A-Za-z])[lLIi1]\.?\s*(?P<law>"+D+r"{1,4}|vlt|ult)\.?(?:\s*(?:(?P<pr>pr)[.*,;]?|(?:[§5sS$&*]|in\s+fin)\.?\s*(?P<pn>"+D+r"{1,3}|vlt|fin)?\.?))?\s*(?P<src>[DC])\.\s*(?P<tail>(?:[A-Za-zæãõ]+[.,]?\s*){1,9})")
def num(x):
    if x is None: return None
    if x in('vlt','ult'): return 'ult'
    return re.sub(r'\D','',x.translate(str.maketrans({'i':'1','I':'1','l':'1','|':'1','&':'8','æ':'2'}))) or None
def convert(text):
    t=re.sub(r'\s+',' ',text)
    out=[];last=None
    for m in RX.finditer(t):
        toks=m.group('tail').split()
        TT=CT if m.group('src')=='C' else None
        if len(toks)>0 and toks[0].lower().rstrip('.,') in('eod','eodem','d','dict'):
            res,u=(last,1) if last else (None,0)
        else:
            res,u=resolve(toks,TT)
        law=num(m.group('law'));pn=num(m.group('pn'))
        if isinstance(res,tuple) and res and res[0]!='AMBIG':
            last=res
            ref=f"{m.group('src')}.{res[0]}.{res[1]}.{law}"+('pr' if m.group('pr') else (f".{pn}" if pn else ''))
            tk=[x for x in re.finditer(r'\S+',m.group('tail'))]
            uu=min(max(u,1),len(tk))
            if res is last and tk and tk[0].group(0).lower().startswith('eod') and len(tk)>1 and tk[1].group(0).lower().startswith('tit'): uu=2
            end=m.start('tail')+tk[uu-1].end() if tk else m.end()
            out.append((m.start(),end,'ok',ref,m.group(0)))
        elif isinstance(res,tuple) and res and res[0]=='AMBIG':
            out.append((m.start(),m.end(),'ambig',str(res[1][:3]),m.group(0)))
        else:
            out.append((m.start(),m.end(),'none','',m.group(0)))
    return out
if __name__=='__main__':
    E=json.load(open('/tmp/claude-0/-home-claude/89e928e4-4473-5419-887c-3a2085f1b398/scratchpad/w/entries1.json'))
    import collections
    names=sys.argv[1:]
    tot=collections.Counter()
    for e in E:
        if e['hw'] in names:
            r=convert(e['text'])
            c=collections.Counter(x[2] for x in r); tot.update(c)
            print(e['hw'],e['page'],len(e['text']),dict(c))
    print(dict(tot))
