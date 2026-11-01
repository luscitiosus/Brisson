"""Página web de consulta (sin Claude) para el léxico de Brisson: / (buscador), con paginación mínima y sin JavaScript."""
import html,re
from urllib.parse import quote
from starlette.responses import HTMLResponse

CSS="""
:root{--bg:#fbf8f1;--fg:#1d1b17;--mut:#6b655a;--line:#ddd5c4;--hein:#8a3b12;--hbg:#f6ebdd;--cor:#1f4e79;--cbg:#e9f0f7;--card:#fffdf8}
@media(prefers-color-scheme:dark){:root{--bg:#16140f;--fg:#ece6d8;--mut:#a39c8c;--line:#3a352a;--hein:#e3a06b;--hbg:#2a2117;--cor:#8fbbe3;--cbg:#16222e;--card:#1c1912}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:18px/1.55 Georgia,'Times New Roman',serif}
main{max-width:46rem;margin:0 auto;padding:1rem 16px 3rem}
h1{font-size:1.5rem;margin:.6rem 0 .1rem}.sub{color:var(--mut);font-size:.9rem;margin:0 0 1rem}
form{display:flex;gap:.5rem;flex-wrap:wrap;margin:.8rem 0}
input[type=text]{flex:1 1 12rem;font:inherit;padding:.55rem .7rem;border:1px solid var(--line);border-radius:6px;background:var(--card);color:var(--fg)}
button{font:inherit;padding:.55rem 1rem;border:1px solid var(--fg);background:var(--fg);color:var(--bg);border-radius:6px;cursor:pointer}
.opts{width:100%;font-size:.9rem;color:var(--mut)}.opts label{margin-right:1rem;white-space:nowrap}
article{border:1px solid var(--line);background:var(--card);border-radius:8px;padding:.2rem 1rem 1rem;margin:1rem 0}
article h2{font-size:1.25rem;margin:.8rem 0 .1rem}.meta{color:var(--mut);font-size:.85rem;margin-bottom:.6rem}
.seg{text-align:justify;text-justify:inter-word;hyphens:auto;-webkit-hyphens:auto;overflow-wrap:break-word;margin:.6rem 0;padding:.1rem 0 .1rem .8rem;border-left:3px solid var(--line)}
.seg.T{border-color:var(--hein);background:var(--hbg)}.seg.C{border-color:var(--cor);background:var(--cbg)}
.tag{display:block;font:600 .72rem/1.3 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.04em;color:var(--mut);margin:.3rem 0 0}
.T .tag{color:var(--hein)}.C .tag{color:var(--cor)}
.gr{background:var(--line);padding:0 .3em;border-radius:3px;font-size:.85em}
.ref{color:var(--cor);font-size:.9em}
i{font-style:italic}details{margin:1.6rem 0;border:1px solid var(--line);border-radius:8px;background:var(--card);padding:.2rem 1rem}summary{cursor:pointer;font-weight:600;padding:.6rem 0}.pf p{margin:.7rem 0;text-align:justify}.pf .pn{font:.75rem system-ui,sans-serif;color:var(--mut);display:block;margin-top:1rem}figure.fr{margin:.6rem auto 1rem;max-width:26rem;text-align:center}figure.fr img{width:100%;height:auto;border-radius:6px;border:1px solid var(--line)}figcaption{font-size:.78rem;color:var(--mut);margin-top:.3rem}button.vers{display:block;margin:1rem auto .2rem;padding:.55rem clamp(.5rem,3vw,1.4rem) .6rem;max-width:100%;text-align:center;cursor:pointer;color:#2b1d10;background:radial-gradient(ellipse at 50% 40%,#f3e6c8,#e3cf9f);border:1px solid #2b1d10;outline:3px double #2b1d10;outline-offset:-6px;border-radius:3px;box-shadow:0 1px 0 #fff8 inset,0 2px 4px #0004;font-family:Georgia,'Times New Roman',serif}
button.vers .t{display:block;font-variant:small-caps;letter-spacing:.22em;font-size:1.05rem;font-weight:bold}
button.vers .s:before{content:"\\2766\\00a0"}button.vers .s:after{content:"\\00a0\\2766"}
button.vers .s{display:block;font-style:italic;font-size:clamp(.78rem,4.3vw,1.02rem);white-space:nowrap}
button.vers:hover,button.vers:focus{background:radial-gradient(ellipse at 50% 40%,#2b1d10,#4a3320);color:#f3e6c8}
.vmsg{text-align:center;font-size:.8rem;color:var(--mut);min-height:1.1em}
a{color:var(--cor)}ul.c{columns:2;padding-left:1.1rem}.mut{color:var(--mut)}
footer{margin-top:2rem;font-size:.82rem;color:var(--mut);border-top:1px solid var(--line);padding-top:.8rem}

abbr.au{text-decoration:underline dotted var(--cor);text-underline-offset:3px;cursor:help}nav.top{display:flex;gap:.4rem 1.1rem;flex-wrap:wrap;justify-content:center;font-variant:small-caps;letter-spacing:.12em;font-size:1rem;margin:.2rem 0 .6rem;padding:.35rem 0;border-top:1px solid var(--line);border-bottom:1px solid var(--line)}
nav.top a{text-decoration:none;color:var(--fg)}nav.top a:hover{color:var(--hein)}
.pn2{display:flex;gap:.6rem;margin:1rem 0 .2rem}.pn2 .sp{flex:1}
a.nv.top{margin-top:.2rem}table.tb{width:100%;border-collapse:collapse;font-size:.88rem}table.tb th,table.tb td{border-bottom:1px solid var(--line);padding:.25rem .35rem;text-align:left;vertical-align:top}table.tb th{font:600 .72rem system-ui,sans-serif;text-transform:uppercase;color:var(--mut)}a.nv{flex:1 1 0;min-width:0;display:block;text-align:center;text-decoration:none;color:#2b1d10;padding:.45rem .5rem .5rem;background:radial-gradient(ellipse at 50% 40%,#f3e6c8,#e3cf9f);border:1px solid #2b1d10;outline:3px double #2b1d10;outline-offset:-5px;border-radius:3px;box-shadow:0 1px 0 #fff8 inset,0 2px 4px #0004;font-variant:small-caps;letter-spacing:.14em;font-size:1rem;font-weight:bold}
a.nv small{display:block;font:italic .8rem Georgia,serif;letter-spacing:0;font-variant:normal;font-weight:normal;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
a.nv:hover,a.nv:focus{background:radial-gradient(ellipse at 50% 40%,#2b1d10,#4a3320);color:#f3e6c8}
.abc{display:flex;flex-wrap:wrap;gap:.3rem;justify-content:center;margin:.8rem 0}.abc a{min-width:2.1rem;text-align:center;padding:.25rem .3rem;border:1px solid var(--line);border-radius:4px;background:var(--card);text-decoration:none;font-weight:bold}
.abc a small{display:block;font:.62rem system-ui,sans-serif;color:var(--mut);font-weight:normal}
.vd{border:1px solid var(--hein);background:var(--hbg);border-radius:8px;padding:.4rem 1rem .8rem;margin:1rem 0}.vd h3{margin:.4rem 0;font-variant:small-caps;letter-spacing:.14em}
details.ab>summary{font-size:1.1rem}details.ab details{margin:.4rem 0;padding:.1rem .8rem}
@media(max-width:480px){body{font-size:17px}ul.c{columns:1}}
"""
I0,I1='\ue000','\ue001'
_VID=re.compile(r"(?<![A-Za-zæœ])[Vv]id(?:e\b|\.)")
_OKTOK=re.compile(r"^(?:(?:Tomo|Tom|Libro|Lib|Capite|Cap|Titulo|Tit|Epist|Orat)\.?,?|[A-ZÆŒ][A-Za-zæœ]{0,12}\.,?|[A-ZÆŒ]{3,}[.,]?|[IVXLCDM]{1,7}(?:\.[IVXLCDM]{1,7})?[.,]?|\d+[.,;]?|[a-z]{1,4}\.,?|[a-z]{1,4}\.\d+[.,;]?|§\.?\d*[.,]?|infra|supra|seq\.|sqq?\.)$")
_STOPW={'et','vel','vt','id','est','quae','quod','sed','de','in','cum','ad'}
def _vid(t):
    """Tras «vid.»/«vide» viene una cita: la pongo en cursiva hasta la primera palabra que ya no lo parece."""
    out=[];pos=0
    for m in _VID.finditer(t):
        if m.start()<pos: continue
        i=m.end();n=0;end=i
        for tm in re.finditer(r"\s+(\S+)",t[i:]):
            tok=tm.group(1).strip(I0+I1)
            if tok.lower().rstrip('.,;') in _STOPW or not _OKTOK.match(tok): break
            end=i+tm.end();n+=1
            if n>=12 or tok.endswith(('.',)) and False: break
        if end>i:
            out.append(t[pos:m.start()]+I0+t[m.start():end]+I1);pos=end
    out.append(t[pos:]);return ''.join(out)
