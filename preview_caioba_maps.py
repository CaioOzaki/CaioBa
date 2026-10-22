"""Perspective inspection of the meshes reloaded from the candidate Unity files."""
from pathlib import Path
import sys,numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'tools/python'))
import UnityPy
from UnityPy.helpers.MeshHelper import MeshHandler
def render(file,name,eye,at,palette,texture=None):
 e=UnityPy.load(str(R/'maps-v11'/file));o=next(o for o in e.objects if o.type.name=='Mesh' and name in o.read().m_Name)
 m=MeshHandler(o.read());m.process();v=np.array(m.m_Vertices);uv=np.array(m.m_UV0)
 eye=np.array(eye);forward=np.array(at)-eye;forward=forward/np.linalg.norm(forward);right=np.cross([0,1,0],forward);right/=np.linalg.norm(right);up=np.cross(forward,right)
 relative=v-eye;cam=np.array([relative@right,relative@up,relative@forward]).T
 W,H=1200,800;pix=np.full((H,W,3),[143,191,202],np.uint8);depth=np.full((H,W),np.inf)
 xy=cam[:,:2]/np.maximum(cam[:,2,None],.01)*850;xy[:,0]+=W/2;xy[:,1]=H/2-xy[:,1]
 for part,triangles in enumerate(m.get_triangles()):
  col=np.array(palette[part],float)
  for ids in triangles:
   ids=list(ids)
   if np.any(cam[ids,2]<.1):continue
   a,b,c=xy[ids];lo=np.maximum(np.floor(np.min([a,b,c],0)).astype(int),0);hi=np.minimum(np.ceil(np.max([a,b,c],0)).astype(int)+1,[W,H])
   if np.any(hi<=lo):continue
   xx,yy=np.meshgrid(np.arange(lo[0],hi[0])+.5,np.arange(lo[1],hi[1])+.5)
   den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
   if abs(den)<1e-9:continue
   w0=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/den
   w1=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/den;w2=1-w0-w1
   inv=w0/cam[ids[0],2]+w1/cam[ids[1],2]+w2/cam[ids[2],2];z=1/np.maximum(inv,1e-12)
   dest=depth[lo[1]:hi[1],lo[0]:hi[0]];mask=(w0>=0)&(w1>=0)&(w2>=0)&(z<dest)
   if not mask.any():continue
   n=np.cross(v[ids[1]]-v[ids[0]],v[ids[2]]-v[ids[0]]);n/=np.linalg.norm(n)
   light=.72+.28*abs(n@np.array([.2,.9,.3]))
   if texture is not None and part==0:
    u=(w0*uv[ids[0],0]/cam[ids[0],2]+w1*uv[ids[1],0]/cam[ids[1],2]+w2*uv[ids[2],0]/cam[ids[2],2])*z
    vv=(w0*uv[ids[0],1]/cam[ids[0],2]+w1*uv[ids[1],1]/cam[ids[1],2]+w2*uv[ids[2],1]/cam[ids[2],2])*z
    tx=np.clip((u*(texture.shape[1]-1)).astype(int),0,texture.shape[1]-1);ty=np.clip(((1-vv)*(texture.shape[0]-1)).astype(int),0,texture.shape[0]-1);rgb=(texture[ty,tx,:3]*light).astype(np.uint8)
    pix[lo[1]:hi[1],lo[0]:hi[0]][mask]=rgb[mask]
   else:pix[lo[1]:hi[1],lo[0]:hi[0]][mask]=(col*light).astype(np.uint8)
   dest[mask]=z[mask]
 im=Image.fromarray(pix);d=ImageDraw.Draw(im);d.rectangle((0,745,W,800),fill='#102938');d.text((20,762),'CAIOBA | Previa da geometria exportada. Iluminacao e objetos do jogo nao representados.',fill='white',font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20))
 return im
e=UnityPy.load(str(R/'maps-v11/sharedassets3.assets'));tex=np.array(next(o for o in e.objects if o.path_id==13).read().image)
render('level3','estrutura nova',(10,10,-16),(0,2,1),[(255,255,255),(18,51,67),(229,227,215),(23,118,129)],tex).save(R/'assets/caioba/indoor-preview.png')

e=UnityPy.load(str(R/'maps-v11/resources.assets'));tex=np.array(next(o for o in e.objects if o.path_id==42).read().image)
render('resources.assets','protecao postes',(90,90,-210),(0,85,0),[(255,255,255)],tex).save(R/'assets/caioba/poste-preview.png')
print('Indoor and actual post mesh previews saved')
