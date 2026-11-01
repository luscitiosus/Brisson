"""Textos latinos del Digesto, Código, Instituciones y Código Teodosiano, para enlazar las citas del Brisson.

Fuente: BIA, Bibliotheca Iuris Antiqui (IGSG-CNR), CC BY-NC-SA 4.0. Se descargan al construir la imagen
(`python romanos.py`), igual que en el conector Romanorum. Si la descarga falla, la web sigue funcionando sin enlaces.
"""
import html, os, re, sqlite3, sys, time, unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB = Path(os.environ.get('ROMANOS_DB', ROOT / 'data' / 'romanos.db'))
API = 'https://dspace-clarin-it.ilc.cnr.it/server/api'
OBRAS = {  # sigla de Brisson -> (id, título, uuid DSpace, handle)
    'D': ('digesta', 'Digesta Iustiniani', 'df516228-3a20-4e4c-bcbc-4b6f5483d113', 'OPEN-972'),
    'C': ('codex', 'Codex Iustinianus', '8db00bdc-18ac-4fa2-9151-71d9318892f8', 'OPEN-967'),
    'CTh': ('cth', 'Codex Theodosianus', 'abd9457a-d67a-4567-80a2-b540d9286e4a', 'OPEN-968'),
    'PS': ('ps', 'Pauli Sententiae (Receptae Sententiae)', '4968ba6f-ce21-400a-87c7-767e69cf0ca9', 'OPEN-965'),
    'I': ('inst', 'Institutiones Iustiniani', 'e412fd76-6830-4e1a-8fb1-df496d63a049', 'OPEN-962'),
}
_DIV = re.compile(r'^div\d*$'); _WS = re.compile(r'\s+')
_BLOCK = {'p', 'head', 'argument', 'lg', 'l', 'ab', 'lb', 'milestone'}
def local(t): return t.rsplit('}', 1)[-1]
def clean(s): return _WS.sub(' ', s).strip()
def fold(s):
    s = unicodedata.normalize('NFKD', s)
    return ''.join(c for c in s if not unicodedata.combining(c)).lower()
def split_ref(ref):
    toks = re.findall(r'[0-9]+|[a-z]+', fold(ref)); i = 0
    while i < len(toks) and not toks[i].isdigit(): i += 1
    rest = ['pr' if t in ('princ', 'principium') else t for t in toks[i:]]
    return [(t.lstrip('0') or '0') if t.isdigit() else t for t in rest]
def own_text(el, skip_head=False):
    out = []
    def walk(e, top):
        name = local(e.tag)
        if not top and _DIV.match(name): return
        if name == 'teiHeader' or (skip_head and not top and name == 'head'):
            if e.tail and not top: out.append(e.tail)
            return
        if name == 'milestone' and e.get('n'): out.append(f" §{e.get('n')} ")
        elif name in _BLOCK: out.append(' ')
        if e.text: out.append(e.text)
        for c in e:
            walk(c, False)
            if _DIV.match(local(c.tag)) and c.tail: out.append(c.tail)
        if not top and e.tail: out.append(e.tail)
    walk(el, True); return clean(''.join(out))
def head_text(el):
    for c in el:
        if local(c.tag) in ('head', 'argument'): return clean(' '.join(c.itertext()))
    for c in el:
        if _DIV.match(local(c.tag)) and (c.get('type') or '').lower() in ('rubrica', 'rubric'): return own_text(c)
    return ''

SCHEMA = """CREATE TABLE nodes(id INTEGER PRIMARY KEY, w TEXT, key TEXT, n TEXT, type TEXT, leaf INTEGER,
 depth INTEGER, parent INTEGER, ord INTEGER, head TEXT, text TEXT);
CREATE INDEX nk ON nodes(w,key); CREATE INDEX np ON nodes(parent);
CREATE TABLE obras(w TEXT PRIMARY KEY, titulo TEXT, handle TEXT);"""

def ingest(con, w, path):
    root = ET.parse(path).getroot()
    body = next((e for e in root.iter() if local(e.tag) == 'body'), root)
    cnt = [0]
    def visit(el, pid, pkey, depth):
        seen = set(); idx = 0
        for ch in el:
            if not _DIV.match(local(ch.tag)): continue
            idx += 1; n = ch.get('n') or ''; typ = ch.get('type') or ''
            parts = split_ref(n)
            if pkey and not re.match(r'[a-zA-Z]', n or '0') and parts: parts = pkey.split('#')[0].split('.') + parts
            key = '.'.join(parts) if parts else (f'{pkey}.{idx}' if pkey else str(idx))
            if pkey is not None and key == pkey: key = f"{key}#{fold(typ) or 'x'}"
            if key in seen: key = f'{pkey}.{idx}' if pkey else str(idx)
            seen.add(key)
            leaf = not any(_DIV.match(local(c.tag)) for c in ch)
            cnt[0] += 1
            cur = con.execute('INSERT INTO nodes(w,key,n,type,leaf,depth,parent,ord,head,text) VALUES(?,?,?,?,?,?,?,?,?,?)',
                (w, key, n or key, typ, int(leaf), depth, pid, cnt[0], head_text(ch), own_text(ch, skip_head=not leaf)))
            visit(ch, cur.lastrowid, key, depth + 1)
    visit(body, None, None, 0); return cnt[0]

