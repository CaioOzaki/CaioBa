"""Original v26 CloudCourt art deltas. Caller owns asset serialization.
No legacy build imports, game installation, scripts or collider changes.
"""
from pathlib import Path
import copy,json,math,sys
R=Path(__file__).resolve().parent
sys.path[:0]=[str(R),str(R/'tools/python')]
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from build_environment_v21 import (put,readable,ptr,vec,clone,named,material,owned_mesh,owned_material,visual,geometry_class,snapshot,delta,set_rgb_full_mips)
from fix_gloves_v16 import hierarchy
A=R/'assets/cloudcourt-v26'
FONT='C:/Windows/Fonts/arialbd.ttf'

def label(im,xy,text,size,fill='#102b53',stroke=0):
 ImageDraw.Draw(im).text(xy,text,font=ImageFont.truetype(FONT,size),anchor='mm',fill=fill,stroke_width=stroke,stroke_fill='#101b31')

def ball_art(beach=False):
 """Own geometric panel design, not a branded original or traced image."""
 n=1024;y,x=np.mgrid[:n,:n];u=x/n;v=y/n
 # Continuous periodic wave seams; horizontal wrap closes exactly on the sphere.
 panel=np.floor((u+.045*np.sin(v*math.pi*2))*8).astype(int)%8
 if beach:
  colors=np.array([[250,246,227],[247,203,31],[26,102,186],[250,246,227],[247,203,31],[26,102,186],[250,246,227],[26,102,186]])
 else:colors=np.array([[250,211,20],[22,73,164]]*4)
 rgb=colors[panel].astype(np.uint8)
 phase=((u+.045*np.sin(v*math.pi*2))*8)%1
 seam=(phase<.009)|(phase>.991);rgb[seam]=[23,43,66]
 # Fine own pebble texture, low contrast and smaller than printed artwork.
 dots=((x%9-4)**2+(y%9-4)**2)<1.8
 rgb[dots]=np.maximum(rgb[dots].astype(int)-9,0)
 im=Image.fromarray(rgb)
 for cx in [256,768]:
  # Brand is on a clean original central badge, readable on two sides.
  d=ImageDraw.Draw(im);d.rounded_rectangle((cx-153,438,cx+153,570),radius=24,fill='#f8efcc',outline='#102b53',width=5)
  label(im,(cx,481),'CloudCourt',43)
  label(im,(cx,535),'BEACH PRO' if beach else 'INDOOR 300',22)
 return im

def banner_art():
 im=Image.new('RGB',(512,1536),'#194c8d');d=ImageDraw.Draw(im)
 d.rectangle((12,12,499,1523),outline='#ffd34c',width=12)
 d.rectangle((35,35,476,1500),outline='#eff8ff',width=3)
 for y in range(70,1500,100):
  d.line((52,y,116,y-48),fill='#3376b5',width=10);d.line((396,y+48,460,y),fill='#3376b5',width=10)
 # Own rising-cloud/volleyball emblem.
 d.ellipse((136,64,376,304),fill='#ffd34c',outline='#10223b',width=10)
 d.arc((159,88,352,280),25,335,fill='#174a87',width=9)
 d.arc((190,88,320,280),75,285,fill='#174a87',width=8)
 d.line((163,183,348,183),fill='#174a87',width=8)
 for i,c in enumerate('CLOUDCOURT'):
  label(im,(256,370+i*98),c,101,fill='#fff3cf',stroke=6)
 d.polygon([(113,1390),(256,1334),(399,1390),(256,1446)],fill='#ffd34c',outline='#10223b',width=6)
 label(im,(256,1393),'VR',55)
 return im

def sphere_geometry(radius=10.2908):
 G=geometry_class();g=G(1);rows=24;cols=64
 def p(i,j):
  a=2*math.pi*i/cols;t=math.pi*j/rows
  return (radius*math.sin(t)*math.cos(a),radius*math.cos(t),radius*math.sin(t)*math.sin(a))
 for j in range(rows):
  for i in range(cols):
   # Geometry derives outward normals from this ordering; UV0 left half atlas.
   pts=[p(i,j),p(i,j+1),p(i+1,j+1),p(i+1,j)]
   if j in (0,rows-1):
    # Pole quads deliberately have one collapsed triangle, matching UV seam.
    pass
   g.quad(0,list(reversed(pts)),list(reversed([((1-i/cols)*.5,1-j/rows),((1-i/cols)*.5,1-(j+1)/rows),((1-(i+1)/cols)*.5,1-(j+1)/rows),((1-(i+1)/cols)*.5,1-j/rows)])))
 return g

def texture(f,template,name,image):
 o=named(f,'Texture2D',name)
 if o is None:
  d=copy.deepcopy(template.read_typetree());d['m_Name']=name;o=f.objects[clone(f,template,d)]
 t=o.read();set_rgb_full_mips(t,image);t.save();readable(o);return o.path_id

