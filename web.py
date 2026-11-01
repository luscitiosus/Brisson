"""Página web de consulta (sin Claude) para el léxico de Brisson: / (buscador), con paginación mínima y sin JavaScript."""
import html,re,collections
from urllib.parse import quote
from starlette.responses import HTMLResponse as _HR
_LIG=re.compile(r'ae|AE|Ae|aE')
def _lig(m):
    x=m.group(0);return 'Æ' if x[0]=='A' else 'æ'
_SPL=re.compile(r'(<style.*?</style>|<script.*?</script>|<[^>]+>)',re.S)
_GR=re.compile(r'[\u0370-\u03ff\u1f00-\u1fff]+(?:[ \u0387\u00b7,.;:][\u0370-\u03ff\u1f00-\u1fff]+)*')
def _tx(x): return _GR.sub(lambda m:'<span class="grc" lang="grc">'+m.group(0)+'</span>',_LIG.sub(_lig,x))
def lig_html(h):
    p=_SPL.split(h)
    return ''.join(x if i%2 else _tx(x) for i,x in enumerate(p))
class HTMLResponse(_HR):
    def __init__(self,content,*a,**k):
        super().__init__(lig_html(content) if isinstance(content,str) else content,*a,**k)

CSS="""
nav.top{position:sticky;top:0;z-index:5;background:var(--bg);padding:.4rem 0;border-bottom:1px solid var(--line)}
.bc{font-size:.85rem;color:var(--mut);margin:.6rem 0 0}.bc a{color:var(--mut)}
.pg{display:flex;gap:.6rem;flex-wrap:wrap;align-items:center;margin:1rem 0}.pg a,.pg span{padding:.3rem .7rem;border:1px solid var(--line);border-radius:6px;text-decoration:none}
.res li{margin:.7rem 0;list-style:none}.res{padding:0}mark{background:rgba(180,140,60,.35);color:inherit;padding:0 .1em;border-radius:2px}
.sg{font-size:.9rem;color:var(--mut)}.sg a{margin-right:.8rem}
#top{position:fixed;right:12px;bottom:12px;background:var(--card);border:1px solid var(--line);border-radius:50%;width:2.4rem;height:2.4rem;text-align:center;line-height:2.3rem;text-decoration:none;opacity:.85}
.ir{display:flex;gap:.5rem;align-items:center;margin:.6rem 0;font-size:.9rem;color:var(--mut)}.ir input{width:6rem;font:inherit;padding:.3rem .5rem;border:1px solid var(--line);border-radius:6px;background:var(--card);color:var(--fg)}
@font-face{font-family:'GFS Complutum';src:url('/fuente?f=Complutum') format('opentype');font-display:swap}
.grc{font-family:'GFS Complutum','GFS Porson','Palatino Linotype',serif}
@font-face{font-family:'Ibarra Real Nova';src:url('/fuente?f=Regular') format('truetype');font-weight:400;font-style:normal;font-display:swap}
@font-face{font-family:'Ibarra Real Nova';src:url('/fuente?f=Italic') format('truetype');font-weight:400;font-style:italic;font-display:swap}
@font-face{font-family:'Ibarra Real Nova';src:url('/fuente?f=Bold') format('truetype');font-weight:700;font-style:normal;font-display:swap}
@font-face{font-family:'Ibarra Real Nova';src:url('/fuente?f=BoldItalic') format('truetype');font-weight:700;font-style:italic;font-display:swap}
:root{--bg:#fbf8f1;--fg:#1d1b17;--mut:#6b655a;--line:#ddd5c4;--hein:#8a3b12;--hbg:#f6ebdd;--cor:#1f4e79;--cbg:#e9f0f7;--card:#fffdf8}
@media(prefers-color-scheme:dark){:root{--bg:#16140f;--fg:#ece6d8;--mut:#a39c8c;--line:#3a352a;--hein:#e3a06b;--hbg:#2a2117;--cor:#8fbbe3;--cbg:#16222e;--card:#1c1912}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:19px/1.55 'Ibarra Real Nova',Georgia,'Times New Roman',serif}
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
a.ref{text-decoration:underline dotted}
a.lex{color:inherit;text-decoration:underline dotted var(--hein)}
.lx{border:1px solid var(--line);background:var(--card);border-radius:8px;padding:.2rem 1rem 1rem;margin:1rem 0}.lx h3{margin:.8rem 0 .2rem}.lx .vs a{margin-right:.6rem;white-space:nowrap}
.hit{background:rgba(180,140,60,.25);padding:.2em .4em;border-left:3px solid var(--cor)}
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
a.nv small{display:block;font:italic .8rem 'Ibarra Real Nova',Georgia,serif;letter-spacing:0;font-variant:normal;font-weight:normal;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
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
_FUENTES=[None]
_LEXS=[]
_PRE=r"(?:S\.?\s?C\.?|Senatusconsult\w*|[Ll]ex|[Ll]ege|[Ll]egem|[Ll]egis)\s+(?:de\s+)?"
def _lex_cargar(L):
    for x in L:
        rx=x['rx']
        con=re.compile(r"(?<![A-Za-z\u00e6])"+_PRE+"(?:"+rx+r")(?![A-Za-z\u00e6])")
        sin=None
        if x['tipo']=='senadoconsulto':
            core=rx.replace(r"|Vell\.","")
            sin=re.compile(r"(?<![A-Za-z\u00e6])(?=[A-Za-z\u00e6]*ian)(?:"+core+r")(?<!ianus)(?![A-Za-z\u00e6])")
        _LEXS.append((x,con,sin))
def _lexl(t):
    if not _LEXS: return t
    for x,con,sin in _LEXS:
        tt=x['nombre']
        rep=lambda m:f'<a class="lex" href="/leges#{x["id"]}" title="{tt}">{m.group(0)}</a>'
        t=con.sub(rep,t)
        if sin:
            parts=re.split(r'(<a class="lex".*?</a>|<[^>]+>)',t)
            t=''.join(p if i%2 else sin.sub(rep,p) for i,p in enumerate(parts))
    return t
_RR=re.compile(r'^(D|C|CTh|I)\.(\d+)\.(\d+)\.(\d+|ult)(?:\.?pr|\.(\d+|ult))?$|^(PS)\.(\d+)\.(\d+)(?:\.(\d+))?$')
def _refl(m):
    r=m.group(1);mm=_RR.match(html.unescape(r))
    if not mm or not _FUENTES[0]: return f'<span class="ref">[{r}]</span>'
    sig,b,t,l,p=mm.group(1),mm.group(2),mm.group(3),mm.group(4),mm.group(5)
    if not sig: return f'<span class="ref">[{r}]</span>'
    dest='pr' if r.endswith('pr') else (p or '')
    q=f"{sig}.{b}.{t}.{l}"+(f".{dest}" if dest else '')
    return f'<a class="ref" href="/fons?r={q}" title="Leer el texto latino (BIA)">[{r}]</a>'
_RM={'I':1,'II':2,'III':3,'IV':4,'V':5}
_M='[\ue000\ue001]*';_S='(?:\\s|[\ue000\ue001])+'
_RPS=re.compile(r'(Paull?\.?'+_S+r'[Rr]ecept\.?'+_S+r'[Ss]ent\.?'+_S+r'(?:[Ll]ib\.?'+_S+r')?)('+_M+r'(?:I{1,3}|IV|V|[1-5])'+_M+r')\s*[,.]?(?:\s|[\ue000\ue001])*(?:[Tt]it\.?\s*)?(\d{1,2})(?!\d)')
def _ps(t):
    if not _FUENTES[0] or 'ps' not in _FUENTES[0].obras(): return t
    def f(m):
        lb=re.sub('[\ue000\ue001]','',m.group(2));b=_RM.get(lb) or int(lb)
        return f'<a class="ref" href="/fons?r=PS.{b}.{m.group(3)}" title="Pauli Sententiae {b}.{m.group(3)}: texto latino (BIA)">'+re.sub('[\ue000\ue001]','',m.group(0))+'</a>'
    return _RPS.sub(f,t)
def _fmt(t):
    t=_lexl(_ps(html.escape(_vid(t))))
    t=re.sub(r'\[((?:D|C|CTh|I|N)\.[^\]]*)\]',_refl,t)
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
def _navbtn(i,lado):
    if lado=='prior':
        h=f"<a class='nv' href='/entrada?n={i-1}'>&#9756; Vox prior<small>{html.escape(_D[i-1]['hw'])}</small></a>" if i>0 else ''
    else:
        h=f"<a class='nv' href='/entrada?n={i+1}'>Vox posterior &#9758;<small>{html.escape(_D[i+1]['hw'])}</small></a>" if i<len(_D)-1 else ''
    return f"<div class='pn2'>{h}</div>" if h else ''
def _entrada(e,capa,imagen_url,i=None):
    nT=sum(1 for s in e['segs'] if s['k']=='T');ng=e.get('ngr',0)
    out=[f"<article><h2>{html.escape(e['hw'])}</h2><div class='meta'>p. {e['page']} del PDF · "
         f"<a href='{html.escape(imagen_url(e['page']))}' target='_blank' rel='noopener'>ver la página</a>"
         +(f" · {ng} pasaje(s) en griego" if ng else "")+f" · {nT} tramo(s) con nota de Heineccio</div>"]
    if i is not None and _D: out.append(_navbtn(i,'prior'))
    for s in e['segs']:
        k=s['k']
        if capa=='brisson' and k!='B' or capa=='heineccio' and k!='T' or capa=='corchetes' and k!='C': continue
        tag={'T':'Tramo que termina en HEIN. (nota de Heineccio)','B':'Brisson','C':'Entre corchetes en la edición'}[k]
        out.append(f"<div class='seg {k}' lang='la'><span class='tag'>{tag}</span>{_fmt(s.get('h',s['t']))}</div>")
    if i is not None and _D: out.append(_navbtn(i,'posterior'))
    out.append("</article>");return ''.join(out)
PREF="""<details id="pref"><summary>Dissertatio praeuia: Praefatio noua Io. Henrici Boehmeri (De interpretationis grammaticae fatis et usu vario in iure Romano)</summary><div id="prefbox"><p class="mut">Cargando…</p><noscript><p><a href="/prefacio">Abrir el texto en una página aparte</a></p></noscript></div></details>
<script>document.getElementById('pref').addEventListener('toggle',function(){if(this.open&&!this.dataset.ok){this.dataset.ok=1;fetch('/prefacio?fragmento=1').then(function(r){return r.text()}).then(function(h){document.getElementById('prefbox').innerHTML=h}).catch(function(){document.getElementById('prefbox').innerHTML='<p><a href="/prefacio">Abrir en página aparte</a></p>'})}})</script>"""
SCRIPT='<script>\n(function(){var q=document.querySelector(\'input[name=q]\'),dl=document.getElementById(\'sug\'),t;\nif(q)q.addEventListener(\'input\',function(){clearTimeout(t);var v=q.value.trim();if(v.length<2)return;t=setTimeout(function(){fetch(\'/sugerir?q=\'+encodeURIComponent(v)).then(function(r){return r.json()}).then(function(a){dl.innerHTML=a.map(function(x){return \'<option value="\'+x+\'">\'}).join(\'\')}).catch(function(){})},180)});\ndocument.addEventListener(\'keydown\',function(e){var el=document.activeElement,tag=el&&el.tagName;if(tag==\'INPUT\'||tag==\'SELECT\'||tag==\'TEXTAREA\')return;if(e.ctrlKey||e.metaKey||e.altKey)return;\nif(e.key==\'/\'){e.preventDefault();q&&q.focus()}\nelse if(e.key==\'ArrowLeft\'||e.key==\'ArrowRight\'){var l=document.querySelectorAll(\'a.nv\');if(l.length&&document.querySelectorAll(\'article\').length==1){var pr=null,po=null;l.forEach(function(a){if(a.textContent.indexOf(\'prior\')>-1)pr=a;else po=a});var a=e.key==\'ArrowLeft\'?pr:po;if(a)location=a.href}}});\ntry{var m=location.pathname==\'/entrada\'||(location.pathname==\'/\'&&document.querySelectorAll(\'article\').length==1);if(m){var h=document.querySelector(\'article h2\');if(h){var L=JSON.parse(localStorage.getItem(\'rec\')||\'[]\'),u=location.pathname+location.search;L=L.filter(function(x){return x[0]!=h.textContent});L.unshift([h.textContent,u]);localStorage.setItem(\'rec\',JSON.stringify(L.slice(0,12)))}}\nvar b=document.getElementById(\'rec\');if(b){var L2=JSON.parse(localStorage.getItem(\'rec\')||\'[]\');if(L2.length){b.innerHTML=\'<h3>Nuper uisae</h3><p class="sg">\'+L2.map(function(x){var a=document.createElement(\'a\');a.href=x[1];a.textContent=x[0];return a.outerHTML}).join(\' \')+\'</p>\'}}}catch(e){}\n})();</script><a id="top" href="#" title="Ad principium">&uarr;</a>'
def pagina(cuerpo,q='',capa='ambas',modo='entrada'):
    sel=lambda v,x:' checked' if v==x else ''
    return f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Brisson · léxico jurídico latino</title><style>{CSS}</style></head><body><main>
<nav class="top"><a href="/">Quaerere</a><a href="/indice">Index vocum</a><a href="/auctores">Auctores</a><a href="/tabula">Tabula</a><a href="/loci">Loci</a><a href="/leges">Leges</a><a href="/fortuita">Vox fortuita</a></nav>
<h1>Brisson, <i>De verborum quae ad ius pertinent significatione</i></h1>
<p class="sub">Edición de Heineccio (Halle, 1743). Texto de OCR, con Brisson y Heineccio en capas distintas.</p>
<figure class="fr"><img src="/portada.jpg" alt="Frontispicio grabado de la edición de 1743: retratos de Brisson y de Heineccio" width="900" height="806" loading="lazy"><figcaption>Frontispicio de la edición de 1743 (grabado de G. A. Gründler y Susang): Brisson y Heineccio. Imagen de la ULB Sachsen-Anhalt, Halle.</figcaption></figure>
<form method="get" action="/"><input type="text" name="q" value="{html.escape(q)}" placeholder="palabra latina, \u00abfrase\u00bb o cita (D. 47.2.1)" autocapitalize="none" autocorrect="off" spellcheck="false" autocomplete="off" list="sug" autofocus><datalist id="sug"></datalist><button>Buscar</button>
<div class="opts"><label><input type="radio" name="modo" value="entrada"{sel(modo,'entrada')}> entrada</label><label><input type="radio" name="modo" value="texto"{sel(modo,'texto')}> en todo el texto</label>
<label>capa <select name="capa"><option value="ambas"{' selected' if capa=='ambas' else ''}>ambas</option><option value="brisson"{' selected' if capa=='brisson' else ''}>solo Brisson</option><option value="heineccio"{' selected' if capa=='heineccio' else ''}>solo Heineccio</option><option value="corchetes"{' selected' if capa=='corchetes' else ''}>solo corchetes</option></select></label></div></form>
{cuerpo}
{PREF}
{SCRIPT}
<footer>OCR sin revisar: los números de las citas pueden estar mal leídos y el griego sale como ⟦griego⟧ (consulta la imagen). Capa «Heineccio»: tramo que termina con la firma HEIN. y puede incluir texto de Brisson anterior a la nota. Tipografía: Ibarra Real Nova y, para el griego, GFS Complutum (SIL OFL). Uso académico; contrasta las citas con las fuentes.</footer></main></body></html>"""
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
        return HTMLResponse(pagina(_migas(n)+_entrada(D[n],capa,imagen_url,n),'',capa,'entrada'))
    import indices
    indices.montar(mcp,D,pagina,_AUT,_RXA)
    import romanos
    _lex_cargar(_j.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'leges.json'),encoding='utf-8')))
    @mcp.custom_route("/leges",methods=["GET"])
    async def leges(request):
        cuerpo=["<h2>Leges et senatus consulta</h2><p class='mut'>Leyes y senadoconsultos romanos que cita el l\u00e9xico, con una breve descripci\u00f3n en espa\u00f1ol y las fuentes de donde sale (Instituciones, Digesto y Gayo en la edici\u00f3n de BIA; Wikipedia para las dem\u00e1s). Cada menci\u00f3n en el texto enlaza aqu\u00ed. Las voces citan esas leyes con variantes de OCR; las leyes con muchos hom\u00f3nimos (Cornelia, Iulia\u2026) no se incluyen todav\u00eda.</p>"]
        for x,con,sin in _LEXS:
            vs=collections.Counter()
            for i,e in enumerate(D):
                for sg in e['segs']:
                    tx=sg['t'].replace(I0,'').replace(I1,'')
                    n=len(con.findall(tx))+(len(sin.findall(tx)) if sin else 0)
                    if n: vs[i]+=n
            fu=' \u00b7 '.join(f"<a href='{html.escape(f['u'])}'"+(" target='_blank' rel='noopener'" if f['u'].startswith('http') else '')+f">{html.escape(f['t'])}</a>" for f in x['fuentes'])
            vo=' '.join(f"<a href='/entrada?n={i}'>{html.escape(D[i]['hw'])}</a>" for i,_ in vs.most_common(40))
            cuerpo.append(f"<div class='lx' id='{x['id']}'><h3>{html.escape(x['nombre'])}</h3><div class='meta'>{x['tipo']} \u00b7 {sum(vs.values())} menci\u00f3n(es) en {len(vs)} voz(es)</div><p>{html.escape(x['desc'])}</p><p class='mut'>Fuente: {fu}</p>"+(f"<p class='vs' lang='la'>{vo}</p>" if vo else '')+"</div>")
        return HTMLResponse(pagina(''.join(cuerpo),'','ambas','entrada'))
    _F=romanos.Fuentes()
    _FUENTES[0]=_F if _F.ok() and _F.obras() else None
    @mcp.custom_route("/fons",methods=["GET"])
    async def fons(request):
        r=request.query_params.get('r','');mm=_RR.match(r)
        d=_FUENTES[0].leer(r.split('.')[0],'.'.join(x for x in r.split('.')[1:])) if (mm and _FUENTES[0]) else None
        if not d:
            return HTMLResponse(pagina(f"<article><h2>Fons non inuentus</h2><p>No encuentro <b>{html.escape(r)}</b> en la edición de BIA (la cita puede tener un error de OCR). <a href='javascript:history.back()'>&#9756; Redi</a></p></article>",'','ambas','entrada'),status_code=404)
        dest=d['dest'];filas=[]
        for et,tx in d['filas']:
            e=html.escape(et);sel=False
            if dest:
                if dest=='pr': sel=et.endswith('pr')
                else: sel=et.endswith('.'+dest)
            filas.append(f"<p class='{'hit' if sel else ''}' lang='la'><span class='tag'>{e}</span> {html.escape(tx)}</p>")
        ref=html.escape(r.replace('.',' ',0))
        cab=f"<article><h2>{html.escape(d['obra'])} {html.escape(r.split('.',1)[1])}</h2><div class='meta'>{html.escape(d['tit'])}</div>"
        pie="<p class='mut'>Texto: Bibliotheca Iuris Antiqui (IGSG-CNR), CC BY-NC-SA 4.0. Es lectura de la edición crítica; la numeración puede diferir de la del Brisson.</p><p><a href='javascript:history.back()'>&#9756; Redi ad vocem</a></p></article>"
        return HTMLResponse(pagina(cab+''.join(filas)+pie,'','ambas','entrada'))
    @mcp.custom_route("/fortuita",methods=["GET"])
    async def fortuita(request):
        return RedirectResponse('/entrada?n='+str(random.choice(BIG)),status_code=302)
    @mcp.custom_route("/indice",methods=["GET"])
    async def indice(request):
        l=(request.query_params.get('letra') or '').upper()[:1]
        if request.query_params.get('fragmento') and l in LET:
            idx=LET[l]
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
    @mcp.custom_route("/fuente",methods=["GET"])
    async def fuente(request):
        n=request.query_params.get('f','')
        base=os.path.dirname(os.path.abspath(__file__))
        if n=='Complutum': return Response(open(os.path.join(base,'fuentes','GFSPolyglot.otf'),'rb').read(),media_type='font/otf',headers={'Cache-Control':'public, max-age=604800'})
        if n not in('Regular','Italic','Bold','BoldItalic'): return Response(status_code=404)
        b=open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'fuentes',f'IbarraRealNova-{n}.ttf'),'rb').read()
        return Response(b,media_type='font/ttf',headers={'Cache-Control':'public, max-age=604800'})
    @mcp.custom_route("/portada.jpg",methods=["GET"])
    async def portada(request):
        b=open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'portada.jpg'),'rb').read()
        return Response(b,media_type='image/jpeg',headers={'Cache-Control':'public, max-age=86400'})
    @mcp.custom_route("/prefacio",methods=["GET"])
    async def prefacio(request):
        frag=_prefacio(imagen_url)
        if request.query_params.get('fragmento'): return HTMLResponse(frag)
        return HTMLResponse(pagina(frag,'', 'ambas','entrada').replace(PREF,'',1))
    import difflib
    def _ncls(t): return t.replace(I0,'').replace(I1,'')
    _TX={}
    def _txt(capa):
        if capa not in _TX:
            ok={'ambas':'TBC','brisson':'B','heineccio':'T','corchetes':'C'}[capa]
            _TX[capa]=[' \n'.join(_ncls(x['t']) for x in e['segs'] if x['k'] in ok) for e in D]
        return _TX[capa]
    def _tokrx(w):
        w=re.escape(w)
        w=w.replace('ae','(?:ae|æ)').replace('AE','(?:AE|Æ)').replace('oe','(?:oe|œ)')
        w=re.sub(r'[uv]','[uv]',w,flags=re.I);w=re.sub(r'[ij]','[ij]',w,flags=re.I)
        return w
    _CITA=re.compile(r'^\s*(D|C|CTh|I)\.?\s*(\d+)\s*[.,]\s*(\d+)(?:\s*[.,]\s*(\d+|ult))?(?:\s*[.,]?\s*(pr))?\s*\.?\s*$',re.I)
    def _regs(q):
        m=_CITA.match(q)
        if m:
            sg=m.group(1).upper() if m.group(1).upper()!='CTH' else 'CTh'
            r=r'\['+sg+r'\.'+m.group(2)+r'\.'+m.group(3)+(r'\.'+m.group(4)+r'(?![0-9])' if m.group(4) else r'\.')
            return [re.compile(r)],'cita'
        toks=[a or b for a,b in re.findall(r'"([^"]+)"|(\S+)',q.replace('\u00ab','"').replace('\u00bb','"'))]
        out=[]
        for tk in toks[:6]:
            tk=tk.strip()
            if not tk: continue
            out.append(re.compile(r'\s+'.join(_tokrx(x) for x in tk.split()),re.I))
        return out,'texto'
    def _buscar(q,capa,pag):
        rxs,tipo=_regs(q)
        if not rxs: return None
        T=_txt(capa);res=[]
        for i,t in enumerate(T):
            ms=[]
            for rx in rxs:
                m=rx.search(t)
                if not m: break
                ms.append(m)
            else:
                n=len(rxs[0].findall(t)) if tipo=='texto' else 1
                hw=1 if all(rx.search(D[i]['hw']) for rx in rxs) else 0
                res.append((-hw,-n,i,ms[0]))
        res.sort()
        PP=25;tot=len(res);ini=pag*PP;li=[]
        for _,_,i,m in res[ini:ini+PP]:
            t=T[i];a=max(0,m.start()-100);b=min(len(t),m.end()+100);e=D[i]
            pre=_fmt(t[a:m.start()]);med=_fmt(t[m.start():m.end()]);post=_fmt(t[m.end():b])
            li.append(f"<li><a href='/entrada?n={i}'>{html.escape(e['hw'])}</a> <span class='mut'>(p. {e['page']})</span><br>…{pre}<mark>{med}</mark>{post}…</li>")
        return tot,li,tipo
    def _pager(q,capa,pag,tot,PP=25):
        base=f"/?q={quote(q)}&modo=texto&capa={capa}"
        h="<div class='pg'>"
        if pag>0: h+=f"<a href='{base}&p={pag-1}'>&#9756; Prior</a>"
        h+=f"<span>{pag*PP+1}&ndash;{min(tot,(pag+1)*PP)} de {tot}</span>"
        if (pag+1)*PP<tot: h+=f"<a href='{base}&p={pag+1}'>Posterior &#9758;</a>"
        return h+"</div>"
    @mcp.custom_route("/sugerir",methods=["GET"])
    async def sugerir(request):
        import json as _jj
        from starlette.responses import JSONResponse
        k=key(request.query_params.get('q','')[:40])
        if not k: return JSONResponse([])
        c=[x for x in KEYS if x.startswith(k)][:8]
        if len(c)<8 and len(k)>=3: c+=[x for x in difflib.get_close_matches(k,KEYS,n=8-len(c),cutoff=.78) if x not in c]
        return JSONResponse([D[BY[x][0]]['hw'] for x in c])
    @mcp.custom_route("/pagina",methods=["GET"])
    async def ir_pagina(request):
        try: n=int(request.query_params.get('n','0'))
        except ValueError: n=0
        j=0
        for i,e in enumerate(D):
            if e['page']<=n: j=i
            else: break
        return RedirectResponse(f'/entrada?n={j}',status_code=302)
    def _migas(i):
        l=letra(D[i]['hw'])
        return f"<p class='bc'><a href='/'>Quaerere</a> &rsaquo; <a href='/indice'>Index</a> &rsaquo; <a href='/indice?letra={l}'>{l}</a> &rsaquo; {html.escape(D[i]['hw'])}</p>"
    @mcp.custom_route("/",methods=["GET"])
    async def inicio(request):
        q=(request.query_params.get('q') or '').strip()[:120];capa=request.query_params.get('capa','ambas');modo=request.query_params.get('modo','entrada')
        try: pag=max(0,int(request.query_params.get('p','0')))
        except ValueError: pag=0
        if capa not in('ambas','brisson','heineccio','corchetes'): capa='ambas'
        if not q:
            hoy=datetime.date.today();n=BIG[(hoy.toordinal()*7919)%len(BIG)];e=D[n]
            txt=re.sub(r'\s+',' ',e['segs'][0]['t'].replace(I0,'').replace(I1,''));txt=txt[:320]+('\u2026' if len(txt)>320 else '')
            vd=f"<div class='vd'><h3>Vox diei</h3><b>{html.escape(e['hw'])}</b> <span class='mut'>(p. {e['page']})</span><p lang='la'>{_fmt(txt)}</p><a href='/entrada?n={n}'>Lege totum &rarr;</a> \u00b7 <a href='/fortuita'>Aliam vocem!</a></div>"
            ir=f"<form class='ir' method='get' action='/pagina'><label>Ir a la p\u00e1gina del PDF <input type='number' name='n' min='1' max='{D[-1]['page']}'></label><button>Ir</button></form>"
            ayuda="<p class='mut'>Escribe una palabra (se buscan tambi\u00e9n sus formas declinadas), una \u00abfrase entre comillas\u00bb, varias palabras (todas deben aparecer) o una cita como <a href='/?q=D.+47.2.1&modo=texto'>D. 47.2.1</a> para ver qu\u00e9 voces la mencionan. Atajos: <b>/</b> busca, <b>\u2190 \u2192</b> pasan de una voz a otra.</p>"
            return HTMLResponse(pagina(ayuda+abc()+ir+"<div id='rec'></div>"+vd,q,capa,modo))
        if modo!='texto':
            k=key(q);idx=None
            if k and ' ' not in q.strip():
                for st in stems(k):
                    idx=BY.get(st)
                    if idx: break
            if idx:
                cuerpo=''.join(_migas(i)+_entrada(D[i],capa,imagen_url,i) if len(idx)==1 else _entrada(D[i],capa,imagen_url,i) for i in idx)
                return HTMLResponse(pagina(cuerpo,q,capa,modo))
            sug=''
            if k and re.fullmatch(r"[A-Za-z\u00e6\u0153\u00c6\u0152]+",q.strip()):
                pref=[x for x in KEYS if x.startswith(stems(k)[-1])][:40]
                cer=[x for x in difflib.get_close_matches(k,KEYS,n=6,cutoff=.72) if x not in pref]
                if pref or cer:
                    sug="<p class='sg'>\u00bfQuiz\u00e1s buscabas?: "+''.join(f"<a href='/?q={quote(D[BY[c][0]]['hw'])}'>{html.escape(D[BY[c][0]]['hw'])}</a>" for c in (cer+pref)[:30])+"</p>"
            modo='texto'
            aviso=(f"<p class='mut'>No hay entrada que se llame \u00ab{html.escape(q)}\u00bb; se busca en todo el texto.</p>" if re.fullmatch(r'\S+',q) and not _CITA.match(q) else '')+sug
        else: aviso=''
        r=_buscar(q,capa,pag)
        if not r or not r[0]:
            return HTMLResponse(pagina(aviso+f"<p>Sin resultados para \u00ab{html.escape(q)}\u00bb.</p>",q,capa,'texto'))
        tot,li,tipo=r
        cab=f"<p class='mut'>{tot} voz(es) {'citan ' if tipo=='cita' else 'contienen '}\u00ab{html.escape(q)}\u00bb. Orden: primero las que lo llevan en el lema, despu\u00e9s por n\u00famero de apariciones.</p>"
        return HTMLResponse(pagina(aviso+cab+"<ul class='res'>"+''.join(li)+"</ul>"+_pager(q,capa,pag,tot),q,capa,'texto'))
