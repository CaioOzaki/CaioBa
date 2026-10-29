"""Author new low-poly venue meshes and vector-pattern atlases for build 9216628.
No changes to the native gameplay DLL. Original scenes retained in version backup.
"""
from pathlib import Path
import sys,copy,struct,json,math,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'tools/python'))
import UnityPy
from UnityPy.helpers.MeshHelper import MeshHandler
DATA=R/'working/VolleyballFever_Data'
OUT=R/'maps-v11';OUT.mkdir(exist_ok=True)
A=R/'assets/caioba';A.mkdir(exist_ok=True)
env=UnityPy.load(str(DATA))
files={o.assets_file.name:o.assets_file for o in env.objects}
# Always build from the preserved pre-map objects, avoiding accumulated edits.
for n in ['resources.assets','level1','level2','level3','sharedassets1.assets','sharedassets3.assets']:
 old=UnityPy.load(str(R/'versions/v10-antes-mapas'/n)).file
 # Resolve external streams through the existing complete installation.
 old.parent=env;files[n]=old
def obj(f,i):return files[f].objects[i]
def tree(f,i):return obj(f,i).read_typetree()
def save(f,i,d):obj(f,i).save_typetree(d)
def ptr(i,f=0):return {'m_FileID':f,'m_PathID':i}
def vec(x,y,z):return dict(x=float(x),y=float(y),z=float(z))
def clone(source,f,data):
 target=files[f];o=copy.copy(source);o.assets_file=target;o.path_id=max(target.objects)+1
 match=next((i for i,t in enumerate(target.types) if t.class_id==source.class_id and t.script_type_index==source.serialized_type.script_type_index),None)
 if match is None:match=len(target.types);target.types.append(copy.deepcopy(source.serialized_type))
 o.type_id=match;o.serialized_type=target.types[match];o.data=source.get_raw_data();target.objects[o.path_id]=o;o.save_typetree(data)
 return o.path_id
def color(s):return dict(zip('rgba',[int(s[i:i+2],16)/255 for i in (1,3,5)]+[1.]))
def material(f,i,name,hexcolor,texture=None):
 d=tree(f,i);d['m_Name']=name;d['m_ShaderKeywords']='_EMISSION';d['m_LightmapFlags']=2
 p=d['m_SavedProperties'];p['m_TexEnvs']=[('_MainTex',{'m_Texture':ptr(texture or 0),'m_Scale':dict(x=1.,y=1.),'m_Offset':dict(x=0.,y=0.)})]
 p['m_Floats']=[(k,0. if k in ['_Metallic','_Glossiness','_GlossMapScale','_Parallax'] else v) for k,v in p['m_Floats']]
 c=color(hexcolor);em={k:(v*.23 if k!='a' else 1.) for k,v in c.items()}
 p['m_Colors']=[('_Color',c),('_EmissionColor',em)]
 return d
class Geometry:
 def __init__(self,n):self.parts=[[] for _ in range(n)]
 def quad(self,part,points,uv=None):
  p=np.array(points,float);normal=np.cross(p[1]-p[0],p[2]-p[0]);normal/=np.linalg.norm(normal)
  self.parts[part].append((p.tolist(),normal.tolist(),uv or [(0,0),(0,1),(1,1),(1,0)]))
 def box(self,part,c,size):
  x,y,z=c;a,b,d=np.array(size)/2
  v=[(x-a,y-b,z-d),(x+a,y-b,z-d),(x+a,y+b,z-d),(x-a,y+b,z-d),(x-a,y-b,z+d),(x+a,y-b,z+d),(x+a,y+b,z+d),(x-a,y+b,z+d)]
  for face in [(0,3,2,1),(4,5,6,7),(0,4,7,3),(1,2,6,5),(3,7,6,2),(0,1,5,4)]:self.quad(part,[v[i] for i in face])
 def floor(self,part,x0,x1,z0,z1,y=0,uv=None):self.quad(part,[(x0,y,z0),(x0,y,z1),(x1,y,z1),(x1,y,z0)],uv)
 def serial(self,template,name):
  d=copy.deepcopy(template);verts=[];indices=[];subs=[]
  for part in self.parts:
   first=len(verts);start=len(indices)
   for p,n,uv in part:
    k=len(verts)
    for point,tex in zip(p,uv):verts.append(tuple(point)+tuple(n)+(1.,0.,0.,1.)+tuple(tex)+tuple(tex))
    indices.extend([k,k+1,k+2,k,k+2,k+3])
   bounds=np.array([v[:3] for v in verts[first:]]) if len(verts)>first else np.zeros((1,3))
   subs.append(dict(firstByte=start*2,indexCount=len(indices)-start,topology=0,baseVertex=0,firstVertex=first,vertexCount=len(verts)-first,localAABB=aabb(bounds)))
  assert len(verts)<65536
  d['m_Name']=name;d['m_SubMeshes']=subs;d['m_IndexFormat']=0;d['m_IndexBuffer']=struct.pack('<'+'H'*len(indices),*indices)
  d['m_VertexData']['m_VertexCount']=len(verts);d['m_VertexData']['m_DataSize']=b''.join(struct.pack('<14f',*v) for v in verts)
  d['m_LocalAABB']=aabb(np.array([v[:3] for v in verts]));d['m_StreamData']=dict(offset=0,size=0,path='')
  d['m_BakedConvexCollisionMesh']=b'';d['m_BakedTriangleCollisionMesh']=b'';d['m_IsReadable']=True
  return d
 def export(self,name):
  (A/(name+'.json')).write_text(json.dumps(self.parts))
