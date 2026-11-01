import re,json,unicodedata
W='/tmp/claude-0/-home-claude/89e928e4-4473-5419-887c-3a2085f1b398/scratchpad/w/'
def nz(w):
    w=unicodedata.normalize('NFKD',w.lower())
    w=''.join(c for c in w if c.isascii())
    w=w.replace('v','u').replace('j','i')
    return re.sub(r'[^a-z]','',w)
TITLES=[]
for ln in open(W+'dtitles.txt',encoding='utf-8'):
    p=ln.strip().split('|')
    for i,t in enumerate(p[1:],1):
        ws=[nz(x) for x in re.split(r'[\s,:]+',t) if nz(x)]
        TITLES.append((int(p[0]),i,t,ws))
CT=[]
for ln in open(W+'ctitles.txt',encoding='utf-8'):
    p=ln.strip().split('|')
    for i,t in enumerate(p[1:],1):
        ws=[nz(x) for x in re.split(r'[\s,:]+',t) if nz(x)]
        CT.append((int(p[0]),i,t,ws))
ALIAS={'sc':['senatus','consultum'],'scto':['senatus','consulto'],'l':['legem'],'leg':['legem']}
STOP={'de','et','vel','ad','in','ex','si','ut','qui','quae','quod','a','ne','sive','id','est','cum','pro','per','quibus','quo'}
def lev(a,b):
    p=list(range(len(b)+1))
    for i,ca in enumerate(a,1):
        c=[i]
        for j,cb in enumerate(b,1):
            c.append(min(p[j]+1,c[j-1]+1,p[j-1]+(ca!=cb)))
        p=c
    return p[-1]
def tokmatch(tok,w):
    if not tok: return False
    if tok==w: return True
    if len(tok)<3 or tok in STOP: return False
    if w.startswith(tok): return True
    if 'qu' in tok and w.startswith(tok.replace('qu','c')): return True
    if len(tok)>=4 and lev(tok,w[:len(tok)])<=1: return True
    if len(tok)>=6 and lev(tok,w[:len(tok)])<=2: return True
    return False
def match_title(tokens,TT=None):
    cand=[(b,t,tt,ws,0) for (b,t,tt,ws) in (TT or TITLES)]
    used=0;best=None
    for n,tok in enumerate(tokens):
        raw=tok
        nt=nz(tok)
        if not nt: break
        exp=ALIAS.get(nt) if (nt in ALIAS and tok.rstrip(',').endswith('.') or nt=='sc') else None
        new=[]
        for (b,t,tt,ws,pos) in cand:
            if exp:
                if ws[pos:pos+len(exp)]==exp or all(tokmatch(x[:3],ws[pos+i][:3]) for i,x in enumerate(exp) if pos+i<len(ws)):
                    new.append((b,t,tt,ws,pos+len(exp)))
            elif pos<len(ws) and tokmatch(nt,ws[pos]):
                new.append((b,t,tt,ws,pos+1))
        if not new: break
        cand=new;used=n+1
        full=[c for c in cand if c[4]==len(c[3])]
        if full: best=(full,used)
    return best,cand,used
def resolve(tokens,TT=None):
    best,cand,used=match_title(tokens,TT)
    if not cand or used==0: return None,0
    content=[nz(t) for t in tokens[:used] if nz(t) not in STOP and nz(t) not in ALIAS]
    if not content and not any(nz(t) in ALIAS for t in tokens[:used]): return None,0
    nxt=tokens[used] if used<len(tokens) else ''
    def suspicious():
        return bool(re.fullmatch(r'[a-z\u00e6]{3,}\.',nxt))
    if best is not None:
        full,u=best
        if u==used:
            if len(full)==1: return full[0][:2],u
            return ('AMBIG',[(c[0],c[1]) for c in full]),u
        if len(cand)==1 and not suspicious(): return cand[0][:2],used
        if len(full)==1 and not suspicious(): return full[0][:2],u
        return ('AMBIG',[(c[0],c[1]) for c in (full if full else cand)]),u
    if len(cand)==1 and not suspicious(): return cand[0][:2],used
    return ('AMBIG',[(c[0],c[1]) for c in cand]),used
if __name__=='__main__':
    for s in ['de incend. ruin.','de fideic. libert.','ad SC. Trebell.','de his, quae vt indign.','de adim. vel transf. leg.','de pact. conu.','de verb. signif.','de minor.','de man. vind.','ad L. Aquil.']:
        print(s,resolve(s.split()))
