"""Servidor MCP «Brisson»: De verborum quae ad ius pertinent significatione (Brisson, ed. Heineccio, Halle 1743).
Texto íntegro, sin recortar citas, en capas: Brisson / tramos que terminan en nota de Heineccio (HEIN.) / corchetes.

    python server.py            # HTTP (Streamable HTTP) en 0.0.0.0:$PORT$MCP_PATH, para claude.ai y el móvil
    python server.py --stdio    # stdio, para Claude Desktop en local
"""
import json,re,os,sys
from mcp.server.fastmcp import FastMCP, Image
HERE=os.path.dirname(os.path.abspath(__file__))
import urn_halle
INSTRUCTIONS="""Léxico jurídico latino de Brisson con las notas de Heineccio (1743). `brisson(palabra)` da la entrada con el texto íntegro y las citas ya convertidas a numeración moderna entre [corchetes] (D., C.); la capa dice qué es de Brisson y qué termina en HEIN. `brisson_texto` busca dentro de todas las entradas. El griego del OCR es ilegible y aparece como ⟦griego⟧: da al usuario el enlace de la página y pídele una captura de la línea; con `ligaturas_griegas` tienes la lámina de nexos para leerla. Lo que leas en una imagen es lectura tuya, no texto verificado: dilo. Los números de las citas pueden tener errores de OCR; no los des por buenos sin contrastarlos con el conector de fuentes romanas."""
_SECRET=os.environ.get("MCP_SECRET","").strip("/")
PATH=os.environ.get("MCP_PATH") or (f"/{_SECRET}/mcp" if _SECRET else "/mcp")
mcp=FastMCP("Brisson",instructions=INSTRUCTIONS,host="0.0.0.0",port=int(os.environ.get("PORT","8000")),streamable_http_path=PATH,stateless_http=True,json_response=True)
@mcp.custom_route("/healthz",methods=["GET"])
async def healthz(request):
    from starlette.responses import PlainTextResponse
    return PlainTextResponse("ok")
D=json.load(open(os.path.join(HERE,'brisson.json'),encoding='utf-8'))
BY={}
for i,e in enumerate(D): BY.setdefault(e['key'],[]).append(i)
KEYS=sorted(BY)
LAB={'T':'Heineccio','C':'corchetes'}
def imagen_url(n):
    """Enlace persistente a la imagen de la página en la edición de Halle (VD18 10747656)."""
    return "https://nbn-resolving.org/"+urn_halle.url_p(n)
def key(w):
    w=w.lower().replace('æ','ae').replace('œ','oe').replace('j','i').replace('u','v')
    return re.sub(r'[^a-z]','',w)
ENDS=['ibus','orum','arum','antur','untur','abat','ebat','are','ere','ire','ari','ent','ant','unt','ium','um','us','is','es','os','as','ae','am','em','im','ui','ti','tur','at','et','it','i','o','a','e','u','s','m']
def stems(k):
    out=[k]
    for s in ENDS:
        if k.endswith(s) and len(k)-len(s)>=3: out.append(k[:-len(s)])
    return list(dict.fromkeys(out))
def imagen_url(n):
    """Enlace persistente a la imagen de la página en la edición de Halle (VD18 10747656)."""
    return "https://nbn-resolving.org/"+urn_halle.url_p(n)
def render(idxs,capa):
    parts=[]
    for i in idxs:
        e=D[i];nT=sum(1 for s in e['segs'] if s['k']=='T')
        ng=e.get('ngr',0)
        parts.append(f"## {e['hw']} (PDF p.{e['page']}; tramos con nota de Heineccio: {nT}"+(f"; {ng} pasaje(s) en griego ilegible ⟦griego⟧ → imagen: {imagen_url(e['page'])}" if ng else "")+")")
        for s in e['segs']:
            if s['k']=='T' and capa in('ambas','heineccio'): parts.append("[Tramo que termina en HEIN.] "+s['t'])
            elif s['k']=='B' and capa in('ambas','brisson'): parts.append("[Brisson] "+s['t'])
            elif s['k']=='C' and capa in('ambas','corchetes'): parts.append("[Entre corchetes en la edición] "+s['t'])
    return "\n".join(parts)
@mcp.tool()
def brisson(palabra:str,capa:str="ambas",parte:int=1,max_caracteres:int=6000)->str:
    """Entrada de Brisson para una palabra latina (u/v, i/j indiferentes; admite formas flexionadas simples). capa: ambas|brisson|heineccio|corchetes. Texto íntegro con citas; si es largo, usa parte=2,3…"""
    k=key(palabra)
    for st in stems(k):
        idx=BY.get(st)
        if idx: break
    else:
        cand=[x for x in KEYS if x.startswith(stems(k)[-1])][:15]
        if not cand: return f"Sin entrada para «{palabra}». Prueba brisson_texto."
        return "Sin coincidencia exacta. Entradas próximas: "+", ".join(D[BY[c][0]]['hw'] for c in cand)
    txt=render(idx,capa)
    n=max(1,-(-len(txt)//max_caracteres)); parte=max(1,min(parte,n))
    out=txt[(parte-1)*max_caracteres:parte*max_caracteres]
    return out+(f"\n[parte {parte}/{n}]" if n>1 else "")
@mcp.tool()
def brisson_texto(consulta:str,limite:int=15)->str:
    """Busca una palabra dentro del texto de todas las entradas (también la que no es cabecera). Devuelve cabecera, página y un fragmento corto."""
    q=re.compile(''.join('[uv]' if c in 'uvUV' else re.escape(c) for c in consulta),re.I)
    res=[]
    for e in D:
        for s in e['segs']:
            m=q.search(s['t'])
            if m:
                a=max(0,m.start()-60);res.append(f"{e['hw']} (p.{e['page']}, {LAB.get(s['k'],'Brisson')}): …{s['t'][a:m.end()+60]}…");break
        if len(res)>=limite:break
    return "\n".join(res) or "Sin resultados."

@mcp.tool()
def brisson_pagina(pagina:int)->str:
    """Enlace a la imagen de una página del libro (el número que muestran las entradas como «PDF p.N»), para ver el griego o comprobar una cita."""
    return imagen_url(pagina)
@mcp.tool()
def ligaturas_griegas()->Image:
    """Lámina de ligaturas y abreviaturas del griego impreso (C. Cobley). Úsala para leer el griego de una captura del libro."""
    return Image(data=open(os.path.join(HERE,'ligaturas_griegas.png'),'rb').read(),format='png')
if __name__=="__main__":
    if "--stdio" in sys.argv: mcp.run("stdio")
    else:
        print(f"Escuchando en http://0.0.0.0:{mcp.settings.port}{PATH}",file=sys.stderr)
        mcp.run("streamable-http")
