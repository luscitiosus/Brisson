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
    n=norm(hw);c=[n]
    for s in ENDS:
        if n.endswith(s) and len(n)-len(s)>=3:
            st=n[:-len(s)]
            for x in SUF:
                if st+x not in c: c.append(st+x)
    return c
_L={}
def cargar():
    if not _L:
        try: _L.update(json.load(gzip.open(os.path.join(HERE,'datos','lexica.json.gz'),'rt',encoding='utf-8')))
        except Exception: _L['_vacio']=1
    return _L
def buscar(hw):
    L=cargar()
    for k in candidatos(hw):
        if k in L: return k,L[k]
    return None,None