def aabb(v):return {'m_Center':vec(*((v.min(0)+v.max(0))/2)),'m_Extent':vec(*((v.max(0)-v.min(0))/2))}
def reset_renderer(d):
 d['m_StaticBatchInfo']=dict(firstSubMesh=0,subMeshCount=0);d['m_StaticBatchRoot']=ptr(0)
 d['m_LightmapIndex']=65535;d['m_LightmapTilingOffset']=dict(x=1.,y=1.,z=0.,w=0.);d['m_ProbeAnchor']=ptr(0)
 return d
def settex(f,i,im):
 t=obj(f,i).read();t.set_image(im,mipmap_count=t.m_MipCount or 1);t.save()
def svg_atlas(name,w,h,background,rects,texts):
 # Native vector artwork with a matching raster atlas for Unity's Texture2D.
 im=Image.new('RGB',(w,h),background);dr=ImageDraw.Draw(im)
 svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',f'<rect width="{w}" height="{h}" fill="{background}"/>']
 for x,y,rw,rh,c in rects:
  dr.rectangle((x,y,x+rw,y+rh),fill=c);svg.append(f'<rect x="{x}" y="{y}" width="{rw}" height="{rh}" fill="{c}"/>')
 for textrow in texts:
  x,y,size,text,c=textrow[:5];angle=textrow[5] if len(textrow)>5 else 0
  font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',size)
  if angle:
   layer=Image.new('RGBA',(w,h));ImageDraw.Draw(layer).text((w/2,h/2),text,font=font,fill=c,anchor='mm');layer=layer.rotate(-angle);im.paste(layer,(int(x-w/2),int(y-h/2)),layer)
  else:dr.text((x,y),text,font=font,fill=c,anchor='mm')
  svg.append(f'<text x="{x}" y="{y}" transform="rotate({angle} {x} {y})" dominant-baseline="central" text-anchor="middle" font-family="Arial" font-weight="bold" font-size="{size}" fill="{c}">{text}</text>')
 svg.append('</svg>');(A/(name+'.svg')).write_text('\n'.join(svg));im.save(A/(name+'.png'));return im

# New court graphic: full 9 x 18 m playing surface, exact +/-3 m attack lines.
w=h=1024;rects=[]
rects.append((0,341,w,342,'#117e89'))
for y in [0,341,512,683,1019]:rects.append((0,y,w,5,'#f6f4df'))
for x in [0,1018]:rects.append((x,0,6,h,'#f6f4df'))
court=svg_atlas('Caioba-quadra',w,h,'#17465c',rects,[(512,175,69,'CAIOBA','#e8e5d6',180),(512,850,69,'CAIOBA','#e8e5d6')])
settex('sharedassets3.assets',13,court)
for i,name,c,tex in [(6,'Caioba / quadra','#ffffff',13),(2,'Caioba / area livre','#123343',None),(5,'Caioba / paineis','#e5e3d7',None),(3,'Caioba / estrutura','#177681',None),(7,'Caioba / cobertura','#c3d1d2',None)]:save('sharedassets3.assets',i,material('sharedassets3.assets',i,name,c,tex))

# Completely new hall geometry. Original floor/collision origin is retained.
hall=Geometry(4);hall.floor(0,-4.5,4.5,-9,9,.001,[(0,0),(0,1),(1,1),(1,0)])
hall.floor(1,-12,12,-18,-9);hall.floor(1,-12,12,9,18);hall.floor(1,-12,-4.5,-9,9);hall.floor(1,4.5,12,-9,9)
for x in [-12,12]:
 hall.box(2,(x,7,0),(.25,14,36))
 for z in range(-16,17,4):hall.box(3,(x*.98,7,z),(.35,14,.32))
 hall.box(3,(x*.98,1.2,0),(.15,2.4,36))
 # Low stepped seating beyond the unobstructed run-off.
 for s in range(3):hall.box(2,(math.copysign(9+s*.8,x),.22+s*.25,0),(.75,.44+s*.5,22))