def build():
    import httpx
    DB.parent.mkdir(parents=True, exist_ok=True)
    tmp = DB.with_suffix('.tmp'); tmp.unlink(missing_ok=True)
    con = sqlite3.connect(tmp); con.executescript(SCHEMA)
    cl = httpx.Client(timeout=httpx.Timeout(300, connect=30), follow_redirects=True, headers={'User-Agent': 'brisson-web/1.0 (estudio personal)'})
    ok = 0
    for sig, (w, titulo, uuid, h) in OBRAS.items():
        xml = DB.parent / f'{w}.xml'
        try:
            for intento in range(4):
                try:
                    bundles = cl.get(f'{API}/core/items/{uuid}/bundles').json(); done = False
                    for b in bundles['_embedded']['bundles']:
                        if b['name'] != 'ORIGINAL': continue
                        for bs in cl.get(b['_links']['bitstreams']['href']).json()['_embedded']['bitstreams']:
                            if bs['name'].lower().endswith('.xml'):
                                r = cl.get(f"{API}/core/bitstreams/{bs['uuid']}/content"); r.raise_for_status()
                                xml.write_bytes(r.content); done = True; break
                        if done: break
                    if not done: raise RuntimeError('sin XML')
                    break
                except Exception as e:
                    print('  reintento', w, e, file=sys.stderr); time.sleep(2 ** (intento + 1))
            else: raise RuntimeError('descarga fallida')
            n = ingest(con, w, xml); xml.unlink(missing_ok=True)
            con.execute('INSERT INTO obras VALUES(?,?,?)', (w, titulo, f'http://hdl.handle.net/20.500.11752/{h}'))
            print('  ok', w, n, file=sys.stderr); ok += 1
        except Exception as e:
            print('  fallo', w, e, file=sys.stderr)
    con.commit(); con.execute('VACUUM'); con.close()
    if ok: tmp.replace(DB)
    else: tmp.unlink(missing_ok=True); print('Sin textos romanos: la web funcionará sin esos enlaces.', file=sys.stderr)

class Fuentes:
    def __init__(self):
        self.con = None
        if DB.exists():
            try: self.con = sqlite3.connect(f'file:{DB}?mode=ro', uri=True, check_same_thread=False); self.con.row_factory = sqlite3.Row
            except Exception: self.con = None
    def ok(self): return self.con is not None
    def obras(self): return {r['w'] for r in self.con.execute('SELECT w FROM obras')} if self.ok() else set()
    def _frag(self, w, partes):
        """Nodo de la ley (libro.título.ley); 'ult' = la última del título."""
        b, t, l = partes[:3]
        if l == 'ult':
            nums = []
            for r in self.con.execute("SELECT key FROM nodes WHERE w=? AND key LIKE ? AND depth>=2", (w, f'{b}.{t}.%')):
                p = r['key'].split('.')
                if len(p) == 3 and p[2].isdigit(): nums.append(int(p[2]))
            if not nums: return None
            l = str(max(nums))
        return self.con.execute('SELECT * FROM nodes WHERE w=? AND key=? ORDER BY ord', (w, f'{b}.{t}.{l}')).fetchone()
    def leer(self, sig, ref):
        """ref = '1.1.10' o '1.1.10.pr' → (título obra, rúbrica, [(etiqueta, texto)], etiqueta destacada, nota)"""
        if not self.ok() or sig not in OBRAS: return None
        w = OBRAS[sig][0]; partes = [p for p in ref.split('.') if p]
        if sig == 'PS':
            if len(partes) < 2: return None
            fr = self.con.execute('SELECT * FROM nodes WHERE w=? AND key=? ORDER BY ord', (w, f'{partes[0]}.{partes[1]}')).fetchone()
            partes = partes[:2] + [''] + partes[2:3]
        elif len(partes) < 3: return None
        else: fr = self._frag(w, partes)
        if not fr: return None
        tit = fr if sig == 'PS' else self.con.execute('SELECT head FROM nodes WHERE w=? AND key=?', (w, '.'.join(partes[:2]))).fetchone()
        filas = []
        def walk(n):
            if n['leaf']: filas.append((n['n'] if n['type'].lower() not in ('inscriptio', 'subscriptio') else n['type'].lower(), n['text']))
            elif n['text']: filas.append((n['n'], n['text']))
            for c in self.con.execute('SELECT * FROM nodes WHERE parent=? ORDER BY ord', (n['id'],)): walk(c)
        walk(fr)
        ult = fr['key'].split('.')
        return {'obra': OBRAS[sig][1], 'tit': tit['head'] if tit else '', 'ley': fr['key'], 'filas': filas,
                'dest': partes[3] if len(partes) > 3 else ''}

if __name__ == '__main__':
    try: build()
    except Exception as e: print('romanos.py:', e, file=sys.stderr)
