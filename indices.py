"""Índices de la web: autores y obras citados, tabla de voces por letra y loci (títulos del Digesto/Código citados)."""
import html,re,json,os,collections
from urllib.parse import quote
from starlette.responses import HTMLResponse
AQUI=os.path.dirname(os.path.abspath(__file__))
REF=re.compile(r'\[(D|C|CTh)\.(\d+)\.(\d+)\.(\d+|ult)(?:pr|\.\d+)?\]')
LOCW={'Lib','Libr','Cap','Idem','Vid','Tom','Tomo','Tit','Lect','Lectionum','Cap','Libro','Orat'}
def _titulos(fn):
    T={}
    try:
        for l in open(os.path.join(AQUI,'citas',fn),encoding='utf-8'):
            p=l.rstrip('\n').split('|')
            if p[0].isdigit(): T[int(p[0])]=p[1:]
    except OSError: pass
    return T
def montar(mcp,D,pagina,AUT,RXA):
    OB=json.load(open(os.path.join(AQUI,'fuentes_obras.json'),encoding='utf-8'))
    DT=_titulos('dtitles.txt');CT=_titulos('ctitles.txt')
    EA=[collections.Counter() for _ in D]      # autores por entrada
    AB=collections.defaultdict(collections.Counter)   # autor -> abreviaturas
    WK=collections.defaultdict(collections.Counter)   # autor -> obra (token)
    LOCI=collections.defaultdict(lambda:collections.defaultdict(set))  # (src,b,t)->idx->leyes
    NREF=[0]*len(D)
    wrx=re.compile(r'(?<![A-Za-zæ])('+'|'.join(sorted(map(re.escape,AUT),key=len,reverse=True))+r')\.?(?:\s+[A-Z][a-zæ]{0,3}\.?)?\s+([A-Z][a-zæ]{3,12})')
    for i,e in enumerate(D):
        for s in e['segs']:
            t=s['t'].replace('','').replace('','')
            for m in RXA.finditer(t):
                a=AUT[m.group(1)].split(' (')[0];EA[i][a]+=1;AB[a][m.group(1)]+=1
            for m in wrx.finditer(t):
                w=m.group(2)
                if w not in LOCW: WK[AUT[m.group(1)].split(' (')[0]][w]+=1
            for m in REF.finditer(t):
                LOCI[(m[1],int(m[2]),int(m[3]))][i].add(m[4]);NREF[i]+=1
    AUTH=collections.Counter()
    for i in range(len(D)):
        for a,n in EA[i].items(): AUTH[a]+=n
    LET={}
    for i,e in enumerate(D):
        c=re.sub(r'[^A-Z]','',e['hw'].upper())[:1] or '#';c={'J':'I','U':'V'}.get(c,c);LET.setdefault(c,[]).append(i)
    LETRAS=sorted(LET)
    def tabla(idx,extra=None):
        h="<table class='tb'><tr><th>Vox</th><th>p.</th><th>Leges</th><th>Auctores</th></tr>"
        for i in idx:
            top=', '.join(f"{a} ({n})" for a,n in EA[i].most_common(3))
            h+=f"<tr><td><a href='/entrada?n={i}'>{html.escape(D[i]['hw'])}</a></td><td>{D[i]['page']}</td><td>{NREF[i] or ''}</td><td>{html.escape(top)}</td></tr>"
        return h+"</table>"
    def abc(base):
        return "<div class='abc'>"+''.join(f"<a href='{base}?letra={l}'>{l}<small>{len(LET[l])}</small></a>" for l in LETRAS)+"</div>"
    def obra_titulo(a,w):
        for k,v in OB.get(a,{}).items():
            for kk in k.split('/'):
                if w.lower().startswith(kk.lower()[:4]): return v
        return ''
    @mcp.custom_route("/auctores",methods=["GET"])
    async def auctores(request):
        li=''.join(f"<li><a href='/auctor?a={quote(a)}'><b>{html.escape(a)}</b></a> <span class='mut'>{n} citas en {sum(1 for i in range(len(D)) if a in EA[i])} entradas</span><br><small>"+' · '.join(f"{html.escape(x)}. ({m})" for x,m in AB[a].most_common(5))+"</small></li>" for a,n in AUTH.most_common())
        return HTMLResponse(pagina("<h2>Auctores citati</h2><p class='mut'>Autores y eruditos citados por Brisson y Heineccio, por abreviatura del texto (OCR sin revisar). Pulsa un nombre para ver sus obras y las voces que lo citan.</p><ul>"+li+"</ul>",'','ambas','entrada'))
    @mcp.custom_route("/auctor",methods=["GET"])
    async def auctor(request):
        a=(request.query_params.get('a') or '')
        if a not in AUTH: return HTMLResponse(pagina("<p>Autor no encontrado. <a href='/auctores'>Ver el índice de autores</a>.</p>",'','ambas','entrada'))
        idx=[i for i in range(len(D)) if a in EA[i]]
        ob=''.join(f"<tr><td>{html.escape(w)}.</td><td>{n}</td><td>{html.escape(obra_titulo(a,w))}</td></tr>" for w,n in WK[a].most_common(15) if n>=2)
        cab=f"<h2>{html.escape(a)}</h2><p class='mut'>{AUTH[a]} citas en {len(idx)} voces. Abreviaturas: "+', '.join(f"{html.escape(x)}. ({m})" for x,m in AB[a].most_common(8))+"</p>"
        if ob: cab+="<h3>Obras citadas</h3><table class='tb'><tr><th>Obra (abrev.)</th><th>Citas</th><th>Título</th></tr>"+ob+"</table>"
        g={}
        for i in idx: g.setdefault(re.sub(r'[^A-Z]','',D[i]['hw'].upper())[:1] or '#',[]).append(i)
        det=''.join(f"<details class='ab'><summary>{html.escape(k)} <span class='mut'>({len(v)})</span></summary>"+tabla_a(v,a)+"</details>" for k,v in sorted(g.items()))
        return HTMLResponse(pagina(cab+"<h3>Voces que lo citan</h3>"+det,'','ambas','entrada'))
    def tabla_a(idx,a):
        h="<table class='tb'><tr><th>Vox</th><th>p.</th><th>Citas</th></tr>"
        for i in idx: h+=f"<tr><td><a href='/entrada?n={i}'>{html.escape(D[i]['hw'])}</a></td><td>{D[i]['page']}</td><td>{EA[i][a]}</td></tr>"
        return h+"</table>"
    @mcp.custom_route("/tabula",methods=["GET"])
    async def tabula(request):
        l=(request.query_params.get('letra') or '').upper()[:1]
        if request.query_params.get('fragmento') and l in LET:
            idx=LET[l]
            g={}
            for i in idx: g.setdefault(re.sub(r'[^A-Z]','',D[i]['hw'].upper())[:2],[]).append(i)
            return HTMLResponse(''.join(f"<details><summary>{html.escape(k)} <span class='mut'>({len(v)}) · {html.escape(D[v[0]]['hw'])} – {html.escape(D[v[-1]]['hw'])}</span></summary>{tabla(v)}</details>" for k,v in sorted(g.items())))
        det=''.join(f"<details class='ab' data-l='{k}' data-u='/tabula'><summary>{k} <span class='mut'>({len(LET[k])}) · {html.escape(D[LET[k][0]]['hw'])} – {html.escape(D[LET[k][-1]]['hw'])}</span></summary><div class='bx'></div></details>" for k in LETRAS)
        js="<script>document.querySelectorAll('details.ab[data-u]').forEach(function(d){d.addEventListener('toggle',function(){if(d.open&&!d.dataset.ok){d.dataset.ok=1;fetch(d.dataset.u+'?letra='+d.dataset.l+'&fragmento=1').then(function(r){return r.text()}).then(function(h){d.querySelector('.bx').innerHTML=h})}})})</script>"
        return HTMLResponse(pagina(f"<h2>Tabula vocum</h2><p class='mut'>Todas las voces, letra por letra, con página, número de leyes citadas y autores más citados. Pulsa una letra.</p>"+det+js,'','ambas','entrada'))
    def tit_nombre(src,b,t):
        T=(DT if src=='D' else CT if src=='C' else {}).get(b)
        return (T[t-1].capitalize() if T and 0<t<=len(T) else '')
    @mcp.custom_route("/loci",methods=["GET"])
    async def loci(request):
        ref=request.query_params.get('ref') or ''
        m=re.fullmatch(r'(D|C|CTh)\.(\d+)\.(\d+)',ref)
        if m:
            k=(m[1],int(m[2]),int(m[3]));ent=LOCI.get(k,{})
            h=f"<h2>{html.escape(ref)}</h2><p class='mut'>{html.escape(tit_nombre(*k))} · citado en {len(ent)} voces</p><table class='tb'><tr><th>Vox</th><th>p.</th><th>Leyes citadas</th></tr>"
            def key(x): return int(x) if x.isdigit() else 999
            for i in sorted(ent,key=lambda j:D[j]['hw']):
                h+=f"<tr><td><a href='/entrada?n={i}'>{html.escape(D[i]['hw'])}</a></td><td>{D[i]['page']}</td><td>{', '.join(sorted(ent[i],key=key))}</td></tr>"
            return HTMLResponse(pagina(h+"</table><p><a href='/loci'>&larr; Index locorum</a></p>",'','ambas','entrada'))
        src=request.query_params.get('src');b=request.query_params.get('libro')
        if request.query_params.get('fragmento') and src in('D','C','CTh') and b and b.isdigit():
            ts=sorted((k for k in LOCI if k[0]==src and k[1]==int(b)),key=lambda k:k[2])
            return HTMLResponse("<ul>"+''.join(f"<li><a href='/loci?ref={k[0]}.{k[1]}.{k[2]}'>{k[0]}.{k[1]}.{k[2]}</a> {html.escape(tit_nombre(*k))} <span class='mut'>({len(LOCI[k])} voces)</span></li>" for k in ts)+"</ul>")
        det=''
        for src,nom,rng in(('D','Digesta',range(1,51)),('C','Codex',range(1,13)),('CTh','Codex Theodosianus',range(1,17))):
            det+=f"<h3>{nom}</h3>"
            for b in rng:
                n=sum(len(v) for k,v in LOCI.items() if k[0]==src and k[1]==b)
                if n: det+=f"<details class='ab' data-l='{b}' data-s='{src}'><summary>{src}. {b} <span class='mut'>({n} citas)</span></summary><div class='bx'></div></details>"
        js="<script>document.querySelectorAll('details.ab[data-s]').forEach(function(d){d.addEventListener('toggle',function(){if(d.open&&!d.dataset.ok){d.dataset.ok=1;fetch('/loci?fragmento=1&src='+d.dataset.s+'&libro='+d.dataset.l).then(function(r){return r.text()}).then(function(h){d.querySelector('.bx').innerHTML=h})}})})</script>"
        return HTMLResponse(pagina("<h2>Index locorum</h2><p class='mut'>Los pasajes del Corpus Iuris que cita el libro (según las referencias convertidas, que pueden tener errores de OCR). Despliega un libro y elige un título para ver qué voces lo citan.</p>"+det+js,'','ambas','entrada'))
