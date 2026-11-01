import re,json,sys
sys.path.insert(0,'.')
import ocrfix,greek2
P=open('w/raw.txt',encoding='utf-8').read().split('\f')
d=json.load(open('/home/claude/brisson/brisson.json'));V=ocrfix.build(d);voc=greek2.build_vocab(d)
ROM=r"[IVXLCxXlViI1]{1,8}"
H1=re.compile(r"^\W*(?:%s)?\W*[IV1l]?\s*I?VSTI\s+HENNINGII\s+BOEHME\s?RI,?\s*IC\.?\s*(?:PRAEFATIO\s+NOVA)?"%ROM,re.I)
H2=re.compile(r"^\W*DE\s+INTERPRET\.?\s*GRAMM\w*\.?\s*IN\s*N?IVR\.?\s*ROM\.?\s*FATIS\s+ET\s+VARI?\s?O?\s?VSV\.?\s*(?:%s)?"%ROM,re.I)
H3=re.compile(r"^\W*PRAEFATIO\s+NOVA\s*(?:%s)?"%ROM,re.I)
out=[]
for n in range(19,62):
    t=' '.join(P[n-1].split())
    t0=t
    for h in (H1,H2,H3): t=h.sub('',t,count=1)
    if n==19: t=re.sub(r'^.*?(?=IVSTI)','',t,count=1)
    t=ocrfix.fix_text(t,V)
    t=re.sub(r'(?<=[a-zæœ])- (?=[a-zæœ]{2,})','',t)
    # saltos de párrafo en cada § 
    t=re.sub(r'\s+(§\.?\s*[IVXLxl]{1,6}\.)',r'\n\n\1',t)
    out.append({'n':n,'t':t.strip(),'cab':t0!=t})
json.dump({'titulo':'Praefatio nova de Justus Henning Boehmer: De interpretationis grammaticae fatis et usu vario in iure Romano','paginas':out},open('/home/claude/brisson/prefacio.json','w',encoding='utf-8'),ensure_ascii=False)
print(sum(o['cab'] for o in out),'cabeceras quitadas de',len(out))
print(out[0]['t'][:700]);print('----');print(out[5]['t'][:600])
