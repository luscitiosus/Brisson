"""Texto de las XII Tablas (The Latin Library, dominio público) -> datos/xii.json, por tablas y fragmentos."""
import json,re,sys
t=open(sys.argv[1],encoding='utf-8',errors='ignore').read()
import re as _r;i=_r.search(r'TABULA I\s*\n',t).start();t=t[i:]
t=t[:t.find('Ius Romanum The Latin Library')] if 'Ius Romanum The Latin Library' in t else t
R={'I':1,'II':2,'III':3,'IV':4,'V':5,'VI':6,'VII':7,'VIII':8,'IX':9,'X':10,'XI':11,'XII':12}
parts=re.split(r'\n\s*TABULA ([IVX]+)\s*\n',"\n"+t)
out={}
for k in range(1,len(parts),2):
    n=R[parts[k]];bl=[]
    for b in re.split(r'\n[ \t]*\n',parts[k+1]):
        b=re.sub(r'\s+',' ',b).strip()
        if b and b not in('.','. .'): bl.append({'t':b,'x':b.startswith('(')})
    out[n]=bl
json.dump(out,open('datos/xii.json','w'),ensure_ascii=False)
print({k:len(v) for k,v in out.items()})