for z in [-18,18]:
 hall.box(2,(0,7,z),(24,14,.25));hall.box(3,(0,2.8,z*.994),(24,.35,.1))
 for x in [-9,-6,0,6,9]:hall.box(3,(x,7,z*.99),(.3,14,.25))
roof=Geometry(2)
roof.quad(1,[(-12,14,-18), (0,16,-18),(0,16,18),(-12,14,18)])
roof.quad(1,[(0,16,-18),(12,14,-18),(12,14,18),(0,16,18)])
for z in range(-16,17,4):roof.box(0,(0,13.8,z),(24,.16,.18))
template=tree('level3',14)
save('level3',14,hall.serial(template,'Caioba Arena / estrutura nova'))
save('level3',7,roof.serial(template,'Caioba Arena / teto 14-16m'))
for mf,mesh,ren,trans in [(202,14,167,109),(199,7,164,105)]:
 d=tree('level3',mf);d['m_Mesh']=ptr(mesh);save('level3',mf,d)
 save('level3',ren,reset_renderer(tree('level3',ren)))
 d=tree('level3',trans);d['m_LocalPosition']=vec(13.3399400711,-4.581384182,11.563920975);save('level3',trans,d)
# Old lines are replaced by the new exact court atlas, avoiding overlapping stripes.
d=tree('level3',165);d['m_Enabled']=False;save('level3',165,d)
# Unbatch ceiling fixtures so their visible mesh follows the raised collider.
for o in list(files['level3'].objects.values()):
 if o.type.name=='GameObject' and o.read().m_Name=='LightMesh':
  comps={files['level3'].objects[c.component.path_id].type.name:c.component.path_id for c in o.read().m_Component}
  d=tree('level3',comps['MeshFilter']);d['m_Mesh']=tree('level3',comps['MeshCollider'])['m_Mesh'];save('level3',comps['MeshFilter'],d)
  save('level3',comps['MeshRenderer'],reset_renderer(tree('level3',comps['MeshRenderer'])))
# Old precomputed ceiling occlusion is invalid for the newly built hall.
for f in ['level3']:
 for o in list(files[f].objects.values()):
  if o.type.name=='OcclusionCullingSettings':
   d=o.read_typetree()
   if 'm_OcclusionCullingData' in d:d['m_OcclusionCullingData']=ptr(0);o.save_typetree(d)
  if o.type.name=='Transform':
   d=o.read_typetree();go=files[f].objects.get(d['m_GameObject']['m_PathID'])
   if go and go.type.name=='GameObject' and go.read().m_Name.startswith('Light') and d['m_Father']['m_PathID']==0:
    d['m_LocalPosition']['y']=13.5;o.save_typetree(d)
hall.export('indoor-geometry');roof.export('indoor-roof')

# Author fresh padding, pole and tape artwork with the same UV island placements.
rects=[(0,0,1024,45,'#e3c178'),(0,940,1024,84,'#e3c178'),(480,0,28,1024,'#0c2736')]
pad=svg_atlas('Caioba-postes',512,1024,'#166a79',[(0,0,512,35,'#e3c178'),(0,989,512,35,'#e3c178')],[(256,180+i*130,110,c,'#ffffff') for i,c in enumerate('CAIOBA')])
settex('resources.assets',42,pad)
# Give every side an independent full UV rectangle, avoiding the original
# packed islands and U coordinates beyond 1 which sliced the previous label.
padding=Geometry(1);padding.box(0,(0,84.55,0),(45,170,24))
save('resources.assets',66,padding.serial(template,'Caioba / protecao postes'))
save('resources.assets',7,material('resources.assets',7,'Caioba / protecao','#ffffff',42))
for mf,ren in [(189,154),(192,157)]:
 d=tree('level3',mf);d['m_Mesh']=ptr(66,3);save('level3',mf,d)
 save('level3',ren,reset_renderer(tree('level3',ren)))
