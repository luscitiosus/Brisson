import re,sys
sys.path.insert(0,'.')
import cites,cites2,conv
RX=conv.RX;num=conv.num
TH={'theod','theodos','theodosian','th','thed','thevd','theodosiani','codtheod'}
def convert(text):
    t=re.sub(r'\s+',' ',text);out=[];last=None
    for m in RX.finditer(t):
        toks=m.group('tail').split();src=m.group('src')
        th=False
        if src=='C' and toks and cites.nz(toks[0]) in TH: th=True;toks=toks[1:]
        TT=cites2.CTH if th else (cites.CT if src=='C' else cites.TITLES)
        nstart=1 if th else 0
        if toks and cites.nz(toks[0]) in('eod','eodem','d','dict') and last and last[0]==(src if not th else 'CTh'):
            res,u=last[1],1
            if len(toks)>1 and cites.nz(toks[1]).startswith('tit'): u=2
        else:
            res,u=cites2.resolve(toks,TT)
        law=num(m.group('law'));pn=num(m.group('pn'))
        tk=list(re.finditer(r'\S+',m.group('tail')))
        if isinstance(res,tuple) and res and res[0]!='AMBIG':
            lab='CTh' if th else src
            last=(lab,res)
            ref=f"{lab}.{res[0]}.{res[1]}.{law}"+('pr' if m.group('pr') else (f".{pn}" if pn else ''))
            uu=min(max(u+nstart,1),len(tk))
            end=m.start('tail')+tk[uu-1].end() if tk else m.end()
            out.append((m.start(),end,'ok',ref,m.group(0)))
        elif isinstance(res,tuple) and res and res[0]=='AMBIG':
            out.append((m.start(),m.end(),'ambig',str(res[1][:3]),m.group(0)))
        else: out.append((m.start(),m.end(),'none','',m.group(0)))
    return out
