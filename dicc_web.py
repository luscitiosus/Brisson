"""Lectura del Diccionario de Derecho Romano (Reus, 1982) en la web, con contraseña (DICT_PASS) y sin texto en el HTML:
cada definición se sirve como imagen PNG generada en el servidor. Sin DICT_PASS o sin DICT_KEY la función queda desactivada."""
import hashlib,hmac,html,io,os,re,time
from urllib.parse import quote
from starlette.responses import Response,RedirectResponse
HERE=os.path.dirname(os.path.abspath(__file__))
def _sello(): return (os.environ.get('DICT_KEY','')+'|'+os.environ.get('DICT_PASS','')).encode()
def _tok(exp): return f"{exp}.{hmac.new(_sello(),str(exp).encode(),hashlib.sha256).hexdigest()[:32]}"
def _ok(request):
    c=request.cookies.get('dk','')
    try: exp,h=c.split('.',1);return int(exp)>time.time() and hmac.compare_digest(c,_tok(int(exp)))
    except Exception: return False
_FONT={}
def _fuente(sz):
    from PIL import ImageFont
    if sz not in _FONT: _FONT[sz]=(ImageFont.truetype(os.path.join(HERE,'fuentes','IbarraRealNova-Regular.ttf'),sz),ImageFont.truetype(os.path.join(HERE,'fuentes','IbarraRealNova-Bold.ttf'),sz))
    return _FONT[sz]
def _png(hw,txt):
    from PIL import Image,ImageDraw
    W,M,SZ=1000,28,30
    f,fb=_fuente(SZ);dr=ImageDraw.Draw(Image.new('RGB',(10,10)))
    lines=[];cur=''
    # la cabecera en negrita va en la primera línea; el resto se ajusta por palabras
    pal=[(w,True) for w in (hw+'.—').split()]+[(w,False) for w in txt.split()]
    x=M;y=M;lh=int(SZ*1.45);runs=[]
    for w,b in pal:
        ft=fb if b else f;ww=dr.textlength(w+' ',font=ft)
        if x+ww>W-M and x>M: x=M;y+=lh
        runs.append((x,y,w,ft));x+=ww
    H=y+lh+M
    im=Image.new('RGB',(W,H),(251,247,238));d=ImageDraw.Draw(im)
    for x,y,w,ft in runs: d.text((x,y),w,font=ft,fill=(30,26,20))
    b=io.BytesIO();im.save(b,'PNG',optimize=True);return b.getvalue()
