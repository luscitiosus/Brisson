"""Párrafos numerados (§.) y letras capitales omitidas en la Praefatio: «5. I Rudenter» → «§. I.  Prudenter»."""
import re,json,collections
def rom(s):
    s=s.upper().replace('L','I') if False else s
    s=re.sub('[l1|]','I',s).upper()
    v={'I':1,'V':5,'X':10,'L':50}
    try:
        tot=0
        for i,c in enumerate(s):
            x=v[c]
            tot+= -x if i+1<len(s) and v[s[i+1]]>x else x
        return tot
    except KeyError: return None
def toroman(n):
    out='';
    for v,s in((50,'L'),(40,'XL'),(10,'X'),(9,'IX'),(5,'V'),(4,'IV'),(1,'I')):
        while n>=v: out+=s;n-=v
    return out
d=json.load(open('brisson.json'));V=collections.Counter()
for e in d:
    for s in e['segs']:
        for w in re.findall(r"[a-zæœ]{3,}",s['t']): V[w]+=1
P=json.load(open('prefacio.json'))
exp=1;found=[]
RX=re.compile(r"(?<![\w§])(?:§|5|S|\$)\s*\.?\s*([IVXLl1|]{1,6})\s*\.?\s+(?=[A-Za-zæœ])")
for pg in P['paginas']:
    t=pg['t']
    def r(m):
        global exp
        v=rom(m.group(1))
        if v==exp:
            found.append(v);exp+=1
            return '\n\n§. '+toroman(v)+'. '
        return m.group(0)
    t=RX.sub(r,t)
    # capital omitida: primera palabra tras §. N.
    def cap(m):
        w=m.group(2)
        if V.get(w.lower(),0)>=3 or len(w)<4: return m.group(0)
        for ch in 'pqscdtmrnabeifglouvhx':
            c=ch+w.lower()
            if V.get(c,0)>=8:
                return m.group(1)+ (ch.upper()+w)
        return m.group(0)
    t=re.sub(r"(§\. [IVXL]+\. )([A-Za-zæœ]+)",cap,t)
    pg['t']=t
print('§ encontrados',found)
json.dump(P,open('prefacio.json','w',encoding='utf-8'),ensure_ascii=False)
txt=' '.join(p['t'] for p in P['paginas'])
print(re.findall(r'§\. [IVXL]+\. \S+ \S+',txt)[:40])