def _fmt(t):
    t=html.escape(_vid(t))
    t=re.sub(r'\[((?:D|C|CTh|I|N)\.[^\]]*)\]',r'<span class="ref">[\1]</span>',t)
    t=t.replace('⟦griego⟧','<span class="gr" title="griego ilegible en el OCR: mira la imagen de la página">⟦griego⟧</span>')
    res=[];d=0
    for ch in t:
        if ch==I0:
            if d==0: res.append('<i>')
            d+=1
        elif ch==I1:
            if d==1: res.append('</i>')
            d=max(0,d-1)
        else: res.append(ch)
    if d>0: res.append('</i>')
    return ''.join(res)
_D=[]
def _navbtn(i):
    a=f"<a class='nv' href='/entrada?n={i-1}'>&#9756; Vox prior<small>{html.escape(_D[i-1]['hw'])}</small></a>" if i>0 else "<span class='sp'></span>"
    b=f"<a class='nv' href='/entrada?n={i+1}'>Vox posterior &#9758;<small>{html.escape(_D[i+1]['hw'])}</small></a>" if i<len(_D)-1 else "<span class='sp'></span>"
    return f"<div class='pn2'>{a}{b}</div>"
def _entrada(e,capa,imagen_url,i=None):
    nT=sum(1 for s in e['segs'] if s['k']=='T');ng=e.get('ngr',0)
    out=[f"<article><h2>{html.escape(e['hw'])}</h2><div class='meta'>p. {e['page']} del PDF · "
         f"<a href='{html.escape(imagen_url(e['page']))}' target='_blank' rel='noopener'>ver la página</a>"
         +(f" · {ng} pasaje(s) en griego" if ng else "")+f" · {nT} tramo(s) con nota de Heineccio</div>"]
    if i is not None and _D: out.append(_navbtn(i))
    for s in e['segs']:
        k=s['k']
        if capa=='brisson' and k!='B' or capa=='heineccio' and k!='T' or capa=='corchetes' and k!='C': continue
        tag={'T':'Tramo que termina en HEIN. (nota de Heineccio)','B':'Brisson','C':'Entre corchetes en la edición'}[k]
        out.append(f"<div class='seg {k}' lang='la'><span class='tag'>{tag}</span>{_fmt(s.get('h',s['t']))}</div>")
    if i is not None and _D: out.append(_navbtn(i))
    out.append("</article>");return ''.join(out)
