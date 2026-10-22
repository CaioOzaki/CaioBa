from pathlib import Path
import sys,json,numpy as np
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'tools/python'))
import UnityPy
from UnityPy.helpers.MeshHelper import MeshHandler
out={}
for f in ['level1','level2','level3']:
 e=UnityPy.load(str(R/'maps-v11'/f)).file
 for o in e.objects.values():
  if o.type.name=='Mesh' and o.read().m_Name.startswith('Caioba'):
   name=o.read().m_Name;m=MeshHandler(o.read());m.process();v=np.array(m.m_Vertices);tris=np.array([t for part in m.get_triangles() for t in part]);assert np.isfinite(v).all()
   hits=[]
   for x,z in [(0,0),(-4,-8),(4,8),(0,-11),(0,11)]:
    yy=[]
    for a,b,c in v[tris]:
     den=(b[2]-c[2])*(a[0]-c[0])+(c[0]-b[0])*(a[2]-c[2])
     if abs(den)<1e-8:continue
     u=((b[2]-c[2])*(x-c[0])+(c[0]-b[0])*(z-c[2]))/den
     w=((c[2]-a[2])*(x-c[0])+(a[0]-c[0])*(z-c[2]))/den
     if u>=-1e-7 and w>=-1e-7 and u+w<=1+1e-7:yy.append(float(u*a[1]+w*b[1]+(1-u-w)*c[1]))
    assert yy
    if 'teto' in name:assert min(yy)>13
    else:assert abs(min(yy))<.01,(f,x,z,yy)
    hits.append(round(min(yy),4))
   out[f+':'+name]={'vertices':len(v),'triangles':len(tris),'vertical_contacts':hits}
 for o in e.objects.values():
  if o.type.name in ['MeshFilter','MeshCollider']:
   d=o.read_typetree();p=d.get('m_Mesh',{});i=p.get('m_PathID',0)
   if i and p.get('m_FileID')==0:assert i in e.objects
res=UnityPy.load(str(R/'maps-v11/resources.assets')).file
for i in [40,42,47,51,52]:
 t=res.objects[i].read();im=t.image;assert im.width>0
 if i==51:assert im.mode=='RGBA' and im.getextrema()[3]==(0,255),(im.mode,im.getextrema())
 out[t.m_Name]={'size':im.size,'mode':im.mode}
(R/'analysis/maps-validation.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
