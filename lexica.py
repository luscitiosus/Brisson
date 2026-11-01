"""Léxicos de apoyo (Perseus Digital Library, CC BY-SA 4.0): Lewis & Short, A Latin Dictionary (1879) y
Lewis, An Elementary Latin Dictionary (1890). Datos precalculados en datos/lexica.json.gz por lexica_build.py."""
import gzip,json,os,re,unicodedata
HERE=os.path.dirname(os.path.abspath(__file__))
def norm(w):
    w=unicodedata.normalize('NFD',w.lower());w=''.join(c for c in w if unicodedata.category(c)!='Mn')
    return re.sub(r'[^a-z]','',w.replace('v','u').replace('j','i').replace('æ','ae').replace('œ','oe'))
ENDS=sorted(['ibus','orum','arum','antur','untur','abat','ebat','are','ere','ire','ari','ent','ant','unt','ium','um','us','is','es','os','as','ae','am','em','im','ui','ti','tur','at','et','it','i','o','a','e','u','s','m'],key=len,reverse=True)
SUF=('us','um','a','o','is','e','are','ere','ire','or','ium','es','ia','io','er','i','ans','ens')
def candidatos(hw):
    n=norm(hw);c=(infinitivo(hw) or [])+[n]
    for s in ENDS:
        if n.endswith(s) and len(n)-len(s)>=3:
            st=n[:-len(s)]
            for x in SUF:
                if st+x not in c: c.append(st+x)
    return c
_ESP={'esse':['sum'],'posse':['possum'],'ferre':['fero'],'velle':['volo'],'nolle':['nolo'],'malle':['malo'],'ire':['eo'],'fieri':['fio'],'dare':['do'],'stare':['sto'],'edere':['edo'],'ferri':['feror'],'quire':['queo'],'nequire':['nequeo']}
_PRE_F=['af','adf','of','obf','suf','subf','dif','dis','ef','ex','in','con','de','per','prae','pro','re','trans','au','ab','circum','inter','ad','ob','sub','anti','ante']
_ASIM=[(a+c,b+c) for a,b,cs in (('ad','ac','c'),('ad','af','f'),('ad','ag','g'),('ad','al','l'),('ad','an','n'),('ad','ap','p'),('ad','ar','r'),('ad','as','s'),('ad','at','t'),('in','im','p'),('in','im','b'),('in','im','m'),('in','il','l'),('in','ir','r'),('con','com','p'),('con','com','b'),('con','com','m'),('con','col','l'),('con','cor','r'),('sub','suc','c'),('sub','suf','f'),('sub','sug','g'),('sub','sum','m'),('sub','sup','p'),('ob','oc','c'),('ob','of','f'),('ob','op','p'),('ex','ef','f')) for c in [cs]]
_ASIM+=[('adgn','agn'),('adsc','asc'),('adst','ast'),('adsp','asp'),('adqu','acqu'),('inl','ill'),('obi','obi'),('negl','negl')]
def infinitivo(hw):
    """Lemas posibles (primera persona) si hw es un infinitivo; None si no lo parece."""
    n=norm(hw)
    if n in _ESP: return list(_ESP[n])
    if n.endswith('esse') and len(n)>5: p=n[:-4]; return [p+'sum']+([ 'ad'+n[2:-4]+'sum'] if False else [])
    if n.endswith('ferre') and len(n)>6:
        p=n[:-5];c=[p+'fero']
        if p.startswith('af'): c.append('adfero')
        if p.startswith('of'): c.append('obfero')
        if p.startswith('suf'): c.append('subfero')
        return c
    out=[]
    for fin,sus in (('are',['o']),('ere',['eo','io','o']),('ire',['io','eo']),('ari',['or','o']),('eri',['eor','eo','or']),('iri',['ior','io','or'])):
        if n.endswith(fin) and len(n)-3>=2:
            out+=[n[:-3]+x for x in sus]
    if not out: return None
    res=[]
    for x in out:
        res.append(x)
        for a,b in _ASIM:
            if x.startswith(a) and b+x[len(a):] not in res: res.append(b+x[len(a):]); 
    return res
_VERBO=re.compile(r'\bv\. (?:a|n|dep|freq|inch|desid|intens)\b|\bverb\b|v\. a\.|v\. n\.|v\. dep\.')
_L={}
def cargar():
    if not _L:
        try: _L.update(json.load(gzip.open(os.path.join(HERE,'datos','lexica.json.gz'),'rt',encoding='utf-8')))
        except Exception: _L['_vacio']=1
    return _L
def buscar(hw):
    L=cargar()
    for k in (infinitivo(hw) or []):
        v=L.get(k)
        if v and any(_VERBO.search(x['t'][:400]) for x in v.get('ls',[])+v.get('el',[])): return k,v
    for k in candidatos(hw):
        if k in L: return k,L[k]
    return None,None
