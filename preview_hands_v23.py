"""Smooth-shaded orthographic preview from actual serialized mesh buffers."""
from pathlib import Path
import sys,json
R=Path(__file__).resolve().parent;sys.path[:0]=[str(R),str(R/'tools/python')]
import numpy as np,UnityPy
from PIL import Image,ImageDraw,ImageFont
from test_hands_assets_v23 import unpack
from fix_gloves_v16 import hierarchy
OUT=R/'analysis'

def render(o,view,side,size=370):
 d,v,tr=unpack(o);pos=v[:,:3].copy();norm=v[:,3:6].copy()
 # Display each mirror in its anatomical view; both keep fingers upward.
 if side=='R':pos[:,0]*=-1;norm[:,0]*=-1
 if view=='front':axes=np.array([[0,1,0],[0,0,1],[1,0,0]])
 else:axes=np.array([[1,0,0],[0,0,1],[0,-1,0]])
 q=pos@axes.T;n=norm@axes.T;xy=np.stack([size*.46+q[:,0]*1100,size*.82-q[:,1]*1100],axis=1)
 im=np.full((size,size,3),245,dtype=np.uint8);depth=np.full((size,size),-1e9);light=np.array([-.35,.55,.76]);light/=np.linalg.norm(light)
 for ids in tr:
  p=xy[ids];edge1=p[1]-p[0];edge2=p[2]-p[0];area=edge1[0]*edge2[1]-edge1[1]*edge2[0]
  if abs(area)<1e-7:continue
  x0=max(0,int(p[:,0].min()));x1=min(size-1,int(p[:,0].max())+1);y0=max(0,int(p[:,1].min()));y1=min(size-1,int(p[:,1].max())+1)
  if x0>x1 or y0>y1:continue
  yy,xx=np.mgrid[y0:y1+1,x0:x1+1];a=((p[1,0]-xx)*(p[2,1]-yy)-(p[1,1]-yy)*(p[2,0]-xx))/area;b=((p[2,0]-xx)*(p[0,1]-yy)-(p[2,1]-yy)*(p[0,0]-xx))/area;c=1-a-b
  z=a*q[ids[0],2]+b*q[ids[1],2]+c*q[ids[2],2];old=depth[y0:y1+1,x0:x1+1];ok=(a>=0)&(b>=0)&(c>=0)&(z>old)
  no=a[...,None]*n[ids[0]]+b[...,None]*n[ids[1]]+c[...,None]*n[ids[2]];no/=np.maximum(np.linalg.norm(no,axis=2,keepdims=True),1e-12);shade=np.clip(.63+.37*(no@light),.32,1)
  color=np.array([207,165,129]) if v[ids,10].mean()<.6 else np.array([62,76,97]);rgb=np.clip(color*shade[...,None],0,255).astype(np.uint8);im[y0:y1+1,x0:x1+1][ok]=rgb[ok];old[ok]=z[ok]
 return Image.fromarray(im)

def hands(f):
 g,t,p=hierarchy(f);out={}
 for pose in ('Open','Closed','Thumb','Set'):
  for side in ('L','R'):
   suffix=f'Hand Root {side}/{pose}/Cloudcourt {pose} Glove' if pose in ('Open','Closed') else f'Hand Root {side}/'+('CC_ThumbsUp' if pose=='Thumb' else 'CC_SettingOpen')
   tid=next(i for path,i in p.items() if path.endswith(suffix));go=g[t[tid]['m_GameObject']['m_PathID']];fd=next(f.objects[c['component']['m_PathID']].read_typetree() for c in go['m_Component'] if f.objects[c['component']['m_PathID']].type.name=='MeshFilter');out[pose,side]=f.objects[fd['m_Mesh']['m_PathID']]
 return out

def main():
 files={ver:UnityPy.load(str(R/path/'resources.assets')).file for ver,path in [('v22','versions/cloudcourt-v22-antes-v23'),('v23','visuals-v23-hands')]};hs={ver:hands(f) for ver,f in files.items()};font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',23);small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',17)
 for comparison in (False,True):
  canvas=Image.new('RGB',(1500,1750),'white');dr=ImageDraw.Draw(canvas);dr.text((20,12),'OFFLINE SERIALIZED 3D PREVIEW - not a headset capture',fill='#213249',font=font)
  rows=[('v22','L','front'),('v23','L','front'),('v22','L','side'),('v23','L','side')] if comparison else [('v23','L','front'),('v23','L','side'),('v23','R','front'),('v23','R','side')]
  for row,(ver,side,view) in enumerate(rows):
   for col,pose in enumerate(('Open','Closed','Thumb','Set')):
    y=60+row*415;x=col*375;canvas.paste(render(hs[ver][pose,side],view,side),(x,y+35));dr.text((x+12,y+3),f'{ver} {pose} | {side} {view}',fill='#213249',font=small)
  dr.text((18,1730),'Same camera scale, neutral skin/cuff palette; +Y thumb edge / +Z fingers. Runtime poses and transforms unchanged.',fill='#31455c',font=small)
  name='v23-hands-comparison.png' if comparison else 'v23-hands-preview.png';canvas.save(OUT/name);print(OUT/name)
 (OUT/'v23-hands-preview.json').write_text(json.dumps(dict(scope='Offline actual serialized geometry, smooth vertex-normal shading, neutral palette; not headset capture',files=['v23-hands-preview.png','v23-hands-comparison.png'],camera='Orthographic front +X and side -Y; same scale 1100px/m; mirrored anatomical views',all_poses=['Open','Closed','Thumb','Set'],sides=['L','R']),indent=2))
if __name__=='__main__':main()

