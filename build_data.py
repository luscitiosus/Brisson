"""Construye data/brisson.json a partir de brisson_entries.json (entradas ya separadas y con citas convertidas)."""
import json,re,sys
H=re.compile(r'H\s?E\s?I\s?N\.')
def key(w):
    w=w.lower().replace('æ','ae').replace('œ','oe').replace('j','i').replace('u','v')
    return re.sub(r'[^a-z]','',w)
src=sys.argv[1]; out=sys.argv[2]
E=json.load(open(src,encoding='utf-8'))
res=[]
for e in E:
    t=e['text'];segs=[];pos=0
    for m in H.finditer(t):
        segs.append({'k':'T','t':t[pos:m.end()].strip()});pos=m.end()
    rest=t[pos:].strip()
    if rest: segs.append({'k':'C' if e.get('br') else 'B','t':rest})
    res.append({'hw':e['hw'],'key':key(e['hw']),'page':e['page'],'segs':segs})
json.dump(res,open(out,'w',encoding='utf-8'),ensure_ascii=False)
print(len(res),'entradas')
