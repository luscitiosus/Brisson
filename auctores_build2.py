"""Añade a datos/auctores.json.gz (ya construido con auctores_build.py) más autores de Perseus canonical-latinLit:
Tácito, Suetonio y obras de Cicerón. Uso: python auctores_build2.py <canonical-latinLit/data>"""
import glob,gzip,json,os,re,sys
import xml.etree.ElementTree as ET
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from auctores_build import texto,loc
RAIZ=sys.argv[1]
V={'suet_iul':('phi1348','abo011','Suetonius, Diuus Iulius'),'suet_aug':('phi1348','abo012','Suetonius, Diuus Augustus'),
 'suet_tib':('phi1348','abo013','Suetonius, Tiberius'),'suet_cal':('phi1348','abo014','Suetonius, Caligula'),
 'suet_claud':('phi1348','abo015','Suetonius, Diuus Claudius'),'suet_ner':('phi1348','abo016','Suetonius, Nero'),
 'suet_galb':('phi1348','abo017','Suetonius, Galba'),'suet_oth':('phi1348','abo018','Suetonius, Otho'),
 'suet_vit':('phi1348','abo019','Suetonius, Vitellius'),'suet_vesp':('phi1348','abo020','Suetonius, Diuus Vespasianus'),
 'suet_tit':('phi1348','abo021','Suetonius, Diuus Titus'),'suet_dom':('phi1348','abo022','Suetonius, Domitianus'),
 'tac_ann':('phi1351','phi005','Tacitus, Annales'),'tac_hist':('phi1351','phi004','Tacitus, Historiae'),
 'cic_inv':('phi0474','phi036','Cicero, De inuentione'),'cic_off':('phi0474','phi055','Cicero, De officiis'),
 'cic_orat':('phi0474','phi037','Cicero, De oratore'),'cic_dom':('phi0474','phi020','Cicero, De domo sua'),
 'cic_diu':('phi0474','phi004','Cicero, Diuinatio in Q. Caecilium')}
def extrae(f):
    r=ET.parse(f).getroot();body=next(e for e in r.iter() if loc(e.tag)=='body');out={}
    def divs(e): return [c for c in e if loc(c.tag)=='div']
    def visit(el,libro):
        for c in divs(el):
            n=c.get('n');st=c.get('subtype') or c.get('type')
            if n is None: visit(c,libro);continue
            if st in('book','card') or (st=='textpart' and libro is None and divs(c) and (divs(c)[0].get('subtype') in('chapter','section'))):
                visit(c,n);continue
            if st in('chapter','section') or st=='textpart':
                out[f"{libro or 1}.{n}"]=texto(c);continue
            visit(c,libro)
    visit(body,None);return out
res=json.load(gzip.open('datos/auctores.json.gz','rt',encoding='utf-8'))
for k,(a,w,t) in V.items():
    fs=sorted(glob.glob(f'{RAIZ}/{a}/{w}/*lat*.xml'))
    if not fs: print('SIN TEXTO',k);continue
    P={}
    for f in fs:
        try: d=extrae(f)
        except Exception as e: print('ERR',f,e);continue
        for kk,v in d.items():
            if len(v)>len(P.get(kk,'')): P[kk]=v
    print(k,len(P),list(P)[:3]);res[k]={'t':t,'p':P}
with gzip.open('datos/auctores.json.gz','wt',encoding='utf-8') as g: json.dump(res,g,ensure_ascii=False)
print(os.path.getsize('datos/auctores.json.gz')/1e6,'MB')