def build_art_assets_v26(files,write_art=True):
 if write_art:A.mkdir(parents=True,exist_ok=True)
 before={n:snapshot(f) for n,f in files.items()}
 f=files['resources.assets'];indoor=ball_art();beach=ball_art(True)
 dual=Image.new('RGB',(2048,1024));dual.paste(indoor,(0,0));dual.paste(beach,(1024,0))
 t=f.objects[40].read();set_rgb_full_mips(t,dual);t.save();readable(f.objects[40])
 # Existing actual visible binding, shared by offline/host/client balls.
 put(f.objects[3],material(f,f.objects[3],'CloudCourt Per Map Ball','#ffffff',ptr(148,2),40))
 g=sphere_geometry();d=g.serial(f.objects[62].read_typetree(),'CloudCourt dual-atlas ball')
 d['m_VertexData']['m_Channels'][5]=dict(stream=0,offset=48,format=0,dimension=2)
 # Spherical vertex normals avoid visible latitude facets in directional lighting.
 raw=bytearray(d['m_VertexData']['m_DataSize']);v=np.ndarray((d['m_VertexData']['m_VertexCount'],14),dtype='<f4',buffer=raw)
 v[:,3:6]=v[:,:3]/np.linalg.norm(v[:,:3],axis=1)[:,None];d['m_VertexData']['m_DataSize']=bytes(raw);put(f.objects[62],d)
 s=files['level3'];banner=banner_art();tex=texture(s,next(o for o in s.objects.values() if o.type.name=='Texture2D'),'CloudCourt vertical flag v26',banner)
 mat_template=next(o for o in s.objects.values() if o.type.name=='Material')
 mat=owned_material(s,mat_template,'CloudCourt vertical flag v26','#ffffff',ptr(148,2),tex)
 old=named(s,'Mesh','Cloudcourt arena ribbons');assert old is not None
 g=geometry_class()(1)
 for sign in [-1,1]:
  for z in [-14,-6,2,10,14]:
   x=sign*11.20;points=[(x,5.15,z-.55),(x,7.65,z-.55),(x,7.65,z+.55),(x,5.15,z+.55)]
   # Each wall faces court; no rear text mirroring, no collision components.
   if sign==1:points=list(reversed(points))
   g.quad(0,points);g.quad(0,list(reversed(points)))
 mid=owned_mesh(s,old,g,'Cloudcourt arena ribbons');visual(s,'Cloudcourt Arena Banners',mid,[mat])
 # Indoor scene uses a separate net copy, not the resources GameRules prefab.
 ant=named(f,'Mesh','Cloudcourt visual antennas');assert ant is not None
 ant_id=clone(s,next(o for o in s.objects.values() if o.type.name=='Mesh'),ant.read_typetree())
 a_material=named(f,'Material','Cloudcourt Soft Gloves');assert a_material
 # Use the resources palette through a valid scene external reference.
 scene_mat=copy.deepcopy(a_material.read_typetree());scene_mat['m_Name']='CloudCourt antenna palette v26'
 scene_mat['m_Shader']=ptr(148,2)
 for _,v in scene_mat['m_SavedProperties']['m_TexEnvs']:
  v['m_Texture']['m_FileID']=3 if v['m_Texture']['m_PathID'] else 0
 amid=clone(s,mat_template,scene_mat);visual(s,'CloudCourt Indoor Antennas v26',ant_id,[amid])
 if write_art:
  for nm,im in [('ball-indoor',indoor),('ball-beach',beach),('ball-dual-atlas',dual),('arena-flag',banner)]:im.save(A/(nm+'.png'))
 # Day beach lost its cube-net renderer; restore only that component disabled.
 # Online lifecycle activates it for lobby practice and hides it for match.
 lobby_net=None
 if 'level1' in files:
  beach_scene=files['level1'];gs,ts,paths=hierarchy(beach_scene);tr=paths['Environment/Net net'];gid=ts[tr]['m_GameObject']['m_PathID'];go=copy.deepcopy(gs[gid])
  if not any(beach_scene.objects[c['component']['m_PathID']].type.name=='MeshRenderer' for c in go['m_Component']):
   template=next(o for o in beach_scene.objects.values() if o.type.name=='MeshRenderer');rd=copy.deepcopy(template.read_typetree())
   resources_index=next(i+1 for i,e in enumerate(beach_scene.externals) if e.path.endswith('resources.assets'))
   rd.update(m_GameObject=ptr(gid),m_Enabled=False,m_Materials=[ptr(10,resources_index)],m_StaticBatchInfo=dict(firstSubMesh=0,subMeshCount=0),m_StaticBatchRoot=ptr(0),m_LightmapIndex=65535)
   lobby_net=clone(beach_scene,template,rd);go['m_Component'].append(dict(component=ptr(lobby_net)));put(beach_scene.objects[gid],go)
 report=dict(changed_objects={n:delta(f,before[n]) for n,f in files.items()},ball=dict(texture=40,material=3,mesh=62,child_path='VisualVolleyball/RegularMesh/DavidVolleyball',atlas_size=[2048,1024],uv_x_range=[0,.5],indoor_offset=[0,0],beach_offset=[.5,0],runtime_map_offset_required=True),flags=dict(texture=tex,material=mat,mesh=mid,count=10),indoor_antennas=dict(mesh=ant_id,material=amid),original_geometry_and_art=True,lobby_net_renderer_added=lobby_net)
 return report





