"""Detecta las manecillas (☞/☜) del margen del Brisson-Heineccio 1743: marcan la línea donde empieza cada adición de Heineccio.
Requisitos: poppler (pdftoppm, pdftotext) en el PATH, y `pip install opencv-python numpy`.
Uso:  python manecillas.py brisson.pdf salida.json [--desde 1] [--hasta 1500] [--procesos 4]
Salida: lista de {pagina, lado, score, linea} (la línea impresa a la que apunta la manecilla)."""
import argparse,json,os,re,subprocess,sys,tempfile
from concurrent.futures import ProcessPoolExecutor
import cv2,numpy as np
AQUI=os.path.dirname(os.path.abspath(__file__))
TPL=cv2.imread(os.path.join(AQUI,'manecilla_izq.png'),0)
TPD=cv2.imread(os.path.join(AQUI,'manecilla_der.png'),0)
DPI=200
def lineas(pdf,n):
    x=subprocess.run(['pdftotext','-f',str(n),'-l',str(n),'-bbox-layout',pdf,'-'],capture_output=True,text=True,encoding='utf-8').stdout
    pw,ph=[float(v) for v in re.search(r'<page width="([\d.]+)" height="([\d.]+)"',x).groups()]
    L=[]
    for m in re.finditer(r'<line xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</line>',x,re.S):
        x0,y0,x1,y1=[float(v) for v in m.groups()[:4]]
        t=' '.join(re.findall(r'>([^<]+)</word>',m.group(5)))
        L.append((x0,y0,x1,y1,t))
    return pw,ph,L
def detecta(img):
    res=[]
    for lado,t,thr,esc in(('izq',TPL,0.70,(0.7,0.8,0.9,1.0)),('der',cv2.flip(TPL,1),0.74,(0.7,0.8,0.9,1.0)),('der',TPD,0.72,(0.8,0.9,1.0,1.1,1.2))):
        for s in esc:
            tt=cv2.resize(t,None,fx=s,fy=s,interpolation=cv2.INTER_AREA)
            r=cv2.matchTemplate(img,tt,cv2.TM_CCOEFF_NORMED)
            ys,xs=np.where(r>=thr)
            res+=[(float(r[y,x]),lado,x+tt.shape[1]/2,y+tt.shape[0]/2) for y,x in zip(ys,xs)]
    res.sort(reverse=True);keep=[]
    for sc,lado,cx,cy in res:
        if all(abs(cx-k[2])>40 or abs(cy-k[3])>25 for k in keep): keep.append((sc,lado,cx,cy))
    return keep
def pagina(args):
    pdf,n=args
    with tempfile.TemporaryDirectory() as d:
        subprocess.run(['pdftoppm','-r',str(DPI),'-f',str(n),'-l',str(n),'-gray','-png',pdf,os.path.join(d,'p')],check=True)
        f=[x for x in os.listdir(d) if x.endswith('.png')][0]
        img=cv2.imread(os.path.join(d,f),0)
    pw,ph,L=lineas(pdf,n)
    k=pw/img.shape[1];out=[]
    for sc,lado,cx,cy in detecta(img):
        cx*=k;cy*=k;mejor=None
        for x0,y0,x1,y1,t in L:
            if len(t.replace(' ',''))<4: continue
            dist=(x0-cx) if lado=='izq' else (cx-x1)
            if -8<=dist<=90 and y0-4<=cy<=y1+4:
                dy=abs((y0+y1)/2-cy)
                if mejor is None or dy<mejor[0]: mejor=(dy,t)
        out.append({'pagina':n,'lado':lado,'score':round(sc,2),'y':round(cy,1),'linea':mejor[1] if mejor else None})
    return out
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('pdf');ap.add_argument('salida')
    ap.add_argument('--desde',type=int,default=1);ap.add_argument('--hasta',type=int,default=0);ap.add_argument('--procesos',type=int,default=2)
    a=ap.parse_args()
    if not a.hasta:
        info=subprocess.run(['pdfinfo',a.pdf],capture_output=True,text=True).stdout
        a.hasta=int(re.search(r'Pages:\s+(\d+)',info).group(1))
    res=[]
    with ProcessPoolExecutor(a.procesos) as ex:
        for i,o in enumerate(ex.map(pagina,[(a.pdf,n) for n in range(a.desde,a.hasta+1)]),a.desde):
            res+=o
            if i%50==0: print('página',i,len(res),'manecillas',file=sys.stderr,flush=True)
    json.dump(res,open(a.salida,'w',encoding='utf-8'),ensure_ascii=False,indent=1)
    print(len(res),'manecillas;',sum(1 for r in res if not r['linea']),'sin línea asignada')
