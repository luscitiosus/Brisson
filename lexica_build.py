"""Construye datos/lexica.json.gz a partir de PerseusDL/lexica (L&S eng2 y Elementary). Uso:
   python lexica_build.py <carpeta pdllex/lat> brisson.json"""
import gzip,html,json,os,re,sys
from lexica import norm,candidatos
RAIZ,JS=sys.argv[1],sys.argv[2]
D=json.load(open(JS,encoding='utf-8'))
quiero=set()
for e in D: quiero.update(candidatos(e['hw']))
def limpia(x,tope,plano=False):
    x=re.sub(r'<sense[^>]*level="1"[^>]*>','\n¶1 ',x);x=re.sub(r'<sense[^>]*level="[2-9]"[^>]*>','\n¶2 ',x)
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
        out.setdefault(k,{}).setdefault('ls',[]).append({'k':re.sub(r'\d+$','',m.group(1)),'t':limpia(m.group(2),6000)})
el=open(os.path.join(RAIZ,'viaf2845558','viaf001','viaf2845558.viaf001.xml'),encoding='utf-8').read()
for m in re.finditer(r'<entry [^>]*key="([^"]+)"[^>]*>(.*?)</entry>',el,flags=re.S):
    k=norm(re.sub(r'\d+$','',m.group(1)))
    if k in quiero:
        out.setdefault(k,{}).setdefault('el',[]).append({'k':re.sub(r'\d+$','',m.group(1)),'t':limpia(m.group(2),1500,True)})
with gzip.open('datos/lexica.json.gz','wt',encoding='utf-8') as g: json.dump(out,g,ensure_ascii=False)
print(len(out),'claves;',os.path.getsize('datos/lexica.json.gz')/1e6,'MB')
n=sum(1 for e in D if any(c in out for c in candidatos(e['hw'])))
print('voces con lexicón:',n,'de',len(D))
