import json,sys
sys.path.insert(0,'.')
import griego_detector as greek2
d=json.load(open('brisson.json'))
voc=greek2.build_vocab(d)
M='⟦griego⟧'
tot=0;ent=0
for e in d:
    g=0
    for s in e['segs']:
        t=s['t'];R=[(a,b) for a,b in greek2.runs(t,voc) if any(ord(c)>127 and c!='ſ' for c in t[a:b])]
        if not R: continue
        orig=[];out=[];p=0
        for a,b in R:
            out.append(t[p:a]);out.append(M);orig.append(t[a:b]);p=b
        out.append(t[p:]);s['t']=''.join(out);s['gr']=orig;g+=len(R)
    if g: e['ngr']=g;ent+=1;tot+=g
json.dump(d,open('brisson.json','w',encoding='utf-8'),ensure_ascii=False)
print(tot,'tramos en',ent,'entradas')
