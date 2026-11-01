"""Construye datos/whitaker.json.gz: glosas breves en inglés de Whitaker's Words (DICTLINE.GEN + INFLECTS.LAT)
para las voces de Brisson que no tienen entrada en Lewis & Short. Uso: python ww_build.py <carpeta whitakers-words> brisson.json"""
import gzip,json,os,re,sys
from lexica import norm,buscar
RAIZ,JS=sys.argv[1],sys.argv[2]
D=json.load(open(JS,encoding='utf-8'))
fins=set()
for ln in open(os.path.join(RAIZ,'INFLECTS.LAT'),encoding='latin-1'):
    p=ln.split('--')[0].split()
    if len(p)>=8 and p[0] in('N','ADJ','V','PRON','NUM'):
        try: fins.add(p[7].lower() if p[6].isdigit() and p[7]!='0' else '')
        except Exception: pass
    # el sufijo es el campo tras las dos cifras de longitud
for ln in open(os.path.join(RAIZ,'INFLECTS.LAT'),encoding='latin-1'):
    p=ln.split('--')[0].split()
    for i,x in enumerate(p[:-2]):
        if x.isdigit() and i+1<len(p) and p[i+1].isdigit() and len(p)>i+2 and p[i+2].isalpha() and i>=3:
            fins.add(p[i+2].lower() if int(x)>0 else '');break
fins.add('')
ST={}
for ln in open(os.path.join(RAIZ,'DICTLINE.GEN'),encoding='latin-1'):
    ln=ln.rstrip('\r\n')
    if len(ln)<110: continue
    st=[ln[i*19:(i+1)*19].strip() for i in range(4)]
    rest=ln[76:].split(None,1)
    if not rest: continue
    pos=rest[0]
    if pos not in('N','ADJ','V','ADV','PREP','CONJ','PRON','NUM','INTERJ'): continue
    g=ln[110:].strip().lstrip('|').strip().rstrip(';').strip()
    if not g: continue
    for s in set(st[:2]):
        if s and s!='zzz':
            ST.setdefault(norm(s),[]).append((pos,g[:220],s))
out={}
for e in D:
    if buscar(e['hw'])[0]: continue
    n=norm(e['hw'])
    for cut in range(len(n),3,-1):
        if n[cut:] in fins and n[:cut] in ST:
            pos,g,s=ST[n[:cut]][0]
            out[n]={'s':s,'p':pos,'g':g};break
        if n in ST and cut==len(n): pass
with gzip.open('datos/whitaker.json.gz','wt',encoding='utf-8') as f: json.dump(out,f,ensure_ascii=False)
print(len(fins),'terminaciones;',len(ST),'raíces;',len(out),'voces con glosa')
print(list(out.items())[:8])