def montar(mcp,D,pagina,HTMLResponse):
    import diccionario,lexica
    def activo(): return bool(os.environ.get('DICT_PASS')) and diccionario.disponible()
    def ent(n):
        hw=D[n]['hw'];lem=lexica.buscar(hw)[0]
        return diccionario.buscar(hw,[lem] if lem else [])
    def vista(titulo,items,extra=''):
        h=[f"<article><h2>{html.escape(titulo)}</h2><p class='mut'>Diccionario de Derecho Romano, Instituto Editorial Reus, Madrid, 1982. Obra con derechos de autor, mostrada como imagen para lectura personal.</p><form method='get' action='/dicc'><input name='q' placeholder='cabecera o texto…'> <button>Quaere</button></form>"]
        for i,e in items: h.append(f"<p><img src='/dicc.png?i={i}' alt='Definición de {html.escape(e['hw'])}' draggable='false' style='max-width:100%;height:auto;user-select:none;-webkit-user-select:none;-webkit-touch-callout:none' oncontextmenu='return false'></p>")
        h.append(extra+"</article><style>img{pointer-events:none}</style>")
        return ''.join(h)
    @mcp.custom_route("/dicc/estado",methods=["GET"])
    async def estado(request):
        k=os.environ.get('DICT_KEY','').strip();p=os.environ.get('DICT_PASS','')
        try:
            import cryptography;cr='s\u00ed'
        except Exception: cr='NO'
        fe=os.path.exists(os.path.join(HERE,'datos','dict.enc'))
        n=len(diccionario.cargar()['e']) if k else 0
        f=lambda b:'s\u00ed' if b else 'NO'
        return HTMLResponse(pagina(f"<article><h2>Estado del diccionario</h2><ul><li>DICT_KEY definida: {f(k)} (longitud {len(k)}; debe ser 44)</li><li>DICT_PASS definida: {f(p)}</li><li>Archivo datos/dict.enc presente: {f(fe)}</li><li>Biblioteca de cifrado instalada: {cr}</li><li>Entradas descifradas: {n}</li></ul></article>",'','ambas','entrada'))
    @mcp.custom_route("/dicc/login",methods=["GET","POST"])
    async def login(request):
        if not activo(): return HTMLResponse(pagina("<article><h2>Diccionario</h2><p>No está activado en este servidor.</p></article>",'','ambas','entrada'),status_code=404)
        err=''
        nxt=request.query_params.get('next','/dicc')
        if not nxt.startswith('/'): nxt='/dicc'
        if request.method=='POST':
            f=await request.form()
            if hmac.compare_digest(str(f.get('p','')).encode(),os.environ['DICT_PASS'].encode()):
                r=RedirectResponse(nxt,status_code=303);r.set_cookie('dk',_tok(int(time.time())+30*86400),max_age=30*86400,httponly=True,secure=True,samesite='lax');return r
            err="<p><b>Clave incorrecta.</b></p>"
        return HTMLResponse(pagina(f"<article><h2>Diccionario de Derecho Romano</h2>{err}<form method='post' action='/dicc/login?next={quote(nxt)}'><input type='password' name='p' placeholder='Clave' autofocus> <button>Intrare</button></form></article>",'','ambas','entrada'))
    @mcp.custom_route("/dicc",methods=["GET"])
    async def dicc(request):
        if not activo(): return HTMLResponse(pagina("<article><h2>Diccionario</h2><p>No está activado en este servidor.</p></article>",'','ambas','entrada'),status_code=404)
        if not _ok(request): return RedirectResponse('/dicc/login?next='+quote(str(request.url.path)+('?'+request.url.query if request.url.query else '')),status_code=303)
        C=diccionario.cargar();p=request.query_params
        if p.get('n','').isdigit() and int(p['n'])<len(D):
            ex,rel=ent(int(p['n']));items=[(C['e'].index(e),e) for e in ex]
            x=("<p><b>Voces relacionadas:</b> "+' '.join(f"<a href='/dicc?q={quote(r)}'>{html.escape(r)}</a>" for r in rel[:30])+"</p>") if rel else ''
            return HTMLResponse(pagina(vista(D[int(p['n'])]['hw'],items,x),'','ambas','entrada'))
        q=(p.get('q') or '').strip()
        if q:
            qq=' '.join(lexica.norm(w.replace('0','O')) for w in q.split() if lexica.norm(w.replace('0','O')))
            ids=list(C['k'].get(qq,[]))
            for k,li in C['k'].items():
                if len(ids)>=12: break
                if k.startswith(qq): ids+=[i for i in li if i not in ids]
            if not ids:
                rx=re.compile(''.join('[uv]' if c in 'uvUV' else re.escape(c) for c in q),re.I)
                ids=[i for i,e in enumerate(C['e']) if rx.search(e['t'])][:10]
            return HTMLResponse(pagina(vista('«'+q+'»',[(i,C['e'][i]) for i in ids[:12]]),'','ambas','entrada'))
        return HTMLResponse(pagina(vista('Diccionario de Derecho Romano',[]),'','ambas','entrada'))
    @mcp.custom_route("/dicc.png",methods=["GET"])
    async def dpng(request):
        if not activo() or not _ok(request): return Response(status_code=403)
        i=request.query_params.get('i','');C=diccionario.cargar()
        if not i.isdigit() or int(i)>=len(C['e']): return Response(status_code=404)
        e=C['e'][int(i)]
        return Response(_png(e['hw'],e['t']),media_type='image/png',headers={'Cache-Control':'private, no-store','X-Robots-Tag':'noindex'})
