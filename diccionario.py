"""Diccionario de Derecho Romano (Instituto Editorial Reus, 1982): texto cifrado en datos/dict.enc, legible solo con la
clave DICT_KEY (variable de entorno en Render). El texto no está en claro en el repositorio y solo sale por el conector MCP."""
import json,os,re
from lexica import norm
HERE=os.path.dirname(os.path.abspath(__file__))
_E=[None]
def cargar():
    if _E[0] is not None: return _E[0]
    _E[0]={'e':[],'k':{},'p':{}}
    k=os.environ.get('DICT_KEY','').strip()
    try:
        from cryptography.fernet import Fernet
        d=json.loads(Fernet(k.encode()).decrypt(open(os.path.join(HERE,'datos','dict.enc'),'rb').read()).decode('utf-8'))
    except Exception: return _E[0]
    E=d['entradas'];_E[0]['e']=E
    for i,e in enumerate(E):
        ws=[norm(w.replace('0','O')) for w in re.split(r'\s+',e['hw']) if norm(w.replace('0','O'))]
        e['_k']=' '.join(ws)
        _E[0]['k'].setdefault(e['_k'],[]).append(i)
        if ws: _E[0]['p'].setdefault(ws[0],[]).append(i)
    return _E[0]
def disponible(): return bool(cargar()['e'])
def buscar(hw,lemas_extra=()):
    """(entradas exactas, nombres de voces relacionadas que empiezan por la misma palabra)"""
    C=cargar()
    if not C['e']: return [],[]
    n=norm(hw);claves=[n]+[x for x in lemas_extra if x]
    try:
        import lemas
        solo={k for k in C['p'] if ' ' not in k}
        claves+=lemas.lematizar(n,solo,3)
    except Exception: pass
    vistos=[];ex=[]
    for k in claves:
        for i in C['k'].get(k,[]):
            if i not in vistos: vistos.append(i);ex.append(C['e'][i])
    rel=[];rv=set()
    for k in claves[:3]:
        for i in C['p'].get(k,[]):
            if i not in vistos and C['e'][i]['hw'] not in rv:
                rv.add(C['e'][i]['hw']);rel.append(C['e'][i]['hw'])
    return ex,rel
def texto(e): return f"{e['hw']}.— {e['t']}"
