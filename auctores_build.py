"""Extrae de la Perseus Digital Library (canonical-latinLit, CC BY-SA) los pasajes por libro y capítulo
de los autores que Brisson cita, en un fichero compacto: datos/auctores.json.gz"""
import glob,gzip,json,os,re,sys
import xml.etree.ElementTree as ET
RAIZ=sys.argv[1] if len(sys.argv)>1 else 'canonical-latinLit/data'
OBRAS={ # clave: (carpeta phi, obra, título)
 'gellius':('phi1254','phi001','Aulus Gellius, Noctes Atticae'),
 'plinius':('phi0978','phi001','Plinius Maior, Naturalis Historia'),
 'livius':('phi0914','phi001','Titus Livius, Ab urbe condita'),
 'valerius':('phi1038','phi001','Valerius Maximus, Facta et dicta memorabilia'),
 'quintilianus':('phi1002','phi001','Quintilianus, Institutio oratoria'),
 'columella':('phi0845','phi002','Columella, De re rustica'),
 'vitruvius':('phi1056','phi001','Vitruvius, De architectura'),
 'curtius':('phi0860','phi001','Curtius Rufus, Historiae Alexandri Magni'),
}
def loc(t): return t.rsplit('}',1)[-1]
def texto(e):
    s=[]
    def w(x):
        n=loc(x.tag)
        if n in('note','head','teiHeader','bibl'):
            if x.tail: s.append(x.tail)
            return
        if x.text: s.append(x.text)
        for c in x:
            if loc(c.tag)=='div' and c.get('n') and c.get('subtype','')=='section' or (loc(c.tag)=='div' and c.get('type')=='textpart' and c.get('n') and loc(x.tag)=='div' and x.get('subtype')=='chapter'):
                s.append(f" [{c.get('n')}] ")
            w(c)
        if x.tail: s.append(x.tail)
    w(e);return re.sub(r'\s+',' ',''.join(s)).strip()
def extrae(f):
    r=ET.parse(f).getroot();out={}
    body=next(e for e in r.iter() if loc(e.tag)=='body')
    def visit(el,ruta):
        for c in el:
            if loc(c.tag)!='div': continue
            n=c.get('n');st=c.get('subtype') or c.get('type')
            if n is None: visit(c,ruta);continue
            if st=='book' or (len(ruta)==0 and st in('textpart','book')):
                visit(c,[n]);continue
            if st=='chapter' and len(ruta)==1:
                out[f"{ruta[0]}.{n}"]=texto(c);continue
            if st in('section',) and len(ruta)==1 and False: pass
            visit(c,ruta+[n] if st not in('chapter','section') else ruta)
    visit(body,[]);return out
if __name__=='__main__':
    res={}
    for k,(a,w,t) in OBRAS.items():
        P={}
        for f in sorted(glob.glob(f'{RAIZ}/{a}/{w}/*lat*.xml')):
            try: d=extrae(f)
            except Exception as e: print('ERR',f,e);continue
            for kk,v in d.items():
                if len(v)>len(P.get(kk,'')): P[kk]=v
        print(k,len(P),sum(len(v) for v in P.values())//1000,'KB',list(P)[:3])
        res[k]={'t':t,'p':P}
    os.makedirs('datos',exist_ok=True)
    with gzip.open('datos/auctores.json.gz','wt',encoding='utf-8') as g: json.dump(res,g,ensure_ascii=False)
    print(os.path.getsize('datos/auctores.json.gz')/1e6,'MB')
