"""Construye datos/lexica.json.gz a partir de PerseusDL/lexica (L&S eng2 y Elementary). Uso:
   python lexica_build.py <carpeta pdllex/lat> brisson.json"""
import gzip,html,json,os,re,sys
from lexica import norm,candidatos
import lemas
RAIZ,JS=sys.argv[1],sys.argv[2]
D=json.load(open(JS,encoding='utf-8'))
quiero=set()
for e in D: quiero.update(candidatos(e['hw']))
_ls=open(os.path.join(RAIZ,'ls','lat.ls.perseus-eng2.xml'),encoding='utf-8').read()
_el=open(os.path.join(RAIZ,'viaf2845558','viaf001','viaf2845558.viaf001.xml'),encoding='utf-8').read()
TODAS=set(norm(re.sub(r'\d+$','',m)) for m in re.findall(r'<entryFree[^>]*key="([^"]+)"',_ls))|set(norm(re.sub(r'\d+$','',m)) for m in re.findall(r'<entry [^>]*key="([^"]+)"',_el))
ALIAS={}
for e in D:
    n=norm(e['hw'])
    if any(c in TODAS for c in candidatos(e['hw'])): continue
    r=lemas.lematizar(n,TODAS,1)
    if r: ALIAS[n]=r[0]; quiero.add(r[0])
def limpia(x,tope,plano=False):
    def _sn(m):
        a=m.group(0);lv=re.search(r'level="(\d)"',a);n=re.search(r' n="([^"]*)"',a)
        return '\n¶'+('1' if not lv or lv.group(1)=='1' else '2')+' '+((n.group(1)+'. ') if n and n.group(1) else '')
    x=re.sub(r'<sense[^>]*>',_sn,x)
    x=re.sub(r'<hi rend="ital">(.*?)</hi>',r'\1',x,flags=re.S)
    x=re.sub(r'<[^>]+>','',x);x=html.unescape(x)
    x=re.sub(r'[ \t]+',' ',x);x=(re.sub(r'\s+',' ',x) if plano else re.sub(r'\n\s*','\n',x)).strip()
    x=html.escape(x).replace('','<i>').replace('','</i>')
    x=x.replace('\n¶1 ','\n').replace('\n¶2 ','\n&nbsp;&nbsp;')
    if len(x)>tope:
        x=x[:tope];x=x[:x.rfind(' ')]+' …'
        if x.count('<i>')>x.count('</i>'): x+='</i>'
    return x
out={}
ls=open(os.path.join(RAIZ,'ls','lat.ls.perseus-eng2.xml'),encoding='utf-8').read()
for m in re.finditer(r'<entryFree[^>]*key="([^"]+)"[^>]*>(.*?)</entryFree>',ls,flags=re.S):
    k=norm(re.sub(r'\d+$','',m.group(1)))
    if k in quiero:
        out.setdefault(k,{}).setdefault('ls',[]).append({'k':re.sub(r'\d+$','',m.group(1)),'t':limpia(m.group(2),14000)})
el=open(os.path.join(RAIZ,'viaf2845558','viaf001','viaf2845558.viaf001.xml'),encoding='utf-8').read()
for m in re.finditer(r'<entry [^>]*key="([^"]+)"[^>]*>(.*?)</entry>',el,flags=re.S):
    k=norm(re.sub(r'\d+$','',m.group(1)))
    if k in quiero:
        out.setdefault(k,{}).setdefault('el',[]).append({'k':re.sub(r'\d+$','',m.group(1)),'t':limpia(m.group(2),1500,True)})
out['_alias']=ALIAS
PAR={}
for k,v in out.items():
    if k.startswith('_') or not v.get('ls'): continue
    t=re.sub(r'<[^>]+>','',v['ls'][0]['t'])[:160]
    m=list(re.finditer(r'\b(?:m|f|n|adj|a|subst)\.\s*[,;]?\s*',t))
    if not m: continue
    ws=re.findall(r"[A-Za-zāēīōūăĕĭŏŭ]+",t[m[0].end():m[0].end()+60])[:2]
    if ws and ws[0].lower() in('v','cf','vid'): continue
    for w in ws:
        p=norm(w)
        if p!=k and p in TODAS and len(p)>=3 and p not in('cf','from','prop','sc','esp','id','qs','also','the','and','for','in','of','to','see','like','with','that','adj','of','or'):
            PAR[k]=p;break
out['_par']=PAR
with gzip.open('datos/lexica.json.gz','wt',encoding='utf-8') as g: json.dump(out,g,ensure_ascii=False)
print(len(out),'claves;',os.path.getsize('datos/lexica.json.gz')/1e6,'MB')
n=sum(1 for e in D if any(c in out for c in candidatos(e['hw'])) or norm(e['hw']) in ALIAS)
print('voces con lexicón:',n,'de',len(D))
