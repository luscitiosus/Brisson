"""Lematizador heurístico: de una forma flexionada (cabecera de Brisson) a posibles lemas de Lewis & Short.
Solo devuelve lemas que existen en el conjunto de claves dado (el índice completo de L&S/Elementary)."""
import re
ASIM=[('adg','agg'),('adgn','agn'),('adc','acc'),('adt','att'),('adf','aff'),('adl','all'),('adn','ann'),('adp','app'),('adr','arr'),('ads','ass'),('adsc','asc'),('adst','ast'),('adsp','asp'),('adq','acq'),
('inp','imp'),('inb','imb'),('inm','imm'),('inl','ill'),('inr','irr'),('conl','coll'),('conm','comm'),('conp','comp'),('conb','comb'),('conr','corr'),
('subc','succ'),('subp','supp'),('subf','suff'),('subg','sugg'),('subm','summ'),('obc','occ'),('obp','opp'),('obf','off'),('exf','eff'),('disf','diff')]
def variantes(n):
    v=[n]
    for a,b in ASIM:
        if n.startswith(a) and len(n)>len(a)+2: v.append(b+n[len(a):])
    return v
OBL=['ia','ionibus','ionum','ionem','ionis','iones','ione','ibus','orum','arum','ntium','ntibus','ntis','ntem','ntes','nte','tatis','tatem','tates','tate','ium','ibus','is','es','em','um','os','as','am','ae','ei','ui','us','i','e','a','o','u']
LE=['','us','a','um','er','ir','is','e','es','s','x','o','io','or','as','ns','men','al','ar','ex','ps','t','tas','tus','tio','sio','ia','ium','ius','eus','ator','trix','tor','c','l','r','n','ans','ens','ex','ix','ax','ox','ux','ur']
VERB=['abatur','abantur','abat','abant','abit','abunt','atur','antur','ant','at','aret','arent','aui','auit','auerunt','atus','ata','atum','ati','atae','atos','atis','ando','andi','endi','endo','ent','et','ebat','ebant','ebit','ui','uit','uerunt','itus','ita','itum','iti','it','unt','untur','itur','imus','amus','emus','tur','nt','t','antis','antes','ans','entis','entes','ens','iendi','iens','ientis','iat','ias','ere','ari','eri','iri','are','ire']
VL=['o','eo','io','or','eor','ior','sco','scor']
def _esp(st):
    r=[]
    if st.endswith('ion') : r.append(st[:-3]+'io')
    if st.endswith('in') : r.append(st[:-2]+'o')
    if st.endswith('ent'): r.append(st[:-3]+'ens')
    if st.endswith('ant'): r.append(st[:-3]+'ans')
    if st[-1:] in 'gc': r.append(st[:-1]+'x')
    if st.endswith(('ic','ig')): r.append(st[:-2]+'ex')
    if st.endswith('ud'): r.append(st[:-2]+'ut')
    if st.endswith('or') : r.append(st)   # ya nominativo
    if st.endswith('ar'): r.append(st+'e')
    if st.endswith('al'): r.append(st+'e')
    if st.endswith('ili'): r.append(st[:-1]+'is')
    return r
def lematizar(n,keys,max_=2):
    out=[]
    def add(c):
        if len(c)>=3 and c in keys and c not in out: out.append(c)
    for h in variantes(n):
        add(h)
        for fe in sorted(OBL,key=len,reverse=True):
            if h.endswith(fe) and len(h)-len(fe)>=2:
                st=h[:-len(fe)]
                if fe.startswith('ion'): add(st+'io'); continue
                if fe.startswith('tat'): add(st+'tas'); continue
                if fe.startswith('nti') or fe in('ntes','nte','ntem'): add(st+'ns'); add(st+'ntia'); add(st+'nt')
                for c in _esp(st): add(c)
                for x in LE: add(st+x)
        for fe in sorted(VERB,key=len,reverse=True):
            if h.endswith(fe) and len(h)-len(fe)>=2:
                st=h[:-len(fe)]
                for x in VL: add(st+x)
        if len(out)>=max_: break
    return out[:max_]