PREF="""<details id="pref"><summary>Dissertatio praeuia: Praefatio noua Io. Henrici Boehmeri (De interpretationis grammaticae fatis et usu vario in iure Romano)</summary><div id="prefbox"><p class="mut">Cargando…</p><noscript><p><a href="/prefacio">Abrir el texto en una página aparte</a></p></noscript></div></details>
<script>document.getElementById('pref').addEventListener('toggle',function(){if(this.open&&!this.dataset.ok){this.dataset.ok=1;fetch('/prefacio?fragmento=1').then(function(r){return r.text()}).then(function(h){document.getElementById('prefbox').innerHTML=h}).catch(function(){document.getElementById('prefbox').innerHTML='<p><a href="/prefacio">Abrir en página aparte</a></p>'})}})</script>"""
SCRIPT=""
def pagina(cuerpo,q='',capa='ambas',modo='entrada'):
    sel=lambda v,x:' checked' if v==x else ''
    return f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Brisson · léxico jurídico latino</title><style>{CSS}</style></head><body><main>
<nav class="top"><a href="/">Quaerere</a><a href="/indice">Index vocum</a><a href="/auctores">Auctores</a><a href="/tabula">Tabula</a><a href="/loci">Loci</a><a href="/fortuita">Vox fortuita</a></nav>
<h1>Brisson, <i>De verborum quae ad ius pertinent significatione</i></h1>
<p class="sub">Edición de Heineccio (Halle, 1743). Texto de OCR, con Brisson y Heineccio en capas distintas.</p>
<figure class="fr"><img src="/portada.jpg" alt="Frontispicio grabado de la edición de 1743: retratos de Brisson y de Heineccio" width="900" height="806" loading="lazy"><figcaption>Frontispicio de la edición de 1743 (grabado de G. A. Gründler y Susang): Brisson y Heineccio. Imagen de la ULB Sachsen-Anhalt, Halle.</figcaption></figure>
<form method="get" action="/"><input type="text" name="q" value="{html.escape(q)}" placeholder="palabra latina, p. ej. exagium" autocapitalize="none" autocorrect="off" spellcheck="false" autofocus><button>Buscar</button>
<div class="opts"><label><input type="radio" name="modo" value="entrada"{sel(modo,'entrada')}> entrada</label><label><input type="radio" name="modo" value="texto"{sel(modo,'texto')}> en todo el texto</label>
<label>capa <select name="capa"><option value="ambas"{' selected' if capa=='ambas' else ''}>ambas</option><option value="brisson"{' selected' if capa=='brisson' else ''}>solo Brisson</option><option value="heineccio"{' selected' if capa=='heineccio' else ''}>solo Heineccio</option><option value="corchetes"{' selected' if capa=='corchetes' else ''}>solo corchetes</option></select></label></div></form>
{cuerpo}
{PREF}
{SCRIPT}
<footer>OCR sin revisar: los números de las citas pueden estar mal leídos y el griego sale como ⟦griego⟧ (consulta la imagen). Capa «Heineccio»: tramo que termina con la firma HEIN. y puede incluir texto de Brisson anterior a la nota. Uso académico; contrasta las citas con las fuentes.</footer></main></body></html>"""
def _prefacio(imagen_url):
    import json,os
    P=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'prefacio.json'),encoding='utf-8'))
    out=[f"<div class='pf'><p class='mut'>{html.escape(P['titulo'])}. Texto de OCR sin revisar; antes de cada página hay un enlace a su imagen.</p>"]
    for pg in P['paginas']:
        out.append(f"<span class='pn'><a href='{html.escape(imagen_url(pg['n']))}' target='_blank' rel='noopener'>página {pg['n']} del PDF</a></span>")
        for par in pg['t'].split('\n\n'):
            if par.strip(): out.append('<p>'+_fmt(par.strip())+'</p>')
    out.append('</div>');return ''.join(out)
def registrar(mcp,D,BY,KEYS,key,stems,imagen_url):
    import os
    from starlette.responses import Response
    import random,datetime,json as _j
    global _AUT,_RXA
    _AUT=_j.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'fuentes.json'),encoding='utf-8'))
    _RXA=re.compile(r'(?<![A-Za-zæ])('+'|'.join(sorted(map(re.escape,_AUT),key=len,reverse=True))+r')(?=\.)')
    AC={};AE={}
    for _i,_e in enumerate(D):
        for _s in _e['segs']:
            for _m in _RXA.finditer(_s['t'].replace(I0,'').replace(I1,'')):
                _k=_AUT[_m.group(1)].split(' (')[0];AC.setdefault(_k,{}).setdefault(_m.group(1),0);AC[_k][_m.group(1)]+=1;AE.setdefault(_k,set()).add(_i)
    from starlette.responses import RedirectResponse
    _D.clear();_D.extend(D)
    def letra(hw):
        c=re.sub(r'[^A-Z]','',hw.upper())[:1] or '#'
        return {'J':'I','U':'V'}.get(c,c)
    LET={}
    for i,e in enumerate(D): LET.setdefault(letra(e['hw']),[]).append(i)
    LETRAS=sorted(LET)
    BIG=[i for i,e in enumerate(D) if sum(len(x['t']) for x in e['segs'])>400]
    def abc(act=''):
        return "<div class='abc'>"+''.join(f"<a href='/indice?letra={l}' title='{len(LET[l])} voces'>{l}<small>{len(LET[l])}</small></a>" for l in LETRAS)+"</div>"
    @mcp.custom_route("/entrada",methods=["GET"])
    async def entrada(request):
        try: n=int(request.query_params.get('n','0'))
        except ValueError: n=0
        n=max(0,min(len(D)-1,n));capa=request.query_params.get('capa','ambas')
        if capa not in('ambas','brisson','heineccio','corchetes'): capa='ambas'
        return HTMLResponse(pagina(_entrada(D[n],capa,imagen_url,n),'',capa,'entrada'))
    import indices
    indices.montar(mcp,D,pagina,_AUT,_RXA)
    @mcp.custom_route("/fortuita",methods=["GET"])
    async def fortuita(request):
        return RedirectResponse('/entrada?n='+str(random.choice(BIG)),status_code=302)
    @mcp.custom_route("/indice",methods=["GET"])
    async def indice(request):
        l=(request.query_params.get('letra') or '').upper()[:1]
        if request.query_params.get('fragmento') and l in LET:
            idx=LET[l]
            if len(idx)<=120:
                return HTMLResponse("<ul class='c'>"+''.join(f"<li><a href='/entrada?n={i}'>{html.escape(D[i]['hw'])}</a></li>" for i in idx)+"</ul>")
            g={}
            for i in idx: g.setdefault(re.sub(r'[^A-Z]','',D[i]['hw'].upper())[:2],[]).append(i)
            return HTMLResponse(''.join(f"<details><summary>{html.escape(k)} <span class='mut'>({len(v)}) · {html.escape(D[v[0]]['hw'])} – {html.escape(D[v[-1]]['hw'])}</span></summary><ul class='c'>"+''.join(f"<li><a href='/entrada?n={i}'>{html.escape(D[i]['hw'])}</a></li>" for i in v)+"</ul></details>" for k,v in sorted(g.items())))
        if l in LET:
            idx=LET[l]
            cuerpo=abc()+f"<h2>Littera {l} <span class='mut'>({len(idx)} voces)</span></h2><div id='fr'><p class='mut'>Cargando…</p></div><script>fetch('/indice?letra={l}&fragmento=1').then(function(r){{return r.text()}}).then(function(h){{document.getElementById('fr').innerHTML=h}})</script>"
            return HTMLResponse(pagina(cuerpo,'','ambas','entrada'))
        det=''.join(f"<details class='ab' data-l='{k}'><summary>{k} <span class='mut'>({len(LET[k])}) · {html.escape(D[LET[k][0]]['hw'])} – {html.escape(D[LET[k][-1]]['hw'])}</span></summary><div class='bx'></div></details>" for k in LETRAS)
        js="<script>document.querySelectorAll('details.ab').forEach(function(d){d.addEventListener('toggle',function(){if(d.open&&!d.dataset.ok){d.dataset.ok=1;fetch('/indice?letra='+d.dataset.l+'&fragmento=1').then(function(r){return r.text()}).then(function(h){d.querySelector('.bx').innerHTML=h})}})})</script>"
        return HTMLResponse(pagina(f"<p class='mut'>{len(D)} voces. Elige una letra o despliégala aquí abajo.</p>"+abc()+det+js,'','ambas','entrada'))
    @mcp.custom_route("/portada.jpg",methods=["GET"])
    async def portada(request):
        b=open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'portada.jpg'),'rb').read()
        return Response(b,media_type='image/jpeg',headers={'Cache-Control':'public, max-age=86400'})
    @mcp.custom_route("/prefacio",methods=["GET"])
    async def prefacio(request):
        frag=_prefacio(imagen_url)
        if request.query_params.get('fragmento'): return HTMLResponse(frag)
        return HTMLResponse(pagina(frag,'', 'ambas','entrada').replace(PREF,'',1))
    @mcp.custom_route("/",methods=["GET"])
    async def inicio(request):
        q=(request.query_params.get('q') or '').strip()[:80];capa=request.query_params.get('capa','ambas');modo=request.query_params.get('modo','entrada')
        if capa not in('ambas','brisson','heineccio','corchetes'): capa='ambas'
        if not q:
            hoy=datetime.date.today();n=BIG[(hoy.toordinal()*7919)%len(BIG)];e=D[n]
            txt=re.sub(r'\s+',' ',e['segs'][0]['t'].replace(I0,'').replace(I1,''));txt=txt[:320]+('…' if len(txt)>320 else '')
            vd=f"<div class='vd'><h3>Vox diei</h3><b>{html.escape(e['hw'])}</b> <span class='mut'>(p. {e['page']})</span><p lang='la'>{_fmt(txt)}</p><a href='/entrada?n={n}'>Lege totum &rarr;</a> · <a href='/fortuita'>Aliam vocem!</a></div>"
            return HTMLResponse(pagina("<p class='mut'>Escribe una palabra para ver su entrada, busca en todo el texto, o recorre el índice por letras.</p>"+abc()+vd,q,capa,modo))
        if modo=='texto':
            rx=re.compile(''.join('[uv]' if c in 'uvUV' else '[ij]' if c in 'ijIJ' else re.escape(c) for c in q),re.I)
            res=[];total=0
            for e in D:
                for s in e['segs']:
                    m=rx.search(s['t'])
                    if m:
                        total+=1
                        if len(res)<60:
                            a=max(0,m.start()-90);b=min(len(s['t']),m.end()+90)
                            res.append(f"<li><a href='/?q={quote(e['hw'])}'>{html.escape(e['hw'])}</a> <span class='mut'>(p. {e['page']})</span>: …{_fmt(s['t'][a:m.start()])}<b>{_fmt(s['t'][m.start():m.end()])}</b>{_fmt(s['t'][m.end():b])}…</li>")
                        break
            cab=f"<p class='mut'>{total} entrada(s) contienen «{html.escape(q)}»"+(" (se muestran 60)" if total>60 else "")+".</p>"
            return HTMLResponse(pagina(cab+"<ul>"+''.join(res)+"</ul>" if res else "<p>Sin resultados.</p>",q,capa,modo))
        k=key(q);idx=None
        for st in stems(k):
            idx=BY.get(st)
            if idx: break
        if idx: return HTMLResponse(pagina(''.join(_entrada(D[i],capa,imagen_url,i) for i in idx),q,capa,modo))
        pref=[x for x in KEYS if x.startswith(stems(k)[-1])][:60] if k else []
        if pref:
            li=''.join(f"<li><a href='/?q={quote(D[BY[c][0]]['hw'])}'>{html.escape(D[BY[c][0]]['hw'])}</a></li>" for c in pref)
            return HTMLResponse(pagina(f"<p>Sin entrada exacta para «{html.escape(q)}». Entradas próximas:</p><ul class='c'>{li}</ul>",q,capa,modo))
        return HTMLResponse(pagina(f"<p>Sin entrada para «{html.escape(q)}». Prueba «en todo el texto».</p>",q,capa,modo))
