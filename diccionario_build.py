"""Uso (en local, con el .txt sacado con pdftotext): DICT_KEY=<clave> python diccionario_build.py dict.txt
Genera datos/dict.enc, cifrado con Fernet. NO subir el .txt al repositorio."""
import json,os,re,sys
from cryptography.fernet import Fernet
t=open(sys.argv[1],encoding='utf-8',errors='replace').read().replace('­\n','').replace('\x0c','\n')
L=t.split('\n')
HEAD=re.compile(r"^([A-ZÁÉÍÓÚÑÜ0-9][A-ZÁÉÍÓÚÑÜ0-9 ,;()/'’\-\.]{0,90}?)\.\s?-\s?(.*)$")
ent=[];cur=None
for l in L:
    s=l.rstrip()
    if re.match(r'^\s*\d+\.?\s*$',s): continue
    if re.match(r"^\s+[A-ZÁÉÍÓÚÑÜ0-9 ,;()/'\-\.]+\s-\s[A-ZÁÉÍÓÚÑÜ0-9 ,;()/'\-\.]+$",s): continue   # cabecera de página
    m=HEAD.match(s)
    if m and not s.startswith(' '):
        if cur: ent.append(cur)
        cur={'hw':m.group(1).strip(),'t':m.group(2).strip()}
    elif cur is not None and s.strip():
        cur['t']+=' '+s.strip()
if cur: ent.append(cur)
# el cuerpo empieza en 'AB U. C.' (se descarta el prólogo)
i0=next((i for i,e in enumerate(ent) if e['hw'].startswith('AB')),0)
ent=ent[i0:]
for e in ent: e['t']=re.sub(r'\s+',' ',e['t']).strip()
print(len(ent),'entradas;',sum(len(e['t']) for e in ent)//1000,'KB')
k=os.environ['DICT_KEY'].encode()
open('datos/dict.enc','wb').write(Fernet(k).encrypt(json.dumps({'fuente':'Diccionario de Derecho Romano, Instituto Editorial Reus, Madrid, 1982','entradas':ent},ensure_ascii=False).encode('utf-8')))
print(os.path.getsize('datos/dict.enc')/1e6,'MB')