pole=svg_atlas('Caioba-metal',256,1024,'#364c56',[(16,0,13,1024,'#91a4a6'),(190,0,20,1024,'#213843'),(0,780,256,12,'#d9bf7b')],[])
settex('resources.assets',47,pole)
tape=svg_atlas('Caioba-fita',1024,512,'#e9e7db',[(0,8,1024,6,'#18828e'),(0,215,1024,7,'#18828e'),(0,380,1024,5,'#18828e')],[(260,100,42,'CAIOBA','#185064'),(770,100,42,'CAIOBA','#185064')])
settex('resources.assets',52,tape)
# Net weave is transparent; keep the original shader's alpha cutoff behavior.
net=Image.new('RGBA',(256,256),(15,29,35,0));dr=ImageDraw.Draw(net)
for p in [0,128,255]:dr.line((p,0,p,255),fill=(26,49,57,255),width=3);dr.line((0,p,255,p),fill=(26,49,57,255),width=3)
net.save(A/'Caioba-malha.png');settex('resources.assets',51,net)
(A/'Caioba-malha.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256"><path d="M0 0V256 M128 0V256 M255 0V256 M0 0H256 M0 128H256 M0 255H256" fill="none" stroke="#1a3139" stroke-width="3"/></svg>')
# Explicitly reapply the saved Mikasa atlas instead of relying on menu ball choice.
settex('resources.assets',40,Image.open(R/'assets/Mikasa-BV550C-atlas.png').convert('RGB'))

# Rebuild beach from original scene objects. Keep terrain, shaders and object
# type tables intact; no foreign scene types or inactive terrain dependencies.
beachids={}
for f in ['level1','level2']:
 sf=files[f];rows=[o for o in sf.objects.values() if o.type.name=='GameObject']
 transforms={o.path_id:o.read_typetree() for o in sf.objects.values() if o.type.name=='Transform'}
 def world(tid):
  t=transforms[tid];v=np.array(list(t['m_LocalPosition'].values()))
  return v+world(t['m_Father']['m_PathID']) if t['m_Father']['m_PathID'] else v
 terrain=next(o for o in rows if o.read().m_Name=='Terrain')
 terrainpos=world(terrain.read().m_Component[0].component.path_id)
 td=tree('sharedassets1.assets',67)['m_Heightmap'];hh=np.array(td['m_Heights']).reshape(td['m_Resolution'],td['m_Resolution'])
 def ground(x,z):
  ix=int(np.clip((x-terrainpos[0])/td['m_Scale']['x'],0,td['m_Resolution']-1));iz=int(np.clip((z-terrainpos[2])/td['m_Scale']['z'],0,td['m_Resolution']-1))
  return terrainpos[1]+hh[iz,ix]/32767*td['m_Scale']['y']
 palms=[o for o in rows if o.read().m_Name.startswith('Palmtree')]
 for k,o in enumerate(palms):
  gd=o.read_typetree();tid=gd['m_Component'][0]['component']['m_PathID'];t=transforms[tid];old=world(tid)
  dx=5*math.sin(k*1.7);dz=9*math.cos(k*.9)
  new=old+np.array([dx,0,dz])
  if abs(new[0])<12 and abs(new[2])<18:dx+=18 if new[0]>=0 else -18;new[0]=old[0]+dx
  t['m_LocalPosition']['x']+=dx;t['m_LocalPosition']['z']+=dz;t['m_LocalPosition']['y']+=ground(new[0],new[2])-ground(old[0],old[2]);save(f,tid,t)
  for c in gd['m_Component']:
   ob=sf.objects[c['component']['m_PathID']]
   if ob.type.name=='MeshRenderer':ob.save_typetree(reset_renderer(ob.read_typetree()))
 # Keep original collision/terrain and the native runtime court-line prefab.
 beachids[f]='original terrain, redesigned palm layout, native court markings'

changed=['resources.assets','level1','level2','level3','sharedassets1.assets','sharedassets3.assets']
manifest={'version':'Caioba-mapas-v11','roof_min_m':14,'roof_ridge_m':16,'attack_lines_z':[-3,3],'files':[],'runtime_vr_tested':False}
for f in changed:
 p=OUT/f;p.write_bytes((R/'versions/v10-antes-mapas'/f).read_bytes() if f=='sharedassets1.assets' else files[f].save())
 reread=UnityPy.load(str(p)).file
 assert len(reread.objects)==len(files[f].objects)
 for o in reread.objects.values():
  if o.type.name=='Mesh' and o.read().m_Name.startswith('Caioba'):
   mh=MeshHandler(o.read());mh.process();assert len(mh.m_Vertices)>0
   for part in mh.get_triangles():
    for tri in part:assert all(0<=i<len(mh.m_Vertices) for i in tri)
 manifest['files'].append({'name':f,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'before_sha256':hashlib.sha256((R/'versions/v10-antes-mapas'/f).read_bytes()).hexdigest(),'objects':len(reread.objects)})
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2));print(json.dumps(manifest,indent=2))
